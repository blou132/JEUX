import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_generation_distribution, build_population_stats
from genetics import GeneticTraits
from simulation import HungerSimulation
from world import FoodField


class DebugStatsTests(unittest.TestCase):
    def test_population_stats_include_required_fields(self) -> None:
        creatures = [
            Creature(
                creature_id="c1",
                x=0.0,
                y=0.0,
                energy=50.0,
                traits=GeneticTraits(
                    speed=1.2,
                    metabolism=0.9,
                    max_energy=100.0,
                    prudence=1.1,
                    dominance=0.9,
                    repro_drive=1.2,
                ),
                age=5.0,
            ),
            Creature(
                creature_id="c2",
                x=1.0,
                y=0.0,
                energy=20.0,
                traits=GeneticTraits(
                    speed=0.8,
                    metabolism=1.1,
                    max_energy=100.0,
                    prudence=0.9,
                    dominance=1.1,
                    repro_drive=0.8,
                ),
                age=3.0,
            ),
        ]
        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)

        self.assertEqual(stats["population"], 2)
        self.assertIn("food_remaining", stats)
        self.assertIn("avg_energy", stats)
        self.assertIn("avg_age", stats)
        self.assertIn("avg_generation", stats)
        self.assertIn("total_deaths", stats)
        self.assertIn("total_births", stats)
        self.assertIn("avg_speed", stats)
        self.assertIn("avg_metabolism", stats)
        self.assertIn("avg_prudence", stats)
        self.assertIn("avg_dominance", stats)
        self.assertIn("avg_repro_drive", stats)
        self.assertIn("avg_memory_focus", stats)
        self.assertIn("avg_social_sensitivity", stats)
        self.assertIn("avg_behavior_persistence", stats)
        self.assertIn("avg_exploration_bias", stats)
        self.assertIn("avg_density_preference", stats)
        self.assertIn("avg_energy_efficiency", stats)
        self.assertIn("avg_exhaustion_resistance", stats)
        self.assertIn("std_memory_focus", stats)
        self.assertIn("std_social_sensitivity", stats)
        self.assertIn("std_behavior_persistence", stats)
        self.assertIn("std_exploration_bias", stats)
        self.assertIn("std_density_preference", stats)
        self.assertIn("std_energy_efficiency", stats)
        self.assertIn("std_exhaustion_resistance", stats)
        self.assertIn("avg_effective_energy_drain_multiplier", stats)
        self.assertIn("avg_reproduction_cost_multiplier", stats)
        self.assertIn("energy_drain_events_last_tick", stats)
        self.assertIn("total_energy_drain_events", stats)
        self.assertIn("avg_energy_drain_amount_last_tick", stats)
        self.assertIn("avg_energy_drain_amount_total", stats)
        self.assertIn("avg_energy_drain_multiplier_observed_last_tick", stats)
        self.assertIn("avg_energy_drain_multiplier_observed_total", stats)
        self.assertIn("energy_efficiency_drain_users_avg_tick", stats)
        self.assertIn("energy_efficiency_drain_users_avg_total", stats)
        self.assertIn("energy_efficiency_drain_usage_bias_tick", stats)
        self.assertIn("energy_efficiency_drain_usage_bias_total", stats)
        self.assertIn("reproduction_cost_events_last_tick", stats)
        self.assertIn("total_reproduction_cost_events", stats)
        self.assertIn("avg_reproduction_cost_amount_last_tick", stats)
        self.assertIn("avg_reproduction_cost_amount_total", stats)
        self.assertIn("avg_reproduction_cost_multiplier_observed_last_tick", stats)
        self.assertIn("avg_reproduction_cost_multiplier_observed_total", stats)
        self.assertIn("exhaustion_resistance_reproduction_users_avg_tick", stats)
        self.assertIn("exhaustion_resistance_reproduction_users_avg_total", stats)
        self.assertIn("exhaustion_resistance_reproduction_usage_bias_tick", stats)
        self.assertIn("exhaustion_resistance_reproduction_usage_bias_total", stats)
        self.assertIn("death_causes_last_tick", stats)
        self.assertIn("death_causes_total", stats)
        self.assertIn("flees_last_tick", stats)
        self.assertIn("total_flees", stats)
        self.assertIn("fleeing_creatures_last_tick", stats)
        self.assertIn("avg_flee_threat_distance_last_tick", stats)
        self.assertIn("creatures_with_food_memory", stats)
        self.assertIn("creatures_with_danger_memory", stats)
        self.assertIn("food_memory_guided_moves_last_tick", stats)
        self.assertIn("total_food_memory_guided_moves", stats)
        self.assertIn("danger_memory_avoid_moves_last_tick", stats)
        self.assertIn("total_danger_memory_avoid_moves", stats)
        self.assertIn("food_memory_active_share", stats)
        self.assertIn("danger_memory_active_share", stats)
        self.assertIn("food_memory_usage_per_alive_tick", stats)
        self.assertIn("danger_memory_usage_per_alive_tick", stats)
        self.assertIn("food_memory_usage_per_tick_total", stats)
        self.assertIn("danger_memory_usage_per_tick_total", stats)
        self.assertIn("food_memory_effect_avg_distance_tick", stats)
        self.assertIn("danger_memory_effect_avg_distance_tick", stats)
        self.assertIn("food_memory_effect_avg_distance_total", stats)
        self.assertIn("danger_memory_effect_avg_distance_total", stats)
        self.assertIn("social_follow_moves_last_tick", stats)
        self.assertIn("total_social_follow_moves", stats)
        self.assertIn("social_flee_boosted_last_tick", stats)
        self.assertIn("total_social_flee_boosted", stats)
        self.assertIn("avg_social_flee_multiplier_last_tick", stats)
        self.assertIn("social_follow_usage_per_alive_tick", stats)
        self.assertIn("social_flee_boost_usage_per_alive_tick", stats)
        self.assertIn("social_follow_usage_per_tick_total", stats)
        self.assertIn("social_flee_boost_usage_per_tick_total", stats)
        self.assertIn("social_influenced_creatures_last_tick", stats)
        self.assertIn("total_social_influenced_creatures", stats)
        self.assertIn("social_influenced_share_last_tick", stats)
        self.assertIn("social_influenced_per_tick_total", stats)
        self.assertIn("social_flee_multiplier_avg_total", stats)
        self.assertIn("memory_focus_food_users_avg_tick", stats)
        self.assertIn("memory_focus_food_users_avg_total", stats)
        self.assertIn("memory_focus_food_usage_bias_tick", stats)
        self.assertIn("memory_focus_food_usage_bias_total", stats)
        self.assertIn("memory_focus_danger_users_avg_tick", stats)
        self.assertIn("memory_focus_danger_users_avg_total", stats)
        self.assertIn("memory_focus_danger_usage_bias_tick", stats)
        self.assertIn("memory_focus_danger_usage_bias_total", stats)
        self.assertIn("social_sensitivity_follow_users_avg_tick", stats)
        self.assertIn("social_sensitivity_follow_users_avg_total", stats)
        self.assertIn("social_sensitivity_follow_usage_bias_tick", stats)
        self.assertIn("social_sensitivity_follow_usage_bias_total", stats)
        self.assertIn("social_sensitivity_flee_boost_users_avg_tick", stats)
        self.assertIn("social_sensitivity_flee_boost_users_avg_total", stats)
        self.assertIn("social_sensitivity_flee_boost_usage_bias_tick", stats)
        self.assertIn("social_sensitivity_flee_boost_usage_bias_total", stats)
        self.assertIn("food_detection_moves_last_tick", stats)
        self.assertIn("total_food_detection_moves", stats)
        self.assertIn("food_consumptions_last_tick", stats)
        self.assertIn("total_food_consumptions", stats)
        self.assertIn("threat_detection_flee_last_tick", stats)
        self.assertIn("total_threat_detection_flee", stats)
        self.assertIn("food_detection_usage_per_alive_tick", stats)
        self.assertIn("food_detection_usage_per_tick_total", stats)
        self.assertIn("food_consumption_usage_per_alive_tick", stats)
        self.assertIn("food_consumption_usage_per_tick_total", stats)
        self.assertIn("threat_detection_usage_per_alive_tick", stats)
        self.assertIn("threat_detection_usage_per_tick_total", stats)
        self.assertIn("food_perception_detection_users_avg_tick", stats)
        self.assertIn("food_perception_detection_users_avg_total", stats)
        self.assertIn("food_perception_detection_usage_bias_tick", stats)
        self.assertIn("food_perception_detection_usage_bias_total", stats)
        self.assertIn("food_perception_consumption_users_avg_tick", stats)
        self.assertIn("food_perception_consumption_users_avg_total", stats)
        self.assertIn("food_perception_consumption_usage_bias_tick", stats)
        self.assertIn("food_perception_consumption_usage_bias_total", stats)
        self.assertIn("threat_perception_flee_users_avg_tick", stats)
        self.assertIn("threat_perception_flee_users_avg_total", stats)
        self.assertIn("threat_perception_flee_usage_bias_tick", stats)
        self.assertIn("threat_perception_flee_usage_bias_total", stats)
        self.assertIn("persistence_holds_last_tick", stats)
        self.assertIn("total_persistence_holds", stats)
        self.assertIn("behavior_persistence_hold_users_avg_tick", stats)
        self.assertIn("behavior_persistence_hold_users_avg_total", stats)
        self.assertIn("behavior_persistence_hold_usage_bias_tick", stats)
        self.assertIn("behavior_persistence_hold_usage_bias_total", stats)
        self.assertIn("exploration_bias_guided_moves_last_tick", stats)
        self.assertIn("total_exploration_bias_guided_moves", stats)
        self.assertIn("exploration_bias_usage_per_alive_tick", stats)
        self.assertIn("exploration_bias_usage_per_tick_total", stats)
        self.assertIn("exploration_bias_guided_users_avg_tick", stats)
        self.assertIn("exploration_bias_guided_users_avg_total", stats)
        self.assertIn("exploration_bias_guided_usage_bias_tick", stats)
        self.assertIn("exploration_bias_guided_usage_bias_total", stats)
        self.assertIn("exploration_bias_explore_moves_last_tick", stats)
        self.assertIn("total_exploration_bias_explore_moves", stats)
        self.assertIn("exploration_bias_explore_users_avg_tick", stats)
        self.assertIn("exploration_bias_explore_users_avg_total", stats)
        self.assertIn("exploration_bias_explore_usage_bias_tick", stats)
        self.assertIn("exploration_bias_explore_usage_bias_total", stats)
        self.assertIn("exploration_bias_settle_moves_last_tick", stats)
        self.assertIn("total_exploration_bias_settle_moves", stats)
        self.assertIn("exploration_bias_settle_users_avg_tick", stats)
        self.assertIn("exploration_bias_settle_users_avg_total", stats)
        self.assertIn("exploration_bias_settle_usage_bias_tick", stats)
        self.assertIn("exploration_bias_settle_usage_bias_total", stats)
        self.assertIn("exploration_bias_explore_share_last_tick", stats)
        self.assertIn("exploration_bias_explore_share_total", stats)
        self.assertIn("avg_exploration_bias_anchor_distance_delta_last_tick", stats)
        self.assertIn("avg_exploration_bias_anchor_distance_delta_total", stats)
        self.assertIn("density_preference_guided_moves_last_tick", stats)
        self.assertIn("total_density_preference_guided_moves", stats)
        self.assertIn("density_preference_usage_per_alive_tick", stats)
        self.assertIn("density_preference_usage_per_tick_total", stats)
        self.assertIn("density_preference_guided_users_avg_tick", stats)
        self.assertIn("density_preference_guided_users_avg_total", stats)
        self.assertIn("density_preference_guided_usage_bias_tick", stats)
        self.assertIn("density_preference_guided_usage_bias_total", stats)
        self.assertIn("density_preference_seek_moves_last_tick", stats)
        self.assertIn("total_density_preference_seek_moves", stats)
        self.assertIn("density_preference_seek_users_avg_tick", stats)
        self.assertIn("density_preference_seek_users_avg_total", stats)
        self.assertIn("density_preference_seek_usage_bias_tick", stats)
        self.assertIn("density_preference_seek_usage_bias_total", stats)
        self.assertIn("density_preference_avoid_moves_last_tick", stats)
        self.assertIn("total_density_preference_avoid_moves", stats)
        self.assertIn("density_preference_avoid_users_avg_tick", stats)
        self.assertIn("density_preference_avoid_users_avg_total", stats)
        self.assertIn("density_preference_avoid_usage_bias_tick", stats)
        self.assertIn("density_preference_avoid_usage_bias_total", stats)
        self.assertIn("density_preference_seek_share_last_tick", stats)
        self.assertIn("density_preference_seek_share_total", stats)
        self.assertIn("avg_density_preference_neighbor_count_last_tick", stats)
        self.assertIn("avg_density_preference_neighbor_count_total", stats)
        self.assertIn("avg_density_preference_center_distance_delta_last_tick", stats)
        self.assertIn("avg_density_preference_center_distance_delta_total", stats)
        self.assertIn("search_wander_switches_last_tick", stats)
        self.assertIn("total_search_wander_switches", stats)
        self.assertIn("search_wander_switches_prevented_last_tick", stats)
        self.assertIn("total_search_wander_switches_prevented", stats)
        self.assertIn("search_wander_oscillation_events_last_tick", stats)
        self.assertIn("total_search_wander_oscillation_events", stats)
        self.assertIn("search_wander_switch_rate_last_tick", stats)
        self.assertIn("search_wander_switch_rate_total", stats)
        self.assertIn("search_wander_prevented_rate_last_tick", stats)
        self.assertIn("search_wander_prevented_rate_total", stats)
        self.assertIn("creatures_by_fertility_zone", stats)
        self.assertIn("dominant_proto_group_by_fertility_zone", stats)
        self.assertIn("proto_group_temporal_trends", stats)
        self.assertIn("proto_group_temporal_summary", stats)

    def test_generation_distribution_matches_population_counts(self) -> None:
        creatures = [
            Creature(creature_id="g0_a", x=0.0, y=0.0, energy=80.0, generation=0),
            Creature(creature_id="g0_b", x=1.0, y=0.0, energy=70.0, generation=0),
            Creature(creature_id="g1", x=2.0, y=0.0, energy=60.0, generation=1),
            Creature(creature_id="g2", x=3.0, y=0.0, energy=50.0, generation=2),
        ]
        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        distribution = build_generation_distribution(sim)

        self.assertEqual(sum(distribution.values()), stats["population"])
        self.assertEqual(distribution, {0: 2, 1: 1, 2: 1})
        self.assertAlmostEqual(float(stats["avg_generation"]), 0.75)


if __name__ == "__main__":
    unittest.main()

