from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


SKIP_REPORT_MESSAGE = "Support metrics exports not found; optional check skipped."
ANALYSIS_FAILED_REASON = "analysis failed"
INDEX_START_MARKER = "<!-- support-metrics-index:start -->"
INDEX_END_MARKER = "<!-- support-metrics-index:end -->"
INDEX_DATA_PREFIX = "<!-- support-metrics-index-data:"
INDEX_DATA_SUFFIX = "-->"
SMOKE_REPORT_NOTE = (
    "Note: this smoke report uses controlled fixtures. "
    "It validates the CI/report pipeline, not live gameplay behavior."
)
SMOKE_SUMMARY_WARNING = (
    "Smoke passed means the reporting pipeline works; "
    "it does not validate runtime gameplay metrics."
)
RUNTIME_NO_EXPORTS_MESSAGE = (
    "Runtime support metrics exports not found; no runtime gameplay metrics were evaluated."
)


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
    parser.add_argument(
        "--report-mode",
        type=str,
        default="",
        help="Optional provenance mode label (example: smoke, runtime, local, manual).",
    )
    parser.add_argument(
        "--input-label",
        type=str,
        default="",
        help="Optional provenance input label forwarded to analysis report.",
    )
    parser.add_argument(
        "--compare-input-label",
        type=str,
        default="",
        help="Optional provenance compare input label forwarded to analysis report.",
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


def _infer_report_mode(artifact_name: str, report_mode_arg: str) -> str:
    explicit_mode = report_mode_arg.strip().lower()
    if explicit_mode:
        return explicit_mode
    normalized_artifact = artifact_name.strip().lower()
    if normalized_artifact == "support-metrics-smoke-report":
        return "smoke"
    if normalized_artifact == "support-metrics-report":
        return "runtime"
    return "manual"


def _build_source_label(report_mode: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode == "smoke":
        return "smoke fixtures"
    if normalized_mode == "runtime":
        return "runtime outputs/ci"
    if normalized_mode == "local":
        return "local simulation"
    return "manual"


def _build_blocking_label(report_mode: str) -> str:
    if report_mode.strip().lower() == "smoke":
        return "yes for technical generation only"
    return "no"


def _build_role_label(report_mode: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode == "smoke":
        return "technical pipeline check only"
    if normalized_mode == "runtime":
        return "runtime metrics report"
    if normalized_mode == "local":
        return "local simulation"
    return "manual analysis"


def _build_report_key(report_mode: str, artifact_name: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode in {"smoke", "runtime", "local"}:
        return normalized_mode
    normalized_artifact = artifact_name.strip().lower()
    if normalized_artifact == "support-metrics-smoke-report":
        return "smoke"
    if normalized_artifact == "support-metrics-report":
        return "runtime"
    return "manual"


def _build_runtime_data_label(report_mode: str, compact_status: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode == "smoke":
        return "no"
    if normalized_mode == "runtime":
        if compact_status == "skipped":
            return "no"
        return "yes"
    if normalized_mode == "local":
        return "depends on input files"
    return "depends on input files"


def _build_gameplay_validation_label(report_mode: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode == "smoke":
        return "no"
    if normalized_mode == "runtime":
        return "observation only"
    if normalized_mode == "local":
        return "no"
    return "observation only"


def _build_skip_message(report_mode: str) -> str:
    normalized_mode = report_mode.strip().lower()
    if normalized_mode == "runtime":
        return RUNTIME_NO_EXPORTS_MESSAGE
    if normalized_mode == "smoke":
        return "Smoke support metrics fixtures not found; technical pipeline check skipped."
    return SKIP_REPORT_MESSAGE


def _prepend_smoke_note_if_needed(report_mode: str, report_content: str) -> str:
    if report_mode.strip().lower() != "smoke":
        return report_content
    if SMOKE_REPORT_NOTE in report_content:
        return report_content
    lines: list[str] = []
    lines.append(SMOKE_REPORT_NOTE)
    lines.append("")
    lines.append(report_content)
    return "\n".join(lines)


def _parse_existing_index_block(content: str) -> tuple[dict[str, dict[str, str]], str]:
    index_rows: dict[str, dict[str, str]] = {}
    start = content.find(INDEX_START_MARKER)
    end = content.find(INDEX_END_MARKER)
    if start == -1 or end == -1 or end < start:
        return index_rows, content

    block_end = end + len(INDEX_END_MARKER)
    block = content[start:block_end]
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if line.startswith(INDEX_DATA_PREFIX) and line.endswith(INDEX_DATA_SUFFIX):
            payload = line[len(INDEX_DATA_PREFIX) : -len(INDEX_DATA_SUFFIX)].strip()
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                parsed = {}
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    if isinstance(key, str) and isinstance(value, dict):
                        row: dict[str, str] = {}
                        for field_name, field_value in value.items():
                            if isinstance(field_name, str):
                                row[field_name] = str(field_value)
                        index_rows[key] = row
            break

    content_without_index = (content[:start] + content[block_end:]).lstrip("\n")
    return index_rows, content_without_index


def _build_index_block(index_rows: dict[str, dict[str, str]]) -> str:
    ordered_keys = [key for key in ["smoke", "runtime", "local", "manual"] if key in index_rows]
    ordered_keys.extend(sorted(key for key in index_rows.keys() if key not in ordered_keys))
    lines: list[str] = []
    lines.append(INDEX_START_MARKER)
    lines.append(
        "%s%s %s"
        % (
            INDEX_DATA_PREFIX,
            json.dumps(index_rows, ensure_ascii=False, sort_keys=True),
            INDEX_DATA_SUFFIX,
        )
    )
    lines.append("## Support metrics reports index")
    lines.append(
        "| report | status | mode | source | artifact | blocking | role | runtime_data | gameplay_validation |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for key in ordered_keys:
        row = index_rows.get(key, {})
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                row.get("report", key),
                row.get("status", "n/a"),
                row.get("mode", "manual"),
                row.get("source", "manual"),
                row.get("artifact", "n/a"),
                row.get("blocking", "no"),
                row.get("role", "manual analysis"),
                row.get("runtime_data", "depends on input files"),
                row.get("gameplay_validation", "observation only"),
            )
        )
    lines.append(INDEX_END_MARKER)
    return "\n".join(lines)


def _append_step_summary(
    step_summary_path: Path,
    compact_status: str,
    artifact_name: str,
    report_content: str,
    reason: str = "",
    report_source: str = "",
    input_label: str = "",
    compare_input_label: str = "",
    report_mode: str = "",
) -> None:
    lines: list[str] = []
    lines.append("## Support metrics CI status")
    lines.append("- status: %s" % compact_status)
    if reason:
        lines.append("- reason: %s" % reason)
    lines.append("- blocking: no")
    lines.append("- artifact: %s" % artifact_name)
    if report_source:
        lines.append("- source: %s" % report_source)
    if input_label:
        lines.append("- input: %s" % input_label)
    if compare_input_label:
        lines.append("- compare input: %s" % compare_input_label)
    if report_mode.strip().lower() == "smoke":
        lines.append("- warning: %s" % SMOKE_SUMMARY_WARNING)
    if report_mode.strip().lower() == "runtime" and compact_status == "skipped":
        lines.append("- warning: %s" % RUNTIME_NO_EXPORTS_MESSAGE)
    lines.append("")
    lines.append("## Support metrics report")
    lines.append("")
    section_text = "\n".join(lines) + "\n" + report_content
    if report_content and not report_content.endswith("\n"):
        section_text += "\n"

    report_key = _build_report_key(report_mode, artifact_name)
    row = {
        "report": report_key,
        "status": compact_status,
        "mode": report_mode or "manual",
        "source": report_source or "manual",
        "artifact": artifact_name,
        "blocking": _build_blocking_label(report_mode),
        "role": _build_role_label(report_mode),
        "runtime_data": _build_runtime_data_label(report_mode, compact_status),
        "gameplay_validation": _build_gameplay_validation_label(report_mode),
    }

    existing_content = ""
    if step_summary_path.exists():
        existing_content = _read_text(step_summary_path)
    existing_index_rows, body_without_index = _parse_existing_index_block(existing_content)
    existing_index_rows[report_key] = row
    index_block = _build_index_block(existing_index_rows)

    if body_without_index.strip():
        body = body_without_index.rstrip("\n") + "\n" + section_text
    else:
        body = section_text
    final_content = index_block + "\n\n" + body.lstrip("\n")
    _write_text(step_summary_path, final_content)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_summary_json(
    analyze_script_path: Path,
    baseline_path: Path,
    current_path: Path,
    report_mode: str,
    input_label: str,
    compare_input_label: str,
) -> dict[str, Any]:
    json_command = [
        sys.executable,
        str(analyze_script_path),
        "--input",
        str(baseline_path),
        "--compare-input",
        str(current_path),
        "--input-label",
        input_label,
        "--compare-input-label",
        compare_input_label,
        "--report-mode",
        report_mode,
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
    report_mode: str,
    input_label: str,
    compare_input_label: str,
) -> None:
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_command = [
        sys.executable,
        str(analyze_script_path),
        "--input",
        str(baseline_path),
        "--compare-input",
        str(current_path),
        "--input-label",
        input_label,
        "--compare-input-label",
        compare_input_label,
        "--report-mode",
        report_mode,
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
    report_source: str,
    input_label: str,
    compare_input_label: str,
    report_mode: str,
) -> int:
    skip_report = _build_skip_message(report_mode) + "\n"
    _write_text(report_output_path, skip_report)
    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status="skipped",
            artifact_name=artifact_name,
            report_content=skip_report,
            reason=_build_skip_message(report_mode),
            report_source=report_source,
            input_label=input_label,
            compare_input_label=compare_input_label,
            report_mode=report_mode,
        )
    return 0


def _handle_analysis_error(
    report_output_path: Path,
    step_summary_path: Path | None,
    artifact_name: str,
    strict_mode: bool,
    error_message: str,
    report_source: str,
    input_label: str,
    compare_input_label: str,
    report_mode: str,
) -> int:
    report_content = _build_minimal_error_report(error_message)
    report_content = _prepend_smoke_note_if_needed(report_mode, report_content)
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
            report_source=report_source,
            input_label=input_label,
            compare_input_label=compare_input_label,
            report_mode=report_mode,
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
    report_mode = _infer_report_mode(artifact_name, str(args.report_mode))
    report_source = _build_source_label(report_mode)
    input_label = str(args.input_label).strip() or str(baseline_path)
    compare_input_label = str(args.compare_input_label).strip() or str(current_path)
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
            report_source=report_source,
            input_label=input_label,
            compare_input_label=compare_input_label,
            report_mode=report_mode,
        )

    try:
        _write_markdown_report(
            analyze_script_path=analyze_script_path,
            baseline_path=baseline_path,
            current_path=current_path,
            report_output_path=report_output_path,
            report_mode=report_mode,
            input_label=input_label,
            compare_input_label=compare_input_label,
        )
        summary_json = _build_summary_json(
            analyze_script_path=analyze_script_path,
            baseline_path=baseline_path,
            current_path=current_path,
            report_mode=report_mode,
            input_label=input_label,
            compare_input_label=compare_input_label,
        )
        regression_state = _extract_regression_state(summary_json)
        compact_status = _map_compact_status(regression_state)
        report_content = _read_text(report_output_path)
        report_content = _prepend_smoke_note_if_needed(report_mode, report_content)
        if report_content != _read_text(report_output_path):
            _write_text(report_output_path, report_content)
    except Exception as exc:  # noqa: BLE001 - fail-safe behavior is intentional
        return _handle_analysis_error(
            report_output_path=report_output_path,
            step_summary_path=step_summary_path,
            artifact_name=artifact_name,
            strict_mode=strict_mode,
            error_message=str(exc),
            report_source=report_source,
            input_label=input_label,
            compare_input_label=compare_input_label,
            report_mode=report_mode,
        )

    if step_summary_path is not None:
        _append_step_summary(
            step_summary_path=step_summary_path,
            compact_status=compact_status,
            artifact_name=artifact_name,
            report_content=report_content,
            report_source=report_source,
            input_label=input_label,
            compare_input_label=compare_input_label,
            report_mode=report_mode,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
