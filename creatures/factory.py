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
            energy_efficiency=random_source.uniform(0.97, 1.03),
            exhaustion_resistance=random_source.uniform(0.97, 1.03),
            prudence=random_source.uniform(0.8, 1.2),
            dominance=random_source.uniform(0.8, 1.2),
            repro_drive=random_source.uniform(0.8, 1.2),
            memory_focus=random_source.uniform(0.9, 1.1),
            food_perception=random_source.uniform(0.95, 1.05),
            social_sensitivity=random_source.uniform(0.9, 1.1),
            threat_perception=random_source.uniform(0.95, 1.05),
            risk_taking=random_source.uniform(0.95, 1.05),
            behavior_persistence=random_source.uniform(0.95, 1.05),
            exploration_bias=random_source.uniform(0.95, 1.05),
            density_preference=random_source.uniform(0.95, 1.05),
            mobility_efficiency=random_source.uniform(0.97, 1.03),
            stress_tolerance=random_source.uniform(0.97, 1.03),
            longevity_factor=random_source.uniform(0.97, 1.03),
            environmental_tolerance=random_source.uniform(0.97, 1.03),
            reproduction_timing=random_source.uniform(0.97, 1.03),
            hunger_sensitivity=random_source.uniform(0.97, 1.03),
            gregariousness=random_source.uniform(0.97, 1.03),
            competition_tolerance=random_source.uniform(0.97, 1.03),
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

