import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import build_final_run_summary, build_multi_run_summary, build_population_stats
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_final_run_summary, format_multi_run_summary
from legacy_python.world import FoodField, FoodSource


class PerceptionImpactMetricsTests(unittest.TestCase):
    def test_food_perception_usage_bias_is_visible_in_stats(self) -> None:
        high = Creature(
            creature_id="high_food_perception",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(food_perception=1.2, threat_perception=1.0),
        )
        low = Creature(
            creature_id="low_food_perception",
            x=10.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(food_perception=0.8, threat_perception=1.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="food", x=0.0, y=0.0, energy_value=40.0))

        sim = HungerSimulation(
            creatures=[high, low],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=5.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(401),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)

        self.assertGreater(int(stats["food_detection_moves_last_tick"]), 0)
        self.assertGreater(int(stats["food_consumptions_last_tick"]), 0)
        self.assertGreater(float(stats["food_perception_detection_users_avg_tick"]), float(stats["avg_food_perception"]))
        self.assertGreater(float(stats["food_perception_detection_usage_bias_tick"]), 0.0)
        self.assertGreater(float(stats["food_perception_consumption_users_avg_tick"]), float(stats["avg_food_perception"]))
        self.assertGreater(float(stats["food_perception_consumption_usage_bias_tick"]), 0.0)

    def test_threat_perception_usage_bias_is_visible_in_stats(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.3, max_energy=120.0),
        )
        high = Creature(
            creature_id="high_threat_perception",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(food_perception=1.0, threat_perception=1.3),
        )
        low = Creature(
            creature_id="low_threat_perception",
            x=0.0,
            y=2.0,
            energy=90.0,
            traits=GeneticTraits(food_perception=1.0, threat_perception=0.7),
        )

        sim = HungerSimulation(
            creatures=[high, low, predator],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=5.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(402),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)

        self.assertGreater(int(stats["threat_detection_flee_last_tick"]), 0)
        self.assertGreater(float(stats["threat_perception_flee_users_avg_tick"]), float(stats["avg_threat_perception"]))
        self.assertGreater(float(stats["threat_perception_flee_usage_bias_tick"]), 0.0)

    def test_run_and_multi_summaries_include_perception_impact(self) -> None:
        final_stats = {
            "proto_groups_top": [{"signature": "gA", "share": 0.5}],
            "creatures_by_fertility_zone": {"rich": 4, "neutral": 3, "poor": 1},
            "avg_speed": 1.0,
            "avg_metabolism": 1.0,
            "avg_prudence": 1.0,
            "avg_dominance": 1.0,
            "avg_repro_drive": 1.0,
            "avg_memory_focus": 1.0,
            "std_memory_focus": 0.1,
            "avg_social_sensitivity": 1.0,
            "std_social_sensitivity": 0.1,
            "avg_food_perception": 1.05,
            "std_food_perception": 0.08,
            "avg_threat_perception": 0.95,
            "std_threat_perception": 0.07,
            "memory_focus_food_usage_bias_total": 0.02,
            "memory_focus_danger_usage_bias_total": 0.01,
            "social_sensitivity_follow_usage_bias_total": 0.03,
            "social_sensitivity_flee_boost_usage_bias_total": 0.01,
            "food_perception_detection_usage_bias_total": 0.06,
            "food_perception_consumption_usage_bias_total": 0.04,
            "threat_perception_flee_usage_bias_total": 0.05,
            "total_food_memory_guided_moves": 0,
            "total_danger_memory_avoid_moves": 0,
            "food_memory_active_share": 0.0,
            "danger_memory_active_share": 0.0,
            "food_memory_effect_avg_distance_total": 0.0,
            "danger_memory_effect_avg_distance_total": 0.0,
            "food_memory_usage_per_tick_total": 0.0,
            "danger_memory_usage_per_tick_total": 0.0,
            "total_social_follow_moves": 0,
            "total_social_flee_boosted": 0,
            "social_influenced_creatures_last_tick": 0,
            "social_influenced_share_last_tick": 0.0,
            "social_influenced_per_tick_total": 0.0,
            "social_follow_usage_per_tick_total": 0.0,
            "social_flee_boost_usage_per_tick_total": 0.0,
            "avg_social_flee_multiplier_last_tick": 1.0,
            "social_flee_multiplier_avg_total": 1.0,
        }

        run_summary = build_final_run_summary(final_stats, {"observations": 3, "by_signature": {}})
        impact = run_summary.get("trait_impact")

        self.assertIsInstance(impact, dict)
        assert isinstance(impact, dict)
        self.assertAlmostEqual(float(impact["food_perception_mean"]), 1.05)
        self.assertAlmostEqual(float(impact["threat_perception_mean"]), 0.95)
        self.assertAlmostEqual(float(impact["food_perception_detection_bias"]), 0.06)
        self.assertAlmostEqual(float(impact["food_perception_consumption_bias"]), 0.04)
        self.assertAlmostEqual(float(impact["threat_perception_flee_bias"]), 0.05)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("fp_mu=", run_text)
        self.assertIn("tp_mu=", run_text)
        self.assertIn("bias_fp_det=", run_text)
        self.assertIn("bias_tp_fuite=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 10,
                    "run_summary": run_summary,
                },
                {
                    "seed": 2,
                    "extinct": False,
                    "max_generation": 5,
                    "final_alive": 11,
                    "run_summary": {
                        **run_summary,
                        "trait_impact": {
                            **impact,
                            "food_perception_mean": 0.95,
                            "threat_perception_mean": 1.05,
                            "food_perception_detection_bias": -0.02,
                            "food_perception_consumption_bias": 0.00,
                            "threat_perception_flee_bias": -0.01,
                        },
                    },
                },
            ]
        )

        avg_impact = multi_summary.get("avg_trait_impact")
        self.assertIsInstance(avg_impact, dict)
        assert isinstance(avg_impact, dict)
        self.assertAlmostEqual(float(avg_impact["food_perception_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["threat_perception_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["food_perception_detection_bias"]), 0.02)
        self.assertAlmostEqual(float(avg_impact["threat_perception_flee_bias"]), 0.02)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("fp_mu=", multi_text)
        self.assertIn("tp_mu=", multi_text)
        self.assertIn("bias_fp_det=", multi_text)
        self.assertIn("bias_tp_fuite=", multi_text)


if __name__ == "__main__":
    unittest.main()

