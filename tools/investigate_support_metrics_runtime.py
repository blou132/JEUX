from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


DEFAULT_BASELINE_PATH = Path("outputs/ci/support_metrics_baseline.jsonl")
DEFAULT_CURRENT_PATH = Path("outputs/ci/support_metrics_current.jsonl")
DEFAULT_COMPARISON_PATH = Path("outputs/ci/support_metrics_runtime_comparison.md")
DEFAULT_DECISION_PATH = Path("outputs/ci/support_metrics_runtime_decision.md")
DEFAULT_MARKDOWN_OUTPUT = Path("outputs/ci/support_metrics_runtime_investigation.md")

DECISION_INVESTIGATE_METRICS = "investigate_metrics"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a local runtime investigation report when runtime decision is "
            "investigate_metrics. This tool is observation/debug only."
        )
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
        help="Baseline runtime JSONL path.",
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="Current runtime JSONL path.",
    )
    parser.add_argument(
        "--comparison",
        type=Path,
        default=DEFAULT_COMPARISON_PATH,
        help="Runtime comparison Markdown report path.",
    )
    parser.add_argument(
        "--decision",
        type=Path,
        default=DEFAULT_DECISION_PATH,
        help="Runtime decision Markdown report path.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_MARKDOWN_OUTPUT,
        help="Investigation Markdown output path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero if investigation inputs are missing/invalid.",
    )
    return parser


def _normalize_key(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _as_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _as_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item).strip()
        if text != "":
            normalized.append(text)
    return normalized


def _parse_boolish(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "yes"}:
        return True
    if normalized in {"false", "no"}:
        return False
    return None


def _read_text_file(path: Path, label: str) -> str:
    if not path.exists():
        raise RuntimeError("%s file not found: %s" % (label, path))
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("unable to read %s file: %s" % (label, str(exc))) from exc


