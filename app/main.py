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

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

app.register_blueprint(players_bp, url_prefix="/api/players")


@app.route("/")
def index():
    logger.info("Index route accessed")
    return {"message": "🏟 Welcome to the Football Stats API! 🏟"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104
