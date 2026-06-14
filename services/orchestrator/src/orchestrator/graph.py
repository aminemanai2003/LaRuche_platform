"""
LangGraph supervisor graph.

The graph routes a user message to one or more specialist agents via A2A,
aggregates their outputs, and streams the final answer.

State machine:
  START -> router -> [agent_financial | agent_market | agent_docs | agent_action | agent_qa]
        -> aggregate -> END
"""

from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator
from typing import Annotated, Any, TypedDict

from agentkit.a2a.client import A2AClient
from agentkit.a2a.models import A2AMessage, A2ATask
from langgraph.graph import END, START, StateGraph

# ── State ─────────────────────────────────────────────────────────────────────


def _merge_list(a: list[Any], b: list[Any]) -> list[Any]:
    return a + b


class MeshState(TypedDict):
    user_message: str
    conversation_id: str
    user_id: str
    routed_agents: Annotated[list[str], _merge_list]
    agent_results: Annotated[list[dict[str, Any]], _merge_list]
    final_answer: str


# ── Agent registry ─────────────────────────────────────────────────────────────

_AGENT_URLS: dict[str, str] = {
    "financial": os.getenv("AGENT_FINANCIAL_URL", "http://agent-financial:8001"),
    "market": os.getenv("AGENT_MARKET_URL", "http://agent-market:8002"),
    "docs": os.getenv("AGENT_DOCS_URL", "http://agent-docs:8003"),
    "action": os.getenv("AGENT_ACTION_URL", "http://agent-action:8004"),
    "qa": os.getenv("AGENT_QA_URL", "http://agent-qa:8005"),
}

# Keywords used by the simple rule-based router
_ROUTING_RULES: list[tuple[str, list[str]]] = [
    (
        "financial",
        [
            "aum",
            "portfolio",
            "performance",
            "twr",
            "irr",
            "sharpe",
            "volatility",
            "deal",
            "return",
            "profit",
            "asset",
            "nav",
            "gain",
            "loss",
            "metric",
            "annualized",
            "breakdown",
        ],
    ),
    (
        "market",
        [
            "market",
            "price",
            "quote",
            "stock",
            "rate",
            "gdp",
            "inflation",
            "yield",
            "economic",
            "indicator",
            "index",
            "s&p",
            "nasdaq",
        ],
    ),
    (
        "docs",
        [
            "document",
            "pdf",
            "report",
            "extract",
            "detail",
            "find in",
            "according to",
            "search",
            "more about",
            "fact sheet",
        ],
    ),
    (
        "action",
        ["send", "email", "whatsapp", "notify", "generate report", "export", "share", "download"],
    ),
    ("qa", ["test", "generate test", "validate", "check api", "functional"]),
]


def _route(message: str) -> list[str]:
    lower = message.lower()
    # Whole-word tokens, so single-word keywords don't match inside other words
    # (e.g. "rate" must not match "generate").
    tokens = set(re.findall(r"[a-z0-9&]+", lower))
    matched: list[str] = []
    for agent, keywords in _ROUTING_RULES:
        for kw in keywords:
            hit = kw in lower if (" " in kw or "&" in kw) else kw in tokens
            if hit:
                matched.append(agent)
                break
    return matched or ["financial"]  # default to financial assistant


# ── Graph nodes ───────────────────────────────────────────────────────────────


async def router_node(state: MeshState) -> dict[str, Any]:
    agents = _route(state["user_message"])
    return {"routed_agents": agents}


async def _call_agent(agent: str, state: MeshState) -> dict[str, Any]:
    url = _AGENT_URLS.get(agent, "")
    if not url:
        return {"agent": agent, "output": f"Agent {agent} not configured", "error": True}
    try:
        async with A2AClient(base_url=url) as client:
            task = A2ATask(
                skill_id="chat",
                sender_id="orchestrator",
                messages=[A2AMessage(role="user", content=state["user_message"])],
                context={
                    "conversation_id": state["conversation_id"],
                    "user_id": state["user_id"],
                },
            )
            result = await client.send_task(task)
            content = result.output.content if result.output else ""
            return {"agent": agent, "output": content, "error": result.error is not None}
    except Exception as exc:
        return {"agent": agent, "output": str(exc), "error": True}


async def agents_node(state: MeshState) -> dict[str, Any]:
    tasks = [_call_agent(a, state) for a in state["routed_agents"]]
    results: list[dict[str, Any]] = await asyncio.gather(*tasks)
    return {"agent_results": results}


def aggregate_node(state: MeshState) -> dict[str, Any]:
    parts: list[str] = []
    for r in state["agent_results"]:
        if not r.get("error") and r.get("output"):
            parts.append(r["output"])
    answer = "\n\n".join(parts) if parts else "I was unable to retrieve that information."
    return {"final_answer": answer}


# ── Build the graph ───────────────────────────────────────────────────────────


def build_graph() -> Any:
    g: StateGraph = StateGraph(MeshState)
    g.add_node("router", router_node)
    g.add_node("agents", agents_node)
    g.add_node("aggregate", aggregate_node)
    g.add_edge(START, "router")
    g.add_edge("router", "agents")
    g.add_edge("agents", "aggregate")
    g.add_edge("aggregate", END)
    return g.compile()


_graph = build_graph()


async def run_turn(
    message: str,
    conversation_id: str = "default",
    user_id: str = "anon",
) -> AsyncIterator[str]:
    """Stream the answer token-by-token (currently yields the full answer)."""
    state: MeshState = {
        "user_message": message,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "routed_agents": [],
        "agent_results": [],
        "final_answer": "",
    }
    final_state = await _graph.ainvoke(state)
    answer: str = final_state.get("final_answer", "")
    # Yield word-by-word for a streaming feel
    for word in answer.split(" "):
        yield word + " "
