from __future__ import annotations

from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
