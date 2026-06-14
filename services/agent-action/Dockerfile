FROM python:3.12-slim AS builder

RUN pip install uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY services/agent-action/ services/agent-action/

RUN uv sync --package agent_action --no-dev --frozen

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8004
CMD ["uvicorn", "agent_action.main:app", "--host", "0.0.0.0", "--port", "8004"]
