"""Async HTTP client for sending A2A tasks to a remote agent."""

from __future__ import annotations

import httpx

from agentkit.a2a.models import A2ATask, AgentCard


class A2AClient:
    """
    Sends A2A tasks to a remote agent and fetches its Agent Card.

    Usage:
        async with A2AClient(base_url="http://agent-financial:8001") as client:
            card = await client.get_card()
            result = await client.send_task(task)
    """

    def __init__(self, base_url: str, timeout: float = 60.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> A2AClient:
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client:
            await self._client.aclose()

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("A2AClient must be used as an async context manager")
        return self._client

    async def get_card(self) -> AgentCard:
        r = await self._http().get(f"{self._base}/agent/card")
        r.raise_for_status()
        return AgentCard.model_validate(r.json())

    async def send_task(self, task: A2ATask) -> A2ATask:
        r = await self._http().post(
            f"{self._base}/agent/tasks",
            json=task.model_dump(mode="json"),
        )
        r.raise_for_status()
        return A2ATask.model_validate(r.json())
