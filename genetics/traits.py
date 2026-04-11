from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneticTraits:
    speed: float = 1.0
    metabolism: float = 1.0
    max_energy: float = 100.0

    # Behavioral traits (minimal MVP extension):
    # - prudence: higher means safer decisions, earlier threat avoidance.
    # - dominance: higher means less likely to treat borderline opponents as threats.
    # - repro_drive: higher means more willingness to prioritize reproduction.
    prudence: float = 1.0
    dominance: float = 1.0
    repro_drive: float = 1.0

    def clamp(self) -> "GeneticTraits":
        self.speed = max(0.1, self.speed)
        self.metabolism = max(0.1, self.metabolism)
        self.max_energy = max(1.0, self.max_energy)

        # Keep behavior traits in a narrow positive domain to avoid unstable extremes.
        self.prudence = max(0.2, min(2.0, self.prudence))
        self.dominance = max(0.2, min(2.0, self.dominance))
        self.repro_drive = max(0.2, min(2.0, self.repro_drive))
        return self
