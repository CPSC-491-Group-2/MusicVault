-- Adds the session revocation counter bumped on password change.
BEGIN;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS auth_version INTEGER NOT NULL DEFAULT 1;

COMMIT;
