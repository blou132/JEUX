from __future__ import annotations

from typing import Dict, List

from ai import CreatureIntent, HungerAI
from simulation import HungerSimulation


def build_hunger_snapshot(simulation: HungerSimulation) -> Dict[str, object]:
    creatures: List[Dict[str, object]] = []
    for creature in simulation.creatures:
        intent = simulation.last_intents.get(creature.creature_id)
        flee_distance = simulation.flee_threat_distance_last_tick.get(creature.creature_id)
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
                    "energy_efficiency": round(creature.traits.energy_efficiency, 3),
                    "exhaustion_resistance": round(creature.traits.exhaustion_resistance, 3),
                    "prudence": round(creature.traits.prudence, 3),
                    "dominance": round(creature.traits.dominance, 3),
                    "repro_drive": round(creature.traits.repro_drive, 3),
                    "memory_focus": round(creature.traits.memory_focus, 3),
                    "social_sensitivity": round(creature.traits.social_sensitivity, 3),
                    "food_perception": round(creature.traits.food_perception, 3),
                    "threat_perception": round(creature.traits.threat_perception, 3),
                },
                "intent": None if intent is None else intent.action,
                "action_reason": _intent_reason(intent),
                "threat_target_id": (
                    None
                    if intent is None or intent.action != HungerAI.ACTION_FLEE
                    else intent.target_creature_id
                ),
                "threat_distance": None if flee_distance is None else round(flee_distance, 3),
                "has_food_memory": creature.has_food_memory,
                "food_memory_zone": None
                if creature.last_food_zone is None
                else [round(creature.last_food_zone[0], 3), round(creature.last_food_zone[1], 3)],
                "food_memory_ttl": round(creature.food_memory_ttl, 3),
                "has_danger_memory": creature.has_danger_memory,
                "danger_memory_zone": None
                if creature.last_danger_zone is None
                else [round(creature.last_danger_zone[0], 3), round(creature.last_danger_zone[1], 3)],
                "danger_memory_ttl": round(creature.danger_memory_ttl, 3),
            }
        )

    return {
        "alive_count": simulation.get_alive_count(),
        "dead_count": simulation.get_dead_count(),
        "births_last_tick": simulation.births_last_tick,
        "deaths_last_tick": simulation.deaths_last_tick,
        "flees_last_tick": simulation.flees_last_tick,
        "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
        "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
        "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
        "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
        "total_births": simulation.total_births,
        "total_deaths": simulation.total_deaths,
        "total_flees": simulation.total_flees,
        "total_food_memory_guided_moves": simulation.total_food_memory_guided_moves,
        "total_danger_memory_avoid_moves": simulation.total_danger_memory_avoid_moves,
        "social_follow_moves_last_tick": simulation.social_follow_moves_last_tick,
        "social_flee_boosted_last_tick": simulation.social_flee_boosted_last_tick,
        "social_influenced_creatures_last_tick": simulation.social_influenced_creatures_last_tick,
        "avg_social_flee_multiplier_last_tick": simulation.avg_social_flee_multiplier_last_tick,
        "total_social_follow_moves": simulation.total_social_follow_moves,
        "total_social_flee_boosted": simulation.total_social_flee_boosted,
        "total_social_influenced_creatures": simulation.total_social_influenced_creatures,
        "creatures": creatures,
        "food_sources_count": simulation.food_field.get_food_count(),
        "food_remaining": round(simulation.food_field.get_total_food_energy(), 3),
    }


def _intent_reason(intent: CreatureIntent | None) -> str | None:
    if intent is None:
        return None
    if intent.action == HungerAI.ACTION_DEAD:
        return "dead"
    if intent.action == HungerAI.ACTION_FLEE:
        return "threat_detected"
    if intent.action in (HungerAI.ACTION_SEARCH_FOOD, HungerAI.ACTION_MOVE_TO_FOOD):
        return "hunger"
    if intent.action == HungerAI.ACTION_REPRODUCE:
        return "reproduction_ready"
    if intent.action == HungerAI.ACTION_WANDER:
        return "idle"
    return "other"
