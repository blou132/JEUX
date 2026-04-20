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
    last_food_zone: Optional[Tuple[float, float]] = None
    food_memory_ttl: float = 0.0
    last_danger_zone: Optional[Tuple[float, float]] = None
    danger_memory_ttl: float = 0.0

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

    @property
    def has_food_memory(self) -> bool:
        return self.food_memory_ttl > 0.0 and self.last_food_zone is not None

    @property
    def has_danger_memory(self) -> bool:
        return self.danger_memory_ttl > 0.0 and self.last_danger_zone is not None

    def grow_older(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")
        if self.alive:
            self.age += dt

    def decay_memory(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")

        self.food_memory_ttl = max(0.0, self.food_memory_ttl - dt)
        if self.food_memory_ttl == 0.0:
            self.last_food_zone = None

        self.danger_memory_ttl = max(0.0, self.danger_memory_ttl - dt)
        if self.danger_memory_ttl == 0.0:
            self.last_danger_zone = None

    def remember_food_zone(self, x: float, y: float, ttl: float) -> None:
        if ttl < 0:
            raise ValueError("ttl must be >= 0")
        self.last_food_zone = (x, y)
        self.food_memory_ttl = ttl

    def remember_danger_zone(self, x: float, y: float, ttl: float) -> None:
        if ttl < 0:
            raise ValueError("ttl must be >= 0")
        self.last_danger_zone = (x, y)
        self.danger_memory_ttl = ttl

    def drain_energy(self, dt: float, drain_rate: float, extra_multiplier: float = 1.0) -> None:
        if not self.alive:
            return
        if dt < 0:
            raise ValueError("dt must be >= 0")
        if drain_rate < 0:
            raise ValueError("drain_rate must be >= 0")
        if extra_multiplier < 0:
            raise ValueError("extra_multiplier must be >= 0")

        efficiency_multiplier = 1.0 - (0.25 * (self.traits.energy_efficiency - 1.0))
        effective_drain = (
            drain_rate
            * self.traits.metabolism
            * max(0.1, efficiency_multiplier)
            * max(0.1, extra_multiplier)
        )
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



