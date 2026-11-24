"""Splits text into overlapping, paragraph-aware chunks."""
from __future__ import annotations

from typing import List


def chunk_text(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    if size <= overlap:
        raise ValueError("size must be larger than overlap")
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        # hard-split paragraphs that are longer than a chunk
        while len(para) > size:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:size])
            para = para[size - overlap:]
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}".strip() if tail else para
    if current:
        chunks.append(current)
    return chunks
