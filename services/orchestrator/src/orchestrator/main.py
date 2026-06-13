from fastapi import FastAPI

app = FastAPI(title="orchestrator")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}
