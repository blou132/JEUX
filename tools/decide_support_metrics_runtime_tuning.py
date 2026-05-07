from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import sys
from typing import Any


DECISION_KEEP_TUNING = "keep_tuning"
DECISION_REVERT_TUNING = "revert_tuning"
DECISION_COLLECT_MORE_RUNS = "collect_more_runs"
DECISION_INVESTIGATE_METRICS = "investigate_metrics"
DECISION_NO_DECISION = "no_decision"

VALID_DECISIONS: tuple[str, ...] = (
    DECISION_KEEP_TUNING,
    DECISION_REVERT_TUNING,
    DECISION_COLLECT_MORE_RUNS,
    DECISION_INVESTIGATE_METRICS,
    DECISION_NO_DECISION,
)

DEFAULT_MIN_RUNS = 5
STRONG_DROP_THRESHOLD = -0.10
SLIGHT_DROP_TOLERANCE = -0.02


@dataclass
class DecisionRunCounts:
    baseline_support_gate_runs: int
    current_support_gate_runs: int
    baseline_exports_read: int
    current_exports_read: int
    minimum_required_runs: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeTuningDecision:
    decision: str
    reasons: list[str]
    confidence: str
    minimum_runs_met: bool
    run_counts: DecisionRunCounts
    quality_state: str
    regression_state: str
    support_gate_success_rate_delta: float | None
    rally_champion_success_rate_delta: float | None
    gameplay_change_allowed: bool
    source: str
    note: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["run_counts"] = self.run_counts.to_dict()
        return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Apply a local heuristic decision protocol for runtime support metrics "
            "baseline/current reports. This tool does not apply gameplay changes."
        )
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Path to an existing analyze_run_metrics_history JSON summary.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Baseline runtime JSONL path (used when --summary-json is omitted).",
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=None,
        help="Current runtime JSONL path (used when --summary-json is omitted).",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=DEFAULT_MIN_RUNS,
        help="Minimum support_gate run count required per side (default: 5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=None,
        help="Optional path to write a compact Markdown decision report.",
    )
    return parser


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


def _analyze_script_path() -> Path:
    return Path(__file__).with_name("analyze_run_metrics_history.py")


def _read_summary_from_path(summary_path: Path) -> dict[str, Any]:
    if not summary_path.exists():
        raise RuntimeError("summary JSON file not found: %s" % summary_path)
    try:
        parsed = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("summary JSON file is unreadable or invalid: %s" % str(exc)) from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("summary JSON must be an object")
    return parsed


