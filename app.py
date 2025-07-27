#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()  # Load .env into os.environ

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# ── Configuration & Logging ────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:securepass123@localhost:5432/football_db")
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Flask & Database Initialization ────────────────────────────────────────

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ── Model Definition ───────────────────────────────────────────────────────

class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    team = db.Column(db.String)
    nationality = db.Column(db.String)
    position = db.Column(db.String)
    age = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    last_updated = db.Column(
        db.TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team": self.team,
            "nationality": self.nationality,
            "position": self.position,
            "age": self.age,
            "goals": self.goals,
            "assists": self.assists,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else None
        }

# ── Routes ─────────────────────────────────────────────────────────────────

@app.before_request
def log_request():
    logger.info(f"Incoming request: {request.method} {request.url} - Params: {request.args}")

@app.route('/players', methods=['GET'])
def get_players():
    name = request.args.get('name', type=str)
    team = request.args.get('team', type=str)
    nationality = request.args.get('nationality', type=str)
    page = request.args.get('page', DEFAULT_PAGE, type=int)
    per_page = request.args.get('per_page', DEFAULT_PER_PAGE, type=int)

    if per_page < 1 or per_page > MAX_PER_PAGE:
        return jsonify({"error": f"per_page must be between 1 and {MAX_PER_PAGE}"}), 400

    query = Player.query
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))
    if team:
        query = query.filter(Player.team.ilike(f"%{team}%"))
    if nationality:
        query = query.filter(Player.nationality.ilike(f"%{nationality}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    players_list = [p.to_dict() for p in pagination.items]

    return jsonify({
        "players": players_list,
        "total_pages": pagination.pages,
        "current_page": pagination.page,
        "total_items": pagination.total
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), 500

# ── Entrypoint ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    logger.info(f"Starting Flask server (DB={DATABASE_URL})")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))