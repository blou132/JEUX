import random
import subprocess
import sys
import unittest
from pathlib import Path

from ai import HungerAI
from creatures import Creature
from debug_tools import (
    build_final_run_summary,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from genetics import GeneticTraits
from simulation import HungerSimulation
from ui import format_final_run_summary, format_multi_run_summary
from world import FoodField, FoodSource


class SocialImpactMetricsTests(unittest.TestCase):
    def test_population_stats_include_social_impact_metrics(self) -> None:
        leader = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        follower = Creature(
            creature_id="follower",
            x=0.0,
            y=1.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))

        simulation = HungerSimulation(
            creatures=[leader, follower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=4.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(501),
        )

        simulation.tick(dt=1.0)
        stats = build_population_stats(simulation)

        self.assertIn("social_follow_moves_last_tick", stats)
        self.assertIn("social_flee_boosted_last_tick", stats)
        self.assertIn("social_influenced_creatures_last_tick", stats)
        self.assertIn("social_influenced_share_last_tick", stats)
        self.assertIn("social_influenced_per_tick_total", stats)
        self.assertIn("social_flee_multiplier_avg_total", stats)

        self.assertEqual(int(stats["social_follow_moves_last_tick"]), 1)
        self.assertEqual(int(stats["social_influenced_creatures_last_tick"]), 1)
        self.assertAlmostEqual(float(stats["social_follow_usage_per_alive_tick"]), 0.5)
        self.assertAlmostEqual(float(stats["social_influenced_share_last_tick"]), 0.5)
        self.assertAlmostEqual(float(stats["social_influenced_per_tick_total"]), 1.0)
        self.assertGreaterEqual(float(stats["social_flee_multiplier_avg_total"]), 1.0)

    def test_run_and_multi_summaries_include_social_impact(self) -> None:
        final_stats = {
            "proto_groups_top": [{"signature": "gA", "share": 0.42}],
            "creatures_by_fertility_zone": {"rich": 8, "neutral": 6, "poor": 2},
            "avg_speed": 1.02,
            "avg_metabolism": 0.97,
            "avg_prudence": 1.01,
            "avg_dominance": 1.06,
            "avg_repro_drive": 0.95,
            "total_food_memory_guided_moves": 10,
            "total_danger_memory_avoid_moves": 4,
            "food_memory_active_share": 0.3,
            "danger_memory_active_share": 0.2,
            "food_memory_effect_avg_distance_total": 1.1,
            "danger_memory_effect_avg_distance_total": 0.7,
            "food_memory_usage_per_tick_total": 0.4,
            "danger_memory_usage_per_tick_total": 0.2,
            "total_social_follow_moves": 14,
            "total_social_flee_boosted": 5,
            "social_influenced_creatures_last_tick": 3,
            "social_influenced_share_last_tick": 0.25,
            "social_influenced_per_tick_total": 1.4,
            "social_follow_usage_per_tick_total": 0.7,
            "social_flee_boost_usage_per_tick_total": 0.25,
            "avg_social_flee_multiplier_last_tick": 1.2,
            "social_flee_multiplier_avg_total": 1.15,
        }

        run_summary = build_final_run_summary(final_stats, create_proto_temporal_tracker())
        social = run_summary.get("social_impact")

        self.assertIsInstance(social, dict)
        assert isinstance(social, dict)
        self.assertEqual(int(social["follow_usage_total"]), 14)
        self.assertEqual(int(social["flee_boost_usage_total"]), 5)
        self.assertAlmostEqual(float(social["influenced_share_last_tick"]), 0.25)
        self.assertAlmostEqual(float(social["flee_multiplier_avg_total"]), 1.15)

        text_run = format_final_run_summary(run_summary)
        self.assertIn("social:", text_run)
        self.assertIn("part_infl_tick=", text_run)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 3,
                    "final_alive": 20,
                    "run_summary": run_summary,
                },
                {
                    "seed": 2,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 22,
                    "run_summary": {
                        "final_dominant_group_signature": "gB",
                        "avg_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "memory_impact": {
                            "food_usage_total": 2,
                            "danger_usage_total": 1,
                            "food_active_share": 0.1,
                            "danger_active_share": 0.1,
                            "food_effect_avg_distance": 0.5,
                            "danger_effect_avg_distance": 0.2,
                            "food_usage_per_tick": 0.1,
                            "danger_usage_per_tick": 0.05,
                        },
                        "social_impact": {
                            "follow_usage_total": 6,
                            "flee_boost_usage_total": 2,
                            "influenced_count_last_tick": 2,
                            "influenced_share_last_tick": 0.2,
                            "influenced_per_tick": 0.8,
                            "follow_usage_per_tick": 0.3,
                            "flee_boost_usage_per_tick": 0.1,
                            "flee_multiplier_avg_tick": 1.1,
                            "flee_multiplier_avg_total": 1.08,
                        },
                    },
                },
            ]
        )

        avg_social = multi_summary.get("avg_social_impact")
        self.assertIsInstance(avg_social, dict)
        assert isinstance(avg_social, dict)
        self.assertAlmostEqual(float(avg_social["follow_usage_total"]), 10.0)
        self.assertAlmostEqual(float(avg_social["flee_boost_usage_total"]), 3.5)
        self.assertAlmostEqual(float(avg_social["influenced_share_last_tick"]), 0.225)

        text_multi = format_multi_run_summary(multi_summary)
        self.assertIn("social_moy:", text_multi)
        self.assertIn("part_infl_tick=", text_multi)


if __name__ == "__main__":
    unittest.main()

