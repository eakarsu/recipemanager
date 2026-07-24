#!/usr/bin/env python3
from runtime_server import query

query("""
CREATE TABLE IF NOT EXISTS runtime_schema_migrations (
  name TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS runtime_users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  password_salt CHAR(32) NOT NULL,
  password_hash CHAR(64) NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS runtime_sessions (
  token_hash CHAR(64) PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES runtime_users(id) ON DELETE CASCADE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS runtime_ai_receipts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES runtime_users(id) ON DELETE RESTRICT,
  prompt TEXT NOT NULL CHECK (char_length(prompt) BETWEEN 1 AND 4000),
  content TEXT NOT NULL CHECK (char_length(content) > 0),
  provider TEXT NOT NULL CHECK (provider='openrouter'),
  provider_request_id TEXT NOT NULL,
  model TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO runtime_schema_migrations(name) VALUES('001_supported_acceptance_runtime') ON CONFLICT DO NOTHING;
""")
print("Recipe runtime migrations are current")
