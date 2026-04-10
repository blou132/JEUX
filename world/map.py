from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Tuple


@dataclass(frozen=True)
class SimpleMap:
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("map width and height must be > 0")

    def clamp(self, x: float, y: float) -> Tuple[float, float]:
        clamped_x = min(max(0.0, x), self.width)
        clamped_y = min(max(0.0, y), self.height)
        return clamped_x, clamped_y

    def random_position(self, rng: Random) -> Tuple[float, float]:
        return rng.uniform(0.0, self.width), rng.uniform(0.0, self.height)
