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
                    "risk_taking": round(creature.traits.risk_taking, 3),
                    "behavior_persistence": round(creature.traits.behavior_persistence, 3),
                    "exploration_bias": round(creature.traits.exploration_bias, 3),
                    "density_preference": round(creature.traits.density_preference, 3),
                    "mobility_efficiency": round(creature.traits.mobility_efficiency, 3),
                    "stress_tolerance": round(creature.traits.stress_tolerance, 3),
                    "longevity_factor": round(creature.traits.longevity_factor, 3),
                    "environmental_tolerance": round(creature.traits.environmental_tolerance, 3),
                    "reproduction_timing": round(creature.traits.reproduction_timing, 3),
                    "hunger_sensitivity": round(creature.traits.hunger_sensitivity, 3),
                    "gregariousness": round(creature.traits.gregariousness, 3),
                },
                "intent": None if intent is None else intent.action,
                "action_reason": _intent_reason(intent),
                "persisted_from_previous": False if intent is None else bool(intent.persisted_from_previous),
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

    total_creatures = len(simulation.creatures)
    avg_exploration_bias_population = (
        sum(creature.traits.exploration_bias for creature in simulation.creatures) / total_creatures
        if total_creatures > 0
        else 0.0
    )
    exploration_bias_explore_users_avg_last_tick = (
        simulation.exploration_bias_sum_explore_last_tick / simulation.exploration_bias_explore_moves_last_tick
        if simulation.exploration_bias_explore_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_explore_users_avg_total = (
        simulation.total_exploration_bias_sum_explore / simulation.total_exploration_bias_explore_moves
        if simulation.total_exploration_bias_explore_moves > 0
        else 0.0
    )
    exploration_bias_settle_users_avg_last_tick = (
        simulation.exploration_bias_sum_settle_last_tick / simulation.exploration_bias_settle_moves_last_tick
        if simulation.exploration_bias_settle_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_settle_users_avg_total = (
        simulation.total_exploration_bias_sum_settle / simulation.total_exploration_bias_settle_moves
        if simulation.total_exploration_bias_settle_moves > 0
        else 0.0
    )
    avg_density_preference_population = (
        sum(creature.traits.density_preference for creature in simulation.creatures) / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_mobility_efficiency_population = (
        sum(creature.traits.mobility_efficiency for creature in simulation.creatures) / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_stress_tolerance_population = (
        sum(creature.traits.stress_tolerance for creature in simulation.creatures) / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_longevity_factor_population = (
        sum(creature.traits.longevity_factor for creature in simulation.creatures) / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_environmental_tolerance_population = (
        sum(creature.traits.environmental_tolerance for creature in simulation.creatures)
        / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_reproduction_timing_population = (
        sum(creature.traits.reproduction_timing for creature in simulation.creatures)
        / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_hunger_sensitivity_population = (
        sum(creature.traits.hunger_sensitivity for creature in simulation.creatures)
        / total_creatures
        if total_creatures > 0
        else 0.0
    )
    avg_gregariousness_population = (
        sum(creature.traits.gregariousness for creature in simulation.creatures)
        / total_creatures
        if total_creatures > 0
        else 0.0
    )
    density_preference_seek_users_avg_last_tick = (
        simulation.density_preference_sum_seek_last_tick / simulation.density_preference_seek_moves_last_tick
        if simulation.density_preference_seek_moves_last_tick > 0
        else 0.0
    )
    density_preference_seek_users_avg_total = (
        simulation.total_density_preference_sum_seek / simulation.total_density_preference_seek_moves
        if simulation.total_density_preference_seek_moves > 0
        else 0.0
    )
    density_preference_avoid_users_avg_last_tick = (
        simulation.density_preference_sum_avoid_last_tick / simulation.density_preference_avoid_moves_last_tick
        if simulation.density_preference_avoid_moves_last_tick > 0
        else 0.0
    )
    density_preference_avoid_users_avg_total = (
        simulation.total_density_preference_sum_avoid / simulation.total_density_preference_avoid_moves
        if simulation.total_density_preference_avoid_moves > 0
        else 0.0
    )
    gregariousness_seek_users_avg_last_tick = (
        simulation.gregariousness_sum_seek_last_tick / simulation.gregariousness_seek_moves_last_tick
        if simulation.gregariousness_seek_moves_last_tick > 0
        else 0.0
    )
    gregariousness_seek_users_avg_total = (
        simulation.total_gregariousness_sum_seek / simulation.total_gregariousness_seek_moves
        if simulation.total_gregariousness_seek_moves > 0
        else 0.0
    )
    gregariousness_avoid_users_avg_last_tick = (
        simulation.gregariousness_sum_avoid_last_tick / simulation.gregariousness_avoid_moves_last_tick
        if simulation.gregariousness_avoid_moves_last_tick > 0
        else 0.0
    )
    gregariousness_avoid_users_avg_total = (
        simulation.total_gregariousness_sum_avoid / simulation.total_gregariousness_avoid_moves
        if simulation.total_gregariousness_avoid_moves > 0
        else 0.0
    )
    age_wear_multiplier_avg_last_tick = (
        simulation.age_wear_multiplier_sum_last_tick / simulation.age_wear_active_events_last_tick
        if simulation.age_wear_active_events_last_tick > 0
        else 1.0
    )
    age_wear_multiplier_avg_total = (
        simulation.total_age_wear_multiplier_sum / simulation.total_age_wear_active_events
        if simulation.total_age_wear_active_events > 0
        else 1.0
    )
    longevity_factor_age_wear_users_avg_last_tick = (
        simulation.longevity_factor_sum_age_wear_last_tick / simulation.age_wear_active_events_last_tick
        if simulation.age_wear_active_events_last_tick > 0
        else 0.0
    )
    longevity_factor_age_wear_users_avg_total = (
        simulation.total_longevity_factor_sum_age_wear / simulation.total_age_wear_active_events
        if simulation.total_age_wear_active_events > 0
        else 0.0
    )
    environmental_tolerance_poor_users_avg_last_tick = (
        simulation.environmental_tolerance_sum_poor_drain_last_tick
        / simulation.poor_zone_drain_events_last_tick
        if simulation.poor_zone_drain_events_last_tick > 0
        else 0.0
    )
    environmental_tolerance_poor_users_avg_total = (
        simulation.total_environmental_tolerance_sum_poor_drain
        / simulation.total_poor_zone_drain_events
        if simulation.total_poor_zone_drain_events > 0
        else 0.0
    )
    environmental_tolerance_rich_users_avg_last_tick = (
        simulation.environmental_tolerance_sum_rich_drain_last_tick
        / simulation.rich_zone_drain_events_last_tick
        if simulation.rich_zone_drain_events_last_tick > 0
        else 0.0
    )
    environmental_tolerance_rich_users_avg_total = (
        simulation.total_environmental_tolerance_sum_rich_drain
        / simulation.total_rich_zone_drain_events
        if simulation.total_rich_zone_drain_events > 0
        else 0.0
    )
    zone_drain_multiplier_avg_last_tick = (
        simulation.zone_drain_multiplier_sum_last_tick / simulation.energy_drain_events_last_tick
        if simulation.energy_drain_events_last_tick > 0
        else 1.0
    )
    zone_drain_multiplier_avg_total = (
        simulation.total_zone_drain_multiplier_sum / simulation.total_energy_drain_events
        if simulation.total_energy_drain_events > 0
        else 1.0
    )
    reproduction_timing_reproduction_users_avg_last_tick = (
        simulation.reproduction_timing_sum_reproduction_last_tick / simulation.reproduction_cost_events_last_tick
        if simulation.reproduction_cost_events_last_tick > 0
        else 0.0
    )
    reproduction_timing_reproduction_users_avg_total = (
        simulation.total_reproduction_timing_sum_reproduction / simulation.total_reproduction_cost_events
        if simulation.total_reproduction_cost_events > 0
        else 0.0
    )
    reproduction_timing_threshold_multiplier_avg_last_tick = (
        simulation.reproduction_timing_threshold_multiplier_sum_reproduction_last_tick
        / simulation.reproduction_cost_events_last_tick
        if simulation.reproduction_cost_events_last_tick > 0
        else 1.0
    )
    reproduction_timing_threshold_multiplier_avg_total = (
        simulation.total_reproduction_timing_threshold_multiplier_sum_reproduction
        / simulation.total_reproduction_cost_events
        if simulation.total_reproduction_cost_events > 0
        else 1.0
    )
    hunger_sensitivity_search_users_avg_last_tick = (
        simulation.hunger_sensitivity_sum_search_last_tick / simulation.hunger_search_actions_last_tick
        if simulation.hunger_search_actions_last_tick > 0
        else 0.0
    )
    hunger_sensitivity_search_users_avg_total = (
        simulation.total_hunger_sensitivity_sum_search / simulation.total_hunger_search_actions
        if simulation.total_hunger_search_actions > 0
        else 0.0
    )
    mobility_efficiency_movement_users_avg_last_tick = (
        simulation.mobility_efficiency_sum_movement_last_tick / simulation.movement_actions_last_tick
        if simulation.movement_actions_last_tick > 0
        else 0.0
    )
    mobility_efficiency_movement_users_avg_total = (
        simulation.total_mobility_efficiency_sum_movement / simulation.total_movement_actions
        if simulation.total_movement_actions > 0
        else 0.0
    )
    movement_multiplier_avg_total = (
        simulation.total_movement_multiplier_sum / simulation.total_movement_actions
        if simulation.total_movement_actions > 0
        else 1.0
    )
    movement_distance_avg_total = (
        simulation.total_movement_distance_sum / simulation.total_movement_actions
        if simulation.total_movement_actions > 0
        else 0.0
    )
    stress_tolerance_pressure_users_avg_last_tick = (
        simulation.stress_tolerance_sum_pressure_last_tick / simulation.stress_pressure_events_last_tick
        if simulation.stress_pressure_events_last_tick > 0
        else 0.0
    )
    stress_tolerance_pressure_flee_users_avg_last_tick = (
        simulation.stress_tolerance_sum_pressure_flee_last_tick
        / simulation.stress_pressure_flee_events_last_tick
        if simulation.stress_pressure_flee_events_last_tick > 0
        else 0.0
    )

    return {
        "alive_count": simulation.get_alive_count(),
        "dead_count": simulation.get_dead_count(),
        "births_last_tick": simulation.births_last_tick,
        "deaths_last_tick": simulation.deaths_last_tick,
        "flees_last_tick": simulation.flees_last_tick,
        "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
        "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
        "borderline_threat_encounters_last_tick": simulation.borderline_threat_encounters_last_tick,
        "borderline_threat_flees_last_tick": simulation.borderline_threat_flees_last_tick,
        "borderline_threat_flee_rate_last_tick": (
            simulation.borderline_threat_flees_last_tick / simulation.borderline_threat_encounters_last_tick
            if simulation.borderline_threat_encounters_last_tick > 0
            else 0.0
        ),
        "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
        "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
        "total_births": simulation.total_births,
        "total_deaths": simulation.total_deaths,
        "total_flees": simulation.total_flees,
        "total_borderline_threat_encounters": simulation.total_borderline_threat_encounters,
        "total_borderline_threat_flees": simulation.total_borderline_threat_flees,
        "persistence_holds_last_tick": simulation.persistence_holds_last_tick,
        "total_persistence_holds": simulation.total_persistence_holds,
        "persistence_holding_creatures_last_tick": list(simulation.persistence_holding_creatures_last_tick),
        "search_wander_switches_last_tick": simulation.search_wander_switches_last_tick,
        "total_search_wander_switches": simulation.total_search_wander_switches,
        "search_wander_switches_prevented_last_tick": simulation.search_wander_switches_prevented_last_tick,
        "total_search_wander_switches_prevented": simulation.total_search_wander_switches_prevented,
        "search_wander_oscillation_events_last_tick": simulation.search_wander_oscillation_events_last_tick,
        "total_search_wander_oscillation_events": simulation.total_search_wander_oscillation_events,
        "exploration_bias_guided_moves_last_tick": simulation.exploration_bias_guided_moves_last_tick,
        "total_exploration_bias_guided_moves": simulation.total_exploration_bias_guided_moves,
        "exploration_bias_explore_moves_last_tick": simulation.exploration_bias_explore_moves_last_tick,
        "total_exploration_bias_explore_moves": simulation.total_exploration_bias_explore_moves,
        "exploration_bias_explore_users_avg_last_tick": exploration_bias_explore_users_avg_last_tick,
        "exploration_bias_explore_users_avg_total": exploration_bias_explore_users_avg_total,
        "exploration_bias_explore_usage_bias_last_tick": (
            exploration_bias_explore_users_avg_last_tick - avg_exploration_bias_population
            if simulation.exploration_bias_explore_moves_last_tick > 0
            else 0.0
        ),
        "exploration_bias_explore_usage_bias_total": (
            exploration_bias_explore_users_avg_total - avg_exploration_bias_population
            if simulation.total_exploration_bias_explore_moves > 0
            else 0.0
        ),
        "exploration_bias_settle_moves_last_tick": simulation.exploration_bias_settle_moves_last_tick,
        "total_exploration_bias_settle_moves": simulation.total_exploration_bias_settle_moves,
        "exploration_bias_settle_users_avg_last_tick": exploration_bias_settle_users_avg_last_tick,
        "exploration_bias_settle_users_avg_total": exploration_bias_settle_users_avg_total,
        "exploration_bias_settle_usage_bias_last_tick": (
            exploration_bias_settle_users_avg_last_tick - avg_exploration_bias_population
            if simulation.exploration_bias_settle_moves_last_tick > 0
            else 0.0
        ),
        "exploration_bias_settle_usage_bias_total": (
            exploration_bias_settle_users_avg_total - avg_exploration_bias_population
            if simulation.total_exploration_bias_settle_moves > 0
            else 0.0
        ),
        "avg_exploration_bias_anchor_distance_delta_last_tick": (
            simulation.avg_exploration_bias_anchor_distance_delta_last_tick
        ),
        "density_preference_guided_moves_last_tick": simulation.density_preference_guided_moves_last_tick,
        "total_density_preference_guided_moves": simulation.total_density_preference_guided_moves,
        "density_preference_seek_moves_last_tick": simulation.density_preference_seek_moves_last_tick,
        "total_density_preference_seek_moves": simulation.total_density_preference_seek_moves,
        "density_preference_seek_users_avg_last_tick": density_preference_seek_users_avg_last_tick,
        "density_preference_seek_users_avg_total": density_preference_seek_users_avg_total,
        "density_preference_seek_usage_bias_last_tick": (
            density_preference_seek_users_avg_last_tick - avg_density_preference_population
            if simulation.density_preference_seek_moves_last_tick > 0
            else 0.0
        ),
        "density_preference_seek_usage_bias_total": (
            density_preference_seek_users_avg_total - avg_density_preference_population
            if simulation.total_density_preference_seek_moves > 0
            else 0.0
        ),
        "density_preference_avoid_moves_last_tick": simulation.density_preference_avoid_moves_last_tick,
        "total_density_preference_avoid_moves": simulation.total_density_preference_avoid_moves,
        "density_preference_avoid_users_avg_last_tick": density_preference_avoid_users_avg_last_tick,
        "density_preference_avoid_users_avg_total": density_preference_avoid_users_avg_total,
        "density_preference_avoid_usage_bias_last_tick": (
            density_preference_avoid_users_avg_last_tick - avg_density_preference_population
            if simulation.density_preference_avoid_moves_last_tick > 0
            else 0.0
        ),
        "density_preference_avoid_usage_bias_total": (
            density_preference_avoid_users_avg_total - avg_density_preference_population
            if simulation.total_density_preference_avoid_moves > 0
            else 0.0
        ),
        "avg_density_preference_neighbor_count_last_tick": (
            simulation.density_preference_neighbor_count_sum_last_tick
            / simulation.density_preference_guided_moves_last_tick
            if simulation.density_preference_guided_moves_last_tick > 0
            else 0.0
        ),
        "avg_density_preference_center_distance_delta_last_tick": (
            simulation.avg_density_preference_center_distance_delta_last_tick
        ),
        "gregariousness_guided_moves_last_tick": simulation.gregariousness_guided_moves_last_tick,
        "total_gregariousness_guided_moves": simulation.total_gregariousness_guided_moves,
        "gregariousness_seek_moves_last_tick": simulation.gregariousness_seek_moves_last_tick,
        "total_gregariousness_seek_moves": simulation.total_gregariousness_seek_moves,
        "gregariousness_seek_users_avg_last_tick": gregariousness_seek_users_avg_last_tick,
        "gregariousness_seek_users_avg_total": gregariousness_seek_users_avg_total,
        "gregariousness_seek_usage_bias_last_tick": (
            gregariousness_seek_users_avg_last_tick - avg_gregariousness_population
            if simulation.gregariousness_seek_moves_last_tick > 0
            else 0.0
        ),
        "gregariousness_seek_usage_bias_total": (
            gregariousness_seek_users_avg_total - avg_gregariousness_population
            if simulation.total_gregariousness_seek_moves > 0
            else 0.0
        ),
        "gregariousness_avoid_moves_last_tick": simulation.gregariousness_avoid_moves_last_tick,
        "total_gregariousness_avoid_moves": simulation.total_gregariousness_avoid_moves,
        "gregariousness_avoid_users_avg_last_tick": gregariousness_avoid_users_avg_last_tick,
        "gregariousness_avoid_users_avg_total": gregariousness_avoid_users_avg_total,
        "gregariousness_avoid_usage_bias_last_tick": (
            gregariousness_avoid_users_avg_last_tick - avg_gregariousness_population
            if simulation.gregariousness_avoid_moves_last_tick > 0
            else 0.0
        ),
        "gregariousness_avoid_usage_bias_total": (
            gregariousness_avoid_users_avg_total - avg_gregariousness_population
            if simulation.total_gregariousness_avoid_moves > 0
            else 0.0
        ),
        "avg_gregariousness_neighbor_count_last_tick": (
            simulation.gregariousness_neighbor_count_sum_last_tick
            / simulation.gregariousness_guided_moves_last_tick
            if simulation.gregariousness_guided_moves_last_tick > 0
            else 0.0
        ),
        "avg_gregariousness_center_distance_delta_last_tick": (
            simulation.avg_gregariousness_center_distance_delta_last_tick
        ),
        "age_wear_active_events_last_tick": simulation.age_wear_active_events_last_tick,
        "total_age_wear_active_events": simulation.total_age_wear_active_events,
        "age_wear_multiplier_avg_last_tick": age_wear_multiplier_avg_last_tick,
        "age_wear_multiplier_avg_total": age_wear_multiplier_avg_total,
        "longevity_factor_age_wear_users_avg_last_tick": longevity_factor_age_wear_users_avg_last_tick,
        "longevity_factor_age_wear_users_avg_total": longevity_factor_age_wear_users_avg_total,
        "longevity_factor_age_wear_usage_bias_last_tick": (
            longevity_factor_age_wear_users_avg_last_tick - avg_longevity_factor_population
            if simulation.age_wear_active_events_last_tick > 0
            else 0.0
        ),
        "longevity_factor_age_wear_usage_bias_total": (
            longevity_factor_age_wear_users_avg_total - avg_longevity_factor_population
            if simulation.total_age_wear_active_events > 0
            else 0.0
        ),
        "poor_zone_drain_events_last_tick": simulation.poor_zone_drain_events_last_tick,
        "total_poor_zone_drain_events": simulation.total_poor_zone_drain_events,
        "rich_zone_drain_events_last_tick": simulation.rich_zone_drain_events_last_tick,
        "total_rich_zone_drain_events": simulation.total_rich_zone_drain_events,
        "zone_drain_multiplier_avg_last_tick": zone_drain_multiplier_avg_last_tick,
        "zone_drain_multiplier_avg_total": zone_drain_multiplier_avg_total,
        "environmental_tolerance_poor_users_avg_last_tick": environmental_tolerance_poor_users_avg_last_tick,
        "environmental_tolerance_poor_users_avg_total": environmental_tolerance_poor_users_avg_total,
        "environmental_tolerance_rich_users_avg_last_tick": environmental_tolerance_rich_users_avg_last_tick,
        "environmental_tolerance_rich_users_avg_total": environmental_tolerance_rich_users_avg_total,
        "environmental_tolerance_poor_usage_bias_last_tick": (
            environmental_tolerance_poor_users_avg_last_tick - avg_environmental_tolerance_population
            if simulation.poor_zone_drain_events_last_tick > 0
            else 0.0
        ),
        "environmental_tolerance_poor_usage_bias_total": (
            environmental_tolerance_poor_users_avg_total - avg_environmental_tolerance_population
            if simulation.total_poor_zone_drain_events > 0
            else 0.0
        ),
        "environmental_tolerance_rich_usage_bias_last_tick": (
            environmental_tolerance_rich_users_avg_last_tick - avg_environmental_tolerance_population
            if simulation.rich_zone_drain_events_last_tick > 0
            else 0.0
        ),
        "environmental_tolerance_rich_usage_bias_total": (
            environmental_tolerance_rich_users_avg_total - avg_environmental_tolerance_population
            if simulation.total_rich_zone_drain_events > 0
            else 0.0
        ),
        "reproduction_timing_reproduction_users_avg_last_tick": (
            reproduction_timing_reproduction_users_avg_last_tick
        ),
        "reproduction_timing_reproduction_users_avg_total": (
            reproduction_timing_reproduction_users_avg_total
        ),
        "reproduction_timing_reproduction_usage_bias_last_tick": (
            reproduction_timing_reproduction_users_avg_last_tick - avg_reproduction_timing_population
            if simulation.reproduction_cost_events_last_tick > 0
            else 0.0
        ),
        "reproduction_timing_reproduction_usage_bias_total": (
            reproduction_timing_reproduction_users_avg_total - avg_reproduction_timing_population
            if simulation.total_reproduction_cost_events > 0
            else 0.0
        ),
        "reproduction_timing_threshold_multiplier_avg_last_tick": (
            reproduction_timing_threshold_multiplier_avg_last_tick
        ),
        "reproduction_timing_threshold_multiplier_avg_total": (
            reproduction_timing_threshold_multiplier_avg_total
        ),
        "hunger_search_actions_last_tick": simulation.hunger_search_actions_last_tick,
        "total_hunger_search_actions": simulation.total_hunger_search_actions,
        "avg_hunger_sensitivity_population": avg_hunger_sensitivity_population,
        "hunger_sensitivity_search_users_avg_last_tick": (
            hunger_sensitivity_search_users_avg_last_tick
        ),
        "hunger_sensitivity_search_users_avg_total": (
            hunger_sensitivity_search_users_avg_total
        ),
        "hunger_sensitivity_search_usage_bias_last_tick": (
            hunger_sensitivity_search_users_avg_last_tick - avg_hunger_sensitivity_population
            if simulation.hunger_search_actions_last_tick > 0
            else 0.0
        ),
        "hunger_sensitivity_search_usage_bias_total": (
            hunger_sensitivity_search_users_avg_total - avg_hunger_sensitivity_population
            if simulation.total_hunger_search_actions > 0
            else 0.0
        ),
        "movement_actions_last_tick": simulation.movement_actions_last_tick,
        "total_movement_actions": simulation.total_movement_actions,
        "movement_multiplier_avg_last_tick": simulation.avg_movement_multiplier_last_tick,
        "movement_multiplier_avg_total": movement_multiplier_avg_total,
        "movement_distance_avg_last_tick": simulation.avg_movement_distance_last_tick,
        "movement_distance_avg_total": movement_distance_avg_total,
        "avg_stress_tolerance_population": avg_stress_tolerance_population,
        "stress_pressure_events_last_tick": simulation.stress_pressure_events_last_tick,
        "stress_pressure_flee_events_last_tick": simulation.stress_pressure_flee_events_last_tick,
        "stress_pressure_flee_rate_last_tick": (
            simulation.stress_pressure_flee_events_last_tick / simulation.stress_pressure_events_last_tick
            if simulation.stress_pressure_events_last_tick > 0
            else 0.0
        ),
        "stress_tolerance_pressure_users_avg_last_tick": stress_tolerance_pressure_users_avg_last_tick,
        "stress_tolerance_pressure_flee_users_avg_last_tick": (
            stress_tolerance_pressure_flee_users_avg_last_tick
        ),
        "stress_tolerance_pressure_flee_usage_bias_last_tick": (
            stress_tolerance_pressure_flee_users_avg_last_tick
            - stress_tolerance_pressure_users_avg_last_tick
            if simulation.stress_pressure_flee_events_last_tick > 0
            else 0.0
        ),
        "mobility_efficiency_movement_users_avg_last_tick": (
            mobility_efficiency_movement_users_avg_last_tick
        ),
        "mobility_efficiency_movement_users_avg_total": (
            mobility_efficiency_movement_users_avg_total
        ),
        "mobility_efficiency_movement_usage_bias_last_tick": (
            mobility_efficiency_movement_users_avg_last_tick - avg_mobility_efficiency_population
            if simulation.movement_actions_last_tick > 0
            else 0.0
        ),
        "mobility_efficiency_movement_usage_bias_total": (
            mobility_efficiency_movement_users_avg_total - avg_mobility_efficiency_population
            if simulation.total_movement_actions > 0
            else 0.0
        ),
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
    if intent.persisted_from_previous:
        return "intent_inertia"
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
