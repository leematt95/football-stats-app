from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):  # type: ignore[name-defined]
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(20))
    team = db.Column(db.String(100))
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    games = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    xg = db.Column(db.String(20))  # Expected goals
    xa = db.Column(db.String(20))  # Expected assists
    shots = db.Column(db.Integer)
    key_passes = db.Column(db.Integer)
    yellow_cards = db.Column(db.Integer)
    red_cards = db.Column(db.Integer)
    last_updated = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)

    def _expand_position(self, position: str) -> str:
        """Convert position abbreviations to full names"""
        if not position:
            return "Unknown"

        position_map = {
            "GK": "Goalkeeper",
            "D": "Defender",
            "M": "Midfielder",
            "F": "Forward",
            "S": "Substitute",  # Added missing position code
        }

        # Handle multiple positions (e.g., "F M", "D S")
        positions = position.split()
        expanded = []
        for pos in positions:
            mapped_pos = position_map.get(pos.strip())
            if mapped_pos is None:
                raise ValueError(f"Unknown position code: {pos.strip()}")
            expanded.append(mapped_pos)

        return " / ".join(expanded)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ID": self.id,
            "Name": self.name,
            "Position": self._expand_position(self.position),
            "Club": self.team,
            "Goals": self.goals,
            "Assists": self.assists,
            "Matches": self.games,
            "Minutes": self.minutes,
            "Expected_Goals": float(self.xg) if self.xg else 0.0,
            "Expected_Assists": float(self.xa) if self.xa else 0.0,
            "Shots": self.shots,
            "Key_Passes": self.key_passes,
            "Yellow_Cards": self.yellow_cards,
            "Red_Cards": self.red_cards,
            "Last_Updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
        }

    def __repr__(self):
        return f"<Player {self.name} ({self.position}) from {self.team}>"
