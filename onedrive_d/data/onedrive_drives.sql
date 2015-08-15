CREATE TABLE IF NOT EXISTS drives (
  drive_id     TEXT PRIMARY KEY,
  account_id   TEXT,
  account_type TEXT,
  drive_dump   TEXT,
  UNIQUE (account_id, account_type, drive_id)
    ON CONFLICT REPLACE
);