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


class EnvironmentalToleranceTraitTests(unittest.TestCase):
    def test_environmental_tolerance_lightly_modulates_zone_drain(self) -> None:
        high_tol = Creature(
            creature_id="high",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=1.0,
                environmental_tolerance=1.15,
                max_energy=100.0,
            ),
        )
        low_tol = Creature(
            creature_id="low",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=1.0,
                environmental_tolerance=0.85,
                max_energy=100.0,
            ),
        )

        sim = HungerSimulation(
            creatures=[high_tol, low_tol],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=200.0,
            fertility_zone_getter=lambda _x, _y: "poor",
            random_source=random.Random(1101),
        )

        sim.tick(dt=1.0)

        high_expected = 100.0 - (10.0 * (1.0 - (0.20 * (1.15 - 1.0))))
        low_expected = 100.0 - (10.0 * (1.0 - (0.20 * (0.85 - 1.0))))
        self.assertAlmostEqual(high_tol.energy, high_expected, places=3)
        self.assertAlmostEqual(low_tol.energy, low_expected, places=3)
        self.assertGreater(high_tol.energy, low_tol.energy)

    def test_environmental_tolerance_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(environmental_tolerance=1.1)
        parent_b = GeneticTraits(environmental_tolerance=0.9)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.environmental_tolerance, 1.1)

    def test_environmental_tolerance_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        poor_tol = Creature(
            creature_id="poor_user",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(environmental_tolerance=1.15, max_energy=100.0),
        )
        rich_tol = Creature(
            creature_id="rich_user",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(environmental_tolerance=0.85, max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[poor_tol, rich_tol],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=8.0,
            reproduction_energy_threshold=200.0,
            fertility_zone_getter=lambda x, _y: "poor" if x < 0.5 else "rich",
            random_source=random.Random(1102),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_environmental_tolerance", stats)
        self.assertIn("std_environmental_tolerance", stats)
        self.assertIn("zone_drain_multiplier_avg_last_tick", stats)
        self.assertIn("poor_zone_drain_events_last_tick", stats)
        self.assertIn("rich_zone_drain_events_last_tick", stats)
        self.assertIn("environmental_tolerance_poor_usage_bias_tick", stats)
        self.assertIn("environmental_tolerance_rich_usage_bias_tick", stats)
        self.assertAlmostEqual(float(stats["avg_environmental_tolerance"]), 1.0)
        self.assertGreater(float(stats["std_environmental_tolerance"]), 0.0)
        self.assertGreaterEqual(int(stats["poor_zone_drain_events_last_tick"]), 1)
        self.assertGreaterEqual(int(stats["rich_zone_drain_events_last_tick"]), 1)
        self.assertGreater(float(stats["environmental_tolerance_poor_usage_bias_tick"]), 0.0)
        self.assertLess(float(stats["environmental_tolerance_rich_usage_bias_tick"]), 0.0)

        creature_row = snapshot["creatures"][0]
        self.assertIn("environmental_tolerance", creature_row["traits"])

    def test_run_summaries_include_environmental_tolerance_impact_metrics(self) -> None:
        final_stats = {
            "avg_environmental_tolerance": 1.02,
            "std_environmental_tolerance": 0.06,
            "zone_drain_multiplier_avg_total": 0.99,
            "poor_zone_drain_usage_per_tick_total": 1.4,
            "rich_zone_drain_usage_per_tick_total": 0.8,
            "environmental_tolerance_poor_users_avg_total": 1.08,
            "environmental_tolerance_poor_usage_bias_total": 0.06,
            "environmental_tolerance_rich_users_avg_total": 0.95,
            "environmental_tolerance_rich_usage_bias_total": -0.07,
        }
        tracker = create_proto_temporal_tracker()

        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(trait_impact["environmental_tolerance_mean"]), 1.02)
        self.assertAlmostEqual(float(trait_impact["environmental_tolerance_std"]), 0.06)
        self.assertAlmostEqual(float(trait_impact["zone_drain_multiplier_observed"]), 0.99)
        self.assertAlmostEqual(float(trait_impact["poor_zone_drain_usage_per_tick"]), 1.4)
        self.assertAlmostEqual(float(trait_impact["rich_zone_drain_usage_per_tick"]), 0.8)
        self.assertAlmostEqual(float(trait_impact["environmental_tolerance_poor_drain_bias"]), 0.06)
        self.assertAlmostEqual(float(trait_impact["environmental_tolerance_rich_drain_bias"]), -0.07)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("env_mu=", run_text)
        self.assertIn("env_obs:", run_text)

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
        self.assertAlmostEqual(float(avg_trait_impact["environmental_tolerance_mean"]), 1.02)
        self.assertAlmostEqual(float(avg_trait_impact["zone_drain_multiplier_observed"]), 0.99)
        self.assertAlmostEqual(float(avg_trait_impact["environmental_tolerance_poor_drain_bias"]), 0.06)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("env_mu=", multi_text)
        self.assertIn("env_obs_moy:", multi_text)


if __name__ == "__main__":
    unittest.main()

