from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneticTraits:
    speed: float = 1.0
    metabolism: float = 1.0
    max_energy: float = 100.0

    # Energy traits:
    # - energy_efficiency: >1.0 reduces passive drain, <1.0 increases it.
    # - exhaustion_resistance: >1.0 reduces reproduction exhaustion cost.
    energy_efficiency: float = 1.0
    exhaustion_resistance: float = 1.0

    # Behavioral traits (minimal MVP extension):
    # - prudence: higher means safer decisions, earlier threat avoidance.
    # - dominance: higher means less likely to treat borderline opponents as threats.
    # - repro_drive: higher means more willingness to prioritize reproduction.
    # - memory_focus: higher means stronger tendency to reuse local memories.
    # - social_sensitivity: higher means stronger responsiveness to nearby social cues.
    # - food_perception: higher means slightly farther food detection.
    # - threat_perception: higher means slightly farther threat detection.
    prudence: float = 1.0
    dominance: float = 1.0
    repro_drive: float = 1.0
    memory_focus: float = 1.0
    social_sensitivity: float = 1.0
    food_perception: float = 1.0
    threat_perception: float = 1.0

    def clamp(self) -> "GeneticTraits":
        self.speed = max(0.1, self.speed)
        self.metabolism = max(0.1, self.metabolism)
        self.max_energy = max(1.0, self.max_energy)

        # Keep endurance traits in a tight range for a light gameplay effect.
        self.energy_efficiency = max(0.9, min(1.1, self.energy_efficiency))
        self.exhaustion_resistance = max(0.9, min(1.1, self.exhaustion_resistance))

        # Keep behavior traits in a narrow positive domain to avoid unstable extremes.
        self.prudence = max(0.2, min(2.0, self.prudence))
        self.dominance = max(0.2, min(2.0, self.dominance))
        self.repro_drive = max(0.2, min(2.0, self.repro_drive))
        self.memory_focus = max(0.5, min(1.5, self.memory_focus))
        self.social_sensitivity = max(0.5, min(1.5, self.social_sensitivity))
        self.food_perception = max(0.7, min(1.3, self.food_perception))
        self.threat_perception = max(0.7, min(1.3, self.threat_perception))
        return self

