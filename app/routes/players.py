from flask import Blueprint, request, jsonify
from app.models.player import Player

# Blueprint sets module-local route definitions
players_bp = Blueprint("players", __name__)

# ——————————————————————————————————————————
# Read all players or search by name
# URL: GET /api/players/?name=<substring>
# ——————————————————————————————————————————
@players_bp.route("/", methods=["GET"])
def get_players():
    name_query = request.args.get("name")
    if name_query:
        # ilike = case-insensitive LIKE (PostgreSQL)
        players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()
    else:
        players = Player.query.all()

    return jsonify([p.to_dict() for p in players]), 200

# ——————————————————————————————————————————
# Read single player by ID
# URL: GET /api/players/<int:player_id>
# ——————————————————————————————————————————
@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get_or_404(player_id)  # 404 if not found
    return jsonify(player.to_dict()), 200
