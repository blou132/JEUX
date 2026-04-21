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
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class CompetitionToleranceTraitTests(unittest.TestCase):
    def _run_single_creature(
        self, competition_tolerance: float, seed: int
    ) -> tuple[HungerSimulation, float, float]:
        subject = Creature(
            creature_id="subject",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(competition_tolerance=competition_tolerance, max_energy=100.0),
        )
        subject.remember_food_zone(3.0, 0.0, ttl=8.0)

        n1 = Creature(
            creature_id="n1",
            x=2.8,
            y=0.3,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        n2 = Creature(
            creature_id="n2",
            x=2.8,
            y=-0.3,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )

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

        before = subject.distance_to(3.0, 0.0)
        sim.tick(dt=1.0)
        after = subject.distance_to(3.0, 0.0)
        return sim, before, after

    def test_competition_tolerance_influences_food_zone_competition_behavior(self) -> None:
        sim_stay, before_stay, after_stay = self._run_single_creature(1.15, seed=3)
        sim_avoid, before_avoid, after_avoid = self._run_single_creature(0.85, seed=3)

        self.assertEqual(sim_stay.last_intents["subject"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_avoid.last_intents["subject"].action, HungerAI.ACTION_WANDER)

        self.assertEqual(sim_stay.competition_tolerance_guided_moves_last_tick, 1)
        self.assertEqual(sim_stay.competition_tolerance_stay_moves_last_tick, 1)
        self.assertEqual(sim_avoid.competition_tolerance_guided_moves_last_tick, 1)
        self.assertEqual(sim_avoid.competition_tolerance_avoid_moves_last_tick, 1)

        self.assertLess(after_stay, before_stay)
        self.assertGreater(after_avoid, before_avoid)

    def test_competition_tolerance_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(competition_tolerance=0.9)
        parent_b = GeneticTraits(competition_tolerance=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.competition_tolerance, 1.1)

    def test_competition_tolerance_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        high = Creature(
            creature_id="high",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(competition_tolerance=1.15, max_energy=100.0),
        )
        low = Creature(
            creature_id="low",
            x=0.5,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(competition_tolerance=0.85, max_energy=100.0),
        )
        high.remember_food_zone(3.0, 0.0, ttl=8.0)
        low.remember_food_zone(3.0, 0.0, ttl=8.0)

        n1 = Creature(
            creature_id="n1",
            x=2.8,
            y=0.3,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        n2 = Creature(
            creature_id="n2",
            x=2.8,
            y=-0.3,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[high, low, n1, n2],
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
            random_source=random.Random(87),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_competition_tolerance", stats)
        self.assertIn("std_competition_tolerance", stats)
        self.assertIn("competition_tolerance_guided_moves_last_tick", stats)
        self.assertIn("competition_tolerance_stay_moves_last_tick", stats)
        self.assertIn("competition_tolerance_avoid_moves_last_tick", stats)
        self.assertIn("competition_tolerance_stay_usage_bias_tick", stats)
        self.assertIn("competition_tolerance_avoid_usage_bias_tick", stats)
        self.assertIn("competition_tolerance_stay_share_last_tick", stats)
        self.assertIn("avg_competition_tolerance_neighbor_count_last_tick", stats)
        self.assertIn("avg_competition_tolerance_anchor_distance_delta_last_tick", stats)

        self.assertGreater(float(stats["std_competition_tolerance"]), 0.0)
        self.assertGreater(int(stats["competition_tolerance_guided_moves_last_tick"]), 0)
        self.assertGreater(int(stats["competition_tolerance_stay_moves_last_tick"]), 0)
        self.assertGreater(int(stats["competition_tolerance_avoid_moves_last_tick"]), 0)

        row = snapshot["creatures"][0]
        self.assertIn("competition_tolerance", row["traits"])

    def test_competition_tolerance_is_visible_in_run_and_multi_summaries(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_competition_tolerance": 1.02,
            "std_competition_tolerance": 0.06,
            "competition_tolerance_guided_usage_bias_total": 0.03,
            "total_competition_tolerance_guided_moves": 12,
            "total_competition_tolerance_stay_moves": 7,
            "total_competition_tolerance_avoid_moves": 5,
            "competition_tolerance_stay_usage_per_tick_total": 0.21,
            "competition_tolerance_avoid_usage_per_tick_total": 0.15,
            "competition_tolerance_stay_share_total": 0.583333,
            "competition_tolerance_avoid_share_total": 0.416667,
            "competition_tolerance_stay_users_avg_total": 1.07,
            "competition_tolerance_stay_usage_bias_total": 0.05,
            "competition_tolerance_avoid_users_avg_total": 0.94,
            "competition_tolerance_avoid_usage_bias_total": -0.08,
            "avg_competition_tolerance_neighbor_count_total": 2.3,
            "avg_competition_tolerance_anchor_distance_delta_total": -0.04,
        }

        run_summary = build_final_run_summary(final_stats, tracker)
        impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(impact["competition_tolerance_mean"]), 1.02)
        self.assertAlmostEqual(float(impact["competition_tolerance_std"]), 0.06)
        self.assertAlmostEqual(float(impact["competition_tolerance_guided_bias"]), 0.03)
        self.assertEqual(int(impact["competition_tolerance_guided_total"]), 12)
        self.assertEqual(int(impact["competition_tolerance_stay_total"]), 7)
        self.assertEqual(int(impact["competition_tolerance_avoid_total"]), 5)
        self.assertAlmostEqual(float(impact["competition_tolerance_stay_share"]), 0.583333)
        self.assertAlmostEqual(float(impact["competition_tolerance_avoid_share"]), 0.416667)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 3,
                    "final_alive": 8,
                    "run_summary": run_summary,
                },
                {
                    "seed": 2,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 9,
                    "run_summary": {
                        **run_summary,
                        "trait_impact": {
                            **impact,
                            "competition_tolerance_mean": 0.98,
                            "competition_tolerance_guided_bias": -0.01,
                            "competition_tolerance_stay_share": 0.5,
                            "competition_tolerance_stay_users_avg": 1.01,
                            "competition_tolerance_stay_usage_bias": 0.02,
                            "competition_tolerance_avoid_users_avg": 0.97,
                            "competition_tolerance_avoid_usage_bias": -0.01,
                        },
                    },
                },
            ]
        )

        avg_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_guided_bias"]), 0.01)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_stay_share"]), 0.5416665)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_stay_users_avg"]), 1.04)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_stay_usage_bias"]), 0.035)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_avoid_users_avg"]), 0.955)
        self.assertAlmostEqual(float(avg_impact["competition_tolerance_avoid_usage_bias"]), -0.045)


if __name__ == "__main__":
    unittest.main()
