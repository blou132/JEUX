from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_HISTORY_PATH = Path("run_metrics_history.jsonl")
COMPARISON_SUPPORT_GATE_METRICS = (
    "avg_support_gate_run_success_rate",
    "avg_support_gate_run_available_ratio",
    "objective_success_rate",
    "avg_support_gate_run_attempts",
    "avg_support_gate_run_success",
)
COMPARISON_RATE_METRICS = {
    "avg_support_gate_run_success_rate",
    "avg_support_gate_run_available_ratio",
    "objective_success_rate",
}
COMPARISON_AVAILABLE_DROP_TOLERANCE = -0.05
COMPARISON_STRONG_DROP_THRESHOLD = -0.10


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _as_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def read_jsonl_records(input_path: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    invalid_lines = 0

    for line_number, raw_line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines += 1
            continue
        if not isinstance(parsed, dict):
            invalid_lines += 1
            continue
        parsed["_line_number"] = line_number
        records.append(parsed)

    return records, invalid_lines


def _pick_best_run(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    best_record: dict[str, Any] | None = None
    best_key: tuple[float, float, float] | None = None
    for record in records:
        rate = _as_float(record.get("support_gate_run_success_rate"))
        available = _as_float(record.get("support_gate_run_available_ratio"))
        success = _as_float(record.get("support_gate_run_success"))
        if rate is None:
            continue
        key = (
            rate,
            available if available is not None else -1.0,
            success if success is not None else -1.0,
        )
        if best_key is None or key > best_key:
            best_key = key
            best_record = record
    return best_record


def _pick_worst_run(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    worst_record: dict[str, Any] | None = None
    worst_key: tuple[float, float, float] | None = None
    for record in records:
        rate = _as_float(record.get("support_gate_run_success_rate"))
        available = _as_float(record.get("support_gate_run_available_ratio"))
        success = _as_float(record.get("support_gate_run_success"))
        if rate is None:
            continue
        key = (
            rate,
            available if available is not None else 2.0,
            success if success is not None else 2.0,
        )
        if worst_key is None or key < worst_key:
            worst_key = key
            worst_record = record
    return worst_record


def _run_label(record: dict[str, Any] | None) -> str:
    if record is None:
        return "n/a"
    export_id = str(record.get("export_id", "")).strip()
    if export_id:
        return export_id
    line_number = _as_int(record.get("_line_number"))
    if line_number is not None:
        return "line_%d" % line_number
    return "unknown"


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def build_support_gate_recommendations(summary: dict[str, Any]) -> list[str]:
    support_gate = summary.get("support_gate", {})
    records = int(support_gate.get("records", 0))
    avg_available_ratio = _as_float(support_gate.get("avg_support_gate_run_available_ratio"))
    avg_success_rate = _as_float(support_gate.get("avg_support_gate_run_success_rate"))
    objective_success_rate = _as_float(support_gate.get("objective_success_rate"))
    invalid_lines = int(summary.get("invalid_lines", 0))

    recommendations: list[str] = []
    if records <= 0:
        recommendations.append("Not enough support_gate data.")
    elif avg_available_ratio is not None and avg_available_ratio < 0.25:
        recommendations.append(
            "Support gate availability looks low: consider increasing gate availability window."
        )
    elif (
        avg_success_rate is not None
        and avg_success_rate < 0.40
        and avg_available_ratio is not None
        and avg_available_ratio >= 0.25
    ):
        recommendations.append(
            "Support gate success rate is low: improve interaction feedback or reduce cooldown/actions required."
        )
    elif (
        avg_success_rate is not None
        and objective_success_rate is not None
        and avg_success_rate > 0.85
        and objective_success_rate > 0.80
    ):
        recommendations.append(
            "Support gate objective may be too easy: consider a slight increase in required actions/time."
        )
    else:
        recommendations.append("Support gate tuning looks stable.")

    if invalid_lines > 0:
        recommendations.append("Some input lines were ignored because they were invalid JSON records.")

    return recommendations


def build_summary(
    all_records: list[dict[str, Any]],
    invalid_lines: int,
    objective_filter: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    filtered_records = list(all_records)
    if objective_filter:
        objective_id = objective_filter.strip()
        filtered_records = [record for record in filtered_records if str(record.get("objective_id", "")) == objective_id]

    if limit is not None and limit > 0 and len(filtered_records) > limit:
        filtered_records = filtered_records[-limit:]

    status_counts: dict[str, int] = {"completed": 0, "failed": 0, "running": 0}
    objective_counts: dict[str, int] = {}
    for record in filtered_records:
        status = str(record.get("run_status", "running")).strip().lower()
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = status_counts.get(status, 0) + 1
        objective_id = str(record.get("objective_id", "unknown")).strip() or "unknown"
        objective_counts[objective_id] = objective_counts.get(objective_id, 0) + 1

    support_gate_records = [record for record in filtered_records if str(record.get("objective_id", "")) == "support_gate"]
    attempts_values = [_as_float(record.get("support_gate_run_attempts")) for record in support_gate_records]
    success_values = [_as_float(record.get("support_gate_run_success")) for record in support_gate_records]
    success_rate_values = [_as_float(record.get("support_gate_run_success_rate")) for record in support_gate_records]
    available_rate_values = [_as_float(record.get("support_gate_run_available_ratio")) for record in support_gate_records]

    attempts_avg = _average([value for value in attempts_values if value is not None])
    success_avg = _average([value for value in success_values if value is not None])
    success_rate_avg = _average([value for value in success_rate_values if value is not None])
    available_rate_avg = _average([value for value in available_rate_values if value is not None])

    support_gate_completed = 0
    support_gate_failed = 0
    for record in support_gate_records:
        objective_status = str(record.get("objective_status", "")).strip().lower()
        if objective_status == "completed":
            support_gate_completed += 1
        elif objective_status == "failed":
            support_gate_failed += 1

    objective_success_rate: float | None = None
    total_resolved = support_gate_completed + support_gate_failed
    if total_resolved > 0:
        objective_success_rate = float(support_gate_completed / total_resolved)

    best_run = _pick_best_run(support_gate_records)
    worst_run = _pick_worst_run(support_gate_records)

    summary = {
        "input_total_records": len(all_records),
        "invalid_lines": invalid_lines,
        "objective_filter": objective_filter or "",
        "limit": limit,
        "exports_read": len(filtered_records),
        "run_status_counts": status_counts,
        "objective_counts": objective_counts,
        "support_gate": {
            "records": len(support_gate_records),
            "avg_support_gate_run_attempts": attempts_avg,
            "avg_support_gate_run_success": success_avg,
            "avg_support_gate_run_success_rate": success_rate_avg,
            "avg_support_gate_run_available_ratio": available_rate_avg,
            "best_run": _run_label(best_run),
            "worst_run": _run_label(worst_run),
            "objective_success_rate": objective_success_rate,
            "objective_completed": support_gate_completed,
            "objective_failed": support_gate_failed,
        },
    }
    summary["recommendations"] = build_support_gate_recommendations(summary)
    return summary


def _compute_delta_and_percent(baseline: float | None, candidate: float | None) -> tuple[float | None, float | None]:
    if baseline is None or candidate is None:
        return None, None
    delta = candidate - baseline
    if abs(baseline) < 1e-9:
        return delta, None
    return delta, (delta / abs(baseline)) * 100.0


def _format_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _format_ratio(value: float | None) -> str:
    return _pct(value)


def _format_delta(value: float | None, is_rate: bool) -> str:
    if value is None:
        return "n/a"
    if is_rate:
        return f"{value * 100.0:+.1f}pp"
    return f"{value:+.2f}"


def _format_percent_change(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.1f}%"


def build_comparison_summary(baseline_summary: dict[str, Any], candidate_summary: dict[str, Any]) -> dict[str, Any]:
    baseline_support_gate = baseline_summary.get("support_gate", {})
    candidate_support_gate = candidate_summary.get("support_gate", {})

    baseline_metrics: dict[str, float | None] = {}
    candidate_metrics: dict[str, float | None] = {}
    delta_metrics: dict[str, float | None] = {}
    delta_percent_metrics: dict[str, float | None] = {}

    for metric_name in COMPARISON_SUPPORT_GATE_METRICS:
        baseline_value = _as_float(baseline_support_gate.get(metric_name))
        candidate_value = _as_float(candidate_support_gate.get(metric_name))
        delta_value, delta_percent_value = _compute_delta_and_percent(baseline_value, candidate_value)
        baseline_metrics[metric_name] = baseline_value
        candidate_metrics[metric_name] = candidate_value
        delta_metrics[metric_name] = delta_value
        delta_percent_metrics[metric_name] = delta_percent_value

    comparison = {
        "baseline_exports_read": int(baseline_summary.get("exports_read", 0)),
        "candidate_exports_read": int(candidate_summary.get("exports_read", 0)),
        "baseline_invalid_lines": int(baseline_summary.get("invalid_lines", 0)),
        "candidate_invalid_lines": int(candidate_summary.get("invalid_lines", 0)),
        "baseline_support_gate_records": int(baseline_support_gate.get("records", 0)),
        "candidate_support_gate_records": int(candidate_support_gate.get("records", 0)),
        "support_gate": {
            "baseline": baseline_metrics,
            "candidate": candidate_metrics,
            "delta": delta_metrics,
            "delta_percent": delta_percent_metrics,
        },
    }
    comparison["confidence"] = build_comparison_confidence(comparison)
    comparison["recommendation"] = build_comparison_recommendation(comparison)
    return comparison


def build_comparison_confidence(comparison: dict[str, Any]) -> str:
    baseline_records = int(comparison.get("baseline_support_gate_records", 0))
    candidate_records = int(comparison.get("candidate_support_gate_records", 0))
    if baseline_records < 3 or candidate_records < 3:
        return "low"
    if baseline_records >= 10 and candidate_records >= 10:
        return "high"
    return "medium"


def build_comparison_recommendation(comparison: dict[str, Any]) -> str:
    baseline_records = int(comparison.get("baseline_support_gate_records", 0))
    candidate_records = int(comparison.get("candidate_support_gate_records", 0))
    if baseline_records <= 0 or candidate_records <= 0:
        return "Insufficient support_gate data for comparison."

    support_gate_comparison = comparison.get("support_gate", {})
    delta_metrics = support_gate_comparison.get("delta", {})
    success_rate_delta = _as_float(delta_metrics.get("avg_support_gate_run_success_rate"))
    available_ratio_delta = _as_float(delta_metrics.get("avg_support_gate_run_available_ratio"))
    objective_success_delta = _as_float(delta_metrics.get("objective_success_rate"))

    if success_rate_delta is None or available_ratio_delta is None or objective_success_delta is None:
        return "Insufficient support_gate data for comparison."

    if success_rate_delta > 0.0 and available_ratio_delta <= COMPARISON_STRONG_DROP_THRESHOLD:
        return "Mixed result: success improved but availability got worse."
    if success_rate_delta <= COMPARISON_STRONG_DROP_THRESHOLD or objective_success_delta <= COMPARISON_STRONG_DROP_THRESHOLD:
        return "Candidate looks worse for support_gate."
    if (
        success_rate_delta > 0.0
        and objective_success_delta >= 0.0
        and available_ratio_delta >= COMPARISON_AVAILABLE_DROP_TOLERANCE
    ):
        return "Candidate looks better for support_gate."
    return "Comparison is inconclusive."


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return "%d%%" % int(round(value * 100.0))


def format_summary_text(summary: dict[str, Any]) -> str:
    status_counts = summary.get("run_status_counts", {})
    objective_counts = summary.get("objective_counts", {})
    support_gate = summary.get("support_gate", {})
    recommendations = summary.get("recommendations", [])

    lines: list[str] = []
    lines.append("Run Metrics History Analysis")
    lines.append(
        "Exports read=%d (total valid=%d, invalid lines=%d)"
        % (
            int(summary.get("exports_read", 0)),
            int(summary.get("input_total_records", 0)),
            int(summary.get("invalid_lines", 0)),
        )
    )
    objective_filter = str(summary.get("objective_filter", "")).strip()
    if objective_filter:
        lines.append("Filter objective_id=%s" % objective_filter)
    limit = summary.get("limit")
    if isinstance(limit, int) and limit > 0:
        lines.append("Limit=%d (latest records)" % limit)
    lines.append(
        "Runs: completed=%d failed=%d running=%d"
        % (
            int(status_counts.get("completed", 0)),
            int(status_counts.get("failed", 0)),
            int(status_counts.get("running", 0)),
        )
    )

    if objective_counts:
        objective_parts = [f"{objective_id}={count}" for objective_id, count in sorted(objective_counts.items())]
        lines.append("Objectives: " + ", ".join(objective_parts))
    else:
        lines.append("Objectives: none")

    lines.append("Support gate records=%d" % int(support_gate.get("records", 0)))
    lines.append(
        "Support gate avg: attempts=%s success=%s rate=%s available=%s"
        % (
            "n/a" if support_gate.get("avg_support_gate_run_attempts") is None else f"{float(support_gate.get('avg_support_gate_run_attempts')):.2f}",
            "n/a" if support_gate.get("avg_support_gate_run_success") is None else f"{float(support_gate.get('avg_support_gate_run_success')):.2f}",
            _pct(_as_float(support_gate.get("avg_support_gate_run_success_rate"))),
            _pct(_as_float(support_gate.get("avg_support_gate_run_available_ratio"))),
        )
    )
    lines.append(
        "Support gate best=%s worst=%s objective_success=%s"
        % (
            str(support_gate.get("best_run", "n/a")),
            str(support_gate.get("worst_run", "n/a")),
            _pct(_as_float(support_gate.get("objective_success_rate"))),
        )
    )
    lines.append("Recommendations:")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")

    comparison = summary.get("comparison")
    if isinstance(comparison, dict):
        support_gate_comparison = comparison.get("support_gate", {})
        baseline_metrics = support_gate_comparison.get("baseline", {})
        candidate_metrics = support_gate_comparison.get("candidate", {})
        delta_metrics = support_gate_comparison.get("delta", {})
        delta_percent_metrics = support_gate_comparison.get("delta_percent", {})
        comparison_recommendation = str(comparison.get("recommendation", "")).strip()
        comparison_confidence = str(comparison.get("confidence", "")).strip().lower()

        lines.append("")
        lines.append("Comparison:")
        lines.append(
            "Baseline exports=%d Candidate exports=%d"
            % (
                int(comparison.get("baseline_exports_read", 0)),
                int(comparison.get("candidate_exports_read", 0)),
            )
        )
        if comparison_confidence:
            lines.append("Comparison confidence: %s" % comparison_confidence)
            if comparison_confidence == "low":
                lines.append("Use more runs before trusting this comparison.")
        if comparison_recommendation:
            lines.append("Comparison recommendation: %s" % comparison_recommendation)
        for metric_name in COMPARISON_SUPPORT_GATE_METRICS:
            is_rate_metric = metric_name in COMPARISON_RATE_METRICS
            baseline_value = _as_float(baseline_metrics.get(metric_name))
            candidate_value = _as_float(candidate_metrics.get(metric_name))
            delta_value = _as_float(delta_metrics.get(metric_name))
            delta_percent_value = _as_float(delta_percent_metrics.get(metric_name))
            baseline_label = _format_ratio(baseline_value) if is_rate_metric else _format_number(baseline_value)
            candidate_label = _format_ratio(candidate_value) if is_rate_metric else _format_number(candidate_value)
            delta_label = _format_delta(delta_value, is_rate_metric)
            change_label = _format_percent_change(delta_percent_value)
            lines.append(
                "- %s: baseline=%s candidate=%s delta=%s (change=%s)"
                % (metric_name, baseline_label, candidate_label, delta_label, change_label)
            )
    return "\n".join(lines)


def format_summary_markdown(summary: dict[str, Any]) -> str:
    status_counts = summary.get("run_status_counts", {})
    objective_counts = summary.get("objective_counts", {})
    support_gate = summary.get("support_gate", {})
    recommendations = summary.get("recommendations", [])

    lines: list[str] = []
    lines.append("# Run Metrics History Analysis")
    lines.append("")
    lines.append(
        "- Exports read: %d" % int(summary.get("exports_read", 0))
    )
    lines.append(
        "- Total valid records: %d" % int(summary.get("input_total_records", 0))
    )
    lines.append(
        "- Invalid lines: %d" % int(summary.get("invalid_lines", 0))
    )

    objective_filter = str(summary.get("objective_filter", "")).strip()
    if objective_filter:
        lines.append("- Objective filter: `%s`" % objective_filter)
    limit = summary.get("limit")
    if isinstance(limit, int) and limit > 0:
        lines.append("- Limit: %d latest records" % limit)

    lines.append("")
    lines.append("## Run status counts")
    lines.append(
        "- completed: %d" % int(status_counts.get("completed", 0))
    )
    lines.append(
        "- failed: %d" % int(status_counts.get("failed", 0))
    )
    lines.append(
        "- running: %d" % int(status_counts.get("running", 0))
    )

    lines.append("")
    lines.append("## Objective counts")
    if objective_counts:
        for objective_id, count in sorted(objective_counts.items()):
            lines.append("- %s: %d" % (objective_id, int(count)))
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## Support gate")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append("| records | %d |" % int(support_gate.get("records", 0)))
    lines.append(
        "| avg attempts | %s |"
        % (
            "n/a"
            if support_gate.get("avg_support_gate_run_attempts") is None
            else f"{float(support_gate.get('avg_support_gate_run_attempts')):.2f}"
        )
    )
    lines.append(
        "| avg success | %s |"
        % (
            "n/a"
            if support_gate.get("avg_support_gate_run_success") is None
            else f"{float(support_gate.get('avg_support_gate_run_success')):.2f}"
        )
    )
    lines.append(
        "| avg success rate | %s |"
        % _pct(_as_float(support_gate.get("avg_support_gate_run_success_rate")))
    )
    lines.append(
        "| avg available ratio | %s |"
        % _pct(_as_float(support_gate.get("avg_support_gate_run_available_ratio")))
    )
    lines.append("| best run | %s |" % str(support_gate.get("best_run", "n/a")))
    lines.append("| worst run | %s |" % str(support_gate.get("worst_run", "n/a")))
    lines.append(
        "| objective success rate | %s |"
        % _pct(_as_float(support_gate.get("objective_success_rate")))
    )

    lines.append("")
    lines.append("## Recommendations")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")

    comparison = summary.get("comparison")
    if isinstance(comparison, dict):
        support_gate_comparison = comparison.get("support_gate", {})
        baseline_metrics = support_gate_comparison.get("baseline", {})
        candidate_metrics = support_gate_comparison.get("candidate", {})
        delta_metrics = support_gate_comparison.get("delta", {})
        delta_percent_metrics = support_gate_comparison.get("delta_percent", {})
        comparison_recommendation = str(comparison.get("recommendation", "")).strip()
        comparison_confidence = str(comparison.get("confidence", "")).strip().lower()

        lines.append("")
        lines.append("## Comparison")
        lines.append("")
        lines.append(
            "- Baseline exports read: %d"
            % int(comparison.get("baseline_exports_read", 0))
        )
        lines.append(
            "- Candidate exports read: %d"
            % int(comparison.get("candidate_exports_read", 0))
        )
        if comparison_confidence:
            lines.append("- Confidence: %s" % comparison_confidence)
            if comparison_confidence == "low":
                lines.append("- Use more runs before trusting this comparison.")
        if comparison_recommendation:
            lines.append("- Recommendation: %s" % comparison_recommendation)
        lines.append("| Metric | Baseline | Candidate | Delta | Change |")
        lines.append("|---|---|---|---|---|")
        for metric_name in COMPARISON_SUPPORT_GATE_METRICS:
            is_rate_metric = metric_name in COMPARISON_RATE_METRICS
            baseline_value = _as_float(baseline_metrics.get(metric_name))
            candidate_value = _as_float(candidate_metrics.get(metric_name))
            delta_value = _as_float(delta_metrics.get(metric_name))
            delta_percent_value = _as_float(delta_percent_metrics.get(metric_name))
            baseline_label = _format_ratio(baseline_value) if is_rate_metric else _format_number(baseline_value)
            candidate_label = _format_ratio(candidate_value) if is_rate_metric else _format_number(candidate_value)
            delta_label = _format_delta(delta_value, is_rate_metric)
            change_label = _format_percent_change(delta_percent_value)
            lines.append(
                "| %s | %s | %s | %s | %s |"
                % (metric_name, baseline_label, candidate_label, delta_label, change_label)
            )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze run metrics history JSONL exports.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to run_metrics_history.jsonl file.",
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help="Optional objective_id filter (example: support_gate).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit on the number of latest filtered records.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown", "md"),
        default="text",
        help="Output format. Default is text.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output file path. If provided, writes result to file instead of stdout.",
    )
    parser.add_argument(
        "--compare-input",
        type=Path,
        default=None,
        help="Optional second JSONL file to compare against --input (treated as candidate).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path: Path = args.input
    objective = args.objective.strip()
    limit = int(args.limit)
    if limit < 0:
        print("ERROR: --limit must be >= 0")
        return 1
    if not input_path.exists():
        print("ERROR: input file not found: %s" % input_path)
        return 1
    compare_input_path: Path | None = args.compare_input
    if compare_input_path is not None and not compare_input_path.exists():
        print("ERROR: compare input file not found: %s" % compare_input_path)
        return 1

    records, invalid_lines = read_jsonl_records(input_path)
    summary = build_summary(
        records,
        invalid_lines,
        objective_filter=objective if objective else None,
        limit=limit if limit > 0 else None,
    )
    if compare_input_path is not None:
        compare_records, compare_invalid_lines = read_jsonl_records(compare_input_path)
        candidate_summary = build_summary(
            compare_records,
            compare_invalid_lines,
            objective_filter=objective if objective else None,
            limit=limit if limit > 0 else None,
        )
        summary["comparison"] = build_comparison_summary(summary, candidate_summary)

    output_format = str(args.format).strip().lower()
    if output_format == "md":
        output_format = "markdown"

    rendered_output = ""
    if output_format == "json":
        rendered_output = json.dumps(summary, indent=2, ensure_ascii=False)
    elif output_format == "markdown":
        rendered_output = format_summary_markdown(summary)
    else:
        rendered_output = format_summary_text(summary)

    output_path: Path | None = args.output
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered_output + "\n", encoding="utf-8")
    else:
        print(rendered_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
