import subprocess
import sys
import unittest
from pathlib import Path

from debug_tools import build_multi_run_summary
from ui import format_multi_run_summary


class MultiRunModeTests(unittest.TestCase):
    def test_multi_run_summary_aggregates_expected_values(self) -> None:
        results = [
            {
                "seed": 10,
                "extinct": False,
                "max_generation": 8,
                "final_alive": 40,
                "run_summary": {
                    "final_dominant_group_signature": "gA",
                    "avg_traits": {
                        "speed": 1.00,
                        "metabolism": 0.95,
                        "prudence": 1.02,
                        "dominance": 1.01,
                        "repro_drive": 0.98,
                    },
                },
            },
            {
                "seed": 12,
                "extinct": True,
                "max_generation": 4,
                "final_alive": 0,
                "run_summary": {
                    "final_dominant_group_signature": "gB",
                    "avg_traits": {
                        "speed": 0.90,
                        "metabolism": 1.05,
                        "prudence": 0.98,
                        "dominance": 1.10,
                        "repro_drive": 0.92,
                    },
                },
            },
            {
                "seed": 14,
                "extinct": False,
                "max_generation": 10,
                "final_alive": 30,
                "run_summary": {
                    "final_dominant_group_signature": "gA",
                    "avg_traits": {
                        "speed": 1.10,
                        "metabolism": 1.00,
                        "prudence": 1.00,
                        "dominance": 0.95,
                        "repro_drive": 1.05,
                    },
                },
            },
        ]

        summary = build_multi_run_summary(results)

        self.assertEqual(int(summary["runs"]), 3)
        self.assertEqual(summary["seeds"], [10, 12, 14])
        self.assertEqual(int(summary["extinction_count"]), 1)
        self.assertAlmostEqual(float(summary["extinction_rate"]), 1.0 / 3.0)
        self.assertAlmostEqual(float(summary["avg_max_generation"]), (8 + 4 + 10) / 3)
        self.assertAlmostEqual(float(summary["avg_final_population"]), (40 + 0 + 30) / 3)
        self.assertEqual(summary["most_frequent_final_dominant_group"], "gA")
        self.assertEqual(int(summary["most_frequent_final_dominant_group_count"]), 2)
        self.assertAlmostEqual(float(summary["most_frequent_final_dominant_group_share"]), 2.0 / 3.0)

        avg_traits = summary["avg_final_traits"]
        self.assertAlmostEqual(float(avg_traits["speed"]), (1.0 + 0.9 + 1.1) / 3)
        self.assertAlmostEqual(float(avg_traits["metabolism"]), (0.95 + 1.05 + 1.0) / 3)

    def test_multi_run_summary_text_is_readable(self) -> None:
        summary = {
            "runs": 3,
            "seeds": [10, 12, 14],
            "extinction_count": 1,
            "extinction_rate": 0.3333,
            "avg_max_generation": 7.33,
            "avg_final_population": 23.33,
            "avg_final_traits": {
                "speed": 1.0,
                "metabolism": 1.0,
                "prudence": 1.0,
                "dominance": 1.0,
                "repro_drive": 1.0,
            },
            "most_frequent_final_dominant_group": "gA",
            "most_frequent_final_dominant_group_count": 2,
            "most_frequent_final_dominant_group_share": 0.66,
        }

        text = format_multi_run_summary(summary)

        self.assertIn("multi_runs:", text)
        self.assertIn("runs=3", text)
        self.assertIn("extinctions=1/3", text)
        self.assertIn("gen_max_moy=", text)
        self.assertIn("pop_finale_moy=", text)
        self.assertIn("traits_finaux_moy:", text)
        self.assertIn("social_moy:", text)
        self.assertIn("traits_impact_moy:", text)
        self.assertIn("dominant_final_freq=gA", text)

    def test_multi_run_summary_includes_avg_memory_impact(self) -> None:
        results = [
            {
                "seed": 10,
                "extinct": False,
                "max_generation": 8,
                "final_alive": 40,
                "run_summary": {
                    "final_dominant_group_signature": "gA",
                    "avg_traits": {
                        "speed": 1.0,
                        "metabolism": 1.0,
                        "prudence": 1.0,
                        "dominance": 1.0,
                        "repro_drive": 1.0,
                    },
                    "memory_impact": {
                        "food_usage_total": 12,
                        "danger_usage_total": 5,
                        "food_active_share": 0.4,
                        "danger_active_share": 0.2,
                        "food_effect_avg_distance": 1.3,
                        "danger_effect_avg_distance": 0.6,
                        "food_usage_per_tick": 0.5,
                        "danger_usage_per_tick": 0.2,
                    },
                    "trait_impact": {
                        "memory_focus_mean": 1.05,
                        "memory_focus_std": 0.10,
                        "social_sensitivity_mean": 0.95,
                        "social_sensitivity_std": 0.08,
                        "memory_focus_food_bias": 0.04,
                        "memory_focus_danger_bias": 0.01,
                        "social_sensitivity_follow_bias": 0.03,
                        "social_sensitivity_flee_boost_bias": 0.02,
                    },
                    "social_impact": {
                        "follow_usage_total": 8,
                        "flee_boost_usage_total": 3,
                        "influenced_count_last_tick": 2,
                        "influenced_share_last_tick": 0.25,
                        "influenced_per_tick": 0.9,
                        "follow_usage_per_tick": 0.4,
                        "flee_boost_usage_per_tick": 0.15,
                        "flee_multiplier_avg_tick": 1.2,
                        "flee_multiplier_avg_total": 1.1,
                    },
                },
            },
            {
                "seed": 12,
                "extinct": True,
                "max_generation": 4,
                "final_alive": 0,
                "run_summary": {
                    "final_dominant_group_signature": "gB",
                    "avg_traits": {
                        "speed": 1.0,
                        "metabolism": 1.0,
                        "prudence": 1.0,
                        "dominance": 1.0,
                        "repro_drive": 1.0,
                    },
                    "memory_impact": {
                        "food_usage_total": 4,
                        "danger_usage_total": 1,
                        "food_active_share": 0.2,
                        "danger_active_share": 0.1,
                        "food_effect_avg_distance": 0.7,
                        "danger_effect_avg_distance": 0.3,
                        "food_usage_per_tick": 0.2,
                        "danger_usage_per_tick": 0.1,
                    },
                    "trait_impact": {
                        "memory_focus_mean": 0.95,
                        "memory_focus_std": 0.07,
                        "social_sensitivity_mean": 1.05,
                        "social_sensitivity_std": 0.12,
                        "memory_focus_food_bias": -0.02,
                        "memory_focus_danger_bias": 0.00,
                        "social_sensitivity_follow_bias": -0.01,
                        "social_sensitivity_flee_boost_bias": 0.01,
                    },
                    "social_impact": {
                        "follow_usage_total": 2,
                        "flee_boost_usage_total": 1,
                        "influenced_count_last_tick": 1,
                        "influenced_share_last_tick": 0.1,
                        "influenced_per_tick": 0.4,
                        "follow_usage_per_tick": 0.15,
                        "flee_boost_usage_per_tick": 0.05,
                        "flee_multiplier_avg_tick": 1.1,
                        "flee_multiplier_avg_total": 1.05,
                    },
                },
            },
        ]

        summary = build_multi_run_summary(results)
        avg_memory = summary.get("avg_memory_impact")

        self.assertIsInstance(avg_memory, dict)
        assert isinstance(avg_memory, dict)
        self.assertAlmostEqual(float(avg_memory["food_usage_total"]), 8.0)
        self.assertAlmostEqual(float(avg_memory["danger_usage_total"]), 3.0)
        self.assertAlmostEqual(float(avg_memory["food_active_share"]), 0.3)
        self.assertAlmostEqual(float(avg_memory["danger_active_share"]), 0.15)

        avg_trait_impact = summary.get("avg_trait_impact")
        self.assertIsInstance(avg_trait_impact, dict)
        assert isinstance(avg_trait_impact, dict)
        self.assertAlmostEqual(float(avg_trait_impact["memory_focus_mean"]), 1.0)
        self.assertAlmostEqual(float(avg_trait_impact["social_sensitivity_mean"]), 1.0)

        avg_social = summary.get("avg_social_impact")
        self.assertIsInstance(avg_social, dict)
        assert isinstance(avg_social, dict)
        self.assertAlmostEqual(float(avg_social["follow_usage_total"]), 5.0)
        self.assertAlmostEqual(float(avg_social["flee_boost_usage_total"]), 2.0)
        self.assertAlmostEqual(float(avg_social["influenced_share_last_tick"]), 0.175)

        text_summary = format_multi_run_summary(summary)
        self.assertIn("memoire_moy:", text_summary)
        self.assertIn("social_moy:", text_summary)

    def test_cli_multi_run_mode_outputs_summary(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--runs",
            "2",
            "--seed",
            "100",
            "--seed-step",
            "3",
            "--steps",
            "30",
            "--log-interval",
            "15",
        ]

        completed = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )

        output = completed.stdout
        self.assertIn("=== Multi-Run Mode ===", output)
        self.assertIn("seeds: 100,103", output)
        self.assertIn("--- Multi-Run Summary ---", output)
        self.assertIn("multi_runs:", output)

    def test_cli_single_run_mode_keeps_existing_output(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--runs",
            "1",
            "--seed",
            "42",
            "--steps",
            "20",
            "--log-interval",
            "10",
        ]

        completed = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )

        output = completed.stdout
        self.assertIn("=== Evolution MVP Simulation ===", output)
        self.assertIn("--- Run Summary ---", output)
        self.assertNotIn("--- Multi-Run Summary ---", output)


if __name__ == "__main__":
    unittest.main()

