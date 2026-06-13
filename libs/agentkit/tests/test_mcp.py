"""MCP tool base and registry tests."""

import pytest
from agentkit.mcp.registry import MCPRegistry
from agentkit.mcp.tool import MCPTool, ToolResult


class AddTool(MCPTool):
    @property
    def name(self) -> str:
        return "math.add"

    @property
    def description(self) -> str:
        return "Add two numbers."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        }

    async def execute(self, **kwargs: object) -> ToolResult:
        a = float(kwargs["a"])  # type: ignore[arg-type]
        b = float(kwargs["b"])  # type: ignore[arg-type]
        return ToolResult(content=a + b)


class FailTool(MCPTool):
    @property
    def name(self) -> str:
        return "always.fail"

    @property
    def description(self) -> str:
        return "Always returns an error."

    async def execute(self, **kwargs: object) -> ToolResult:
        return ToolResult(content=None, error="intentional failure")


def test_tool_to_dict() -> None:
    tool = AddTool()
    d = tool.to_dict()
    assert d["type"] == "function"
    assert d["function"]["name"] == "math.add"
    assert "properties" in d["function"]["parameters"]


@pytest.mark.asyncio
async def test_registry_call() -> None:
    reg = MCPRegistry()
    reg.register(AddTool())
    result = await reg.call("math.add", a=3, b=4)
    assert result.ok
    assert result.content == 7.0


@pytest.mark.asyncio
async def test_registry_missing_tool() -> None:
    reg = MCPRegistry()
    with pytest.raises(KeyError, match="not registered"):
        await reg.call("no.such.tool")


@pytest.mark.asyncio
async def test_registry_error_result() -> None:
    reg = MCPRegistry()
    reg.register(FailTool())
    result = await reg.call("always.fail")
    assert not result.ok
    assert result.error == "intentional failure"


def test_registry_to_dict() -> None:
    reg = MCPRegistry()
    reg.register(AddTool())
    reg.register(FailTool())
    defs = reg.to_dict()
    assert len(defs) == 2
    names = {d["function"]["name"] for d in defs}
    assert names == {"math.add", "always.fail"}


def test_registry_contains_and_len() -> None:
    reg = MCPRegistry()
    reg.register(AddTool())
    assert "math.add" in reg
    assert "other" not in reg
    assert len(reg) == 1
