from __future__ import annotations

from typing import Dict

from simulation import HungerSimulation


def build_population_stats(simulation: HungerSimulation) -> Dict[str, float | int]:
    total = simulation.get_total_count()
    alive = simulation.get_alive_count()
    dead = simulation.get_dead_count()

    if total == 0:
        return {
            "population": 0,
            "alive": 0,
            "dead": 0,
            "food_sources": simulation.food_field.get_food_count(),
            "food_remaining": 0.0,
            "avg_energy": 0.0,
            "avg_age": 0.0,
            "avg_generation": 0.0,
            "avg_speed": 0.0,
            "avg_metabolism": 0.0,
            "births_last_tick": simulation.births_last_tick,
            "total_births": simulation.total_births,
            "deaths_last_tick": simulation.deaths_last_tick,
            "total_deaths": simulation.total_deaths,
        }

    avg_energy = sum(c.energy for c in simulation.creatures) / total
    avg_age = sum(c.age for c in simulation.creatures) / total
    avg_generation = sum(c.generation for c in simulation.creatures) / total
    avg_speed = sum(c.traits.speed for c in simulation.creatures) / total
    avg_metabolism = sum(c.traits.metabolism for c in simulation.creatures) / total

    return {
        "population": total,
        "alive": alive,
        "dead": dead,
        "food_sources": simulation.food_field.get_food_count(),
        "food_remaining": simulation.food_field.get_total_food_energy(),
        "avg_energy": avg_energy,
        "avg_age": avg_age,
        "avg_generation": avg_generation,
        "avg_speed": avg_speed,
        "avg_metabolism": avg_metabolism,
        "births_last_tick": simulation.births_last_tick,
        "total_births": simulation.total_births,
        "deaths_last_tick": simulation.deaths_last_tick,
        "total_deaths": simulation.total_deaths,
    }


def build_generation_distribution(simulation: HungerSimulation) -> Dict[int, int]:
    distribution: Dict[int, int] = {}
    for creature in simulation.creatures:
        distribution[creature.generation] = distribution.get(creature.generation, 0) + 1
    return distribution
