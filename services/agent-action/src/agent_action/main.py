from fastapi import FastAPI

app = FastAPI(title="agent-action")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent-action"}
