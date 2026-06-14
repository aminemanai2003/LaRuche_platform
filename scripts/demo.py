"""
WealthMesh demo script — reproduces a full private-banking conversation.

Usage:
    uv run python scripts/demo.py [--url http://localhost:8000]

Prerequisites:
    1. Start services: docker compose -f docker-compose.dev.yml up -d
    2. Pull LLM: ollama pull qwen2.5:3b
    3. Run this script
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

import httpx

_CONVERSATION = [
    {
        "turn": 1,
        "message": "What is the total AUM of my portfolio?",
        "expect": ["20", "million", "AUM"],
    },
    {
        "turn": 2,
        "message": "And what is the TWR since inception?",
        "expect": ["178", "TWR"],
    },
    {
        "turn": 3,
        "message": "Show me the geographic breakdown.",
        "expect": ["Asia", "America"],
    },
    {
        "turn": 4,
        "message": "What are the top performing deals?",
        "expect": ["deal"],
    },
    {
        "turn": 5,
        "message": "What is the current S&P 500 level?",
        "expect": ["5247", "S&P"],
    },
    {
        "turn": 6,
        "message": "What is the US Federal Reserve interest rate?",
        "expect": ["5.25", "Fed"],
    },
    {
        "turn": 7,
        "message": "Search for the Aurora Brands factsheet document.",
        "expect": ["Aurora"],
    },
    {
        "turn": 8,
        "message": "Build a portfolio performance report for the client.",
        "expect": ["AUM", "report"],
    },
    {
        "turn": 9,
        "message": "Send the report by email to client@wealthmesh.local — confirm send.",
        "expect": ["email", "confirm"],
    },
]

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"


async def stream_turn(
    client: httpx.AsyncClient, base_url: str, message: str, conv_id: str, token: str
) -> str:
    """Stream one chat turn and return full response text."""
    answer = ""
    async with client.stream(
        "POST",
        f"{base_url}/api/chat",
        json={"message": message, "conversation_id": conv_id},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    ) as resp:
        if resp.status_code != 200:
            return f"[HTTP {resp.status_code}]"
        async for line in resp.aiter_lines():
            if line.startswith("data: ") and "[DONE]" not in line:
                import json

                try:
                    payload = json.loads(line[6:])
                    tok = payload.get("token", "")
                    answer += tok
                    print(tok, end="", flush=True)
                except Exception:
                    pass
    return answer


def check_expectations(answer: str, expect: list[str]) -> bool:
    lower = answer.lower()
    return all(kw.lower() in lower for kw in expect)


async def run_demo(base_url: str, token: str = "dev-token") -> int:
    conv_id = f"demo-{int(time.time())}"
    passed = 0

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}WealthMesh — Private Banking AI Demo{RESET}")
    print(f"Target: {base_url}  |  Conversation: {conv_id}")
    print(f"{'=' * 60}{RESET}\n")

    async with httpx.AsyncClient(timeout=60) as client:
        # Health check
        try:
            r = await client.get(f"{base_url}/health")
            r.raise_for_status()
            print(f"{GREEN}✓ Orchestrator healthy{RESET}\n")
        except Exception as exc:
            print(f"{RED}✗ Orchestrator not reachable: {exc}{RESET}")
            print("  Start with: docker compose -f docker-compose.dev.yml up -d")
            return 1

        for item in _CONVERSATION:
            n = item["turn"]
            msg = item["message"]
            expect = item["expect"]

            print(f"{CYAN}{BOLD}[Turn {n}]{RESET} {BOLD}{msg}{RESET}")
            print(f"{GRAY}Assistant: {RESET}", end="")

            t0 = time.monotonic()
            answer = await stream_turn(client, base_url, msg, conv_id, token)
            latency = (time.monotonic() - t0) * 1000

            ok = check_expectations(answer, expect)
            status = f"{GREEN}✓ PASS{RESET}" if ok else f"{YELLOW}~ PARTIAL{RESET}"
            print(f"\n  {status}  ({latency:.0f} ms)\n")

            if ok:
                passed += 1

    total = len(_CONVERSATION)
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"Results: {passed}/{total} turns met keyword expectations")
    if passed == total:
        print(f"{GREEN}{BOLD}All demo turns passed!{RESET}")
    elif passed >= total * 0.7:
        print(f"{YELLOW}Most turns passed — LLM grounding may vary without Ollama.{RESET}")
    else:
        print(f"{RED}Several turns missed expectations — check if Ollama is running.{RESET}")
    print(f"{'=' * 60}{RESET}\n")
    return 0 if passed >= total * 0.7 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="WealthMesh demo")
    parser.add_argument("--url", default="http://localhost:8000", help="Orchestrator base URL")
    parser.add_argument("--token", default="dev-token", help="Bearer token")
    args = parser.parse_args()
    return asyncio.run(run_demo(args.url, args.token))


if __name__ == "__main__":
    sys.exit(main())
