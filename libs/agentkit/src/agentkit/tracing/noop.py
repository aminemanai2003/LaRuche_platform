"""No-op tracing — replaced with Langfuse spans in Phase 12."""

from __future__ import annotations

import contextlib
from collections.abc import Generator
from typing import Any


@contextlib.contextmanager
def trace_span(name: str, **_metadata: Any) -> Generator[None, None, None]:
    """
    Context manager that marks a logical span.
    Currently a no-op; Phase 12 replaces the body with Langfuse instrumentation.
    """
    yield
