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


class LongevityTraitTests(unittest.TestCase):
    def test_longevity_factor_modulates_age_wear_drain(self) -> None:
        high_longevity = Creature(
            creature_id="high",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=1.0,
                longevity_factor=1.15,
                max_energy=100.0,
            ),
        )
        high_longevity.age = 30.0

        low_longevity = Creature(
            creature_id="low",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=1.0,
                longevity_factor=0.85,
                max_energy=100.0,
            ),
        )
        low_longevity.age = 30.0

        sim = HungerSimulation(
            creatures=[high_longevity, low_longevity],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(1001),
        )

        sim.tick(dt=1.0)

        high_expected = 100.0 - (
            10.0 * HungerSimulation._compute_age_wear_multiplier(high_longevity)
        )
        low_expected = 100.0 - (
            10.0 * HungerSimulation._compute_age_wear_multiplier(low_longevity)
        )
        self.assertAlmostEqual(high_longevity.energy, high_expected, places=3)
        self.assertAlmostEqual(low_longevity.energy, low_expected, places=3)
        self.assertGreater(high_longevity.energy, low_longevity.energy)
        self.assertGreaterEqual(sim.age_wear_active_events_last_tick, 1)

    def test_longevity_trait_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(longevity_factor=1.1)
        parent_b = GeneticTraits(longevity_factor=0.9)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.longevity_factor, 1.1)

    def test_longevity_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        slow_aging = Creature(
            creature_id="slow",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(longevity_factor=1.15, max_energy=100.0),
        )
        slow_aging.age = 10.0

        fast_aging = Creature(
            creature_id="fast",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(longevity_factor=0.85, max_energy=100.0),
        )
        fast_aging.age = 30.0

        sim = HungerSimulation(
            creatures=[slow_aging, fast_aging],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(1002),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_longevity_factor", stats)
        self.assertIn("std_longevity_factor", stats)
        self.assertIn("age_wear_active_events_last_tick", stats)
        self.assertIn("avg_age_wear_multiplier_observed_last_tick", stats)
        self.assertIn("longevity_factor_age_wear_usage_bias_tick", stats)
        self.assertAlmostEqual(float(stats["avg_longevity_factor"]), 1.0)
        self.assertGreater(float(stats["std_longevity_factor"]), 0.0)
        self.assertGreaterEqual(int(stats["age_wear_active_events_last_tick"]), 1)
        self.assertGreater(float(stats["avg_age_wear_multiplier_observed_last_tick"]), 1.0)
        self.assertLess(float(stats["longevity_factor_age_wear_usage_bias_tick"]), 0.0)

        creature_row = snapshot["creatures"][0]
        self.assertIn("longevity_factor", creature_row["traits"])

    def test_run_summaries_include_longevity_impact_metrics(self) -> None:
        final_stats = {
            "avg_longevity_factor": 1.03,
            "std_longevity_factor": 0.07,
            "age_wear_usage_per_tick_total": 0.25,
            "avg_age_wear_multiplier_observed_total": 1.12,
            "longevity_factor_age_wear_usage_bias_total": -0.04,
        }
        tracker = create_proto_temporal_tracker()

        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(trait_impact["longevity_factor_mean"]), 1.03)
        self.assertAlmostEqual(float(trait_impact["longevity_factor_std"]), 0.07)
        self.assertAlmostEqual(float(trait_impact["age_wear_usage_per_tick"]), 0.25)
        self.assertAlmostEqual(float(trait_impact["age_wear_multiplier_observed"]), 1.12)
        self.assertAlmostEqual(float(trait_impact["longevity_factor_age_wear_bias"]), -0.04)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("lg_mu=", run_text)
        self.assertIn("agewear_freq=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 3,
                    "final_alive": 9,
                    "run_summary": run_summary,
                }
            ]
        )
        avg_trait_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_trait_impact["longevity_factor_mean"]), 1.03)
        self.assertAlmostEqual(float(avg_trait_impact["age_wear_usage_per_tick"]), 0.25)
        self.assertAlmostEqual(float(avg_trait_impact["age_wear_multiplier_observed"]), 1.12)
        self.assertAlmostEqual(float(avg_trait_impact["longevity_factor_age_wear_bias"]), -0.04)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("lg_mu=", multi_text)
        self.assertIn("agewear_freq=", multi_text)


if __name__ == "__main__":
    unittest.main()

