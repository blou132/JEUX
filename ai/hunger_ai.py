from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from creatures import Creature
from world import FoodField, FoodSource


@dataclass(frozen=True)
class CreatureIntent:
    action: str
    target_food_id: Optional[str] = None
    target_creature_id: Optional[str] = None


class HungerAI:
    ACTION_DEAD = "dead"
    ACTION_FLEE = "flee"
    ACTION_SEARCH_FOOD = "search_food"
    ACTION_MOVE_TO_FOOD = "move_to_food"
    ACTION_REPRODUCE = "reproduce"
    ACTION_WANDER = "wander"

    def __init__(
        self,
        hunger_seek_threshold: float = 0.6,
        food_detection_range: float = 18.0,
        threat_detection_range: float = 5.0,
        threat_strength_ratio: float = 1.15,
    ) -> None:
        if not 0.0 <= hunger_seek_threshold <= 1.0:
            raise ValueError("hunger_seek_threshold must be in [0, 1]")
        if food_detection_range < 0:
            raise ValueError("food_detection_range must be >= 0")
        if threat_detection_range < 0:
            raise ValueError("threat_detection_range must be >= 0")
        if threat_strength_ratio < 1.0:
            raise ValueError("threat_strength_ratio must be >= 1.0")

        self.hunger_seek_threshold = hunger_seek_threshold
        self.food_detection_range = food_detection_range
        self.threat_detection_range = threat_detection_range
        self.threat_strength_ratio = threat_strength_ratio

    def decide(
        self,
        creature: Creature,
        food_field: FoodField,
        can_reproduce: bool = False,
        nearby_creatures: Iterable[Creature] | None = None,
    ) -> CreatureIntent:
        if not creature.alive:
            return CreatureIntent(action=self.ACTION_DEAD)

        # Priority 0: immediate survival when a stronger nearby creature is detected.
        nearest_threat = self._nearest_threat(creature, nearby_creatures)
        if nearest_threat is not None:
            return CreatureIntent(action=self.ACTION_FLEE, target_creature_id=nearest_threat.creature_id)

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

    def _nearest_threat(
        self,
        creature: Creature,
        nearby_creatures: Iterable[Creature] | None,
    ) -> Creature | None:
        if nearby_creatures is None or self.threat_detection_range <= 0.0:
            return None

        best_threat: Creature | None = None
        best_distance_sq = float("inf")
        max_axis_distance = self.threat_detection_range
        max_distance_sq = self.threat_detection_range * self.threat_detection_range

        for other in nearby_creatures:
            if not other.alive or other.creature_id == creature.creature_id:
                continue
            if not self._is_threat(creature, other):
                continue

            dx = other.x - creature.x
            if dx > max_axis_distance or dx < -max_axis_distance:
                continue
            dy = other.y - creature.y
            if dy > max_axis_distance or dy < -max_axis_distance:
                continue

            distance_sq = (dx * dx) + (dy * dy)
            if distance_sq > max_distance_sq:
                continue
            if distance_sq < best_distance_sq:
                best_threat = other
                best_distance_sq = distance_sq

        return best_threat

    def _is_threat(self, creature: Creature, other: Creature) -> bool:
        # A threat is a stronger nearby creature that is itself in active hunger.
        if other.hunger < self.hunger_seek_threshold:
            return False

        creature_power = creature.traits.speed * creature.traits.max_energy
        other_power = other.traits.speed * other.traits.max_energy
        return other_power >= creature_power * self.threat_strength_ratio
