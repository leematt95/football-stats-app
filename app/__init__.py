from dotenv import load_dotenv
from flask import Flask

from app.routes.players import players_bp


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.register_blueprint(players_bp, url_prefix="/api/players")
    return app
