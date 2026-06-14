"""LLM client tests — fully mocked, no Ollama required."""

from __future__ import annotations

import httpx
import pytest
from agentkit.llm.client import LLMClient, ModelRole, _model_for


def test_model_for_role_defaults() -> None:
    assert _model_for(ModelRole.DEFAULT) in ("qwen2.5:3b", "llama3.2:3b")
    assert _model_for(ModelRole.CONVERSATIONAL) in ("qwen2.5:7b", "mistral:7b-instruct")
    assert _model_for(ModelRole.EMBED) == "nomic-embed-text"


def test_model_for_role_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_DEFAULT", "custom-model:3b")
    assert _model_for(ModelRole.DEFAULT) == "custom-model:3b"


@pytest.mark.asyncio
async def test_chat_success(respx_mock: object) -> None:
    """Mock Ollama /api/chat and verify LLMClient.chat() parses the response."""
    import respx

    respx.post("http://localhost:11434/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "The Sharpe ratio is 0.58."}},
        )
    )

    async with LLMClient(role=ModelRole.DEFAULT) as llm:
        reply = await llm.chat([{"role": "user", "content": "What is my Sharpe ratio?"}])
    assert "0.58" in reply


@pytest.mark.asyncio
async def test_embed_success() -> None:
    """Mock Ollama /api/embed and verify dimensions."""
    import respx

    fake_vector = [0.1] * 768
    with respx.mock:
        respx.post("http://localhost:11434/api/embed").mock(
            return_value=httpx.Response(200, json={"embeddings": [fake_vector]})
        )
        async with LLMClient() as llm:
            vecs = await llm.embed("portfolio time-weighted return")
    assert len(vecs) == 1
    assert len(vecs[0]) == 768


def test_llm_client_lazily_creates_http_client() -> None:
    # The agents hold a module-level LLMClient and call chat() directly (no
    # `async with`), so _http() must lazily create the client instead of raising.
    llm = LLMClient()
    assert llm._client is None
    client = llm._http()
    assert isinstance(client, httpx.AsyncClient)
    assert llm._http() is client  # reused, not recreated
