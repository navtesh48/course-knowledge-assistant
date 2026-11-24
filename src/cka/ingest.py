"""Ingestion pipeline + folder watcher.

    python -m cka.ingest            # ingest everything in INBOX_DIR once
    python -m cka.ingest --watch    # keep running; new/changed files are picked up automatically
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from . import config, db, vectorstore
from .chunking import chunk_text
from .extract import SUPPORTED, extract_text, file_hash, infer_tags


def ingest_file(path: str, inbox: str = config.INBOX_DIR) -> str:
    """Returns 'ingested', 'unchanged', 'empty' or 'skipped'."""
    if Path(path).suffix.lower() not in SUPPORTED:
        return "skipped"
    digest = file_hash(path)
    existing = db.get_document(path)
    if existing and existing["content_hash"] == digest:
        return "unchanged"
    text = extract_text(path)
    chunks = chunk_text(text, config.CHUNK_CHARS, config.CHUNK_OVERLAP)
    if not chunks:
        return "empty"
    tags = infer_tags(path, inbox)
    title = Path(path).stem.replace("_", " ").replace("-", " ").title()
    vectorstore.add_chunks(path, title, tags, chunks)
    db.upsert_document(path, title, tags, digest, len(chunks))
    return "ingested"


def ingest_all(inbox: str = config.INBOX_DIR) -> dict:
    counts: dict = {}
    for dirpath, _, files in os.walk(inbox):
        for name in files:
            result = ingest_file(os.path.join(dirpath, name), inbox)
            counts[result] = counts.get(result, 0) + 1
    return counts


def watch(inbox: str = config.INBOX_DIR) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class H(FileSystemEventHandler):
        def _handle(self, event):
            if not event.is_directory:
                time.sleep(0.5)  # let the writer finish
                print(f"{event.src_path}: {ingest_file(event.src_path, inbox)}")

        on_created = on_modified = _handle

    obs = Observer()
    obs.schedule(H(), inbox, recursive=True)
    obs.start()
    print(f"Watching {inbox} …")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    a = ap.parse_args()
    os.makedirs(config.INBOX_DIR, exist_ok=True)
    db.init_schema()
    print(ingest_all())
    if a.watch:
        watch()
