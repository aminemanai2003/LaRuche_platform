FROM python:3.12-slim AS builder

RUN pip install uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY services/agent-market/ services/agent-market/

RUN uv sync --package agent_market --no-dev --frozen

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8002
CMD ["uvicorn", "agent_market.main:app", "--host", "0.0.0.0", "--port", "8002"]
