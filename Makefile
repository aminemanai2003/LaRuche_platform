.PHONY: install lint test dev-up dev-down

## Install all Python workspaces
install:
	uv sync --all-packages

## Run linters
lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy libs/agentkit/src

## Run all tests
test:
	uv run pytest

## Start dev infrastructure (Postgres, Redis, Qdrant, MailHog, Langfuse, MLflow)
dev-up:
	docker compose -f docker-compose.dev.yml up -d

## Stop dev infrastructure
dev-down:
	docker compose -f docker-compose.dev.yml down
