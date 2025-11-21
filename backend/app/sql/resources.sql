CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    response_body TEXT,
    response_status INTEGER,
    response_headers TEXT,
    path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE embeddings USING vss0(
    embedding(768)
);