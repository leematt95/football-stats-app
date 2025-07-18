#!/usr/bin/env bash
set -e

# Wait for Postgres (service name 'db' on default port)
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" >/dev/null 2>&1; do
  echo "Waiting for Postgres at $DB_HOST..."
  sleep 1
done

# Run the import script
echo "Seeding database with initial data..."
python import_players.py

# Finally, start the Flask app
echo "Starting Flask API..."
python -m app.main
# Note: Ensure the import_players.py script is idempotent
# to avoid duplicate entries if the container restarts.