def _parse_markdown_sections(markdown_content: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_section = "root"
    sections[current_section] = {}
    for raw_line in markdown_content.splitlines():
        line = raw_line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            section_name = line.lstrip("#").strip().lower()
            if section_name == "":
                section_name = "root"
            current_section = section_name
            if current_section not in sections:
                sections[current_section] = {}
            continue
        if not line.startswith("- "):
            continue
        payload = line[2:].strip()
        if ":" not in payload:
            continue
        key, value = payload.split(":", 1)
        sections[current_section][_normalize_key(key)] = value.strip()
    return sections


def _analyze_script_path() -> Path:
    return Path(__file__).with_name("analyze_run_metrics_history.py")


def _run_analyze_summary(input_path: Path, compare_input_path: Path | None = None) -> dict[str, Any]:
    command = [
        sys.executable,
        str(_analyze_script_path()),
        "--input",
        str(input_path),
        "--format",
        "json",
    ]
    if compare_input_path is not None:
        command.extend(["--compare-input", str(compare_input_path)])
        command.extend(["--report-mode", "runtime", "--ci-check"])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        combined = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError("analyze_run_metrics_history failed: %s" % combined)
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("analyze_run_metrics_history returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("analyze_run_metrics_history output must be a JSON object")
    return parsed


def _format_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100.0:.1f}%"


def _format_warnings(warnings: list[str]) -> str:
    if not warnings:
        return "none"
    return ", ".join(warnings)


def _build_likely_cause(
    decision: str,
    reasons: list[str],
    regression_state: str,
    quality_state: str,
    minimum_runs_met: bool,
    baseline_warnings: list[str],
    current_warnings: list[str],
    warning_count_delta: int | None,
    changed_fields: list[str],
) -> str:
    if decision != DECISION_INVESTIGATE_METRICS:
        return "runtime decision is %s; investigation report is informational only." % decision
    if not minimum_runs_met:
        return "minimum required runtime runs are not met; keep/revert decision remains blocked."
    if current_warnings:
        return "current quality warnings detected: %s." % _format_warnings(current_warnings)
    if baseline_warnings:
        return "baseline quality warnings detected: %s." % _format_warnings(baseline_warnings)
    if quality_state in {"warning", "incomplete"}:
        return "support metrics quality state is %s; data coherence review is required." % quality_state
    if regression_state == "warning":
        changed_label = ", ".join(changed_fields) if changed_fields else "unknown changed fields"
        if warning_count_delta is None:
            return "regression_state=warning with changed signals (%s)." % changed_label
        return (
            "regression_state=warning with warning_count_delta=%+d and changed fields: %s."
            % (warning_count_delta, changed_label)
        )
    if reasons:
        return "decision reasons indicate investigation is required: %s." % ", ".join(reasons)
    return "investigation was requested but no dominant blocker signal was isolated."


def _build_next_action(
    decision: str,
    minimum_runs_met: bool,
    regression_state: str,
    quality_state: str,
    baseline_warnings: list[str],
    current_warnings: list[str],
    analyze_final_decision_code: str,
) -> str:
    if decision == "collect_more_runs":
        return "collect_more_runs"
    if decision == "keep_tuning":
        return "keep blocked"
    if decision == "revert_tuning":
        return "revert blocked"
    if decision == DECISION_INVESTIGATE_METRICS:
        if not minimum_runs_met:
            return "collect_more_runs"
        if current_warnings or baseline_warnings:
            return "inspect warning"
        if quality_state in {"warning", "incomplete"}:
            return "inspect warning"
        if regression_state == "warning":
            return "inspect warning"
        if analyze_final_decision_code == "keep_candidate_for_more_testing":
            return "keep blocked"
        if analyze_final_decision_code == "reject_candidate_or_revert":
            return "revert blocked"
        return "inspect warning"
    return "inspect warning"


def _extract_decision_markdown_payload(
    decision_sections: dict[str, dict[str, str]]
) -> tuple[str, str, list[str], bool, bool]:
    protocol_section = decision_sections.get("runtime gameplay decision protocol", {})
    runs_section = decision_sections.get("runs", {})
    signals_section = decision_sections.get("signals", {})

    decision = str(protocol_section.get("decision", "")).strip().lower()
    confidence = str(protocol_section.get("confidence", "")).strip().lower()
    reasons_label = str(signals_section.get("reasons", "")).strip()
    reasons: list[str] = []
    if reasons_label != "" and reasons_label.lower() != "none":
        reasons = [item.strip() for item in reasons_label.split(",") if item.strip() != ""]

    minimum_runs_met_label = str(protocol_section.get("minimum_runs_met", "")).strip()
    minimum_runs_met = _parse_boolish(minimum_runs_met_label)
    if minimum_runs_met is None:
        minimum_runs_met = False

    gameplay_change_allowed_label = str(protocol_section.get("gameplay_change_allowed", "")).strip()
    gameplay_change_allowed = _parse_boolish(gameplay_change_allowed_label)
    if gameplay_change_allowed is None:
        gameplay_change_allowed = False

    # Validate that these sections are really present.
    if decision == "":
        raise RuntimeError("decision markdown is missing '- decision: ...' entry")
    if not runs_section:
        raise RuntimeError("decision markdown is missing '## Runs' section")
    if not signals_section:
        raise RuntimeError("decision markdown is missing '## Signals' section")

    return decision, confidence, reasons, minimum_runs_met, gameplay_change_allowed


def _build_investigation_report(args: argparse.Namespace) -> dict[str, Any]:
    _read_text_file(args.comparison, "comparison markdown")
    decision_markdown_content = _read_text_file(args.decision, "decision markdown")

    decision_sections = _parse_markdown_sections(decision_markdown_content)
    (
        runtime_decision,
        runtime_confidence,
        runtime_reasons,
        minimum_runs_met,
        gameplay_change_allowed_from_decision,
    ) = _extract_decision_markdown_payload(decision_sections)

    try:
        baseline_summary = _run_analyze_summary(args.baseline)
    except RuntimeError as exc:
        raise RuntimeError("unable to analyze baseline runtime file: %s" % str(exc)) from exc
    try:
        current_summary = _run_analyze_summary(args.current)
    except RuntimeError as exc:
        raise RuntimeError("unable to analyze current runtime file: %s" % str(exc)) from exc
    try:
        comparison_summary = _run_analyze_summary(args.baseline, args.current)
    except RuntimeError as exc:
        raise RuntimeError("unable to analyze baseline/current comparison: %s" % str(exc)) from exc

    baseline_invalid_lines = _as_int(baseline_summary.get("invalid_lines"))
    current_invalid_lines = _as_int(current_summary.get("invalid_lines"))
    if baseline_invalid_lines > 0:
        raise RuntimeError(
            "baseline runtime file contains invalid JSON lines: %d" % baseline_invalid_lines
        )
    if current_invalid_lines > 0:
        raise RuntimeError(
            "current runtime file contains invalid JSON lines: %d" % current_invalid_lines
        )

    comparison_block = comparison_summary.get("comparison", {})
    if not isinstance(comparison_block, dict):
        comparison_block = {}

    regression_block = comparison_summary.get("support_metrics_regression", {})
    if not isinstance(regression_block, dict):
        regression_block = {}

    analyze_quality_block = comparison_summary.get("support_metrics_quality", {})
    if not isinstance(analyze_quality_block, dict):
        analyze_quality_block = {}

    final_decision_block = comparison_summary.get("support_metrics_final_decision", {})
    if not isinstance(final_decision_block, dict):
        final_decision_block = {}

    baseline_quality_block = baseline_summary.get("support_metrics_quality", {})
    if not isinstance(baseline_quality_block, dict):
        baseline_quality_block = {}

    current_quality_block = current_summary.get("support_metrics_quality", {})
    if not isinstance(current_quality_block, dict):
        current_quality_block = {}

    baseline_champion_block = baseline_summary.get("champion_support", {})
    if not isinstance(baseline_champion_block, dict):
        baseline_champion_block = {}

    current_champion_block = current_summary.get("champion_support", {})
    if not isinstance(current_champion_block, dict):
        current_champion_block = {}

    baseline_champion_diagnostic = baseline_champion_block.get("diagnostic", {})
    if not isinstance(baseline_champion_diagnostic, dict):
        baseline_champion_diagnostic = {}

    current_champion_diagnostic = current_champion_block.get("diagnostic", {})
    if not isinstance(current_champion_diagnostic, dict):
        current_champion_diagnostic = {}

    baseline_quality_warnings = _as_list_of_strings(baseline_quality_block.get("warnings"))
    current_quality_warnings = _as_list_of_strings(current_quality_block.get("warnings"))

    regression_state = str(regression_block.get("regression_state", "")).strip().lower() or "unknown"
    quality_state = (
        str(analyze_quality_block.get("state", "")).strip().lower()
        or str(current_quality_block.get("state", "")).strip().lower()
        or "unknown"
    )
    warning_count_delta_raw = regression_block.get("warning_count_delta")
    warning_count_delta = _as_int(warning_count_delta_raw) if warning_count_delta_raw is not None else None
    changed_fields = _as_list_of_strings(regression_block.get("changed_fields"))

    baseline_runs = _as_int(comparison_block.get("baseline_support_gate_records"))
    current_runs = _as_int(comparison_block.get("candidate_support_gate_records"))
    baseline_exports_read = _as_int(comparison_block.get("baseline_exports_read"))
    current_exports_read = _as_int(comparison_block.get("candidate_exports_read"))

    if baseline_runs <= 0:
        baseline_runs = _as_int(baseline_summary.get("support_gate", {}).get("records"))
    if current_runs <= 0:
        current_runs = _as_int(current_summary.get("support_gate", {}).get("records"))
    if baseline_exports_read <= 0:
        baseline_exports_read = _as_int(baseline_summary.get("exports_read"))
    if current_exports_read <= 0:
        current_exports_read = _as_int(current_summary.get("exports_read"))

    final_decision_code = str(final_decision_block.get("decision", "")).strip()
    final_decision_confidence = str(final_decision_block.get("confidence", "")).strip()
    final_decision_reasons = _as_list_of_strings(final_decision_block.get("reasons"))

    likely_cause = _build_likely_cause(
        decision=runtime_decision,
        reasons=runtime_reasons,
        regression_state=regression_state,
        quality_state=quality_state,
        minimum_runs_met=minimum_runs_met,
        baseline_warnings=baseline_quality_warnings,
        current_warnings=current_quality_warnings,
        warning_count_delta=warning_count_delta,
        changed_fields=changed_fields,
    )
    next_action = _build_next_action(
        decision=runtime_decision,
        minimum_runs_met=minimum_runs_met,
        regression_state=regression_state,
        quality_state=quality_state,
        baseline_warnings=baseline_quality_warnings,
        current_warnings=current_quality_warnings,
        analyze_final_decision_code=final_decision_code,
    )

    report: dict[str, Any] = {
        "decision": runtime_decision,
        "confidence": runtime_confidence or "unknown",
        "reasons": runtime_reasons,
        "minimum_runs_met": minimum_runs_met,
        "regression_state": regression_state,
        "quality_state": quality_state,
        "warnings": {
            "baseline": baseline_quality_warnings,
            "current": current_quality_warnings,
        },
        "support_metrics_final_decision": {
            "decision": final_decision_code or "unknown",
            "confidence": final_decision_confidence or "unknown",
            "reasons": final_decision_reasons,
        },
        "support_metrics_regression": {
            "regression_state": regression_state,
            "changed_fields": changed_fields,
            "warning_count_delta": warning_count_delta,
            "interpretation": str(regression_block.get("interpretation", "")).strip() or "unknown",
        },
        "run_counts": {
            "baseline_runs": baseline_runs,
            "current_runs": current_runs,
            "baseline_exports_read": baseline_exports_read,
            "current_exports_read": current_exports_read,
        },
        "champion_support_success_rate": {
            "baseline": _as_float(baseline_champion_block.get("avg_champion_support_run_success_rate")),
            "current": _as_float(current_champion_block.get("avg_champion_support_run_success_rate")),
        },
        "champion_support_pressure": {
            "baseline_cooldown": str(
                baseline_champion_diagnostic.get("cooldown_pressure", "n/a")
            ).strip()
            or "n/a",
            "baseline_unavailable": str(
                baseline_champion_diagnostic.get("unavailable_pressure", "n/a")
            ).strip()
            or "n/a",
            "current_cooldown": str(
                current_champion_diagnostic.get("cooldown_pressure", "n/a")
            ).strip()
            or "n/a",
            "current_unavailable": str(
                current_champion_diagnostic.get("unavailable_pressure", "n/a")
            ).strip()
            or "n/a",
        },
        "likely_cause": likely_cause,
        "next_action": next_action,
        "gameplay_change_allowed": False,
        "decision_markdown_gameplay_change_allowed": gameplay_change_allowed_from_decision,
        "note": "Observation/debug report only. No automatic gameplay decision is applied.",
        "paths": {
            "baseline": str(args.baseline),
            "current": str(args.current),
            "comparison": str(args.comparison),
            "decision": str(args.decision),
        },
    }
    return report


def _build_markdown_report(report: dict[str, Any]) -> str:
    warnings_block = report.get("warnings", {})
    baseline_warnings = []
    current_warnings = []
    if isinstance(warnings_block, dict):
        baseline_warnings = _as_list_of_strings(warnings_block.get("baseline"))
        current_warnings = _as_list_of_strings(warnings_block.get("current"))
    warnings_label = "baseline=%s | current=%s" % (
        _format_warnings(baseline_warnings),
        _format_warnings(current_warnings),
    )

    run_counts = report.get("run_counts", {})
    champion_rates = report.get("champion_support_success_rate", {})
    champion_pressure = report.get("champion_support_pressure", {})
    final_decision = report.get("support_metrics_final_decision", {})
    regression = report.get("support_metrics_regression", {})

    final_reasons = []
    if isinstance(final_decision, dict):
        final_reasons = _as_list_of_strings(final_decision.get("reasons"))
    regression_changed_fields = []
    if isinstance(regression, dict):
        regression_changed_fields = _as_list_of_strings(regression.get("changed_fields"))
    decision_reasons = _as_list_of_strings(report.get("reasons"))

    lines: list[str] = []
    lines.append("# Support metrics runtime investigation")
    lines.append("- decision: %s" % str(report.get("decision", "unknown")))
    lines.append("- regression_state: %s" % str(report.get("regression_state", "unknown")))
    lines.append("- quality_state: %s" % str(report.get("quality_state", "unknown")))
    lines.append("- warnings: %s" % warnings_label)
    lines.append("- likely cause: %s" % str(report.get("likely_cause", "unknown")))
    lines.append("- next action: %s" % str(report.get("next_action", "inspect warning")))
    lines.append("- gameplay_change_allowed: false")
    lines.append("")
    lines.append("## Runtime signals")
    lines.append("- confidence: %s" % str(report.get("confidence", "unknown")))
    lines.append("- reasons: %s" % (", ".join(decision_reasons) if decision_reasons else "none"))
    lines.append("- baseline runs: %d" % _as_int(run_counts.get("baseline_runs") if isinstance(run_counts, dict) else 0))
    lines.append("- current runs: %d" % _as_int(run_counts.get("current_runs") if isinstance(run_counts, dict) else 0))
    lines.append(
        "- baseline exports read: %d"
        % _as_int(run_counts.get("baseline_exports_read") if isinstance(run_counts, dict) else 0)
    )
    lines.append(
        "- current exports read: %d"
        % _as_int(run_counts.get("current_exports_read") if isinstance(run_counts, dict) else 0)
    )
    lines.append("")
    lines.append("## Support metrics regression")
    lines.append("- state: %s" % str(regression.get("regression_state", "unknown")))
    lines.append("- warning_count_delta: %s" % str(regression.get("warning_count_delta", "n/a")))
    lines.append(
        "- changed_fields: %s"
        % (", ".join(regression_changed_fields) if regression_changed_fields else "none")
    )
    lines.append("- interpretation: %s" % str(regression.get("interpretation", "unknown")))
    lines.append("")
    lines.append("## Support metrics final decision")
    lines.append("- decision: %s" % str(final_decision.get("decision", "unknown")))
    lines.append("- confidence: %s" % str(final_decision.get("confidence", "unknown")))
    lines.append("- reasons: %s" % (", ".join(final_reasons) if final_reasons else "none"))
    lines.append("")
    lines.append("## Champion support")
    lines.append(
        "- success_rate baseline: %s"
        % _format_ratio(
            _as_float(champion_rates.get("baseline") if isinstance(champion_rates, dict) else None)
        )
    )
    lines.append(
        "- success_rate current: %s"
        % _format_ratio(
            _as_float(champion_rates.get("current") if isinstance(champion_rates, dict) else None)
        )
    )
    lines.append(
        "- cooldown pressure baseline/current: %s / %s"
        % (
            str(champion_pressure.get("baseline_cooldown", "n/a")) if isinstance(champion_pressure, dict) else "n/a",
            str(champion_pressure.get("current_cooldown", "n/a")) if isinstance(champion_pressure, dict) else "n/a",
        )
    )
    lines.append(
        "- unavailable pressure baseline/current: %s / %s"
        % (
            str(champion_pressure.get("baseline_unavailable", "n/a")) if isinstance(champion_pressure, dict) else "n/a",
            str(champion_pressure.get("current_unavailable", "n/a")) if isinstance(champion_pressure, dict) else "n/a",
        )
    )
    lines.append("")
    lines.append("## Note")
    lines.append(str(report.get("note", "Observation/debug report only.")))
    return "\n".join(lines) + "\n"


def _print_text_report(report: dict[str, Any]) -> None:
    print("Support metrics runtime investigation:")
    print("- decision: %s" % str(report.get("decision", "unknown")))
    print("- confidence: %s" % str(report.get("confidence", "unknown")))
    print("- regression_state: %s" % str(report.get("regression_state", "unknown")))
    print("- quality_state: %s" % str(report.get("quality_state", "unknown")))
    print("- likely cause: %s" % str(report.get("likely_cause", "unknown")))
    print("- next action: %s" % str(report.get("next_action", "inspect warning")))
    print("- gameplay_change_allowed: false")


def main() -> int:
    args = _build_parser().parse_args()

    try:
        report = _build_investigation_report(args)
    except RuntimeError as exc:
        print("ERROR: %s" % str(exc), file=sys.stderr)
        return 1

    markdown_content = _build_markdown_report(report)
    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_content, encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text_report(report)

    if args.check:
        if bool(report.get("gameplay_change_allowed", True)):
            print(
                "ERROR: gameplay_change_allowed must remain false for investigation reports.",
                file=sys.stderr,
            )
            return 1
        if bool(report.get("decision_markdown_gameplay_change_allowed", False)):
            print(
                "ERROR: decision markdown unexpectedly reports gameplay_change_allowed=true.",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
