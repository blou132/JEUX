from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Optional, Tuple

from genetics import GeneticTraits


@dataclass
class Creature:
    creature_id: str
    x: float
    y: float
    energy: float = 100.0
    max_energy: Optional[float] = None
    alive: bool = True
    traits: GeneticTraits = field(default_factory=GeneticTraits)
    generation: int = 0
    age: float = 0.0
    parent_ids: Optional[Tuple[str, str]] = None

    def __post_init__(self) -> None:
        if self.max_energy is None:
            self.max_energy = self.traits.max_energy
        else:
            self.traits.max_energy = self.max_energy
        self.traits.clamp()
        self.max_energy = self.traits.max_energy
        self.energy = max(0.0, min(self.energy, self.max_energy))
        if self.energy == 0.0:
            self.alive = False

    @property
    def hunger(self) -> float:
        """Normalized hunger from 0.0 (full) to 1.0 (starving)."""
        if not self.alive or self.max_energy <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - (self.energy / self.max_energy)))

    def grow_older(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")
        if self.alive:
            self.age += dt

    def drain_energy(self, dt: float, drain_rate: float) -> None:
        if not self.alive:
            return
        if dt < 0:
            raise ValueError("dt must be >= 0")
        if drain_rate < 0:
            raise ValueError("drain_rate must be >= 0")

        effective_drain = drain_rate * self.traits.metabolism
        self.energy = max(0.0, self.energy - (effective_drain * dt))
        if self.energy == 0.0:
            self.alive = False

    def add_energy(self, amount: float) -> None:
        if not self.alive:
            return
        if amount < 0:
            raise ValueError("amount must be >= 0")
        self.energy = min(self.max_energy, self.energy + amount)

    def spend_energy(self, amount: float) -> None:
        if not self.alive:
            return
        if amount < 0:
            raise ValueError("amount must be >= 0")
        self.energy = max(0.0, self.energy - amount)
        if self.energy == 0.0:
            self.alive = False

    def distance_to(self, target_x: float, target_y: float) -> float:
        return hypot(target_x - self.x, target_y - self.y)

    def move_towards(self, target_x: float, target_y: float, max_distance: float) -> bool:
        """Move toward a target. Returns True if target is reached this step."""
        if not self.alive:
            return False
        if max_distance < 0:
            raise ValueError("max_distance must be >= 0")

        distance = self.distance_to(target_x, target_y)
        if distance == 0.0:
            return True
        if max_distance >= distance:
            self.x = target_x
            self.y = target_y
            return True

        ratio = max_distance / distance
        self.x += (target_x - self.x) * ratio
        self.y += (target_y - self.y) * ratio
        return False
