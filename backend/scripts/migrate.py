import argparse
import os
import re
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "DDL" / "migrations"

# Every runner must use this same advisory lock key.
LOCK_KEY = 4910002


def to_libpq_uri(url: str) -> str:
    return re.sub(r"^postgresql\+\w+://", "postgresql://", url)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List pending migrations without applying them.",
    )
    args = parser.parse_args()

    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2

    dsn = to_libpq_uri(url)

    try:
        conn = psycopg2.connect(dsn)
    except psycopg2.OperationalError as exc:
        first_line = str(exc).strip().splitlines()[0]
        print(f"could not connect to the database: {first_line}", file=sys.stderr)
        return 1

    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))

            if args.dry_run:
                cur.execute("SELECT to_regclass('schema_migrations')")
                table_exists = cur.fetchone()[0] is not None
                applied = set()
                if table_exists:
                    cur.execute("SELECT filename FROM schema_migrations")
                    applied = {row[0] for row in cur.fetchall()}
            else:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    "filename TEXT PRIMARY KEY, "
                    "applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
                cur.execute("SELECT filename FROM schema_migrations")
                applied = {row[0] for row in cur.fetchall()}

            pending = sorted(
                p.name for p in MIGRATIONS_DIR.glob("*.sql") if p.name not in applied
            )

            if not pending:
                print("no pending migrations")
                return 0

            if args.dry_run:
                for name in pending:
                    print(f"pending {name}")
                return 0

            for name in pending:
                path = MIGRATIONS_DIR / name
                try:
                    cur.execute(path.read_text())
                    cur.execute(
                        "INSERT INTO schema_migrations (filename) VALUES (%s)",
                        (name,),
                    )
                    print(f"applied {name}", flush=True)
                except psycopg2.Error as exc:
                    print(f"failed {name}: {str(exc).strip()}", file=sys.stderr)
                    return 1

            return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
