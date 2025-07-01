from flask import Blueprint, jsonify

players_bp = Blueprint("players", __name__)

@players_bp.route("/", methods=["GET"])
def get_players():
    sample_players = [
        {"id": 1, "name": "Bukayo Saka", "position": "RW", "team": "Arsenal"},
        {"id": 2, "name": "Erling Haaland", "position": "ST", "team": "Man City"}
    ]
    return jsonify(sample_players)
@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id):
    sample_player = {
        "id": player_id,
        "name": "Bukayo Saka",
        "position": "RW",
        "team": "Arsenal"
    }
    return jsonify(sample_player)