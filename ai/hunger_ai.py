from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from creatures import Creature
from world import FoodField, FoodSource


@dataclass(frozen=True)
class CreatureIntent:
    action: str
    target_food_id: Optional[str] = None


class HungerAI:
    ACTION_DEAD = "dead"
    ACTION_SEARCH_FOOD = "search_food"
    ACTION_MOVE_TO_FOOD = "move_to_food"
    ACTION_REPRODUCE = "reproduce"
    ACTION_WANDER = "wander"

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
            return CreatureIntent(action=self.ACTION_DEAD)

        nearest_food = food_field.get_nearest_food(creature.x, creature.y)
        is_hungry = creature.hunger >= self.hunger_seek_threshold

        # Priority 1: high hunger means active food seeking.
        if is_hungry:
            return self._food_seeking_intent(creature, nearest_food)

        # Priority 2: reproduction when pairing/energy conditions are met.
        if can_reproduce:
            return CreatureIntent(action=self.ACTION_REPRODUCE)

        # Fallback behavior.
        return CreatureIntent(action=self.ACTION_WANDER)

    def _food_seeking_intent(self, creature: Creature, nearest_food: Optional[FoodSource]) -> CreatureIntent:
        if nearest_food is None:
            return CreatureIntent(action=self.ACTION_SEARCH_FOOD)

        food_distance = creature.distance_to(nearest_food.x, nearest_food.y)
        if food_distance <= self.food_detection_range:
            return CreatureIntent(action=self.ACTION_MOVE_TO_FOOD, target_food_id=nearest_food.food_id)

        return CreatureIntent(action=self.ACTION_SEARCH_FOOD)
