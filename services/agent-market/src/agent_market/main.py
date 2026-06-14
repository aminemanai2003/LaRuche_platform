from __future__ import annotations

from typing import Any

from agentkit.a2a.models import A2ATask, AgentCard, AgentSkill
from agentkit.a2a.router import a2a_router
from agentkit.llm.client import LLMClient, ModelRole
from agentkit.mcp.registry import MCPRegistry
from agentkit.tracing import trace_span
from fastapi import FastAPI

from agent_market.tools import EconIndicatorTool, MarketOverviewTool, MarketQuoteTool

# ── Registry ──────────────────────────────────────────────────────────────────

_registry = MCPRegistry()
_registry.register(MarketQuoteTool())
_registry.register(EconIndicatorTool())
_registry.register(MarketOverviewTool())

_TOOL_MAP: list[tuple[list[str], str, dict[str, Any]]] = [
    (["s&p", "spx", "nasdaq", "stock", "index"], "market.quote", {"symbol": "SPX"}),
    (["bitcoin", "btc", "crypto"], "market.quote", {"symbol": "BTC"}),
    (["gold", "gld"], "market.quote", {"symbol": "GLD"}),
    (["inflation", "cpi"], "econ.indicator", {"indicator": "us_inflation"}),
    (["fed", "interest rate", "federal reserve"], "econ.indicator", {"indicator": "us_fed_rate"}),
    (["gdp"], "econ.indicator", {"indicator": "us_gdp_growth"}),
    (["yield", "treasury", "10y"], "econ.indicator", {"indicator": "us_10y_yield"}),
    (["vix", "volatility index"], "econ.indicator", {"indicator": "vix"}),
    (["overview", "conditions", "summary"], "market.overview", {}),
]

_llm = LLMClient(role=ModelRole.DEFAULT)

_SYSTEM_PROMPT = """You are a market-data assistant for a private bank.
Answer the user's question using ONLY the tool data provided.
Be precise with numbers; do not invent figures."""


def _pick_tools(message: str) -> list[tuple[str, dict[str, Any]]]:
    """Return every tool whose keywords match — supports multi-part questions."""
    lower = message.lower()
    picked: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    for keywords, tool, kwargs in _TOOL_MAP:
        if any(kw in lower for kw in keywords):
            sig = f"{tool}:{kwargs}"
            if sig not in seen:
                picked.append((tool, kwargs))
                seen.add(sig)
    return picked or [("market.overview", {})]


async def handle_task(task: A2ATask) -> A2ATask:
    msg = task.messages[-1].content if task.messages else ""
    with trace_span("market_agent", task_id=task.task_id):
        tool_calls = _pick_tools(msg)
        tool_outputs: list[str] = []
        for tool_name, kwargs in tool_calls:
            result = await _registry.call(tool_name, **kwargs)
            if result.ok and result.content:
                tool_outputs.append(result.content)
        tool_context = "\n".join(tool_outputs)

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"User question: {msg}\n\nTool data:\n{tool_context}\n\n"
                    "Answer using only the tool data above."
                ),
            },
        ]
        try:
            answer = await _llm.chat(messages)
        except Exception:
            answer = tool_context or "No market data available."
    return task.succeed(answer, {"tools_called": [t for t, _ in tool_calls]})


_CARD = AgentCard(
    id="agent-market",
    name="Market-Data Agent",
    description="Economic indicators and market quotes.",
    version="0.1.0",
    url="http://agent-market:8002",
    skills=[
        AgentSkill(
            id="chat",
            name="Market Chat",
            description="Answer market data questions.",
            input_schema={"type": "object", "properties": {"message": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"answer": {"type": "string"}}},
        )
    ],
)

app = FastAPI(title="Market-Data Agent", version="0.1.0")
app.include_router(a2a_router(_CARD, handle_task))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent-market"}
