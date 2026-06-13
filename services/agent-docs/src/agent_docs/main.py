from fastapi import FastAPI

app = FastAPI(title="agent-docs")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent-docs"}
