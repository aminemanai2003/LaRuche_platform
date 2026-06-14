FROM python:3.12-slim AS builder

RUN pip install uv
WORKDIR /app

# Copy workspace config and all required packages
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY services/orchestrator/ services/orchestrator/

RUN uv sync --package orchestrator --no-dev --frozen

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
