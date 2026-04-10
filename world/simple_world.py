from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .food import FoodField, FoodSource
from .map import SimpleMap


@dataclass
class FoodSpawnConfig:
    initial_food_count: int = 40
    min_food_count: int = 20
    food_energy_base: float = 35.0
    food_energy_variation: float = 10.0


class SimpleWorld:
    def __init__(
        self,
        world_map: SimpleMap,
        spawn_config: FoodSpawnConfig | None = None,
        random_source: Random | None = None,
    ) -> None:
        self.map = world_map
        self.spawn_config = spawn_config or FoodSpawnConfig()
        self.random_source = random_source or Random()
        self.food_field = FoodField()
        self._food_counter = 0
        self.seed_food(self.spawn_config.initial_food_count)

    def seed_food(self, count: int) -> None:
        if count < 0:
            raise ValueError("count must be >= 0")
        for _ in range(count):
            self._spawn_one_food()

    def tick(self) -> None:
        missing = self.spawn_config.min_food_count - self.food_field.get_food_count()
        if missing > 0:
            self.seed_food(missing)

    def _spawn_one_food(self) -> None:
        x, y = self.map.random_position(self.random_source)
        energy = self.spawn_config.food_energy_base + self.random_source.uniform(
            -self.spawn_config.food_energy_variation,
            self.spawn_config.food_energy_variation,
        )
        food = FoodSource(
            food_id=f"food_{self._food_counter}",
            x=x,
            y=y,
            energy_value=max(1.0, energy),
        )
        self._food_counter += 1
        self.food_field.add_food(food)
