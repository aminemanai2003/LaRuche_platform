from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from agentkit.auth import UserContext, get_current_user
from fastapi import Depends, FastAPI, Response
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
    conv_id = body.conversation_id or str(uuid.uuid4())

    async def _sse() -> AsyncIterator[str]:
        async for token in run_turn(body.message, conv_id, user.user_id):
            payload = json.dumps({"token": token, "conversation_id": conv_id})
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_sse(), media_type="text/event-stream")
