"""Retrieve relevant chunks and answer with numbered citations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from . import config

SYSTEM = (
    "You answer questions about the student's own course materials. Use ONLY the numbered "
    "context passages. Cite passages inline like [1] or [2]. If the context does not contain "
    "the answer, say you could not find it in the materials."
)


@dataclass
class Answer:
    text: str
    sources: List[dict]


def build_context(hits: List[dict]) -> str:
    return "\n\n".join(f"[{i}] ({h['title']}, chunk {h['chunk']})\n{h['text']}" for i, h in enumerate(hits, 1))


def ask(question: str, course: Optional[str] = None, k: int = config.TOP_K) -> Answer:
    from openai import OpenAI

    from . import db, vectorstore

    hits = vectorstore.search(question, k, course)
    if not hits:
        return Answer("No documents have been ingested yet.", [])
    resp = OpenAI().chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{build_context(hits)}\n\nQuestion: {question}"},
        ],
    )
    text = resp.choices[0].message.content or ""
    sources = [{"n": i, "title": h["title"], "course": h["course"], "topic": h["topic"],
                "source_type": h["source_type"], "chunk": h["chunk"]} for i, h in enumerate(hits, 1)]
    try:
        db.log_query(question, text, sources)
    except Exception:  # history is best-effort
        pass
    return Answer(text, sources)
