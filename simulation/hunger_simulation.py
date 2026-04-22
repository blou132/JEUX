from __future__ import annotations

import random
from math import cos, hypot, pi, sin
from typing import Callable, Dict, Iterable, Set

from ai import CreatureIntent, HungerAI
from creatures import Creature
from genetics import inherit_traits
from world import FoodField, SimpleMap


class HungerSimulation:
    DEATH_CAUSE_STARVATION = "starvation"
    DEATH_CAUSE_EXHAUSTION = "exhaustion"
    DEATH_CAUSE_UNKNOWN = "unknown"
    AGE_WEAR_START = 22.0
    AGE_WEAR_RATE = 0.012
    AGE_WEAR_MAX_EXTRA_MULTIPLIER = 0.35

    def __init__(
        self,
        creatures: Iterable[Creature],
        food_field: FoodField,
        ai_system: HungerAI,
        energy_drain_rate: float = 1.0,
        movement_speed: float = 1.0,
        eat_rate: float = 20.0,
        reproduction_energy_threshold: float = 70.0,
        reproduction_cost: float = 20.0,
        reproduction_distance: float = 1.5,
        reproduction_min_age: float = 0.0,
        mutation_variation: float = 0.1,
        random_source: random.Random | None = None,
        world_map: SimpleMap | None = None,
        food_memory_duration: float = 8.0,
        danger_memory_duration: float = 6.0,
        food_memory_recall_distance: float = 8.0,
        danger_memory_avoid_distance: float = 5.0,
        social_influence_distance: float = 6.0,
        social_follow_strength: float = 0.35,
        social_flee_boost_per_neighbor: float = 0.15,
        social_flee_boost_max: float = 0.45,
        fertility_zone_getter: Callable[[float, float], str] | None = None,
    ) -> None:
        if (
            energy_drain_rate < 0
            or movement_speed < 0
            or eat_rate < 0
            or reproduction_energy_threshold < 0
            or reproduction_cost < 0
            or reproduction_distance < 0
            or reproduction_min_age < 0
            or mutation_variation < 0
            or food_memory_duration < 0
            or danger_memory_duration < 0
            or food_memory_recall_distance < 0
            or danger_memory_avoid_distance < 0
            or social_influence_distance < 0
            or social_follow_strength < 0
            or social_flee_boost_per_neighbor < 0
            or social_flee_boost_max < 0
        ):
            raise ValueError("rates must be >= 0")

        self.creatures = list(creatures)
        self.food_field = food_field
        self.ai_system = ai_system
        self.energy_drain_rate = energy_drain_rate
        self.movement_speed = movement_speed
        self.eat_rate = eat_rate
        self.reproduction_energy_threshold = reproduction_energy_threshold
        self.reproduction_cost = reproduction_cost
        self.reproduction_distance = reproduction_distance
        self.reproduction_min_age = reproduction_min_age
        self.mutation_variation = mutation_variation
        self.random_source = random_source or random.Random()
        self.world_map = world_map

        self.food_memory_duration = food_memory_duration
        self.danger_memory_duration = danger_memory_duration
        self.food_memory_recall_distance = food_memory_recall_distance
        self.danger_memory_avoid_distance = danger_memory_avoid_distance
        self.social_influence_distance = social_influence_distance
        self.social_follow_strength = social_follow_strength
        self.social_flee_boost_per_neighbor = social_flee_boost_per_neighbor
        self.social_flee_boost_max = social_flee_boost_max
        self.fertility_zone_getter = fertility_zone_getter

        self.last_intents: Dict[str, CreatureIntent] = {}
        self._child_counter = 0

        self.births_last_tick = 0
        self.total_births = 0
        self.deaths_last_tick = 0
        self.total_deaths = 0
        self.flees_last_tick = 0
        self.total_flees = 0
        self.fleeing_creatures_last_tick: list[str] = []
        self.flee_threat_distance_last_tick: Dict[str, float] = {}
        self.avg_flee_threat_distance_last_tick = 0.0
        self.food_detection_moves_last_tick = 0
        self.total_food_detection_moves = 0
        self.food_perception_sum_detection_last_tick = 0.0
        self.total_food_perception_sum_detection = 0.0
        self.food_consumptions_last_tick = 0
        self.total_food_consumptions = 0
        self.food_perception_sum_consumption_last_tick = 0.0
        self.total_food_perception_sum_consumption = 0.0
        self.threat_detection_flee_last_tick = 0
        self.total_threat_detection_flee = 0
        self.threat_perception_sum_flee_last_tick = 0.0
        self.total_threat_perception_sum_flee = 0.0
        self.risk_taking_sum_flee_last_tick = 0.0
        self.total_risk_taking_sum_flee = 0.0
        self.borderline_threat_encounters_last_tick = 0
        self.total_borderline_threat_encounters = 0
        self.borderline_threat_flees_last_tick = 0
        self.total_borderline_threat_flees = 0
        self.risk_taking_sum_borderline_encounters_last_tick = 0.0
        self.total_risk_taking_sum_borderline_encounters = 0.0
        self.risk_taking_sum_borderline_flees_last_tick = 0.0
        self.total_risk_taking_sum_borderline_flees = 0.0
        self.stress_pressure_events_last_tick = 0
        self.total_stress_pressure_events = 0
        self.stress_pressure_flee_events_last_tick = 0
        self.total_stress_pressure_flee_events = 0
        self.stress_tolerance_sum_pressure_last_tick = 0.0
        self.total_stress_tolerance_sum_pressure = 0.0
        self.stress_tolerance_sum_pressure_flee_last_tick = 0.0
        self.total_stress_tolerance_sum_pressure_flee = 0.0
        self.persistence_holds_last_tick = 0
        self.total_persistence_holds = 0
        self.behavior_persistence_sum_holds_last_tick = 0.0
        self.total_behavior_persistence_sum_holds = 0.0
        self.persistence_holding_creatures_last_tick: list[str] = []
        self.search_wander_switches_last_tick = 0
        self.total_search_wander_switches = 0
        self.search_wander_switches_prevented_last_tick = 0
        self.total_search_wander_switches_prevented = 0
        self.search_wander_oscillation_events_last_tick = 0
        self.total_search_wander_oscillation_events = 0
        self.exploration_bias_guided_moves_last_tick = 0
        self.total_exploration_bias_guided_moves = 0
        self.exploration_bias_sum_guided_last_tick = 0.0
        self.total_exploration_bias_sum_guided = 0.0
        self.exploration_bias_explore_moves_last_tick = 0
        self.total_exploration_bias_explore_moves = 0
        self.exploration_bias_sum_explore_last_tick = 0.0
        self.total_exploration_bias_sum_explore = 0.0
        self.exploration_bias_settle_moves_last_tick = 0
        self.total_exploration_bias_settle_moves = 0
        self.exploration_bias_sum_settle_last_tick = 0.0
        self.total_exploration_bias_sum_settle = 0.0
        self.exploration_bias_anchor_distance_delta_last_tick = 0.0
        self.total_exploration_bias_anchor_distance_delta = 0.0
        self.avg_exploration_bias_anchor_distance_delta_last_tick = 0.0
        self.density_preference_guided_moves_last_tick = 0
        self.total_density_preference_guided_moves = 0
        self.density_preference_sum_guided_last_tick = 0.0
        self.total_density_preference_sum_guided = 0.0
        self.density_preference_seek_moves_last_tick = 0
        self.total_density_preference_seek_moves = 0
        self.density_preference_sum_seek_last_tick = 0.0
        self.total_density_preference_sum_seek = 0.0
        self.density_preference_avoid_moves_last_tick = 0
        self.total_density_preference_avoid_moves = 0
        self.density_preference_sum_avoid_last_tick = 0.0
        self.total_density_preference_sum_avoid = 0.0
        self.density_preference_neighbor_count_sum_last_tick = 0.0
        self.total_density_preference_neighbor_count_sum = 0.0
        self.density_preference_center_distance_delta_last_tick = 0.0
        self.total_density_preference_center_distance_delta = 0.0
        self.avg_density_preference_center_distance_delta_last_tick = 0.0
        self.gregariousness_guided_moves_last_tick = 0
        self.total_gregariousness_guided_moves = 0
        self.gregariousness_sum_guided_last_tick = 0.0
        self.total_gregariousness_sum_guided = 0.0
        self.gregariousness_seek_moves_last_tick = 0
        self.total_gregariousness_seek_moves = 0
        self.gregariousness_sum_seek_last_tick = 0.0
        self.total_gregariousness_sum_seek = 0.0
        self.gregariousness_avoid_moves_last_tick = 0
        self.total_gregariousness_avoid_moves = 0
        self.gregariousness_sum_avoid_last_tick = 0.0
        self.total_gregariousness_sum_avoid = 0.0
        self.gregariousness_neighbor_count_sum_last_tick = 0.0
        self.total_gregariousness_neighbor_count_sum = 0.0
        self.gregariousness_center_distance_delta_last_tick = 0.0
        self.total_gregariousness_center_distance_delta = 0.0
        self.avg_gregariousness_center_distance_delta_last_tick = 0.0
        self.competition_tolerance_guided_moves_last_tick = 0
        self.total_competition_tolerance_guided_moves = 0
        self.competition_tolerance_sum_guided_last_tick = 0.0
        self.total_competition_tolerance_sum_guided = 0.0
        self.competition_tolerance_stay_moves_last_tick = 0
        self.total_competition_tolerance_stay_moves = 0
        self.competition_tolerance_sum_stay_last_tick = 0.0
        self.total_competition_tolerance_sum_stay = 0.0
        self.competition_tolerance_avoid_moves_last_tick = 0
        self.total_competition_tolerance_avoid_moves = 0
        self.competition_tolerance_sum_avoid_last_tick = 0.0
        self.total_competition_tolerance_sum_avoid = 0.0
        self.competition_tolerance_neighbor_count_sum_last_tick = 0.0
        self.total_competition_tolerance_neighbor_count_sum = 0.0
        self.competition_tolerance_anchor_distance_delta_last_tick = 0.0
        self.total_competition_tolerance_anchor_distance_delta = 0.0
        self.avg_competition_tolerance_anchor_distance_delta_last_tick = 0.0
        self.resource_commitment_guided_moves_last_tick = 0
        self.total_resource_commitment_guided_moves = 0
        self.resource_commitment_sum_guided_last_tick = 0.0
        self.total_resource_commitment_sum_guided = 0.0
        self.resource_commitment_stay_moves_last_tick = 0
        self.total_resource_commitment_stay_moves = 0
        self.resource_commitment_sum_stay_last_tick = 0.0
        self.total_resource_commitment_sum_stay = 0.0
        self.resource_commitment_switch_moves_last_tick = 0
        self.total_resource_commitment_switch_moves = 0
        self.resource_commitment_sum_switch_last_tick = 0.0
        self.total_resource_commitment_sum_switch = 0.0
        self.resource_commitment_anchor_distance_delta_last_tick = 0.0
        self.total_resource_commitment_anchor_distance_delta = 0.0
        self.avg_resource_commitment_anchor_distance_delta_last_tick = 0.0
        self.resource_commitment_sum_food_memory_last_tick = 0.0
        self.total_resource_commitment_sum_food_memory = 0.0
        self.resource_commitment_recall_multiplier_sum_last_tick = 0.0
        self.total_resource_commitment_recall_multiplier_sum = 0.0
        self.movement_actions_last_tick = 0
        self.total_movement_actions = 0
        self.mobility_efficiency_sum_movement_last_tick = 0.0
        self.total_mobility_efficiency_sum_movement = 0.0
        self.movement_multiplier_sum_last_tick = 0.0
        self.total_movement_multiplier_sum = 0.0
        self.movement_distance_sum_last_tick = 0.0
        self.total_movement_distance_sum = 0.0
        self.avg_movement_multiplier_last_tick = 1.0
        self.avg_movement_distance_last_tick = 0.0

        self.food_memory_guided_moves_last_tick = 0
        self.total_food_memory_guided_moves = 0
        self.danger_memory_avoid_moves_last_tick = 0
        self.total_danger_memory_avoid_moves = 0
        self.memory_focus_sum_food_memory_last_tick = 0.0
        self.total_memory_focus_sum_food_memory = 0.0
        self.memory_focus_sum_danger_memory_last_tick = 0.0
        self.total_memory_focus_sum_danger_memory = 0.0
        self.food_memory_distance_gain_last_tick = 0.0
        self.total_food_memory_distance_gain = 0.0
        self.avg_food_memory_distance_gain_last_tick = 0.0
        self.danger_memory_distance_gain_last_tick = 0.0
        self.total_danger_memory_distance_gain = 0.0
        self.avg_danger_memory_distance_gain_last_tick = 0.0
        self.tick_count = 0
        self.social_follow_moves_last_tick = 0
        self.total_social_follow_moves = 0
        self.social_flee_boosted_last_tick = 0
        self.total_social_flee_boosted = 0
        self.social_flee_multiplier_sum_last_tick = 0.0
        self.avg_social_flee_multiplier_last_tick = 1.0
        self.social_influenced_creatures_last_tick = 0
        self.total_social_influenced_creatures = 0
        self.total_social_flee_multiplier_sum = 0.0
        self.social_sensitivity_sum_follow_last_tick = 0.0
        self.total_social_sensitivity_sum_follow = 0.0
        self.social_sensitivity_sum_flee_boost_last_tick = 0.0
        self.total_social_sensitivity_sum_flee_boost = 0.0

        self.energy_drain_events_last_tick = 0
        self.total_energy_drain_events = 0
        self.energy_drain_amount_last_tick = 0.0
        self.total_energy_drain_amount = 0.0
        self.energy_drain_multiplier_sum_last_tick = 0.0
        self.total_energy_drain_multiplier_sum = 0.0
        self.energy_efficiency_sum_drain_last_tick = 0.0
        self.total_energy_efficiency_sum_drain = 0.0
        self.poor_zone_drain_events_last_tick = 0
        self.total_poor_zone_drain_events = 0
        self.rich_zone_drain_events_last_tick = 0
        self.total_rich_zone_drain_events = 0
        self.environmental_tolerance_sum_poor_drain_last_tick = 0.0
        self.total_environmental_tolerance_sum_poor_drain = 0.0
        self.environmental_tolerance_sum_rich_drain_last_tick = 0.0
        self.total_environmental_tolerance_sum_rich_drain = 0.0
        self.zone_drain_multiplier_sum_last_tick = 0.0
        self.total_zone_drain_multiplier_sum = 0.0
        self.age_wear_active_events_last_tick = 0
        self.total_age_wear_active_events = 0
        self.age_wear_multiplier_sum_last_tick = 0.0
        self.total_age_wear_multiplier_sum = 0.0
        self.longevity_factor_sum_age_wear_last_tick = 0.0
        self.total_longevity_factor_sum_age_wear = 0.0
        self.reproduction_cost_events_last_tick = 0
        self.total_reproduction_cost_events = 0
        self.reproduction_cost_amount_last_tick = 0.0
        self.total_reproduction_cost_amount = 0.0
        self.reproduction_cost_multiplier_sum_last_tick = 0.0
        self.total_reproduction_cost_multiplier_sum = 0.0
        self.exhaustion_resistance_sum_reproduction_last_tick = 0.0
        self.total_exhaustion_resistance_sum_reproduction = 0.0
        self.reproduction_timing_sum_reproduction_last_tick = 0.0
        self.total_reproduction_timing_sum_reproduction = 0.0
        self.reproduction_timing_threshold_multiplier_sum_reproduction_last_tick = 0.0
        self.total_reproduction_timing_threshold_multiplier_sum_reproduction = 0.0
        self.hunger_search_actions_last_tick = 0
        self.total_hunger_search_actions = 0
        self.hunger_sensitivity_sum_search_last_tick = 0.0
        self.total_hunger_sensitivity_sum_search = 0.0

        self.death_causes_last_tick: Dict[str, int] = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }
        self.total_death_causes: Dict[str, int] = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }

    def tick(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")

        self.births_last_tick = 0
        self.deaths_last_tick = 0
        self.flees_last_tick = 0
        self.fleeing_creatures_last_tick = []
        self.flee_threat_distance_last_tick = {}
        self.avg_flee_threat_distance_last_tick = 0.0
        self.food_detection_moves_last_tick = 0
        self.food_perception_sum_detection_last_tick = 0.0
        self.food_consumptions_last_tick = 0
        self.food_perception_sum_consumption_last_tick = 0.0
        self.threat_detection_flee_last_tick = 0
        self.threat_perception_sum_flee_last_tick = 0.0
        self.risk_taking_sum_flee_last_tick = 0.0
        self.borderline_threat_encounters_last_tick = 0
        self.borderline_threat_flees_last_tick = 0
        self.risk_taking_sum_borderline_encounters_last_tick = 0.0
        self.risk_taking_sum_borderline_flees_last_tick = 0.0
        self.stress_pressure_events_last_tick = 0
        self.stress_pressure_flee_events_last_tick = 0
        self.stress_tolerance_sum_pressure_last_tick = 0.0
        self.stress_tolerance_sum_pressure_flee_last_tick = 0.0
        self.persistence_holds_last_tick = 0
        self.behavior_persistence_sum_holds_last_tick = 0.0
        self.persistence_holding_creatures_last_tick = []
        self.search_wander_switches_last_tick = 0
        self.search_wander_switches_prevented_last_tick = 0
        self.search_wander_oscillation_events_last_tick = 0
        self.exploration_bias_guided_moves_last_tick = 0
        self.exploration_bias_sum_guided_last_tick = 0.0
        self.exploration_bias_explore_moves_last_tick = 0
        self.exploration_bias_sum_explore_last_tick = 0.0
        self.exploration_bias_settle_moves_last_tick = 0
        self.exploration_bias_sum_settle_last_tick = 0.0
        self.exploration_bias_anchor_distance_delta_last_tick = 0.0
        self.avg_exploration_bias_anchor_distance_delta_last_tick = 0.0
        self.density_preference_guided_moves_last_tick = 0
        self.density_preference_sum_guided_last_tick = 0.0
        self.density_preference_seek_moves_last_tick = 0
        self.density_preference_sum_seek_last_tick = 0.0
        self.density_preference_avoid_moves_last_tick = 0
        self.density_preference_sum_avoid_last_tick = 0.0
        self.density_preference_neighbor_count_sum_last_tick = 0.0
        self.density_preference_center_distance_delta_last_tick = 0.0
        self.avg_density_preference_center_distance_delta_last_tick = 0.0
        self.gregariousness_guided_moves_last_tick = 0
        self.gregariousness_sum_guided_last_tick = 0.0
        self.gregariousness_seek_moves_last_tick = 0
        self.gregariousness_sum_seek_last_tick = 0.0
        self.gregariousness_avoid_moves_last_tick = 0
        self.gregariousness_sum_avoid_last_tick = 0.0
        self.gregariousness_neighbor_count_sum_last_tick = 0.0
        self.gregariousness_center_distance_delta_last_tick = 0.0
        self.avg_gregariousness_center_distance_delta_last_tick = 0.0
        self.competition_tolerance_guided_moves_last_tick = 0
        self.competition_tolerance_sum_guided_last_tick = 0.0
        self.competition_tolerance_stay_moves_last_tick = 0
        self.competition_tolerance_sum_stay_last_tick = 0.0
        self.competition_tolerance_avoid_moves_last_tick = 0
        self.competition_tolerance_sum_avoid_last_tick = 0.0
        self.competition_tolerance_neighbor_count_sum_last_tick = 0.0
        self.competition_tolerance_anchor_distance_delta_last_tick = 0.0
        self.avg_competition_tolerance_anchor_distance_delta_last_tick = 0.0
        self.resource_commitment_guided_moves_last_tick = 0
        self.resource_commitment_sum_guided_last_tick = 0.0
        self.resource_commitment_stay_moves_last_tick = 0
        self.resource_commitment_sum_stay_last_tick = 0.0
        self.resource_commitment_switch_moves_last_tick = 0
        self.resource_commitment_sum_switch_last_tick = 0.0
        self.resource_commitment_anchor_distance_delta_last_tick = 0.0
        self.avg_resource_commitment_anchor_distance_delta_last_tick = 0.0
        self.resource_commitment_sum_food_memory_last_tick = 0.0
        self.resource_commitment_recall_multiplier_sum_last_tick = 0.0
        self.movement_actions_last_tick = 0
        self.mobility_efficiency_sum_movement_last_tick = 0.0
        self.movement_multiplier_sum_last_tick = 0.0
        self.movement_distance_sum_last_tick = 0.0
        self.avg_movement_multiplier_last_tick = 1.0
        self.avg_movement_distance_last_tick = 0.0
        self.food_memory_guided_moves_last_tick = 0
        self.danger_memory_avoid_moves_last_tick = 0
        self.memory_focus_sum_food_memory_last_tick = 0.0
        self.memory_focus_sum_danger_memory_last_tick = 0.0
        self.food_memory_distance_gain_last_tick = 0.0
        self.avg_food_memory_distance_gain_last_tick = 0.0
        self.danger_memory_distance_gain_last_tick = 0.0
        self.avg_danger_memory_distance_gain_last_tick = 0.0
        self.social_follow_moves_last_tick = 0
        self.social_sensitivity_sum_follow_last_tick = 0.0
        self.social_flee_boosted_last_tick = 0
        self.social_sensitivity_sum_flee_boost_last_tick = 0.0
        self.social_flee_multiplier_sum_last_tick = 0.0
        self.avg_social_flee_multiplier_last_tick = 1.0
        self.social_influenced_creatures_last_tick = 0
        self.energy_drain_events_last_tick = 0
        self.energy_drain_amount_last_tick = 0.0
        self.energy_drain_multiplier_sum_last_tick = 0.0
        self.energy_efficiency_sum_drain_last_tick = 0.0
        self.poor_zone_drain_events_last_tick = 0
        self.rich_zone_drain_events_last_tick = 0
        self.environmental_tolerance_sum_poor_drain_last_tick = 0.0
        self.environmental_tolerance_sum_rich_drain_last_tick = 0.0
        self.zone_drain_multiplier_sum_last_tick = 0.0
        self.age_wear_active_events_last_tick = 0
        self.age_wear_multiplier_sum_last_tick = 0.0
        self.longevity_factor_sum_age_wear_last_tick = 0.0
        self.reproduction_cost_events_last_tick = 0
        self.reproduction_cost_amount_last_tick = 0.0
        self.reproduction_cost_multiplier_sum_last_tick = 0.0
        self.exhaustion_resistance_sum_reproduction_last_tick = 0.0
        self.reproduction_timing_sum_reproduction_last_tick = 0.0
        self.reproduction_timing_threshold_multiplier_sum_reproduction_last_tick = 0.0
        self.hunger_search_actions_last_tick = 0
        self.hunger_sensitivity_sum_search_last_tick = 0.0
        self.death_causes_last_tick = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }

        dead_before = self.get_dead_count()
        alive_before_ids = {creature.creature_id for creature in self.creatures if creature.alive}

        # 1) Passive aging, memory decay and energy loss.
        for creature in self.creatures:
            creature.grow_older(dt)
            creature.decay_memory(dt)
            zone_drain_multiplier = 1.0
            if creature.alive:
                drain_multiplier = self._compute_energy_efficiency_drain_multiplier(creature)
                age_wear_multiplier = self._compute_age_wear_multiplier(creature)
                zone_drain_multiplier, zone_name = self._compute_environmental_zone_multiplier(
                    creature
                )
                effective_drain = (
                    self.energy_drain_rate
                    * creature.traits.metabolism
                    * drain_multiplier
                    * age_wear_multiplier
                    * zone_drain_multiplier
                )
                self.energy_drain_events_last_tick += 1
                self.total_energy_drain_events += 1
                self.energy_drain_amount_last_tick += effective_drain * dt
                self.total_energy_drain_amount += effective_drain * dt
                self.energy_drain_multiplier_sum_last_tick += (
                    drain_multiplier * age_wear_multiplier * zone_drain_multiplier
                )
                self.total_energy_drain_multiplier_sum += (
                    drain_multiplier * age_wear_multiplier * zone_drain_multiplier
                )
                self.energy_efficiency_sum_drain_last_tick += creature.traits.energy_efficiency
                self.total_energy_efficiency_sum_drain += creature.traits.energy_efficiency
                self.zone_drain_multiplier_sum_last_tick += zone_drain_multiplier
                self.total_zone_drain_multiplier_sum += zone_drain_multiplier
                if zone_name == "poor":
                    self.poor_zone_drain_events_last_tick += 1
                    self.total_poor_zone_drain_events += 1
                    self.environmental_tolerance_sum_poor_drain_last_tick += (
                        creature.traits.environmental_tolerance
                    )
                    self.total_environmental_tolerance_sum_poor_drain += (
                        creature.traits.environmental_tolerance
                    )
                elif zone_name == "rich":
                    self.rich_zone_drain_events_last_tick += 1
                    self.total_rich_zone_drain_events += 1
                    self.environmental_tolerance_sum_rich_drain_last_tick += (
                        creature.traits.environmental_tolerance
                    )
                    self.total_environmental_tolerance_sum_rich_drain += (
                        creature.traits.environmental_tolerance
                    )
                if age_wear_multiplier > 1.0:
                    self.age_wear_active_events_last_tick += 1
                    self.total_age_wear_active_events += 1
                    self.age_wear_multiplier_sum_last_tick += age_wear_multiplier
                    self.total_age_wear_multiplier_sum += age_wear_multiplier
                    self.longevity_factor_sum_age_wear_last_tick += creature.traits.longevity_factor
                    self.total_longevity_factor_sum_age_wear += creature.traits.longevity_factor
            else:
                age_wear_multiplier = 1.0
            creature.drain_energy(
                dt=dt,
                drain_rate=self.energy_drain_rate,
                extra_multiplier=age_wear_multiplier * zone_drain_multiplier,
            )

        starvation_deaths = sum(
            1
            for creature in self.creatures
            if creature.creature_id in alive_before_ids and not creature.alive
        )
        self.death_causes_last_tick[self.DEATH_CAUSE_STARVATION] = starvation_deaths

        # 2) Decide behavior for each creature.
        reproduction_candidates = self._build_reproduction_candidates()
        previous_intents = self.last_intents
        intents: Dict[str, CreatureIntent] = {}
        for creature in self.creatures:
            previous_intent = previous_intents.get(creature.creature_id)
            intents[creature.creature_id] = self.ai_system.decide(
                creature,
                self.food_field,
                can_reproduce=(creature.creature_id in reproduction_candidates),
                nearby_creatures=self.creatures,
                previous_intent=previous_intent,
            )
        self.last_intents = intents

        for creature in self.creatures:
            if not creature.alive:
                continue
            intent = intents[creature.creature_id]
            previous_intent = previous_intents.get(creature.creature_id)
            if intent.action in (HungerAI.ACTION_SEARCH_FOOD, HungerAI.ACTION_MOVE_TO_FOOD):
                self.hunger_search_actions_last_tick += 1
                self.total_hunger_search_actions += 1
                self.hunger_sensitivity_sum_search_last_tick += creature.traits.hunger_sensitivity
                self.total_hunger_sensitivity_sum_search += creature.traits.hunger_sensitivity
            if intent.action == HungerAI.ACTION_MOVE_TO_FOOD and intent.target_food_id is not None:
                self.food_detection_moves_last_tick += 1
                self.total_food_detection_moves += 1
                self.food_perception_sum_detection_last_tick += creature.traits.food_perception
                self.total_food_perception_sum_detection += creature.traits.food_perception
            if intent.action == HungerAI.ACTION_FLEE:
                self.threat_detection_flee_last_tick += 1
                self.total_threat_detection_flee += 1
                self.threat_perception_sum_flee_last_tick += creature.traits.threat_perception
                self.total_threat_perception_sum_flee += creature.traits.threat_perception
                self.risk_taking_sum_flee_last_tick += creature.traits.risk_taking
                self.total_risk_taking_sum_flee += creature.traits.risk_taking

            if intent.persisted_from_previous:
                self.persistence_holds_last_tick += 1
                self.total_persistence_holds += 1
                self.behavior_persistence_sum_holds_last_tick += creature.traits.behavior_persistence
                self.total_behavior_persistence_sum_holds += creature.traits.behavior_persistence
                self.persistence_holding_creatures_last_tick.append(creature.creature_id)

            if previous_intent is not None:
                if self._is_search_wander_switch(previous_intent.action, intent.action):
                    self.search_wander_switches_last_tick += 1
                    self.total_search_wander_switches += 1
                    self.search_wander_oscillation_events_last_tick += 1
                    self.total_search_wander_oscillation_events += 1
                elif (
                    intent.persisted_from_previous
                    and self._is_search_wander_action(previous_intent.action)
                ):
                    self.search_wander_switches_prevented_last_tick += 1
                    self.total_search_wander_switches_prevented += 1
                    self.search_wander_oscillation_events_last_tick += 1
                    self.total_search_wander_oscillation_events += 1

            borderline_threat = self.ai_system.find_nearest_borderline_threat(
                creature,
                self.creatures,
            )
            if borderline_threat is not None:
                in_stress_pressure = self._is_stress_pressure_context(creature)
                self.borderline_threat_encounters_last_tick += 1
                self.total_borderline_threat_encounters += 1
                self.risk_taking_sum_borderline_encounters_last_tick += creature.traits.risk_taking
                self.total_risk_taking_sum_borderline_encounters += creature.traits.risk_taking

                if in_stress_pressure:
                    self.stress_pressure_events_last_tick += 1
                    self.total_stress_pressure_events += 1
                    self.stress_tolerance_sum_pressure_last_tick += creature.traits.stress_tolerance
                    self.total_stress_tolerance_sum_pressure += creature.traits.stress_tolerance

                if intent.action == HungerAI.ACTION_FLEE:
                    self.borderline_threat_flees_last_tick += 1
                    self.total_borderline_threat_flees += 1
                    self.risk_taking_sum_borderline_flees_last_tick += creature.traits.risk_taking
                    self.total_risk_taking_sum_borderline_flees += creature.traits.risk_taking
                    if in_stress_pressure:
                        self.stress_pressure_flee_events_last_tick += 1
                        self.total_stress_pressure_flee_events += 1
                        self.stress_tolerance_sum_pressure_flee_last_tick += (
                            creature.traits.stress_tolerance
                        )
                        self.total_stress_tolerance_sum_pressure_flee += (
                            creature.traits.stress_tolerance
                        )

        # 3) Execute movement and feeding behavior.
        creatures_by_id = {creature.creature_id: creature for creature in self.creatures}
        social_influenced_ids: set[str] = set()

        for creature in self.creatures:
            if not creature.alive:
                continue

            intent = intents[creature.creature_id]
            # THREAT/FLEE: execute flee intent before normal food/wander actions.
            if intent.action == HungerAI.ACTION_FLEE:
                threat = None
                if intent.target_creature_id is not None:
                    threat = creatures_by_id.get(intent.target_creature_id)

                if threat is None or not threat.alive:
                    self._wander(creature, dt, activity=1.0, allow_exploration_bias=False)
                    continue

                threat_distance = creature.distance_to(threat.x, threat.y)
                flee_boost_multiplier = self._social_flee_boost_multiplier(
                    creature,
                    intents,
                    creatures_by_id,
                )
                self._flee_from(creature, threat, dt, boost_multiplier=flee_boost_multiplier)
                if flee_boost_multiplier > 1.0:
                    self.social_flee_boosted_last_tick += 1
                    self.total_social_flee_boosted += 1
                    self.social_flee_multiplier_sum_last_tick += flee_boost_multiplier
                    self.total_social_flee_multiplier_sum += flee_boost_multiplier
                    self.social_sensitivity_sum_flee_boost_last_tick += creature.traits.social_sensitivity
                    self.total_social_sensitivity_sum_flee_boost += creature.traits.social_sensitivity
                    social_influenced_ids.add(creature.creature_id)
                creature.remember_danger_zone(threat.x, threat.y, ttl=self.danger_memory_duration)

                self.flees_last_tick += 1
                self.total_flees += 1
                self.fleeing_creatures_last_tick.append(creature.creature_id)
                self.flee_threat_distance_last_tick[creature.creature_id] = threat_distance
                continue

            if intent.action == "move_to_food" and intent.target_food_id is not None:
                target = self.food_field.get_food(intent.target_food_id)
                if target is None:
                    if not self._move_using_memory(creature, dt, search_mode=True):
                        self._wander(creature, dt, activity=1.0)
                    continue

                step_distance = self._movement_step_distance(creature, dt, activity=1.0)
                before_x = creature.x
                before_y = creature.y
                reached = creature.move_towards(
                    target_x=target.x,
                    target_y=target.y,
                    max_distance=step_distance,
                )
                self._clamp_creature_position(creature)
                moved_distance = creature.distance_to(before_x, before_y)
                self._record_mobility_usage(creature, moved_distance)
                if reached:
                    eaten = self.food_field.consume(target.food_id, self.eat_rate * dt)
                    creature.add_energy(eaten)
                    if eaten > 0.0:
                        self.food_consumptions_last_tick += 1
                        self.total_food_consumptions += 1
                        self.food_perception_sum_consumption_last_tick += creature.traits.food_perception
                        self.total_food_perception_sum_consumption += creature.traits.food_perception
                        creature.remember_food_zone(target.x, target.y, ttl=self.food_memory_duration)
                continue

            if intent.action == "search_food":
                if not self._move_using_memory(creature, dt, search_mode=True):
                    if self._move_using_social_follow(creature, dt, intents, creatures_by_id):
                        social_influenced_ids.add(creature.creature_id)
                    else:
                        # Search mode: more active movement than idle wandering.
                        self._wander(creature, dt, activity=1.0)
                continue

            if intent.action == "wander":
                if not self._move_using_memory(creature, dt, search_mode=False):
                    if self._move_using_social_follow(creature, dt, intents, creatures_by_id):
                        social_influenced_ids.add(creature.creature_id)
                    else:
                        self._wander(creature, dt, activity=0.5)

        self.social_influenced_creatures_last_tick = len(social_influenced_ids)
        self.total_social_influenced_creatures += self.social_influenced_creatures_last_tick

        if self.flee_threat_distance_last_tick:
            self.avg_flee_threat_distance_last_tick = (
                sum(self.flee_threat_distance_last_tick.values())
                / len(self.flee_threat_distance_last_tick)
            )
        else:
            self.avg_flee_threat_distance_last_tick = 0.0

        if self.food_memory_guided_moves_last_tick > 0:
            self.avg_food_memory_distance_gain_last_tick = (
                self.food_memory_distance_gain_last_tick / self.food_memory_guided_moves_last_tick
            )
        else:
            self.avg_food_memory_distance_gain_last_tick = 0.0

        if self.danger_memory_avoid_moves_last_tick > 0:
            self.avg_danger_memory_distance_gain_last_tick = (
                self.danger_memory_distance_gain_last_tick / self.danger_memory_avoid_moves_last_tick
            )
        else:
            self.avg_danger_memory_distance_gain_last_tick = 0.0

        if self.social_flee_boosted_last_tick > 0:
            self.avg_social_flee_multiplier_last_tick = (
                self.social_flee_multiplier_sum_last_tick / self.social_flee_boosted_last_tick
            )
        else:
            self.avg_social_flee_multiplier_last_tick = 1.0

        if self.exploration_bias_guided_moves_last_tick > 0:
            self.avg_exploration_bias_anchor_distance_delta_last_tick = (
                self.exploration_bias_anchor_distance_delta_last_tick
                / self.exploration_bias_guided_moves_last_tick
            )
        else:
            self.avg_exploration_bias_anchor_distance_delta_last_tick = 0.0

        if self.density_preference_guided_moves_last_tick > 0:
            self.avg_density_preference_center_distance_delta_last_tick = (
                self.density_preference_center_distance_delta_last_tick
                / self.density_preference_guided_moves_last_tick
            )
        else:
            self.avg_density_preference_center_distance_delta_last_tick = 0.0

        if self.gregariousness_guided_moves_last_tick > 0:
            self.avg_gregariousness_center_distance_delta_last_tick = (
                self.gregariousness_center_distance_delta_last_tick
                / self.gregariousness_guided_moves_last_tick
            )
        else:
            self.avg_gregariousness_center_distance_delta_last_tick = 0.0

        if self.competition_tolerance_guided_moves_last_tick > 0:
            self.avg_competition_tolerance_anchor_distance_delta_last_tick = (
                self.competition_tolerance_anchor_distance_delta_last_tick
                / self.competition_tolerance_guided_moves_last_tick
            )
        else:
            self.avg_competition_tolerance_anchor_distance_delta_last_tick = 0.0

        if self.resource_commitment_guided_moves_last_tick > 0:
            self.avg_resource_commitment_anchor_distance_delta_last_tick = (
                self.resource_commitment_anchor_distance_delta_last_tick
                / self.resource_commitment_guided_moves_last_tick
            )
        else:
            self.avg_resource_commitment_anchor_distance_delta_last_tick = 0.0

        if self.movement_actions_last_tick > 0:
            self.avg_movement_multiplier_last_tick = (
                self.movement_multiplier_sum_last_tick / self.movement_actions_last_tick
            )
            self.avg_movement_distance_last_tick = (
                self.movement_distance_sum_last_tick / self.movement_actions_last_tick
            )
        else:
            self.avg_movement_multiplier_last_tick = 1.0
            self.avg_movement_distance_last_tick = 0.0

        # 4) Reproduction with simple inheritance + mutation.
        exhaustion_deaths = self._process_reproduction(intents)
        self.death_causes_last_tick[self.DEATH_CAUSE_EXHAUSTION] = exhaustion_deaths

        dead_after = self.get_dead_count()
        self.deaths_last_tick = max(0, dead_after - dead_before)
        self.total_deaths += self.deaths_last_tick

        known_deaths = (
            self.death_causes_last_tick[self.DEATH_CAUSE_STARVATION]
            + self.death_causes_last_tick[self.DEATH_CAUSE_EXHAUSTION]
        )
        self.death_causes_last_tick[self.DEATH_CAUSE_UNKNOWN] = max(0, self.deaths_last_tick - known_deaths)

        for cause, value in self.death_causes_last_tick.items():
            self.total_death_causes[cause] += value

        self.tick_count += 1

    def _is_reproduction_eligible(self, creature: Creature) -> bool:
        required_energy = (
            self.reproduction_energy_threshold
            * self._compute_reproduction_timing_threshold_multiplier(creature)
        )
        return (
            creature.alive
            and creature.age >= self.reproduction_min_age
            and creature.energy >= required_energy
        )

    def _build_reproduction_candidates(self) -> Set[str]:
        eligible = [c for c in self.creatures if self._is_reproduction_eligible(c)]
        candidates: Set[str] = set()

        for idx, parent_a in enumerate(eligible):
            for parent_b in eligible[idx + 1 :]:
                if parent_a.distance_to(parent_b.x, parent_b.y) <= self.reproduction_distance:
                    candidates.add(parent_a.creature_id)
                    candidates.add(parent_b.creature_id)

        return candidates

    def _process_reproduction(self, intents: Dict[str, CreatureIntent]) -> int:
        newborns: list[Creature] = []
        used_ids: set[str] = set()
        exhaustion_deaths = 0

        candidates = [
            c
            for c in self.creatures
            if self._is_reproduction_eligible(c) and intents[c.creature_id].action == "reproduce"
        ]

        for idx, parent_a in enumerate(candidates):
            if parent_a.creature_id in used_ids:
                continue

            for parent_b in candidates[idx + 1 :]:
                if parent_b.creature_id in used_ids:
                    continue
                if parent_a.distance_to(parent_b.x, parent_b.y) > self.reproduction_distance:
                    continue

                child_traits = inherit_traits(
                    parent_a.traits,
                    parent_b.traits,
                    mutation_variation=self.mutation_variation,
                    rng=self.random_source,
                )

                child_x = (parent_a.x + parent_b.x) / 2.0
                child_y = (parent_a.y + parent_b.y) / 2.0
                if self.world_map is not None:
                    child_x, child_y = self.world_map.clamp(child_x, child_y)

                child = Creature(
                    creature_id=f"child_{self._child_counter}",
                    x=child_x,
                    y=child_y,
                    energy=child_traits.max_energy * 0.5,
                    traits=child_traits,
                    generation=max(parent_a.generation, parent_b.generation) + 1,
                    parent_ids=(parent_a.creature_id, parent_b.creature_id),
                )
                self._child_counter += 1
                newborns.append(child)

                parent_a_alive_before = parent_a.alive
                parent_b_alive_before = parent_b.alive

                parent_a_resistance_multiplier = self._compute_exhaustion_resistance_reproduction_multiplier(
                    parent_a
                )
                parent_b_resistance_multiplier = self._compute_exhaustion_resistance_reproduction_multiplier(
                    parent_b
                )
                parent_a_timing_multiplier = self._compute_reproduction_timing_threshold_multiplier(
                    parent_a
                )
                parent_b_timing_multiplier = self._compute_reproduction_timing_threshold_multiplier(
                    parent_b
                )
                parent_a_cost = self.reproduction_cost * parent_a_resistance_multiplier
                parent_b_cost = self.reproduction_cost * parent_b_resistance_multiplier

                parent_a.spend_energy(parent_a_cost)
                parent_b.spend_energy(parent_b_cost)
                self.reproduction_cost_events_last_tick += 2
                self.total_reproduction_cost_events += 2
                self.reproduction_cost_amount_last_tick += parent_a_cost + parent_b_cost
                self.total_reproduction_cost_amount += parent_a_cost + parent_b_cost
                self.reproduction_cost_multiplier_sum_last_tick += (
                    parent_a_resistance_multiplier + parent_b_resistance_multiplier
                )
                self.total_reproduction_cost_multiplier_sum += (
                    parent_a_resistance_multiplier + parent_b_resistance_multiplier
                )
                self.exhaustion_resistance_sum_reproduction_last_tick += (
                    parent_a.traits.exhaustion_resistance + parent_b.traits.exhaustion_resistance
                )
                self.total_exhaustion_resistance_sum_reproduction += (
                    parent_a.traits.exhaustion_resistance + parent_b.traits.exhaustion_resistance
                )
                self.reproduction_timing_sum_reproduction_last_tick += (
                    parent_a.traits.reproduction_timing + parent_b.traits.reproduction_timing
                )
                self.total_reproduction_timing_sum_reproduction += (
                    parent_a.traits.reproduction_timing + parent_b.traits.reproduction_timing
                )
                self.reproduction_timing_threshold_multiplier_sum_reproduction_last_tick += (
                    parent_a_timing_multiplier + parent_b_timing_multiplier
                )
                self.total_reproduction_timing_threshold_multiplier_sum_reproduction += (
                    parent_a_timing_multiplier + parent_b_timing_multiplier
                )

                if parent_a_alive_before and not parent_a.alive:
                    exhaustion_deaths += 1
                if parent_b_alive_before and not parent_b.alive:
                    exhaustion_deaths += 1

                used_ids.add(parent_a.creature_id)
                used_ids.add(parent_b.creature_id)
                break

        if newborns:
            self.creatures.extend(newborns)
            self.births_last_tick = len(newborns)
            self.total_births += len(newborns)

        return exhaustion_deaths

    def _move_using_memory(self, creature: Creature, dt: float, search_mode: bool) -> bool:
        if self._avoid_danger_memory(creature, dt):
            return True

        if search_mode:
            return self._move_towards_food_memory(creature, dt, activity=1.0)

        return False

    def _move_towards_food_memory(self, creature: Creature, dt: float, activity: float) -> bool:
        if not creature.has_food_memory:
            return False

        recall_multiplier = self._compute_resource_commitment_recall_multiplier(creature)
        effective_recall_distance = (
            self.food_memory_recall_distance * creature.traits.memory_focus * recall_multiplier
        )
        if effective_recall_distance <= 0.0:
            return False

        assert creature.last_food_zone is not None
        target_x, target_y = creature.last_food_zone
        distance_to_memory = creature.distance_to(target_x, target_y)
        if distance_to_memory > effective_recall_distance:
            return False

        step_distance = self._movement_step_distance(creature, dt, activity=activity)
        if step_distance <= 0.0:
            return False

        before_distance = distance_to_memory
        before_x = creature.x
        before_y = creature.y
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=step_distance)
        self._clamp_creature_position(creature)
        moved_distance = creature.distance_to(before_x, before_y)
        self._record_mobility_usage(creature, moved_distance)
        after_distance = creature.distance_to(target_x, target_y)
        distance_gain = max(0.0, before_distance - after_distance)

        self.food_memory_guided_moves_last_tick += 1
        self.total_food_memory_guided_moves += 1
        self.memory_focus_sum_food_memory_last_tick += creature.traits.memory_focus
        self.total_memory_focus_sum_food_memory += creature.traits.memory_focus
        self.resource_commitment_sum_food_memory_last_tick += creature.traits.resource_commitment
        self.total_resource_commitment_sum_food_memory += creature.traits.resource_commitment
        self.resource_commitment_recall_multiplier_sum_last_tick += recall_multiplier
        self.total_resource_commitment_recall_multiplier_sum += recall_multiplier
        self.food_memory_distance_gain_last_tick += distance_gain
        self.total_food_memory_distance_gain += distance_gain
        return True

    def _avoid_danger_memory(self, creature: Creature, dt: float) -> bool:
        if not creature.has_danger_memory:
            return False

        effective_avoid_distance = self.danger_memory_avoid_distance * creature.traits.memory_focus
        if effective_avoid_distance <= 0.0:
            return False

        assert creature.last_danger_zone is not None
        danger_x, danger_y = creature.last_danger_zone
        distance_to_danger = creature.distance_to(danger_x, danger_y)
        if distance_to_danger > effective_avoid_distance:
            return False

        step_distance = self._movement_step_distance(creature, dt, activity=1.0)
        if step_distance <= 0.0:
            return False

        before_distance = distance_to_danger
        dx = creature.x - danger_x
        dy = creature.y - danger_y
        if dx == 0.0 and dy == 0.0:
            self._wander(creature, dt, activity=1.0, allow_exploration_bias=False)
        else:
            target_x = creature.x + dx
            target_y = creature.y + dy
            before_x = creature.x
            before_y = creature.y
            creature.move_towards(target_x=target_x, target_y=target_y, max_distance=step_distance)
            self._clamp_creature_position(creature)
            moved_distance = creature.distance_to(before_x, before_y)
            self._record_mobility_usage(creature, moved_distance)
        after_distance = creature.distance_to(danger_x, danger_y)
        distance_gain = max(0.0, after_distance - before_distance)

        self.danger_memory_avoid_moves_last_tick += 1
        self.total_danger_memory_avoid_moves += 1
        self.memory_focus_sum_danger_memory_last_tick += creature.traits.memory_focus
        self.total_memory_focus_sum_danger_memory += creature.traits.memory_focus
        self.danger_memory_distance_gain_last_tick += distance_gain
        self.total_danger_memory_distance_gain += distance_gain
        return True

    def _move_using_social_follow(
        self,
        creature: Creature,
        dt: float,
        intents: Dict[str, CreatureIntent],
        creatures_by_id: Dict[str, Creature],
    ) -> bool:
        effective_social_distance = self.social_influence_distance * creature.traits.social_sensitivity
        effective_follow_strength = self.social_follow_strength * creature.traits.social_sensitivity

        if effective_social_distance <= 0.0 or effective_follow_strength <= 0.0:
            return False

        nearest_target: tuple[float, float] | None = None
        nearest_distance = float("inf")

        for other_id, other_intent in intents.items():
            if other_id == creature.creature_id:
                continue

            other = creatures_by_id.get(other_id)
            if other is None or not other.alive:
                continue

            if other_intent.action != HungerAI.ACTION_MOVE_TO_FOOD or other_intent.target_food_id is None:
                continue

            distance_to_other = creature.distance_to(other.x, other.y)
            if distance_to_other > effective_social_distance:
                continue

            food = self.food_field.get_food(other_intent.target_food_id)
            if food is None:
                continue

            if distance_to_other < nearest_distance:
                nearest_distance = distance_to_other
                nearest_target = (food.x, food.y)

        if nearest_target is None:
            return False

        step_distance = self._movement_step_distance(
            creature,
            dt,
            activity=effective_follow_strength,
        )
        if step_distance <= 0.0:
            return False

        before_x = creature.x
        before_y = creature.y
        creature.move_towards(
            target_x=nearest_target[0],
            target_y=nearest_target[1],
            max_distance=step_distance,
        )
        self._clamp_creature_position(creature)
        moved_distance = creature.distance_to(before_x, before_y)
        self._record_mobility_usage(creature, moved_distance)
        self.social_follow_moves_last_tick += 1
        self.total_social_follow_moves += 1
        self.social_sensitivity_sum_follow_last_tick += creature.traits.social_sensitivity
        self.total_social_sensitivity_sum_follow += creature.traits.social_sensitivity
        return True

    def _social_flee_boost_multiplier(
        self,
        creature: Creature,
        intents: Dict[str, CreatureIntent],
        creatures_by_id: Dict[str, Creature],
    ) -> float:
        effective_social_distance = self.social_influence_distance * creature.traits.social_sensitivity
        effective_boost_per_neighbor = self.social_flee_boost_per_neighbor * creature.traits.social_sensitivity
        effective_boost_max = self.social_flee_boost_max * creature.traits.social_sensitivity

        if effective_social_distance <= 0.0 or effective_boost_per_neighbor <= 0.0:
            return 1.0

        nearby_fleeing = 0
        for other_id, other_intent in intents.items():
            if other_id == creature.creature_id:
                continue

            if other_intent.action != HungerAI.ACTION_FLEE:
                continue

            other = creatures_by_id.get(other_id)
            if other is None or not other.alive:
                continue

            if creature.distance_to(other.x, other.y) <= effective_social_distance:
                nearby_fleeing += 1

        if nearby_fleeing <= 0:
            return 1.0

        boost = min(effective_boost_max, nearby_fleeing * effective_boost_per_neighbor)
        return 1.0 + boost

    def _wander(
        self,
        creature: Creature,
        dt: float,
        activity: float = 0.5,
        allow_exploration_bias: bool = True,
    ) -> None:
        if activity < 0:
            raise ValueError("activity must be >= 0")

        distance = self._movement_step_distance(creature, dt, activity=activity)
        if distance <= 0:
            return

        angle = self.random_source.uniform(0.0, 2.0 * pi)
        dir_x = cos(angle)
        dir_y = sin(angle)

        anchor: tuple[float, float] | None = None
        direction_mode: str | None = None
        before_anchor_distance = 0.0
        if allow_exploration_bias and creature.has_food_memory and creature.last_food_zone is not None:
            strength = min(0.35, abs(creature.traits.exploration_bias - 1.0))
            if strength > 0.0:
                anchor = creature.last_food_zone
                dx = creature.x - anchor[0]
                dy = creature.y - anchor[1]
                anchor_norm = hypot(dx, dy)
                if anchor_norm > 1e-9:
                    away_x = dx / anchor_norm
                    away_y = dy / anchor_norm
                    if creature.traits.exploration_bias >= 1.0:
                        bias_x = away_x
                        bias_y = away_y
                        direction_mode = "explore"
                    else:
                        bias_x = -away_x
                        bias_y = -away_y
                        direction_mode = "settle"

                    blended_x = ((1.0 - strength) * dir_x) + (strength * bias_x)
                    blended_y = ((1.0 - strength) * dir_y) + (strength * bias_y)
                    blended_norm = hypot(blended_x, blended_y)
                    if blended_norm > 1e-9:
                        dir_x = blended_x / blended_norm
                        dir_y = blended_y / blended_norm
                        before_anchor_distance = creature.distance_to(anchor[0], anchor[1])
                    else:
                        anchor = None
                        direction_mode = None
                else:
                    anchor = None

        density_center: tuple[float, float] | None = None
        density_mode: str | None = None
        density_neighbor_count = 0
        before_density_center_distance = 0.0
        if allow_exploration_bias:
            density_strength = min(0.22, abs(creature.traits.density_preference - 1.0) * 0.55)
            if density_strength > 0.0:
                local_density_radius = max(2.0, self.social_influence_distance * 0.6)
                if local_density_radius > 0.0:
                    sum_x = 0.0
                    sum_y = 0.0
                    neighbor_count = 0
                    for other in self.creatures:
                        if not other.alive or other.creature_id == creature.creature_id:
                            continue
                        if creature.distance_to(other.x, other.y) > local_density_radius:
                            continue
                        sum_x += other.x
                        sum_y += other.y
                        neighbor_count += 1

                    if neighbor_count > 0:
                        center_x = sum_x / neighbor_count
                        center_y = sum_y / neighbor_count
                        to_center_x = center_x - creature.x
                        to_center_y = center_y - creature.y
                        center_norm = hypot(to_center_x, to_center_y)
                        if center_norm > 1e-9:
                            if creature.traits.density_preference >= 1.0:
                                bias_x = to_center_x / center_norm
                                bias_y = to_center_y / center_norm
                                density_mode = "seek"
                            elif neighbor_count >= 2:
                                bias_x = -to_center_x / center_norm
                                bias_y = -to_center_y / center_norm
                                density_mode = "avoid"
                            else:
                                bias_x = 0.0
                                bias_y = 0.0

                            if density_mode is not None:
                                blended_x = ((1.0 - density_strength) * dir_x) + (density_strength * bias_x)
                                blended_y = ((1.0 - density_strength) * dir_y) + (density_strength * bias_y)
                                blended_norm = hypot(blended_x, blended_y)
                                if blended_norm > 1e-9:
                                    dir_x = blended_x / blended_norm
                                    dir_y = blended_y / blended_norm
                                    density_center = (center_x, center_y)
                                    density_neighbor_count = neighbor_count
                                    before_density_center_distance = creature.distance_to(center_x, center_y)
                                else:
                                    density_mode = None

        gregarious_center: tuple[float, float] | None = None
        gregarious_mode: str | None = None
        gregarious_neighbor_count = 0
        before_gregarious_center_distance = 0.0
        if allow_exploration_bias:
            gregarious_strength = min(0.18, abs(creature.traits.gregariousness - 1.0) * 0.45)
            if gregarious_strength > 0.0:
                local_social_radius = max(2.0, self.social_influence_distance * 0.7)
                if local_social_radius > 0.0:
                    sum_x = 0.0
                    sum_y = 0.0
                    neighbor_count = 0
                    for other in self.creatures:
                        if not other.alive or other.creature_id == creature.creature_id:
                            continue
                        if creature.distance_to(other.x, other.y) > local_social_radius:
                            continue
                        sum_x += other.x
                        sum_y += other.y
                        neighbor_count += 1

                    if neighbor_count > 0:
                        center_x = sum_x / neighbor_count
                        center_y = sum_y / neighbor_count
                        to_center_x = center_x - creature.x
                        to_center_y = center_y - creature.y
                        center_norm = hypot(to_center_x, to_center_y)
                        if center_norm > 1e-9:
                            if creature.traits.gregariousness >= 1.0:
                                bias_x = to_center_x / center_norm
                                bias_y = to_center_y / center_norm
                                gregarious_mode = "seek"
                            else:
                                bias_x = -to_center_x / center_norm
                                bias_y = -to_center_y / center_norm
                                gregarious_mode = "avoid"

                            blended_x = ((1.0 - gregarious_strength) * dir_x) + (
                                gregarious_strength * bias_x
                            )
                            blended_y = ((1.0 - gregarious_strength) * dir_y) + (
                                gregarious_strength * bias_y
                            )
                            blended_norm = hypot(blended_x, blended_y)
                            if blended_norm > 1e-9:
                                dir_x = blended_x / blended_norm
                                dir_y = blended_y / blended_norm
                                gregarious_center = (center_x, center_y)
                                gregarious_neighbor_count = neighbor_count
                                before_gregarious_center_distance = creature.distance_to(
                                    center_x,
                                    center_y,
                                )
                            else:
                                gregarious_mode = None

        competition_anchor: tuple[float, float] | None = None
        competition_mode: str | None = None
        competition_neighbor_count = 0
        before_competition_anchor_distance = 0.0
        if allow_exploration_bias and creature.has_food_memory and creature.last_food_zone is not None:
            competition_strength = min(
                0.26,
                abs(creature.traits.competition_tolerance - 1.0) * 1.4,
            )
            if competition_strength > 0.0:
                local_competition_radius = max(2.0, self.social_influence_distance * 0.65)
                if local_competition_radius > 0.0:
                    for other in self.creatures:
                        if not other.alive or other.creature_id == creature.creature_id:
                            continue
                        if creature.distance_to(other.x, other.y) <= local_competition_radius:
                            competition_neighbor_count += 1

                if competition_neighbor_count > 0:
                    anchor_x, anchor_y = creature.last_food_zone
                    to_anchor_x = anchor_x - creature.x
                    to_anchor_y = anchor_y - creature.y
                    anchor_norm = hypot(to_anchor_x, to_anchor_y)
                    if anchor_norm > 1e-9:
                        if creature.traits.competition_tolerance >= 1.0:
                            bias_x = to_anchor_x / anchor_norm
                            bias_y = to_anchor_y / anchor_norm
                            competition_mode = "stay"
                        elif competition_neighbor_count >= 2:
                            bias_x = -to_anchor_x / anchor_norm
                            bias_y = -to_anchor_y / anchor_norm
                            competition_mode = "avoid"
                        else:
                            bias_x = 0.0
                            bias_y = 0.0

                        if competition_mode is not None:
                            blended_x = ((1.0 - competition_strength) * dir_x) + (
                                competition_strength * bias_x
                            )
                            blended_y = ((1.0 - competition_strength) * dir_y) + (
                                competition_strength * bias_y
                            )
                            blended_norm = hypot(blended_x, blended_y)
                            if blended_norm > 1e-9:
                                dir_x = blended_x / blended_norm
                                dir_y = blended_y / blended_norm
                                competition_anchor = (anchor_x, anchor_y)
                                before_competition_anchor_distance = creature.distance_to(
                                    anchor_x,
                                    anchor_y,
                                )
                            else:
                                competition_mode = None

        resource_anchor: tuple[float, float] | None = None
        resource_mode: str | None = None
        before_resource_anchor_distance = 0.0
        if allow_exploration_bias and creature.has_food_memory and creature.last_food_zone is not None:
            resource_strength = min(
                0.2,
                abs(creature.traits.resource_commitment - 1.0) * 0.8,
            )
            if resource_strength > 0.0:
                anchor_x, anchor_y = creature.last_food_zone
                to_anchor_x = anchor_x - creature.x
                to_anchor_y = anchor_y - creature.y
                anchor_norm = hypot(to_anchor_x, to_anchor_y)
                if anchor_norm > 1e-9:
                    if creature.traits.resource_commitment >= 1.0:
                        bias_x = to_anchor_x / anchor_norm
                        bias_y = to_anchor_y / anchor_norm
                        resource_mode = "stay"
                    else:
                        bias_x = -to_anchor_x / anchor_norm
                        bias_y = -to_anchor_y / anchor_norm
                        resource_mode = "switch"

                    blended_x = ((1.0 - resource_strength) * dir_x) + (resource_strength * bias_x)
                    blended_y = ((1.0 - resource_strength) * dir_y) + (resource_strength * bias_y)
                    blended_norm = hypot(blended_x, blended_y)
                    if blended_norm > 1e-9:
                        dir_x = blended_x / blended_norm
                        dir_y = blended_y / blended_norm
                        resource_anchor = (anchor_x, anchor_y)
                        before_resource_anchor_distance = creature.distance_to(anchor_x, anchor_y)
                    else:
                        resource_mode = None

        target_x = creature.x + (dir_x * distance)
        target_y = creature.y + (dir_y * distance)
        before_x = creature.x
        before_y = creature.y
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=distance)
        self._clamp_creature_position(creature)
        moved_distance = creature.distance_to(before_x, before_y)
        self._record_mobility_usage(creature, moved_distance)

        if anchor is not None and direction_mode is not None:
            after_anchor_distance = creature.distance_to(anchor[0], anchor[1])
            distance_delta = after_anchor_distance - before_anchor_distance
            self.exploration_bias_guided_moves_last_tick += 1
            self.total_exploration_bias_guided_moves += 1
            self.exploration_bias_sum_guided_last_tick += creature.traits.exploration_bias
            self.total_exploration_bias_sum_guided += creature.traits.exploration_bias
            self.exploration_bias_anchor_distance_delta_last_tick += distance_delta
            self.total_exploration_bias_anchor_distance_delta += distance_delta
            if direction_mode == "explore":
                self.exploration_bias_explore_moves_last_tick += 1
                self.total_exploration_bias_explore_moves += 1
                self.exploration_bias_sum_explore_last_tick += creature.traits.exploration_bias
                self.total_exploration_bias_sum_explore += creature.traits.exploration_bias
            else:
                self.exploration_bias_settle_moves_last_tick += 1
                self.total_exploration_bias_settle_moves += 1
                self.exploration_bias_sum_settle_last_tick += creature.traits.exploration_bias
                self.total_exploration_bias_sum_settle += creature.traits.exploration_bias

        if density_center is not None and density_mode is not None:
            after_density_center_distance = creature.distance_to(density_center[0], density_center[1])
            center_distance_delta = after_density_center_distance - before_density_center_distance

            self.density_preference_guided_moves_last_tick += 1
            self.total_density_preference_guided_moves += 1
            self.density_preference_sum_guided_last_tick += creature.traits.density_preference
            self.total_density_preference_sum_guided += creature.traits.density_preference
            self.density_preference_neighbor_count_sum_last_tick += density_neighbor_count
            self.total_density_preference_neighbor_count_sum += density_neighbor_count
            self.density_preference_center_distance_delta_last_tick += center_distance_delta
            self.total_density_preference_center_distance_delta += center_distance_delta
            if density_mode == "seek":
                self.density_preference_seek_moves_last_tick += 1
                self.total_density_preference_seek_moves += 1
                self.density_preference_sum_seek_last_tick += creature.traits.density_preference
                self.total_density_preference_sum_seek += creature.traits.density_preference
            else:
                self.density_preference_avoid_moves_last_tick += 1
                self.total_density_preference_avoid_moves += 1
                self.density_preference_sum_avoid_last_tick += creature.traits.density_preference
                self.total_density_preference_sum_avoid += creature.traits.density_preference

        if gregarious_center is not None and gregarious_mode is not None:
            after_gregarious_center_distance = creature.distance_to(
                gregarious_center[0],
                gregarious_center[1],
            )
            center_distance_delta = after_gregarious_center_distance - before_gregarious_center_distance
            self.gregariousness_guided_moves_last_tick += 1
            self.total_gregariousness_guided_moves += 1
            self.gregariousness_sum_guided_last_tick += creature.traits.gregariousness
            self.total_gregariousness_sum_guided += creature.traits.gregariousness
            self.gregariousness_neighbor_count_sum_last_tick += gregarious_neighbor_count
            self.total_gregariousness_neighbor_count_sum += gregarious_neighbor_count
            self.gregariousness_center_distance_delta_last_tick += center_distance_delta
            self.total_gregariousness_center_distance_delta += center_distance_delta
            if gregarious_mode == "seek":
                self.gregariousness_seek_moves_last_tick += 1
                self.total_gregariousness_seek_moves += 1
                self.gregariousness_sum_seek_last_tick += creature.traits.gregariousness
                self.total_gregariousness_sum_seek += creature.traits.gregariousness
            else:
                self.gregariousness_avoid_moves_last_tick += 1
                self.total_gregariousness_avoid_moves += 1
                self.gregariousness_sum_avoid_last_tick += creature.traits.gregariousness
                self.total_gregariousness_sum_avoid += creature.traits.gregariousness

        if competition_anchor is not None and competition_mode is not None:
            after_competition_anchor_distance = creature.distance_to(
                competition_anchor[0],
                competition_anchor[1],
            )
            anchor_distance_delta = (
                after_competition_anchor_distance - before_competition_anchor_distance
            )
            self.competition_tolerance_guided_moves_last_tick += 1
            self.total_competition_tolerance_guided_moves += 1
            self.competition_tolerance_sum_guided_last_tick += creature.traits.competition_tolerance
            self.total_competition_tolerance_sum_guided += creature.traits.competition_tolerance
            self.competition_tolerance_neighbor_count_sum_last_tick += competition_neighbor_count
            self.total_competition_tolerance_neighbor_count_sum += competition_neighbor_count
            self.competition_tolerance_anchor_distance_delta_last_tick += anchor_distance_delta
            self.total_competition_tolerance_anchor_distance_delta += anchor_distance_delta
            if competition_mode == "stay":
                self.competition_tolerance_stay_moves_last_tick += 1
                self.total_competition_tolerance_stay_moves += 1
                self.competition_tolerance_sum_stay_last_tick += creature.traits.competition_tolerance
                self.total_competition_tolerance_sum_stay += creature.traits.competition_tolerance
            else:
                self.competition_tolerance_avoid_moves_last_tick += 1
                self.total_competition_tolerance_avoid_moves += 1
                self.competition_tolerance_sum_avoid_last_tick += creature.traits.competition_tolerance
                self.total_competition_tolerance_sum_avoid += creature.traits.competition_tolerance

        if resource_anchor is not None and resource_mode is not None:
            after_resource_anchor_distance = creature.distance_to(
                resource_anchor[0],
                resource_anchor[1],
            )
            anchor_distance_delta = after_resource_anchor_distance - before_resource_anchor_distance
            self.resource_commitment_guided_moves_last_tick += 1
            self.total_resource_commitment_guided_moves += 1
            self.resource_commitment_sum_guided_last_tick += creature.traits.resource_commitment
            self.total_resource_commitment_sum_guided += creature.traits.resource_commitment
            self.resource_commitment_anchor_distance_delta_last_tick += anchor_distance_delta
            self.total_resource_commitment_anchor_distance_delta += anchor_distance_delta
            if resource_mode == "stay":
                self.resource_commitment_stay_moves_last_tick += 1
                self.total_resource_commitment_stay_moves += 1
                self.resource_commitment_sum_stay_last_tick += creature.traits.resource_commitment
                self.total_resource_commitment_sum_stay += creature.traits.resource_commitment
            else:
                self.resource_commitment_switch_moves_last_tick += 1
                self.total_resource_commitment_switch_moves += 1
                self.resource_commitment_sum_switch_last_tick += creature.traits.resource_commitment
                self.total_resource_commitment_sum_switch += creature.traits.resource_commitment

    # THREAT/FLEE: move in the opposite direction of the threat (no pathfinding).
    def _flee_from(
        self,
        creature: Creature,
        threat: Creature,
        dt: float,
        boost_multiplier: float = 1.0,
    ) -> None:
        flee_distance = self._movement_step_distance(
            creature,
            dt,
            activity=1.2 * max(1.0, boost_multiplier),
        )
        if flee_distance <= 0:
            return

        dx = creature.x - threat.x
        dy = creature.y - threat.y

        if dx == 0.0 and dy == 0.0:
            self._wander(creature, dt, activity=1.2, allow_exploration_bias=False)
            return

        target_x = creature.x + dx
        target_y = creature.y + dy
        before_x = creature.x
        before_y = creature.y
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=flee_distance)
        self._clamp_creature_position(creature)
        moved_distance = creature.distance_to(before_x, before_y)
        self._record_mobility_usage(creature, moved_distance)

    def _clamp_creature_position(self, creature: Creature) -> None:
        if self.world_map is not None:
            creature.x, creature.y = self.world_map.clamp(creature.x, creature.y)

    def get_alive_count(self) -> int:
        return sum(1 for creature in self.creatures if creature.alive)

    def get_dead_count(self) -> int:
        return sum(1 for creature in self.creatures if not creature.alive)

    def get_total_count(self) -> int:
        return len(self.creatures)

    @staticmethod
    def _compute_energy_efficiency_drain_multiplier(creature: Creature) -> float:
        return max(0.1, 1.0 - (0.25 * (creature.traits.energy_efficiency - 1.0)))

    @classmethod
    def _compute_age_wear_multiplier(cls, creature: Creature) -> float:
        longevity = max(0.1, creature.traits.longevity_factor)
        start_age = cls.AGE_WEAR_START * longevity
        extra_age = max(0.0, creature.age - start_age)
        wear_rate = cls.AGE_WEAR_RATE / longevity
        wear_bonus = min(cls.AGE_WEAR_MAX_EXTRA_MULTIPLIER, extra_age * wear_rate)
        return 1.0 + wear_bonus

    @staticmethod
    def _compute_exhaustion_resistance_reproduction_multiplier(creature: Creature) -> float:
        return max(0.1, 1.0 - (0.3 * (creature.traits.exhaustion_resistance - 1.0)))

    @staticmethod
    def _compute_reproduction_timing_threshold_multiplier(creature: Creature) -> float:
        # Light individual bias:
        # - >1.0 waits for slightly more energy margin before reproducing.
        # - <1.0 accepts reproducing with slightly less margin.
        return max(0.9, min(1.1, 1.0 + (0.1 * (creature.traits.reproduction_timing - 1.0))))

    @staticmethod
    def _compute_resource_commitment_recall_multiplier(creature: Creature) -> float:
        # Light individual bias:
        # - >1.0 keeps local food-memory recall slightly longer.
        # - <1.0 drops local food-memory guidance slightly sooner.
        return max(0.9, min(1.1, 1.0 + (0.7 * (creature.traits.resource_commitment - 1.0))))

    @staticmethod
    def _compute_mobility_efficiency_multiplier(creature: Creature) -> float:
        return max(0.9, min(1.1, creature.traits.mobility_efficiency))

    def _movement_step_distance(self, creature: Creature, dt: float, activity: float) -> float:
        if dt <= 0.0 or activity <= 0.0:
            return 0.0
        return (
            self.movement_speed
            * activity
            * creature.traits.speed
            * self._compute_mobility_efficiency_multiplier(creature)
            * dt
        )

    def _record_mobility_usage(self, creature: Creature, moved_distance: float) -> None:
        self.movement_actions_last_tick += 1
        self.total_movement_actions += 1
        self.mobility_efficiency_sum_movement_last_tick += creature.traits.mobility_efficiency
        self.total_mobility_efficiency_sum_movement += creature.traits.mobility_efficiency
        multiplier = self._compute_mobility_efficiency_multiplier(creature)
        self.movement_multiplier_sum_last_tick += multiplier
        self.total_movement_multiplier_sum += multiplier
        safe_distance = max(0.0, moved_distance)
        self.movement_distance_sum_last_tick += safe_distance
        self.total_movement_distance_sum += safe_distance

    def _resolve_fertility_zone(self, x: float, y: float) -> str:
        if self.fertility_zone_getter is None:
            return "neutral"
        zone_name = str(self.fertility_zone_getter(x, y))
        if zone_name not in ("rich", "neutral", "poor"):
            return "neutral"
        return zone_name

    def _compute_environmental_zone_multiplier(self, creature: Creature) -> tuple[float, str]:
        zone_name = self._resolve_fertility_zone(creature.x, creature.y)
        tolerance = max(0.1, creature.traits.environmental_tolerance)
        delta = tolerance - 1.0

        if zone_name == "poor":
            multiplier = 1.0 - (0.20 * delta)
        elif zone_name == "rich":
            multiplier = 1.0 - (0.10 * delta)
        else:
            multiplier = 1.0

        return max(0.9, min(1.1, multiplier)), zone_name

    def _is_stress_pressure_context(self, creature: Creature) -> bool:
        low_energy = creature.energy <= (creature.max_energy * 0.35)
        return creature.hunger >= self.ai_system.hunger_seek_threshold or low_energy

    @staticmethod
    def _is_search_wander_action(action: str) -> bool:
        return action in (HungerAI.ACTION_SEARCH_FOOD, HungerAI.ACTION_WANDER)

    @classmethod
    def _is_search_wander_switch(cls, previous_action: str, next_action: str) -> bool:
        return (
            previous_action != next_action
            and cls._is_search_wander_action(previous_action)
            and cls._is_search_wander_action(next_action)
        )