def _build_summary_from_baseline_current(
    baseline_path: Path,
    current_path: Path,
) -> dict[str, Any]:
    if not baseline_path.exists():
        raise RuntimeError("baseline file not found: %s" % baseline_path)
    if not current_path.exists():
        raise RuntimeError("current file not found: %s" % current_path)

    command = [
        sys.executable,
        str(_analyze_script_path()),
        "--input",
        str(baseline_path),
        "--compare-input",
        str(current_path),
        "--report-mode",
        "runtime",
        "--ci-check",
        "--format",
        "json",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        combined = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError("unable to build summary from baseline/current: %s" % combined)
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("analyze summary output is invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("analyze summary output must be a JSON object")
    return parsed


def _resolve_summary(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    if args.summary_json is not None:
        return _read_summary_from_path(args.summary_json), "summary_json"
    if args.baseline is None or args.current is None:
        raise RuntimeError(
            "Provide --summary-json or both --baseline and --current."
        )
    return (
        _build_summary_from_baseline_current(args.baseline, args.current),
        "baseline_current_inputs",
    )


def _extract_run_counts(summary: dict[str, Any], min_runs: int) -> DecisionRunCounts:
    comparison = summary.get("comparison", {})
    if isinstance(comparison, dict) and comparison:
        return DecisionRunCounts(
            baseline_support_gate_runs=_as_int(comparison.get("baseline_support_gate_records")),
            current_support_gate_runs=_as_int(comparison.get("candidate_support_gate_records")),
            baseline_exports_read=_as_int(comparison.get("baseline_exports_read")),
            current_exports_read=_as_int(comparison.get("candidate_exports_read")),
            minimum_required_runs=min_runs,
        )

    support_gate = summary.get("support_gate", {})
    current_runs = _as_int(support_gate.get("records")) if isinstance(support_gate, dict) else 0
    current_exports = _as_int(summary.get("exports_read"))
    return DecisionRunCounts(
        baseline_support_gate_runs=0,
        current_support_gate_runs=current_runs,
        baseline_exports_read=0,
        current_exports_read=current_exports,
        minimum_required_runs=min_runs,
    )


def _extract_data_state(summary: dict[str, Any]) -> str:
    support_systems_summary = summary.get("support_systems_summary", {})
    if isinstance(support_systems_summary, dict):
        data_state = str(support_systems_summary.get("data_state", "")).strip().lower()
        if data_state in {"complete", "partial", "no_data"}:
            return data_state
    quality_state = str(summary.get("support_metrics_quality", {}).get("state", "")).strip().lower()
    if quality_state == "no_data":
        return "no_data"
    if quality_state in {"warning", "incomplete"}:
        return "partial"
    if quality_state == "valid":
        return "complete"
    return "partial"


def _build_decision(summary: dict[str, Any], min_runs: int, source: str) -> RuntimeTuningDecision:
    quality = summary.get("support_metrics_quality", {})
    regression = summary.get("support_metrics_regression", {})
    final_decision = summary.get("support_metrics_final_decision", {})

    quality_state = str(quality.get("state", "")).strip().lower() if isinstance(quality, dict) else ""
    regression_state = (
        str(regression.get("regression_state", "")).strip().lower()
        if isinstance(regression, dict)
        else ""
    )
    final_decision_code = (
        str(final_decision.get("decision", "")).strip().lower()
        if isinstance(final_decision, dict)
        else ""
    )

    support_gate_delta = _as_float(
        regression.get("support_gate_success_rate_delta") if isinstance(regression, dict) else None
    )
    champion_delta = _as_float(
        regression.get("rally_champion_success_rate_delta") if isinstance(regression, dict) else None
    )

    run_counts = _extract_run_counts(summary, min_runs=min_runs)
    has_baseline_runs = run_counts.baseline_support_gate_runs > 0 or run_counts.baseline_exports_read > 0
    if has_baseline_runs:
        minimum_runs_met = (
            run_counts.baseline_support_gate_runs >= min_runs
            and run_counts.current_support_gate_runs >= min_runs
        )
    else:
        minimum_runs_met = run_counts.current_support_gate_runs >= min_runs

    reasons: list[str] = []
    decision = DECISION_NO_DECISION
    confidence = "low"

    data_state = _extract_data_state(summary)
    exports_read = _as_int(summary.get("exports_read"))
    runtime_absent = (
        data_state == "no_data"
        or quality_state == "no_data"
        or exports_read <= 0
        or final_decision_code == "no_runtime_data"
    )

    strong_drop = (
        (support_gate_delta is not None and support_gate_delta <= STRONG_DROP_THRESHOLD)
        or (champion_delta is not None and champion_delta <= STRONG_DROP_THRESHOLD)
    )

    acceptable_stability = (
        (support_gate_delta is None or support_gate_delta >= SLIGHT_DROP_TOLERANCE)
        and (champion_delta is None or champion_delta >= SLIGHT_DROP_TOLERANCE)
    )

    if runtime_absent:
        decision = DECISION_COLLECT_MORE_RUNS
        confidence = "low"
        reasons.append("runtime_data_absent")
    elif quality_state == "warning":
        decision = DECISION_INVESTIGATE_METRICS
        confidence = "medium"
        reasons.append("quality_warning")
    elif regression_state == "warning":
        if strong_drop:
            decision = DECISION_REVERT_TUNING
            confidence = "high" if minimum_runs_met else "medium"
            reasons.append("regression_warning_strong_drop")
        else:
            decision = DECISION_INVESTIGATE_METRICS
            confidence = "medium"
            reasons.append("regression_warning")
    elif strong_drop:
        decision = DECISION_REVERT_TUNING
        confidence = "high" if minimum_runs_met else "medium"
        reasons.append("strong_success_rate_drop")
    elif final_decision_code == "collect_more_runs_before_deciding":
        decision = DECISION_COLLECT_MORE_RUNS
        confidence = "low"
        reasons.append("analyze_final_decision_collect_more_runs")
    elif regression_state in {"incompatible", "no_baseline"}:
        decision = DECISION_COLLECT_MORE_RUNS
        confidence = "low"
        reasons.append("regression_context_insufficient")
    elif not minimum_runs_met:
        decision = DECISION_COLLECT_MORE_RUNS
        confidence = "low"
        reasons.append("minimum_runs_not_met")
    elif regression_state in {"stable", "changed"} and acceptable_stability:
        decision = DECISION_KEEP_TUNING
        confidence = "high" if (
            run_counts.baseline_support_gate_runs >= (min_runs + 5)
            and run_counts.current_support_gate_runs >= (min_runs + 5)
        ) else "medium"
        reasons.append("stable_or_slightly_improved_without_warning")
    elif regression_state in {"stable", "changed"}:
        decision = DECISION_INVESTIGATE_METRICS
        confidence = "medium"
        reasons.append("minor_regression_needs_review")
    else:
        decision = DECISION_NO_DECISION
        confidence = "low"
        reasons.append("insufficient_decision_signals")

    if decision not in VALID_DECISIONS:
        decision = DECISION_NO_DECISION
        confidence = "low"
        reasons = ["invalid_decision_fallback"]

    return RuntimeTuningDecision(
        decision=decision,
        reasons=list(dict.fromkeys(reasons)),
        confidence=confidence,
        minimum_runs_met=minimum_runs_met,
        run_counts=run_counts,
        quality_state=quality_state or "unknown",
        regression_state=regression_state or "unknown",
        support_gate_success_rate_delta=support_gate_delta,
        rally_champion_success_rate_delta=champion_delta,
        gameplay_change_allowed=False,
        source=source,
        note=(
            "Heuristic runtime decision aid only (no statistical proof). "
            "A human must decide whether to apply gameplay changes."
        ),
    )


def _build_markdown_report(report: RuntimeTuningDecision) -> str:
    reasons_label = ", ".join(report.reasons) if report.reasons else "none"
    support_gate_delta_label = (
        "n/a"
        if report.support_gate_success_rate_delta is None
        else f"{report.support_gate_success_rate_delta * 100.0:+.1f}pp"
    )
    champion_delta_label = (
        "n/a"
        if report.rally_champion_success_rate_delta is None
        else f"{report.rally_champion_success_rate_delta * 100.0:+.1f}pp"
    )

    lines: list[str] = []
    lines.append("# Runtime gameplay decision protocol")
    lines.append("")
    lines.append("- decision: %s" % report.decision)
    lines.append("- confidence: %s" % report.confidence)
    lines.append("- minimum_runs_met: %s" % ("true" if report.minimum_runs_met else "false"))
    lines.append("- gameplay_change_allowed: false")
    lines.append("- source: %s" % report.source)
    lines.append("")
    lines.append("## Runs")
    lines.append("- minimum required runs per side: %d" % report.run_counts.minimum_required_runs)
    lines.append("- baseline support_gate runs: %d" % report.run_counts.baseline_support_gate_runs)
    lines.append("- current support_gate runs: %d" % report.run_counts.current_support_gate_runs)
    lines.append("- baseline exports read: %d" % report.run_counts.baseline_exports_read)
    lines.append("- current exports read: %d" % report.run_counts.current_exports_read)
    lines.append("")
    lines.append("## Signals")
    lines.append("- quality_state: %s" % report.quality_state)
    lines.append("- regression_state: %s" % report.regression_state)
    lines.append("- support_gate_success_rate_delta: %s" % support_gate_delta_label)
    lines.append("- rally_champion_success_rate_delta: %s" % champion_delta_label)
    lines.append("- reasons: %s" % reasons_label)
    lines.append("")
    lines.append("## Note")
    lines.append(report.note)
    return "\n".join(lines) + "\n"


def _print_text_report(report: RuntimeTuningDecision) -> None:
    print("Runtime gameplay decision protocol:")
    print("- decision: %s" % report.decision)
    print("- confidence: %s" % report.confidence)
    print("- minimum_runs_met: %s" % ("yes" if report.minimum_runs_met else "no"))
    print("- minimum required runs per side: %d" % report.run_counts.minimum_required_runs)
    print("- baseline support_gate runs: %d" % report.run_counts.baseline_support_gate_runs)
    print("- current support_gate runs: %d" % report.run_counts.current_support_gate_runs)
    print("- baseline exports read: %d" % report.run_counts.baseline_exports_read)
    print("- current exports read: %d" % report.run_counts.current_exports_read)
    print("- quality_state: %s" % report.quality_state)
    print("- regression_state: %s" % report.regression_state)
    print(
        "- support_gate_success_rate_delta: %s"
        % (
            "n/a"
            if report.support_gate_success_rate_delta is None
            else f"{report.support_gate_success_rate_delta * 100.0:+.1f}pp"
        )
    )
    print(
        "- rally_champion_success_rate_delta: %s"
        % (
            "n/a"
            if report.rally_champion_success_rate_delta is None
            else f"{report.rally_champion_success_rate_delta * 100.0:+.1f}pp"
        )
    )
    print("- reasons: %s" % (", ".join(report.reasons) if report.reasons else "none"))
    print("- gameplay_change_allowed: false")
    print("- note: %s" % report.note)


def main() -> int:
    args = _build_parser().parse_args()

    if args.min_runs <= 0:
        print("--min-runs must be greater than 0.", file=sys.stderr)
        return 2

    try:
        summary, source = _resolve_summary(args)
        report = _build_decision(summary, min_runs=int(args.min_runs), source=source)
    except RuntimeError as exc:
        print("ERROR: %s" % str(exc), file=sys.stderr)
        return 1

    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(_build_markdown_report(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
