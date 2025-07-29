import logging
import os

from dotenv import load_dotenv
from flask import Flask
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

# ----------------------------------------
# Initialize database (only once!)
# ----------------------------------------
db.init_app(app)
migrate = Migrate(app, db)

# Create tables if they don't exist (safer approach)
with app.app_context():
    try:
        # Only create tables if they don't exist
        db.create_all()
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # In production, you might want to exit here

# ----------------------------------------
# Register Blueprint for modular routes
# ----------------------------------------
app.register_blueprint(players_bp, url_prefix="/api/players")


# ----------------------------------------
# Root route for sanity checks
# ----------------------------------------
@app.route("/")
def index():
    logger.info("Index route accessed")
    return {"message": "🏟 Welcome to the Football Stats API! 🏟"}, 200


# ----------------------------------------
# Run the application (if not using Docker)
# ----------------------------------------
if __name__ == "__main__":
    # Bind to all interfaces for development - use reverse proxy in production
    app.run(host="0.0.0.0", port=5000)  # nosec B104
