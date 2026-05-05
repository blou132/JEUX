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
    "stddev_support_gate_run_success_rate",
)
COMPARISON_RATE_METRICS = {
    "avg_support_gate_run_success_rate",
    "avg_support_gate_run_available_ratio",
    "objective_success_rate",
    "stddev_support_gate_run_success_rate",
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


def _pick_best_champion_run(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    best_record: dict[str, Any] | None = None
    best_key: tuple[float, float, float] | None = None
    for record in records:
        rate = _as_float(record.get("champion_support_run_success_rate"))
        success = _as_float(record.get("champion_support_run_success"))
        attempts = _as_float(record.get("champion_support_run_attempts"))
        if rate is None:
            continue
        key = (
            rate,
            success if success is not None else -1.0,
            attempts if attempts is not None else -1.0,
        )
        if best_key is None or key > best_key:
            best_key = key
            best_record = record
    return best_record


def _pick_worst_champion_run(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    worst_record: dict[str, Any] | None = None
    worst_key: tuple[float, float, float] | None = None
    for record in records:
        rate = _as_float(record.get("champion_support_run_success_rate"))
        success = _as_float(record.get("champion_support_run_success"))
        attempts = _as_float(record.get("champion_support_run_attempts"))
        if rate is None:
            continue
        key = (
            rate,
            success if success is not None else 2.0,
            attempts if attempts is not None else 2.0,
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


def _stddev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean_value = float(sum(values) / len(values))
    variance = float(sum((value - mean_value) ** 2 for value in values) / len(values))
    return variance ** 0.5


def _build_support_gate_stability_label(success_rate_values: list[float]) -> str:
    stddev_success_rate = _stddev(success_rate_values)
    if stddev_success_rate is None:
        return "unknown"
    if stddev_success_rate >= 0.25:
        return "unstable"
    if stddev_success_rate >= 0.12:
        return "variable"
    return "stable"


def _build_pressure_label(blocked_avg: float | None, attempts_avg: float | None) -> str:
    if blocked_avg is None or attempts_avg is None:
        return "n/a"
    if attempts_avg <= 0.0:
        return "n/a"
    blocked_ratio = max(0.0, blocked_avg) / attempts_avg
    if blocked_ratio >= 0.60:
        return "high"
    if blocked_ratio >= 0.30:
        return "medium"
    return "low"


def _build_champion_support_interpretation(
    records: int,
    attempts_avg: float | None,
    success_rate_avg: float | None,
    cooldown_pressure: str,
    unavailable_pressure: str,
    objective_completed: int,
    objective_failed: int,
) -> str:
    if records <= 0:
        return "n/a"
    if (
        attempts_avg is None
        and success_rate_avg is None
        and cooldown_pressure == "n/a"
        and unavailable_pressure == "n/a"
    ):
        return "n/a"

    signals: list[str] = []
    if attempts_avg is not None and attempts_avg < 2.0:
        signals.append("few attempts")
    if success_rate_avg is not None and success_rate_avg < 0.40:
        signals.append("low success rate")
    if cooldown_pressure == "high":
        signals.append("high cooldown pressure")
    elif cooldown_pressure == "medium":
        signals.append("medium cooldown pressure")
    if unavailable_pressure == "high":
        signals.append("high unavailable pressure")
    elif unavailable_pressure == "medium":
        signals.append("medium unavailable pressure")
    if objective_failed > objective_completed and attempts_avg is not None and attempts_avg > 0.0:
        signals.append("objective often failed despite attempts")
    if not signals:
        return "no major champion support pressure detected"
    return "; ".join(signals)


def _build_champion_multi_run_stability_label(
    records: int,
    has_data: bool,
    success_rate_values: list[float],
    objective_completed: int,
    objective_failed: int,
) -> str:
    if records < 2 or not has_data:
        return "n/a"
    if objective_completed > 0 and objective_failed > 0:
        return "unstable"
    success_rate_stddev = _stddev(success_rate_values)
    if success_rate_stddev is None:
        return "n/a"
    if success_rate_stddev >= 0.20:
        return "unstable"
    if success_rate_stddev >= 0.10:
        return "variable"
    return "stable"


def _build_champion_multi_run_interpretation(
    records: int,
    has_data: bool,
    attempts_avg: float | None,
    success_rate_avg: float | None,
    cooldown_pressure: str,
    unavailable_pressure: str,
    objective_completed: int,
    objective_failed: int,
    stability_label: str,
) -> str:
    if records <= 0 or not has_data:
        return "no_data"
    if attempts_avg is not None and attempts_avg < 2.0:
        return "low_attempts"
    if cooldown_pressure == "high":
        return "cooldown_bottleneck"
    if unavailable_pressure == "high":
        return "unavailable_bottleneck"
    if objective_completed > 0 and objective_failed > 0:
        return "unstable_success"
    if objective_completed > 0 and objective_failed == 0:
        if success_rate_avg is None or success_rate_avg >= 0.40:
            return "stable_successful"
    if stability_label == "unstable":
        return "unstable_success"
    if objective_failed > 0:
        return "unstable_success"
    return "stable_successful"


def _build_support_gate_main_bottleneck(
    records: int,
    success_rate_avg: float | None,
    available_ratio_avg: float | None,
    stability_label: str,
) -> str:
    if records <= 0 or success_rate_avg is None:
        return "n/a"
    if available_ratio_avg is not None and available_ratio_avg < 0.25:
        return "availability"
    if (
        available_ratio_avg is not None
        and available_ratio_avg >= 0.25
        and success_rate_avg < 0.40
    ):
        return "success_rate"
    if stability_label in {"unstable", "variable"}:
        return "stability"
    return "none"


def _build_support_systems_summary(
    support_gate_success_rate_avg: float | None,
    support_gate_main_bottleneck: str,
    support_gate_stability_label: str,
    support_gate_records: int,
    champion_success_rate_avg: float | None,
    champion_global_interpretation: str,
    champion_records: int,
) -> dict[str, Any]:
    support_gate_has_data = support_gate_records > 0 and support_gate_success_rate_avg is not None
    champion_has_data = champion_records > 0 and champion_success_rate_avg is not None

    data_state = "partial"
    if support_gate_has_data and champion_has_data:
        data_state = "complete"
    elif not support_gate_has_data and not champion_has_data:
        data_state = "no_data"

    support_gate_is_limited = support_gate_has_data and support_gate_main_bottleneck not in {"none", "n/a"}
    support_gate_is_stable = (
        support_gate_has_data
        and support_gate_main_bottleneck == "none"
        and support_gate_stability_label == "stable"
    )
    champion_is_stable = champion_global_interpretation == "stable_successful"
    champion_is_limited = champion_global_interpretation in {
        "unstable_success",
        "cooldown_bottleneck",
        "unavailable_bottleneck",
        "low_attempts",
    }

    interpretation = "partial_data"
    if data_state == "no_data":
        interpretation = "no_data"
    elif data_state == "partial":
        interpretation = "partial_data"
    elif support_gate_is_stable and champion_is_stable:
        interpretation = "both_stable"
    elif support_gate_is_stable and champion_is_limited:
        interpretation = "support_gate_stable_champion_unstable"
    elif support_gate_is_limited and champion_is_stable:
        interpretation = "support_gate_limited_champion_stable"
    elif support_gate_is_limited and champion_is_limited:
        interpretation = "both_limited"
    else:
        interpretation = "partial_data"

    support_gate_label = (
        "rate=%s bottleneck=%s"
        % (_pct(support_gate_success_rate_avg), support_gate_main_bottleneck)
    )
    rally_champion_label = (
        "rate=%s interpretation=%s"
        % (_pct(champion_success_rate_avg), champion_global_interpretation or "no_data")
    )

    return {
        "support_gate_success_rate_avg": support_gate_success_rate_avg,
        "rally_champion_success_rate_avg": champion_success_rate_avg,
        "support_gate_main_bottleneck": support_gate_main_bottleneck,
        "rally_champion_global_interpretation": champion_global_interpretation or "no_data",
        "data_state": data_state,
        "support_gate": support_gate_label,
        "rally_champion": rally_champion_label,
        "global_state": data_state,
        "interpretation": interpretation,
    }


def build_support_gate_recommendations(summary: dict[str, Any]) -> list[str]:
    support_gate = summary.get("support_gate", {})
    records = int(support_gate.get("records", 0))
    avg_available_ratio = _as_float(support_gate.get("avg_support_gate_run_available_ratio"))
    avg_success_rate = _as_float(support_gate.get("avg_support_gate_run_success_rate"))
    objective_success_rate = _as_float(support_gate.get("objective_success_rate"))
    stability_label = str(support_gate.get("support_gate_stability_label", "")).strip().lower()
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
    if stability_label == "unstable":
        recommendations.append("Support gate results vary a lot: run more tests before changing tuning.")

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
    success_rate_numeric_values = [value for value in success_rate_values if value is not None]
    available_rate_numeric_values = [value for value in available_rate_values if value is not None]

    attempts_avg = _average([value for value in attempts_values if value is not None])
    success_avg = _average([value for value in success_values if value is not None])
    success_rate_avg = _average(success_rate_numeric_values)
    available_rate_avg = _average(available_rate_numeric_values)
    success_rate_stddev = _stddev(success_rate_numeric_values)
    available_rate_stddev = _stddev(available_rate_numeric_values)
    support_gate_stability_label = _build_support_gate_stability_label(success_rate_numeric_values)

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

    champion_support_records = [
        record for record in filtered_records if str(record.get("objective_id", "")) == "rally_champion"
    ]
    champion_attempt_values = [
        _as_float(record.get("champion_support_run_attempts"))
        for record in champion_support_records
    ]
    champion_success_values = [
        _as_float(record.get("champion_support_run_success"))
        for record in champion_support_records
    ]
    champion_success_rate_values = [
        _as_float(record.get("champion_support_run_success_rate"))
        for record in champion_support_records
    ]
    champion_success_rate_numeric_values = [
        value for value in champion_success_rate_values if value is not None
    ]
    champion_attempt_avg = _average([value for value in champion_attempt_values if value is not None])
    champion_success_avg = _average([value for value in champion_success_values if value is not None])
    champion_success_rate_avg = _average(champion_success_rate_numeric_values)
    champion_attempt_total_values = [
        _as_float(record.get("champion_support_attempts_total"))
        for record in champion_support_records
    ]
    champion_success_total_values = [
        _as_float(record.get("champion_support_success_total"))
        for record in champion_support_records
    ]
    champion_unavailable_total_values = [
        _as_float(record.get("champion_support_unavailable_total"))
        for record in champion_support_records
    ]
    champion_cooldown_total_values = [
        _as_float(record.get("champion_support_cooldown_blocked_total"))
        for record in champion_support_records
    ]
    champion_completed_total_values = [
        _as_float(record.get("champion_support_completed_total"))
        for record in champion_support_records
    ]
    champion_failed_total_values = [
        _as_float(record.get("champion_support_failed_total"))
        for record in champion_support_records
    ]
    champion_attempt_total_avg = _average(
        [value for value in champion_attempt_total_values if value is not None]
    )
    champion_success_total_avg = _average(
        [value for value in champion_success_total_values if value is not None]
    )
    champion_unavailable_total_avg = _average(
        [value for value in champion_unavailable_total_values if value is not None]
    )
    champion_cooldown_total_avg = _average(
        [value for value in champion_cooldown_total_values if value is not None]
    )
    champion_completed_total_avg = _average(
        [value for value in champion_completed_total_values if value is not None]
    )
    champion_failed_total_avg = _average(
        [value for value in champion_failed_total_values if value is not None]
    )

    champion_completed = 0
    champion_failed = 0
    for record in champion_support_records:
        objective_status = str(record.get("objective_status", "")).strip().lower()
        if objective_status == "completed":
            champion_completed += 1
        elif objective_status == "failed":
            champion_failed += 1

    champion_objective_success_rate: float | None = None
    champion_resolved = champion_completed + champion_failed
    if champion_resolved > 0:
        champion_objective_success_rate = float(champion_completed / champion_resolved)
    champion_cooldown_pressure = _build_pressure_label(
        champion_cooldown_total_avg, champion_attempt_total_avg
    )
    champion_unavailable_pressure = _build_pressure_label(
        champion_unavailable_total_avg, champion_attempt_total_avg
    )
    champion_interpretation = _build_champion_support_interpretation(
        records=len(champion_support_records),
        attempts_avg=champion_attempt_avg,
        success_rate_avg=champion_success_rate_avg,
        cooldown_pressure=champion_cooldown_pressure,
        unavailable_pressure=champion_unavailable_pressure,
        objective_completed=champion_completed,
        objective_failed=champion_failed,
    )
    champion_multi_run_has_data = any(
        value is not None
        for value in [
            champion_attempt_avg,
            champion_success_avg,
            champion_success_rate_avg,
            champion_cooldown_total_avg,
            champion_unavailable_total_avg,
        ]
    )
    champion_multi_run_stability = _build_champion_multi_run_stability_label(
        records=len(champion_support_records),
        has_data=champion_multi_run_has_data,
        success_rate_values=champion_success_rate_numeric_values,
        objective_completed=champion_completed,
        objective_failed=champion_failed,
    )
    champion_multi_run_interpretation = _build_champion_multi_run_interpretation(
        records=len(champion_support_records),
        has_data=champion_multi_run_has_data,
        attempts_avg=champion_attempt_avg,
        success_rate_avg=champion_success_rate_avg,
        cooldown_pressure=champion_cooldown_pressure,
        unavailable_pressure=champion_unavailable_pressure,
        objective_completed=champion_completed,
        objective_failed=champion_failed,
        stability_label=champion_multi_run_stability,
    )
    support_gate_main_bottleneck = _build_support_gate_main_bottleneck(
        records=len(support_gate_records),
        success_rate_avg=success_rate_avg,
        available_ratio_avg=available_rate_avg,
        stability_label=support_gate_stability_label,
    )
    support_systems_summary = _build_support_systems_summary(
        support_gate_success_rate_avg=success_rate_avg,
        support_gate_main_bottleneck=support_gate_main_bottleneck,
        support_gate_stability_label=support_gate_stability_label,
        support_gate_records=len(support_gate_records),
        champion_success_rate_avg=champion_success_rate_avg,
        champion_global_interpretation=champion_multi_run_interpretation,
        champion_records=len(champion_support_records),
    )

    champion_best_run = _pick_best_champion_run(champion_support_records)
    champion_worst_run = _pick_worst_champion_run(champion_support_records)
    champion_tuning_label = ""
    for record in reversed(champion_support_records):
        label = str(record.get("champion_support_tuning_label", "")).strip()
        if label != "":
            champion_tuning_label = label
            break

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
            "stddev_support_gate_run_success_rate": success_rate_stddev,
            "stddev_support_gate_run_available_ratio": available_rate_stddev,
            "support_gate_stability_label": support_gate_stability_label,
            "best_run": _run_label(best_run),
            "worst_run": _run_label(worst_run),
            "objective_success_rate": objective_success_rate,
            "objective_completed": support_gate_completed,
            "objective_failed": support_gate_failed,
        },
        "champion_support": {
            "records": len(champion_support_records),
            "avg_champion_support_run_attempts": champion_attempt_avg,
            "avg_champion_support_run_success": champion_success_avg,
            "avg_champion_support_run_success_rate": champion_success_rate_avg,
            "avg_champion_support_attempts_total": champion_attempt_total_avg,
            "avg_champion_support_success_total": champion_success_total_avg,
            "avg_champion_support_unavailable_total": champion_unavailable_total_avg,
            "avg_champion_support_cooldown_blocked_total": champion_cooldown_total_avg,
            "avg_champion_support_completed_total": champion_completed_total_avg,
            "avg_champion_support_failed_total": champion_failed_total_avg,
            "best_run": _run_label(champion_best_run),
            "worst_run": _run_label(champion_worst_run),
            "objective_success_rate": champion_objective_success_rate,
            "objective_completed": champion_completed,
            "objective_failed": champion_failed,
            "latest_champion_support_tuning_label": champion_tuning_label,
            "diagnostic": {
                "attempts_avg": champion_attempt_avg,
                "success_rate_avg": champion_success_rate_avg,
                "cooldown_pressure": champion_cooldown_pressure,
                "unavailable_pressure": champion_unavailable_pressure,
                "objective_completion": "%d/%d" % (champion_completed, champion_resolved),
                "interpretation": champion_interpretation,
            },
            "multi_run_comparison": {
                "avg_attempts": champion_attempt_avg,
                "avg_success": champion_success_avg,
                "avg_success_rate": champion_success_rate_avg,
                "avg_cooldown": champion_cooldown_total_avg,
                "avg_unavailable": champion_unavailable_total_avg,
                "objective_completed": champion_completed,
                "objective_failed": champion_failed,
                "diagnostic_stability": champion_multi_run_stability,
                "global_interpretation": champion_multi_run_interpretation,
            },
        },
        "support_systems_summary": support_systems_summary,
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


def build_final_decision(summary: dict[str, Any]) -> str:
    comparison = summary.get("comparison")
    support_gate = summary.get("support_gate", {})
    recommendations = summary.get("recommendations", [])
    support_gate_records = int(support_gate.get("records", 0))
    stability_label = str(support_gate.get("support_gate_stability_label", "")).strip().lower()

    if isinstance(comparison, dict):
        confidence = str(comparison.get("confidence", "")).strip().lower()
        recommendation = str(comparison.get("recommendation", "")).strip().lower()
        if confidence == "low":
            return "Collect more runs before deciding."
        if (
            recommendation == "candidate looks better for support_gate."
            and confidence in {"medium", "high"}
            and stability_label != "unstable"
        ):
            return "Candidate tuning can be kept for further testing."
        if recommendation == "candidate looks worse for support_gate.":
            return "Reject candidate tuning or revert."
        if recommendation.startswith("mixed result"):
            return "Review tradeoff before changing tuning."
        return "No clear tuning decision."

    if support_gate_records <= 0:
        return "Collect support_gate runs first."
    if stability_label == "unstable":
        return "Run more tests before tuning."

    recommendation_lines = [str(item).lower() for item in recommendations] if isinstance(recommendations, list) else []
    if any("too easy" in item for item in recommendation_lines):
        return "Consider making support_gate slightly harder."
    if any("availability looks low" in item for item in recommendation_lines):
        return "Consider increasing gate availability."
    if any("success rate is low" in item for item in recommendation_lines):
        return "Consider improving feedback or easing interaction."
    if stability_label == "stable":
        return "Current support_gate tuning looks acceptable."
    return "No clear tuning decision."


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return "%d%%" % int(round(value * 100.0))


def format_summary_text(summary: dict[str, Any]) -> str:
    status_counts = summary.get("run_status_counts", {})
    objective_counts = summary.get("objective_counts", {})
    support_gate = summary.get("support_gate", {})
    champion_support = summary.get("champion_support", {})
    support_systems_summary = summary.get("support_systems_summary", {})
    recommendations = summary.get("recommendations", [])
    final_decision = str(summary.get("final_decision", "")).strip()

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
    lines.append(
        "Support gate stability: %s"
        % str(support_gate.get("support_gate_stability_label", "unknown"))
    )
    lines.append("Champion support records=%d" % int(champion_support.get("records", 0)))
    lines.append(
        "Champion support avg: attempts=%s success=%s rate=%s"
        % (
            (
                "n/a"
                if champion_support.get("avg_champion_support_run_attempts") is None
                else f"{float(champion_support.get('avg_champion_support_run_attempts')):.2f}"
            ),
            (
                "n/a"
                if champion_support.get("avg_champion_support_run_success") is None
                else f"{float(champion_support.get('avg_champion_support_run_success')):.2f}"
            ),
            _pct(_as_float(champion_support.get("avg_champion_support_run_success_rate"))),
        )
    )
    lines.append(
        "Champion support best=%s worst=%s objective_success=%s"
        % (
            str(champion_support.get("best_run", "n/a")),
            str(champion_support.get("worst_run", "n/a")),
            _pct(_as_float(champion_support.get("objective_success_rate"))),
        )
    )
    champion_tuning_label = str(champion_support.get("latest_champion_support_tuning_label", "")).strip()
    if champion_tuning_label:
        lines.append("Champion support latest tuning: %s" % champion_tuning_label)
    champion_diagnostic = champion_support.get("diagnostic", {})
    champion_cooldown_pressure = str(champion_diagnostic.get("cooldown_pressure", "n/a")).strip() or "n/a"
    champion_unavailable_pressure = str(champion_diagnostic.get("unavailable_pressure", "n/a")).strip() or "n/a"
    champion_objective_completion = (
        str(champion_diagnostic.get("objective_completion", "")).strip()
        or "n/a"
    )
    champion_interpretation = (
        str(champion_diagnostic.get("interpretation", "")).strip()
        or "n/a"
    )
    lines.append("Champion support diagnostic:")
    lines.append(
        "- attempts avg: %s"
        % (
            "n/a"
            if champion_diagnostic.get("attempts_avg") is None
            else f"{float(champion_diagnostic.get('attempts_avg')):.2f}"
        )
    )
    lines.append(
        "- success rate avg: %s"
        % _pct(_as_float(champion_diagnostic.get("success_rate_avg")))
    )
    lines.append("- cooldown pressure: %s" % champion_cooldown_pressure)
    lines.append("- unavailable pressure: %s" % champion_unavailable_pressure)
    lines.append("- objective completion: %s" % champion_objective_completion)
    lines.append("- interpretation: %s" % champion_interpretation)
    champion_multi_run = champion_support.get("multi_run_comparison", {})
    champion_multi_run_stability = (
        str(champion_multi_run.get("diagnostic_stability", "")).strip()
        or "n/a"
    )
    champion_multi_run_interpretation = (
        str(champion_multi_run.get("global_interpretation", "")).strip()
        or "no_data"
    )
    lines.append("Champion support multi-run comparison:")
    lines.append(
        "- attempts avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_attempts") is None
            else f"{float(champion_multi_run.get('avg_attempts')):.2f}"
        )
    )
    lines.append(
        "- success avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_success") is None
            else f"{float(champion_multi_run.get('avg_success')):.2f}"
        )
    )
    lines.append(
        "- success rate avg: %s"
        % _pct(_as_float(champion_multi_run.get("avg_success_rate")))
    )
    lines.append(
        "- cooldown avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_cooldown") is None
            else f"{float(champion_multi_run.get('avg_cooldown')):.2f}"
        )
    )
    lines.append(
        "- unavailable avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_unavailable") is None
            else f"{float(champion_multi_run.get('avg_unavailable')):.2f}"
        )
    )
    lines.append(
        "- objective completed: %d"
        % int(champion_multi_run.get("objective_completed", 0))
    )
    lines.append(
        "- objective failed: %d"
        % int(champion_multi_run.get("objective_failed", 0))
    )
    lines.append("- diagnostic stability: %s" % champion_multi_run_stability)
    lines.append("- global interpretation: %s" % champion_multi_run_interpretation)
    lines.append("Support systems summary:")
    lines.append("- support_gate: %s" % str(support_systems_summary.get("support_gate", "n/a")))
    lines.append("- rally_champion: %s" % str(support_systems_summary.get("rally_champion", "n/a")))
    lines.append("- global state: %s" % str(support_systems_summary.get("global_state", "no_data")))
    lines.append("- interpretation: %s" % str(support_systems_summary.get("interpretation", "no_data")))
    lines.append("Recommendations:")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")
    if final_decision:
        lines.append("Final decision: %s" % final_decision)

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
    champion_support = summary.get("champion_support", {})
    support_systems_summary = summary.get("support_systems_summary", {})
    recommendations = summary.get("recommendations", [])
    final_decision = str(summary.get("final_decision", "")).strip()

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
    lines.append(
        "| stddev success rate | %s |"
        % _pct(_as_float(support_gate.get("stddev_support_gate_run_success_rate")))
    )
    lines.append(
        "| stddev available ratio | %s |"
        % _pct(_as_float(support_gate.get("stddev_support_gate_run_available_ratio")))
    )
    lines.append(
        "| support gate stability | %s |"
        % str(support_gate.get("support_gate_stability_label", "unknown"))
    )

    lines.append("")
    lines.append("## Champion support")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append("| records | %d |" % int(champion_support.get("records", 0)))
    lines.append(
        "| avg attempts | %s |"
        % (
            "n/a"
            if champion_support.get("avg_champion_support_run_attempts") is None
            else f"{float(champion_support.get('avg_champion_support_run_attempts')):.2f}"
        )
    )
    lines.append(
        "| avg success | %s |"
        % (
            "n/a"
            if champion_support.get("avg_champion_support_run_success") is None
            else f"{float(champion_support.get('avg_champion_support_run_success')):.2f}"
        )
    )
    lines.append(
        "| avg success rate | %s |"
        % _pct(_as_float(champion_support.get("avg_champion_support_run_success_rate")))
    )
    lines.append("| best run | %s |" % str(champion_support.get("best_run", "n/a")))
    lines.append("| worst run | %s |" % str(champion_support.get("worst_run", "n/a")))
    lines.append(
        "| objective success rate | %s |"
        % _pct(_as_float(champion_support.get("objective_success_rate")))
    )
    lines.append(
        "| latest tuning label | %s |"
        % (
            str(champion_support.get("latest_champion_support_tuning_label", "")).strip()
            if str(champion_support.get("latest_champion_support_tuning_label", "")).strip()
            else "n/a"
        )
    )
    champion_diagnostic = champion_support.get("diagnostic", {})
    champion_cooldown_pressure = str(champion_diagnostic.get("cooldown_pressure", "n/a")).strip() or "n/a"
    champion_unavailable_pressure = str(champion_diagnostic.get("unavailable_pressure", "n/a")).strip() or "n/a"
    champion_objective_completion = (
        str(champion_diagnostic.get("objective_completion", "")).strip()
        or "n/a"
    )
    champion_interpretation = (
        str(champion_diagnostic.get("interpretation", "")).strip()
        or "n/a"
    )

    lines.append("")
    lines.append("### Champion support diagnostic")
    lines.append(
        "- attempts avg: %s"
        % (
            "n/a"
            if champion_diagnostic.get("attempts_avg") is None
            else f"{float(champion_diagnostic.get('attempts_avg')):.2f}"
        )
    )
    lines.append(
        "- success rate avg: %s"
        % _pct(_as_float(champion_diagnostic.get("success_rate_avg")))
    )
    lines.append("- cooldown pressure: %s" % champion_cooldown_pressure)
    lines.append("- unavailable pressure: %s" % champion_unavailable_pressure)
    lines.append("- objective completion: %s" % champion_objective_completion)
    lines.append("- interpretation: %s" % champion_interpretation)
    champion_multi_run = champion_support.get("multi_run_comparison", {})
    champion_multi_run_stability = (
        str(champion_multi_run.get("diagnostic_stability", "")).strip()
        or "n/a"
    )
    champion_multi_run_interpretation = (
        str(champion_multi_run.get("global_interpretation", "")).strip()
        or "no_data"
    )
    lines.append("")
    lines.append("### Champion support multi-run comparison")
    lines.append(
        "- attempts avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_attempts") is None
            else f"{float(champion_multi_run.get('avg_attempts')):.2f}"
        )
    )
    lines.append(
        "- success avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_success") is None
            else f"{float(champion_multi_run.get('avg_success')):.2f}"
        )
    )
    lines.append(
        "- success rate avg: %s"
        % _pct(_as_float(champion_multi_run.get("avg_success_rate")))
    )
    lines.append(
        "- cooldown avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_cooldown") is None
            else f"{float(champion_multi_run.get('avg_cooldown')):.2f}"
        )
    )
    lines.append(
        "- unavailable avg: %s"
        % (
            "n/a"
            if champion_multi_run.get("avg_unavailable") is None
            else f"{float(champion_multi_run.get('avg_unavailable')):.2f}"
        )
    )
    lines.append(
        "- objective completed: %d"
        % int(champion_multi_run.get("objective_completed", 0))
    )
    lines.append(
        "- objective failed: %d"
        % int(champion_multi_run.get("objective_failed", 0))
    )
    lines.append("- diagnostic stability: %s" % champion_multi_run_stability)
    lines.append("- global interpretation: %s" % champion_multi_run_interpretation)
    lines.append("")
    lines.append("### Support systems summary")
    lines.append("- support_gate: %s" % str(support_systems_summary.get("support_gate", "n/a")))
    lines.append("- rally_champion: %s" % str(support_systems_summary.get("rally_champion", "n/a")))
    lines.append("- global state: %s" % str(support_systems_summary.get("global_state", "no_data")))
    lines.append("- interpretation: %s" % str(support_systems_summary.get("interpretation", "no_data")))

    lines.append("")
    lines.append("## Recommendations")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")
    if final_decision:
        lines.append("")
        lines.append("## Final decision")
        lines.append("- %s" % final_decision)

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
    summary["final_decision"] = build_final_decision(summary)

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
