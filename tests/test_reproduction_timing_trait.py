import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import (
    build_final_run_summary,
    build_hunger_snapshot,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from legacy_python.genetics import GeneticTraits, inherit_traits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_final_run_summary, format_multi_run_summary
from legacy_python.world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class ReproductionTimingTraitTests(unittest.TestCase):
    def test_reproduction_timing_lightly_modulates_reproduction_threshold(self) -> None:
        wait_more = Creature(
            creature_id="wait_more",
            x=0.0,
            y=0.0,
            energy=69.0,
            traits=GeneticTraits(reproduction_timing=1.15, max_energy=100.0),
            age=1.0,
        )
        early = Creature(
            creature_id="early",
            x=0.5,
            y=0.0,
            energy=69.0,
            traits=GeneticTraits(reproduction_timing=0.85, max_energy=100.0),
            age=1.0,
        )

        sim = HungerSimulation(
            creatures=[wait_more, early],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=70.0,
            reproduction_min_age=0.0,
            random_source=random.Random(1201),
        )

        self.assertFalse(sim._is_reproduction_eligible(wait_more))
        self.assertTrue(sim._is_reproduction_eligible(early))

    def test_reproduction_timing_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(reproduction_timing=1.1)
        parent_b = GeneticTraits(reproduction_timing=0.9)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.reproduction_timing, 1.1)

    def test_reproduction_timing_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        high_a = Creature(
            creature_id="ha",
            x=0.0,
            y=0.0,
            energy=120.0,
            traits=GeneticTraits(reproduction_timing=1.15, max_energy=150.0),
            age=1.0,
        )
        high_b = Creature(
            creature_id="hb",
            x=0.4,
            y=0.0,
            energy=120.0,
            traits=GeneticTraits(reproduction_timing=1.15, max_energy=150.0),
            age=1.0,
        )
        low = Creature(
            creature_id="low",
            x=10.0,
            y=10.0,
            energy=120.0,
            traits=GeneticTraits(reproduction_timing=0.85, max_energy=150.0),
            age=1.0,
        )

        sim = HungerSimulation(
            creatures=[high_a, high_b, low],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=100.0,
            reproduction_distance=1.0,
            reproduction_cost=5.0,
            random_source=random.Random(1202),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertEqual(sim.total_births, 1)
        self.assertIn("avg_reproduction_timing", stats)
        self.assertIn("std_reproduction_timing", stats)
        self.assertIn("avg_reproduction_timing_threshold_multiplier", stats)
        self.assertIn("reproduction_timing_reproduction_users_avg_tick", stats)
        self.assertIn("reproduction_timing_reproduction_usage_bias_tick", stats)
        self.assertIn("avg_reproduction_timing_threshold_multiplier_observed_last_tick", stats)
        self.assertGreater(float(stats["avg_reproduction_timing"]), 1.0)
        self.assertLess(float(stats["avg_reproduction_timing"]), 1.2)
        self.assertAlmostEqual(float(stats["reproduction_timing_reproduction_users_avg_tick"]), 1.15, places=3)
        self.assertGreater(float(stats["reproduction_timing_reproduction_usage_bias_tick"]), 0.0)
        self.assertAlmostEqual(
            float(stats["avg_reproduction_timing_threshold_multiplier_observed_last_tick"]),
            1.015,
            places=3,
        )

        creature_row = snapshot["creatures"][0]
        self.assertIn("reproduction_timing", creature_row["traits"])

    def test_run_summaries_include_reproduction_timing_impact_metrics(self) -> None:
        final_stats = {
            "avg_reproduction_timing": 1.03,
            "std_reproduction_timing": 0.05,
            "reproduction_timing_reproduction_usage_bias_total": 0.04,
            "avg_reproduction_timing_threshold_multiplier_observed_total": 0.986,
        }
        tracker = create_proto_temporal_tracker()

        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(trait_impact["reproduction_timing_mean"]), 1.03)
        self.assertAlmostEqual(float(trait_impact["reproduction_timing_std"]), 0.05)
        self.assertAlmostEqual(float(trait_impact["reproduction_timing_reproduction_bias"]), 0.04)
        self.assertAlmostEqual(
            float(trait_impact["reproduction_timing_threshold_multiplier_observed"]),
            0.986,
        )

        run_text = format_final_run_summary(run_summary)
        self.assertIn("rt_mu=", run_text)
        self.assertIn("bias_rt_repro=", run_text)
        self.assertIn("repro_timing_mult=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 12,
                    "run_summary": run_summary,
                }
            ]
        )
        avg_trait_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_trait_impact["reproduction_timing_mean"]), 1.03)
        self.assertAlmostEqual(
            float(avg_trait_impact["reproduction_timing_threshold_multiplier_observed"]),
            0.986,
        )

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("rt_mu=", multi_text)
        self.assertIn("bias_rt_repro=", multi_text)
        self.assertIn("repro_timing_mult=", multi_text)


if __name__ == "__main__":
    unittest.main()

