from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from random import Random
from typing import Dict, Tuple

from .food import FoodField, FoodSource
from .map import SimpleMap


@dataclass
class FoodSpawnConfig:
    initial_food_count: int = 40
    min_food_count: int = 20
    food_energy_base: float = 35.0
    food_energy_variation: float = 10.0
    fertility_cols: int = 4
    fertility_rows: int = 3
    fertility_amplitude: float = 0.30
    fertility_energy_influence: float = 0.15
    spawn_candidate_count: int = 3


class SimpleWorld:
    _RICH_THRESHOLD = 1.12
    _POOR_THRESHOLD = 0.88

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

        self._validate_spawn_config()
        self._fertility_grid = self._build_fertility_grid()

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

    def fertility_at(self, x: float, y: float) -> float:
        row, col = self._cell_from_position(x, y)
        return self._fertility_grid[row][col]

    def get_fertility_zone(self, x: float, y: float) -> str:
        fertility = self.fertility_at(x, y)
        if fertility >= self._RICH_THRESHOLD:
            return "rich"
        if fertility <= self._POOR_THRESHOLD:
            return "poor"
        return "neutral"

    def get_food_zone_stats(self) -> Dict[str, float | int]:
        rich = 0
        poor = 0
        neutral = 0
        fertility_sum = 0.0
        count = 0

        for source in self.food_field.iter_sources():
            fertility = self.fertility_at(source.x, source.y)
            fertility_sum += fertility
            count += 1
            if fertility >= self._RICH_THRESHOLD:
                rich += 1
            elif fertility <= self._POOR_THRESHOLD:
                poor += 1
            else:
                neutral += 1

        avg_fertility = 1.0 if count == 0 else fertility_sum / count
        return {
            "rich": rich,
            "neutral": neutral,
            "poor": poor,
            "avg_fertility": avg_fertility,
            "total": count,
        }

    def _spawn_one_food(self) -> None:
        x, y, fertility = self._pick_spawn_position()

        energy = self.spawn_config.food_energy_base + self.random_source.uniform(
            -self.spawn_config.food_energy_variation,
            self.spawn_config.food_energy_variation,
        )
        energy_multiplier = 1.0 + (
            (fertility - 1.0) * self.spawn_config.fertility_energy_influence
        )
        food = FoodSource(
            food_id=f"food_{self._food_counter}",
            x=x,
            y=y,
            energy_value=max(1.0, energy * energy_multiplier),
        )
        self._food_counter += 1
        self.food_field.add_food(food)

    def _pick_spawn_position(self) -> Tuple[float, float, float]:
        best_x, best_y = self.map.random_position(self.random_source)
        best_fertility = self.fertility_at(best_x, best_y)

        for _ in range(self.spawn_config.spawn_candidate_count - 1):
            candidate_x, candidate_y = self.map.random_position(self.random_source)
            candidate_fertility = self.fertility_at(candidate_x, candidate_y)
            if candidate_fertility > best_fertility:
                best_x = candidate_x
                best_y = candidate_y
                best_fertility = candidate_fertility

        return best_x, best_y, best_fertility

    def _cell_from_position(self, x: float, y: float) -> Tuple[int, int]:
        cols = self.spawn_config.fertility_cols
        rows = self.spawn_config.fertility_rows

        if self.map.width <= 0 or self.map.height <= 0:
            return 0, 0

        clamped_x = min(max(0.0, x), self.map.width)
        clamped_y = min(max(0.0, y), self.map.height)

        col = min(cols - 1, int((clamped_x / self.map.width) * cols))
        row = min(rows - 1, int((clamped_y / self.map.height) * rows))
        return row, col

    def _build_fertility_grid(self) -> list[list[float]]:
        cols = self.spawn_config.fertility_cols
        rows = self.spawn_config.fertility_rows
        amplitude = self.spawn_config.fertility_amplitude

        grid: list[list[float]] = []
        for row in range(rows):
            row_values: list[float] = []
            for col in range(cols):
                phase_x = ((col + 0.5) / cols) * 2.0 * pi
                phase_y = ((row + 0.5) / rows) * 2.0 * pi
                variation = sin(phase_x) * cos(phase_y)
                fertility = 1.0 + (amplitude * variation)
                row_values.append(max(0.1, fertility))
            grid.append(row_values)
        return grid

    def _validate_spawn_config(self) -> None:
        if self.spawn_config.fertility_cols <= 0 or self.spawn_config.fertility_rows <= 0:
            raise ValueError("fertility_cols and fertility_rows must be > 0")
        if self.spawn_config.spawn_candidate_count <= 0:
            raise ValueError("spawn_candidate_count must be > 0")
        if self.spawn_config.fertility_amplitude < 0:
            raise ValueError("fertility_amplitude must be >= 0")
        if self.spawn_config.fertility_energy_influence < 0:
            raise ValueError("fertility_energy_influence must be >= 0")

