from flask import Flask
from dotenv import load_dotenv
import os
import logging
from app.models.player import db                 # Import the Player model
from app.routes.players import players_bp            # Import Blueprint for players

# ----------------------------------------
# Load environment variables from .env file
# ----------------------------------------
load_dotenv()

# ----------------------------------------
# Set up logging using environment config
# ----------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_file = os.getenv("LOG_FILE", "app.log")

logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.StreamHandler(),              # Output logs to terminal
        logging.FileHandler(log_file)         # Output logs to file
    ]
)

logger = logging.getLogger(__name__)

# ----------------------------------------
# Create Flask app instance
# ----------------------------------------
app = Flask(__name__)
app.config.from_prefixed_env()                 # Load all FLASK_* and SQLALCHEMY_* env variables

# ----------------------------------------
# Initialize database with Flask app
# ----------------------------------------
db.init_app(app)                               # Binds SQLAlchemy instance to Flask app

# ----------------------------------------
# Register Blueprints for modular routes
# ----------------------------------------
app.register_blueprint(players_bp, url_prefix="/api/players")  # Prefix player routes with /api/players

# ----------------------------------------
# Define default root route
# ----------------------------------------
@app.route("/")
def index():
    logger.info("Index route accessed")
    return {"message": "🏟 Welcome to the Football Stats API! 🏟"}
# ----------------------------------------
