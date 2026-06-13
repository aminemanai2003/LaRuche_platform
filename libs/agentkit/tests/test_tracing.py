"""Tracing no-op stub tests."""

from agentkit.tracing import trace_span


def test_trace_span_is_noop() -> None:
    result = []
    with trace_span("test.span", model="qwen2.5:3b", agent="financial"):
        result.append(1)
    assert result == [1]


def test_trace_span_propagates_exceptions() -> None:
    import pytest

    with pytest.raises(ValueError, match="boom"), trace_span("test.error"):
        raise ValueError("boom")
