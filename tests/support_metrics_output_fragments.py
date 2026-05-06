from __future__ import annotations

from pathlib import Path
import unittest


def load_expected_fragments(path: Path) -> list[str]:
    fragments: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "" or line.startswith("#"):
            continue
        fragments.append(line)
    return fragments


def assert_expected_fragments_present(
    test_case: unittest.TestCase,
    output_text: str,
    fragments_path: Path,
) -> None:
    fragments = load_expected_fragments(fragments_path)
    test_case.assertGreater(
        len(fragments),
        0,
        msg=f"No expected fragments loaded from {fragments_path}",
    )
    for fragment in fragments:
        test_case.assertIn(
            fragment,
            output_text,
            msg=f"Missing expected fragment in output: {fragment!r}",
        )
