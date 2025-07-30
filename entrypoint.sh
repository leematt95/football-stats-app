#!/usr/bin/env bash
set -e

: "${DB_HOST:?DB_HOST is not set}"
: "${DB_PORT:?DB_PORT is not set}"
: "${POSTGRES_DB:?POSTGRES_DB is not set}"
: "${POSTGRES_USER:?POSTGRES_USER is not set}"

echo "Using DB_HOST=$DB_HOST, DB_PORT=$DB_PORT, POSTGRES_DB=$POSTGRES_DB, POSTGRES_USER=$POSTGRES_USER"

timeout=30
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -d "$POSTGRES_DB" -U "$POSTGRES_USER" >/dev/null; do
  if [ $timeout -le 0 ]; then
    echo "Postgres is not ready after 30 seconds. Exiting."
    exit 1
  fi
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT... ($timeout)"
  sleep 1
  timeout=$((timeout - 1))
done

echo "Postgres is available."

echo "Seeding database…"
if ! python import_players.py; then
  echo "Database seeding failed. Exiting."
  exit 1
fi

echo "Starting API…"
exec python -m app.main