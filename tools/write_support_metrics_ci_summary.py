from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


SKIP_REPORT_MESSAGE = "Support metrics exports not found; optional check skipped."
ANALYSIS_FAILED_REASON = "analysis failed"


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
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit code on technical analysis errors.",
    )
    parser.add_argument(
        "--analyze-script",
        type=Path,
        default=None,
        help="Optional path override for analyze_run_metrics_history.py (mainly for tests).",
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    try:
        parsed = json.loads(json_result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("support metrics json analysis returned invalid JSON") from exc
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


def _extract_regression_state(summary_json: dict[str, Any]) -> str:
    regression = summary_json.get("support_metrics_regression")
    if not isinstance(regression, dict):
        raise RuntimeError("support_metrics_regression block is missing")
    regression_state = str(regression.get("regression_state", "")).strip()
    if regression_state == "":
        raise RuntimeError("support_metrics_regression.regression_state is missing")
    return regression_state


def _build_minimal_error_report(error_message: str) -> str:
    lines: list[str] = []
    lines.append("# Support Metrics CI report")
    lines.append("")
    lines.append("Support metrics CI check failed")
    lines.append("")
    lines.append("- reason: analysis failed")
    lines.append("- blocking: no")
    lines.append("- status: warning")
    lines.append("- detail: %s" % error_message)
    lines.append("")
    lines.append("This report is debug/observation only.")
    return "\n".join(lines) + "\n"


def _handle_skip(
    report_output_path: Path,
    step_summary_path: Path | None,
    artifact_name: str,
) -> int:
    skip_report = SKIP_REPORT_MESSAGE + "\n"
    _write_text(report_output_path, skip_report)
    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status="skipped",
            artifact_name=artifact_name,
            report_content=skip_report,
            reason="exports baseline/current not found",
        )
    return 0


def _handle_analysis_error(
    report_output_path: Path,
    step_summary_path: Path | None,
    artifact_name: str,
    strict_mode: bool,
    error_message: str,
) -> int:
    report_content = _build_minimal_error_report(error_message)
    write_error_message = ""
    try:
        _write_text(report_output_path, report_content)
    except OSError as exc:
        write_error_message = "unable to write report file: %s" % str(exc)
        report_content += "\nReport write error: %s\n" % write_error_message

    reason = ANALYSIS_FAILED_REASON
    if write_error_message:
        reason = "%s (%s)" % (ANALYSIS_FAILED_REASON, write_error_message)
    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status="warning",
            artifact_name=artifact_name,
            report_content=report_content,
            reason=reason,
        )
    if strict_mode:
        return 1
    return 0


def main() -> int:
    args = _build_parser().parse_args()
    baseline_path: Path = args.baseline
    current_path: Path = args.current
    report_output_path: Path = args.report_output
    step_summary_path: Path | None = args.step_summary
    artifact_name = str(args.artifact_name).strip() or "support-metrics-report"
    strict_mode = bool(args.strict)
    _ = bool(args.ci_check)

    analyze_script_path = (
        args.analyze_script
        if args.analyze_script is not None
        else Path(__file__).with_name("analyze_run_metrics_history.py")
    )

    baseline_exists = baseline_path.exists()
    current_exists = current_path.exists()
    if not baseline_exists or not current_exists:
        return _handle_skip(
            report_output_path=report_output_path,
            step_summary_path=step_summary_path,
            artifact_name=artifact_name,
        )

    try:
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
        regression_state = _extract_regression_state(summary_json)
        compact_status = _map_compact_status(regression_state)
        report_content = _read_text(report_output_path)
    except Exception as exc:  # noqa: BLE001 - fail-safe behavior is intentional
        return _handle_analysis_error(
            report_output_path=report_output_path,
            step_summary_path=step_summary_path,
            artifact_name=artifact_name,
            strict_mode=strict_mode,
            error_message=str(exc),
        )

    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status=compact_status,
            artifact_name=artifact_name,
            report_content=report_content,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
