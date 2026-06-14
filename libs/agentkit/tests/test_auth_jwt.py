"""
Real Keycloak JWT validation tests — no Keycloak server needed.

We generate an RSA keypair, mock the JWKS client to return the public key, and
sign tokens locally to prove get_current_user actually verifies RS256 signatures
and rejects bad/missing tokens when KEYCLOAK_URL is configured.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import pytest
from agentkit.auth import UserContext, get_current_user
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def _app() -> FastAPI:
    app = FastAPI()

    @app.get("/me")
    async def me(user: UserContext = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
        return {"user_id": user.user_id, "email": user.email, "roles": user.roles}

    return app


client = TestClient(_app())


@pytest.fixture
def rsa_keys() -> tuple[bytes, object]:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return priv_pem, priv.public_key()


def _patch_jwks(monkeypatch: pytest.MonkeyPatch, public_key: object) -> None:
    """Make `from jwt import PyJWKClient` return a client yielding public_key."""

    class _FakeSigningKey:
        def __init__(self, key: object) -> None:
            self.key = key

    class _FakeJWKClient:
        def __init__(self, _url: str) -> None:
            pass

        def get_signing_key_from_jwt(self, _token: str) -> _FakeSigningKey:
            return _FakeSigningKey(public_key)

    monkeypatch.setattr(pyjwt, "PyJWKClient", _FakeJWKClient)


def _claims(**overrides: object) -> dict[str, object]:
    claims: dict[str, object] = {
        "sub": "00000000-0000-0000-0000-000000000002",
        "email": "client@wealthmesh.local",
        "iss": "http://keycloak:8080/realms/wealth",
        "azp": "web",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
        "realm_access": {"roles": ["client"]},
    }
    claims.update(overrides)
    return claims


def test_valid_token_authenticates(monkeypatch: pytest.MonkeyPatch, rsa_keys: tuple) -> None:
    priv_pem, public_key = rsa_keys
    monkeypatch.setenv("KEYCLOAK_URL", "http://keycloak:8080")
    _patch_jwks(monkeypatch, public_key)

    token = pyjwt.encode(_claims(), priv_pem, algorithm="RS256")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "client@wealthmesh.local"
    assert "client" in r.json()["roles"]


def test_missing_token_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYCLOAK_URL", "http://keycloak:8080")
    r = client.get("/me")
    assert r.status_code == 401


def test_tampered_token_rejected(monkeypatch: pytest.MonkeyPatch, rsa_keys: tuple) -> None:
    _, public_key = rsa_keys
    # Sign with a *different* key than the one the JWKS returns → signature invalid.
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_pem = other.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    monkeypatch.setenv("KEYCLOAK_URL", "http://keycloak:8080")
    _patch_jwks(monkeypatch, public_key)

    token = pyjwt.encode(_claims(sub="x"), other_pem, algorithm="RS256")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


@pytest.mark.parametrize(
    ("claim_overrides", "env"),
    [
        ({"iss": "http://attacker.invalid/realms/wealth"}, {}),
        ({"azp": "untrusted-client"}, {}),
        ({"azp": "advisor-portal"}, {"KEYCLOAK_ALLOWED_CLIENTS": "advisor-portal"}),
    ],
)
def test_issuer_and_client_are_enforced(
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: tuple,
    claim_overrides: dict[str, object],
    env: dict[str, str],
) -> None:
    priv_pem, public_key = rsa_keys
    monkeypatch.setenv("KEYCLOAK_URL", "http://keycloak:8080")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    _patch_jwks(monkeypatch, public_key)

    token = pyjwt.encode(_claims(**claim_overrides), priv_pem, algorithm="RS256")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    expected = 200 if env else 401
    assert r.status_code == expected


def test_dev_bypass_when_no_keycloak(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KEYCLOAK_URL", raising=False)
    r = client.get("/me")
    assert r.status_code == 200
    assert r.json()["user_id"] == "dev-user"
