from flask import Flask
from dotenv import load_dotenv
import os
import logging

from app.models.player import db          # SQLAlchemy instance
from app.routes.players import players_bp # Blueprint for player routes

# ----------------------------------------
# Create Flask app instance
# ----------------------------------------
app = Flask(__name__)

# ----------------------------------------
# Load environment variables from .env
# ----------------------------------------
# .env: plain-text file holding key=value lines (e.g. DB URIs, secrets)
load_dotenv()

# ----------------------------------------
# App configuration
# ----------------------------------------
app.config["SQLALCHEMY_DATABASE_URI"]      = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"]                        = os.getenv("DEBUG", "False").lower() == "true"
app.config.from_prefixed_env()  # picks up any FLASK_* or SQLALCHEMY_* vars

# ----------------------------------------
# Logging setup
# ----------------------------------------
log_level  = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.StreamHandler(),               # send logs to STDOUT
        logging.FileHandler(os.getenv("LOG_FILE", "app.log"))
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Initialize database
# ----------------------------------------
db.init_app(app)
with app.app_context():
    db.create_all()   # Creates all tables if they don't exist

# ----------------------------------------
# Register Blueprint for modular routes
# Prefix of "/api/players" means:
#   GET /api/players/        → list/search players
#   GET /api/players/<id>    → single player lookup
# ----------------------------------------
app.register_blueprint(players_bp, url_prefix="/api/players")

# ----------------------------------------
# Root route for sanity checks
# ----------------------------------------
@app.route("/")
def index():
    logger.info("Index route accessed")
    return {"message": "🏟 Welcome to the Football Stats API! 🏟"}, 200
