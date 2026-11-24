-- Every ingested document is tagged by course, topic and source.
CREATE TABLE IF NOT EXISTS documents (
    id            SERIAL PRIMARY KEY,
    path          TEXT UNIQUE NOT NULL,
    title         TEXT NOT NULL,
    course        TEXT NOT NULL DEFAULT 'general',
    topic         TEXT NOT NULL DEFAULT 'general',
    source_type   TEXT NOT NULL CHECK (source_type IN ('lecture', 'paper', 'textbook', 'notes')),
    content_hash  TEXT NOT NULL,
    n_chunks      INTEGER NOT NULL DEFAULT 0,
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_documents_course ON documents (course);
CREATE INDEX IF NOT EXISTS idx_documents_topic  ON documents (topic);

CREATE TABLE IF NOT EXISTS queries (
    id          SERIAL PRIMARY KEY,
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    sources     JSONB NOT NULL DEFAULT '[]',
    asked_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
