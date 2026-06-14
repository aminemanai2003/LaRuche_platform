"""LangGraph supervisor routing tests — no real agents needed."""

from __future__ import annotations

from orchestrator.graph import _route, aggregate_node


def test_route_financial():
    assert "financial" in _route("What is my current AUM?")


def test_route_market():
    assert "market" in _route("What is the S&P 500 index today?")


def test_route_docs():
    assert "docs" in _route("Search the PDF for deal details")


def test_route_action():
    assert "action" in _route("Please send me an email with my portfolio")


def test_route_default():
    assert _route("Tell me something useful") == ["financial"]


def test_route_greeting_without_calling_an_agent():
    assert _route("hello there") == []


def test_greeting_with_question_still_routes_to_financial():
    assert _route("Hello, what is my portfolio AUM?") == ["financial"]


def test_route_multi():
    agents = _route("Send me the portfolio AUM and the S&P market data by email")
    assert "financial" in agents
    assert "action" in agents


async def test_aggregate_node_no_errors():
    state = {
        "user_message": "",
        "conversation_id": "c1",
        "user_id": "u1",
        "routed_agents": [],
        "agent_results": [
            {"agent": "financial", "output": "AUM is $20.4M", "error": False},
            {"agent": "market", "output": "S&P 500 at 5100", "error": False},
        ],
        "final_answer": "",
    }
    result = aggregate_node(state)  # type: ignore[arg-type]
    assert "AUM" in result["final_answer"]
    assert "5100" in result["final_answer"]


async def test_aggregate_node_skips_errors():
    state = {
        "user_message": "",
        "conversation_id": "c1",
        "user_id": "u1",
        "routed_agents": [],
        "agent_results": [
            {"agent": "financial", "output": "AUM is $20.4M", "error": False},
            {"agent": "market", "output": "timeout", "error": True},
        ],
        "final_answer": "",
    }
    result = aggregate_node(state)  # type: ignore[arg-type]
    assert "AUM" in result["final_answer"]
    assert "timeout" not in result["final_answer"]


async def test_aggregate_node_returns_greeting():
    state = {
        "user_message": "hello",
        "conversation_id": "c1",
        "user_id": "u1",
        "routed_agents": [],
        "agent_results": [],
        "final_answer": "",
    }
    result = aggregate_node(state)  # type: ignore[arg-type]
    assert "portfolio performance" in result["final_answer"]
