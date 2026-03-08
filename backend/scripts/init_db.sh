#!/usr/bin/env bash
# init_db.sh — Run Alembic migrations then seed the initial admin user.
# Called automatically by Docker Compose via the backend entrypoint,
# or run manually: bash backend/scripts/init_db.sh

set -euo pipefail

echo "[init_db] Running Alembic migrations..."
alembic upgrade head

echo "[init_db] Seeding initial admin user (skipped if already exists)..."
python /app/scripts/seed_admin.py

echo "[init_db] Done."
