import random
import tempfile
import unittest
from pathlib import Path

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import (
    build_final_run_summary,
    build_hunger_snapshot,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from legacy_python.debug_tools.export_analysis import load_export_payload
from legacy_python.debug_tools.export_results import export_results
from legacy_python.genetics import GeneticTraits, inherit_traits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_final_run_summary, format_multi_run_summary
from legacy_python.world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class StressToleranceTraitTests(unittest.TestCase):
    def test_stress_tolerance_lightly_modulates_borderline_threat_reaction(self) -> None:
        ai = HungerAI(
            hunger_seek_threshold=0.6,
            threat_detection_range=10.0,
            threat_strength_ratio=1.15,
        )
        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(speed=1.18, max_energy=100.0),
        )
        low_stress = Creature(
            creature_id="low_stress",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(stress_tolerance=0.85, max_energy=100.0),
        )
        high_stress = Creature(
            creature_id="high_stress",
            x=0.0,
            y=1.0,
            energy=20.0,
            traits=GeneticTraits(stress_tolerance=1.15, max_energy=100.0),
        )

        low_intent = ai.decide(low_stress, FoodField(), nearby_creatures=[low_stress, high_stress, predator])
        high_intent = ai.decide(high_stress, FoodField(), nearby_creatures=[high_stress, low_stress, predator])

        self.assertEqual(low_intent.action, HungerAI.ACTION_FLEE)
        self.assertNotEqual(high_intent.action, HungerAI.ACTION_FLEE)

    def test_stress_tolerance_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(stress_tolerance=0.9)
        parent_b = GeneticTraits(stress_tolerance=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())
        self.assertAlmostEqual(child.stress_tolerance, 1.1)

    def test_stress_tolerance_is_visible_in_stats_and_snapshot(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(speed=1.18, max_energy=100.0),
        )
        low_stress = Creature(
            creature_id="low_stress",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(stress_tolerance=0.85, max_energy=100.0),
        )
        high_stress = Creature(
            creature_id="high_stress",
            x=0.0,
            y=1.0,
            energy=20.0,
            traits=GeneticTraits(stress_tolerance=1.15, max_energy=100.0),
        )

        simulation = HungerSimulation(
            creatures=[low_stress, high_stress, predator],
            food_field=FoodField(),
            ai_system=HungerAI(
                hunger_seek_threshold=0.6,
                threat_detection_range=10.0,
                threat_strength_ratio=1.15,
            ),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(1601),
        )

        simulation.tick(dt=1.0)
        stats = build_population_stats(simulation)
        snapshot = build_hunger_snapshot(simulation)

        self.assertIn("avg_stress_tolerance", stats)
        self.assertIn("std_stress_tolerance", stats)
        self.assertIn("stress_pressure_events_last_tick", stats)
        self.assertIn("stress_pressure_flee_events_last_tick", stats)
        self.assertIn("stress_tolerance_pressure_flee_usage_bias_tick", stats)

        self.assertGreater(float(stats["std_stress_tolerance"]), 0.0)
        self.assertGreater(int(stats["stress_pressure_events_last_tick"]), 0)
        self.assertGreater(int(stats["stress_pressure_flee_events_last_tick"]), 0)
        self.assertLess(float(stats["stress_tolerance_pressure_flee_usage_bias_tick"]), 0.0)

        creature_row = snapshot["creatures"][0]
        self.assertIn("stress_tolerance", creature_row["traits"])
        self.assertIn("stress_pressure_events_last_tick", snapshot)
        self.assertIn("stress_pressure_flee_events_last_tick", snapshot)

    def test_run_and_multi_summaries_include_stress_tolerance_impact(self) -> None:
        final_stats = {
            "avg_stress_tolerance": 1.02,
            "std_stress_tolerance": 0.05,
            "total_stress_pressure_events": 8,
            "total_stress_pressure_flee_events": 3,
            "stress_pressure_flee_rate_total": 0.375,
            "stress_tolerance_pressure_users_avg_total": 1.01,
            "stress_tolerance_pressure_flee_users_avg_total": 0.94,
            "stress_tolerance_pressure_flee_usage_bias_total": -0.07,
        }

        tracker = create_proto_temporal_tracker()
        run_summary = build_final_run_summary(final_stats, tracker)
        trait_impact = run_summary["trait_impact"]

        self.assertAlmostEqual(float(trait_impact["stress_tolerance_mean"]), 1.02)
        self.assertAlmostEqual(float(trait_impact["stress_tolerance_std"]), 0.05)
        self.assertAlmostEqual(float(trait_impact["stress_pressure_events"]), 8.0)
        self.assertAlmostEqual(float(trait_impact["stress_pressure_flee_events"]), 3.0)
        self.assertAlmostEqual(float(trait_impact["stress_pressure_flee_rate"]), 0.375)
        self.assertAlmostEqual(float(trait_impact["stress_tolerance_pressure_flee_bias"]), -0.07)

        run_text = format_final_run_summary(run_summary)
        self.assertIn("st_mu=", run_text)
        self.assertIn("stress:cas=", run_text)
        self.assertIn("bias_st_fuite=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 10,
                    "run_summary": run_summary,
                }
            ]
        )
        avg_trait_impact = multi_summary["avg_trait_impact"]
        self.assertAlmostEqual(float(avg_trait_impact["stress_tolerance_mean"]), 1.02)
        self.assertAlmostEqual(float(avg_trait_impact["stress_pressure_flee_rate"]), 0.375)

        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("st_mu=", multi_text)
        self.assertIn("stress_moy:cas=", multi_text)
        self.assertIn("bias_st_fuite=", multi_text)

    def test_export_analysis_csv_preserves_stress_tolerance_metrics(self) -> None:
        payload = {
            "mode": "multi",
            "seeds": [21, 22],
            "run_count": 2,
            "multi_run_summary": {
                "runs": 2,
                "seeds": [21, 22],
                "extinction_count": 0,
                "extinction_rate": 0.0,
                "avg_max_generation": 4.0,
                "avg_final_population": 18.0,
                "avg_final_traits": {
                    "speed": 1.0,
                    "metabolism": 1.0,
                    "prudence": 1.0,
                    "dominance": 1.0,
                    "risk_taking": 1.0,
                    "stress_tolerance": 1.04,
                    "repro_drive": 1.0,
                    "food_perception": 1.0,
                    "threat_perception": 1.0,
                    "behavior_persistence": 1.0,
                    "exploration_bias": 1.0,
                    "density_preference": 1.0,
                    "mobility_efficiency": 1.0,
                    "energy_efficiency": 1.0,
                    "exhaustion_resistance": 1.0,
                    "longevity_factor": 1.0,
                    "environmental_tolerance": 1.0,
                    "reproduction_timing": 1.0,
                },
                "avg_trait_impact": {
                    "memory_focus_mean": 1.0,
                    "memory_focus_std": 0.0,
                    "social_sensitivity_mean": 1.0,
                    "social_sensitivity_std": 0.0,
                    "food_perception_mean": 1.0,
                    "food_perception_std": 0.0,
                    "threat_perception_mean": 1.0,
                    "threat_perception_std": 0.0,
                    "risk_taking_mean": 1.0,
                    "risk_taking_std": 0.0,
                    "stress_tolerance_mean": 1.04,
                    "stress_tolerance_std": 0.03,
                    "stress_pressure_events": 6.0,
                    "stress_pressure_flee_events": 2.0,
                    "stress_pressure_flee_rate": 0.333,
                    "stress_tolerance_pressure_mean": 1.01,
                    "stress_tolerance_pressure_flee_mean": 0.95,
                    "stress_tolerance_pressure_flee_bias": -0.06,
                },
                "avg_memory_impact": {},
                "avg_social_impact": {},
                "most_frequent_final_dominant_group": "gA",
                "most_frequent_final_dominant_group_count": 1,
                "most_frequent_final_dominant_group_share": 0.5,
            },
            "per_run": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi.csv"
            export_results(payload, str(path), "csv")
            loaded = load_export_payload(str(path), input_format="csv")

        summary = loaded["multi_run_summary"]
        avg_traits = summary["avg_final_traits"]
        avg_trait_impact = summary["avg_trait_impact"]

        self.assertAlmostEqual(float(avg_traits["stress_tolerance"]), 1.04)
        self.assertAlmostEqual(float(avg_trait_impact["stress_tolerance_mean"]), 1.04)
        self.assertAlmostEqual(float(avg_trait_impact["stress_tolerance_std"]), 0.03)
        self.assertAlmostEqual(float(avg_trait_impact["stress_pressure_events"]), 6.0)
        self.assertAlmostEqual(float(avg_trait_impact["stress_pressure_flee_events"]), 2.0)
        self.assertAlmostEqual(float(avg_trait_impact["stress_tolerance_pressure_flee_bias"]), -0.06)


if __name__ == "__main__":
    unittest.main()

