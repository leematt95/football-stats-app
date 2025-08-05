import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request
from flask_migrate import Migrate

# ----------------------------------------
# Load environment variables from .env
# ----------------------------------------
load_dotenv()  # Load environment variables from .env file

# ----------------------------------------
# Import database and routes after load_dotenv
# ----------------------------------------
from app.models.player import db  # SQLAlchemy instance  # noqa: E402
from app.routes.players import players_bp  # noqa: E402

# ----------------------------------------
# Create Flask app instance
# ----------------------------------------
app = Flask(__name__)

# ----------------------------------------
# App configuration
# ----------------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# ----------------------------------------
# Logging setup
# ----------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.StreamHandler(),  # Send logs to STDOUT
        logging.FileHandler(os.getenv("LOG_FILE", "app.log")),  # Write logs to file
    ],
)
logger = logging.getLogger(__name__)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

app.register_blueprint(players_bp, url_prefix="/api/players")


# ----------------------------------------
# Error Handlers for API Consistency
# ----------------------------------------
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status_code": 404
        }), 404
    # For non-API routes, return HTML error
    return f"<h1>404 Not Found</h1><p>The page you're looking for doesn't exist.</p>", 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors with JSON response for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Method Not Allowed",
            "message": f"Method {request.method} not allowed for this endpoint",
            "status_code": 405
        }), 405
    return f"<h1>405 Method Not Allowed</h1><p>Method {request.method} not allowed.</p>", 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with JSON response for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "status_code": 500
        }), 500
    return "<h1>500 Internal Server Error</h1><p>Something went wrong.</p>", 500


@app.route("/")
def index():
    """Root endpoint - return JSON for API calls, redirect for browser."""
    # Check if this is an API call (JSON requested) or browser request
    if request.headers.get('Content-Type') == 'application/json' or \
       'application/json' in request.headers.get('Accept', ''):
        logger.info("API root route accessed")
        return jsonify({
            "message": "🏟 Welcome to the Football Stats API! 🏟",
            "version": "1.0.0",
            "endpoints": {
                "players": "/api/players/",
                "search": "/api/players/search/",
                "dashboard": "/api/players/dashboard"
            }
        }), 200
    else:
        logger.info("Index route accessed - redirecting to dashboard")
        return redirect("/api/players/dashboard")


@app.route("/api")
def api_info():
    logger.info("API info route accessed")
    return jsonify({
        "message": "🏟 Welcome to the Football Stats API! 🏟",
        "version": "1.0.0",
        "endpoints": {
            "players": "/api/players/",
            "search": "/api/players/search/",
            "dashboard": "/api/players/dashboard"
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104
