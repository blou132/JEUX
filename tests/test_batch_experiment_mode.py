import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BatchExperimentModeTests(unittest.TestCase):
    def test_cli_batch_mode_outputs_summary_per_value(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--batch-param",
            "energy_drain_rate",
            "--batch-values",
            "1.0,1.5",
            "--batch-runs",
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
            timeout=180,
        )

        output = completed.stdout
        self.assertIn("=== Batch Experimental Mode ===", output)
        self.assertIn("param=energy_drain_rate", output)
        self.assertIn("--- Batch Value 1/2: energy_drain_rate=1.0 ---", output)
        self.assertIn("--- Batch Value 2/2: energy_drain_rate=1.5 ---", output)
        self.assertIn("--- Batch Summary ---", output)
        self.assertIn("energy_drain_rate=1.0 runs=2", output)
        self.assertIn("energy_drain_rate=1.5 runs=2", output)
        self.assertIn("--- Batch Comparative Summary ---", output)
        self.assertIn("batch_comparatif:", output)
        self.assertIn("plus_stable:", output)
        self.assertIn("meilleure_gen_max_moy:", output)
        self.assertIn("meilleure_pop_finale_moy:", output)
        self.assertIn("plus_faible_taux_extinction:", output)
        self.assertIn("energie_batch:", output)
        self.assertIn("effet_drain_energie_max:", output)
        self.assertIn("effet_cout_reproduction_max:", output)
        self.assertIn("dispersion_energie_max:", output)
        self.assertIn("exploration_bias_batch:", output)
        self.assertIn("usage_explore_max:", output)
        self.assertIn("usage_settle_max:", output)
        self.assertIn("usage_guided_max:", output)
        self.assertIn("density_preference_batch:", output)
        self.assertIn("usage_seek_max:", output)
        self.assertIn("usage_avoid_max:", output)
        self.assertIn("part_avoid_max:", output)
        self.assertIn("longevity_factor_batch:", output)
        self.assertIn("effet_usure_age_max:", output)
        self.assertIn("reduction_drain_age_max:", output)
        self.assertIn("dispersion_longevite_max:", output)
        self.assertIn("reproduction_timing_batch:", output)
        self.assertIn("effet_seuil_reproductif_max:", output)
        self.assertIn("reproduction_plus_precoce_max:", output)
        self.assertIn("reproduction_plus_prudente_max:", output)

    def test_batch_mode_json_export_created_and_coherent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "batch_experiment.json"
            cmd = [
                sys.executable,
                "main.py",
                "--batch-param",
                "energy_drain_rate",
                "--batch-values",
                "1.0,1.5",
                "--batch-runs",
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

            completed = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )

            output = completed.stdout
            self.assertTrue(export_path.exists())
            self.assertIn("export:", output)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "batch")
            self.assertEqual(payload["batch_param"], "energy_drain_rate")
            self.assertEqual(payload["runs_per_value"], 2)
            self.assertEqual(payload["batch_values"], [1.0, 1.5])

            scenarios = payload["scenarios"]
            self.assertEqual(len(scenarios), 2)
            self.assertEqual(float(scenarios[0]["parameter_value"]), 1.0)
            self.assertEqual(float(scenarios[1]["parameter_value"]), 1.5)
            self.assertEqual(scenarios[0]["seeds"], [100, 103])
            self.assertEqual(int(scenarios[0]["multi_run_summary"]["runs"]), 2)
            self.assertEqual(int(scenarios[1]["multi_run_summary"]["runs"]), 2)

            comparative = payload.get("comparative_summary")
            self.assertIsInstance(comparative, dict)
            self.assertEqual(comparative.get("batch_param"), "energy_drain_rate")
            self.assertIn("most_stable", comparative)
            self.assertIn("best_avg_max_generation", comparative)
            self.assertIn("best_avg_final_population", comparative)
            self.assertIn("lowest_extinction_rate", comparative)
            energy = comparative.get("energy_comparative")
            self.assertIsInstance(energy, dict)
            density = comparative.get("density_preference_comparative")
            self.assertIsInstance(density, dict)
            longevity = comparative.get("longevity_comparative")
            self.assertIsInstance(longevity, dict)
            reproduction_timing = comparative.get("reproduction_timing_comparative")
            self.assertIsInstance(reproduction_timing, dict)
            assert isinstance(energy, dict)
            self.assertIn("available", energy)

    def test_cli_memory_batch_outputs_memory_comparative(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--batch-param",
            "food_memory_duration",
            "--batch-values",
            "0,8",
            "--batch-runs",
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
            timeout=180,
        )

        output = completed.stdout
        self.assertIn("param=food_memory_duration", output)
        self.assertIn("--- Batch Comparative Summary ---", output)
        self.assertIn("memoire_batch:", output)
        self.assertIn("usage_memoire_utile_max:", output)
        self.assertIn("usage_memoire_dangereuse_max:", output)
        self.assertIn("effet_memoire_utile_max:", output)
        self.assertIn("effet_memoire_dangereuse_max:", output)
        self.assertIn("traits_batch:", output)
        self.assertIn("bias_usage_memoire_max:", output)
        self.assertIn("bias_usage_social_max:", output)
        self.assertIn("dispersion_traits_max:", output)

    def test_memory_batch_json_export_contains_memory_comparative(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "batch_memory.json"
            cmd = [
                sys.executable,
                "main.py",
                "--batch-param",
                "food_memory_duration",
                "--batch-values",
                "0,8",
                "--batch-runs",
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
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )

            payload = json.loads(export_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "batch")
        self.assertEqual(payload["batch_param"], "food_memory_duration")

        comparative = payload.get("comparative_summary")
        self.assertIsInstance(comparative, dict)
        assert isinstance(comparative, dict)
        memory = comparative.get("memory_comparative")
        self.assertIsInstance(memory, dict)
        assert isinstance(memory, dict)
        self.assertIn("available", memory)

        trait = comparative.get("trait_comparative")
        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertIn("available", trait)

    def test_cli_social_batch_outputs_social_comparative(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--batch-param",
            "social_follow_strength",
            "--batch-values",
            "0,0.35",
            "--batch-runs",
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
            timeout=180,
        )

        output = completed.stdout
        self.assertIn("param=social_follow_strength", output)
        self.assertIn("--- Batch Comparative Summary ---", output)
        self.assertIn("social_batch:", output)
        self.assertIn("usage_suivi_social_max:", output)
        self.assertIn("usage_boost_fuite_social_max:", output)
        self.assertIn("part_creatures_influencees_max:", output)
        self.assertIn("effet_multiplicateur_fuite_max:", output)
        self.assertIn("traits_batch:", output)
        self.assertIn("bias_usage_memoire_max:", output)
        self.assertIn("bias_usage_social_max:", output)
        self.assertIn("dispersion_traits_max:", output)

    def test_social_batch_json_export_contains_social_comparative(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "batch_social.json"
            cmd = [
                sys.executable,
                "main.py",
                "--batch-param",
                "social_follow_strength",
                "--batch-values",
                "0,0.35",
                "--batch-runs",
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
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )

            payload = json.loads(export_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "batch")
        self.assertEqual(payload["batch_param"], "social_follow_strength")

        comparative = payload.get("comparative_summary")
        self.assertIsInstance(comparative, dict)
        assert isinstance(comparative, dict)
        social = comparative.get("social_comparative")
        self.assertIsInstance(social, dict)
        assert isinstance(social, dict)
        self.assertIn("available", social)

        trait = comparative.get("trait_comparative")
        self.assertIsInstance(trait, dict)
        assert isinstance(trait, dict)
        self.assertIn("available", trait)


if __name__ == "__main__":
    unittest.main()
