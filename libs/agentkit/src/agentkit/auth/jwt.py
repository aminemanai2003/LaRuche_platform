"""
JWT validation dependency for FastAPI services.

Validates a Bearer token issued by Keycloak (or any OIDC provider) using
the public key from the JWKS endpoint. Falls back to a dev bypass when
KEYCLOAK_URL is not set.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, Request, status


@dataclass
class UserContext:
    user_id: str
    email: str
    roles: list[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        return role in self.roles


def _dev_user() -> UserContext:
    return UserContext(user_id="dev-user", email="dev@local", roles=["advisor"])


def _extract_bearer(request: Request) -> str | None:
    auth: str = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def get_current_user(request: Request) -> UserContext:
    """
    FastAPI dependency — extract + validate the JWT.
    In dev (no KEYCLOAK_URL) returns a dev user so services work without Keycloak.
    """
    keycloak_url = os.getenv("KEYCLOAK_URL")
    if not keycloak_url:
        return _dev_user()

    token = _extract_bearer(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        import jwt as pyjwt  # python-jose or PyJWT

        realm = os.getenv("KEYCLOAK_REALM", "wealth")
        jwks_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/certs"

        # Use PyJWT with JWKS client for key rotation support
        from jwt import PyJWKClient

        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        issuer = f"{keycloak_url}/realms/{realm}"
        payload: dict[str, Any] = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False, "require": ["exp", "iss", "sub"]},
        )
        allowed_clients = {
            client.strip()
            for client in os.getenv("KEYCLOAK_ALLOWED_CLIENTS", "web,mobile,backend").split(",")
            if client.strip()
        }
        authorized_party = payload.get("azp")
        if authorized_party not in allowed_clients:
            raise pyjwt.InvalidTokenError(
                f"Unauthorized client: {authorized_party or 'missing azp'}"
            )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    roles: list[str] = payload.get("realm_access", {}).get("roles", [])
    return UserContext(
        user_id=payload.get("sub", ""),
        email=payload.get("email", ""),
        roles=roles,
    )


def require_role(role: str) -> object:
    """FastAPI dependency factory — raises 403 if user lacks the given role."""
    from fastapi import Depends  # noqa: PLC0415

    async def _check(
        user: UserContext = Depends(get_current_user),  # noqa: B008
    ) -> UserContext:
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return user

    return Depends(_check)
