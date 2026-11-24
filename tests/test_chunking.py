import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from cka.chunking import chunk_text
from cka.extract import infer_tags
from cka.rag import build_context


def test_empty_text_gives_no_chunks():
    assert chunk_text("   \n\n ") == []


def test_chunks_respect_size_and_cover_text():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 60 for i in range(20))
    chunks = chunk_text(text, size=500, overlap=50)
    assert len(chunks) > 3
    assert all(len(c) <= 600 for c in chunks)  # size + overlap carry-over
    assert "Paragraph 0." in chunks[0] and "Paragraph 19." in chunks[-1]


def test_giant_paragraph_is_split():
    chunks = chunk_text("x" * 5000, size=1000, overlap=100)
    assert len(chunks) >= 5


def test_bad_overlap_rejected():
    with pytest.raises(ValueError):
        chunk_text("hello", size=10, overlap=10)


def test_infer_tags_from_path():
    t = infer_tags("/inbox/cse310/graphs/lecture_05.pdf", "/inbox")
    assert (t.course, t.topic, t.source_type) == ("cse310", "graphs", "lecture")
    assert infer_tags("/inbox/readme.txt", "/inbox").course == "general"


def test_context_is_numbered():
    ctx = build_context([{"title": "A", "chunk": 0, "text": "foo"}, {"title": "B", "chunk": 2, "text": "bar"}])
    assert ctx.startswith("[1] (A, chunk 0)") and "[2] (B, chunk 2)" in ctx
