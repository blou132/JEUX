from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from support_metrics_ci_contract_manifest import (  # noqa: E402
    REQUIRED_MANIFEST_KEYS,
    load_support_metrics_contract_manifest,
)


STATE_OK = "ok"
STATE_ERROR = "error"


@dataclass
class SupportMetricsManifestCheck:
    overall: str
    manifest_path: str
    required_keys: list[str]
    present_keys: list[str]
    tools_count: int
    artifacts_count: int
    fragment_categories_count: int
    workflow_steps_count: int
    expected_invariants_count: int
    report_modes_count: int
    issues: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate support metrics CI contract manifest structure and "
            "referenced tool paths."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when manifest contract is invalid.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed issues when available.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to validate (default: current repository root).",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=None,
        help="Optional path to write a compact Markdown manifest report.",
    )
    return parser


def build_manifest_check(root: Path) -> SupportMetricsManifestCheck:
    load_result = load_support_metrics_contract_manifest(root)
    issues = list(load_result.issues)
    manifest = load_result.manifest if load_result.manifest is not None else {}

    tools = manifest.get("tools", [])
    artifacts = manifest.get("artifacts", [])
    fragment_categories = manifest.get("fragment_categories", [])
    workflow_steps = manifest.get("workflow_steps", [])
    expected_invariants = manifest.get("expected_invariants", [])
    report_modes = manifest.get("report_modes", [])

    if isinstance(tools, list):
        for raw_tool_path in tools:
            if not isinstance(raw_tool_path, str):
                continue
            tool_path = raw_tool_path.strip()
            if tool_path == "":
                continue
            if not (root / tool_path).exists():
                issues.append("manifest tool path is missing on disk: %s" % tool_path)

    overall = STATE_OK if len(issues) == 0 else STATE_ERROR
    present_keys = sorted(manifest.keys()) if isinstance(manifest, dict) else []

    return SupportMetricsManifestCheck(
        overall=overall,
        manifest_path=str(load_result.path),
        required_keys=list(REQUIRED_MANIFEST_KEYS),
        present_keys=present_keys,
        tools_count=len(tools) if isinstance(tools, list) else 0,
        artifacts_count=len(artifacts) if isinstance(artifacts, list) else 0,
        fragment_categories_count=(
            len(fragment_categories) if isinstance(fragment_categories, list) else 0
        ),
        workflow_steps_count=len(workflow_steps) if isinstance(workflow_steps, list) else 0,
        expected_invariants_count=(
            len(expected_invariants) if isinstance(expected_invariants, list) else 0
        ),
        report_modes_count=len(report_modes) if isinstance(report_modes, list) else 0,
        issues=issues,
    )


def _print_text_report(check: SupportMetricsManifestCheck, verbose: bool) -> None:
    print("Support metrics CI manifest:")
    print("- path: %s" % check.manifest_path)
    print("- overall: %s" % check.overall)
    print("- required keys: %d" % len(check.required_keys))
    print("- present keys: %d" % len(check.present_keys))
    print("- tools: %d" % check.tools_count)
    print("- artifacts: %d" % check.artifacts_count)
    print("- fragment categories: %d" % check.fragment_categories_count)
    print("- workflow steps: %d" % check.workflow_steps_count)
    print("- expected invariants: %d" % check.expected_invariants_count)
    print("- report modes: %d" % check.report_modes_count)

    if verbose or check.issues:
        print("- issues:")
        if check.issues:
            for issue in check.issues:
                print("  - %s" % issue)
        else:
            print("  - none")


def _build_markdown_report(check: SupportMetricsManifestCheck) -> str:
    lines: list[str] = []
    lines.append("# Support metrics CI manifest")
    lines.append("")
    lines.append("- overall: %s" % check.overall)
    lines.append("- tools: %d" % check.tools_count)
    lines.append("- artifacts: %d" % check.artifacts_count)
    lines.append("- fragment_categories: %d" % check.fragment_categories_count)
    lines.append("- workflow_steps: %d" % check.workflow_steps_count)
    lines.append("- expected_invariants: %d" % check.expected_invariants_count)
    lines.append("- report_modes: %d" % check.report_modes_count)
    lines.append("- interpretation: maintenance CI/debug only, not gameplay validation")
    return "\n".join(lines) + "\n"


def _write_markdown_report(path: Path, check: SupportMetricsManifestCheck) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_build_markdown_report(check), encoding="utf-8")


def main() -> int:
    args = _build_parser().parse_args()
    check = build_manifest_check(args.root)

    if args.markdown_output is not None:
        _write_markdown_report(args.markdown_output, check)

    if args.json:
        print(json.dumps(check.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(check, verbose=args.verbose)

    if args.check and check.overall != STATE_OK:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
