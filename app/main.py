from flask import Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()  # Load .env file variables

@app.route("/")
def home():
    return "🏟️ Football Stats App is running!"

@app.route("/db-check")
def check_env():
    # Read values from .env
    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")
    return f"User: {db_user}, Pass: {db_pass}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)