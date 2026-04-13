from __future__ import annotations

import random
from typing import Optional

from .traits import GeneticTraits


def _mutate_with_delta(base_value: float, delta: float) -> float:
    return base_value * (1.0 + delta)


def inherit_traits(
    parent_a: GeneticTraits,
    parent_b: GeneticTraits,
    mutation_variation: float = 0.1,
    rng: Optional[random.Random] = None,
) -> GeneticTraits:
    if mutation_variation < 0:
        raise ValueError("mutation_variation must be >= 0")

    random_source = rng or random.Random()

    avg_speed = (parent_a.speed + parent_b.speed) / 2.0
    avg_metabolism = (parent_a.metabolism + parent_b.metabolism) / 2.0
    avg_max_energy = (parent_a.max_energy + parent_b.max_energy) / 2.0
    avg_energy_efficiency = (parent_a.energy_efficiency + parent_b.energy_efficiency) / 2.0
    avg_exhaustion_resistance = (
        parent_a.exhaustion_resistance + parent_b.exhaustion_resistance
    ) / 2.0
    avg_prudence = (parent_a.prudence + parent_b.prudence) / 2.0
    avg_dominance = (parent_a.dominance + parent_b.dominance) / 2.0
    avg_repro_drive = (parent_a.repro_drive + parent_b.repro_drive) / 2.0
    avg_memory_focus = (parent_a.memory_focus + parent_b.memory_focus) / 2.0
    avg_social_sensitivity = (parent_a.social_sensitivity + parent_b.social_sensitivity) / 2.0
    avg_food_perception = (parent_a.food_perception + parent_b.food_perception) / 2.0
    avg_threat_perception = (parent_a.threat_perception + parent_b.threat_perception) / 2.0
    avg_risk_taking = (parent_a.risk_taking + parent_b.risk_taking) / 2.0

    # Keep the same number of RNG draws as the original MVP inheritance logic
    # so overall simulation dynamics stay comparable.
    delta_speed = random_source.uniform(-mutation_variation, mutation_variation)
    delta_metabolism = random_source.uniform(-mutation_variation, mutation_variation)
    delta_max_energy = random_source.uniform(-mutation_variation, mutation_variation)

    behavior_delta = (delta_speed + delta_metabolism + delta_max_energy) / 3.0

    child_traits = GeneticTraits(
        speed=_mutate_with_delta(avg_speed, delta_speed),
        metabolism=_mutate_with_delta(avg_metabolism, delta_metabolism),
        max_energy=_mutate_with_delta(avg_max_energy, delta_max_energy),
        energy_efficiency=_mutate_with_delta(avg_energy_efficiency, delta_metabolism),
        exhaustion_resistance=_mutate_with_delta(avg_exhaustion_resistance, delta_max_energy),
        prudence=_mutate_with_delta(avg_prudence, behavior_delta),
        dominance=_mutate_with_delta(avg_dominance, delta_speed),
        repro_drive=_mutate_with_delta(avg_repro_drive, delta_metabolism),
        memory_focus=_mutate_with_delta(avg_memory_focus, behavior_delta),
        food_perception=_mutate_with_delta(avg_food_perception, delta_metabolism),
        social_sensitivity=_mutate_with_delta(avg_social_sensitivity, delta_max_energy),
        threat_perception=_mutate_with_delta(avg_threat_perception, delta_max_energy),
        risk_taking=_mutate_with_delta(avg_risk_taking, behavior_delta),
    )
    return child_traits.clamp()
