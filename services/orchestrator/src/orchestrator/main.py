from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from agentkit.auth import UserContext, get_current_user
from agentkit.guardrails import GuardrailViolation, check_message
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from orchestrator.graph import run_turn

app = FastAPI(title="Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory GDPR deletion log (persist to DB in production)
_DELETION_LOG: list[dict[str, Any]] = []


# ── Health ─────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}


# ── Auth ───────────────────────────────────────────────────────────────────────


@app.get("/auth/verify")
async def auth_verify(  # noqa: B008
    response: Response,
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> dict[str, str]:
    """Traefik forward-auth — validates JWT and injects user headers."""
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


# ── Chat (SSE streaming) ───────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = ""


@app.post("/api/chat")
async def chat(  # noqa: B008
    body: ChatRequest,
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> StreamingResponse:
    """Stream a chat turn through the LangGraph supervisor."""
    try:
        safe_message = check_message(body.message)
    except GuardrailViolation as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    conv_id = body.conversation_id or str(uuid.uuid4())

    async def _sse() -> AsyncIterator[str]:
        async for token in run_turn(safe_message, conv_id, user.user_id):
            payload = json.dumps({"token": token, "conversation_id": conv_id})
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_sse(), media_type="text/event-stream")


# ── GDPR ───────────────────────────────────────────────────────────────────────


@app.delete("/api/gdpr/delete-my-data")
async def gdpr_delete(  # noqa: B008
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> dict[str, str]:
    """
    GDPR Article 17 — Right to Erasure.
    Logs the deletion request; production should cascade to all data stores.
    """
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user_id": user.user_id,
        "email": user.email,
        "action": "delete_all_personal_data",
        "status": "acknowledged",
        "note": (
            "Production: cascade delete to Postgres (conversations, audit_log rows), "
            "Qdrant vectors, Langfuse traces for this user."
        ),
    }
    _DELETION_LOG.append(entry)
    return {
        "status": "acknowledged",
        "user_id": user.user_id,
        "message": (
            "Your personal data deletion request has been logged. "
            "Data will be purged within 30 days per GDPR Article 17."
        ),
    }


@app.get("/api/gdpr/deletion-log")
async def gdpr_log(  # noqa: B008
    user: UserContext = Depends(get_current_user),  # noqa: B008
) -> list[dict[str, Any]]:
    """Return deletion log (admin-only in production — requires 'admin' role)."""
    if "admin" not in user.roles and "advisor" not in user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _DELETION_LOG
