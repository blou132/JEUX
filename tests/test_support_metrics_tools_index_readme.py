from __future__ import annotations

from pathlib import Path
import unittest

from support_metrics_ci_contract_manifest import (
    load_support_metrics_contract_manifest,
)
from tests.support_metrics_output_fragments import assert_expected_fragments_present


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
EXPECTED_FRAGMENTS_PATH = (
    ROOT / "tests" / "fixtures" / "support_metrics_tools_index_expected_fragments.txt"
)


class SupportMetricsToolsIndexReadmeTests(unittest.TestCase):
    def test_readme_contains_support_metrics_tools_index_fragments(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        assert_expected_fragments_present(self, content, EXPECTED_FRAGMENTS_PATH)

    def test_readme_contains_manifest_tools_and_invariants(self) -> None:
        result = load_support_metrics_contract_manifest(ROOT)
        self.assertTrue(result.is_valid, msg="\n".join(result.issues))
        assert result.manifest is not None

        readme_content = README_PATH.read_text(encoding="utf-8")
        for tool_path in result.manifest["tools"]:
            self.assertIn(tool_path, readme_content)
        for invariant in result.manifest["expected_invariants"]:
            self.assertIn(invariant, readme_content)


if __name__ == "__main__":
    unittest.main()
