CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    client_ip TEXT,
    method TEXT,
    path TEXT,
    query_params TEXT NOT NULL,
    semantic_key TEXT NOT NULL,
    headers_json TEXT,
    request_body TEXT,
    response_body TEXT,
    response_status INTEGER,
    response_raw TEXT,
    response_headers TEXT,
    session_id TEXT,
    requested_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);