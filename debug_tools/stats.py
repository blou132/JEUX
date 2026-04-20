from __future__ import annotations

from math import sqrt
from typing import Dict, Iterable

from creatures import Creature
from simulation import HungerSimulation

_PROTO_GROUP_WIDTH_SPEED = 0.2
_PROTO_GROUP_WIDTH_METABOLISM = 0.15
_PROTO_GROUP_WIDTH_BEHAVIOR = 0.25
_PROTO_TREND_STABLE_DELTA = 0.02

_PROTO_TEMPORAL_STATUSES = ("stable", "en_hausse", "en_baisse", "nouveau")
_ZONE_NAMES = ("rich", "neutral", "poor")


def build_population_stats(
    simulation: HungerSimulation,
    world: object | None = None,
    previous_stats: Dict[str, object] | None = None,
) -> Dict[str, object]:
    total = simulation.get_total_count()
    alive = simulation.get_alive_count()
    dead = simulation.get_dead_count()

    alive_creatures = [creature for creature in simulation.creatures if creature.alive]
    food_memory_active_count = sum(1 for creature in alive_creatures if creature.has_food_memory)
    danger_memory_active_count = sum(1 for creature in alive_creatures if creature.has_danger_memory)
    (
        zone_distribution,
        dominant_proto_by_zone,
    ) = _build_proto_zone_observations(alive_creatures, world)

    food_memory_active_share = (food_memory_active_count / alive) if alive > 0 else 0.0
    danger_memory_active_share = (danger_memory_active_count / alive) if alive > 0 else 0.0

    avg_food_memory_distance_gain_total = (
        simulation.total_food_memory_distance_gain / simulation.total_food_memory_guided_moves
        if simulation.total_food_memory_guided_moves > 0
        else 0.0
    )
    avg_danger_memory_distance_gain_total = (
        simulation.total_danger_memory_distance_gain / simulation.total_danger_memory_avoid_moves
        if simulation.total_danger_memory_avoid_moves > 0
        else 0.0
    )
    avg_social_flee_multiplier_total = (
        simulation.total_social_flee_multiplier_sum / simulation.total_social_flee_boosted
        if simulation.total_social_flee_boosted > 0
        else 1.0
    )

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
            "avg_prudence": 0.0,
            "avg_dominance": 0.0,
            "avg_repro_drive": 0.0,
            "avg_memory_focus": 0.0,
            "avg_social_sensitivity": 0.0,
            "avg_food_perception": 0.0,
            "avg_threat_perception": 0.0,
            "avg_risk_taking": 0.0,
            "avg_behavior_persistence": 0.0,
            "avg_exploration_bias": 0.0,
            "avg_density_preference": 0.0,
            "avg_energy_efficiency": 0.0,
            "avg_exhaustion_resistance": 0.0,
            "std_memory_focus": 0.0,
            "std_social_sensitivity": 0.0,
            "std_food_perception": 0.0,
            "std_threat_perception": 0.0,
            "std_risk_taking": 0.0,
            "std_behavior_persistence": 0.0,
            "std_exploration_bias": 0.0,
            "std_density_preference": 0.0,
            "std_energy_efficiency": 0.0,
            "std_exhaustion_resistance": 0.0,
            "avg_effective_energy_drain_multiplier": 0.0,
            "avg_reproduction_cost_multiplier": 0.0,
            "energy_drain_events_last_tick": 0,
            "total_energy_drain_events": 0,
            "avg_energy_drain_amount_last_tick": 0.0,
            "avg_energy_drain_amount_total": 0.0,
            "avg_energy_drain_multiplier_observed_last_tick": 0.0,
            "avg_energy_drain_multiplier_observed_total": 0.0,
            "energy_efficiency_drain_users_avg_tick": 0.0,
            "energy_efficiency_drain_users_avg_total": 0.0,
            "energy_efficiency_drain_usage_bias_tick": 0.0,
            "energy_efficiency_drain_usage_bias_total": 0.0,
            "reproduction_cost_events_last_tick": 0,
            "total_reproduction_cost_events": 0,
            "avg_reproduction_cost_amount_last_tick": 0.0,
            "avg_reproduction_cost_amount_total": 0.0,
            "avg_reproduction_cost_multiplier_observed_last_tick": 0.0,
            "avg_reproduction_cost_multiplier_observed_total": 0.0,
            "exhaustion_resistance_reproduction_users_avg_tick": 0.0,
            "exhaustion_resistance_reproduction_users_avg_total": 0.0,
            "exhaustion_resistance_reproduction_usage_bias_tick": 0.0,
            "exhaustion_resistance_reproduction_usage_bias_total": 0.0,
            "proto_group_count": 0,
            "proto_groups_top": [],
            "dominant_proto_group_share": 0.0,
            "proto_group_temporal_trends": [],
            "proto_group_temporal_summary": _empty_proto_temporal_summary(),
            "creatures_by_fertility_zone": zone_distribution,
            "dominant_proto_group_by_fertility_zone": dominant_proto_by_zone,
            "births_last_tick": simulation.births_last_tick,
            "total_births": simulation.total_births,
            "deaths_last_tick": simulation.deaths_last_tick,
            "total_deaths": simulation.total_deaths,
            "flees_last_tick": simulation.flees_last_tick,
            "total_flees": simulation.total_flees,
            "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
            "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
            "creatures_with_food_memory": 0,
            "creatures_with_danger_memory": 0,
            "food_memory_active_share": 0.0,
            "danger_memory_active_share": 0.0,
            "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
            "total_food_memory_guided_moves": simulation.total_food_memory_guided_moves,
            "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
            "total_danger_memory_avoid_moves": simulation.total_danger_memory_avoid_moves,
            "food_memory_usage_per_alive_tick": 0.0,
            "danger_memory_usage_per_alive_tick": 0.0,
            "food_memory_usage_per_tick_total": 0.0,
            "danger_memory_usage_per_tick_total": 0.0,
            "food_memory_effect_avg_distance_tick": simulation.avg_food_memory_distance_gain_last_tick,
            "danger_memory_effect_avg_distance_tick": simulation.avg_danger_memory_distance_gain_last_tick,
            "food_memory_effect_avg_distance_total": avg_food_memory_distance_gain_total,
            "danger_memory_effect_avg_distance_total": avg_danger_memory_distance_gain_total,
            "social_follow_moves_last_tick": simulation.social_follow_moves_last_tick,
            "total_social_follow_moves": simulation.total_social_follow_moves,
            "social_flee_boosted_last_tick": simulation.social_flee_boosted_last_tick,
            "total_social_flee_boosted": simulation.total_social_flee_boosted,
            "avg_social_flee_multiplier_last_tick": simulation.avg_social_flee_multiplier_last_tick,
            "social_follow_usage_per_alive_tick": 0.0,
            "social_flee_boost_usage_per_alive_tick": 0.0,
            "social_follow_usage_per_tick_total": 0.0,
            "social_flee_boost_usage_per_tick_total": 0.0,
            "social_influenced_creatures_last_tick": 0,
            "total_social_influenced_creatures": 0,
            "social_influenced_share_last_tick": 0.0,
            "social_influenced_per_tick_total": 0.0,
            "social_flee_multiplier_avg_total": avg_social_flee_multiplier_total,
            "memory_focus_food_users_avg_tick": 0.0,
            "memory_focus_food_users_avg_total": 0.0,
            "memory_focus_food_usage_bias_tick": 0.0,
            "memory_focus_food_usage_bias_total": 0.0,
            "memory_focus_danger_users_avg_tick": 0.0,
            "memory_focus_danger_users_avg_total": 0.0,
            "memory_focus_danger_usage_bias_tick": 0.0,
            "memory_focus_danger_usage_bias_total": 0.0,
            "social_sensitivity_follow_users_avg_tick": 0.0,
            "social_sensitivity_follow_users_avg_total": 0.0,
            "social_sensitivity_follow_usage_bias_tick": 0.0,
            "social_sensitivity_follow_usage_bias_total": 0.0,
            "social_sensitivity_flee_boost_users_avg_tick": 0.0,
            "social_sensitivity_flee_boost_users_avg_total": 0.0,
            "social_sensitivity_flee_boost_usage_bias_tick": 0.0,
            "social_sensitivity_flee_boost_usage_bias_total": 0.0,
            "food_detection_moves_last_tick": simulation.food_detection_moves_last_tick,
            "total_food_detection_moves": simulation.total_food_detection_moves,
            "food_consumptions_last_tick": simulation.food_consumptions_last_tick,
            "total_food_consumptions": simulation.total_food_consumptions,
            "threat_detection_flee_last_tick": simulation.threat_detection_flee_last_tick,
            "total_threat_detection_flee": simulation.total_threat_detection_flee,
            "food_detection_usage_per_alive_tick": 0.0,
            "food_detection_usage_per_tick_total": 0.0,
            "food_consumption_usage_per_alive_tick": 0.0,
            "food_consumption_usage_per_tick_total": 0.0,
            "threat_detection_usage_per_alive_tick": 0.0,
            "threat_detection_usage_per_tick_total": 0.0,
            "food_perception_detection_users_avg_tick": 0.0,
            "food_perception_detection_users_avg_total": 0.0,
            "food_perception_detection_usage_bias_tick": 0.0,
            "food_perception_detection_usage_bias_total": 0.0,
            "food_perception_consumption_users_avg_tick": 0.0,
            "food_perception_consumption_users_avg_total": 0.0,
            "food_perception_consumption_usage_bias_tick": 0.0,
            "food_perception_consumption_usage_bias_total": 0.0,
            "threat_perception_flee_users_avg_tick": 0.0,
            "threat_perception_flee_users_avg_total": 0.0,
            "threat_perception_flee_usage_bias_tick": 0.0,
            "threat_perception_flee_usage_bias_total": 0.0,
            "risk_taking_flee_users_avg_tick": 0.0,
            "risk_taking_flee_users_avg_total": 0.0,
            "risk_taking_flee_usage_bias_tick": 0.0,
            "risk_taking_flee_usage_bias_total": 0.0,
            "persistence_holds_last_tick": 0,
            "total_persistence_holds": 0,
            "persistence_hold_usage_per_alive_tick": 0.0,
            "persistence_hold_usage_per_tick_total": 0.0,
            "behavior_persistence_hold_users_avg_tick": 0.0,
            "behavior_persistence_hold_users_avg_total": 0.0,
            "behavior_persistence_hold_usage_bias_tick": 0.0,
            "behavior_persistence_hold_usage_bias_total": 0.0,
            "exploration_bias_guided_moves_last_tick": 0,
            "total_exploration_bias_guided_moves": 0,
            "exploration_bias_usage_per_alive_tick": 0.0,
            "exploration_bias_usage_per_tick_total": 0.0,
            "exploration_bias_guided_users_avg_tick": 0.0,
            "exploration_bias_guided_users_avg_total": 0.0,
            "exploration_bias_guided_usage_bias_tick": 0.0,
            "exploration_bias_guided_usage_bias_total": 0.0,
            "exploration_bias_explore_moves_last_tick": 0,
            "total_exploration_bias_explore_moves": 0,
            "exploration_bias_explore_users_avg_tick": 0.0,
            "exploration_bias_explore_users_avg_total": 0.0,
            "exploration_bias_explore_usage_bias_tick": 0.0,
            "exploration_bias_explore_usage_bias_total": 0.0,
            "exploration_bias_settle_moves_last_tick": 0,
            "total_exploration_bias_settle_moves": 0,
            "exploration_bias_settle_users_avg_tick": 0.0,
            "exploration_bias_settle_users_avg_total": 0.0,
            "exploration_bias_settle_usage_bias_tick": 0.0,
            "exploration_bias_settle_usage_bias_total": 0.0,
            "exploration_bias_explore_share_last_tick": 0.0,
            "exploration_bias_explore_share_total": 0.0,
            "avg_exploration_bias_anchor_distance_delta_last_tick": (
                simulation.avg_exploration_bias_anchor_distance_delta_last_tick
            ),
            "avg_exploration_bias_anchor_distance_delta_total": 0.0,
            "density_preference_guided_moves_last_tick": 0,
            "total_density_preference_guided_moves": 0,
            "density_preference_usage_per_alive_tick": 0.0,
            "density_preference_usage_per_tick_total": 0.0,
            "density_preference_seek_moves_last_tick": 0,
            "total_density_preference_seek_moves": 0,
            "density_preference_seek_usage_per_alive_tick": 0.0,
            "density_preference_seek_usage_per_tick_total": 0.0,
            "density_preference_seek_users_avg_tick": 0.0,
            "density_preference_seek_users_avg_total": 0.0,
            "density_preference_seek_usage_bias_tick": 0.0,
            "density_preference_seek_usage_bias_total": 0.0,
            "density_preference_avoid_moves_last_tick": 0,
            "total_density_preference_avoid_moves": 0,
            "density_preference_avoid_usage_per_alive_tick": 0.0,
            "density_preference_avoid_usage_per_tick_total": 0.0,
            "density_preference_avoid_users_avg_tick": 0.0,
            "density_preference_avoid_users_avg_total": 0.0,
            "density_preference_avoid_usage_bias_tick": 0.0,
            "density_preference_avoid_usage_bias_total": 0.0,
            "density_preference_seek_share_last_tick": 0.0,
            "density_preference_seek_share_total": 0.0,
            "density_preference_avoid_share_last_tick": 0.0,
            "density_preference_avoid_share_total": 0.0,
            "density_preference_guided_users_avg_tick": 0.0,
            "density_preference_guided_users_avg_total": 0.0,
            "density_preference_guided_usage_bias_tick": 0.0,
            "density_preference_guided_usage_bias_total": 0.0,
            "avg_density_preference_neighbor_count_last_tick": 0.0,
            "avg_density_preference_neighbor_count_total": 0.0,
            "avg_density_preference_center_distance_delta_last_tick": 0.0,
            "avg_density_preference_center_distance_delta_total": 0.0,
            "search_wander_switches_last_tick": 0,
            "total_search_wander_switches": 0,
            "search_wander_switches_prevented_last_tick": 0,
            "total_search_wander_switches_prevented": 0,
            "search_wander_oscillation_events_last_tick": 0,
            "total_search_wander_oscillation_events": 0,
            "search_wander_switch_rate_last_tick": 0.0,
            "search_wander_switch_rate_total": 0.0,
            "search_wander_prevented_rate_last_tick": 0.0,
            "search_wander_prevented_rate_total": 0.0,
            "borderline_threat_encounters_last_tick": 0,
            "total_borderline_threat_encounters": 0,
            "borderline_threat_flees_last_tick": 0,
            "total_borderline_threat_flees": 0,
            "borderline_threat_flee_rate_last_tick": 0.0,
            "borderline_threat_flee_rate_total": 0.0,
            "risk_taking_borderline_encounter_users_avg_tick": 0.0,
            "risk_taking_borderline_encounter_users_avg_total": 0.0,
            "risk_taking_borderline_flee_users_avg_tick": 0.0,
            "risk_taking_borderline_flee_users_avg_total": 0.0,
            "risk_taking_borderline_flee_usage_bias_tick": 0.0,
            "risk_taking_borderline_flee_usage_bias_total": 0.0,
            "death_causes_last_tick": dict(simulation.death_causes_last_tick),
            "death_causes_total": dict(simulation.total_death_causes),
        }

    avg_energy = sum(c.energy for c in simulation.creatures) / total
    avg_age = sum(c.age for c in simulation.creatures) / total
    avg_generation = sum(c.generation for c in simulation.creatures) / total
    avg_speed = sum(c.traits.speed for c in simulation.creatures) / total
    avg_metabolism = sum(c.traits.metabolism for c in simulation.creatures) / total
    avg_prudence = sum(c.traits.prudence for c in simulation.creatures) / total
    avg_dominance = sum(c.traits.dominance for c in simulation.creatures) / total
    avg_repro_drive = sum(c.traits.repro_drive for c in simulation.creatures) / total
    avg_memory_focus = sum(c.traits.memory_focus for c in simulation.creatures) / total
    avg_social_sensitivity = sum(c.traits.social_sensitivity for c in simulation.creatures) / total
    avg_food_perception = sum(c.traits.food_perception for c in simulation.creatures) / total
    avg_threat_perception = sum(c.traits.threat_perception for c in simulation.creatures) / total
    avg_risk_taking = sum(c.traits.risk_taking for c in simulation.creatures) / total
    avg_behavior_persistence = sum(c.traits.behavior_persistence for c in simulation.creatures) / total
    avg_exploration_bias = sum(c.traits.exploration_bias for c in simulation.creatures) / total
    avg_density_preference = sum(c.traits.density_preference for c in simulation.creatures) / total
    avg_energy_efficiency = sum(c.traits.energy_efficiency for c in simulation.creatures) / total
    avg_exhaustion_resistance = sum(c.traits.exhaustion_resistance for c in simulation.creatures) / total
    avg_effective_energy_drain_multiplier = avg_metabolism * max(0.1, 1.0 - (0.25 * (avg_energy_efficiency - 1.0)))
    avg_reproduction_cost_multiplier = max(0.1, 1.0 - (0.3 * (avg_exhaustion_resistance - 1.0)))
    avg_energy_drain_amount_last_tick = (
        simulation.energy_drain_amount_last_tick / simulation.energy_drain_events_last_tick
        if simulation.energy_drain_events_last_tick > 0
        else 0.0
    )
    avg_energy_drain_amount_total = (
        simulation.total_energy_drain_amount / simulation.total_energy_drain_events
        if simulation.total_energy_drain_events > 0
        else 0.0
    )
    avg_energy_drain_multiplier_observed_last_tick = (
        simulation.energy_drain_multiplier_sum_last_tick / simulation.energy_drain_events_last_tick
        if simulation.energy_drain_events_last_tick > 0
        else 0.0
    )
    avg_energy_drain_multiplier_observed_total = (
        simulation.total_energy_drain_multiplier_sum / simulation.total_energy_drain_events
        if simulation.total_energy_drain_events > 0
        else 0.0
    )
    avg_energy_efficiency_drain_users_tick = (
        simulation.energy_efficiency_sum_drain_last_tick / simulation.energy_drain_events_last_tick
        if simulation.energy_drain_events_last_tick > 0
        else 0.0
    )
    avg_energy_efficiency_drain_users_total = (
        simulation.total_energy_efficiency_sum_drain / simulation.total_energy_drain_events
        if simulation.total_energy_drain_events > 0
        else 0.0
    )
    energy_efficiency_drain_usage_bias_tick = (
        avg_energy_efficiency_drain_users_tick - avg_energy_efficiency
        if simulation.energy_drain_events_last_tick > 0
        else 0.0
    )
    energy_efficiency_drain_usage_bias_total = (
        avg_energy_efficiency_drain_users_total - avg_energy_efficiency
        if simulation.total_energy_drain_events > 0
        else 0.0
    )
    avg_reproduction_cost_amount_last_tick = (
        simulation.reproduction_cost_amount_last_tick / simulation.reproduction_cost_events_last_tick
        if simulation.reproduction_cost_events_last_tick > 0
        else 0.0
    )
    avg_reproduction_cost_amount_total = (
        simulation.total_reproduction_cost_amount / simulation.total_reproduction_cost_events
        if simulation.total_reproduction_cost_events > 0
        else 0.0
    )
    avg_reproduction_cost_multiplier_observed_last_tick = (
        simulation.reproduction_cost_multiplier_sum_last_tick / simulation.reproduction_cost_events_last_tick
        if simulation.reproduction_cost_events_last_tick > 0
        else 0.0
    )
    avg_reproduction_cost_multiplier_observed_total = (
        simulation.total_reproduction_cost_multiplier_sum / simulation.total_reproduction_cost_events
        if simulation.total_reproduction_cost_events > 0
        else 0.0
    )
    avg_exhaustion_resistance_reproduction_users_tick = (
        simulation.exhaustion_resistance_sum_reproduction_last_tick / simulation.reproduction_cost_events_last_tick
        if simulation.reproduction_cost_events_last_tick > 0
        else 0.0
    )
    avg_exhaustion_resistance_reproduction_users_total = (
        simulation.total_exhaustion_resistance_sum_reproduction / simulation.total_reproduction_cost_events
        if simulation.total_reproduction_cost_events > 0
        else 0.0
    )
    exhaustion_resistance_reproduction_usage_bias_tick = (
        avg_exhaustion_resistance_reproduction_users_tick - avg_exhaustion_resistance
        if simulation.reproduction_cost_events_last_tick > 0
        else 0.0
    )
    exhaustion_resistance_reproduction_usage_bias_total = (
        avg_exhaustion_resistance_reproduction_users_total - avg_exhaustion_resistance
        if simulation.total_reproduction_cost_events > 0
        else 0.0
    )

    memory_focus_values = [c.traits.memory_focus for c in simulation.creatures]
    social_sensitivity_values = [c.traits.social_sensitivity for c in simulation.creatures]
    food_perception_values = [c.traits.food_perception for c in simulation.creatures]
    threat_perception_values = [c.traits.threat_perception for c in simulation.creatures]
    risk_taking_values = [c.traits.risk_taking for c in simulation.creatures]
    behavior_persistence_values = [c.traits.behavior_persistence for c in simulation.creatures]
    exploration_bias_values = [c.traits.exploration_bias for c in simulation.creatures]
    density_preference_values = [c.traits.density_preference for c in simulation.creatures]
    energy_efficiency_values = [c.traits.energy_efficiency for c in simulation.creatures]
    exhaustion_resistance_values = [c.traits.exhaustion_resistance for c in simulation.creatures]

    std_memory_focus = _stddev_from_mean(memory_focus_values, avg_memory_focus)
    std_social_sensitivity = _stddev_from_mean(social_sensitivity_values, avg_social_sensitivity)
    std_food_perception = _stddev_from_mean(food_perception_values, avg_food_perception)
    std_threat_perception = _stddev_from_mean(threat_perception_values, avg_threat_perception)
    std_risk_taking = _stddev_from_mean(risk_taking_values, avg_risk_taking)
    std_behavior_persistence = _stddev_from_mean(behavior_persistence_values, avg_behavior_persistence)
    std_exploration_bias = _stddev_from_mean(exploration_bias_values, avg_exploration_bias)
    std_density_preference = _stddev_from_mean(density_preference_values, avg_density_preference)
    std_energy_efficiency = _stddev_from_mean(energy_efficiency_values, avg_energy_efficiency)
    std_exhaustion_resistance = _stddev_from_mean(exhaustion_resistance_values, avg_exhaustion_resistance)

    avg_memory_focus_food_users_tick = (
        simulation.memory_focus_sum_food_memory_last_tick / simulation.food_memory_guided_moves_last_tick
        if simulation.food_memory_guided_moves_last_tick > 0
        else 0.0
    )
    avg_memory_focus_food_users_total = (
        simulation.total_memory_focus_sum_food_memory / simulation.total_food_memory_guided_moves
        if simulation.total_food_memory_guided_moves > 0
        else 0.0
    )
    avg_memory_focus_danger_users_tick = (
        simulation.memory_focus_sum_danger_memory_last_tick / simulation.danger_memory_avoid_moves_last_tick
        if simulation.danger_memory_avoid_moves_last_tick > 0
        else 0.0
    )
    avg_memory_focus_danger_users_total = (
        simulation.total_memory_focus_sum_danger_memory / simulation.total_danger_memory_avoid_moves
        if simulation.total_danger_memory_avoid_moves > 0
        else 0.0
    )

    memory_focus_food_usage_bias_tick = (
        avg_memory_focus_food_users_tick - avg_memory_focus
        if simulation.food_memory_guided_moves_last_tick > 0
        else 0.0
    )
    memory_focus_food_usage_bias_total = (
        avg_memory_focus_food_users_total - avg_memory_focus
        if simulation.total_food_memory_guided_moves > 0
        else 0.0
    )
    memory_focus_danger_usage_bias_tick = (
        avg_memory_focus_danger_users_tick - avg_memory_focus
        if simulation.danger_memory_avoid_moves_last_tick > 0
        else 0.0
    )
    memory_focus_danger_usage_bias_total = (
        avg_memory_focus_danger_users_total - avg_memory_focus
        if simulation.total_danger_memory_avoid_moves > 0
        else 0.0
    )

    avg_social_sensitivity_follow_users_tick = (
        simulation.social_sensitivity_sum_follow_last_tick / simulation.social_follow_moves_last_tick
        if simulation.social_follow_moves_last_tick > 0
        else 0.0
    )
    avg_social_sensitivity_follow_users_total = (
        simulation.total_social_sensitivity_sum_follow / simulation.total_social_follow_moves
        if simulation.total_social_follow_moves > 0
        else 0.0
    )
    avg_social_sensitivity_flee_boost_users_tick = (
        simulation.social_sensitivity_sum_flee_boost_last_tick / simulation.social_flee_boosted_last_tick
        if simulation.social_flee_boosted_last_tick > 0
        else 0.0
    )
    avg_social_sensitivity_flee_boost_users_total = (
        simulation.total_social_sensitivity_sum_flee_boost / simulation.total_social_flee_boosted
        if simulation.total_social_flee_boosted > 0
        else 0.0
    )

    social_sensitivity_follow_usage_bias_tick = (
        avg_social_sensitivity_follow_users_tick - avg_social_sensitivity
        if simulation.social_follow_moves_last_tick > 0
        else 0.0
    )
    social_sensitivity_follow_usage_bias_total = (
        avg_social_sensitivity_follow_users_total - avg_social_sensitivity
        if simulation.total_social_follow_moves > 0
        else 0.0
    )
    social_sensitivity_flee_boost_usage_bias_tick = (
        avg_social_sensitivity_flee_boost_users_tick - avg_social_sensitivity
        if simulation.social_flee_boosted_last_tick > 0
        else 0.0
    )
    social_sensitivity_flee_boost_usage_bias_total = (
        avg_social_sensitivity_flee_boost_users_total - avg_social_sensitivity
        if simulation.total_social_flee_boosted > 0
        else 0.0
    )

    avg_food_perception_detection_users_tick = (
        simulation.food_perception_sum_detection_last_tick / simulation.food_detection_moves_last_tick
        if simulation.food_detection_moves_last_tick > 0
        else 0.0
    )
    avg_food_perception_detection_users_total = (
        simulation.total_food_perception_sum_detection / simulation.total_food_detection_moves
        if simulation.total_food_detection_moves > 0
        else 0.0
    )
    avg_food_perception_consumption_users_tick = (
        simulation.food_perception_sum_consumption_last_tick / simulation.food_consumptions_last_tick
        if simulation.food_consumptions_last_tick > 0
        else 0.0
    )
    avg_food_perception_consumption_users_total = (
        simulation.total_food_perception_sum_consumption / simulation.total_food_consumptions
        if simulation.total_food_consumptions > 0
        else 0.0
    )
    avg_threat_perception_flee_users_tick = (
        simulation.threat_perception_sum_flee_last_tick / simulation.threat_detection_flee_last_tick
        if simulation.threat_detection_flee_last_tick > 0
        else 0.0
    )
    avg_threat_perception_flee_users_total = (
        simulation.total_threat_perception_sum_flee / simulation.total_threat_detection_flee
        if simulation.total_threat_detection_flee > 0
        else 0.0
    )

    food_perception_detection_usage_bias_tick = (
        avg_food_perception_detection_users_tick - avg_food_perception
        if simulation.food_detection_moves_last_tick > 0
        else 0.0
    )
    food_perception_detection_usage_bias_total = (
        avg_food_perception_detection_users_total - avg_food_perception
        if simulation.total_food_detection_moves > 0
        else 0.0
    )
    food_perception_consumption_usage_bias_tick = (
        avg_food_perception_consumption_users_tick - avg_food_perception
        if simulation.food_consumptions_last_tick > 0
        else 0.0
    )
    food_perception_consumption_usage_bias_total = (
        avg_food_perception_consumption_users_total - avg_food_perception
        if simulation.total_food_consumptions > 0
        else 0.0
    )
    threat_perception_flee_usage_bias_tick = (
        avg_threat_perception_flee_users_tick - avg_threat_perception
        if simulation.threat_detection_flee_last_tick > 0
        else 0.0
    )
    threat_perception_flee_usage_bias_total = (
        avg_threat_perception_flee_users_total - avg_threat_perception
        if simulation.total_threat_detection_flee > 0
        else 0.0
    )
    avg_risk_taking_flee_users_tick = (
        simulation.risk_taking_sum_flee_last_tick / simulation.threat_detection_flee_last_tick
        if simulation.threat_detection_flee_last_tick > 0
        else 0.0
    )
    avg_risk_taking_flee_users_total = (
        simulation.total_risk_taking_sum_flee / simulation.total_threat_detection_flee
        if simulation.total_threat_detection_flee > 0
        else 0.0
    )
    risk_taking_flee_usage_bias_tick = (
        avg_risk_taking_flee_users_tick - avg_risk_taking
        if simulation.threat_detection_flee_last_tick > 0
        else 0.0
    )
    risk_taking_flee_usage_bias_total = (
        avg_risk_taking_flee_users_total - avg_risk_taking
        if simulation.total_threat_detection_flee > 0
        else 0.0
    )
    avg_behavior_persistence_hold_users_tick = (
        simulation.behavior_persistence_sum_holds_last_tick / simulation.persistence_holds_last_tick
        if simulation.persistence_holds_last_tick > 0
        else 0.0
    )
    avg_behavior_persistence_hold_users_total = (
        simulation.total_behavior_persistence_sum_holds / simulation.total_persistence_holds
        if simulation.total_persistence_holds > 0
        else 0.0
    )
    behavior_persistence_hold_usage_bias_tick = (
        avg_behavior_persistence_hold_users_tick - avg_behavior_persistence
        if simulation.persistence_holds_last_tick > 0
        else 0.0
    )
    behavior_persistence_hold_usage_bias_total = (
        avg_behavior_persistence_hold_users_total - avg_behavior_persistence
        if simulation.total_persistence_holds > 0
        else 0.0
    )
    avg_exploration_bias_guided_users_tick = (
        simulation.exploration_bias_sum_guided_last_tick / simulation.exploration_bias_guided_moves_last_tick
        if simulation.exploration_bias_guided_moves_last_tick > 0
        else 0.0
    )
    avg_exploration_bias_guided_users_total = (
        simulation.total_exploration_bias_sum_guided / simulation.total_exploration_bias_guided_moves
        if simulation.total_exploration_bias_guided_moves > 0
        else 0.0
    )
    exploration_bias_guided_usage_bias_tick = (
        avg_exploration_bias_guided_users_tick - avg_exploration_bias
        if simulation.exploration_bias_guided_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_guided_usage_bias_total = (
        avg_exploration_bias_guided_users_total - avg_exploration_bias
        if simulation.total_exploration_bias_guided_moves > 0
        else 0.0
    )
    exploration_bias_explore_share_last_tick = (
        simulation.exploration_bias_explore_moves_last_tick / simulation.exploration_bias_guided_moves_last_tick
        if simulation.exploration_bias_guided_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_explore_share_total = (
        simulation.total_exploration_bias_explore_moves / simulation.total_exploration_bias_guided_moves
        if simulation.total_exploration_bias_guided_moves > 0
        else 0.0
    )
    avg_exploration_bias_explore_users_tick = (
        simulation.exploration_bias_sum_explore_last_tick / simulation.exploration_bias_explore_moves_last_tick
        if simulation.exploration_bias_explore_moves_last_tick > 0
        else 0.0
    )
    avg_exploration_bias_explore_users_total = (
        simulation.total_exploration_bias_sum_explore / simulation.total_exploration_bias_explore_moves
        if simulation.total_exploration_bias_explore_moves > 0
        else 0.0
    )
    exploration_bias_explore_usage_bias_tick = (
        avg_exploration_bias_explore_users_tick - avg_exploration_bias
        if simulation.exploration_bias_explore_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_explore_usage_bias_total = (
        avg_exploration_bias_explore_users_total - avg_exploration_bias
        if simulation.total_exploration_bias_explore_moves > 0
        else 0.0
    )
    avg_exploration_bias_settle_users_tick = (
        simulation.exploration_bias_sum_settle_last_tick / simulation.exploration_bias_settle_moves_last_tick
        if simulation.exploration_bias_settle_moves_last_tick > 0
        else 0.0
    )
    avg_exploration_bias_settle_users_total = (
        simulation.total_exploration_bias_sum_settle / simulation.total_exploration_bias_settle_moves
        if simulation.total_exploration_bias_settle_moves > 0
        else 0.0
    )
    exploration_bias_settle_usage_bias_tick = (
        avg_exploration_bias_settle_users_tick - avg_exploration_bias
        if simulation.exploration_bias_settle_moves_last_tick > 0
        else 0.0
    )
    exploration_bias_settle_usage_bias_total = (
        avg_exploration_bias_settle_users_total - avg_exploration_bias
        if simulation.total_exploration_bias_settle_moves > 0
        else 0.0
    )
    avg_exploration_bias_anchor_distance_delta_total = (
        simulation.total_exploration_bias_anchor_distance_delta / simulation.total_exploration_bias_guided_moves
        if simulation.total_exploration_bias_guided_moves > 0
        else 0.0
    )
    avg_density_preference_guided_users_tick = (
        simulation.density_preference_sum_guided_last_tick / simulation.density_preference_guided_moves_last_tick
        if simulation.density_preference_guided_moves_last_tick > 0
        else 0.0
    )
    avg_density_preference_guided_users_total = (
        simulation.total_density_preference_sum_guided / simulation.total_density_preference_guided_moves
        if simulation.total_density_preference_guided_moves > 0
        else 0.0
    )
    density_preference_guided_usage_bias_tick = (
        avg_density_preference_guided_users_tick - avg_density_preference
        if simulation.density_preference_guided_moves_last_tick > 0
        else 0.0
    )
    density_preference_guided_usage_bias_total = (
        avg_density_preference_guided_users_total - avg_density_preference
        if simulation.total_density_preference_guided_moves > 0
        else 0.0
    )
    density_preference_seek_share_last_tick = (
        simulation.density_preference_seek_moves_last_tick / simulation.density_preference_guided_moves_last_tick
        if simulation.density_preference_guided_moves_last_tick > 0
        else 0.0
    )
    density_preference_seek_share_total = (
        simulation.total_density_preference_seek_moves / simulation.total_density_preference_guided_moves
        if simulation.total_density_preference_guided_moves > 0
        else 0.0
    )
    avg_density_preference_seek_users_tick = (
        simulation.density_preference_sum_seek_last_tick / simulation.density_preference_seek_moves_last_tick
        if simulation.density_preference_seek_moves_last_tick > 0
        else 0.0
    )
    avg_density_preference_seek_users_total = (
        simulation.total_density_preference_sum_seek / simulation.total_density_preference_seek_moves
        if simulation.total_density_preference_seek_moves > 0
        else 0.0
    )
    density_preference_seek_usage_bias_tick = (
        avg_density_preference_seek_users_tick - avg_density_preference
        if simulation.density_preference_seek_moves_last_tick > 0
        else 0.0
    )
    density_preference_seek_usage_bias_total = (
        avg_density_preference_seek_users_total - avg_density_preference
        if simulation.total_density_preference_seek_moves > 0
        else 0.0
    )
    avg_density_preference_avoid_users_tick = (
        simulation.density_preference_sum_avoid_last_tick / simulation.density_preference_avoid_moves_last_tick
        if simulation.density_preference_avoid_moves_last_tick > 0
        else 0.0
    )
    avg_density_preference_avoid_users_total = (
        simulation.total_density_preference_sum_avoid / simulation.total_density_preference_avoid_moves
        if simulation.total_density_preference_avoid_moves > 0
        else 0.0
    )
    density_preference_avoid_usage_bias_tick = (
        avg_density_preference_avoid_users_tick - avg_density_preference
        if simulation.density_preference_avoid_moves_last_tick > 0
        else 0.0
    )
    density_preference_avoid_usage_bias_total = (
        avg_density_preference_avoid_users_total - avg_density_preference
        if simulation.total_density_preference_avoid_moves > 0
        else 0.0
    )
    avg_density_preference_neighbor_count_last_tick = (
        simulation.density_preference_neighbor_count_sum_last_tick / simulation.density_preference_guided_moves_last_tick
        if simulation.density_preference_guided_moves_last_tick > 0
        else 0.0
    )
    avg_density_preference_neighbor_count_total = (
        simulation.total_density_preference_neighbor_count_sum / simulation.total_density_preference_guided_moves
        if simulation.total_density_preference_guided_moves > 0
        else 0.0
    )
    avg_density_preference_center_distance_delta_total = (
        simulation.total_density_preference_center_distance_delta / simulation.total_density_preference_guided_moves
        if simulation.total_density_preference_guided_moves > 0
        else 0.0
    )
    search_wander_switch_rate_last_tick = (
        simulation.search_wander_switches_last_tick / simulation.search_wander_oscillation_events_last_tick
        if simulation.search_wander_oscillation_events_last_tick > 0
        else 0.0
    )
    search_wander_switch_rate_total = (
        simulation.total_search_wander_switches / simulation.total_search_wander_oscillation_events
        if simulation.total_search_wander_oscillation_events > 0
        else 0.0
    )
    search_wander_prevented_rate_last_tick = (
        simulation.search_wander_switches_prevented_last_tick
        / simulation.search_wander_oscillation_events_last_tick
        if simulation.search_wander_oscillation_events_last_tick > 0
        else 0.0
    )
    search_wander_prevented_rate_total = (
        simulation.total_search_wander_switches_prevented / simulation.total_search_wander_oscillation_events
        if simulation.total_search_wander_oscillation_events > 0
        else 0.0
    )
    borderline_threat_flee_rate_tick = (
        simulation.borderline_threat_flees_last_tick / simulation.borderline_threat_encounters_last_tick
        if simulation.borderline_threat_encounters_last_tick > 0
        else 0.0
    )
    borderline_threat_flee_rate_total = (
        simulation.total_borderline_threat_flees / simulation.total_borderline_threat_encounters
        if simulation.total_borderline_threat_encounters > 0
        else 0.0
    )
    avg_risk_taking_borderline_encounter_users_tick = (
        simulation.risk_taking_sum_borderline_encounters_last_tick
        / simulation.borderline_threat_encounters_last_tick
        if simulation.borderline_threat_encounters_last_tick > 0
        else 0.0
    )
    avg_risk_taking_borderline_encounter_users_total = (
        simulation.total_risk_taking_sum_borderline_encounters
        / simulation.total_borderline_threat_encounters
        if simulation.total_borderline_threat_encounters > 0
        else 0.0
    )
    avg_risk_taking_borderline_flee_users_tick = (
        simulation.risk_taking_sum_borderline_flees_last_tick
        / simulation.borderline_threat_flees_last_tick
        if simulation.borderline_threat_flees_last_tick > 0
        else 0.0
    )
    avg_risk_taking_borderline_flee_users_total = (
        simulation.total_risk_taking_sum_borderline_flees
        / simulation.total_borderline_threat_flees
        if simulation.total_borderline_threat_flees > 0
        else 0.0
    )
    risk_taking_borderline_flee_usage_bias_tick = (
        avg_risk_taking_borderline_flee_users_tick - avg_risk_taking_borderline_encounter_users_tick
        if simulation.borderline_threat_flees_last_tick > 0
        else 0.0
    )
    risk_taking_borderline_flee_usage_bias_total = (
        avg_risk_taking_borderline_flee_users_total - avg_risk_taking_borderline_encounter_users_total
        if simulation.total_borderline_threat_flees > 0
        else 0.0
    )

    proto_group_count, proto_groups_top, dominant_proto_group_share = _build_proto_groups(
        alive_creatures,
        max_groups=3,
    )
    (
        proto_group_temporal_trends,
        proto_group_temporal_summary,
    ) = _build_proto_group_temporal_observations(
        proto_groups_top,
        previous_stats=previous_stats,
        max_groups=3,
    )

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
        "avg_prudence": avg_prudence,
        "avg_dominance": avg_dominance,
        "avg_repro_drive": avg_repro_drive,
        "avg_memory_focus": avg_memory_focus,
        "avg_social_sensitivity": avg_social_sensitivity,
        "avg_food_perception": avg_food_perception,
        "avg_threat_perception": avg_threat_perception,
        "avg_risk_taking": avg_risk_taking,
        "avg_behavior_persistence": avg_behavior_persistence,
        "avg_exploration_bias": avg_exploration_bias,
        "avg_density_preference": avg_density_preference,
        "avg_energy_efficiency": avg_energy_efficiency,
        "avg_exhaustion_resistance": avg_exhaustion_resistance,
        "std_memory_focus": std_memory_focus,
        "std_social_sensitivity": std_social_sensitivity,
        "std_food_perception": std_food_perception,
        "std_threat_perception": std_threat_perception,
        "std_risk_taking": std_risk_taking,
        "std_behavior_persistence": std_behavior_persistence,
        "std_exploration_bias": std_exploration_bias,
        "std_density_preference": std_density_preference,
        "std_energy_efficiency": std_energy_efficiency,
        "std_exhaustion_resistance": std_exhaustion_resistance,
        "avg_effective_energy_drain_multiplier": avg_effective_energy_drain_multiplier,
        "avg_reproduction_cost_multiplier": avg_reproduction_cost_multiplier,
        "energy_drain_events_last_tick": simulation.energy_drain_events_last_tick,
        "total_energy_drain_events": simulation.total_energy_drain_events,
        "avg_energy_drain_amount_last_tick": avg_energy_drain_amount_last_tick,
        "avg_energy_drain_amount_total": avg_energy_drain_amount_total,
        "avg_energy_drain_multiplier_observed_last_tick": avg_energy_drain_multiplier_observed_last_tick,
        "avg_energy_drain_multiplier_observed_total": avg_energy_drain_multiplier_observed_total,
        "energy_efficiency_drain_users_avg_tick": avg_energy_efficiency_drain_users_tick,
        "energy_efficiency_drain_users_avg_total": avg_energy_efficiency_drain_users_total,
        "energy_efficiency_drain_usage_bias_tick": energy_efficiency_drain_usage_bias_tick,
        "energy_efficiency_drain_usage_bias_total": energy_efficiency_drain_usage_bias_total,
        "reproduction_cost_events_last_tick": simulation.reproduction_cost_events_last_tick,
        "total_reproduction_cost_events": simulation.total_reproduction_cost_events,
        "avg_reproduction_cost_amount_last_tick": avg_reproduction_cost_amount_last_tick,
        "avg_reproduction_cost_amount_total": avg_reproduction_cost_amount_total,
        "avg_reproduction_cost_multiplier_observed_last_tick": avg_reproduction_cost_multiplier_observed_last_tick,
        "avg_reproduction_cost_multiplier_observed_total": avg_reproduction_cost_multiplier_observed_total,
        "exhaustion_resistance_reproduction_users_avg_tick": avg_exhaustion_resistance_reproduction_users_tick,
        "exhaustion_resistance_reproduction_users_avg_total": avg_exhaustion_resistance_reproduction_users_total,
        "exhaustion_resistance_reproduction_usage_bias_tick": exhaustion_resistance_reproduction_usage_bias_tick,
        "exhaustion_resistance_reproduction_usage_bias_total": exhaustion_resistance_reproduction_usage_bias_total,
        "proto_group_count": proto_group_count,
        "proto_groups_top": proto_groups_top,
        "dominant_proto_group_share": dominant_proto_group_share,
        "proto_group_temporal_trends": proto_group_temporal_trends,
        "proto_group_temporal_summary": proto_group_temporal_summary,
        "creatures_by_fertility_zone": zone_distribution,
        "dominant_proto_group_by_fertility_zone": dominant_proto_by_zone,
        "births_last_tick": simulation.births_last_tick,
        "total_births": simulation.total_births,
        "deaths_last_tick": simulation.deaths_last_tick,
        "total_deaths": simulation.total_deaths,
        "flees_last_tick": simulation.flees_last_tick,
        "total_flees": simulation.total_flees,
        "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
        "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
        "creatures_with_food_memory": food_memory_active_count,
        "creatures_with_danger_memory": danger_memory_active_count,
        "food_memory_active_share": food_memory_active_share,
        "danger_memory_active_share": danger_memory_active_share,
        "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
        "total_food_memory_guided_moves": simulation.total_food_memory_guided_moves,
        "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
        "total_danger_memory_avoid_moves": simulation.total_danger_memory_avoid_moves,
        "food_memory_usage_per_alive_tick": simulation.food_memory_guided_moves_last_tick / alive,
        "danger_memory_usage_per_alive_tick": simulation.danger_memory_avoid_moves_last_tick / alive,
        "food_memory_usage_per_tick_total": simulation.total_food_memory_guided_moves / max(1, simulation.tick_count),
        "danger_memory_usage_per_tick_total": simulation.total_danger_memory_avoid_moves / max(1, simulation.tick_count),
        "food_memory_effect_avg_distance_tick": simulation.avg_food_memory_distance_gain_last_tick,
        "danger_memory_effect_avg_distance_tick": simulation.avg_danger_memory_distance_gain_last_tick,
        "food_memory_effect_avg_distance_total": avg_food_memory_distance_gain_total,
        "danger_memory_effect_avg_distance_total": avg_danger_memory_distance_gain_total,
        "social_follow_moves_last_tick": simulation.social_follow_moves_last_tick,
        "total_social_follow_moves": simulation.total_social_follow_moves,
        "social_flee_boosted_last_tick": simulation.social_flee_boosted_last_tick,
        "total_social_flee_boosted": simulation.total_social_flee_boosted,
        "avg_social_flee_multiplier_last_tick": simulation.avg_social_flee_multiplier_last_tick,
        "social_follow_usage_per_alive_tick": simulation.social_follow_moves_last_tick / alive,
        "social_flee_boost_usage_per_alive_tick": simulation.social_flee_boosted_last_tick / alive,
        "social_follow_usage_per_tick_total": simulation.total_social_follow_moves / max(1, simulation.tick_count),
        "social_flee_boost_usage_per_tick_total": simulation.total_social_flee_boosted / max(1, simulation.tick_count),
        "social_influenced_creatures_last_tick": simulation.social_influenced_creatures_last_tick,
        "total_social_influenced_creatures": simulation.total_social_influenced_creatures,
        "social_influenced_share_last_tick": simulation.social_influenced_creatures_last_tick / alive,
        "social_influenced_per_tick_total": simulation.total_social_influenced_creatures / max(1, simulation.tick_count),
        "social_flee_multiplier_avg_total": avg_social_flee_multiplier_total,
        "memory_focus_food_users_avg_tick": avg_memory_focus_food_users_tick,
        "memory_focus_food_users_avg_total": avg_memory_focus_food_users_total,
        "memory_focus_food_usage_bias_tick": memory_focus_food_usage_bias_tick,
        "memory_focus_food_usage_bias_total": memory_focus_food_usage_bias_total,
        "memory_focus_danger_users_avg_tick": avg_memory_focus_danger_users_tick,
        "memory_focus_danger_users_avg_total": avg_memory_focus_danger_users_total,
        "memory_focus_danger_usage_bias_tick": memory_focus_danger_usage_bias_tick,
        "memory_focus_danger_usage_bias_total": memory_focus_danger_usage_bias_total,
        "social_sensitivity_follow_users_avg_tick": avg_social_sensitivity_follow_users_tick,
        "social_sensitivity_follow_users_avg_total": avg_social_sensitivity_follow_users_total,
        "social_sensitivity_follow_usage_bias_tick": social_sensitivity_follow_usage_bias_tick,
        "social_sensitivity_follow_usage_bias_total": social_sensitivity_follow_usage_bias_total,
        "social_sensitivity_flee_boost_users_avg_tick": avg_social_sensitivity_flee_boost_users_tick,
        "social_sensitivity_flee_boost_users_avg_total": avg_social_sensitivity_flee_boost_users_total,
        "social_sensitivity_flee_boost_usage_bias_tick": social_sensitivity_flee_boost_usage_bias_tick,
        "social_sensitivity_flee_boost_usage_bias_total": social_sensitivity_flee_boost_usage_bias_total,
        "food_detection_moves_last_tick": simulation.food_detection_moves_last_tick,
        "total_food_detection_moves": simulation.total_food_detection_moves,
        "food_consumptions_last_tick": simulation.food_consumptions_last_tick,
        "total_food_consumptions": simulation.total_food_consumptions,
        "threat_detection_flee_last_tick": simulation.threat_detection_flee_last_tick,
        "total_threat_detection_flee": simulation.total_threat_detection_flee,
        "food_detection_usage_per_alive_tick": simulation.food_detection_moves_last_tick / alive,
        "food_detection_usage_per_tick_total": simulation.total_food_detection_moves / max(1, simulation.tick_count),
        "food_consumption_usage_per_alive_tick": simulation.food_consumptions_last_tick / alive,
        "food_consumption_usage_per_tick_total": simulation.total_food_consumptions / max(1, simulation.tick_count),
        "threat_detection_usage_per_alive_tick": simulation.threat_detection_flee_last_tick / alive,
        "threat_detection_usage_per_tick_total": simulation.total_threat_detection_flee / max(1, simulation.tick_count),
        "food_perception_detection_users_avg_tick": avg_food_perception_detection_users_tick,
        "food_perception_detection_users_avg_total": avg_food_perception_detection_users_total,
        "food_perception_detection_usage_bias_tick": food_perception_detection_usage_bias_tick,
        "food_perception_detection_usage_bias_total": food_perception_detection_usage_bias_total,
        "food_perception_consumption_users_avg_tick": avg_food_perception_consumption_users_tick,
        "food_perception_consumption_users_avg_total": avg_food_perception_consumption_users_total,
        "food_perception_consumption_usage_bias_tick": food_perception_consumption_usage_bias_tick,
        "food_perception_consumption_usage_bias_total": food_perception_consumption_usage_bias_total,
        "threat_perception_flee_users_avg_tick": avg_threat_perception_flee_users_tick,
        "threat_perception_flee_users_avg_total": avg_threat_perception_flee_users_total,
        "threat_perception_flee_usage_bias_tick": threat_perception_flee_usage_bias_tick,
        "threat_perception_flee_usage_bias_total": threat_perception_flee_usage_bias_total,
        "risk_taking_flee_users_avg_tick": avg_risk_taking_flee_users_tick,
        "risk_taking_flee_users_avg_total": avg_risk_taking_flee_users_total,
        "risk_taking_flee_usage_bias_tick": risk_taking_flee_usage_bias_tick,
        "risk_taking_flee_usage_bias_total": risk_taking_flee_usage_bias_total,
        "persistence_holds_last_tick": simulation.persistence_holds_last_tick,
        "total_persistence_holds": simulation.total_persistence_holds,
        "persistence_hold_usage_per_alive_tick": simulation.persistence_holds_last_tick / alive,
        "persistence_hold_usage_per_tick_total": simulation.total_persistence_holds / max(1, simulation.tick_count),
        "behavior_persistence_hold_users_avg_tick": avg_behavior_persistence_hold_users_tick,
        "behavior_persistence_hold_users_avg_total": avg_behavior_persistence_hold_users_total,
        "behavior_persistence_hold_usage_bias_tick": behavior_persistence_hold_usage_bias_tick,
        "behavior_persistence_hold_usage_bias_total": behavior_persistence_hold_usage_bias_total,
        "exploration_bias_guided_moves_last_tick": simulation.exploration_bias_guided_moves_last_tick,
        "total_exploration_bias_guided_moves": simulation.total_exploration_bias_guided_moves,
        "exploration_bias_usage_per_alive_tick": simulation.exploration_bias_guided_moves_last_tick / alive,
        "exploration_bias_usage_per_tick_total": (
            simulation.total_exploration_bias_guided_moves / max(1, simulation.tick_count)
        ),
        "exploration_bias_guided_users_avg_tick": avg_exploration_bias_guided_users_tick,
        "exploration_bias_guided_users_avg_total": avg_exploration_bias_guided_users_total,
        "exploration_bias_guided_usage_bias_tick": exploration_bias_guided_usage_bias_tick,
        "exploration_bias_guided_usage_bias_total": exploration_bias_guided_usage_bias_total,
        "exploration_bias_explore_moves_last_tick": simulation.exploration_bias_explore_moves_last_tick,
        "total_exploration_bias_explore_moves": simulation.total_exploration_bias_explore_moves,
        "exploration_bias_explore_users_avg_tick": avg_exploration_bias_explore_users_tick,
        "exploration_bias_explore_users_avg_total": avg_exploration_bias_explore_users_total,
        "exploration_bias_explore_usage_bias_tick": exploration_bias_explore_usage_bias_tick,
        "exploration_bias_explore_usage_bias_total": exploration_bias_explore_usage_bias_total,
        "exploration_bias_settle_moves_last_tick": simulation.exploration_bias_settle_moves_last_tick,
        "total_exploration_bias_settle_moves": simulation.total_exploration_bias_settle_moves,
        "exploration_bias_settle_users_avg_tick": avg_exploration_bias_settle_users_tick,
        "exploration_bias_settle_users_avg_total": avg_exploration_bias_settle_users_total,
        "exploration_bias_settle_usage_bias_tick": exploration_bias_settle_usage_bias_tick,
        "exploration_bias_settle_usage_bias_total": exploration_bias_settle_usage_bias_total,
        "exploration_bias_explore_share_last_tick": exploration_bias_explore_share_last_tick,
        "exploration_bias_explore_share_total": exploration_bias_explore_share_total,
        "avg_exploration_bias_anchor_distance_delta_last_tick": (
            simulation.avg_exploration_bias_anchor_distance_delta_last_tick
        ),
        "avg_exploration_bias_anchor_distance_delta_total": avg_exploration_bias_anchor_distance_delta_total,
        "density_preference_guided_moves_last_tick": simulation.density_preference_guided_moves_last_tick,
        "total_density_preference_guided_moves": simulation.total_density_preference_guided_moves,
        "density_preference_usage_per_alive_tick": (
            simulation.density_preference_guided_moves_last_tick / alive
        ),
        "density_preference_usage_per_tick_total": (
            simulation.total_density_preference_guided_moves / max(1, simulation.tick_count)
        ),
        "density_preference_guided_users_avg_tick": avg_density_preference_guided_users_tick,
        "density_preference_guided_users_avg_total": avg_density_preference_guided_users_total,
        "density_preference_guided_usage_bias_tick": density_preference_guided_usage_bias_tick,
        "density_preference_guided_usage_bias_total": density_preference_guided_usage_bias_total,
        "density_preference_seek_moves_last_tick": simulation.density_preference_seek_moves_last_tick,
        "total_density_preference_seek_moves": simulation.total_density_preference_seek_moves,
        "density_preference_seek_usage_per_alive_tick": (
            simulation.density_preference_seek_moves_last_tick / max(1, alive)
        ),
        "density_preference_seek_usage_per_tick_total": (
            simulation.total_density_preference_seek_moves / max(1, simulation.tick_count)
        ),
        "density_preference_seek_users_avg_tick": avg_density_preference_seek_users_tick,
        "density_preference_seek_users_avg_total": avg_density_preference_seek_users_total,
        "density_preference_seek_usage_bias_tick": density_preference_seek_usage_bias_tick,
        "density_preference_seek_usage_bias_total": density_preference_seek_usage_bias_total,
        "density_preference_avoid_moves_last_tick": simulation.density_preference_avoid_moves_last_tick,
        "total_density_preference_avoid_moves": simulation.total_density_preference_avoid_moves,
        "density_preference_avoid_usage_per_alive_tick": (
            simulation.density_preference_avoid_moves_last_tick / max(1, alive)
        ),
        "density_preference_avoid_usage_per_tick_total": (
            simulation.total_density_preference_avoid_moves / max(1, simulation.tick_count)
        ),
        "density_preference_avoid_users_avg_tick": avg_density_preference_avoid_users_tick,
        "density_preference_avoid_users_avg_total": avg_density_preference_avoid_users_total,
        "density_preference_avoid_usage_bias_tick": density_preference_avoid_usage_bias_tick,
        "density_preference_avoid_usage_bias_total": density_preference_avoid_usage_bias_total,
        "density_preference_seek_share_last_tick": density_preference_seek_share_last_tick,
        "density_preference_seek_share_total": density_preference_seek_share_total,
        "density_preference_avoid_share_last_tick": (
            1.0 - density_preference_seek_share_last_tick
            if simulation.density_preference_guided_moves_last_tick > 0
            else 0.0
        ),
        "density_preference_avoid_share_total": (
            1.0 - density_preference_seek_share_total
            if simulation.total_density_preference_guided_moves > 0
            else 0.0
        ),
        "avg_density_preference_neighbor_count_last_tick": avg_density_preference_neighbor_count_last_tick,
        "avg_density_preference_neighbor_count_total": avg_density_preference_neighbor_count_total,
        "avg_density_preference_center_distance_delta_last_tick": (
            simulation.avg_density_preference_center_distance_delta_last_tick
        ),
        "avg_density_preference_center_distance_delta_total": avg_density_preference_center_distance_delta_total,
        "search_wander_switches_last_tick": simulation.search_wander_switches_last_tick,
        "total_search_wander_switches": simulation.total_search_wander_switches,
        "search_wander_switches_prevented_last_tick": simulation.search_wander_switches_prevented_last_tick,
        "total_search_wander_switches_prevented": simulation.total_search_wander_switches_prevented,
        "search_wander_oscillation_events_last_tick": simulation.search_wander_oscillation_events_last_tick,
        "total_search_wander_oscillation_events": simulation.total_search_wander_oscillation_events,
        "search_wander_switch_rate_last_tick": search_wander_switch_rate_last_tick,
        "search_wander_switch_rate_total": search_wander_switch_rate_total,
        "search_wander_prevented_rate_last_tick": search_wander_prevented_rate_last_tick,
        "search_wander_prevented_rate_total": search_wander_prevented_rate_total,
        "borderline_threat_encounters_last_tick": simulation.borderline_threat_encounters_last_tick,
        "total_borderline_threat_encounters": simulation.total_borderline_threat_encounters,
        "borderline_threat_flees_last_tick": simulation.borderline_threat_flees_last_tick,
        "total_borderline_threat_flees": simulation.total_borderline_threat_flees,
        "borderline_threat_flee_rate_last_tick": borderline_threat_flee_rate_tick,
        "borderline_threat_flee_rate_total": borderline_threat_flee_rate_total,
        "risk_taking_borderline_encounter_users_avg_tick": avg_risk_taking_borderline_encounter_users_tick,
        "risk_taking_borderline_encounter_users_avg_total": avg_risk_taking_borderline_encounter_users_total,
        "risk_taking_borderline_flee_users_avg_tick": avg_risk_taking_borderline_flee_users_tick,
        "risk_taking_borderline_flee_users_avg_total": avg_risk_taking_borderline_flee_users_total,
        "risk_taking_borderline_flee_usage_bias_tick": risk_taking_borderline_flee_usage_bias_tick,
        "risk_taking_borderline_flee_usage_bias_total": risk_taking_borderline_flee_usage_bias_total,
        "death_causes_last_tick": dict(simulation.death_causes_last_tick),
        "death_causes_total": dict(simulation.total_death_causes),
    }

def build_generation_distribution(simulation: HungerSimulation) -> Dict[int, int]:
    distribution: Dict[int, int] = {}
    for creature in simulation.creatures:
        distribution[creature.generation] = distribution.get(creature.generation, 0) + 1
    return distribution


def create_proto_temporal_tracker() -> Dict[str, object]:
    return {
        "observations": 0,
        "by_signature": {},
    }


def update_proto_temporal_tracker(tracker: Dict[str, object], stats: Dict[str, object]) -> None:
    tracker["observations"] = int(tracker.get("observations", 0)) + 1

    by_signature = tracker.get("by_signature")
    if not isinstance(by_signature, dict):
        by_signature = {}
        tracker["by_signature"] = by_signature

    raw_trends = stats.get("proto_group_temporal_trends")
    if not isinstance(raw_trends, list):
        return

    for trend in raw_trends:
        if not isinstance(trend, dict):
            continue

        signature = str(trend.get("signature", "?"))
        status = str(trend.get("status", ""))
        if status not in _PROTO_TEMPORAL_STATUSES:
            continue

        counts = by_signature.get(signature)
        if not isinstance(counts, dict):
            counts = _empty_proto_temporal_summary()
            by_signature[signature] = counts

        counts[status] = int(counts.get(status, 0)) + 1


def build_final_run_summary(
    final_stats: Dict[str, object],
    temporal_tracker: Dict[str, object],
) -> Dict[str, object]:
    dominant_signature = "-"
    dominant_share = 0.0

    raw_top_groups = final_stats.get("proto_groups_top")
    if isinstance(raw_top_groups, list) and len(raw_top_groups) > 0:
        first = raw_top_groups[0]
        if isinstance(first, dict):
            dominant_signature = str(first.get("signature", "-"))
            dominant_share = float(first.get("share", 0.0))

    by_signature = _read_status_counts(temporal_tracker)
    stable_signature, stable_count = _pick_signature_by_status(by_signature, "stable")
    rising_signature, rising_count = _pick_signature_by_status(by_signature, "en_hausse")

    memory_impact = {
        "food_usage_total": int(final_stats.get("total_food_memory_guided_moves", 0)),
        "danger_usage_total": int(final_stats.get("total_danger_memory_avoid_moves", 0)),
        "food_active_share": float(final_stats.get("food_memory_active_share", 0.0)),
        "danger_active_share": float(final_stats.get("danger_memory_active_share", 0.0)),
        "food_effect_avg_distance": float(final_stats.get("food_memory_effect_avg_distance_total", 0.0)),
        "danger_effect_avg_distance": float(final_stats.get("danger_memory_effect_avg_distance_total", 0.0)),
        "food_usage_per_tick": float(final_stats.get("food_memory_usage_per_tick_total", 0.0)),
        "danger_usage_per_tick": float(final_stats.get("danger_memory_usage_per_tick_total", 0.0)),
    }
    social_impact = {
        "follow_usage_total": int(final_stats.get("total_social_follow_moves", 0)),
        "flee_boost_usage_total": int(final_stats.get("total_social_flee_boosted", 0)),
        "influenced_count_last_tick": int(final_stats.get("social_influenced_creatures_last_tick", 0)),
        "influenced_share_last_tick": float(final_stats.get("social_influenced_share_last_tick", 0.0)),
        "influenced_per_tick": float(final_stats.get("social_influenced_per_tick_total", 0.0)),
        "follow_usage_per_tick": float(final_stats.get("social_follow_usage_per_tick_total", 0.0)),
        "flee_boost_usage_per_tick": float(final_stats.get("social_flee_boost_usage_per_tick_total", 0.0)),
        "flee_multiplier_avg_tick": float(final_stats.get("avg_social_flee_multiplier_last_tick", 1.0)),
        "flee_multiplier_avg_total": float(final_stats.get("social_flee_multiplier_avg_total", 1.0)),
    }
    trait_impact = {
        "memory_focus_mean": float(final_stats.get("avg_memory_focus", 0.0)),
        "memory_focus_std": float(final_stats.get("std_memory_focus", 0.0)),
        "social_sensitivity_mean": float(final_stats.get("avg_social_sensitivity", 0.0)),
        "social_sensitivity_std": float(final_stats.get("std_social_sensitivity", 0.0)),
        "food_perception_mean": float(final_stats.get("avg_food_perception", 0.0)),
        "food_perception_std": float(final_stats.get("std_food_perception", 0.0)),
        "threat_perception_mean": float(final_stats.get("avg_threat_perception", 0.0)),
        "threat_perception_std": float(final_stats.get("std_threat_perception", 0.0)),
        "risk_taking_mean": float(final_stats.get("avg_risk_taking", 0.0)),
        "risk_taking_std": float(final_stats.get("std_risk_taking", 0.0)),
        "behavior_persistence_mean": float(final_stats.get("avg_behavior_persistence", 0.0)),
        "behavior_persistence_std": float(final_stats.get("std_behavior_persistence", 0.0)),
        "exploration_bias_mean": float(final_stats.get("avg_exploration_bias", 0.0)),
        "exploration_bias_std": float(final_stats.get("std_exploration_bias", 0.0)),
        "density_preference_mean": float(final_stats.get("avg_density_preference", 0.0)),
        "density_preference_std": float(final_stats.get("std_density_preference", 0.0)),
        "energy_efficiency_mean": float(final_stats.get("avg_energy_efficiency", 0.0)),
        "energy_efficiency_std": float(final_stats.get("std_energy_efficiency", 0.0)),
        "exhaustion_resistance_mean": float(final_stats.get("avg_exhaustion_resistance", 0.0)),
        "exhaustion_resistance_std": float(final_stats.get("std_exhaustion_resistance", 0.0)),
        "energy_efficiency_drain_bias": float(final_stats.get("energy_efficiency_drain_usage_bias_total", 0.0)),
        "exhaustion_resistance_reproduction_bias": float(
            final_stats.get("exhaustion_resistance_reproduction_usage_bias_total", 0.0)
        ),
        "energy_drain_multiplier_observed": float(
            final_stats.get("avg_energy_drain_multiplier_observed_total", 0.0)
        ),
        "reproduction_cost_multiplier_observed": float(
            final_stats.get("avg_reproduction_cost_multiplier_observed_total", 0.0)
        ),
        "energy_drain_amount_observed": float(final_stats.get("avg_energy_drain_amount_total", 0.0)),
        "reproduction_cost_amount_observed": float(final_stats.get("avg_reproduction_cost_amount_total", 0.0)),
        "memory_focus_food_bias": float(final_stats.get("memory_focus_food_usage_bias_total", 0.0)),
        "memory_focus_danger_bias": float(final_stats.get("memory_focus_danger_usage_bias_total", 0.0)),
        "social_sensitivity_follow_bias": float(final_stats.get("social_sensitivity_follow_usage_bias_total", 0.0)),
        "social_sensitivity_flee_boost_bias": float(final_stats.get("social_sensitivity_flee_boost_usage_bias_total", 0.0)),
        "food_perception_detection_bias": float(final_stats.get("food_perception_detection_usage_bias_total", 0.0)),
        "food_perception_consumption_bias": float(final_stats.get("food_perception_consumption_usage_bias_total", 0.0)),
        "threat_perception_flee_bias": float(final_stats.get("threat_perception_flee_usage_bias_total", 0.0)),
        "risk_taking_flee_bias": float(final_stats.get("risk_taking_flee_usage_bias_total", 0.0)),
        "behavior_persistence_hold_bias": float(
            final_stats.get("behavior_persistence_hold_usage_bias_total", 0.0)
        ),
        "exploration_bias_guided_bias": float(
            final_stats.get("exploration_bias_guided_usage_bias_total", 0.0)
        ),
        "exploration_bias_guided_total": int(final_stats.get("total_exploration_bias_guided_moves", 0)),
        "exploration_bias_explore_share": float(
            final_stats.get("exploration_bias_explore_share_total", 0.0)
        ),
        "exploration_bias_explore_users_avg": float(
            final_stats.get("exploration_bias_explore_users_avg_total", 0.0)
        ),
        "exploration_bias_explore_usage_bias": float(
            final_stats.get("exploration_bias_explore_usage_bias_total", 0.0)
        ),
        "exploration_bias_settle_users_avg": float(
            final_stats.get("exploration_bias_settle_users_avg_total", 0.0)
        ),
        "exploration_bias_settle_usage_bias": float(
            final_stats.get("exploration_bias_settle_usage_bias_total", 0.0)
        ),
        "exploration_bias_anchor_distance_delta": float(
            final_stats.get("avg_exploration_bias_anchor_distance_delta_total", 0.0)
        ),
        "density_preference_guided_bias": float(
            final_stats.get("density_preference_guided_usage_bias_total", 0.0)
        ),
        "density_preference_guided_total": int(
            final_stats.get("total_density_preference_guided_moves", 0)
        ),
        "density_preference_seek_total": int(final_stats.get("total_density_preference_seek_moves", 0)),
        "density_preference_avoid_total": int(final_stats.get("total_density_preference_avoid_moves", 0)),
        "density_preference_seek_usage_per_tick": float(
            final_stats.get("density_preference_seek_usage_per_tick_total", 0.0)
        ),
        "density_preference_avoid_usage_per_tick": float(
            final_stats.get("density_preference_avoid_usage_per_tick_total", 0.0)
        ),
        "density_preference_seek_share": float(final_stats.get("density_preference_seek_share_total", 0.0)),
        "density_preference_avoid_share": float(final_stats.get("density_preference_avoid_share_total", 0.0)),
        "density_preference_seek_users_avg": float(
            final_stats.get("density_preference_seek_users_avg_total", 0.0)
        ),
        "density_preference_seek_usage_bias": float(
            final_stats.get("density_preference_seek_usage_bias_total", 0.0)
        ),
        "density_preference_avoid_users_avg": float(
            final_stats.get("density_preference_avoid_users_avg_total", 0.0)
        ),
        "density_preference_avoid_usage_bias": float(
            final_stats.get("density_preference_avoid_usage_bias_total", 0.0)
        ),
        "density_preference_neighbor_count_avg": float(
            final_stats.get("avg_density_preference_neighbor_count_total", 0.0)
        ),
        "density_preference_center_distance_delta": float(
            final_stats.get("avg_density_preference_center_distance_delta_total", 0.0)
        ),
        "persistence_holds_total": int(final_stats.get("total_persistence_holds", 0)),
        "behavior_persistence_oscillation_switch_rate": float(
            final_stats.get("search_wander_switch_rate_total", 0.0)
        ),
        "behavior_persistence_oscillation_prevented_rate": float(
            final_stats.get("search_wander_prevented_rate_total", 0.0)
        ),
        "search_wander_switches_total": int(final_stats.get("total_search_wander_switches", 0)),
        "search_wander_switches_prevented_total": int(
            final_stats.get("total_search_wander_switches_prevented", 0)
        ),
        "search_wander_oscillation_events_total": int(
            final_stats.get("total_search_wander_oscillation_events", 0)
        ),
        "borderline_threat_encounters": int(final_stats.get("total_borderline_threat_encounters", 0)),
        "borderline_threat_flees": int(final_stats.get("total_borderline_threat_flees", 0)),
        "borderline_threat_flee_rate": float(final_stats.get("borderline_threat_flee_rate_total", 0.0)),
        "risk_taking_borderline_encounter_mean": float(
            final_stats.get("risk_taking_borderline_encounter_users_avg_total", 0.0)
        ),
        "risk_taking_borderline_flee_mean": float(
            final_stats.get("risk_taking_borderline_flee_users_avg_total", 0.0)
        ),
        "risk_taking_borderline_flee_bias": float(
            final_stats.get("risk_taking_borderline_flee_usage_bias_total", 0.0)
        ),
    }

    return {
        "final_dominant_group_signature": dominant_signature,
        "final_dominant_group_share": dominant_share,
        "most_stable_group_signature": stable_signature,
        "most_stable_group_count": stable_count,
        "most_rising_group_signature": rising_signature,
        "most_rising_group_count": rising_count,
        "final_zone_distribution": _normalize_zone_distribution(
            final_stats.get("creatures_by_fertility_zone")
        ),
        "avg_traits": _read_avg_traits(final_stats),
        "memory_impact": memory_impact,
        "social_impact": social_impact,
        "trait_impact": trait_impact,
        "observed_logs": int(temporal_tracker.get("observations", 0)),
    }


def build_multi_run_summary(run_results: Iterable[Dict[str, object]]) -> Dict[str, object]:
    runs = list(run_results)
    run_count = len(runs)
    if run_count == 0:
        return {
            "runs": 0,
            "seeds": [],
            "extinction_count": 0,
            "extinction_rate": 0.0,
            "avg_max_generation": 0.0,
            "avg_final_population": 0.0,
            "avg_final_traits": {
                "speed": 0.0,
                "metabolism": 0.0,
                "prudence": 0.0,
                "dominance": 0.0,
                "repro_drive": 0.0,
                "food_perception": 0.0,
                "threat_perception": 0.0,
                "risk_taking": 0.0,
                "behavior_persistence": 0.0,
                "exploration_bias": 0.0,
                "density_preference": 0.0,
                "energy_efficiency": 0.0,
                "exhaustion_resistance": 0.0,
            },
            "avg_memory_impact": {
                "food_usage_total": 0.0,
                "danger_usage_total": 0.0,
                "food_active_share": 0.0,
                "danger_active_share": 0.0,
                "food_effect_avg_distance": 0.0,
                "danger_effect_avg_distance": 0.0,
                "food_usage_per_tick": 0.0,
                "danger_usage_per_tick": 0.0,
            },
            "avg_social_impact": {
                "follow_usage_total": 0.0,
                "flee_boost_usage_total": 0.0,
                "influenced_count_last_tick": 0.0,
                "influenced_share_last_tick": 0.0,
                "influenced_per_tick": 0.0,
                "follow_usage_per_tick": 0.0,
                "flee_boost_usage_per_tick": 0.0,
                "flee_multiplier_avg_tick": 1.0,
                "flee_multiplier_avg_total": 1.0,
            },
            "avg_trait_impact": {
                "memory_focus_mean": 0.0,
                "memory_focus_std": 0.0,
                "social_sensitivity_mean": 0.0,
                "social_sensitivity_std": 0.0,
                "food_perception_mean": 0.0,
                "food_perception_std": 0.0,
                "threat_perception_mean": 0.0,
                "threat_perception_std": 0.0,
                "risk_taking_mean": 0.0,
                "risk_taking_std": 0.0,
                "behavior_persistence_mean": 0.0,
                "behavior_persistence_std": 0.0,
                "exploration_bias_mean": 0.0,
                "exploration_bias_std": 0.0,
                "density_preference_mean": 0.0,
                "density_preference_std": 0.0,
                "energy_efficiency_mean": 0.0,
                "energy_efficiency_std": 0.0,
                "exhaustion_resistance_mean": 0.0,
                "exhaustion_resistance_std": 0.0,
                "energy_efficiency_drain_bias": 0.0,
                "exhaustion_resistance_reproduction_bias": 0.0,
                "energy_drain_multiplier_observed": 0.0,
                "reproduction_cost_multiplier_observed": 0.0,
                "energy_drain_amount_observed": 0.0,
                "reproduction_cost_amount_observed": 0.0,
                "memory_focus_food_bias": 0.0,
                "memory_focus_danger_bias": 0.0,
                "social_sensitivity_follow_bias": 0.0,
                "social_sensitivity_flee_boost_bias": 0.0,
                "food_perception_detection_bias": 0.0,
                "food_perception_consumption_bias": 0.0,
                "threat_perception_flee_bias": 0.0,
                "risk_taking_flee_bias": 0.0,
                "behavior_persistence_hold_bias": 0.0,
                "exploration_bias_guided_bias": 0.0,
                "exploration_bias_guided_total": 0.0,
                "exploration_bias_explore_share": 0.0,
                "exploration_bias_explore_users_avg": 0.0,
                "exploration_bias_explore_usage_bias": 0.0,
                "exploration_bias_settle_users_avg": 0.0,
                "exploration_bias_settle_usage_bias": 0.0,
                "exploration_bias_anchor_distance_delta": 0.0,
                "density_preference_guided_bias": 0.0,
                "density_preference_guided_total": 0.0,
                "density_preference_seek_total": 0.0,
                "density_preference_avoid_total": 0.0,
                "density_preference_seek_usage_per_tick": 0.0,
                "density_preference_avoid_usage_per_tick": 0.0,
                "density_preference_seek_share": 0.0,
                "density_preference_avoid_share": 0.0,
                "density_preference_seek_users_avg": 0.0,
                "density_preference_seek_usage_bias": 0.0,
                "density_preference_avoid_users_avg": 0.0,
                "density_preference_avoid_usage_bias": 0.0,
                "density_preference_neighbor_count_avg": 0.0,
                "density_preference_center_distance_delta": 0.0,
                "persistence_holds_total": 0.0,
                "behavior_persistence_oscillation_switch_rate": 0.0,
                "behavior_persistence_oscillation_prevented_rate": 0.0,
                "search_wander_switches_total": 0.0,
                "search_wander_switches_prevented_total": 0.0,
                "search_wander_oscillation_events_total": 0.0,
                "borderline_threat_encounters": 0.0,
                "borderline_threat_flees": 0.0,
                "borderline_threat_flee_rate": 0.0,
                "risk_taking_borderline_encounter_mean": 0.0,
                "risk_taking_borderline_flee_mean": 0.0,
                "risk_taking_borderline_flee_bias": 0.0,
            },
            "most_frequent_final_dominant_group": "-",
            "most_frequent_final_dominant_group_count": 0,
            "most_frequent_final_dominant_group_share": 0.0,
        }

    seeds: list[int] = []
    extinction_count = 0
    max_generation_sum = 0.0
    final_population_sum = 0.0

    avg_traits_acc = {
        "speed": 0.0,
        "metabolism": 0.0,
        "prudence": 0.0,
        "dominance": 0.0,
        "repro_drive": 0.0,
        "food_perception": 0.0,
        "threat_perception": 0.0,
        "risk_taking": 0.0,
        "behavior_persistence": 0.0,
        "exploration_bias": 0.0,
        "density_preference": 0.0,
        "energy_efficiency": 0.0,
        "exhaustion_resistance": 0.0,
    }
    avg_memory_acc = {
        "food_usage_total": 0.0,
        "danger_usage_total": 0.0,
        "food_active_share": 0.0,
        "danger_active_share": 0.0,
        "food_effect_avg_distance": 0.0,
        "danger_effect_avg_distance": 0.0,
        "food_usage_per_tick": 0.0,
        "danger_usage_per_tick": 0.0,
    }
    avg_social_acc = {
        "follow_usage_total": 0.0,
        "flee_boost_usage_total": 0.0,
        "influenced_count_last_tick": 0.0,
        "influenced_share_last_tick": 0.0,
        "influenced_per_tick": 0.0,
        "follow_usage_per_tick": 0.0,
        "flee_boost_usage_per_tick": 0.0,
        "flee_multiplier_avg_tick": 0.0,
        "flee_multiplier_avg_total": 0.0,
    }
    avg_trait_impact_acc = {
        "memory_focus_mean": 0.0,
        "memory_focus_std": 0.0,
        "social_sensitivity_mean": 0.0,
        "social_sensitivity_std": 0.0,
        "food_perception_mean": 0.0,
        "food_perception_std": 0.0,
        "threat_perception_mean": 0.0,
        "threat_perception_std": 0.0,
        "risk_taking_mean": 0.0,
        "risk_taking_std": 0.0,
        "behavior_persistence_mean": 0.0,
        "behavior_persistence_std": 0.0,
        "exploration_bias_mean": 0.0,
        "exploration_bias_std": 0.0,
        "density_preference_mean": 0.0,
        "density_preference_std": 0.0,
        "energy_efficiency_mean": 0.0,
        "energy_efficiency_std": 0.0,
        "exhaustion_resistance_mean": 0.0,
        "exhaustion_resistance_std": 0.0,
        "energy_efficiency_drain_bias": 0.0,
        "exhaustion_resistance_reproduction_bias": 0.0,
        "energy_drain_multiplier_observed": 0.0,
        "reproduction_cost_multiplier_observed": 0.0,
        "energy_drain_amount_observed": 0.0,
        "reproduction_cost_amount_observed": 0.0,
        "memory_focus_food_bias": 0.0,
        "memory_focus_danger_bias": 0.0,
        "social_sensitivity_follow_bias": 0.0,
        "social_sensitivity_flee_boost_bias": 0.0,
        "food_perception_detection_bias": 0.0,
        "food_perception_consumption_bias": 0.0,
        "threat_perception_flee_bias": 0.0,
        "risk_taking_flee_bias": 0.0,
        "behavior_persistence_hold_bias": 0.0,
        "exploration_bias_guided_bias": 0.0,
        "exploration_bias_guided_total": 0.0,
        "exploration_bias_explore_share": 0.0,
        "exploration_bias_explore_users_avg": 0.0,
        "exploration_bias_explore_usage_bias": 0.0,
        "exploration_bias_settle_users_avg": 0.0,
        "exploration_bias_settle_usage_bias": 0.0,
        "exploration_bias_anchor_distance_delta": 0.0,
        "density_preference_guided_bias": 0.0,
        "density_preference_guided_total": 0.0,
        "density_preference_seek_total": 0.0,
        "density_preference_avoid_total": 0.0,
        "density_preference_seek_usage_per_tick": 0.0,
        "density_preference_avoid_usage_per_tick": 0.0,
        "density_preference_seek_share": 0.0,
        "density_preference_avoid_share": 0.0,
        "density_preference_seek_users_avg": 0.0,
        "density_preference_seek_usage_bias": 0.0,
        "density_preference_avoid_users_avg": 0.0,
        "density_preference_avoid_usage_bias": 0.0,
        "density_preference_neighbor_count_avg": 0.0,
        "density_preference_center_distance_delta": 0.0,
        "persistence_holds_total": 0.0,
        "behavior_persistence_oscillation_switch_rate": 0.0,
        "behavior_persistence_oscillation_prevented_rate": 0.0,
        "search_wander_switches_total": 0.0,
        "search_wander_switches_prevented_total": 0.0,
        "search_wander_oscillation_events_total": 0.0,
        "borderline_threat_encounters": 0.0,
        "borderline_threat_flees": 0.0,
        "borderline_threat_flee_rate": 0.0,
        "risk_taking_borderline_encounter_mean": 0.0,
        "risk_taking_borderline_flee_mean": 0.0,
        "risk_taking_borderline_flee_bias": 0.0,
    }

    dominant_frequency: Dict[str, int] = {}

    for run in runs:
        seeds.append(int(run.get("seed", 0)))

        if bool(run.get("extinct", False)):
            extinction_count += 1

        max_generation_sum += float(run.get("max_generation", 0.0))
        final_population_sum += float(run.get("final_alive", 0.0))

        run_summary = run.get("run_summary")
        if isinstance(run_summary, dict):
            signature = str(run_summary.get("final_dominant_group_signature", "-"))
            if signature != "-":
                dominant_frequency[signature] = dominant_frequency.get(signature, 0) + 1

            traits_raw = run_summary.get("avg_traits")
            if isinstance(traits_raw, dict):
                avg_traits_acc["speed"] += float(traits_raw.get("speed", 0.0))
                avg_traits_acc["metabolism"] += float(traits_raw.get("metabolism", 0.0))
                avg_traits_acc["prudence"] += float(traits_raw.get("prudence", 0.0))
                avg_traits_acc["dominance"] += float(traits_raw.get("dominance", 0.0))
                avg_traits_acc["repro_drive"] += float(traits_raw.get("repro_drive", 0.0))
                avg_traits_acc["food_perception"] += float(traits_raw.get("food_perception", 0.0))
                avg_traits_acc["threat_perception"] += float(traits_raw.get("threat_perception", 0.0))
                avg_traits_acc["risk_taking"] += float(traits_raw.get("risk_taking", 0.0))
                avg_traits_acc["behavior_persistence"] += float(
                    traits_raw.get("behavior_persistence", 0.0)
                )
                avg_traits_acc["exploration_bias"] += float(traits_raw.get("exploration_bias", 0.0))
                avg_traits_acc["density_preference"] += float(
                    traits_raw.get("density_preference", 0.0)
                )
                avg_traits_acc["energy_efficiency"] += float(traits_raw.get("energy_efficiency", 0.0))
                avg_traits_acc["exhaustion_resistance"] += float(traits_raw.get("exhaustion_resistance", 0.0))

            memory_raw = run_summary.get("memory_impact")
            if isinstance(memory_raw, dict):
                avg_memory_acc["food_usage_total"] += float(memory_raw.get("food_usage_total", 0.0))
                avg_memory_acc["danger_usage_total"] += float(memory_raw.get("danger_usage_total", 0.0))
                avg_memory_acc["food_active_share"] += float(memory_raw.get("food_active_share", 0.0))
                avg_memory_acc["danger_active_share"] += float(memory_raw.get("danger_active_share", 0.0))
                avg_memory_acc["food_effect_avg_distance"] += float(memory_raw.get("food_effect_avg_distance", 0.0))
                avg_memory_acc["danger_effect_avg_distance"] += float(memory_raw.get("danger_effect_avg_distance", 0.0))
                avg_memory_acc["food_usage_per_tick"] += float(memory_raw.get("food_usage_per_tick", 0.0))
                avg_memory_acc["danger_usage_per_tick"] += float(memory_raw.get("danger_usage_per_tick", 0.0))

            social_raw = run_summary.get("social_impact")
            if isinstance(social_raw, dict):
                avg_social_acc["follow_usage_total"] += float(social_raw.get("follow_usage_total", 0.0))
                avg_social_acc["flee_boost_usage_total"] += float(social_raw.get("flee_boost_usage_total", 0.0))
                avg_social_acc["influenced_count_last_tick"] += float(social_raw.get("influenced_count_last_tick", 0.0))
                avg_social_acc["influenced_share_last_tick"] += float(social_raw.get("influenced_share_last_tick", 0.0))
                avg_social_acc["influenced_per_tick"] += float(social_raw.get("influenced_per_tick", 0.0))
                avg_social_acc["follow_usage_per_tick"] += float(social_raw.get("follow_usage_per_tick", 0.0))
                avg_social_acc["flee_boost_usage_per_tick"] += float(social_raw.get("flee_boost_usage_per_tick", 0.0))
                avg_social_acc["flee_multiplier_avg_tick"] += float(social_raw.get("flee_multiplier_avg_tick", 1.0))
                avg_social_acc["flee_multiplier_avg_total"] += float(social_raw.get("flee_multiplier_avg_total", 1.0))

            trait_impact_raw = run_summary.get("trait_impact")
            if isinstance(trait_impact_raw, dict):
                avg_trait_impact_acc["memory_focus_mean"] += float(trait_impact_raw.get("memory_focus_mean", 0.0))
                avg_trait_impact_acc["memory_focus_std"] += float(trait_impact_raw.get("memory_focus_std", 0.0))
                avg_trait_impact_acc["social_sensitivity_mean"] += float(trait_impact_raw.get("social_sensitivity_mean", 0.0))
                avg_trait_impact_acc["social_sensitivity_std"] += float(trait_impact_raw.get("social_sensitivity_std", 0.0))
                avg_trait_impact_acc["food_perception_mean"] += float(trait_impact_raw.get("food_perception_mean", 0.0))
                avg_trait_impact_acc["food_perception_std"] += float(trait_impact_raw.get("food_perception_std", 0.0))
                avg_trait_impact_acc["threat_perception_mean"] += float(trait_impact_raw.get("threat_perception_mean", 0.0))
                avg_trait_impact_acc["threat_perception_std"] += float(trait_impact_raw.get("threat_perception_std", 0.0))
                avg_trait_impact_acc["risk_taking_mean"] += float(trait_impact_raw.get("risk_taking_mean", 0.0))
                avg_trait_impact_acc["risk_taking_std"] += float(trait_impact_raw.get("risk_taking_std", 0.0))
                avg_trait_impact_acc["behavior_persistence_mean"] += float(
                    trait_impact_raw.get("behavior_persistence_mean", 0.0)
                )
                avg_trait_impact_acc["behavior_persistence_std"] += float(
                    trait_impact_raw.get("behavior_persistence_std", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_mean"] += float(
                    trait_impact_raw.get("exploration_bias_mean", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_std"] += float(
                    trait_impact_raw.get("exploration_bias_std", 0.0)
                )
                avg_trait_impact_acc["density_preference_mean"] += float(
                    trait_impact_raw.get("density_preference_mean", 0.0)
                )
                avg_trait_impact_acc["density_preference_std"] += float(
                    trait_impact_raw.get("density_preference_std", 0.0)
                )
                avg_trait_impact_acc["energy_efficiency_mean"] += float(trait_impact_raw.get("energy_efficiency_mean", 0.0))
                avg_trait_impact_acc["energy_efficiency_std"] += float(trait_impact_raw.get("energy_efficiency_std", 0.0))
                avg_trait_impact_acc["exhaustion_resistance_mean"] += float(trait_impact_raw.get("exhaustion_resistance_mean", 0.0))
                avg_trait_impact_acc["exhaustion_resistance_std"] += float(trait_impact_raw.get("exhaustion_resistance_std", 0.0))
                avg_trait_impact_acc["energy_efficiency_drain_bias"] += float(
                    trait_impact_raw.get("energy_efficiency_drain_bias", 0.0)
                )
                avg_trait_impact_acc["exhaustion_resistance_reproduction_bias"] += float(
                    trait_impact_raw.get("exhaustion_resistance_reproduction_bias", 0.0)
                )
                avg_trait_impact_acc["energy_drain_multiplier_observed"] += float(
                    trait_impact_raw.get("energy_drain_multiplier_observed", 0.0)
                )
                avg_trait_impact_acc["reproduction_cost_multiplier_observed"] += float(
                    trait_impact_raw.get("reproduction_cost_multiplier_observed", 0.0)
                )
                avg_trait_impact_acc["energy_drain_amount_observed"] += float(
                    trait_impact_raw.get("energy_drain_amount_observed", 0.0)
                )
                avg_trait_impact_acc["reproduction_cost_amount_observed"] += float(
                    trait_impact_raw.get("reproduction_cost_amount_observed", 0.0)
                )
                avg_trait_impact_acc["memory_focus_food_bias"] += float(trait_impact_raw.get("memory_focus_food_bias", 0.0))
                avg_trait_impact_acc["memory_focus_danger_bias"] += float(trait_impact_raw.get("memory_focus_danger_bias", 0.0))
                avg_trait_impact_acc["social_sensitivity_follow_bias"] += float(trait_impact_raw.get("social_sensitivity_follow_bias", 0.0))
                avg_trait_impact_acc["social_sensitivity_flee_boost_bias"] += float(trait_impact_raw.get("social_sensitivity_flee_boost_bias", 0.0))
                avg_trait_impact_acc["food_perception_detection_bias"] += float(trait_impact_raw.get("food_perception_detection_bias", 0.0))
                avg_trait_impact_acc["food_perception_consumption_bias"] += float(trait_impact_raw.get("food_perception_consumption_bias", 0.0))
                avg_trait_impact_acc["threat_perception_flee_bias"] += float(trait_impact_raw.get("threat_perception_flee_bias", 0.0))
                avg_trait_impact_acc["risk_taking_flee_bias"] += float(trait_impact_raw.get("risk_taking_flee_bias", 0.0))
                avg_trait_impact_acc["behavior_persistence_hold_bias"] += float(
                    trait_impact_raw.get("behavior_persistence_hold_bias", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_guided_bias"] += float(
                    trait_impact_raw.get("exploration_bias_guided_bias", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_guided_total"] += float(
                    trait_impact_raw.get("exploration_bias_guided_total", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_explore_share"] += float(
                    trait_impact_raw.get("exploration_bias_explore_share", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_explore_users_avg"] += float(
                    trait_impact_raw.get("exploration_bias_explore_users_avg", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_explore_usage_bias"] += float(
                    trait_impact_raw.get("exploration_bias_explore_usage_bias", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_settle_users_avg"] += float(
                    trait_impact_raw.get("exploration_bias_settle_users_avg", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_settle_usage_bias"] += float(
                    trait_impact_raw.get("exploration_bias_settle_usage_bias", 0.0)
                )
                avg_trait_impact_acc["exploration_bias_anchor_distance_delta"] += float(
                    trait_impact_raw.get("exploration_bias_anchor_distance_delta", 0.0)
                )
                avg_trait_impact_acc["density_preference_guided_bias"] += float(
                    trait_impact_raw.get("density_preference_guided_bias", 0.0)
                )
                avg_trait_impact_acc["density_preference_guided_total"] += float(
                    trait_impact_raw.get("density_preference_guided_total", 0.0)
                )
                avg_trait_impact_acc["density_preference_seek_total"] += float(
                    trait_impact_raw.get("density_preference_seek_total", 0.0)
                )
                avg_trait_impact_acc["density_preference_avoid_total"] += float(
                    trait_impact_raw.get("density_preference_avoid_total", 0.0)
                )
                avg_trait_impact_acc["density_preference_seek_usage_per_tick"] += float(
                    trait_impact_raw.get("density_preference_seek_usage_per_tick", 0.0)
                )
                avg_trait_impact_acc["density_preference_avoid_usage_per_tick"] += float(
                    trait_impact_raw.get("density_preference_avoid_usage_per_tick", 0.0)
                )
                avg_trait_impact_acc["density_preference_seek_share"] += float(
                    trait_impact_raw.get("density_preference_seek_share", 0.0)
                )
                avg_trait_impact_acc["density_preference_avoid_share"] += float(
                    trait_impact_raw.get("density_preference_avoid_share", 0.0)
                )
                avg_trait_impact_acc["density_preference_seek_users_avg"] += float(
                    trait_impact_raw.get("density_preference_seek_users_avg", 0.0)
                )
                avg_trait_impact_acc["density_preference_seek_usage_bias"] += float(
                    trait_impact_raw.get("density_preference_seek_usage_bias", 0.0)
                )
                avg_trait_impact_acc["density_preference_avoid_users_avg"] += float(
                    trait_impact_raw.get("density_preference_avoid_users_avg", 0.0)
                )
                avg_trait_impact_acc["density_preference_avoid_usage_bias"] += float(
                    trait_impact_raw.get("density_preference_avoid_usage_bias", 0.0)
                )
                avg_trait_impact_acc["density_preference_neighbor_count_avg"] += float(
                    trait_impact_raw.get("density_preference_neighbor_count_avg", 0.0)
                )
                avg_trait_impact_acc["density_preference_center_distance_delta"] += float(
                    trait_impact_raw.get("density_preference_center_distance_delta", 0.0)
                )
                avg_trait_impact_acc["persistence_holds_total"] += float(
                    trait_impact_raw.get("persistence_holds_total", 0.0)
                )
                avg_trait_impact_acc["behavior_persistence_oscillation_switch_rate"] += float(
                    trait_impact_raw.get("behavior_persistence_oscillation_switch_rate", 0.0)
                )
                avg_trait_impact_acc["behavior_persistence_oscillation_prevented_rate"] += float(
                    trait_impact_raw.get("behavior_persistence_oscillation_prevented_rate", 0.0)
                )
                avg_trait_impact_acc["search_wander_switches_total"] += float(
                    trait_impact_raw.get("search_wander_switches_total", 0.0)
                )
                avg_trait_impact_acc["search_wander_switches_prevented_total"] += float(
                    trait_impact_raw.get("search_wander_switches_prevented_total", 0.0)
                )
                avg_trait_impact_acc["search_wander_oscillation_events_total"] += float(
                    trait_impact_raw.get("search_wander_oscillation_events_total", 0.0)
                )
                avg_trait_impact_acc["borderline_threat_encounters"] += float(
                    trait_impact_raw.get("borderline_threat_encounters", 0.0)
                )
                avg_trait_impact_acc["borderline_threat_flees"] += float(
                    trait_impact_raw.get("borderline_threat_flees", 0.0)
                )
                avg_trait_impact_acc["borderline_threat_flee_rate"] += float(
                    trait_impact_raw.get("borderline_threat_flee_rate", 0.0)
                )
                avg_trait_impact_acc["risk_taking_borderline_encounter_mean"] += float(
                    trait_impact_raw.get("risk_taking_borderline_encounter_mean", 0.0)
                )
                avg_trait_impact_acc["risk_taking_borderline_flee_mean"] += float(
                    trait_impact_raw.get("risk_taking_borderline_flee_mean", 0.0)
                )
                avg_trait_impact_acc["risk_taking_borderline_flee_bias"] += float(
                    trait_impact_raw.get("risk_taking_borderline_flee_bias", 0.0)
                )

    if dominant_frequency:
        dominant_signature, dominant_count = sorted(
            dominant_frequency.items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
    else:
        dominant_signature, dominant_count = "-", 0

    return {
        "runs": run_count,
        "seeds": seeds,
        "extinction_count": extinction_count,
        "extinction_rate": extinction_count / run_count,
        "avg_max_generation": max_generation_sum / run_count,
        "avg_final_population": final_population_sum / run_count,
        "avg_final_traits": {
            "speed": avg_traits_acc["speed"] / run_count,
            "metabolism": avg_traits_acc["metabolism"] / run_count,
            "prudence": avg_traits_acc["prudence"] / run_count,
            "dominance": avg_traits_acc["dominance"] / run_count,
            "repro_drive": avg_traits_acc["repro_drive"] / run_count,
            "food_perception": avg_traits_acc["food_perception"] / run_count,
            "threat_perception": avg_traits_acc["threat_perception"] / run_count,
            "risk_taking": avg_traits_acc["risk_taking"] / run_count,
            "behavior_persistence": avg_traits_acc["behavior_persistence"] / run_count,
            "exploration_bias": avg_traits_acc["exploration_bias"] / run_count,
            "density_preference": avg_traits_acc["density_preference"] / run_count,
            "energy_efficiency": avg_traits_acc["energy_efficiency"] / run_count,
            "exhaustion_resistance": avg_traits_acc["exhaustion_resistance"] / run_count,
        },
        "avg_memory_impact": {
            "food_usage_total": avg_memory_acc["food_usage_total"] / run_count,
            "danger_usage_total": avg_memory_acc["danger_usage_total"] / run_count,
            "food_active_share": avg_memory_acc["food_active_share"] / run_count,
            "danger_active_share": avg_memory_acc["danger_active_share"] / run_count,
            "food_effect_avg_distance": avg_memory_acc["food_effect_avg_distance"] / run_count,
            "danger_effect_avg_distance": avg_memory_acc["danger_effect_avg_distance"] / run_count,
            "food_usage_per_tick": avg_memory_acc["food_usage_per_tick"] / run_count,
            "danger_usage_per_tick": avg_memory_acc["danger_usage_per_tick"] / run_count,
        },
        "avg_social_impact": {
            "follow_usage_total": avg_social_acc["follow_usage_total"] / run_count,
            "flee_boost_usage_total": avg_social_acc["flee_boost_usage_total"] / run_count,
            "influenced_count_last_tick": avg_social_acc["influenced_count_last_tick"] / run_count,
            "influenced_share_last_tick": avg_social_acc["influenced_share_last_tick"] / run_count,
            "influenced_per_tick": avg_social_acc["influenced_per_tick"] / run_count,
            "follow_usage_per_tick": avg_social_acc["follow_usage_per_tick"] / run_count,
            "flee_boost_usage_per_tick": avg_social_acc["flee_boost_usage_per_tick"] / run_count,
            "flee_multiplier_avg_tick": avg_social_acc["flee_multiplier_avg_tick"] / run_count,
            "flee_multiplier_avg_total": avg_social_acc["flee_multiplier_avg_total"] / run_count,
        },
        "avg_trait_impact": {
            "memory_focus_mean": avg_trait_impact_acc["memory_focus_mean"] / run_count,
            "memory_focus_std": avg_trait_impact_acc["memory_focus_std"] / run_count,
            "social_sensitivity_mean": avg_trait_impact_acc["social_sensitivity_mean"] / run_count,
            "social_sensitivity_std": avg_trait_impact_acc["social_sensitivity_std"] / run_count,
            "food_perception_mean": avg_trait_impact_acc["food_perception_mean"] / run_count,
            "food_perception_std": avg_trait_impact_acc["food_perception_std"] / run_count,
            "threat_perception_mean": avg_trait_impact_acc["threat_perception_mean"] / run_count,
            "threat_perception_std": avg_trait_impact_acc["threat_perception_std"] / run_count,
            "risk_taking_mean": avg_trait_impact_acc["risk_taking_mean"] / run_count,
            "risk_taking_std": avg_trait_impact_acc["risk_taking_std"] / run_count,
            "behavior_persistence_mean": avg_trait_impact_acc["behavior_persistence_mean"] / run_count,
            "behavior_persistence_std": avg_trait_impact_acc["behavior_persistence_std"] / run_count,
            "exploration_bias_mean": avg_trait_impact_acc["exploration_bias_mean"] / run_count,
            "exploration_bias_std": avg_trait_impact_acc["exploration_bias_std"] / run_count,
            "density_preference_mean": avg_trait_impact_acc["density_preference_mean"] / run_count,
            "density_preference_std": avg_trait_impact_acc["density_preference_std"] / run_count,
            "energy_efficiency_mean": avg_trait_impact_acc["energy_efficiency_mean"] / run_count,
            "energy_efficiency_std": avg_trait_impact_acc["energy_efficiency_std"] / run_count,
            "exhaustion_resistance_mean": avg_trait_impact_acc["exhaustion_resistance_mean"] / run_count,
            "exhaustion_resistance_std": avg_trait_impact_acc["exhaustion_resistance_std"] / run_count,
            "energy_efficiency_drain_bias": avg_trait_impact_acc["energy_efficiency_drain_bias"] / run_count,
            "exhaustion_resistance_reproduction_bias": (
                avg_trait_impact_acc["exhaustion_resistance_reproduction_bias"] / run_count
            ),
            "energy_drain_multiplier_observed": (
                avg_trait_impact_acc["energy_drain_multiplier_observed"] / run_count
            ),
            "reproduction_cost_multiplier_observed": (
                avg_trait_impact_acc["reproduction_cost_multiplier_observed"] / run_count
            ),
            "energy_drain_amount_observed": avg_trait_impact_acc["energy_drain_amount_observed"] / run_count,
            "reproduction_cost_amount_observed": (
                avg_trait_impact_acc["reproduction_cost_amount_observed"] / run_count
            ),
            "memory_focus_food_bias": avg_trait_impact_acc["memory_focus_food_bias"] / run_count,
            "memory_focus_danger_bias": avg_trait_impact_acc["memory_focus_danger_bias"] / run_count,
            "social_sensitivity_follow_bias": avg_trait_impact_acc["social_sensitivity_follow_bias"] / run_count,
            "social_sensitivity_flee_boost_bias": avg_trait_impact_acc["social_sensitivity_flee_boost_bias"] / run_count,
            "food_perception_detection_bias": avg_trait_impact_acc["food_perception_detection_bias"] / run_count,
            "food_perception_consumption_bias": avg_trait_impact_acc["food_perception_consumption_bias"] / run_count,
            "threat_perception_flee_bias": avg_trait_impact_acc["threat_perception_flee_bias"] / run_count,
            "risk_taking_flee_bias": avg_trait_impact_acc["risk_taking_flee_bias"] / run_count,
            "behavior_persistence_hold_bias": avg_trait_impact_acc["behavior_persistence_hold_bias"] / run_count,
            "exploration_bias_guided_bias": (
                avg_trait_impact_acc["exploration_bias_guided_bias"] / run_count
            ),
            "exploration_bias_guided_total": (
                avg_trait_impact_acc["exploration_bias_guided_total"] / run_count
            ),
            "exploration_bias_explore_share": (
                avg_trait_impact_acc["exploration_bias_explore_share"] / run_count
            ),
            "exploration_bias_explore_users_avg": (
                avg_trait_impact_acc["exploration_bias_explore_users_avg"] / run_count
            ),
            "exploration_bias_explore_usage_bias": (
                avg_trait_impact_acc["exploration_bias_explore_usage_bias"] / run_count
            ),
            "exploration_bias_settle_users_avg": (
                avg_trait_impact_acc["exploration_bias_settle_users_avg"] / run_count
            ),
            "exploration_bias_settle_usage_bias": (
                avg_trait_impact_acc["exploration_bias_settle_usage_bias"] / run_count
            ),
            "exploration_bias_anchor_distance_delta": (
                avg_trait_impact_acc["exploration_bias_anchor_distance_delta"] / run_count
            ),
            "density_preference_guided_bias": (
                avg_trait_impact_acc["density_preference_guided_bias"] / run_count
            ),
            "density_preference_guided_total": (
                avg_trait_impact_acc["density_preference_guided_total"] / run_count
            ),
            "density_preference_seek_total": (
                avg_trait_impact_acc["density_preference_seek_total"] / run_count
            ),
            "density_preference_avoid_total": (
                avg_trait_impact_acc["density_preference_avoid_total"] / run_count
            ),
            "density_preference_seek_usage_per_tick": (
                avg_trait_impact_acc["density_preference_seek_usage_per_tick"] / run_count
            ),
            "density_preference_avoid_usage_per_tick": (
                avg_trait_impact_acc["density_preference_avoid_usage_per_tick"] / run_count
            ),
            "density_preference_seek_share": (
                avg_trait_impact_acc["density_preference_seek_share"] / run_count
            ),
            "density_preference_avoid_share": (
                avg_trait_impact_acc["density_preference_avoid_share"] / run_count
            ),
            "density_preference_seek_users_avg": (
                avg_trait_impact_acc["density_preference_seek_users_avg"] / run_count
            ),
            "density_preference_seek_usage_bias": (
                avg_trait_impact_acc["density_preference_seek_usage_bias"] / run_count
            ),
            "density_preference_avoid_users_avg": (
                avg_trait_impact_acc["density_preference_avoid_users_avg"] / run_count
            ),
            "density_preference_avoid_usage_bias": (
                avg_trait_impact_acc["density_preference_avoid_usage_bias"] / run_count
            ),
            "density_preference_neighbor_count_avg": (
                avg_trait_impact_acc["density_preference_neighbor_count_avg"] / run_count
            ),
            "density_preference_center_distance_delta": (
                avg_trait_impact_acc["density_preference_center_distance_delta"] / run_count
            ),
            "persistence_holds_total": avg_trait_impact_acc["persistence_holds_total"] / run_count,
            "behavior_persistence_oscillation_switch_rate": (
                avg_trait_impact_acc["behavior_persistence_oscillation_switch_rate"] / run_count
            ),
            "behavior_persistence_oscillation_prevented_rate": (
                avg_trait_impact_acc["behavior_persistence_oscillation_prevented_rate"] / run_count
            ),
            "search_wander_switches_total": avg_trait_impact_acc["search_wander_switches_total"] / run_count,
            "search_wander_switches_prevented_total": (
                avg_trait_impact_acc["search_wander_switches_prevented_total"] / run_count
            ),
            "search_wander_oscillation_events_total": (
                avg_trait_impact_acc["search_wander_oscillation_events_total"] / run_count
            ),
            "borderline_threat_encounters": avg_trait_impact_acc["borderline_threat_encounters"] / run_count,
            "borderline_threat_flees": avg_trait_impact_acc["borderline_threat_flees"] / run_count,
            "borderline_threat_flee_rate": avg_trait_impact_acc["borderline_threat_flee_rate"] / run_count,
            "risk_taking_borderline_encounter_mean": (
                avg_trait_impact_acc["risk_taking_borderline_encounter_mean"] / run_count
            ),
            "risk_taking_borderline_flee_mean": (
                avg_trait_impact_acc["risk_taking_borderline_flee_mean"] / run_count
            ),
            "risk_taking_borderline_flee_bias": (
                avg_trait_impact_acc["risk_taking_borderline_flee_bias"] / run_count
            ),
        },
        "most_frequent_final_dominant_group": dominant_signature,
        "most_frequent_final_dominant_group_count": dominant_count,
        "most_frequent_final_dominant_group_share": dominant_count / run_count,
    }

def _build_proto_zone_observations(
    creatures: Iterable[Creature],
    world: object | None,
) -> tuple[Dict[str, int], Dict[str, Dict[str, object] | None]]:
    zone_distribution = _empty_zone_distribution()
    dominant_proto_by_zone = _empty_zone_dominants()

    if world is None:
        return zone_distribution, dominant_proto_by_zone

    get_zone = getattr(world, "get_fertility_zone", None)
    if not callable(get_zone):
        return zone_distribution, dominant_proto_by_zone

    grouped_by_zone: Dict[str, Dict[str, int]] = {zone: {} for zone in _ZONE_NAMES}

    for creature in creatures:
        zone_name = str(get_zone(creature.x, creature.y))
        if zone_name not in zone_distribution:
            continue

        zone_distribution[zone_name] += 1
        signature = _proto_signature(_proto_group_key(creature))

        bucket = grouped_by_zone[zone_name]
        bucket[signature] = bucket.get(signature, 0) + 1

    for zone_name in _ZONE_NAMES:
        zone_count = zone_distribution[zone_name]
        bucket = grouped_by_zone[zone_name]

        if zone_count <= 0 or not bucket:
            dominant_proto_by_zone[zone_name] = None
            continue

        signature, dominant_count = sorted(bucket.items(), key=lambda item: (-item[1], item[0]))[0]
        dominant_proto_by_zone[zone_name] = {
            "signature": signature,
            "count": dominant_count,
            "share": dominant_count / zone_count,
        }

    return zone_distribution, dominant_proto_by_zone


def _empty_zone_distribution() -> Dict[str, int]:
    return {zone: 0 for zone in _ZONE_NAMES}


def _empty_zone_dominants() -> Dict[str, Dict[str, object] | None]:
    return {zone: None for zone in _ZONE_NAMES}


def _build_proto_group_temporal_observations(
    current_top_groups: list[Dict[str, object]],
    previous_stats: Dict[str, object] | None,
    max_groups: int,
) -> tuple[list[Dict[str, object]], Dict[str, int]]:
    if max_groups <= 0:
        raise ValueError("max_groups must be > 0")

    previous_top_groups = _read_top_groups(previous_stats, max_groups)
    current_groups = _read_top_groups_from_list(current_top_groups, max_groups)

    previous_share_by_signature = {
        str(group["signature"]): float(group["share"]) for group in previous_top_groups
    }
    current_share_by_signature = {
        str(group["signature"]): float(group["share"]) for group in current_groups
    }

    trends: list[Dict[str, object]] = []
    for group in current_groups:
        signature = str(group["signature"])
        current_share = float(group["share"])
        previous_share = previous_share_by_signature.get(signature)

        if previous_share is None:
            status = "nouveau"
            delta_share = current_share
        else:
            delta_share = current_share - previous_share
            if abs(delta_share) <= _PROTO_TREND_STABLE_DELTA:
                status = "stable"
            elif delta_share > 0:
                status = "en_hausse"
            else:
                status = "en_baisse"

        trends.append(
            {
                "signature": signature,
                "status": status,
                "current_share": current_share,
                "previous_share": 0.0 if previous_share is None else previous_share,
                "delta_share": delta_share,
            }
        )

    for signature, previous_share in previous_share_by_signature.items():
        if signature in current_share_by_signature:
            continue
        trends.append(
            {
                "signature": signature,
                "status": "en_baisse",
                "current_share": 0.0,
                "previous_share": previous_share,
                "delta_share": -previous_share,
            }
        )

    summary = _empty_proto_temporal_summary()
    for trend in trends:
        status = str(trend["status"])
        if status in summary:
            summary[status] += 1

    return trends, summary


def _read_top_groups(
    stats: Dict[str, object] | None,
    max_groups: int,
) -> list[Dict[str, object]]:
    if stats is None:
        return []
    raw = stats.get("proto_groups_top")
    if not isinstance(raw, list):
        return []
    return _read_top_groups_from_list(raw, max_groups)


def _read_top_groups_from_list(
    groups: list[Dict[str, object]],
    max_groups: int,
) -> list[Dict[str, object]]:
    parsed: list[Dict[str, object]] = []
    for group in groups[:max_groups]:
        if not isinstance(group, dict):
            continue
        parsed.append(
            {
                "signature": str(group.get("signature", "?")),
                "share": float(group.get("share", 0.0)),
            }
        )
    return parsed


def _empty_proto_temporal_summary() -> Dict[str, int]:
    return {
        "stable": 0,
        "en_hausse": 0,
        "en_baisse": 0,
        "nouveau": 0,
    }


def _read_status_counts(temporal_tracker: Dict[str, object]) -> Dict[str, Dict[str, int]]:
    by_signature_raw = temporal_tracker.get("by_signature")
    if not isinstance(by_signature_raw, dict):
        return {}

    parsed: Dict[str, Dict[str, int]] = {}
    for signature, counts_raw in by_signature_raw.items():
        if not isinstance(counts_raw, dict):
            continue
        parsed[str(signature)] = {
            "stable": int(counts_raw.get("stable", 0)),
            "en_hausse": int(counts_raw.get("en_hausse", 0)),
            "en_baisse": int(counts_raw.get("en_baisse", 0)),
            "nouveau": int(counts_raw.get("nouveau", 0)),
        }
    return parsed


def _pick_signature_by_status(
    by_signature: Dict[str, Dict[str, int]],
    status_name: str,
) -> tuple[str, int]:
    if status_name not in _PROTO_TEMPORAL_STATUSES:
        return "-", 0

    candidates: list[tuple[int, int, str]] = []
    for signature, counts in by_signature.items():
        primary = int(counts.get(status_name, 0))
        if primary <= 0:
            continue

        secondary_name = "en_hausse" if status_name == "stable" else "stable"
        secondary = int(counts.get(secondary_name, 0))
        candidates.append((primary, secondary, signature))

    if not candidates:
        return "-", 0

    best = sorted(candidates, key=lambda item: (-item[0], -item[1], item[2]))[0]
    return best[2], best[0]


def _normalize_zone_distribution(raw: object) -> Dict[str, int]:
    result = {
        "rich": 0,
        "neutral": 0,
        "poor": 0,
    }
    if not isinstance(raw, dict):
        return result

    result["rich"] = int(raw.get("rich", 0))
    result["neutral"] = int(raw.get("neutral", 0))
    result["poor"] = int(raw.get("poor", 0))
    return result


def _read_avg_traits(final_stats: Dict[str, object]) -> Dict[str, float]:
    return {
        "speed": float(final_stats.get("avg_speed", 0.0)),
        "metabolism": float(final_stats.get("avg_metabolism", 0.0)),
        "prudence": float(final_stats.get("avg_prudence", 0.0)),
        "dominance": float(final_stats.get("avg_dominance", 0.0)),
        "repro_drive": float(final_stats.get("avg_repro_drive", 0.0)),
        "food_perception": float(final_stats.get("avg_food_perception", 0.0)),
        "threat_perception": float(final_stats.get("avg_threat_perception", 0.0)),
        "risk_taking": float(final_stats.get("avg_risk_taking", 0.0)),
        "behavior_persistence": float(final_stats.get("avg_behavior_persistence", 0.0)),
        "exploration_bias": float(final_stats.get("avg_exploration_bias", 0.0)),
        "density_preference": float(final_stats.get("avg_density_preference", 0.0)),
        "energy_efficiency": float(final_stats.get("avg_energy_efficiency", 0.0)),
        "exhaustion_resistance": float(final_stats.get("avg_exhaustion_resistance", 0.0)),
    }


def _build_proto_groups(
    creatures: Iterable[Creature],
    max_groups: int,
) -> tuple[int, list[Dict[str, object]], float]:
    grouped: Dict[tuple[int, int, int, int, int], Dict[str, float | int]] = {}

    for creature in creatures:
        key = _proto_group_key(creature)
        if key not in grouped:
            grouped[key] = {
                "size": 0,
                "sum_speed": 0.0,
                "sum_metabolism": 0.0,
                "sum_prudence": 0.0,
                "sum_dominance": 0.0,
                "sum_repro_drive": 0.0,
            }

        bucket = grouped[key]
        bucket["size"] = int(bucket["size"]) + 1
        bucket["sum_speed"] = float(bucket["sum_speed"]) + creature.traits.speed
        bucket["sum_metabolism"] = float(bucket["sum_metabolism"]) + creature.traits.metabolism
        bucket["sum_prudence"] = float(bucket["sum_prudence"]) + creature.traits.prudence
        bucket["sum_dominance"] = float(bucket["sum_dominance"]) + creature.traits.dominance
        bucket["sum_repro_drive"] = float(bucket["sum_repro_drive"]) + creature.traits.repro_drive

    group_count = len(grouped)
    if group_count == 0:
        return 0, [], 0.0

    total = sum(int(bucket["size"]) for bucket in grouped.values())
    ordered_keys = sorted(grouped.keys(), key=lambda key: (-int(grouped[key]["size"]), key))

    top_groups: list[Dict[str, object]] = []
    for key in ordered_keys[:max_groups]:
        bucket = grouped[key]
        size = int(bucket["size"])
        top_groups.append(
            {
                "signature": _proto_signature(key),
                "size": size,
                "share": size / total,
                "avg_speed": float(bucket["sum_speed"]) / size,
                "avg_metabolism": float(bucket["sum_metabolism"]) / size,
                "avg_prudence": float(bucket["sum_prudence"]) / size,
                "avg_dominance": float(bucket["sum_dominance"]) / size,
                "avg_repro_drive": float(bucket["sum_repro_drive"]) / size,
            }
        )

    dominant_share = float(top_groups[0]["share"]) if top_groups else 0.0
    return group_count, top_groups, dominant_share


def _proto_group_key(creature: Creature) -> tuple[int, int, int, int, int]:
    return (
        _quantize(creature.traits.speed, _PROTO_GROUP_WIDTH_SPEED),
        _quantize(creature.traits.metabolism, _PROTO_GROUP_WIDTH_METABOLISM),
        _quantize(creature.traits.prudence, _PROTO_GROUP_WIDTH_BEHAVIOR),
        _quantize(creature.traits.dominance, _PROTO_GROUP_WIDTH_BEHAVIOR),
        _quantize(creature.traits.repro_drive, _PROTO_GROUP_WIDTH_BEHAVIOR),
    )


def _quantize(value: float, width: float) -> int:
    return int(round(value / width))


def _proto_signature(key: tuple[int, int, int, int, int]) -> str:
    return f"s{key[0]}m{key[1]}p{key[2]}d{key[3]}r{key[4]}"


def _stddev_from_mean(values: Iterable[float], mean: float) -> float:
    values_list = list(values)
    if len(values_list) <= 1:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values_list) / len(values_list)
    return sqrt(variance)


