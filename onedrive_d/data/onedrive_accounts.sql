CREATE TABLE IF NOT EXISTS accounts (
  account_id   TEXT PRIMARY KEY,
  account_type TEXT,
  account_dump TEXT,
  profile_dump TEXT,
  UNIQUE (account_id, account_type)
    ON CONFLICT REPLACE
);