from __future__ import annotations

from typing import Dict, List

from simulation import HungerSimulation


def build_hunger_snapshot(simulation: HungerSimulation) -> Dict[str, object]:
    creatures: List[Dict[str, object]] = []
    for creature in simulation.creatures:
        intent = simulation.last_intents.get(creature.creature_id)
        creatures.append(
            {
                "id": creature.creature_id,
                "alive": creature.alive,
                "age": round(creature.age, 2),
                "energy": round(creature.energy, 3),
                "hunger": round(creature.hunger, 3),
                "generation": creature.generation,
                "traits": {
                    "speed": round(creature.traits.speed, 3),
                    "metabolism": round(creature.traits.metabolism, 3),
                    "max_energy": round(creature.traits.max_energy, 3),
                },
                "intent": None if intent is None else intent.action,
            }
        )

    return {
        "alive_count": simulation.get_alive_count(),
        "dead_count": simulation.get_dead_count(),
        "births_last_tick": simulation.births_last_tick,
        "deaths_last_tick": simulation.deaths_last_tick,
        "total_births": simulation.total_births,
        "total_deaths": simulation.total_deaths,
        "creatures": creatures,
        "food_sources_count": simulation.food_field.get_food_count(),
        "food_remaining": round(simulation.food_field.get_total_food_energy(), 3),
    }
