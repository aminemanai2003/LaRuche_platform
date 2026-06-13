"""A2A server router tests — echo agent end-to-end."""

import pytest
from agentkit.a2a.models import A2AMessage, A2AStatus, A2ATask, AgentCard, AgentSkill
from agentkit.a2a.router import a2a_router, task_handler
from fastapi import FastAPI
from fastapi.testclient import TestClient


@task_handler
async def echo_handler(task: A2ATask) -> A2ATask:
    """Simplest possible agent: echoes the last user message back."""
    last_user = next((m.content for m in reversed(task.messages) if m.role == "user"), "")
    return task.succeed(f"ECHO: {last_user}")


CARD = AgentCard(
    id="echo-agent",
    name="Echo Agent",
    description="Returns the user message verbatim.",
    url="http://localhost:9999",
    skills=[AgentSkill(id="echo", name="Echo", description="Echoes input.")],
)


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(a2a_router(CARD, echo_handler))
    return TestClient(app)


def test_get_card(client: TestClient) -> None:
    r = client.get("/agent/card")
    assert r.status_code == 200
    card = AgentCard.model_validate(r.json())
    assert card.id == "echo-agent"
    assert card.skills[0].id == "echo"


def test_send_task_echo(client: TestClient) -> None:
    task = A2ATask(
        skill_id="echo",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="Hello agent!")],
    )
    r = client.post("/agent/tasks", json=task.model_dump(mode="json"))
    assert r.status_code == 200
    result = A2ATask.model_validate(r.json())
    assert result.status == A2AStatus.COMPLETED
    assert result.output is not None
    assert result.output.content == "ECHO: Hello agent!"


def test_send_task_error_handling(client: TestClient) -> None:
    """A handler that raises should return HTTP 500."""

    @task_handler
    async def boom(_: A2ATask) -> A2ATask:
        raise ValueError("something went wrong")

    app2 = FastAPI()
    app2.include_router(a2a_router(CARD, boom))
    c2 = TestClient(app2, raise_server_exceptions=False)

    task = A2ATask(
        skill_id="echo",
        sender_id="orchestrator",
        messages=[A2AMessage(role="user", content="trigger error")],
    )
    r = c2.post("/agent/tasks", json=task.model_dump(mode="json"))
    assert r.status_code == 500
