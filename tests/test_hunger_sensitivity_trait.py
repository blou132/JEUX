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
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class HungerSensitivityTraitTests(unittest.TestCase):
    def test_hunger_sensitivity_modulates_food_search_trigger(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0)
        field = FoodField()

        early_search = Creature(
            creature_id="early_search",
            x=0.0,
            y=0.0,
            energy=40.0,
            traits=GeneticTraits(hunger_sensitivity=1.15, max_energy=100.0),
        )
        late_search = Creature(
            creature_id="late_search",
            x=1.0,
            y=0.0,
            energy=40.0,
            traits=GeneticTraits(hunger_sensitivity=0.85, max_energy=100.0),
        )

        early_intent = ai.decide(early_search, field, can_reproduce=False, nearby_creatures=[])
        late_intent = ai.decide(late_search, field, can_reproduce=False, nearby_creatures=[])

        self.assertEqual(early_intent.action, HungerAI.ACTION_SEARCH_FOOD)
        self.assertEqual(late_intent.action, HungerAI.ACTION_WANDER)

    def test_hunger_sensitivity_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(hunger_sensitivity=1.1)
        parent_b = GeneticTraits(hunger_sensitivity=0.9)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.hunger_sensitivity, 1.1)

    def test_hunger_sensitivity_metrics_are_visible_in_stats_and_snapshot(self) -> None:
        early = Creature(
            creature_id="early",
            x=0.0,
            y=0.0,
            energy=40.0,
            traits=GeneticTraits(hunger_sensitivity=1.15, max_energy=100.0),
        )
        late = Creature(
            creature_id="late",
            x=10.0,
            y=10.0,
            energy=40.0,
            traits=GeneticTraits(hunger_sensitivity=0.85, max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[early, late],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(1501),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_hunger_sensitivity", stats)
        self.assertIn("std_hunger_sensitivity", stats)
        self.assertIn("hunger_search_actions_last_tick", stats)
        self.assertIn("hunger_sensitivity_search_users_avg_tick", stats)
        self.assertIn("hunger_sensitivity_search_usage_bias_tick", stats)
        self.assertGreater(int(stats["hunger_search_actions_last_tick"]), 0)
        self.assertGreater(float(stats["hunger_sensitivity_search_usage_bias_tick"]), 0.0)
        self.assertEqual(snapshot["hunger_search_actions_last_tick"], int(stats["hunger_search_actions_last_tick"]))
        self.assertIn("hunger_sensitivity", snapshot["creatures"][0]["traits"])

    def test_run_summaries_include_hunger_sensitivity_impact_metrics(self) -> None:
        final_stats = {
            "avg_hunger_sensitivity": 1.02,
            "std_hunger_sensitivity": 0.04,
            "hunger_sensitivity_search_usage_bias_total": 0.05,
            "hunger_search_usage_per_tick_total": 0.42,
        }
        tracker = create_proto_temporal_tracker()

        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]
        self.assertAlmostEqual(float(trait_impact["hunger_sensitivity_mean"]), 1.02)
        self.assertAlmostEqual(float(trait_impact["hunger_sensitivity_std"]), 0.04)
        self.assertAlmostEqual(float(trait_impact["hunger_sensitivity_search_bias"]), 0.05)
        self.assertAlmostEqual(float(trait_impact["hunger_search_usage_per_tick"]), 0.42)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("hs_mu=", run_text)
        self.assertIn("bias_hs_search=", run_text)
        self.assertIn("faim_search_freq=", run_text)

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
        self.assertAlmostEqual(float(avg_trait_impact["hunger_sensitivity_mean"]), 1.02)
        self.assertAlmostEqual(float(avg_trait_impact["hunger_sensitivity_search_bias"]), 0.05)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("hs_mu=", multi_text)
        self.assertIn("bias_hs_search=", multi_text)
        self.assertIn("faim_search_freq=", multi_text)


if __name__ == "__main__":
    unittest.main()
