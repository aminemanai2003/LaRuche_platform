from __future__ import annotations

from agentkit.auth import UserContext, get_current_user
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}


@app.get("/auth/verify")
async def auth_verify(  # noqa: B008
    response: Response,
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> dict[str, str]:
    """Traefik forward-auth endpoint — validates JWT, injects user headers."""
    response.headers["X-User-Id"] = user.user_id
    response.headers["X-User-Email"] = user.email
    response.headers["X-User-Roles"] = ",".join(user.roles)
    return {"ok": "true"}


@app.get("/api/me")
async def me(  # noqa: B008
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> dict[str, object]:
    return {
        "user_id": user.user_id,
        "email": user.email,
        "roles": user.roles,
    }
