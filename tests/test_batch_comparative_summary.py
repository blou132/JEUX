import unittest

from debug_tools.batch_comparative import (
    build_batch_comparative_summary,
    format_batch_comparative_summary,
)


class BatchComparativeSummaryTests(unittest.TestCase):
    def test_build_comparative_summary_picks_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 30.0,
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 50.0,
                },
            },
            {
                "parameter_value": 1.4,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 40.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)

        self.assertEqual(summary["batch_param"], "energy_drain_rate")
        self.assertEqual(int(summary["evaluated_values_count"]), 3)

        most_stable = summary["most_stable"]
        self.assertEqual(most_stable["winners"], [1.4])
        self.assertAlmostEqual(float(most_stable["extinction_rate"]), 0.0)
        self.assertAlmostEqual(float(most_stable["avg_final_population"]), 40.0)
        self.assertAlmostEqual(float(most_stable["avg_max_generation"]), 3.0)

        best_gen = summary["best_avg_max_generation"]
        self.assertEqual(best_gen["winners"], [1.2])
        self.assertAlmostEqual(float(best_gen["avg_max_generation"]), 4.0)

        best_pop = summary["best_avg_final_population"]
        self.assertEqual(best_pop["winners"], [1.2])
        self.assertAlmostEqual(float(best_pop["avg_final_population"]), 50.0)

        lowest_ext = summary["lowest_extinction_rate"]
        self.assertEqual(lowest_ext["winners"], [1.0, 1.4])
        self.assertTrue(bool(lowest_ext["tie"]))
        self.assertAlmostEqual(float(lowest_ext["extinction_rate"]), 0.0)

    def test_format_comparative_summary_reports_ties(self) -> None:
        scenarios = [
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 40.0,
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 40.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        text = format_batch_comparative_summary(summary)

        self.assertIn("batch_comparatif:", text)
        self.assertIn("plus_stable: egalite[energy_drain_rate=1.0,1.2]", text)
        self.assertIn("meilleure_gen_max_moy: egalite[energy_drain_rate=1.0,1.2]", text)
        self.assertIn("meilleure_pop_finale_moy: egalite[energy_drain_rate=1.0,1.2]", text)
        self.assertIn("plus_faible_taux_extinction: egalite[energy_drain_rate=1.0,1.2]", text)

    def test_memory_param_summary_includes_memory_comparatives(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.0,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 8.0,
                    "avg_memory_impact": {
                        "food_usage_total": 1.0,
                        "danger_usage_total": 0.5,
                        "food_effect_avg_distance": 0.3,
                        "danger_effect_avg_distance": 0.1,
                    },
                },
            },
            {
                "parameter_value": 8.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 20.0,
                    "avg_memory_impact": {
                        "food_usage_total": 6.0,
                        "danger_usage_total": 3.0,
                        "food_effect_avg_distance": 1.2,
                        "danger_effect_avg_distance": 0.8,
                    },
                },
            },
            {
                "parameter_value": 12.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 18.0,
                    "avg_memory_impact": {
                        "food_usage_total": 4.0,
                        "danger_usage_total": 5.0,
                        "food_effect_avg_distance": 1.2,
                        "danger_effect_avg_distance": 1.1,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("food_memory_duration", scenarios)
        memory = summary.get("memory_comparative")

        self.assertIsInstance(memory, dict)
        assert isinstance(memory, dict)
        self.assertTrue(bool(memory.get("available", False)))

        best_food_usage = memory.get("best_food_memory_usage")
        self.assertIsInstance(best_food_usage, dict)
        assert isinstance(best_food_usage, dict)
        self.assertEqual(best_food_usage["winners"], [8.0])
        self.assertAlmostEqual(float(best_food_usage["value"]), 6.0)

        best_danger_usage = memory.get("best_danger_memory_usage")
        self.assertIsInstance(best_danger_usage, dict)
        assert isinstance(best_danger_usage, dict)
        self.assertEqual(best_danger_usage["winners"], [12.0])
        self.assertAlmostEqual(float(best_danger_usage["value"]), 5.0)

        best_food_effect = memory.get("best_food_memory_effect")
        self.assertIsInstance(best_food_effect, dict)
        assert isinstance(best_food_effect, dict)
        self.assertEqual(best_food_effect["winners"], [8.0, 12.0])
        self.assertTrue(bool(best_food_effect["tie"]))

        text = format_batch_comparative_summary(summary)
        self.assertIn("memoire_batch:", text)
        self.assertIn("usage_memoire_utile_max:", text)
        self.assertIn("usage_memoire_dangereuse_max:", text)
        self.assertIn("effet_memoire_utile_max:", text)
        self.assertIn("effet_memoire_dangereuse_max:", text)

    def test_memory_param_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.0,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 8.0,
                },
            },
            {
                "parameter_value": 8.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 20.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("food_memory_duration", scenarios)
        memory = summary.get("memory_comparative")

        self.assertIsInstance(memory, dict)
        assert isinstance(memory, dict)
        self.assertFalse(bool(memory.get("available", True)))
        self.assertIn("donnees insuffisantes", str(memory.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("memoire_batch:", text)
        self.assertIn("donnees_memoire: n/a", text)


if __name__ == "__main__":
    unittest.main()
