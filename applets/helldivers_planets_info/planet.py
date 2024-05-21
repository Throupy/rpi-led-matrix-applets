from dataclasses import dataclass
from typing import Dict, Any
from rgbmatrix import graphics
from matrix.colours import Colours

@dataclass
class Planet:
    name: str
    current_owner: str
    percentage_liberated: float
    player_count: int
    colour: graphics.Color

    def __str__(self) -> str:
        return f"{self.name} : {self.current_owner} : {self.percentage_liberated} : {self.player_count}"

    @staticmethod
    def from_json(json: Dict[str, Any]) -> 'Planet':
        return Planet(
            name=json.get("name", ""),
            current_owner=json.get("currentOwner", ""),
            percentage_liberated = round(
                int(json.get("health", 0)) / int(json.get("maxHealth", 0)) * 100,
                1
            ),
            player_count=json["statistics"].get("playerCount", ""),
            colour=Colours.AUTOMATON 
                if json.get("currentOwner", "") == "Automaton"
                else Colours.TERMINID
        )