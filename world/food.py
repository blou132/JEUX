from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Dict, Iterable, Optional


@dataclass
class FoodSource:
    food_id: str
    x: float
    y: float
    energy_value: float

    def consume(self, amount: float) -> float:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        eaten = min(self.energy_value, amount)
        self.energy_value -= eaten
        return eaten


class FoodField:
    def __init__(self) -> None:
        self._sources: Dict[str, FoodSource] = {}

    def add_food(self, source: FoodSource) -> None:
        self._sources[source.food_id] = source

    def get_food(self, food_id: str) -> Optional[FoodSource]:
        return self._sources.get(food_id)

    def get_nearest_food(self, x: float, y: float) -> Optional[FoodSource]:
        best_source: Optional[FoodSource] = None
        best_distance = float("inf")

        for source in self._sources.values():
            if source.energy_value <= 0:
                continue
            distance = hypot(source.x - x, source.y - y)
            if distance < best_distance:
                best_source = source
                best_distance = distance
        return best_source

    def consume(self, food_id: str, amount: float) -> float:
        source = self._sources.get(food_id)
        if source is None:
            return 0.0
        eaten = source.consume(amount)
        if source.energy_value <= 0:
            del self._sources[food_id]
        return eaten

    def get_food_count(self) -> int:
        return len(self._sources)

    def get_total_food_energy(self) -> float:
        return sum(source.energy_value for source in self._sources.values() if source.energy_value > 0)

    def iter_sources(self) -> Iterable[FoodSource]:
        return self._sources.values()
