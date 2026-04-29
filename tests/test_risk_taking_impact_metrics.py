import random
import tempfile
import unittest
from pathlib import Path

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import build_batch_comparative_summary, build_population_stats
from legacy_python.debug_tools.batch_comparative import format_batch_comparative_summary
from legacy_python.debug_tools.export_analysis import load_export_payload
from legacy_python.debug_tools.export_results import export_results
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField


class RiskTakingImpactMetricsTests(unittest.TestCase):
    def test_population_stats_expose_risk_taking_impact_indicators(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.15, max_energy=100.0, risk_taking=1.0),
        )
        cautious = Creature(
            creature_id="cautious",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=0.7),
        )
        bold = Creature(
            creature_id="bold",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=1.3),
        )

        sim = HungerSimulation(
            creatures=[cautious, bold, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0, threat_strength_ratio=1.15),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(7),
        )
        sim.tick(1.0)

        stats = build_population_stats(sim)
        required_keys = {
            "avg_risk_taking",
            "std_risk_taking",
            "risk_taking_flee_usage_bias_tick",
            "borderline_threat_encounters_last_tick",
            "borderline_threat_flees_last_tick",
            "borderline_threat_flee_rate_last_tick",
            "risk_taking_borderline_flee_usage_bias_tick",
        }
        self.assertTrue(required_keys.issubset(set(stats.keys())))

        encounters = int(stats["borderline_threat_encounters_last_tick"])
        flees = int(stats["borderline_threat_flees_last_tick"])
        flee_rate = float(stats["borderline_threat_flee_rate_last_tick"])

        self.assertGreater(encounters, 0)
        self.assertGreaterEqual(encounters, flees)
        self.assertGreaterEqual(flee_rate, 0.0)
        self.assertLessEqual(flee_rate, 1.0)
        self.assertGreater(float(stats["std_risk_taking"]), 0.0)

    def test_batch_comparative_exposes_risk_section(self) -> None:
        scenarios = [
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_trait_impact": {
                        "risk_taking_flee_bias": -0.20,
                        "risk_taking_std": 0.08,
                        "risk_taking_borderline_flee_bias": -0.30,
                        "borderline_threat_flee_rate": 0.60,
                        "borderline_threat_encounters": 10.0,
                    },
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 20.0,
                    "avg_trait_impact": {
                        "risk_taking_flee_bias": -0.05,
                        "risk_taking_std": 0.12,
                        "risk_taking_borderline_flee_bias": -0.10,
                        "borderline_threat_flee_rate": 0.80,
                        "borderline_threat_encounters": 8.0,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        risk_summary = summary.get("risk_comparative")
        self.assertIsInstance(risk_summary, dict)
        assert isinstance(risk_summary, dict)
        self.assertTrue(bool(risk_summary.get("available", False)))
        self.assertEqual(risk_summary["best_risk_flee_usage_bias"]["winners"], [1.0])
        self.assertEqual(risk_summary["best_borderline_risk_effect"]["winners"], [1.0])
        self.assertEqual(risk_summary["best_risk_dispersion"]["winners"], [1.2])
        self.assertEqual(risk_summary["best_borderline_flee_rate"]["winners"], [1.2])

        text = format_batch_comparative_summary(summary)
        self.assertIn("risque_batch:", text)
        self.assertIn("usage_fuite_risque_max:", text)
        self.assertIn("effet_borderline_risque_max:", text)
        self.assertIn("dispersion_risque_max:", text)
        self.assertIn("taux_fuite_borderline_max:", text)

    def test_export_analysis_csv_preserves_risk_taking_metrics(self) -> None:
        payload = {
            "mode": "multi",
            "seeds": [10, 11],
            "run_count": 2,
            "multi_run_summary": {
                "runs": 2,
                "seeds": [10, 11],
                "extinction_count": 0,
                "extinction_rate": 0.0,
                "avg_max_generation": 5.0,
                "avg_final_population": 20.0,
                "avg_final_traits": {
                    "speed": 1.0,
                    "metabolism": 1.0,
                    "prudence": 1.0,
                    "dominance": 1.0,
                    "risk_taking": 0.93,
                    "repro_drive": 1.0,
                    "food_perception": 1.0,
                    "threat_perception": 1.0,
                    "energy_efficiency": 1.0,
                    "exhaustion_resistance": 1.0,
                },
                "avg_trait_impact": {
                    "memory_focus_mean": 1.0,
                    "memory_focus_std": 0.1,
                    "social_sensitivity_mean": 1.0,
                    "social_sensitivity_std": 0.1,
                    "food_perception_mean": 1.0,
                    "food_perception_std": 0.1,
                    "threat_perception_mean": 1.0,
                    "threat_perception_std": 0.1,
                    "risk_taking_mean": 0.93,
                    "risk_taking_std": 0.11,
                    "energy_efficiency_mean": 1.0,
                    "energy_efficiency_std": 0.1,
                    "exhaustion_resistance_mean": 1.0,
                    "exhaustion_resistance_std": 0.1,
                    "energy_efficiency_drain_bias": 0.0,
                    "exhaustion_resistance_reproduction_bias": 0.0,
                    "energy_drain_multiplier_observed": 1.0,
                    "reproduction_cost_multiplier_observed": 1.0,
                    "energy_drain_amount_observed": 1.0,
                    "reproduction_cost_amount_observed": 1.0,
                    "memory_focus_food_bias": 0.0,
                    "memory_focus_danger_bias": 0.0,
                    "social_sensitivity_follow_bias": 0.0,
                    "social_sensitivity_flee_boost_bias": 0.0,
                    "food_perception_detection_bias": 0.0,
                    "food_perception_consumption_bias": 0.0,
                    "threat_perception_flee_bias": 0.0,
                    "risk_taking_flee_bias": -0.07,
                    "borderline_threat_encounters": 6.0,
                    "borderline_threat_flees": 3.0,
                    "borderline_threat_flee_rate": 0.5,
                    "risk_taking_borderline_encounter_mean": 0.95,
                    "risk_taking_borderline_flee_mean": 0.87,
                    "risk_taking_borderline_flee_bias": -0.08,
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

        self.assertEqual(loaded["mode"], "multi")
        summary = loaded["multi_run_summary"]
        avg_traits = summary["avg_final_traits"]
        avg_trait_impact = summary["avg_trait_impact"]

        self.assertAlmostEqual(float(avg_traits["risk_taking"]), 0.93)
        self.assertAlmostEqual(float(avg_trait_impact["risk_taking_mean"]), 0.93)
        self.assertAlmostEqual(float(avg_trait_impact["risk_taking_std"]), 0.11)
        self.assertAlmostEqual(float(avg_trait_impact["risk_taking_flee_bias"]), -0.07)
        self.assertAlmostEqual(float(avg_trait_impact["borderline_threat_flee_rate"]), 0.5)
        self.assertAlmostEqual(float(avg_trait_impact["risk_taking_borderline_flee_bias"]), -0.08)


if __name__ == "__main__":
    unittest.main()

