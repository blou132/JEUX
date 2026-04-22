import random
import unittest
from math import pi

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
from ui import format_final_run_summary, format_multi_run_summary, format_population_dynamics
from world import FoodField


class FixedAngleRandom:
    def __init__(self, angle: float) -> None:
        self.angle = angle

    def uniform(self, a: float, b: float) -> float:
        if abs(a) < 1e-12 and abs(b - (2.0 * pi)) < 1e-12:
            return self.angle
        return random.Random(0).uniform(a, b)


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class ResourceCommitmentTraitTests(unittest.TestCase):
    def _run_single_creature(
        self,
        resource_commitment: float,
    ) -> tuple[HungerSimulation, Creature]:
        creature = Creature(
            creature_id="c",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(resource_commitment=resource_commitment, max_energy=100.0),
        )
        creature.remember_food_zone(0.0, 3.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[creature],
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
            random_source=FixedAngleRandom(0.0),
        )

        sim.tick(dt=1.0)
        return sim, creature

    def test_resource_commitment_influences_local_resource_direction(self) -> None:
        sim_stay, creature_stay = self._run_single_creature(1.15)
        sim_switch, creature_switch = self._run_single_creature(0.85)

        self.assertEqual(sim_stay.last_intents["c"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_switch.last_intents["c"].action, HungerAI.ACTION_WANDER)

        self.assertEqual(sim_stay.resource_commitment_guided_moves_last_tick, 1)
        self.assertEqual(sim_switch.resource_commitment_guided_moves_last_tick, 1)
        self.assertEqual(sim_stay.resource_commitment_stay_moves_last_tick, 1)
        self.assertEqual(sim_switch.resource_commitment_switch_moves_last_tick, 1)

        self.assertGreater(creature_stay.y, 0.0)
        self.assertLess(creature_switch.y, 0.0)

    def test_resource_commitment_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(resource_commitment=0.9)
        parent_b = GeneticTraits(resource_commitment=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.resource_commitment, 1.1)

    def test_resource_commitment_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        c1 = Creature(
            creature_id="c1",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(resource_commitment=1.15, max_energy=100.0),
        )
        c2 = Creature(
            creature_id="c2",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(resource_commitment=0.85, max_energy=100.0),
        )
        c1.remember_food_zone(0.0, 3.0, ttl=8.0)
        c2.remember_food_zone(0.0, 3.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[c1, c2],
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
            random_source=FixedAngleRandom(0.0),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_resource_commitment", stats)
        self.assertIn("std_resource_commitment", stats)
        self.assertIn("resource_commitment_guided_moves_last_tick", stats)
        self.assertIn("resource_commitment_stay_moves_last_tick", stats)
        self.assertIn("resource_commitment_switch_moves_last_tick", stats)
        self.assertIn("resource_commitment_stay_usage_bias_tick", stats)
        self.assertIn("resource_commitment_switch_usage_bias_tick", stats)
        self.assertIn("resource_commitment_memory_usage_bias_tick", stats)
        self.assertIn("resource_commitment_recall_multiplier_avg_last_tick", stats)
        self.assertIn("avg_resource_commitment_anchor_distance_delta_last_tick", stats)

        self.assertGreater(float(stats["std_resource_commitment"]), 0.0)
        self.assertEqual(int(stats["resource_commitment_guided_moves_last_tick"]), 2)
        self.assertEqual(int(stats["resource_commitment_stay_moves_last_tick"]), 1)
        self.assertEqual(int(stats["resource_commitment_switch_moves_last_tick"]), 1)

        row = snapshot["creatures"][0]
        self.assertIn("resource_commitment", row["traits"])

        dynamics_text = format_population_dynamics(stats)
        self.assertIn("resource_commitment_tick:", dynamics_text)
        self.assertIn("resource_commitment_log:", dynamics_text)
        self.assertIn("rc_bias=", dynamics_text)
        self.assertIn("recall_rc=", dynamics_text)

    def test_resource_commitment_is_visible_in_run_and_multi_summaries(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_resource_commitment": 1.01,
            "std_resource_commitment": 0.07,
            "resource_commitment_guided_usage_bias_total": 0.02,
            "total_resource_commitment_guided_moves": 12,
            "total_resource_commitment_stay_moves": 7,
            "total_resource_commitment_switch_moves": 5,
            "resource_commitment_stay_usage_per_tick_total": 0.22,
            "resource_commitment_switch_usage_per_tick_total": 0.16,
            "resource_commitment_stay_share_total": 0.583333,
            "resource_commitment_switch_share_total": 0.416667,
            "resource_commitment_stay_users_avg_total": 1.06,
            "resource_commitment_stay_usage_bias_total": 0.05,
            "resource_commitment_switch_users_avg_total": 0.94,
            "resource_commitment_switch_usage_bias_total": -0.07,
            "avg_resource_commitment_anchor_distance_delta_total": -0.06,
            "resource_commitment_memory_usage_bias_total": 0.03,
            "resource_commitment_recall_multiplier_avg_total": 1.04,
        }

        run_summary = build_final_run_summary(final_stats, tracker)
        self.assertIn("resource_commitment", run_summary["avg_traits"])
        self.assertAlmostEqual(float(run_summary["avg_traits"]["resource_commitment"]), 1.01)

        impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(impact["resource_commitment_mean"]), 1.01)
        self.assertAlmostEqual(float(impact["resource_commitment_std"]), 0.07)
        self.assertAlmostEqual(float(impact["resource_commitment_guided_bias"]), 0.02)
        self.assertEqual(int(impact["resource_commitment_guided_total"]), 12)
        self.assertEqual(int(impact["resource_commitment_stay_total"]), 7)
        self.assertEqual(int(impact["resource_commitment_switch_total"]), 5)
        self.assertAlmostEqual(float(impact["resource_commitment_stay_share"]), 0.583333)
        self.assertAlmostEqual(float(impact["resource_commitment_switch_share"]), 0.416667)
        self.assertAlmostEqual(float(impact["resource_commitment_memory_bias"]), 0.03)
        self.assertAlmostEqual(float(impact["resource_commitment_recall_multiplier_observed"]), 1.04)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("rc=", run_text)
        self.assertIn("rc_mu=", run_text)
        self.assertIn("resource_commitment:", run_text)
        self.assertIn("recall_rc=", run_text)

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
                        "avg_traits": {
                            **run_summary["avg_traits"],
                            "resource_commitment": 0.99,
                        },
                        "trait_impact": {
                            **impact,
                            "resource_commitment_mean": 0.99,
                            "resource_commitment_guided_bias": -0.01,
                            "resource_commitment_stay_share": 0.5,
                            "resource_commitment_stay_users_avg": 1.01,
                            "resource_commitment_stay_usage_bias": 0.02,
                            "resource_commitment_switch_users_avg": 0.97,
                            "resource_commitment_switch_usage_bias": -0.02,
                            "resource_commitment_memory_bias": -0.01,
                            "resource_commitment_recall_multiplier_observed": 0.98,
                        },
                    },
                },
            ]
        )

        self.assertAlmostEqual(float(multi_summary["avg_final_traits"]["resource_commitment"]), 1.0)
        avg_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_impact["resource_commitment_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_guided_bias"]), 0.005)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_stay_share"]), 0.5416665)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_stay_users_avg"]), 1.035)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_stay_usage_bias"]), 0.035)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_switch_users_avg"]), 0.955)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_switch_usage_bias"]), -0.045)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_memory_bias"]), 0.01)
        self.assertAlmostEqual(float(avg_impact["resource_commitment_recall_multiplier_observed"]), 1.01)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("rc=", multi_text)
        self.assertIn("rc_mu=", multi_text)
        self.assertIn("resource_commitment_moy:", multi_text)
        self.assertIn("recall_rc=", multi_text)


if __name__ == "__main__":
    unittest.main()
