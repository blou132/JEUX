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
                    "avg_trait_impact": {
                        "memory_focus_food_bias": -0.05,
                        "memory_focus_danger_bias": -0.02,
                        "social_sensitivity_follow_bias": -0.02,
                        "social_sensitivity_flee_boost_bias": -0.01,
                        "memory_focus_std": 0.03,
                        "social_sensitivity_std": 0.04,
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
                    "avg_trait_impact": {
                        "memory_focus_food_bias": 0.09,
                        "memory_focus_danger_bias": 0.07,
                        "social_sensitivity_follow_bias": 0.04,
                        "social_sensitivity_flee_boost_bias": 0.02,
                        "memory_focus_std": 0.10,
                        "social_sensitivity_std": 0.09,
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
                    "avg_trait_impact": {
                        "memory_focus_food_bias": 0.04,
                        "memory_focus_danger_bias": 0.11,
                        "social_sensitivity_follow_bias": 0.06,
                        "social_sensitivity_flee_boost_bias": 0.01,
                        "memory_focus_std": 0.12,
                        "social_sensitivity_std": 0.10,
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

        trait = summary.get("trait_comparative")
        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertTrue(bool(trait.get("available", False)))
        self.assertEqual(trait["best_memory_usage_bias"]["winners"], [8.0])
        self.assertEqual(trait["best_social_usage_bias"]["winners"], [12.0])
        self.assertEqual(trait["best_trait_dispersion"]["winners"], [12.0])
        self.assertEqual(trait["most_stable_config"]["winners"], [8.0])

        text = format_batch_comparative_summary(summary)
        self.assertIn("memoire_batch:", text)
        self.assertIn("usage_memoire_utile_max:", text)
        self.assertIn("usage_memoire_dangereuse_max:", text)
        self.assertIn("effet_memoire_utile_max:", text)
        self.assertIn("effet_memoire_dangereuse_max:", text)
        self.assertIn("traits_batch:", text)
        self.assertIn("bias_usage_memoire_max:", text)
        self.assertIn("bias_usage_social_max:", text)
        self.assertIn("dispersion_traits_max:", text)

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
        trait = summary.get("trait_comparative")

        self.assertIsInstance(memory, dict)
        assert isinstance(memory, dict)
        self.assertFalse(bool(memory.get("available", True)))
        self.assertIn("donnees insuffisantes", str(memory.get("note", "")))

        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertFalse(bool(trait.get("available", True)))
        self.assertIn("donnees insuffisantes", str(trait.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("memoire_batch:", text)
        self.assertIn("donnees_memoire: n/a", text)
        self.assertIn("traits_batch:", text)
        self.assertIn("donnees_traits: n/a", text)

    def test_social_param_summary_includes_social_comparatives(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.0,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 8.0,
                    "avg_social_impact": {
                        "follow_usage_per_tick": 0.00,
                        "flee_boost_usage_per_tick": 0.05,
                        "influenced_share_last_tick": 0.08,
                        "flee_multiplier_avg_total": 1.02,
                    },
                    "avg_trait_impact": {
                        "memory_focus_food_bias": -0.02,
                        "memory_focus_danger_bias": -0.01,
                        "social_sensitivity_follow_bias": -0.01,
                        "social_sensitivity_flee_boost_bias": -0.02,
                        "memory_focus_std": 0.04,
                        "social_sensitivity_std": 0.03,
                    },
                },
            },
            {
                "parameter_value": 0.35,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_social_impact": {
                        "follow_usage_per_tick": 0.30,
                        "flee_boost_usage_per_tick": 0.20,
                        "influenced_share_last_tick": 0.35,
                        "flee_multiplier_avg_total": 1.18,
                    },
                    "avg_trait_impact": {
                        "memory_focus_food_bias": 0.03,
                        "memory_focus_danger_bias": 0.02,
                        "social_sensitivity_follow_bias": 0.08,
                        "social_sensitivity_flee_boost_bias": 0.05,
                        "memory_focus_std": 0.11,
                        "social_sensitivity_std": 0.12,
                    },
                },
            },
            {
                "parameter_value": 0.70,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_social_impact": {
                        "follow_usage_per_tick": 0.45,
                        "flee_boost_usage_per_tick": 0.18,
                        "influenced_share_last_tick": 0.32,
                        "flee_multiplier_avg_total": 1.22,
                    },
                    "avg_trait_impact": {
                        "memory_focus_food_bias": 0.01,
                        "memory_focus_danger_bias": 0.01,
                        "social_sensitivity_follow_bias": 0.10,
                        "social_sensitivity_flee_boost_bias": 0.04,
                        "memory_focus_std": 0.15,
                        "social_sensitivity_std": 0.14,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("social_follow_strength", scenarios)
        social = summary.get("social_comparative")

        self.assertIsInstance(social, dict)
        assert isinstance(social, dict)
        self.assertTrue(bool(social.get("available", False)))

        follow_usage = social.get("best_social_follow_usage")
        self.assertIsInstance(follow_usage, dict)
        assert isinstance(follow_usage, dict)
        self.assertEqual(follow_usage["winners"], [0.7])
        self.assertAlmostEqual(float(follow_usage["value"]), 0.45)

        flee_usage = social.get("best_social_flee_boost_usage")
        self.assertIsInstance(flee_usage, dict)
        assert isinstance(flee_usage, dict)
        self.assertEqual(flee_usage["winners"], [0.35])
        self.assertAlmostEqual(float(flee_usage["value"]), 0.20)

        influenced_share = social.get("best_social_influenced_share")
        self.assertIsInstance(influenced_share, dict)
        assert isinstance(influenced_share, dict)
        self.assertEqual(influenced_share["winners"], [0.35])
        self.assertAlmostEqual(float(influenced_share["value"]), 0.35)

        flee_effect = social.get("best_social_flee_multiplier_effect")
        self.assertIsInstance(flee_effect, dict)
        assert isinstance(flee_effect, dict)
        self.assertEqual(flee_effect["winners"], [0.7])
        self.assertAlmostEqual(float(flee_effect["value"]), 1.22)

        trait = summary.get("trait_comparative")
        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertTrue(bool(trait.get("available", False)))
        self.assertEqual(trait["best_memory_usage_bias"]["winners"], [0.35])
        self.assertEqual(trait["best_social_usage_bias"]["winners"], [0.7])
        self.assertEqual(trait["best_trait_dispersion"]["winners"], [0.7])
        self.assertEqual(trait["most_stable_config"]["winners"], [0.35])

        text = format_batch_comparative_summary(summary)
        self.assertIn("social_batch:", text)
        self.assertIn("usage_suivi_social_max:", text)
        self.assertIn("usage_boost_fuite_social_max:", text)
        self.assertIn("part_creatures_influencees_max:", text)
        self.assertIn("effet_multiplicateur_fuite_max:", text)
        self.assertIn("traits_batch:", text)
        self.assertIn("bias_usage_memoire_max:", text)
        self.assertIn("bias_usage_social_max:", text)
        self.assertIn("dispersion_traits_max:", text)

    def test_social_param_with_insufficient_data_is_reported(self) -> None:
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
                "parameter_value": 0.7,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("social_follow_strength", scenarios)
        social = summary.get("social_comparative")
        trait = summary.get("trait_comparative")

        self.assertIsInstance(social, dict)
        assert isinstance(social, dict)
        self.assertFalse(bool(social.get("available", True)))
        self.assertIn("donnees insuffisantes", str(social.get("note", "")))

        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertFalse(bool(trait.get("available", True)))
        self.assertIn("donnees insuffisantes", str(trait.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("social_batch:", text)
        self.assertIn("donnees_sociales: n/a", text)
        self.assertIn("traits_batch:", text)
        self.assertIn("donnees_traits: n/a", text)

    def test_energy_param_summary_includes_energy_comparatives(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.9,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 15.0,
                    "avg_trait_impact": {
                        "energy_drain_multiplier_observed": 1.01,
                        "reproduction_cost_multiplier_observed": 1.04,
                        "energy_efficiency_std": 0.04,
                        "exhaustion_resistance_std": 0.05,
                    },
                },
            },
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 20.0,
                    "avg_trait_impact": {
                        "energy_drain_multiplier_observed": 0.95,
                        "reproduction_cost_multiplier_observed": 1.02,
                        "energy_efficiency_std": 0.06,
                        "exhaustion_resistance_std": 0.06,
                    },
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 5.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "energy_drain_multiplier_observed": 0.98,
                        "reproduction_cost_multiplier_observed": 0.92,
                        "energy_efficiency_std": 0.11,
                        "exhaustion_resistance_std": 0.09,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        energy = summary.get("energy_comparative")

        self.assertIsInstance(energy, dict)
        assert isinstance(energy, dict)
        self.assertTrue(bool(energy.get("available", False)))
        self.assertEqual(energy["best_energy_drain_effect"]["winners"], [1.0])
        self.assertAlmostEqual(float(energy["best_energy_drain_effect"]["value"]), 0.05)
        self.assertEqual(energy["best_reproduction_cost_effect"]["winners"], [1.2])
        self.assertAlmostEqual(float(energy["best_reproduction_cost_effect"]["value"]), 0.08)
        self.assertEqual(energy["best_energy_trait_dispersion"]["winners"], [1.2])
        self.assertAlmostEqual(float(energy["best_energy_trait_dispersion"]["value"]), 0.10)
        self.assertEqual(energy["most_stable_config"]["winners"], [1.0])

        text = format_batch_comparative_summary(summary)
        self.assertIn("energie_batch:", text)
        self.assertIn("effet_drain_energie_max:", text)
        self.assertIn("effet_cout_reproduction_max:", text)
        self.assertIn("dispersion_energie_max:", text)
        self.assertIn("configuration_plus_stable:", text)

    def test_energy_param_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.9,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 15.0,
                    "avg_trait_impact": {
                        "energy_drain_multiplier_observed": 1.01,
                    },
                },
            },
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 20.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        energy = summary.get("energy_comparative")

        self.assertIsInstance(energy, dict)
        assert isinstance(energy, dict)
        self.assertFalse(bool(energy.get("available", True)))
        self.assertIn("donnees insuffisantes", str(energy.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("energie_batch:", text)
        self.assertIn("donnees_energie: n/a", text)


    def test_perception_comparative_includes_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.8,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 12.0,
                    "avg_trait_impact": {
                        "food_perception_detection_bias": 0.02,
                        "food_perception_consumption_bias": 0.00,
                        "threat_perception_flee_bias": 0.03,
                        "food_perception_std": 0.04,
                        "threat_perception_std": 0.05,
                    },
                },
            },
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 20.0,
                    "avg_trait_impact": {
                        "food_perception_detection_bias": 0.08,
                        "food_perception_consumption_bias": 0.04,
                        "threat_perception_flee_bias": 0.01,
                        "food_perception_std": 0.10,
                        "threat_perception_std": 0.12,
                    },
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "food_perception_detection_bias": 0.06,
                        "food_perception_consumption_bias": 0.02,
                        "threat_perception_flee_bias": 0.09,
                        "food_perception_std": 0.08,
                        "threat_perception_std": 0.10,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        perception = summary.get("perception_comparative")

        self.assertIsInstance(perception, dict)
        assert isinstance(perception, dict)
        self.assertTrue(bool(perception.get("available", False)))
        self.assertEqual(perception["best_food_perception_usage"]["winners"], [1.0])
        self.assertEqual(perception["best_threat_perception_usage"]["winners"], [1.2])
        self.assertEqual(perception["best_perception_dispersion"]["winners"], [1.0])
        self.assertEqual(perception["most_stable_config"]["winners"], [1.0])

        text = format_batch_comparative_summary(summary)
        self.assertIn("perception_batch:", text)
        self.assertIn("usage_food_perception_max:", text)
        self.assertIn("usage_threat_perception_max:", text)
        self.assertIn("dispersion_perception_max:", text)

    def test_perception_comparative_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 1.0,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 20.0,
                    "avg_trait_impact": {
                        "food_perception_detection_bias": 0.02,
                    },
                },
            },
            {
                "parameter_value": 1.2,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 12.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("energy_drain_rate", scenarios)
        perception = summary.get("perception_comparative")

        self.assertIsInstance(perception, dict)
        assert isinstance(perception, dict)
        self.assertFalse(bool(perception.get("available", True)))
        self.assertIn("donnees insuffisantes", str(perception.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("perception_batch:", text)
        self.assertIn("donnees_perception: n/a", text)
if __name__ == "__main__":
    unittest.main()

