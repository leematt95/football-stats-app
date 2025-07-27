from flask import Flask
from dotenv import load_dotenv
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# ----------------------------------------
# Load environment variables from .env
# ----------------------------------------
load_dotenv()  # Load environment variables from .env file

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
# Initialize database
# ----------------------------------------
from app.models.player import db          # SQLAlchemy instance
db.init_app(app)

# ----------------------------------------
# Import routes after app creation
# ----------------------------------------
from app.routes.players import players_bp

# ----------------------------------------
# Logging setup
# ----------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.StreamHandler(),               # Send logs to STDOUT
        logging.FileHandler(os.getenv("LOG_FILE", "app.log"))  # Write logs to file
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Initialize database
# ----------------------------------------
db.init_app(app)
migrate = Migrate(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

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
    app.run(host="0.0.0.0", port=5000)
