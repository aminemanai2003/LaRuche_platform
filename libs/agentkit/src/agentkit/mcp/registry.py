"""MCPRegistry — register and look up tools by name."""

from __future__ import annotations

from typing import Any

from agentkit.mcp.tool import MCPTool, ToolResult


class MCPRegistry:
    """
    Holds all MCPTool instances for an agent.

    Usage:
        registry = MCPRegistry()
        registry.register(MyTool())
        result = await registry.call("my_tool", param1="value")
        tools_json = registry.to_dict()   # pass to LLM as tool definitions
    """

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> MCPTool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered. Available: {list(self._tools)}")
        return self._tools[name]

    async def call(self, name: str, **kwargs: Any) -> ToolResult:
        return await self.get(name).execute(**kwargs)

    def to_dict(self) -> list[dict[str, Any]]:
        """Return all tool definitions in MCP/OpenAI tool format."""
        return [t.to_dict() for t in self._tools.values()]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)
