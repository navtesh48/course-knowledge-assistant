"""ChromaDB collection holding OpenAI embeddings of every chunk."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import chromadb
from openai import OpenAI

from . import config

_client = None
_openai = None


def _collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    return _client.get_or_create_collection("course_chunks", metadata={"hnsw:space": "cosine"})


def embed(texts: List[str]) -> List[List[float]]:
    global _openai
    if _openai is None:
        _openai = OpenAI()
    out: List[List[float]] = []
    for i in range(0, len(texts), 96):
        resp = _openai.embeddings.create(model=config.OPENAI_EMBED_MODEL, input=texts[i:i + 96])
        out.extend(d.embedding for d in resp.data)
    return out


def delete_document(path: str) -> None:
    _collection().delete(where={"path": path})


def add_chunks(path: str, title: str, tags, chunks: List[str]) -> None:
    if not chunks:
        return
    delete_document(path)  # re-ingest replaces old chunks
    _collection().add(
        ids=[f"{path}::{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embed(chunks),
        metadatas=[{"path": path, "title": title, "chunk": i, "course": tags.course,
                    "topic": tags.topic, "source_type": tags.source_type} for i in range(len(chunks))],
    )


def search(question: str, k: int, course: Optional[str] = None) -> List[Dict[str, Any]]:
    col = _collection()
    if col.count() == 0:
        return []
    res = col.query(query_embeddings=embed([question]), n_results=k,
                    where={"course": course} if course else None)
    return [{"text": d, "distance": dist, **m}
            for d, dist, m in zip(res["documents"][0], res["distances"][0], res["metadatas"][0])]
