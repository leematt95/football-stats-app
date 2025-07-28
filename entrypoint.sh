#!/usr/bin/env bash
set -e

# Ensure required environment variables are set
: "${DB_HOST:?DB_HOST is not set}"
: "${DB_PORT:?DB_PORT is not set}"
: "${POSTGRES_DB:?POSTGRES_DB is not set}"
: "${POSTGRES_USER:?POSTGRES_USER is not set}"

echo "Using DB_HOST=$DB_HOST, DB_PORT=$DB_PORT, POSTGRES_DB=$POSTGRES_DB, POSTGRES_USER=$POSTGRES_USER"

# Wait for Postgres to be ready
timeout=30
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -d "$POSTGRES_DB" -U "$POSTGRES_USER" >/dev/null || [ $timeout -eq 0 ]; do
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  sleep 1
  timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
  echo "Postgres is not ready after 30 seconds. Exiting."
  exit 1
fi

# Run database migrations
echo "Running database migrations…"
if ! flask db upgrade; then
  echo "Database migrations failed. Exiting."
  exit 1
fi

# Seed the database
echo "Seeding database…"
if ! python import_players.py; then
  echo "Database seeding failed. Exiting."
  exit 1
fi

# Start the Flask API
echo "Starting API…"
if ! python -m app.main; then
  echo "API failed to start. Exiting."
  exit 1
fi

echo "API started successfully."