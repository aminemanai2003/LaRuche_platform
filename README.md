# WealthMesh — Agentic Mesh for Private Banking

A production-grade AI platform for private banking / wealth management built as a fleet of specialist AI agents communicating over the **A2A protocol**, orchestrated by **LangGraph**, and secured by **Keycloak PKCE**.

A conversational private-banking assistant covering AUM queries, TWR, IRR, Sharpe ratio, geographic/sector breakdowns, document RAG, email actions, and a voice callbot.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Traefik Gateway                        │
│         JWT forward-auth → /api/* (orchestrator)           │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   LangGraph         │
              │   Orchestrator :8000│
              │   (supervisor graph)│
              └──────┬──────────────┘
                     │  A2A HTTP/JSON fan-out
        ┌────────────┼────────────────────────────┐
        ▼            ▼            ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Financial │  │ Market   │  │  Docs    │  │  Action  │
│ Agent    │  │ Agent    │  │  Agent   │  │  Agent   │
│  :8001   │  │  :8002   │  │  :8003   │  │  :8004   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
        ┌──────────┐  ┌──────────┐
        │  QA      │  │  Voice   │
        │ Agent    │  │ Callbot  │
        │  :8005   │  │  :8006   │
        └──────────┘  └──────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Qwen2.5:3b via Ollama (local, RTX 2050) |
| Orchestration | LangGraph supervisor graph, SSE streaming |
| Agent protocol | A2A (HTTP/JSON task envelopes) |
| Tool protocol | MCP (Model Context Protocol) base classes |
| Auth | Keycloak 24 — PKCE for web/mobile, bearer for backend |
| Gateway | Traefik v3 — forward-auth middleware |
| Database | PostgreSQL 16 + SQLAlchemy async + Alembic |
| Cache | Redis 7 |
| Vector store | Qdrant |
| Tracing | Langfuse (spans per agent call) |
| Eval | MLflow + LLM-as-judge golden dataset |
| Voice | faster-whisper STT + Piper TTS |
| Email | MailHog (dev SMTP sandbox) |
| Web frontend | React + Vite + Tailwind CSS |
| Mobile | React Native / Expo |
| Container | Docker Compose (dev) / Kubernetes + Helm (prod) |
| Python tooling | uv workspace, ruff, mypy, pytest-asyncio |

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| orchestrator | 8000 | LangGraph supervisor + auth/verify + GDPR endpoints |
| agent-financial | 8001 | AUM, TWR, IRR, Sharpe, geo/sector breakdowns |
| agent-market | 8002 | Market quotes, economic indicators |
| agent-docs | 8003 | Document ingestion + keyword/RAG search |
| agent-action | 8004 | Report generation, email (MailHog), WhatsApp stub |
| agent-qa | 8005 | AI-SDLC: LLM-generated pytest tests + sandboxed runner |
| voice | 8006 | STT (faster-whisper) + TTS (Piper) + voice-to-voice |

---

## Quick Start

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Docker Desktop
- [Ollama](https://ollama.ai/) running on host

```bash
# Pull the LLM
ollama pull qwen2.5:3b

# Install Python dependencies
uv sync

# Start all infrastructure + services
docker compose -f docker-compose.dev.yml up -d

# Run tests
uv run pytest services/ libs/ -q
```

### Authentication

Two modes, controlled by environment:

- **Dev bypass (default, no Keycloak):** when `KEYCLOAK_URL` is unset, `get_current_user()` returns a hardcoded dev advisor context so all endpoints work immediately. The web app uses `VITE_DEV_AUTH=true`.
- **Real Keycloak (login-only, no self-registration):** RS256 JWTs are verified against the realm JWKS, expected issuer, and an allowed `azp` client (`web,mobile,backend` by default; override with `KEYCLOAK_ALLOWED_CLIENTS`). Pre-seeded users: `advisor@wealthmesh.local / advisor123` and `client@wealthmesh.local / client123`. The client login maps to its portfolio via a fixed `keycloak_id`.

Turn it on:

```bash
# 1. Start identity + db
docker compose -f docker-compose.dev.yml up -d postgres keycloak   # realm auto-imported

# 2. Start the backend with Keycloak enabled
KEYCLOAK_URL=http://localhost:8180 uv run uvicorn orchestrator.main:app --port 8000

# 3. Build/run the web app with real login (uses frontend/.env.production)
cd frontend && npm run build && npm run preview
```

JWT enforcement is covered by `libs/agentkit/tests/test_auth_jwt.py` (valid token → 200, missing/tampered → 401) — no Keycloak server required to run those tests.

---

## API Examples

```bash
# Chat (SSE stream)
curl -N http://localhost:8000/api/chat \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my portfolio AUM?"}'

# GDPR delete-my-data
curl -X DELETE http://localhost:8000/api/gdpr/delete-my-data \
  -H "Authorization: Bearer dev-token"

# Direct A2A call to financial agent
curl http://localhost:8001/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"task_id":"t1","messages":[{"role":"user","content":"Show sector breakdown"}]}'
```

---

## Demo

Reproduces a full private-banking conversation (9 turns: AUM → TWR → geography → deals → S&P → Fed rate → document → report → email):

```bash
# Start services first, then:
uv run python scripts/demo.py --url http://localhost:8000
```

---

## Eval Harness

```bash
# Run golden dataset (14 Q/A pairs, keyword + LLM-as-judge scoring)
uv run python evals/eval_harness.py --no-llm-judge

# With MLflow logging
MLFLOW_TRACKING_URI=http://localhost:5000 \
  uv run python evals/eval_harness.py --run-name baseline
```

---

## Kubernetes / Helm Deployment

```bash
# Start minikube and deploy everything
./scripts/minikube-start.sh

# Or deploy to existing cluster
helm upgrade --install wealthmesh helm/wealthmesh \
  --namespace wealthmesh --create-namespace

# Build all images
./scripts/build-images.sh 1.0.0
```

---

## Compliance

### GDPR (EU 2016/679)
- `DELETE /api/gdpr/delete-my-data` — Right to Erasure (Article 17)
- Audit log with 90-day retention
- Voice audio: in-memory transcription only, never persisted
- Redis conversation TTL: 24 hours

### EU AI Act (Regulation 2024/1689)
- Risk classification: **Limited Risk** (AI assistant, human oversight enforced)
- All LLMs run locally — no personal data sent to third parties
- Model register: [`docs/ai-act-model-register.json`](docs/ai-act-model-register.json)
- Transparency: users are always informed they are interacting with AI

### Prompt Injection Guardrails
All messages are validated by `agentkit.guardrails.check_message()` before reaching agents:
- Injection patterns: "ignore previous instructions", "act as", system tags
- PII extraction patterns: "dump database", "show all passwords"
- Max message length: 4000 characters

---

## Project Structure

```
project/
├── libs/
│   ├── agentkit/          # Shared library: A2A, MCP, LLM, tracing, guardrails
│   └── db/                # SQLAlchemy models, Alembic migrations
├── services/
│   ├── orchestrator/      # LangGraph supervisor
│   ├── agent-financial/   # Portfolio metrics
│   ├── agent-market/      # Market data
│   ├── agent-docs/        # Document RAG
│   ├── agent-action/      # Email / report / WhatsApp
│   ├── agent-qa/          # AI-SDLC test generation
│   └── voice/             # STT + TTS callbot
├── frontend/              # React + Vite + Tailwind web app
├── mobile/                # React Native / Expo mobile app
├── evals/                 # Golden dataset + eval harness
├── infra/
│   ├── traefik/           # Gateway config
│   ├── keycloak/          # Realm export
│   ├── postgres/          # Init SQL
│   └── k8s/               # Kustomize base + overlays
├── helm/wealthmesh/       # Helm chart
├── scripts/               # Demo, build-images, minikube-start
└── docs/                  # AI Act model register
```

---

## Hardware Notes

Built and benchmarked on **RTX 2050 (4GB VRAM)**:
- One LLM loaded at a time via Ollama on host
- All agents use LLM fallback gracefully when Ollama is unavailable
- Minikube limited to 6 GB RAM to leave headroom for Ollama

---

## Phases Completed

| Phase | Description | Tests |
|-------|-------------|-------|
| 0 | Monorepo scaffold | — |
| 1 | RTX 2050 LLM benchmark | — |
| 2 | agentkit shared library | 12 |
| 3 | SQLAlchemy models + Alembic + finance metrics | 14 |
| 4 | Traefik gateway + Keycloak realm | 3 |
| 5 | LangGraph supervisor graph | 8 |
| 6 | Financial Assistant agent | 14 |
| 7 | Market Data agent | 6 |
| 8 | Document / RAG agent | 5 |
| 9 | Action agent (email / report / WhatsApp) | 6 |
| 10 | QA / Tester agent | 3 |
| 11 | Voice callbot (STT + TTS) | 6 |
| 12 | Observability (Langfuse + MLflow eval) | 4 |
| 13 | React web frontend | — |
| 14 | React Native / Expo mobile | — |
| 15 | Kubernetes + Helm + Dockerfiles | — |
| 16 | Compliance + GDPR + guardrails + demo | 16 |
| **Total** | | **121 tests** |
