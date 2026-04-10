from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from creatures import Creature
from world import FoodField


@dataclass(frozen=True)
class CreatureIntent:
    action: str
    target_food_id: Optional[str] = None


class HungerAI:
    def __init__(self, hunger_seek_threshold: float = 0.6) -> None:
        if not 0.0 <= hunger_seek_threshold <= 1.0:
            raise ValueError("hunger_seek_threshold must be in [0, 1]")
        self.hunger_seek_threshold = hunger_seek_threshold

    def decide(self, creature: Creature, food_field: FoodField) -> CreatureIntent:
        if not creature.alive:
            return CreatureIntent(action="dead")

        if creature.hunger >= self.hunger_seek_threshold:
            nearest_food = food_field.get_nearest_food(creature.x, creature.y)
            if nearest_food is not None:
                return CreatureIntent(action="seek_food", target_food_id=nearest_food.food_id)

        return CreatureIntent(action="idle")
