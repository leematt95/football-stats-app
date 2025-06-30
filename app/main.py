from flask import Flask
from dotenv import load_dotenv
import os
import psycopg2  # For PostgreSQL connection
import logging   # For logging setup

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
        logging.StreamHandler(),               # Logs to terminal
        logging.FileHandler(log_file)          # Logs to file specified in .env
    ]
)

logger = logging.getLogger(__name__)

# ----------------------------------------
# Create Flask app instance
# ----------------------------------------
app = Flask(__name__)

# ----------------------------------------
# Load DB credentials from .env
# ----------------------------------------
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_host = "db"  # Refers to service name in docker-compose.yml

# ----------------------------------------
# Connect to the PostgreSQL database
# ----------------------------------------
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host
        )
        logger.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# ----------------------------------------
# Define home route
# ----------------------------------------
@app.route("/")
def index():
    logger.info("Index route accessed")
    return "🏟️Welcome to the Football Stats App!🏟️"

# ----------------------------------------
# Define /db-test route to verify DB connectivity
# ----------------------------------------
@app.route("/db-test")
def db_test():
    logger.info("Attempting database test connection...")

    conn = get_db_connection()
    if conn is None:
        return "❌ Database connection failed. Check logs for details.", 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")  # Simple test query
        result = cur.fetchone()
        logger.info(f"Database test query successful: {result}")
        cur.close()
        conn.close()
        return f"✅ Database is connected. Test query returned: {result}"
    except Exception as e:
        logger.error(f"Database test query failed: {e}")
        return "❌ Database query failed. See logs.", 500
