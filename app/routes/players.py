from flask import Blueprint, request, jsonify
from app.models.player import Player, db

players_bp = Blueprint("players", __name__)

@players_bp.route("/players", methods=["GET"])
def get_players():
    name_query = request.args.get("name")
    if name_query:
        # Case-insensitive partial match using ilike (PostgreSQL)
        players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()
    else:
        players = Player.query.all()

    player_list = [
        {"id": p.id, "name": p.name, "position": p.position, "team": p.team}
        for p in players
    ]
    return jsonify(player_list), 200
@players_bp.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(player.to_dict()), 200