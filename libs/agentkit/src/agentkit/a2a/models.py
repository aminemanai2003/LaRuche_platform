"""A2A protocol data models (Agent Card + Task envelope)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class A2AStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentSkill(BaseModel):
    """One capability an agent advertises."""

    id: str
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)


class AgentCard(BaseModel):
    """Identity + capability manifest for one agent (published at /agent/card)."""

    id: str
    name: str
    description: str
    version: str = "0.1.0"
    url: str  # base URL of this agent, e.g. http://agent-financial:8001
    skills: list[AgentSkill] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class A2AMessage(BaseModel):
    """Single input or output message inside a task."""

    role: str  # "user" | "assistant" | "system"
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class A2ATask(BaseModel):
    """
    Work envelope sent from orchestrator → agent (or agent → agent).

    The sender fills in task_id, skill_id, messages.
    The receiver fills in status, output, error.
    """

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    skill_id: str  # which AgentSkill to invoke
    sender_id: str  # agent id of the caller
    messages: list[A2AMessage]  # conversation history + new user turn
    context: dict[str, Any] = Field(default_factory=dict)  # extra key/value context
    status: A2AStatus = A2AStatus.PENDING
    output: A2AMessage | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def succeed(self, content: str, metadata: dict[str, Any] | None = None) -> A2ATask:
        self.status = A2AStatus.COMPLETED
        self.output = A2AMessage(role="assistant", content=content, metadata=metadata or {})
        self.completed_at = datetime.now(UTC)
        return self

    def fail(self, error: str) -> A2ATask:
        self.status = A2AStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(UTC)
        return self
