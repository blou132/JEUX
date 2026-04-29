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


class ExplorationBiasTraitTests(unittest.TestCase):
    def _run_single_creature(self, exploration_bias: float, seed: int) -> tuple[HungerSimulation, float, float]:
        creature = Creature(
            creature_id="c",
            x=6.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(exploration_bias=exploration_bias, max_energy=100.0),
        )
        creature.remember_food_zone(0.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(seed),
        )

        before = creature.distance_to(0.0, 0.0)
        sim.tick(dt=1.0)
        after = creature.distance_to(0.0, 0.0)
        return sim, before, after

    def test_exploration_bias_influences_wander_around_food_anchor(self) -> None:
        sim_explore, before_explore, after_explore = self._run_single_creature(1.3, seed=77)
        sim_settle, before_settle, after_settle = self._run_single_creature(0.7, seed=77)

        self.assertEqual(sim_explore.last_intents["c"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_settle.last_intents["c"].action, HungerAI.ACTION_WANDER)

        self.assertEqual(sim_explore.exploration_bias_guided_moves_last_tick, 1)
        self.assertEqual(sim_settle.exploration_bias_guided_moves_last_tick, 1)
        self.assertEqual(sim_explore.exploration_bias_explore_moves_last_tick, 1)
        self.assertEqual(sim_settle.exploration_bias_settle_moves_last_tick, 1)

        delta_explore = after_explore - before_explore
        delta_settle = after_settle - before_settle
        self.assertGreater(delta_explore, delta_settle)

    def test_exploration_bias_is_visible_in_stats_and_snapshot(self) -> None:
        c1 = Creature(
            creature_id="c1",
            x=6.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(exploration_bias=1.2, max_energy=100.0),
        )
        c2 = Creature(
            creature_id="c2",
            x=5.0,
            y=2.0,
            energy=80.0,
            traits=GeneticTraits(exploration_bias=0.8, max_energy=100.0),
        )
        c1.remember_food_zone(0.0, 0.0, ttl=8.0)
        c2.remember_food_zone(0.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[c1, c2],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(78),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_exploration_bias", stats)
        self.assertIn("std_exploration_bias", stats)
        self.assertIn("exploration_bias_guided_moves_last_tick", stats)
        self.assertIn("exploration_bias_guided_usage_bias_tick", stats)
        self.assertIn("exploration_bias_explore_users_avg_tick", stats)
        self.assertIn("exploration_bias_explore_usage_bias_tick", stats)
        self.assertIn("exploration_bias_settle_users_avg_tick", stats)
        self.assertIn("exploration_bias_settle_usage_bias_tick", stats)
        self.assertIn("avg_exploration_bias_anchor_distance_delta_last_tick", stats)
        self.assertGreater(float(stats["std_exploration_bias"]), 0.0)
        self.assertGreater(int(stats["exploration_bias_guided_moves_last_tick"]), 0)

        self.assertIn("exploration_bias_guided_moves_last_tick", snapshot)
        self.assertIn("exploration_bias_explore_users_avg_last_tick", snapshot)
        self.assertIn("exploration_bias_settle_users_avg_last_tick", snapshot)
        creature_traits = snapshot["creatures"][0]["traits"]
        self.assertIn("exploration_bias", creature_traits)

    def test_exploration_bias_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(exploration_bias=0.9)
        parent_b = GeneticTraits(exploration_bias=1.1)

        child = inherit_traits(
            parent_a,
            parent_b,
            mutation_variation=0.1,
            rng=random.Random(77),
        )

        self.assertGreaterEqual(child.exploration_bias, 0.7)
        self.assertLessEqual(child.exploration_bias, 1.3)
        self.assertNotAlmostEqual(child.exploration_bias, 1.0, places=6)

    def test_exploration_bias_is_visible_in_run_and_multi_summaries(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_exploration_bias": 1.02,
            "std_exploration_bias": 0.09,
            "exploration_bias_guided_usage_bias_total": 0.04,
            "total_exploration_bias_guided_moves": 12,
            "exploration_bias_explore_share_total": 0.58,
            "exploration_bias_explore_users_avg_total": 1.08,
            "exploration_bias_explore_usage_bias_total": 0.06,
            "exploration_bias_settle_users_avg_total": 0.94,
            "exploration_bias_settle_usage_bias_total": -0.08,
            "avg_exploration_bias_anchor_distance_delta_total": 0.11,
        }

        run_summary = build_final_run_summary(final_stats, tracker)
        impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(impact["exploration_bias_mean"]), 1.02)
        self.assertAlmostEqual(float(impact["exploration_bias_std"]), 0.09)
        self.assertAlmostEqual(float(impact["exploration_bias_guided_bias"]), 0.04)
        self.assertEqual(int(impact["exploration_bias_guided_total"]), 12)
        self.assertAlmostEqual(float(impact["exploration_bias_explore_share"]), 0.58)
        self.assertAlmostEqual(float(impact["exploration_bias_explore_users_avg"]), 1.08)
        self.assertAlmostEqual(float(impact["exploration_bias_explore_usage_bias"]), 0.06)
        self.assertAlmostEqual(float(impact["exploration_bias_settle_users_avg"]), 0.94)
        self.assertAlmostEqual(float(impact["exploration_bias_settle_usage_bias"]), -0.08)
        self.assertAlmostEqual(float(impact["exploration_bias_anchor_distance_delta"]), 0.11)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("ex_mu=", run_text)
        self.assertIn("st_mu=", run_text)
        self.assertIn("exploration:", run_text)

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
                            "exploration_bias_mean": 0.98,
                            "exploration_bias_guided_bias": -0.02,
                            "exploration_bias_explore_share": 0.42,
                            "exploration_bias_explore_users_avg": 1.02,
                            "exploration_bias_explore_usage_bias": 0.03,
                            "exploration_bias_settle_users_avg": 0.97,
                            "exploration_bias_settle_usage_bias": -0.02,
                        },
                    },
                },
            ]
        )

        avg_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_impact["exploration_bias_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_guided_bias"]), 0.01)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_explore_share"]), 0.5)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_explore_users_avg"]), 1.05)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_explore_usage_bias"]), 0.045)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_settle_users_avg"]), 0.955)
        self.assertAlmostEqual(float(avg_impact["exploration_bias_settle_usage_bias"]), -0.05)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("ex_mu=", multi_text)
        self.assertIn("st_mu=", multi_text)
        self.assertIn("exploration_moy:", multi_text)


if __name__ == "__main__":
    unittest.main()

