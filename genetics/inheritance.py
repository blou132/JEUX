from __future__ import annotations

import random
from typing import Optional

from .traits import GeneticTraits


def _mutate_value(base_value: float, mutation_variation: float, rng: random.Random) -> float:
    # Simple mutation: random percentage in [-variation, +variation].
    delta = rng.uniform(-mutation_variation, mutation_variation)
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

    child_traits = GeneticTraits(
        speed=_mutate_value(avg_speed, mutation_variation, random_source),
        metabolism=_mutate_value(avg_metabolism, mutation_variation, random_source),
        max_energy=_mutate_value(avg_max_energy, mutation_variation, random_source),
    )
    return child_traits.clamp()
