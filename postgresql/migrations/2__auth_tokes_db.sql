DROP TABLE IF EXISTS ${SCHEMA}.auth_tokens;

CREATE TABLE IF NOT EXISTS ${SCHEMA}.auth_tokens (
    token TEXT PRIMARY KEY NOT NULL,
    user_id TEXT NOT NULL,
    scopes TEXT[] NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
