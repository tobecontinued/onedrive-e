CREATE TABLE IF NOT EXISTS drives (
  drive_id     TEXT PRIMARY KEY,
  account_id   TEXT,
  account_type TEXT,
  local_root TEXT UNIQUE NOT NULL,
  drive_dump   TEXT,
  UNIQUE (account_id, account_type, drive_id)
    ON CONFLICT REPLACE
);