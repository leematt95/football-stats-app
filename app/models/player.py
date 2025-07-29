from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):  # type: ignore[name-defined]
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    team = db.Column(db.String(100), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "team": self.team,
        }

    def __repr__(self):
        return f"<Player {self.name} ({self.position}) from {self.team}>"
