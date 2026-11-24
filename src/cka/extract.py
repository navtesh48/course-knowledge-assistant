"""Text extraction for PDFs and plain-text notes, plus tag inference from the path."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {".pdf", ".txt", ".md"}


@dataclass
class Tags:
    course: str
    topic: str
    source_type: str


def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n\n".join((p.extract_text() or "") for p in reader.pages)
    if ext in {".txt", ".md"}:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"unsupported file type: {ext}")


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def infer_tags(path: str, inbox: str) -> Tags:
    """Convention: inbox/<course>/<topic>/<file>. Source type comes from the file name."""
    rel = os.path.relpath(path, inbox).split(os.sep)
    course = rel[0].lower() if len(rel) > 1 else "general"
    topic = rel[1].lower() if len(rel) > 2 else "general"
    name = rel[-1].lower()
    if any(k in name for k in ("lecture", "slides", "lec")):
        source = "lecture"
    elif any(k in name for k in ("paper", "arxiv", "journal")):
        source = "paper"
    elif any(k in name for k in ("chapter", "textbook", "ch")):
        source = "textbook"
    else:
        source = "notes"
    return Tags(course, topic, source)
