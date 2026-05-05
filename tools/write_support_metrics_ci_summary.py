from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


SKIP_REPORT_MESSAGE = "Support metrics exports not found; optional check skipped."


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate support metrics CI summary/report for GitHub Actions."
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline support metrics history JSONL.",
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current support metrics history JSONL.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        required=True,
        help="Path to output markdown report file.",
    )
    parser.add_argument(
        "--step-summary",
        type=Path,
        default=None,
        help="Optional path to GitHub step summary file.",
    )
    parser.add_argument(
        "--artifact-name",
        type=str,
        default="support-metrics-report",
        help="Artifact label displayed in the compact summary.",
    )
    parser.add_argument(
        "--ci-check",
        action="store_true",
        help="Explicit CI check intent flag (kept for workflow readability).",
    )
    return parser


def _run_analyze_command(command_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command_args,
        capture_output=True,
        text=True,
    )


def _map_compact_status(regression_state: str) -> str:
    normalized = regression_state.strip().lower()
    if normalized == "stable":
        return "passed"
    if normalized == "changed":
        return "changed"
    if normalized == "warning":
        return "warning"
    if normalized == "no_baseline":
        return "no_baseline"
    return "warning"


def _append_step_summary(
    step_summary_path: Path,
    compact_status: str,
    artifact_name: str,
    report_content: str,
    reason: str = "",
) -> None:
    lines: list[str] = []
    lines.append("## Support metrics CI status")
    lines.append("- status: %s" % compact_status)
    if reason:
        lines.append("- reason: %s" % reason)
    lines.append("- blocking: no")
    lines.append("- artifact: %s" % artifact_name)
    lines.append("")
    lines.append("## Support metrics report")
    lines.append("")

    step_summary_path.parent.mkdir(parents=True, exist_ok=True)
    with step_summary_path.open("a", encoding="utf-8") as summary_file:
        summary_file.write("\n".join(lines))
        summary_file.write("\n")
        summary_file.write(report_content)
        if report_content and not report_content.endswith("\n"):
            summary_file.write("\n")


def _build_summary_json(
    analyze_script_path: Path,
    baseline_path: Path,
    current_path: Path,
) -> dict[str, Any]:
    json_command = [
        sys.executable,
        str(analyze_script_path),
        "--input",
        str(baseline_path),
        "--compare-input",
        str(current_path),
        "--ci-check",
        "--format",
        "json",
    ]
    json_result = _run_analyze_command(json_command)
    if json_result.returncode != 0:
        error_output = (json_result.stdout + "\n" + json_result.stderr).strip()
        raise RuntimeError("support metrics json analysis failed: %s" % error_output)
    parsed = json.loads(json_result.stdout)
    if not isinstance(parsed, dict):
        raise RuntimeError("support metrics json analysis did not return a JSON object")
    return parsed


def _write_markdown_report(
    analyze_script_path: Path,
    baseline_path: Path,
    current_path: Path,
    report_output_path: Path,
) -> None:
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_command = [
        sys.executable,
        str(analyze_script_path),
        "--input",
        str(baseline_path),
        "--compare-input",
        str(current_path),
        "--ci-check",
        "--format",
        "markdown",
        "--output",
        str(report_output_path),
    ]
    markdown_result = _run_analyze_command(markdown_command)
    if markdown_result.returncode != 0:
        error_output = (markdown_result.stdout + "\n" + markdown_result.stderr).strip()
        raise RuntimeError("support metrics markdown report generation failed: %s" % error_output)


def main() -> int:
    args = _build_parser().parse_args()
    baseline_path: Path = args.baseline
    current_path: Path = args.current
    report_output_path: Path = args.report_output
    step_summary_path: Path | None = args.step_summary
    artifact_name = str(args.artifact_name).strip() or "support-metrics-report"
    _ = bool(args.ci_check)
    analyze_script_path = Path(__file__).with_name("analyze_run_metrics_history.py")

    baseline_exists = baseline_path.exists()
    current_exists = current_path.exists()

    if baseline_exists and current_exists:
        _write_markdown_report(
            analyze_script_path=analyze_script_path,
            baseline_path=baseline_path,
            current_path=current_path,
            report_output_path=report_output_path,
        )
        summary_json = _build_summary_json(
            analyze_script_path=analyze_script_path,
            baseline_path=baseline_path,
            current_path=current_path,
        )
        regression_state = (
            str(
                summary_json
                .get("support_metrics_regression", {})
                .get("regression_state", "warning")
            ).strip()
        )
        compact_status = _map_compact_status(regression_state)
        report_content = report_output_path.read_text(encoding="utf-8")
        if step_summary_path is not None:
            _append_step_summary(
                step_summary_path=step_summary_path,
                compact_status=compact_status,
                artifact_name=artifact_name,
                report_content=report_content,
            )
        return 0

    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    report_output_path.write_text(SKIP_REPORT_MESSAGE + "\n", encoding="utf-8")
    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status="skipped",
            artifact_name=artifact_name,
            report_content=SKIP_REPORT_MESSAGE + "\n",
            reason="exports baseline/current not found",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
