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


class GregariousnessTraitTests(unittest.TestCase):
    def _run_single_creature(self, gregariousness: float, seed: int) -> tuple[HungerSimulation, float, float]:
        subject = Creature(
            creature_id="subject",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(gregariousness=gregariousness, max_energy=100.0),
        )
        n1 = Creature(
            creature_id="n1",
            x=3.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        n2 = Creature(
            creature_id="n2",
            x=3.0,
            y=1.0,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        center_x = (n1.x + n2.x) / 2.0
        center_y = (n1.y + n2.y) / 2.0

        sim = HungerSimulation(
            creatures=[subject, n1, n2],
            food_field=FoodField(),
            ai_system=HungerAI(
                hunger_seek_threshold=0.6,
                food_detection_range=0.0,
                threat_detection_range=0.0,
            ),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            social_follow_strength=0.0,
            social_flee_boost_per_neighbor=0.0,
            random_source=random.Random(seed),
        )

        before = subject.distance_to(center_x, center_y)
        sim.tick(dt=1.0)
        after = subject.distance_to(center_x, center_y)
        return sim, before, after

    def test_gregariousness_influences_wander_by_local_creature_density(self) -> None:
        sim_seek, before_seek, after_seek = self._run_single_creature(1.3, seed=77)
        sim_avoid, before_avoid, after_avoid = self._run_single_creature(0.7, seed=77)

        self.assertEqual(sim_seek.last_intents["subject"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_avoid.last_intents["subject"].action, HungerAI.ACTION_WANDER)

        self.assertEqual(sim_seek.gregariousness_guided_moves_last_tick, 1)
        self.assertEqual(sim_seek.gregariousness_seek_moves_last_tick, 1)
        self.assertEqual(sim_avoid.gregariousness_guided_moves_last_tick, 1)
        self.assertEqual(sim_avoid.gregariousness_avoid_moves_last_tick, 1)

        self.assertLess(after_seek, before_seek)
        self.assertGreater(after_avoid, before_avoid)

    def test_gregariousness_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(gregariousness=0.9)
        parent_b = GeneticTraits(gregariousness=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.gregariousness, 1.1)

    def test_gregariousness_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        creatures = [
            Creature(
                creature_id="high",
                x=0.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(gregariousness=1.15, max_energy=100.0),
            ),
            Creature(
                creature_id="low",
                x=0.5,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(gregariousness=0.85, max_energy=100.0),
            ),
            Creature(
                creature_id="n1",
                x=2.8,
                y=0.4,
                energy=80.0,
                traits=GeneticTraits(max_energy=100.0),
            ),
            Creature(
                creature_id="n2",
                x=2.8,
                y=-0.4,
                energy=80.0,
                traits=GeneticTraits(max_energy=100.0),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(
                hunger_seek_threshold=0.6,
                food_detection_range=0.0,
                threat_detection_range=0.0,
            ),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            social_follow_strength=0.0,
            social_flee_boost_per_neighbor=0.0,
            random_source=random.Random(321),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_gregariousness", stats)
        self.assertIn("std_gregariousness", stats)
        self.assertIn("gregariousness_guided_moves_last_tick", stats)
        self.assertIn("gregariousness_seek_moves_last_tick", stats)
        self.assertIn("gregariousness_avoid_moves_last_tick", stats)
        self.assertIn("gregariousness_seek_usage_bias_tick", stats)
        self.assertIn("gregariousness_seek_usage_per_tick_total", stats)
        self.assertIn("gregariousness_avoid_usage_per_tick_total", stats)
        self.assertIn("gregariousness_avoid_share_last_tick", stats)
        self.assertIn("avg_gregariousness_neighbor_count_last_tick", stats)
        self.assertIn("avg_gregariousness_center_distance_delta_last_tick", stats)

        self.assertGreater(float(stats["std_gregariousness"]), 0.0)
        self.assertGreater(int(stats["gregariousness_guided_moves_last_tick"]), 0)
        self.assertGreater(int(stats["gregariousness_seek_moves_last_tick"]), 0)
        self.assertGreater(int(stats["gregariousness_avoid_moves_last_tick"]), 0)
        self.assertGreaterEqual(float(stats["gregariousness_avoid_share_last_tick"]), 0.0)
        self.assertLessEqual(float(stats["gregariousness_avoid_share_last_tick"]), 1.0)

        row = snapshot["creatures"][0]
        self.assertIn("gregariousness", row["traits"])

    def test_gregariousness_is_visible_in_run_and_multi_summaries(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_gregariousness": 1.03,
            "std_gregariousness": 0.08,
            "gregariousness_guided_usage_bias_total": 0.04,
            "total_gregariousness_guided_moves": 10,
            "total_gregariousness_seek_moves": 6,
            "total_gregariousness_avoid_moves": 4,
            "gregariousness_seek_usage_per_tick_total": 0.28,
            "gregariousness_avoid_usage_per_tick_total": 0.17,
            "gregariousness_seek_share_total": 0.6,
            "gregariousness_avoid_share_total": 0.4,
            "gregariousness_seek_users_avg_total": 1.07,
            "gregariousness_seek_usage_bias_total": 0.05,
            "gregariousness_avoid_users_avg_total": 0.94,
            "gregariousness_avoid_usage_bias_total": -0.09,
            "avg_gregariousness_neighbor_count_total": 2.2,
            "avg_gregariousness_center_distance_delta_total": -0.08,
        }

        run_summary = build_final_run_summary(final_stats, tracker)
        impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(impact["gregariousness_mean"]), 1.03)
        self.assertAlmostEqual(float(impact["gregariousness_std"]), 0.08)
        self.assertAlmostEqual(float(impact["gregariousness_guided_bias"]), 0.04)
        self.assertEqual(int(impact["gregariousness_guided_total"]), 10)
        self.assertEqual(int(impact["gregariousness_seek_total"]), 6)
        self.assertEqual(int(impact["gregariousness_avoid_total"]), 4)
        self.assertAlmostEqual(float(impact["gregariousness_seek_share"]), 0.6)
        self.assertAlmostEqual(float(impact["gregariousness_avoid_share"]), 0.4)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("gr_mu=", run_text)
        self.assertIn("gregarite:", run_text)

        multi_summary = build_multi_run_summary(
            [
                {"seed": 1, "extinct": False, "max_generation": 3, "final_alive": 8, "run_summary": run_summary},
                {
                    "seed": 2,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 9,
                    "run_summary": {
                        **run_summary,
                        "trait_impact": {
                            **impact,
                            "gregariousness_mean": 0.97,
                            "gregariousness_guided_bias": -0.02,
                            "gregariousness_seek_share": 0.45,
                            "gregariousness_seek_users_avg": 1.01,
                            "gregariousness_seek_usage_bias": 0.01,
                            "gregariousness_avoid_users_avg": 0.98,
                            "gregariousness_avoid_usage_bias": -0.02,
                        },
                    },
                },
            ]
        )

        avg_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_impact["gregariousness_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["gregariousness_guided_bias"]), 0.01)
        self.assertAlmostEqual(float(avg_impact["gregariousness_seek_share"]), 0.525)
        self.assertAlmostEqual(float(avg_impact["gregariousness_seek_users_avg"]), 1.04)
        self.assertAlmostEqual(float(avg_impact["gregariousness_seek_usage_bias"]), 0.03)
        self.assertAlmostEqual(float(avg_impact["gregariousness_avoid_users_avg"]), 0.96)
        self.assertAlmostEqual(float(avg_impact["gregariousness_avoid_usage_bias"]), -0.055)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("gr_mu=", multi_text)
        self.assertIn("gregarite_moy:", multi_text)


if __name__ == "__main__":
    unittest.main()

