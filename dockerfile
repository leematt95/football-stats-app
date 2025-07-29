# Use Python 3.11 for better performance and security
FROM python:3.11-slim

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set the working directory inside the container
WORKDIR /app

# Install system deps: compiler, libpq for psycopg2, and the Postgres client for pg_isready
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      libpq-dev \
      postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/         ./app/
COPY import_players.py .
COPY wsgi.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Change ownership to app user
RUN chown -R app:app /app
USER app

# Expose the Flask port
EXPOSE 5000

# The entrypoint script will:
#  1. wait for Postgres via pg_isready
#  2. run import_players.py
#  3. start the Flask API (via python -m app.main or flask run)
ENTRYPOINT ["./entrypoint.sh"]


# Note: Flask will automatically use the app.py file as the application entry point
#       if the FLASK_APP environment variable is set to "app.py" (default behavior).
#       If you want to specify it explicitly, you can set it in the Dockerfile:
# ENV FLASK_APP=app.py
#       But this is not necessary if the file is named app.py and Flask is run in the same directory.
#       Flask will automatically discover it.
#       The entrypoint script will handle the import and then start the Flask server.
#       This allows the import script to run before the Flask app starts.
#       The entrypoint script is responsible for running the import_players.py script before starting the Flask server.
#       This ensures that the database is populated with player data before the application starts serving requests.
#       The entrypoint script is executed when the container starts, allowing for any necessary setup before running the application.
#       The entrypoint script is a shell script that runs the import script and then starts the Flask server.
#       The entrypoint script is responsible for running the import_players.py