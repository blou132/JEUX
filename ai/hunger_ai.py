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

        # THREAT/FLEE: priority 0 is immediate escape from a detected nearby threat.
        nearest_threat = self._nearest_threat(creature, nearby_creatures)
        if nearest_threat is not None:
            return CreatureIntent(action=self.ACTION_FLEE, target_creature_id=nearest_threat.creature_id)

        nearest_food = food_field.get_nearest_food(creature.x, creature.y)

        hunger_threshold = self._effective_hunger_seek_threshold(creature)
        is_hungry = creature.hunger >= hunger_threshold
        if is_hungry:
            return self._food_seeking_intent(creature, nearest_food)

        # Reproduction willingness differs slightly across individuals.
        reproduction_hunger_limit = self._effective_reproduction_hunger_limit(creature, hunger_threshold)
        if can_reproduce and creature.hunger <= reproduction_hunger_limit:
            return CreatureIntent(action=self.ACTION_REPRODUCE)

        return CreatureIntent(action=self.ACTION_WANDER)

    def _food_seeking_intent(self, creature: Creature, nearest_food: Optional[FoodSource]) -> CreatureIntent:
        if nearest_food is None:
            return CreatureIntent(action=self.ACTION_SEARCH_FOOD)

        food_distance = creature.distance_to(nearest_food.x, nearest_food.y)
        effective_food_detection_range = self._effective_food_detection_range(creature)
        if food_distance <= effective_food_detection_range:
            return CreatureIntent(action=self.ACTION_MOVE_TO_FOOD, target_food_id=nearest_food.food_id)

        return CreatureIntent(action=self.ACTION_SEARCH_FOOD)

    # THREAT/FLEE: perception helper to find the nearest valid threat.
    def _nearest_threat(
        self,
        creature: Creature,
        nearby_creatures: Iterable[Creature] | None,
    ) -> Creature | None:
        if nearby_creatures is None:
            return None

        effective_threat_detection_range = self._effective_threat_detection_range(creature)
        if effective_threat_detection_range <= 0.0:
            return None

        best_threat: Creature | None = None
        best_distance_sq = float("inf")
        max_axis_distance = effective_threat_detection_range
        max_distance_sq = effective_threat_detection_range * effective_threat_detection_range

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

    # THREAT/FLEE: simple threat model based on hunger and power ratio.
    def _is_threat(self, creature: Creature, other: Creature) -> bool:
        if other.hunger < self.hunger_seek_threshold:
            return False

        creature_power = creature.traits.speed * creature.traits.max_energy
        other_power = other.traits.speed * other.traits.max_energy

        behavior_bias = 0.25 * (creature.traits.dominance - creature.traits.prudence)
        # Light individual risk bias:
        # - higher risk_taking -> slightly less sensitive to borderline threats.
        # - lower risk_taking -> slightly more sensitive.
        risk_bias = 0.15 * (creature.traits.risk_taking - 1.0)
        effective_ratio = max(1.0, self.threat_strength_ratio * (1.0 + behavior_bias + risk_bias))
        return other_power >= creature_power * effective_ratio

    def _effective_food_detection_range(self, creature: Creature) -> float:
        return max(0.0, self.food_detection_range * creature.traits.food_perception)

    def _effective_threat_detection_range(self, creature: Creature) -> float:
        return max(0.0, self.threat_detection_range * creature.traits.threat_perception)

    def _effective_hunger_seek_threshold(self, creature: Creature) -> float:
        threshold = self.hunger_seek_threshold
        threshold -= 0.05 * (creature.traits.prudence - 1.0)
        threshold += 0.03 * (creature.traits.dominance - 1.0)
        return max(0.0, min(1.0, threshold))

    def _effective_reproduction_hunger_limit(
        self, creature: Creature, hunger_threshold: float
    ) -> float:
        limit = hunger_threshold
        limit *= 1.0 + (0.25 * (creature.traits.repro_drive - 1.0))
        limit -= 0.02 * (creature.traits.prudence - 1.0)
        return max(0.0, min(1.0, limit))
