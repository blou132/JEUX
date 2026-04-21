import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import (
    build_final_run_summary,
    build_hunger_snapshot,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from genetics import GeneticTraits, inherit_traits
from simulation import HungerSimulation
from ui import format_final_run_summary, format_multi_run_summary
from world import FoodField, FoodSource


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class MobilityEfficiencyTraitTests(unittest.TestCase):
    def test_mobility_efficiency_lightly_modulates_movement_distance(self) -> None:
        faster = Creature(
            creature_id="fast",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(mobility_efficiency=1.1, max_energy=100.0),
        )
        slower = Creature(
            creature_id="slow",
            x=0.0,
            y=3.0,
            energy=10.0,
            traits=GeneticTraits(mobility_efficiency=0.9, max_energy=100.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=20.0, y=0.0, energy_value=20.0))
        field.add_food(FoodSource(food_id="f2", x=20.0, y=3.0, energy_value=20.0))

        sim = HungerSimulation(
            creatures=[faster, slower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=30.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            random_source=random.Random(1401),
        )
        sim.tick(dt=1.0)

        faster_distance = faster.distance_to(20.0, 0.0)
        slower_distance = slower.distance_to(20.0, 3.0)
        self.assertLess(faster_distance, slower_distance)

    def test_mobility_efficiency_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(mobility_efficiency=1.05)
        parent_b = GeneticTraits(mobility_efficiency=0.95)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.mobility_efficiency, 1.1)

    def test_mobility_efficiency_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        faster = Creature(
            creature_id="fast",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(mobility_efficiency=1.1, max_energy=100.0),
        )
        slower = Creature(
            creature_id="slow",
            x=0.0,
            y=3.0,
            energy=10.0,
            traits=GeneticTraits(mobility_efficiency=0.9, max_energy=100.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=20.0, y=0.0, energy_value=20.0))
        field.add_food(FoodSource(food_id="f2", x=20.0, y=3.0, energy_value=20.0))

        sim = HungerSimulation(
            creatures=[faster, slower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=30.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            random_source=random.Random(1402),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_mobility_efficiency", stats)
        self.assertIn("std_mobility_efficiency", stats)
        self.assertIn("movement_actions_last_tick", stats)
        self.assertIn("avg_movement_multiplier_observed_last_tick", stats)
        self.assertIn("avg_movement_distance_observed_last_tick", stats)
        self.assertIn("avg_movement_distance_observed_total", stats)
        self.assertIn("mobility_efficiency_movement_usage_bias_tick", stats)
        self.assertGreater(float(stats["std_mobility_efficiency"]), 0.0)
        self.assertGreater(int(stats["movement_actions_last_tick"]), 0)
        self.assertGreater(float(stats["avg_movement_distance_observed_last_tick"]), 0.0)

        creature_row = snapshot["creatures"][0]
        self.assertIn("mobility_efficiency", creature_row["traits"])

    def test_run_and_multi_summaries_include_mobility_efficiency_impact(self) -> None:
        final_stats = {
            "avg_mobility_efficiency": 1.03,
            "std_mobility_efficiency": 0.04,
            "mobility_efficiency_movement_usage_bias_total": 0.02,
            "avg_movement_multiplier_observed_total": 1.02,
            "avg_movement_distance_observed_total": 1.35,
            "movement_usage_per_tick_total": 5.5,
        }

        tracker = create_proto_temporal_tracker()
        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]

        self.assertAlmostEqual(float(trait_impact["mobility_efficiency_mean"]), 1.03)
        self.assertAlmostEqual(float(trait_impact["mobility_efficiency_std"]), 0.04)
        self.assertAlmostEqual(float(trait_impact["mobility_efficiency_movement_bias"]), 0.02)
        self.assertAlmostEqual(float(trait_impact["movement_multiplier_observed"]), 1.02)
        self.assertAlmostEqual(float(trait_impact["movement_distance_observed"]), 1.35)
        self.assertAlmostEqual(float(trait_impact["movement_usage_per_tick"]), 5.5)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("mo_mu=", run_text)
        self.assertIn("move_mult=", run_text)
        self.assertIn("move_dist=", run_text)
        self.assertIn("bias_mo_move=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 3,
                    "final_alive": 10,
                    "run_summary": run_summary,
                }
            ]
        )
        avg_trait_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_trait_impact["mobility_efficiency_mean"]), 1.03)
        self.assertAlmostEqual(float(avg_trait_impact["movement_multiplier_observed"]), 1.02)
        self.assertAlmostEqual(float(avg_trait_impact["movement_distance_observed"]), 1.35)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("mo_mu=", multi_text)
        self.assertIn("move_mult=", multi_text)
        self.assertIn("move_dist=", multi_text)
        self.assertIn("bias_mo_move=", multi_text)


if __name__ == "__main__":
    unittest.main()
