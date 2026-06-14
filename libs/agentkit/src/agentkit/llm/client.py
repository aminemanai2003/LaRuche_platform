"""
Async Ollama LLM client.

- Role-based model selection (DEFAULT, CONVERSATIONAL, REASONING, EMBED)
- Streaming and non-streaming chat
- Embedding generation
- Retries with exponential back-off
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

import httpx


class ModelRole(str, Enum):
    DEFAULT = "default"  # fast 3B — routing, most agents
    CONVERSATIONAL = "conversational"  # 7B — financial assistant
    REASONING = "reasoning"  # deepseek-r1 — complex analysis
    EMBED = "embed"  # nomic-embed-text


_ROLE_ENV: dict[ModelRole, str] = {
    ModelRole.DEFAULT: "MODEL_DEFAULT",
    ModelRole.CONVERSATIONAL: "MODEL_CONVERSATIONAL",
    ModelRole.REASONING: "MODEL_REASONING",
    ModelRole.EMBED: "MODEL_EMBED",
}

_ROLE_FALLBACK: dict[ModelRole, str] = {
    ModelRole.DEFAULT: "qwen2.5:3b",
    ModelRole.CONVERSATIONAL: "qwen2.5:7b",
    ModelRole.REASONING: "deepseek-r1:7b",
    ModelRole.EMBED: "nomic-embed-text",
}


def _model_for(role: ModelRole) -> str:
    return os.getenv(_ROLE_ENV[role], _ROLE_FALLBACK[role])


class LLMClient:
    """
    Async Ollama client (OpenAI-compatible endpoint).

    Usage:
        async with LLMClient() as llm:
            reply = await llm.chat([{"role": "user", "content": "Hello"}])
            async for token in llm.stream([{"role": "user", "content": "Hello"}]):
                print(token, end="", flush=True)
    """

    def __init__(
        self,
        base_url: str | None = None,
        role: ModelRole = ModelRole.DEFAULT,
        model: str | None = None,
        temperature: float = 0.0,
        max_retries: int = 3,
        timeout: float = 120.0,
    ) -> None:
        resolved: str = (
            base_url
            or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            or "http://localhost:11434"
        )
        self._base = resolved.rstrip("/")
        self.model = model or _model_for(role)
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> LLMClient:
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client:
            await self._client.aclose()

    def _http(self) -> httpx.AsyncClient:
        # Lazily create the client so LLMClient works both as an async context
        # manager and as a long-lived module-level singleton (as the agents use it).
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    def _chat_payload(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if tools:
            payload["tools"] = tools
        return payload

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Non-streaming chat. Returns the assistant message content."""
        for attempt in range(self.max_retries):
            try:
                r = await self._http().post(
                    f"{self._base}/api/chat",
                    json=self._chat_payload(messages, tools),
                )
                r.raise_for_status()
                data: dict[str, Any] = r.json()
                return str(data["message"]["content"])
            except (httpx.HTTPError, KeyError):
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)
        return ""  # unreachable

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """Streaming chat — yields token strings as they arrive."""
        payload = {**self._chat_payload(messages), "stream": True}
        async with self._http().stream("POST", f"{self._base}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break

    async def embed(self, text: str | list[str]) -> list[list[float]]:
        """Generate embeddings. Returns list of float vectors."""
        embed_model = _model_for(ModelRole.EMBED)
        inputs = [text] if isinstance(text, str) else text
        r = await self._http().post(
            f"{self._base}/api/embed",
            json={"model": embed_model, "input": inputs},
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()
        result: list[list[float]] = data["embeddings"]
        return result
