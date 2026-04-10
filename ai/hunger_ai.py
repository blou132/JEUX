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
    def __init__(self, hunger_seek_threshold: float = 0.6, food_detection_range: float = 18.0) -> None:
        if not 0.0 <= hunger_seek_threshold <= 1.0:
            raise ValueError("hunger_seek_threshold must be in [0, 1]")
        if food_detection_range < 0:
            raise ValueError("food_detection_range must be >= 0")

        self.hunger_seek_threshold = hunger_seek_threshold
        self.food_detection_range = food_detection_range

    def decide(
        self,
        creature: Creature,
        food_field: FoodField,
        can_reproduce: bool = False,
    ) -> CreatureIntent:
        if not creature.alive:
            return CreatureIntent(action="dead")

        nearest_food = food_field.get_nearest_food(creature.x, creature.y)

        # Priority 1: high hunger means looking for food.
        if creature.hunger >= self.hunger_seek_threshold:
            if nearest_food is None:
                return CreatureIntent(action="search_food")

            if creature.distance_to(nearest_food.x, nearest_food.y) <= self.food_detection_range:
                return CreatureIntent(action="move_to_food", target_food_id=nearest_food.food_id)

            return CreatureIntent(action="search_food")

        # Priority 2: reproduce when energy and pairing conditions are met.
        if can_reproduce:
            return CreatureIntent(action="reproduce")

        # Fallback behavior.
        return CreatureIntent(action="wander")
