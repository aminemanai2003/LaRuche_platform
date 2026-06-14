"""
agentkit — shared library for the Agentic Mesh.

Public surface:
    A2A protocol  → agentkit.a2a
    MCP tools     → agentkit.mcp
    LLM client    → agentkit.llm
    Tracing       → agentkit.tracing
    Guardrails    → agentkit.guardrails
"""

__version__ = "0.1.0"

from agentkit.a2a import (
    A2AClient,
    A2AStatus,
    A2ATask,
    AgentCard,
    AgentSkill,
    a2a_router,
    task_handler,
)
from agentkit.guardrails import GuardrailViolation, check_message, is_safe
from agentkit.llm import LLMClient, ModelRole
from agentkit.mcp import MCPRegistry, MCPTool, ToolResult
from agentkit.tracing import trace_span

__all__ = [
    # A2A
    "A2AClient",
    "A2AStatus",
    "A2ATask",
    "AgentCard",
    "AgentSkill",
    "a2a_router",
    "task_handler",
    # LLM
    "LLMClient",
    "ModelRole",
    # MCP
    "MCPRegistry",
    "MCPTool",
    "ToolResult",
    # Tracing
    "trace_span",
    # Guardrails
    "GuardrailViolation",
    "check_message",
    "is_safe",
]
