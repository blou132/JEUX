from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"


class RuntimeGodotValidationChecklistReadmeTests(unittest.TestCase):
    def test_readme_contains_v211_runtime_godot_checklist_section(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("Runtime Godot validation checklist for v211", content)
        self.assertIn("godot --version", content)
        self.assertIn(
            "py tools/run_support_metrics_runtime_pipeline.py --dry-run --runs 5 --seed-start 1000 --min-runs 5",
            content,
        )
        self.assertIn(
            "py tools/run_support_metrics_runtime_pipeline.py --runs 5 --seed-start 1000 --min-runs 5",
            content,
        )

    def test_readme_checklist_contains_expected_outputs_and_decisions(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("outputs/ci/support_metrics_baseline.jsonl", content)
        self.assertIn("outputs/ci/support_metrics_current.jsonl", content)
        self.assertIn("outputs/ci/support_metrics_runtime_comparison.md", content)
        self.assertIn("outputs/ci/support_metrics_runtime_decision.md", content)
        self.assertIn("keep_tuning", content)
        self.assertIn("revert_tuning", content)
        self.assertIn("collect_more_runs", content)
        self.assertIn("investigate_metrics", content)

    def test_readme_checklist_reminds_pipeline_does_not_change_gameplay(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("ne pas modifier le gameplay", content)
        self.assertIn("ne modifient pas le gameplay automatiquement", content)

    def test_readme_contains_runtime_collection_diagnose_section(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("Diagnose runtime collection", content)
        self.assertIn("--diagnose", content)
        self.assertIn("--allow-existing-history", content)
        self.assertIn("--history-path", content)
        self.assertIn(
            "py tools/collect_support_metrics_runtime.py --mode current --runs 1 --seed-start 1000 --godot-bin",
            content,
        )
        self.assertIn(
            "si aucune nouvelle ligne n'est ajoutee au history runtime, la decision gameplay doit rester `collect_more_runs`",
            content,
        )


if __name__ == "__main__":
    unittest.main()
