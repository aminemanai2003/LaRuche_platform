"""Prompt-injection guardrails — lightweight pattern-based filter."""

from __future__ import annotations

import re

# Patterns that suggest prompt injection or jailbreak attempts
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
    re.compile(r"forget\s+(everything|all)\s+(you|above)", re.I),
    re.compile(r"you\s+are\s+now\s+(?!an?\s+advisor)", re.I),
    re.compile(r"act\s+as\s+(if\s+you\s+(are|were)|a\s+(?!financial|wealth))", re.I),
    re.compile(r"disregard\s+(your|all)\s+(prior|previous|system)", re.I),
    re.compile(r"system\s*prompt\s*:", re.I),
    re.compile(r"<\s*/?system\s*>", re.I),
    re.compile(r"\[INST\]|\[\/INST\]", re.I),
    re.compile(r"###\s*(instruction|system|human|assistant)\s*:", re.I),
    re.compile(r"jailbreak|DAN\s+mode|developer\s+mode", re.I),
]

# Patterns flagged as potentially sensitive (PII leakage attempts)
_PII_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"reveal\s+(all\s+)?(user|client|customer)\s+(data|information|details)", re.I),
    re.compile(r"show\s+me\s+(all\s+)?(passwords?|tokens?|api\s*keys?|secrets?)", re.I),
    re.compile(r"dump\s+(the\s+)?(database|all\s+data|user\s+table)", re.I),
]

MAX_MESSAGE_LENGTH = 4000


class GuardrailViolation(ValueError):
    """Raised when a message violates guardrails."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"GuardrailViolation: {reason}")


def check_message(message: str) -> str:
    """
    Validate a user message against guardrails.

    Returns the (possibly truncated) message if safe.
    Raises GuardrailViolation if the message is rejected.
    """
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH]

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(message):
            raise GuardrailViolation(f"Prompt injection detected (pattern: {pattern.pattern[:40]})")

    for pattern in _PII_PATTERNS:
        if pattern.search(message):
            raise GuardrailViolation("Sensitive data extraction attempt detected")

    return message


def is_safe(message: str) -> bool:
    """Return True if the message passes all guardrails."""
    try:
        check_message(message)
        return True
    except GuardrailViolation:
        return False
