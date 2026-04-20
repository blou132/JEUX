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

    def test_behavior_persistence_comparative_includes_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.0,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 10.0,
                    "avg_trait_impact": {
                        "search_wander_switches_prevented_total": 2.0,
                        "behavior_persistence_oscillation_switch_rate": 0.85,
                        "behavior_persistence_oscillation_prevented_rate": 0.15,
                        "search_wander_oscillation_events_total": 12.0,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_trait_impact": {
                        "search_wander_switches_prevented_total": 8.0,
                        "behavior_persistence_oscillation_switch_rate": 0.35,
                        "behavior_persistence_oscillation_prevented_rate": 0.65,
                        "search_wander_oscillation_events_total": 20.0,
                    },
                },
            },
            {
                "parameter_value": 0.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "search_wander_switches_prevented_total": 6.0,
                        "behavior_persistence_oscillation_switch_rate": 0.40,
                        "behavior_persistence_oscillation_prevented_rate": 0.60,
                        "search_wander_oscillation_events_total": 18.0,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        bp = summary.get("behavior_persistence_comparative")

        self.assertIsInstance(bp, dict)
        assert isinstance(bp, dict)
        self.assertTrue(bool(bp.get("available", False)))
        self.assertEqual(bp["best_switches_prevented"]["winners"], [0.1])
        self.assertAlmostEqual(float(bp["best_switches_prevented"]["value"]), 8.0)
        self.assertEqual(bp["lowest_switch_rate"]["winners"], [0.1])
        self.assertAlmostEqual(float(bp["lowest_switch_rate"]["value"]), 0.35)
        self.assertEqual(bp["best_prevented_rate"]["winners"], [0.1])
        self.assertAlmostEqual(float(bp["best_prevented_rate"]["value"]), 0.65)
        self.assertEqual(bp["most_stable_config"]["winners"], [0.1])

        text = format_batch_comparative_summary(summary)
        self.assertIn("behavior_persistence_batch:", text)
        self.assertIn("switchs_evites_max:", text)
        self.assertIn("taux_switch_min:", text)
        self.assertIn("taux_blocage_utile_max:", text)
        self.assertIn("configuration_plus_stable:", text)

    def test_behavior_persistence_comparative_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.0,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 14.0,
                    "avg_trait_impact": {
                        "behavior_persistence_oscillation_switch_rate": 0.5,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 19.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        bp = summary.get("behavior_persistence_comparative")

        self.assertIsInstance(bp, dict)
        assert isinstance(bp, dict)
        self.assertFalse(bool(bp.get("available", True)))
        self.assertIn("donnees insuffisantes", str(bp.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("behavior_persistence_batch:", text)
        self.assertIn("donnees_behavior_persistence: n/a", text)

    def test_exploration_comparative_includes_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.05,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 10.0,
                    "avg_trait_impact": {
                        "exploration_bias_guided_total": 6.0,
                        "exploration_bias_explore_share": 0.75,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_trait_impact": {
                        "exploration_bias_guided_total": 9.0,
                        "exploration_bias_explore_share": 0.45,
                    },
                },
            },
            {
                "parameter_value": 0.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "exploration_bias_guided_total": 11.0,
                        "exploration_bias_explore_share": 0.20,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        exploration = summary.get("exploration_comparative")

        self.assertIsInstance(exploration, dict)
        assert isinstance(exploration, dict)
        self.assertTrue(bool(exploration.get("available", False)))
        self.assertEqual(exploration["best_explore_usage"]["winners"], [0.05])
        self.assertAlmostEqual(float(exploration["best_explore_usage"]["value"]), 0.75)
        self.assertEqual(exploration["best_settle_usage"]["winners"], [0.2])
        self.assertAlmostEqual(float(exploration["best_settle_usage"]["value"]), 0.8)
        self.assertEqual(exploration["best_guided_usage"]["winners"], [0.2])
        self.assertAlmostEqual(float(exploration["best_guided_usage"]["value"]), 11.0)
        self.assertEqual(exploration["most_stable_config"]["winners"], [0.1])

        text = format_batch_comparative_summary(summary)
        self.assertIn("exploration_bias_batch:", text)
        self.assertIn("usage_explore_max:", text)
        self.assertIn("usage_settle_max:", text)
        self.assertIn("usage_guided_max:", text)
        self.assertIn("configuration_plus_stable:", text)

    def test_exploration_comparative_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.05,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 12.0,
                    "avg_trait_impact": {
                        "exploration_bias_explore_share": 0.6,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 16.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        exploration = summary.get("exploration_comparative")

        self.assertIsInstance(exploration, dict)
        assert isinstance(exploration, dict)
        self.assertFalse(bool(exploration.get("available", True)))
        self.assertIn("donnees insuffisantes", str(exploration.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("exploration_bias_batch:", text)
        self.assertIn("donnees_exploration_bias: n/a", text)

    def test_density_preference_comparative_includes_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.05,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 10.0,
                    "avg_trait_impact": {
                        "density_preference_guided_total": 6.0,
                        "density_preference_seek_usage_per_tick": 0.45,
                        "density_preference_avoid_usage_per_tick": 0.10,
                        "density_preference_avoid_share": 0.25,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_trait_impact": {
                        "density_preference_guided_total": 11.0,
                        "density_preference_seek_usage_per_tick": 0.30,
                        "density_preference_avoid_usage_per_tick": 0.40,
                        "density_preference_avoid_share": 0.65,
                    },
                },
            },
            {
                "parameter_value": 0.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "density_preference_guided_total": 9.0,
                        "density_preference_seek_usage_per_tick": 0.20,
                        "density_preference_avoid_usage_per_tick": 0.35,
                        "density_preference_avoid_share": 0.70,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        density = summary.get("density_preference_comparative")

        self.assertIsInstance(density, dict)
        assert isinstance(density, dict)
        self.assertTrue(bool(density.get("available", False)))
        self.assertEqual(density["best_seek_usage"]["winners"], [0.05])
        self.assertAlmostEqual(float(density["best_seek_usage"]["value"]), 0.45)
        self.assertEqual(density["best_avoid_usage"]["winners"], [0.1])
        self.assertAlmostEqual(float(density["best_avoid_usage"]["value"]), 0.4)
        self.assertEqual(density["best_avoid_share"]["winners"], [0.2])
        self.assertAlmostEqual(float(density["best_avoid_share"]["value"]), 0.7)
        self.assertEqual(density["most_stable_config"]["winners"], [0.1])

        text = format_batch_comparative_summary(summary)
        self.assertIn("density_preference_batch:", text)
        self.assertIn("usage_seek_max:", text)
        self.assertIn("usage_avoid_max:", text)
        self.assertIn("part_avoid_max:", text)
        self.assertIn("configuration_plus_stable:", text)

    def test_density_preference_comparative_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.05,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 12.0,
                    "avg_trait_impact": {
                        "density_preference_avoid_share": 0.6,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 16.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        density = summary.get("density_preference_comparative")

        self.assertIsInstance(density, dict)
        assert isinstance(density, dict)
        self.assertFalse(bool(density.get("available", True)))
        self.assertIn("donnees insuffisantes", str(density.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("density_preference_batch:", text)
        self.assertIn("donnees_density_preference: n/a", text)

    def test_longevity_comparative_includes_expected_winners(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.05,
                "multi_run_summary": {
                    "extinction_rate": 0.2,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 10.0,
                    "avg_trait_impact": {
                        "longevity_factor_std": 0.03,
                        "age_wear_usage_per_tick": 0.20,
                        "age_wear_multiplier_observed": 0.96,
                    },
                },
            },
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 4.0,
                    "avg_final_population": 22.0,
                    "avg_trait_impact": {
                        "longevity_factor_std": 0.08,
                        "age_wear_usage_per_tick": 0.30,
                        "age_wear_multiplier_observed": 1.10,
                    },
                },
            },
            {
                "parameter_value": 0.2,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 18.0,
                    "avg_trait_impact": {
                        "longevity_factor_std": 0.05,
                        "age_wear_usage_per_tick": 0.40,
                        "age_wear_multiplier_observed": 0.80,
                    },
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        longevity = summary.get("longevity_comparative")

        self.assertIsInstance(longevity, dict)
        assert isinstance(longevity, dict)
        self.assertTrue(bool(longevity.get("available", False)))
        self.assertEqual(longevity["best_age_wear_effect"]["winners"], [0.2])
        self.assertAlmostEqual(float(longevity["best_age_wear_effect"]["value"]), 0.2)
        self.assertEqual(longevity["best_age_wear_reduction"]["winners"], [0.2])
        self.assertAlmostEqual(float(longevity["best_age_wear_reduction"]["value"]), 0.2)
        self.assertEqual(longevity["best_longevity_dispersion"]["winners"], [0.1])
        self.assertAlmostEqual(float(longevity["best_longevity_dispersion"]["value"]), 0.08)
        self.assertEqual(longevity["most_stable_config"]["winners"], [0.1])

        text = format_batch_comparative_summary(summary)
        self.assertIn("longevity_factor_batch:", text)
        self.assertIn("effet_usure_age_max:", text)
        self.assertIn("reduction_drain_age_max:", text)
        self.assertIn("dispersion_longevite_max:", text)
        self.assertIn("configuration_plus_stable:", text)

    def test_longevity_comparative_with_insufficient_data_is_reported(self) -> None:
        scenarios = [
            {
                "parameter_value": 0.1,
                "multi_run_summary": {
                    "extinction_rate": 0.0,
                    "avg_max_generation": 3.0,
                    "avg_final_population": 16.0,
                    "avg_trait_impact": {
                        "age_wear_usage_per_tick": 0.2,
                    },
                },
            },
            {
                "parameter_value": 0.2,
                "multi_run_summary": {
                    "extinction_rate": 0.1,
                    "avg_max_generation": 2.0,
                    "avg_final_population": 12.0,
                },
            },
        ]

        summary = build_batch_comparative_summary("mutation_variation", scenarios)
        longevity = summary.get("longevity_comparative")

        self.assertIsInstance(longevity, dict)
        assert isinstance(longevity, dict)
        self.assertFalse(bool(longevity.get("available", True)))
        self.assertIn("donnees insuffisantes", str(longevity.get("note", "")))

        text = format_batch_comparative_summary(summary)
        self.assertIn("longevity_factor_batch:", text)
        self.assertIn("donnees_longevity_factor: n/a", text)

if __name__ == "__main__":
    unittest.main()

