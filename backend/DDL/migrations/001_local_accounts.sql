
-- ============================================================
-- MUSICVAULT DATABASE MIGRATION
-- 001_local_accounts.sql
--
-- Purpose:
-- Prepare the database for local authentication while
-- preserving existing Spotify accounts.
--
-- Password hashing is not implemented in this migration.
-- ============================================================

BEGIN;

-- ============================================================
-- 1. ADD PASSWORD STORAGE
-- ============================================================

ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- ============================================================
-- 2. ADD SPOTIFY EMAIL METADATA
-- ============================================================

ALTER TABLE spotify_accounts
ADD COLUMN IF NOT EXISTS email VARCHAR(320);

-- ============================================================
-- 3. PRESERVE EXISTING SPOTIFY EMAILS
-- ============================================================

UPDATE spotify_accounts AS sa
SET email = u.email
FROM users AS u
WHERE sa.user_id = u.id
  AND u.password_hash IS NULL
  AND u.email IS NOT NULL
  AND sa.email IS NULL;

-- ============================================================
-- 4. CLEAR SPOTIFY-ONLY USER LOGIN EMAILS
-- ============================================================

UPDATE users AS u
SET email = NULL
WHERE u.password_hash IS NULL
  AND u.email IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM spotify_accounts AS sa
      WHERE sa.user_id = u.id
  );

-- ============================================================
-- 5. VALIDATE REMAINING LOCAL EMAILS
-- ============================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM users
        WHERE email IS NOT NULL
          AND TRIM(email) = ''
    ) THEN
        RAISE EXCEPTION
            'Blank email addresses found.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM users
        WHERE email IS NOT NULL
        GROUP BY LOWER(TRIM(email))
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Duplicate normalized emails found.';
    END IF;
END;
$$;

-- ============================================================
-- 6. NORMALIZE LOCAL EMAIL ADDRESSES
-- ============================================================

UPDATE users
SET email = LOWER(TRIM(email))
WHERE email IS NOT NULL
  AND email IS DISTINCT FROM LOWER(TRIM(email));

-- ============================================================
-- 7. REMOVE OLD EMAIL UNIQUENESS CONSTRAINT
-- ============================================================

ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_email_key;

DROP INDEX IF EXISTS idx_users_email;

-- ============================================================
-- 8. CREATE CASE-INSENSITIVE UNIQUE INDEX
-- ============================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_ci
ON users (LOWER(email));

COMMIT;