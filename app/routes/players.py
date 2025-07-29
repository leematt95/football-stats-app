import logging
from typing import TYPE_CHECKING, Any, List, Tuple

from flask import Blueprint, Response, jsonify, render_template, request

from app.models.player import Player

if TYPE_CHECKING:
    # This helps type checkers understand Player has a to_dict method
    pass

logger = logging.getLogger(__name__)
# Blueprint sets module-local route definitions
players_bp = Blueprint("players", __name__)


# ——————————————————————————————————————————
# Read all players or search by name
# URL: GET /api/players/?name=<substring>
# ——————————————————————————————————————————
@players_bp.route("/", methods=["GET"])
def get_players() -> Tuple[Response, int]:
    try:
        name_query = request.args.get("name")
        limit = request.args.get("limit", type=int)
        
        if name_query:
            query = Player.query.filter(Player.name.ilike(f"%{name_query}%"))  # type: ignore[attr-defined]
        else:
            query = Player.query  # type: ignore[attr-defined]
        
        if limit:
            query = query.limit(limit)
            
        players = query.all()
        return jsonify([player.to_dict() for player in players]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ——————————————————————————————————————————
# Read single player by ID
# URL: GET /api/players/<int:player_id>
# ——————————————————————————————————————————
@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id: int) -> Tuple[Response, int]:
    try:
        player = Player.query.get(player_id)  # type: ignore[attr-defined]
        if player is None:
            return jsonify({"error": "Player not found"}), 404
        return jsonify(player.to_dict()), 200  # type: ignore[attr-defined]
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ——————————————————————————————————————————
# Search players by name (JSON response)
# URL: GET /api/players/search?name=<substring>
# ——————————————————————————————————————————
@players_bp.route("/search/json", methods=["GET"])
def search_players_json() -> Tuple[Response, int]:
    name_query = request.args.get("name")
    if not name_query:
        return jsonify({"error": "Missing 'name' query parameter"}), 400
    players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()  # type: ignore[attr-defined]
    return jsonify([player.to_dict() for player in players]), 200


# ——————————————————————————————————————————
# Render search results in HTML
# URL: GET /api/players/search/html?name=<substring>
# ——————————————————————————————————————————
@players_bp.route("/search/html", methods=["GET"])
def search_players_html() -> str:
    name_query = request.args.get("name")
    players: List[Any] = []
    if name_query:
        players = Player.query.filter(Player.name.ilike(f"%{name_query}%")).all()  # type: ignore[attr-defined]
    return render_template("search.html", players=players, name_query=name_query)


# ——————————————————————————————————————————
# Add pagination to GET /api/players/
# URL: GET /api/players/paginated?page=<page>&per_page=<per_page>
# ——————————————————————————————————————————
@players_bp.route("/paginated", methods=["GET"])
def get_players_paginated() -> Tuple[Response, int]:
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        name_query = request.args.get("name")
        if name_query:
            pagination = Player.query.filter(  # type: ignore[attr-defined]
                Player.name.ilike(f"%{name_query}%")
            ).paginate(page=page, per_page=per_page, error_out=False)
        else:
            pagination = Player.query.paginate(page=page, per_page=per_page, error_out=False)  # type: ignore[attr-defined]
        players = pagination.items  # type: ignore[attr-defined]
        return (
            jsonify(
                {
                    "players": [player.to_dict() for player in players],
                    "total_pages": pagination.pages,  # type: ignore[attr-defined]
                    "current_page": pagination.page,  # type: ignore[attr-defined]
                    "total_items": pagination.total,  # type: ignore[attr-defined]
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
