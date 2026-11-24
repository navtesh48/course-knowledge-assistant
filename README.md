# Course Knowledge Assistant: RAG Search Across Personal Study Materials

> **Provenance:** a clean reimplementation of a project I originally built; the original code was unavailable, so this was rebuilt from the original design. The 6 unit tests pass (chunking, tag inference, context building). I have **not** run the full pipeline against OpenAI, ChromaDB and PostgreSQL, so retrieval quality is unmeasured and the repo reports no accuracy numbers.

*Mar 2026 – Present*

`Python` `OpenAI API` `ChromaDB` `PostgreSQL` `Streamlit`

Ask plain-English questions over 150+ lecture notes, papers, and textbook excerpts and get answers **with citations back to the source document**.

```
docs_inbox/<course>/<topic>/file.pdf
        │  watchdog (auto-ingest)
        ▼
  extract text ─▶ chunk ─▶ OpenAI embeddings ─▶ ChromaDB
        │                                          │
        ▼                                          ▼
  PostgreSQL (course / topic / source tags)   top-k retrieval ─▶ GPT answer + [1][2] citations
                                                   ▲
                                         Streamlit chat + library UI
```

## How it works
- **Ingestion pipeline** (`src/cka/ingest.py`): watches a folder, extracts text from new PDFs and notes, chunks it, embeds it, and updates metadata automatically. Adding a document takes no manual steps. Unchanged files are skipped by content hash; edited files replace their old chunks.
- **PostgreSQL schema** (`sql/schema.sql`): every document is tagged by course, topic, and source type (lecture / paper / textbook / notes). Tags come from the folder layout `docs_inbox/<course>/<topic>/`.
- **RAG** (`src/cka/rag.py`): retrieves the top-k chunks (optionally filtered by course), asks the model to answer only from them, and returns numbered citations.
- **Streamlit UI** (`app.py`): chat tab with citations and a library tab to browse everything ingested.

## Quick start
```bash
cp .env.example .env            # add OPENAI_API_KEY
docker compose up -d            # PostgreSQL with the schema pre-loaded
pip install -r requirements.txt
export PYTHONPATH=src

python -m cka.ingest --watch    # in one terminal: drop PDFs/notes into docs_inbox/
streamlit run app.py            # in another
```

Example layout:
```
docs_inbox/
  cse310/
    graphs/lecture_05_bfs.pdf
    sorting/chapter_2_notes.md
```

## Tests
```bash
PYTHONPATH=src pytest
```

## Roadmap
- Hybrid (keyword + vector) retrieval
- Re-ranking
- Flashcard / quiz generation from retrieved chunks
