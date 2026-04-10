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
        "creatures": creatures,
        "food_sources_count": simulation.food_field.get_food_count(),
    }
