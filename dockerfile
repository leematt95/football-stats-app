FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      libpq-dev \
      postgresql-client \
      curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=60 --retries=3 -r requirements.txt

COPY app/         ./app/
COPY import_players.py .
COPY wsgi.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN chown -R app:app /app
USER app

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]