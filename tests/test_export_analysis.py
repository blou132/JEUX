import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from legacy_python.debug_tools import export_results
from legacy_python.debug_tools.export_analysis import load_export_payload, summarize_export_payload


class ExportAnalysisTests(unittest.TestCase):
    def test_load_single_json_and_build_summary(self) -> None:
        payload = {
            "mode": "single",
            "seed": 77,
            "extinct": False,
            "max_generation": 5,
            "final_alive": 31,
            "run_summary": {
                "final_dominant_group_signature": "gA",
                "final_dominant_group_share": 0.42,
                "most_stable_group_signature": "gA",
                "most_stable_group_count": 3,
                "most_rising_group_signature": "gC",
                "most_rising_group_count": 2,
                "final_zone_distribution": {"rich": 10, "neutral": 7, "poor": 4},
                "avg_traits": {
                    "speed": 1.01,
                    "metabolism": 0.98,
                    "prudence": 1.02,
                    "dominance": 1.03,
                    "repro_drive": 0.99,
                },
                "observed_logs": 6,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "single.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "single")
        self.assertEqual(int(loaded["seed"]), 77)
        self.assertIn("=== Export Analysis (single) ===", summary)
        self.assertIn("seed=77", summary)
        self.assertIn("synthese_run:", summary)
        self.assertIn("dominant_final=gA", summary)

    def test_load_multi_json_and_build_summary(self) -> None:
        payload = {
            "mode": "multi",
            "seeds": [10, 11, 12],
            "run_count": 3,
            "multi_run_summary": {
                "runs": 3,
                "seeds": [10, 11, 12],
                "extinction_count": 1,
                "extinction_rate": 1.0 / 3.0,
                "avg_max_generation": 6.0,
                "avg_final_population": 24.0,
                "avg_final_traits": {
                    "speed": 1.0,
                    "metabolism": 1.0,
                    "prudence": 1.0,
                    "dominance": 1.0,
                    "repro_drive": 1.0,
                },
                "most_frequent_final_dominant_group": "gA",
                "most_frequent_final_dominant_group_count": 2,
                "most_frequent_final_dominant_group_share": 2.0 / 3.0,
            },
            "per_run": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "multi")
        self.assertEqual(loaded["seeds"], [10, 11, 12])
        self.assertIn("=== Export Analysis (multi) ===", summary)
        self.assertIn("runs=3 seeds=10,11,12", summary)
        self.assertIn("multi_runs:", summary)
        self.assertIn("extinctions=1/3", summary)

    def test_load_batch_json_and_build_summary(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [1.0, 1.5],
            "runs_per_value": 2,
            "comparative_summary": {
                "batch_param": "energy_drain_rate",
                "evaluated_values_count": 2,
                "most_stable": {
                    "winners": [1.0],
                    "extinction_rate": 0.0,
                    "avg_final_population": 44.5,
                    "avg_max_generation": 3.0,
                },
                "best_avg_max_generation": {
                    "winners": [1.0],
                    "avg_max_generation": 3.0,
                },
                "best_avg_final_population": {
                    "winners": [1.0],
                    "avg_final_population": 44.5,
                },
                "lowest_extinction_rate": {
                    "winners": [1.0, 1.5],
                    "extinction_rate": 0.0,
                },
            },
            "scenarios": [
                {
                    "parameter_value": 1.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 3.0,
                        "avg_final_population": 44.5,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 1.5,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("=== Export Analysis (batch) ===", summary)
        self.assertIn("param=energy_drain_rate values=1.0,1.5 runs_per_value=2", summary)
        self.assertIn("energy_drain_rate=1.0", summary)
        self.assertIn("energy_drain_rate=1.5", summary)
        self.assertIn("--- Batch Comparative Summary ---", summary)
        self.assertIn("batch_comparatif:", summary)
        self.assertIn("plus_stable:", summary)

    def test_load_multi_csv_preserves_memory_impact(self) -> None:
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
                    "repro_drive": 1.0,
                },
                "avg_memory_impact": {
                    "food_usage_total": 8.0,
                    "danger_usage_total": 3.0,
                    "food_active_share": 0.25,
                    "danger_active_share": 0.15,
                    "food_effect_avg_distance": 1.2,
                    "danger_effect_avg_distance": 0.6,
                    "food_usage_per_tick": 0.4,
                    "danger_usage_per_tick": 0.2,
                },
                "most_frequent_final_dominant_group": "gA",
                "most_frequent_final_dominant_group_count": 2,
                "most_frequent_final_dominant_group_share": 1.0,
            },
            "per_run": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi.csv"
            export_results(payload, str(path), "csv")

            loaded = load_export_payload(str(path), input_format="csv")
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "multi")
        avg_memory = loaded["multi_run_summary"]["avg_memory_impact"]
        self.assertAlmostEqual(float(avg_memory["food_usage_total"]), 8.0)
        self.assertAlmostEqual(float(avg_memory["danger_usage_total"]), 3.0)
        self.assertIn("memoire_moy:", summary)

    def test_batch_memory_analysis_shows_memory_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "food_memory_duration",
            "batch_values": [0.0, 8.0],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_memory_impact": {
                            "food_usage_total": 1.0,
                            "danger_usage_total": 0.5,
                            "food_effect_avg_distance": 0.2,
                            "danger_effect_avg_distance": 0.1,
                            "food_active_share": 0.0,
                            "danger_active_share": 0.0,
                            "food_usage_per_tick": 0.1,
                            "danger_usage_per_tick": 0.05,
                        },
                        "avg_trait_impact": {
                            "memory_focus_food_bias": -0.04,
                            "memory_focus_danger_bias": -0.01,
                            "social_sensitivity_follow_bias": -0.02,
                            "social_sensitivity_flee_boost_bias": -0.01,
                            "memory_focus_std": 0.03,
                            "social_sensitivity_std": 0.04,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 8.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_memory_impact": {
                            "food_usage_total": 5.0,
                            "danger_usage_total": 3.0,
                            "food_effect_avg_distance": 1.1,
                            "danger_effect_avg_distance": 0.7,
                            "food_active_share": 0.0,
                            "danger_active_share": 0.0,
                            "food_usage_per_tick": 0.4,
                            "danger_usage_per_tick": 0.2,
                        },
                        "avg_trait_impact": {
                            "memory_focus_food_bias": 0.08,
                            "memory_focus_danger_bias": 0.06,
                            "social_sensitivity_follow_bias": 0.03,
                            "social_sensitivity_flee_boost_bias": 0.02,
                            "memory_focus_std": 0.10,
                            "social_sensitivity_std": 0.09,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_memory.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("memoire_batch:", summary)
        self.assertIn("usage_memoire_utile_max:", summary)
        self.assertIn("effet_memoire_dangereuse_max:", summary)
        self.assertIn("traits_batch:", summary)
        self.assertIn("bias_usage_memoire_max:", summary)

    def test_batch_social_analysis_shows_social_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "social_follow_strength",
            "batch_values": [0.0, 0.35],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_social_impact": {
                            "follow_usage_total": 1.0,
                            "flee_boost_usage_total": 0.5,
                            "influenced_count_last_tick": 0.0,
                            "influenced_share_last_tick": 0.05,
                            "influenced_per_tick": 0.1,
                            "follow_usage_per_tick": 0.05,
                            "flee_boost_usage_per_tick": 0.03,
                            "flee_multiplier_avg_tick": 1.01,
                            "flee_multiplier_avg_total": 1.02,
                        },
                        "avg_trait_impact": {
                            "memory_focus_food_bias": -0.01,
                            "memory_focus_danger_bias": -0.01,
                            "social_sensitivity_follow_bias": -0.02,
                            "social_sensitivity_flee_boost_bias": -0.01,
                            "memory_focus_std": 0.04,
                            "social_sensitivity_std": 0.03,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.35,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_social_impact": {
                            "follow_usage_total": 5.0,
                            "flee_boost_usage_total": 3.0,
                            "influenced_count_last_tick": 3.0,
                            "influenced_share_last_tick": 0.3,
                            "influenced_per_tick": 0.9,
                            "follow_usage_per_tick": 0.25,
                            "flee_boost_usage_per_tick": 0.15,
                            "flee_multiplier_avg_tick": 1.08,
                            "flee_multiplier_avg_total": 1.16,
                        },
                        "avg_trait_impact": {
                            "memory_focus_food_bias": 0.02,
                            "memory_focus_danger_bias": 0.01,
                            "social_sensitivity_follow_bias": 0.08,
                            "social_sensitivity_flee_boost_bias": 0.04,
                            "memory_focus_std": 0.11,
                            "social_sensitivity_std": 0.12,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_social.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("social_batch:", summary)
        self.assertIn("usage_suivi_social_max:", summary)
        self.assertIn("usage_boost_fuite_social_max:", summary)
        self.assertIn("part_creatures_influencees_max:", summary)
        self.assertIn("effet_multiplicateur_fuite_max:", summary)
        self.assertIn("traits_batch:", summary)
        self.assertIn("bias_usage_social_max:", summary)

    def test_batch_energy_analysis_shows_energy_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [0.9, 1.1],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.9,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "energy_drain_multiplier_observed": 0.96,
                            "reproduction_cost_multiplier_observed": 0.99,
                            "energy_efficiency_std": 0.09,
                            "exhaustion_resistance_std": 0.07,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 1.1,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 3.0,
                        "avg_final_population": 12.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "energy_drain_multiplier_observed": 1.01,
                            "reproduction_cost_multiplier_observed": 0.91,
                            "energy_efficiency_std": 0.06,
                            "exhaustion_resistance_std": 0.08,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_energy.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("energie_batch:", summary)
        self.assertIn("effet_drain_energie_max:", summary)
        self.assertIn("effet_cout_reproduction_max:", summary)
        self.assertIn("dispersion_energie_max:", summary)
        self.assertIn("configuration_plus_stable:", summary)

    def test_batch_perception_analysis_shows_perception_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [1.0, 1.2],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 1.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 22.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "food_perception_detection_bias": 0.06,
                            "food_perception_consumption_bias": 0.04,
                            "threat_perception_flee_bias": 0.02,
                            "food_perception_std": 0.10,
                            "threat_perception_std": 0.09,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 1.2,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 3.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "food_perception_detection_bias": 0.03,
                            "food_perception_consumption_bias": 0.01,
                            "threat_perception_flee_bias": 0.08,
                            "food_perception_std": 0.07,
                            "threat_perception_std": 0.12,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_perception.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("perception_batch:", summary)
        self.assertIn("usage_food_perception_max:", summary)
        self.assertIn("usage_threat_perception_max:", summary)
        self.assertIn("dispersion_perception_max:", summary)

    def test_batch_behavior_persistence_analysis_shows_behavior_persistence_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "search_wander_switches_prevented_total": 2.0,
                            "behavior_persistence_oscillation_switch_rate": 0.82,
                            "behavior_persistence_oscillation_prevented_rate": 0.18,
                            "search_wander_oscillation_events_total": 10.0,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "search_wander_switches_prevented_total": 8.0,
                            "behavior_persistence_oscillation_switch_rate": 0.35,
                            "behavior_persistence_oscillation_prevented_rate": 0.65,
                            "search_wander_oscillation_events_total": 22.0,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_behavior_persistence.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("behavior_persistence_batch:", summary)
        self.assertIn("switchs_evites_max:", summary)
        self.assertIn("taux_switch_min:", summary)
        self.assertIn("taux_blocage_utile_max:", summary)
        self.assertIn("configuration_plus_stable:", summary)


    def test_batch_exploration_analysis_shows_exploration_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "exploration_bias_guided_total": 5.0,
                            "exploration_bias_explore_share": 0.25,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "exploration_bias_guided_total": 12.0,
                            "exploration_bias_explore_share": 0.65,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_exploration.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("exploration_bias_batch:", summary)
        self.assertIn("usage_explore_max:", summary)
        self.assertIn("usage_settle_max:", summary)
        self.assertIn("usage_guided_max:", summary)

    def test_batch_density_preference_analysis_shows_density_preference_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "density_preference_guided_total": 4.0,
                            "density_preference_seek_usage_per_tick": 0.35,
                            "density_preference_avoid_usage_per_tick": 0.10,
                            "density_preference_avoid_share": 0.22,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "density_preference_guided_total": 10.0,
                            "density_preference_seek_usage_per_tick": 0.20,
                            "density_preference_avoid_usage_per_tick": 0.40,
                            "density_preference_avoid_share": 0.67,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_density_preference.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("density_preference_batch:", summary)
        self.assertIn("usage_seek_max:", summary)
        self.assertIn("usage_avoid_max:", summary)
        self.assertIn("part_avoid_max:", summary)

    def test_batch_longevity_analysis_shows_longevity_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "longevity_factor_std": 0.04,
                            "age_wear_usage_per_tick": 0.20,
                            "age_wear_multiplier_observed": 0.95,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "longevity_factor_std": 0.08,
                            "age_wear_usage_per_tick": 0.25,
                            "age_wear_multiplier_observed": 0.82,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_longevity.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("longevity_factor_batch:", summary)
        self.assertIn("effet_usure_age_max:", summary)
        self.assertIn("reduction_drain_age_max:", summary)
        self.assertIn("dispersion_longevite_max:", summary)

    def test_batch_environmental_tolerance_analysis_shows_environmental_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "environmental_tolerance_std": 0.05,
                            "poor_zone_drain_usage_per_tick": 0.15,
                            "rich_zone_drain_usage_per_tick": 0.08,
                            "environmental_tolerance_poor_drain_bias": 0.06,
                            "environmental_tolerance_rich_drain_bias": 0.03,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "environmental_tolerance_std": 0.09,
                            "poor_zone_drain_usage_per_tick": 0.35,
                            "rich_zone_drain_usage_per_tick": 0.32,
                            "environmental_tolerance_poor_drain_bias": 0.09,
                            "environmental_tolerance_rich_drain_bias": 0.07,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_environmental_tolerance.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("environmental_tolerance_batch:", summary)
        self.assertIn("effet_zone_pauvre_max:", summary)
        self.assertIn("effet_zone_riche_max:", summary)
        self.assertIn("dispersion_tolerance_env_max:", summary)

    def test_batch_reproduction_timing_analysis_shows_reproduction_timing_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "reproduction_timing_std": 0.03,
                            "reproduction_timing_threshold_multiplier_observed": 0.98,
                            "reproduction_timing_reproduction_bias": -0.02,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "reproduction_timing_std": 0.07,
                            "reproduction_timing_threshold_multiplier_observed": 1.05,
                            "reproduction_timing_reproduction_bias": 0.04,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_reproduction_timing.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("reproduction_timing_batch:", summary)
        self.assertIn("effet_seuil_reproductif_max:", summary)
        self.assertIn("reproduction_plus_precoce_max:", summary)
        self.assertIn("reproduction_plus_prudente_max:", summary)

    def test_batch_mobility_analysis_shows_mobility_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "mobility_efficiency_std": 0.03,
                            "movement_distance_observed": 0.8,
                            "movement_usage_per_tick": 1.7,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "mobility_efficiency_std": 0.07,
                            "movement_distance_observed": 1.2,
                            "movement_usage_per_tick": 2.1,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_mobility_efficiency.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("mobility_efficiency_batch:", summary)
        self.assertIn("distance_deplacement_observee_max:", summary)
        self.assertIn("frequence_mouvement_utile_max:", summary)
        self.assertIn("dispersion_mobilite_max:", summary)

    def test_batch_stress_tolerance_analysis_shows_stress_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "stress_tolerance_std": 0.03,
                            "stress_tolerance_pressure_mean": 0.97,
                            "stress_tolerance_pressure_flee_bias": -0.04,
                            "stress_pressure_events": 5.0,
                            "stress_pressure_flee_rate": 0.42,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "stress_tolerance_std": 0.08,
                            "stress_tolerance_pressure_mean": 1.10,
                            "stress_tolerance_pressure_flee_bias": -0.07,
                            "stress_pressure_events": 8.0,
                            "stress_pressure_flee_rate": 0.60,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_stress_tolerance.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("stress_tolerance_batch:", summary)
        self.assertIn("effet_sous_pression_max:", summary)
        self.assertIn("modulation_fuite_tendue_max:", summary)
        self.assertIn("dispersion_stress_tolerance_max:", summary)

    def test_batch_hunger_sensitivity_analysis_shows_hunger_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 8.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "hunger_sensitivity_std": 0.03,
                            "hunger_sensitivity_search_bias": 0.04,
                            "hunger_search_usage_per_tick": 1.1,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "avg_trait_impact": {
                            "hunger_sensitivity_std": 0.07,
                            "hunger_sensitivity_search_bias": -0.06,
                            "hunger_search_usage_per_tick": 1.4,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_hunger_sensitivity.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("hunger_sensitivity_batch:", summary)
        self.assertIn("effet_seuil_faim_max:", summary)
        self.assertIn("recherche_plus_precoce_max:", summary)
        self.assertIn("recherche_plus_tardive_max:", summary)
        self.assertIn("frequence_recherche_faim_max:", summary)
        self.assertIn("dispersion_hunger_sensitivity_max:", summary)

    def test_batch_competition_analysis_from_csv_shows_competition_comparative(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 9.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                            "competition_tolerance": 0.96,
                        },
                        "avg_trait_impact": {
                            "competition_tolerance_mean": 0.96,
                            "competition_tolerance_std": 0.03,
                            "competition_tolerance_guided_total": 4.0,
                            "competition_tolerance_guided_bias": -0.02,
                            "competition_tolerance_stay_total": 1.0,
                            "competition_tolerance_avoid_total": 3.0,
                            "competition_tolerance_stay_usage_per_tick": 0.18,
                            "competition_tolerance_avoid_usage_per_tick": 0.26,
                            "competition_tolerance_stay_share": 0.25,
                            "competition_tolerance_avoid_share": 0.75,
                            "competition_tolerance_stay_users_avg": 0.94,
                            "competition_tolerance_avoid_users_avg": 1.02,
                            "competition_tolerance_stay_usage_bias": 0.01,
                            "competition_tolerance_avoid_usage_bias": -0.04,
                            "competition_tolerance_neighbor_count_avg": 1.4,
                            "competition_tolerance_anchor_distance_delta": 0.12,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 19.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                            "competition_tolerance": 1.06,
                        },
                        "avg_trait_impact": {
                            "competition_tolerance_mean": 1.06,
                            "competition_tolerance_std": 0.07,
                            "competition_tolerance_guided_total": 10.0,
                            "competition_tolerance_guided_bias": 0.05,
                            "competition_tolerance_stay_total": 7.0,
                            "competition_tolerance_avoid_total": 3.0,
                            "competition_tolerance_stay_usage_per_tick": 0.34,
                            "competition_tolerance_avoid_usage_per_tick": 0.12,
                            "competition_tolerance_stay_share": 0.7,
                            "competition_tolerance_avoid_share": 0.3,
                            "competition_tolerance_stay_users_avg": 1.11,
                            "competition_tolerance_avoid_users_avg": 0.97,
                            "competition_tolerance_stay_usage_bias": 0.06,
                            "competition_tolerance_avoid_usage_bias": -0.02,
                            "competition_tolerance_neighbor_count_avg": 2.6,
                            "competition_tolerance_anchor_distance_delta": -0.05,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_competition.csv"
            export_results(payload, str(path), "csv")

            loaded = load_export_payload(str(path), input_format="csv")
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        scenarios = loaded["scenarios"]
        self.assertIsInstance(scenarios, list)
        assert isinstance(scenarios, list)
        self.assertEqual(len(scenarios), 2)
        first_impact = scenarios[0]["multi_run_summary"]["avg_trait_impact"]
        self.assertAlmostEqual(float(first_impact["competition_tolerance_mean"]), 0.96)
        self.assertAlmostEqual(float(first_impact["competition_tolerance_neighbor_count_avg"]), 1.4)
        self.assertAlmostEqual(float(first_impact["competition_tolerance_stay_share"]), 0.25)
        self.assertAlmostEqual(float(first_impact["competition_tolerance_avoid_share"]), 0.75)
        self.assertAlmostEqual(float(first_impact["competition_tolerance_anchor_distance_delta"]), 0.12)
        self.assertIn("competition_tolerance_batch:", summary)
        self.assertIn("usage_stay_competition_max:", summary)
        self.assertIn("usage_avoid_competition_max:", summary)
        self.assertIn("presence_locale_disputee_max:", summary)
        self.assertIn("dispersion_competition_tolerance_max:", summary)

    def test_batch_density_and_gregarious_analysis_from_csv_preserves_metrics(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "mutation_variation",
            "batch_values": [0.05, 0.10],
            "runs_per_value": 2,
            "scenarios": [
                {
                    "parameter_value": 0.05,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 9.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                            "density_preference": 0.97,
                            "gregariousness": 1.04,
                            "resource_commitment": 0.96,
                        },
                        "avg_trait_impact": {
                            "density_preference_guided_total": 4.0,
                            "density_preference_seek_usage_per_tick": 0.28,
                            "density_preference_avoid_usage_per_tick": 0.16,
                            "density_preference_avoid_share": 0.36,
                            "gregariousness_mean": 1.04,
                            "gregariousness_std": 0.03,
                            "gregariousness_guided_total": 5.0,
                            "gregariousness_seek_usage_per_tick": 0.21,
                            "gregariousness_avoid_usage_per_tick": 0.09,
                            "gregariousness_seek_usage_bias": 0.02,
                            "gregariousness_avoid_usage_bias": -0.02,
                            "gregariousness_center_distance_delta": -0.05,
                            "resource_commitment_mean": 0.96,
                            "resource_commitment_guided_total": 6.0,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 0.10,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 4.0,
                        "avg_final_population": 19.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                            "density_preference": 1.05,
                            "gregariousness": 0.94,
                            "resource_commitment": 1.08,
                        },
                        "avg_trait_impact": {
                            "density_preference_guided_total": 10.0,
                            "density_preference_seek_usage_per_tick": 0.14,
                            "density_preference_avoid_usage_per_tick": 0.33,
                            "density_preference_avoid_share": 0.70,
                            "gregariousness_mean": 0.94,
                            "gregariousness_std": 0.07,
                            "gregariousness_guided_total": 10.0,
                            "gregariousness_seek_usage_per_tick": 0.12,
                            "gregariousness_avoid_usage_per_tick": 0.30,
                            "gregariousness_seek_usage_bias": -0.01,
                            "gregariousness_avoid_usage_bias": -0.09,
                            "gregariousness_center_distance_delta": 0.11,
                            "resource_commitment_mean": 1.08,
                            "resource_commitment_guided_total": 12.0,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch_density_gregarious.csv"
            export_results(payload, str(path), "csv")

            loaded = load_export_payload(str(path), input_format="csv")
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        scenarios = loaded["scenarios"]
        self.assertIsInstance(scenarios, list)
        assert isinstance(scenarios, list)
        self.assertEqual(len(scenarios), 2)

        first_traits = scenarios[0]["multi_run_summary"]["avg_final_traits"]
        first_impact = scenarios[0]["multi_run_summary"]["avg_trait_impact"]

        self.assertAlmostEqual(float(first_traits["density_preference"]), 0.97)
        self.assertAlmostEqual(float(first_traits["gregariousness"]), 1.04)
        self.assertAlmostEqual(float(first_traits["resource_commitment"]), 0.96)
        self.assertAlmostEqual(float(first_impact["density_preference_guided_total"]), 4.0)
        self.assertAlmostEqual(float(first_impact["gregariousness_guided_total"]), 5.0)
        self.assertAlmostEqual(float(first_impact["resource_commitment_guided_total"]), 6.0)

        self.assertIn("density_preference_batch:", summary)
        self.assertIn("gregariousness_batch:", summary)

    def test_cli_analysis_on_real_export_json(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "run_export.json"

            run_cmd = [
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
                "--export-path",
                str(export_path),
                "--export-format",
                "json",
            ]
            subprocess.run(
                run_cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            analyze_cmd = [
                sys.executable,
                "analyze_export.py",
                str(export_path),
            ]
            completed = subprocess.run(
                analyze_cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            output = completed.stdout
            self.assertIn("=== Export Analysis (multi) ===", output)
            self.assertIn("runs=2 seeds=100,103", output)
            self.assertIn("multi_runs:", output)


if __name__ == "__main__":
    unittest.main()


