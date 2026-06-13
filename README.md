# Agentic Mesh — Wealth Management

A fleet of AI agents for private-banking / wealth management, inspired by **Mermaid**.
See [`docs/mentor/PLAN.md`](docs/mentor/PLAN.md) for the full project plan.

## Quick start (dev)

```bash
# 1. Copy env
cp .env.example .env

# 2. Start infrastructure
make dev-up   # Postgres, Redis, Qdrant, MailHog, Langfuse, MLflow

# 3. Install Python packages
make install

# 4. Run tests
make test
```

## Stack
- **LLMs:** Ollama (host) — Qwen2.5, Phi-3.5, DeepSeek-R1, Mistral
- **Agents:** FastAPI microservices orchestrated with LangGraph
- **Protocol:** A2A (Agent-to-Agent) + MCP (Model Context Protocol)
- **Gateway:** Traefik + Keycloak (OIDC)
- **Storage:** PostgreSQL + Qdrant (vector) + Redis
- **Observability:** Langfuse + MLflow
- **Frontend:** React + Vite · Mobile: React Native (Expo)
- **Infra:** Docker + Kubernetes (minikube)

## Project layout

```
docs/mentor/     # project brief, PLAN.md, whiteboard image
libs/agentkit/   # shared A2A protocol, MCP base, LLM client
services/        # orchestrator + 5 agent microservices + voice
data/            # DB migrations + seed data
eval/            # evaluation harness + datasets
web/             # React frontend
mobile/          # React Native (Expo)
infra/           # Traefik, Keycloak, K8s manifests
```
