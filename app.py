from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/football")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Players table
class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    team = db.Column(db.String)
    nationality = db.Column(db.String)
    position = db.Column(db.String)
    age = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)

# /players endpoint
@app.route('/players', methods=['GET'])
def get_players():
    try:
        # Read filters from query params
        name = request.args.get('name')
        team = request.args.get('team')
        nationality = request.args.get('nationality')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Base query
        query = Player.query
        if name:
            query = query.filter(Player.name.ilike(f"%{name}%"))
        if team:
            query = query.filter(Player.team.ilike(f"%{team}%"))
        if nationality:
            query = query.filter(Player.nationality.ilike(f"%{nationality}%"))

        # Pagination
        players = query.paginate(page=page, per_page=per_page, error_out=False)

        # Return JSON response
        return jsonify({
            "players": [p.__dict__ for p in players.items],
            "total_pages": players.pages,
            "current_page": players.page,
            "total_items": players.total
        })
    except Exception as e:
        logger.error(f"Error fetching players: {e}")
        return jsonify({"error": str(e)}), 500

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))