"""PostgreSQL access: document metadata and query history."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg

from . import config


def connect() -> psycopg.Connection:
    return psycopg.connect(config.DATABASE_URL, autocommit=True)


def init_schema() -> None:
    sql = (Path(__file__).resolve().parents[2] / "sql" / "schema.sql").read_text()
    with connect() as conn:
        conn.execute(sql)


def get_document(path: str) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("SELECT id, content_hash FROM documents WHERE path=%s", (path,)).fetchone()
    return {"id": row[0], "content_hash": row[1]} if row else None


def upsert_document(path: str, title: str, tags, content_hash: str, n_chunks: int) -> None:
    with connect() as conn:
        conn.execute(
            """INSERT INTO documents (path, title, course, topic, source_type, content_hash, n_chunks)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (path) DO UPDATE SET title=EXCLUDED.title, course=EXCLUDED.course,
                 topic=EXCLUDED.topic, source_type=EXCLUDED.source_type,
                 content_hash=EXCLUDED.content_hash, n_chunks=EXCLUDED.n_chunks, ingested_at=now()""",
            (path, title, tags.course, tags.topic, tags.source_type, content_hash, n_chunks),
        )


def list_documents(course: Optional[str] = None) -> List[Dict[str, Any]]:
    q = "SELECT title, course, topic, source_type, n_chunks, ingested_at FROM documents"
    args: tuple = ()
    if course:
        q += " WHERE course=%s"
        args = (course,)
    with connect() as conn:
        rows = conn.execute(q + " ORDER BY course, topic, title", args).fetchall()
    keys = ["title", "course", "topic", "source_type", "chunks", "ingested_at"]
    return [dict(zip(keys, r)) for r in rows]


def list_courses() -> List[str]:
    with connect() as conn:
        return [r[0] for r in conn.execute("SELECT DISTINCT course FROM documents ORDER BY 1").fetchall()]


def log_query(question: str, answer: str, sources: list) -> None:
    with connect() as conn:
        conn.execute("INSERT INTO queries (question, answer, sources) VALUES (%s,%s,%s)",
                     (question, answer, json.dumps(sources)))
