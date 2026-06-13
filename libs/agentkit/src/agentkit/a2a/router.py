"""
FastAPI router that every agent mounts to expose:
  GET  /agent/card       → AgentCard
  POST /agent/tasks      → execute an A2ATask
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Body

from agentkit.a2a.models import A2AStatus, A2ATask, AgentCard

# Type for the handler function each agent registers
TaskHandlerFn = Callable[[A2ATask], Awaitable[A2ATask]]


def a2a_router(card: AgentCard, handler: TaskHandlerFn) -> APIRouter:
    """
    Build and return a FastAPI router pre-wired with the agent's card and handler.

    Usage (in each agent's main.py):
        from agentkit.a2a import a2a_router, AgentCard
        card = AgentCard(id="agent-financial", ...)
        router = a2a_router(card, my_handler)
        app.include_router(router)
    """
    router = APIRouter(tags=["a2a"])

    @router.get("/agent/card")  # type: ignore[misc]
    async def get_card() -> AgentCard:
        return card

    @router.post("/agent/tasks")  # type: ignore[misc]
    async def receive_task(task: Annotated[A2ATask, Body()]) -> A2ATask:
        task.status = A2AStatus.RUNNING
        try:
            result = await handler(task)
        except Exception as exc:
            task.fail(str(exc))
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return result

    return router


def task_handler(fn: TaskHandlerFn) -> TaskHandlerFn:
    """Decorator — no-op, just marks a function as a task handler for clarity."""
    return fn
