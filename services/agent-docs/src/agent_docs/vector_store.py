from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any

import httpx
from agentkit.llm.client import LLMClient, ModelRole

VECTOR_SIZE = 768
_POINT_NAMESPACE = uuid.UUID("ad5706ac-d819-4e1c-a440-458a1c03f692")


def chunk_text(content: str, size: int = 900, overlap: int = 120) -> list[str]:
    text = content.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            split = text.rfind("\n", start, end)
            if split <= start:
                split = text.rfind(" ", start, end)
            if split > start:
                end = split
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


class QdrantDocumentStore:
    def __init__(
        self,
        url: str | None = None,
        collection: str = "wealth_docs",
        embedder: LLMClient | None = None,
    ) -> None:
        self.url = (url or os.getenv("QDRANT_URL", "http://qdrant:6333")).rstrip("/")
        self.collection = collection
        self.embedder = embedder or LLMClient(role=ModelRole.EMBED, timeout=20)
        self._client = httpx.AsyncClient(timeout=10)
        self._collection_ready = False
        self._seeded = False
        self._seed_lock = asyncio.Lock()

    async def available(self) -> bool:
        try:
            response = await self._client.get(f"{self.url}/collections")
            response.raise_for_status()
        except httpx.HTTPError:
            return False
        return True

    async def _ensure_collection(self) -> None:
        if self._collection_ready:
            return

        response = await self._client.get(f"{self.url}/collections/{self.collection}")
        if response.status_code == 404:
            response = await self._client.put(
                f"{self.url}/collections/{self.collection}",
                json={"vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}},
            )
        response.raise_for_status()
        self._collection_ready = True

    async def upsert(self, doc_id: str, content: str) -> int:
        chunks = chunk_text(content)
        if not chunks:
            return 0

        vectors = await self.embedder.embed(chunks)
        if any(len(vector) != VECTOR_SIZE for vector in vectors):
            raise ValueError(f"Expected {VECTOR_SIZE}-dimension document embeddings")

        await self._ensure_collection()
        response = await self._client.post(
            f"{self.url}/collections/{self.collection}/points/delete",
            params={"wait": "true"},
            json={
                "filter": {
                    "must": [{"key": "doc_id", "match": {"value": doc_id}}],
                }
            },
        )
        response.raise_for_status()
        points = [
            {
                "id": str(uuid.uuid5(_POINT_NAMESPACE, f"{doc_id}:{index}")),
                "vector": vector,
                "payload": {
                    "doc_id": doc_id,
                    "chunk_index": index,
                    "content": chunk,
                },
            }
            for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]
        response = await self._client.put(
            f"{self.url}/collections/{self.collection}/points",
            params={"wait": "true"},
            json={"points": points},
        )
        response.raise_for_status()
        return len(points)

    async def seed(self, documents: dict[str, str]) -> None:
        if self._seeded:
            return
        async with self._seed_lock:
            if self._seeded:
                return
            for doc_id, content in documents.items():
                await self.upsert(doc_id, content)
            self._seeded = True

    async def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        vector = (await self.embedder.embed(query))[0]
        if len(vector) != VECTOR_SIZE:
            raise ValueError(f"Expected a {VECTOR_SIZE}-dimension query embedding")

        await self._ensure_collection()
        response = await self._client.post(
            f"{self.url}/collections/{self.collection}/points/query",
            json={
                "query": vector,
                "limit": top_k,
                "score_threshold": 0.25,
                "with_payload": True,
            },
        )
        response.raise_for_status()
        points = response.json().get("result", {}).get("points", [])
        return [
            {
                "id": point["payload"]["doc_id"],
                "score": point["score"],
                "content": point["payload"]["content"],
            }
            for point in points
            if point.get("payload", {}).get("content")
        ]
