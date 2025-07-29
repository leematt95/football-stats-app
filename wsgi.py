"""
WSGI entry point for production deployment.
Use this with gunicorn: gunicorn --bind 0.0.0.0:5000 wsgi:app
"""
from app.main import app

if __name__ == "__main__":
    app.run()
