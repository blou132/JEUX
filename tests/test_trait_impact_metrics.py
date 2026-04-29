import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import build_final_run_summary, build_multi_run_summary, build_population_stats
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_final_run_summary, format_multi_run_summary
from legacy_python.world import FoodField, FoodSource


class TraitImpactMetricsTests(unittest.TestCase):
    def test_memory_focus_dispersion_and_usage_bias_are_visible(self) -> None:
        high_focus = Creature(
            creature_id="high_focus",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(memory_focus=1.3, social_sensitivity=1.0),
        )
        high_focus.remember_food_zone(6.0, 0.0, ttl=8.0)

        low_focus = Creature(
            creature_id="low_focus",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(memory_focus=0.7, social_sensitivity=1.0),
        )
        low_focus.remember_food_zone(6.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[high_focus, low_focus],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            food_memory_recall_distance=5.0,
            random_source=random.Random(301),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)

        self.assertGreater(float(stats["std_memory_focus"]), 0.0)
        self.assertGreater(float(stats["memory_focus_food_users_avg_tick"]), float(stats["avg_memory_focus"]))
        self.assertGreater(float(stats["memory_focus_food_usage_bias_tick"]), 0.0)

    def test_social_sensitivity_dispersion_and_usage_bias_are_visible(self) -> None:
        leader = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=1.0),
        )
        follower = Creature(
            creature_id="follower",
            x=0.0,
            y=3.3,
            energy=90.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=1.2),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))

        sim = HungerSimulation(
            creatures=[leader, follower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=3.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(302),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)

        self.assertGreater(float(stats["std_social_sensitivity"]), 0.0)
        self.assertGreater(
            float(stats["social_sensitivity_follow_users_avg_tick"]),
            float(stats["avg_social_sensitivity"]),
        )
        self.assertGreater(float(stats["social_sensitivity_follow_usage_bias_tick"]), 0.0)

    def test_run_and_multi_summaries_include_trait_impact(self) -> None:
        final_stats = {
            "proto_groups_top": [{"signature": "gA", "share": 0.5}],
            "creatures_by_fertility_zone": {"rich": 4, "neutral": 3, "poor": 1},
            "avg_speed": 1.0,
            "avg_metabolism": 1.0,
            "avg_prudence": 1.0,
            "avg_dominance": 1.0,
            "avg_repro_drive": 1.0,
            "avg_memory_focus": 1.04,
            "std_memory_focus": 0.12,
            "avg_social_sensitivity": 0.97,
            "std_social_sensitivity": 0.10,
            "memory_focus_food_usage_bias_total": 0.08,
            "memory_focus_danger_usage_bias_total": 0.02,
            "social_sensitivity_follow_usage_bias_total": 0.07,
            "social_sensitivity_flee_boost_usage_bias_total": 0.03,
            "total_food_memory_guided_moves": 9,
            "total_danger_memory_avoid_moves": 4,
            "food_memory_active_share": 0.35,
            "danger_memory_active_share": 0.2,
            "food_memory_effect_avg_distance_total": 1.2,
            "danger_memory_effect_avg_distance_total": 0.7,
            "food_memory_usage_per_tick_total": 0.4,
            "danger_memory_usage_per_tick_total": 0.15,
            "total_social_follow_moves": 8,
            "total_social_flee_boosted": 3,
            "social_influenced_creatures_last_tick": 2,
            "social_influenced_share_last_tick": 0.25,
            "social_influenced_per_tick_total": 0.6,
            "social_follow_usage_per_tick_total": 0.4,
            "social_flee_boost_usage_per_tick_total": 0.15,
            "avg_social_flee_multiplier_last_tick": 1.2,
            "social_flee_multiplier_avg_total": 1.1,
        }

        run_summary = build_final_run_summary(final_stats, {"observations": 3, "by_signature": {}})
        trait_impact = run_summary.get("trait_impact")

        self.assertIsInstance(trait_impact, dict)
        assert isinstance(trait_impact, dict)
        self.assertAlmostEqual(float(trait_impact["memory_focus_mean"]), 1.04)
        self.assertAlmostEqual(float(trait_impact["memory_focus_std"]), 0.12)
        self.assertAlmostEqual(float(trait_impact["social_sensitivity_mean"]), 0.97)
        self.assertAlmostEqual(float(trait_impact["social_sensitivity_std"]), 0.10)
        self.assertAlmostEqual(float(trait_impact["memory_focus_food_bias"]), 0.08)
        self.assertAlmostEqual(float(trait_impact["social_sensitivity_follow_bias"]), 0.07)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("traits_impact:", run_text)

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
                            "memory_focus_mean": 0.96,
                            "memory_focus_std": 0.08,
                            "social_sensitivity_mean": 1.03,
                            "social_sensitivity_std": 0.11,
                            "memory_focus_food_bias": -0.02,
                            "memory_focus_danger_bias": 0.01,
                            "social_sensitivity_follow_bias": -0.03,
                            "social_sensitivity_flee_boost_bias": 0.00,
                        },
                    },
                },
            ]
        )

        avg_trait_impact = multi_summary.get("avg_trait_impact")
        self.assertIsInstance(avg_trait_impact, dict)
        assert isinstance(avg_trait_impact, dict)
        self.assertAlmostEqual(float(avg_trait_impact["memory_focus_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_trait_impact["social_sensitivity_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_trait_impact["memory_focus_food_bias"]), 0.03)
        self.assertAlmostEqual(float(avg_trait_impact["social_sensitivity_follow_bias"]), 0.02)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("traits_impact_moy:", multi_text)


if __name__ == "__main__":
    unittest.main()

