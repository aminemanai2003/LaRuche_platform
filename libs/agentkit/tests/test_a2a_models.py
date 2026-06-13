"""A2A model serialization / deserialization tests."""

import json

from agentkit.a2a.models import A2AMessage, A2AStatus, A2ATask, AgentCard, AgentSkill


def test_agent_card_roundtrip() -> None:
    card = AgentCard(
        id="agent-financial",
        name="Financial Assistant",
        description="Conversational portfolio analytics",
        url="http://agent-financial:8001",
        skills=[
            AgentSkill(
                id="portfolio.query",
                name="Portfolio Query",
                description="Answer questions about AUM, TWR, Sharpe, etc.",
            )
        ],
    )
    data = card.model_dump()
    restored = AgentCard.model_validate(data)
    assert restored.id == card.id
    assert restored.skills[0].id == "portfolio.query"


def test_a2a_task_defaults() -> None:
    task = A2ATask(
        skill_id="portfolio.query",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="What is my AUM?")],
    )
    assert task.status == A2AStatus.PENDING
    assert task.task_id  # auto-generated UUID
    assert task.output is None


def test_a2a_task_succeed() -> None:
    task = A2ATask(
        skill_id="portfolio.query",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="AUM?")],
    )
    task.succeed("Your AUM is $20.4M")
    assert task.status == A2AStatus.COMPLETED
    assert task.output is not None
    assert task.output.content == "Your AUM is $20.4M"
    assert task.completed_at is not None


def test_a2a_task_fail() -> None:
    task = A2ATask(
        skill_id="portfolio.query",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="AUM?")],
    )
    task.fail("Database unavailable")
    assert task.status == A2AStatus.FAILED
    assert task.error == "Database unavailable"


def test_a2a_task_json_roundtrip() -> None:
    task = A2ATask(
        skill_id="portfolio.query",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="What is my Sharpe ratio?")],
    )
    raw = task.model_dump_json()
    restored = A2ATask.model_validate(json.loads(raw))
    assert restored.task_id == task.task_id
    assert restored.messages[0].content == "What is my Sharpe ratio?"
