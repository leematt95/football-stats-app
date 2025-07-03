#!/bin/bash
set -e

# Run database migrations
flask db upgrade

# Start the Flask app
exec flask run --host=0.0.0.0 --port=5000