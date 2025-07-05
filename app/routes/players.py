from flask import Blueprint, request, jsonify
from app.models.player import Player

# Blueprint sets module-local route definitions
players_bp = Blueprint("players", __name__)

# ——————————————————————————————————————————
# Read all players or search by name
# URL: GET /api/players/?name=<substring>
# ——————————————————————————————————————————
@players_bp.route('/', methods=['GET'])
def get_players():
    try:
        name_query = request.args.get('name')
        if name_query:
            players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()
        else:
            players = Player.query.all()
        return jsonify([player.to_dict() for player in players]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ——————————————————————————————————————————
# Read single player by ID
# URL: GET /api/players/<int:player_id>
# ——————————————————————————————————————————
@players_bp.route('/<int:player_id>', methods=['GET'])
def get_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        return jsonify(player.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ——————————————————————————————————————————
# Search players by name
# URL: GET /api/players/search?name=<substring>
# ——————————————————————————————————————————
@players_bp.route('/search', methods=['GET'])
def search_players():
    name_query = request.args.get('name')
    if not name_query:
        return jsonify({"error": "Missing 'name' query parameter"}), 400
    players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()
    return jsonify([player.to_dict() for player in players]), 200

# ——————————————————————————————————————————
# Add pagination to GET /api/players/
# URL: GET /api/players/?page=<page>&per_page=<per_page>
# ——————————————————————————————————————————
@players_bp.route('/paginated', methods=['GET'])
def get_players_paginated():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name_query = request.args.get('name')
        if name_query:
            players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).paginate(page, per_page, False).items
        else:
            players = Player.query.paginate(page, per_page, False).items
        return jsonify([player.to_dict() for player in players]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500