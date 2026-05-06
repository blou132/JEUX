from __future__ import annotations

from pathlib import Path
import unittest

from support_metrics_ci_contract_manifest import (
    load_support_metrics_contract_manifest,
)
from tools.check_support_metrics_ci_fragments import EXPECTED_CATEGORIES


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "tests.yml"


class SupportMetricsCIContractManifestTests(unittest.TestCase):
    def test_manifest_is_valid_json_contract(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        self.assertIsNotNone(result.manifest)

    def test_all_manifest_tools_exist(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None
        for tool_path in result.manifest["tools"]:
            self.assertTrue((ROOT / tool_path).exists(), msg=f"Missing tool from manifest: {tool_path}")

    def test_all_manifest_artifacts_are_in_workflow_and_readme(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None
        workflow_content = WORKFLOW_PATH.read_text(encoding="utf-8")
        readme_content = README_PATH.read_text(encoding="utf-8")
        for artifact_name in result.manifest["artifacts"]:
            self.assertIn(artifact_name, workflow_content)
            self.assertIn(artifact_name, readme_content)

    def test_manifest_fragment_categories_are_covered(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None
        known_categories = set(EXPECTED_CATEGORIES)
        for category in result.manifest["fragment_categories"]:
            self.assertIn(category, known_categories)

    def test_manifest_workflow_steps_exist(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None
        workflow_content = WORKFLOW_PATH.read_text(encoding="utf-8")
        for workflow_step in result.manifest["workflow_steps"]:
            self.assertIn(workflow_step, workflow_content)

    def test_manifest_invariants_exist_in_readme(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None
        readme_content = README_PATH.read_text(encoding="utf-8")
        for invariant in result.manifest["expected_invariants"]:
            self.assertIn(invariant, readme_content)


if __name__ == "__main__":
    unittest.main()
