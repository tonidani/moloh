CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    client_ip TEXT,
    username TEXT,
    password TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);