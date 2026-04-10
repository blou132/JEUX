from __future__ import annotations

from random import Random
from typing import List

from genetics import GeneticTraits
from world import SimpleMap

from .creature import Creature


def create_initial_population(count: int, world_map: SimpleMap, random_source: Random) -> List[Creature]:
    if count < 0:
        raise ValueError("count must be >= 0")

    population: List[Creature] = []
    for index in range(count):
        x, y = world_map.random_position(random_source)
        traits = GeneticTraits(
            speed=random_source.uniform(0.8, 1.2),
            metabolism=random_source.uniform(0.9, 1.1),
            max_energy=random_source.uniform(90.0, 110.0),
        ).clamp()

        creature = Creature(
            creature_id=f"creature_{index}",
            x=x,
            y=y,
            energy=traits.max_energy * 0.75,
            traits=traits,
            generation=0,
        )
        population.append(creature)

    return population
