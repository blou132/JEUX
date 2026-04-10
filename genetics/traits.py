from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneticTraits:
    speed: float = 1.0
    metabolism: float = 1.0
    max_energy: float = 100.0

    def clamp(self) -> "GeneticTraits":
        self.speed = max(0.1, self.speed)
        self.metabolism = max(0.1, self.metabolism)
        self.max_energy = max(1.0, self.max_energy)
        return self
