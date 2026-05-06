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
FINAL_DECISION_TEXT_BY_CODE = {
    "collect_support_gate_runs_first": "Collect support_gate runs first.",
    "collect_more_runs_before_deciding": "Collect more runs before deciding.",
    "keep_candidate_for_more_testing": "Candidate tuning can be kept for further testing.",
    "reject_candidate_or_revert": "Reject candidate tuning or revert.",
    "review_tradeoff_before_tuning": "Review tradeoff before changing tuning.",
    "no_runtime_data": "No runtime support metrics data available.",
}


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


def _build_support_metrics_quality(
    support_gate_records: list[dict[str, Any]],
    champion_support_records: list[dict[str, Any]],
    support_gate_attempt_values: list[float | None],
    support_gate_success_values: list[float | None],
    support_gate_success_rate_values: list[float | None],
    support_gate_cooldown_values: list[float | None],
    support_gate_unavailable_values: list[float | None],
    support_gate_completed: int,
    support_gate_failed: int,
    champion_attempt_values: list[float | None],
    champion_success_values: list[float | None],
    champion_success_rate_values: list[float | None],
    champion_cooldown_values: list[float | None],
    champion_unavailable_values: list[float | None],
    champion_completed: int,
    champion_failed: int,
) -> dict[str, Any]:
    warnings: list[str] = []

    def _any_negative(values: list[float | None]) -> bool:
        return any(value is not None and value < 0.0 for value in values)

    def _any_rate_out_of_range(values: list[float | None]) -> bool:
        return any(value is not None and (value < 0.0 or value > 1.0) for value in values)

    def _any_success_greater_than_attempts(
        success_values: list[float | None], attempts_values: list[float | None]
    ) -> bool:
        for success_value, attempts_value in zip(success_values, attempts_values):
            if success_value is None or attempts_value is None:
                continue
            if success_value > attempts_value:
                return True
        return False

    support_gate_count = len(support_gate_records)
    champion_count = len(champion_support_records)

    if support_gate_count == 0:
        warnings.append("support_gate_missing")
    if champion_count == 0:
        warnings.append("champion_support_missing")

    if support_gate_count == 0 and champion_count == 0:
        warnings.append("no_support_metrics")
    else:
        if _any_success_greater_than_attempts(support_gate_success_values, support_gate_attempt_values):
            warnings.append("support_gate_success_greater_than_attempts")
        if _any_rate_out_of_range(support_gate_success_rate_values):
            warnings.append("support_gate_success_rate_out_of_range")
        if _any_negative(support_gate_attempt_values):
            warnings.append("support_gate_attempts_negative")
        if _any_negative(support_gate_cooldown_values):
            warnings.append("support_gate_cooldown_negative")
        if _any_negative(support_gate_unavailable_values):
            warnings.append("support_gate_unavailable_negative")

        if _any_success_greater_than_attempts(champion_success_values, champion_attempt_values):
            warnings.append("champion_success_greater_than_attempts")
        if _any_rate_out_of_range(champion_success_rate_values):
            warnings.append("champion_success_rate_out_of_range")
        if _any_negative(champion_attempt_values):
            warnings.append("champion_attempts_negative")
        if _any_negative(champion_cooldown_values):
            warnings.append("champion_cooldown_negative")
        if _any_negative(champion_unavailable_values):
            warnings.append("champion_unavailable_negative")

        support_gate_resolved = support_gate_completed + support_gate_failed
        if support_gate_resolved > support_gate_count:
            warnings.append("support_gate_resolution_inconsistent")
        if support_gate_count > 0 and support_gate_resolved == 0:
            warnings.append("support_gate_resolution_missing")

        champion_resolved = champion_completed + champion_failed
        if champion_resolved > champion_count:
            warnings.append("champion_resolution_inconsistent")
        if champion_count > 0 and champion_resolved == 0:
            warnings.append("champion_resolution_missing")

        champion_metric_keys = (
            "champion_support_run_attempts",
            "champion_support_run_success",
            "champion_support_run_success_rate",
            "champion_support_attempts_total",
            "champion_support_success_total",
            "champion_support_unavailable_total",
            "champion_support_cooldown_blocked_total",
            "champion_support_completed_total",
            "champion_support_failed_total",
        )
        if champion_count > 0:
            champion_records_with_metrics = 0
            for record in champion_support_records:
                if any(key in record for key in champion_metric_keys):
                    champion_records_with_metrics += 1
            if champion_records_with_metrics < champion_count:
                warnings.append("partial_legacy_export")

    warning_set = set(warnings)
    state = "valid"
    warning_issue_keys = {
        "support_gate_success_greater_than_attempts",
        "support_gate_success_rate_out_of_range",
        "support_gate_attempts_negative",
        "support_gate_cooldown_negative",
        "support_gate_unavailable_negative",
        "champion_success_greater_than_attempts",
        "champion_success_rate_out_of_range",
        "champion_attempts_negative",
        "champion_cooldown_negative",
        "champion_unavailable_negative",
        "support_gate_resolution_inconsistent",
        "support_gate_resolution_missing",
        "champion_resolution_inconsistent",
        "champion_resolution_missing",
    }
    if "no_support_metrics" in warning_set:
        state = "no_data"
    elif warning_set.intersection(warning_issue_keys):
        state = "warning"
    elif warning_set.intersection({"support_gate_missing", "champion_support_missing", "partial_legacy_export"}):
        state = "incomplete"

    interpretation = "support metrics look consistent"
    if state == "no_data":
        interpretation = "no support metrics available in this history"
    elif state == "warning":
        interpretation = "support metrics contain incoherent values"
    elif state == "incomplete":
        interpretation = "support metrics are partial but still readable"

    ordered_warnings = list(dict.fromkeys(warnings))
    return {
        "state": state,
        "warnings": ordered_warnings,
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
    support_gate_cooldown_values = [
        _as_float(record.get("support_gate_run_cooldown_blocked"))
        for record in support_gate_records
    ]
    support_gate_unavailable_values = [
        _as_float(record.get("support_gate_run_unavailable"))
        for record in support_gate_records
    ]
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
    support_metrics_quality = _build_support_metrics_quality(
        support_gate_records=support_gate_records,
        champion_support_records=champion_support_records,
        support_gate_attempt_values=attempts_values,
        support_gate_success_values=success_values,
        support_gate_success_rate_values=success_rate_values,
        support_gate_cooldown_values=support_gate_cooldown_values,
        support_gate_unavailable_values=support_gate_unavailable_values,
        support_gate_completed=support_gate_completed,
        support_gate_failed=support_gate_failed,
        champion_attempt_values=champion_attempt_values,
        champion_success_values=champion_success_values,
        champion_success_rate_values=champion_success_rate_values,
        champion_cooldown_values=champion_cooldown_total_values,
        champion_unavailable_values=champion_unavailable_total_values,
        champion_completed=champion_completed,
        champion_failed=champion_failed,
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
        "support_metrics_quality": support_metrics_quality,
    }
    summary["recommendations"] = build_support_gate_recommendations(summary)
    summary["support_metrics_regression"] = build_support_metrics_regression(
        None,
        summary,
        baseline_label="n/a",
        current_label="current",
    )
    summary["support_metrics_ci_check"] = build_support_metrics_ci_check(
        summary["support_metrics_regression"],
        enabled=False,
        fail_on_regression=False,
        max_warning_delta=0,
        max_support_gate_success_rate_drop=0.05,
        max_rally_champion_success_rate_drop=0.05,
    )
    summary["support_metrics_final_decision"] = build_support_metrics_final_decision(summary)
    summary["final_decision"] = build_final_decision(summary)
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


def _extract_support_metrics_regression_inputs(summary: dict[str, Any]) -> dict[str, Any] | None:
    support_gate = summary.get("support_gate")
    champion_support = summary.get("champion_support")
    support_systems_summary = summary.get("support_systems_summary")
    support_metrics_quality = summary.get("support_metrics_quality")

    if not isinstance(support_gate, dict):
        return None
    if not isinstance(champion_support, dict):
        return None
    if not isinstance(support_systems_summary, dict):
        return None
    if not isinstance(support_metrics_quality, dict):
        return None

    champion_multi_run = champion_support.get("multi_run_comparison")
    if not isinstance(champion_multi_run, dict):
        return None

    quality_state = str(support_metrics_quality.get("state", "")).strip()
    support_interpretation = str(support_systems_summary.get("interpretation", "")).strip()
    champion_interpretation = str(champion_multi_run.get("global_interpretation", "")).strip()
    quality_warnings = support_metrics_quality.get("warnings")

    if quality_state == "" or support_interpretation == "" or champion_interpretation == "":
        return None
    if not isinstance(quality_warnings, list):
        return None

    return {
        "support_gate_success_rate": _as_float(support_gate.get("avg_support_gate_run_success_rate")),
        "rally_champion_success_rate": _as_float(
            champion_support.get("avg_champion_support_run_success_rate")
        ),
        "quality_state": quality_state,
        "support_systems_interpretation": support_interpretation,
        "champion_multi_run_interpretation": champion_interpretation,
        "warning_count": len(quality_warnings),
    }


def build_support_metrics_regression(
    baseline_summary: dict[str, Any] | None,
    current_summary: dict[str, Any],
    baseline_label: str = "baseline",
    current_label: str = "current",
) -> dict[str, Any]:
    regression = {
        "compared": False,
        "baseline_label": baseline_label,
        "current_label": current_label,
        "changed_fields": [],
        "warning_count_delta": None,
        "quality_state_changed": False,
        "support_gate_success_rate_delta": None,
        "rally_champion_success_rate_delta": None,
        "interpretation_changed": False,
        "regression_state": "no_baseline",
        "interpretation": "no baseline summary provided; regression comparison skipped",
    }
    if baseline_summary is None:
        return regression

    baseline_inputs = _extract_support_metrics_regression_inputs(baseline_summary)
    current_inputs = _extract_support_metrics_regression_inputs(current_summary)
    if baseline_inputs is None or current_inputs is None:
        regression["regression_state"] = "incompatible"
        regression["interpretation"] = "baseline/current summaries are incompatible for regression comparison"
        return regression

    changed_fields: list[str] = []
    warning_count_delta = int(current_inputs["warning_count"]) - int(baseline_inputs["warning_count"])

    support_gate_success_rate_delta: float | None = None
    baseline_support_gate_rate = _as_float(baseline_inputs.get("support_gate_success_rate"))
    current_support_gate_rate = _as_float(current_inputs.get("support_gate_success_rate"))
    if baseline_support_gate_rate is not None and current_support_gate_rate is not None:
        support_gate_success_rate_delta = float(current_support_gate_rate - baseline_support_gate_rate)
        if abs(support_gate_success_rate_delta) > 1e-9:
            changed_fields.append("support_gate.avg_support_gate_run_success_rate")

    rally_champion_success_rate_delta: float | None = None
    baseline_champion_rate = _as_float(baseline_inputs.get("rally_champion_success_rate"))
    current_champion_rate = _as_float(current_inputs.get("rally_champion_success_rate"))
    if baseline_champion_rate is not None and current_champion_rate is not None:
        rally_champion_success_rate_delta = float(current_champion_rate - baseline_champion_rate)
        if abs(rally_champion_success_rate_delta) > 1e-9:
            changed_fields.append("champion_support.avg_champion_support_run_success_rate")

    baseline_quality_state = str(baseline_inputs.get("quality_state", ""))
    current_quality_state = str(current_inputs.get("quality_state", ""))
    quality_state_changed = baseline_quality_state != current_quality_state
    if quality_state_changed:
        changed_fields.append("support_metrics_quality.state")

    baseline_support_interpretation = str(baseline_inputs.get("support_systems_interpretation", ""))
    current_support_interpretation = str(current_inputs.get("support_systems_interpretation", ""))
    if baseline_support_interpretation != current_support_interpretation:
        changed_fields.append("support_systems_summary.interpretation")

    baseline_champion_interpretation = str(baseline_inputs.get("champion_multi_run_interpretation", ""))
    current_champion_interpretation = str(current_inputs.get("champion_multi_run_interpretation", ""))
    champion_interpretation_changed = baseline_champion_interpretation != current_champion_interpretation
    if champion_interpretation_changed:
        changed_fields.append("champion_support.multi_run_comparison.global_interpretation")

    if warning_count_delta != 0:
        changed_fields.append("support_metrics_quality.warning_count")

    interpretation_changed = (
        baseline_support_interpretation != current_support_interpretation
        or champion_interpretation_changed
    )
    regression_state = "stable"
    interpretation = "support metrics are stable compared to baseline"
    if quality_state_changed or warning_count_delta > 0:
        regression_state = "warning"
        interpretation = "support metrics changed with quality degradation signals"
    elif changed_fields:
        regression_state = "changed"
        interpretation = "support metrics changed compared to baseline"

    regression["compared"] = True
    regression["changed_fields"] = list(dict.fromkeys(changed_fields))
    regression["warning_count_delta"] = warning_count_delta
    regression["quality_state_changed"] = quality_state_changed
    regression["support_gate_success_rate_delta"] = support_gate_success_rate_delta
    regression["rally_champion_success_rate_delta"] = rally_champion_success_rate_delta
    regression["interpretation_changed"] = interpretation_changed
    regression["regression_state"] = regression_state
    regression["interpretation"] = interpretation
    return regression


def build_support_metrics_ci_check(
    regression: dict[str, Any] | None,
    enabled: bool,
    fail_on_regression: bool,
    max_warning_delta: int,
    max_support_gate_success_rate_drop: float,
    max_rally_champion_success_rate_drop: float,
) -> dict[str, Any]:
    ci_check = {
        "enabled": enabled,
        "passed": None,
        "fail_on_regression": bool(fail_on_regression),
        "thresholds": {
            "max_warning_delta": int(max_warning_delta),
            "max_support_gate_success_rate_drop": float(max_support_gate_success_rate_drop),
            "max_rally_champion_success_rate_drop": float(max_rally_champion_success_rate_drop),
        },
        "triggered_rules": [],
        "exit_code": 0,
        "interpretation": "CI check disabled",
    }
    if not enabled:
        return ci_check

    if not isinstance(regression, dict):
        ci_check["passed"] = False
        ci_check["triggered_rules"] = ["regression_block_missing"]
        ci_check["interpretation"] = "support metrics regression block is missing"
        if fail_on_regression:
            ci_check["exit_code"] = 1
        return ci_check

    regression_state = str(regression.get("regression_state", "")).strip().lower()
    if regression_state == "no_baseline":
        ci_check["passed"] = None
        ci_check["interpretation"] = "baseline not provided; CI regression check skipped"
        return ci_check

    triggered_rules: list[str] = []
    if regression_state == "warning":
        triggered_rules.append("regression_state_warning")
    elif regression_state == "incompatible":
        triggered_rules.append("regression_state_incompatible")

    warning_delta = _as_float(regression.get("warning_count_delta"))
    if warning_delta is not None and warning_delta > float(max_warning_delta):
        triggered_rules.append("warning_count_delta_exceeded")

    support_gate_success_rate_delta = _as_float(regression.get("support_gate_success_rate_delta"))
    if (
        support_gate_success_rate_delta is not None
        and support_gate_success_rate_delta < -float(max_support_gate_success_rate_drop)
    ):
        triggered_rules.append("support_gate_success_rate_drop_exceeded")

    rally_champion_success_rate_delta = _as_float(
        regression.get("rally_champion_success_rate_delta")
    )
    if (
        rally_champion_success_rate_delta is not None
        and rally_champion_success_rate_delta < -float(max_rally_champion_success_rate_drop)
    ):
        triggered_rules.append("rally_champion_success_rate_drop_exceeded")

    ci_check["triggered_rules"] = triggered_rules
    ci_check["passed"] = len(triggered_rules) == 0
    if ci_check["passed"]:
        ci_check["interpretation"] = "support metrics CI check passed"
    else:
        ci_check["interpretation"] = "support metrics CI check detected regression signals"
        if fail_on_regression:
            ci_check["exit_code"] = 1
    return ci_check


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


def _build_legacy_final_decision(summary: dict[str, Any]) -> str:
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


def _build_support_metrics_data_state(summary: dict[str, Any]) -> str:
    support_systems_summary = summary.get("support_systems_summary", {})
    if isinstance(support_systems_summary, dict):
        data_state = str(support_systems_summary.get("data_state", "")).strip().lower()
        if data_state in {"complete", "partial", "no_data"}:
            return data_state

    support_metrics_quality = summary.get("support_metrics_quality", {})
    if isinstance(support_metrics_quality, dict):
        quality_state = str(support_metrics_quality.get("state", "")).strip().lower()
        if quality_state == "no_data":
            return "no_data"
        if quality_state in {"incomplete", "warning"}:
            return "partial"
        if quality_state == "valid":
            return "complete"
    return "partial"


def _is_strong_regression_warning(regression: dict[str, Any]) -> bool:
    regression_state = str(regression.get("regression_state", "")).strip().lower()
    if regression_state != "warning":
        return False
    if bool(regression.get("quality_state_changed", False)):
        return True

    warning_delta = _as_float(regression.get("warning_count_delta"))
    if warning_delta is not None and warning_delta > 0.0:
        return True

    support_gate_drop = _as_float(regression.get("support_gate_success_rate_delta"))
    if support_gate_drop is not None and support_gate_drop <= COMPARISON_STRONG_DROP_THRESHOLD:
        return True

    champion_drop = _as_float(regression.get("rally_champion_success_rate_delta"))
    if champion_drop is not None and champion_drop <= COMPARISON_STRONG_DROP_THRESHOLD:
        return True
    return False


def build_support_metrics_final_decision(summary: dict[str, Any]) -> dict[str, Any]:
    support_gate = summary.get("support_gate", {})
    champion_support = summary.get("champion_support", {})
    support_metrics_quality = summary.get("support_metrics_quality", {})
    support_metrics_regression = summary.get("support_metrics_regression", {})
    support_metrics_ci_check = summary.get("support_metrics_ci_check", {})

    support_gate_records = int(support_gate.get("records", 0)) if isinstance(support_gate, dict) else 0
    champion_records = int(champion_support.get("records", 0)) if isinstance(champion_support, dict) else 0
    quality_state = (
        str(support_metrics_quality.get("state", "")).strip().lower()
        if isinstance(support_metrics_quality, dict)
        else ""
    )
    regression_state = (
        str(support_metrics_regression.get("regression_state", "")).strip().lower()
        if isinstance(support_metrics_regression, dict)
        else ""
    )
    ci_enabled = bool(support_metrics_ci_check.get("enabled", False)) if isinstance(support_metrics_ci_check, dict) else False
    ci_passed = support_metrics_ci_check.get("passed") if isinstance(support_metrics_ci_check, dict) else None

    data_state = _build_support_metrics_data_state(summary)
    reasons: list[str] = []
    decision = "collect_more_runs_before_deciding"
    confidence = "low"

    if data_state == "no_data":
        decision = "no_runtime_data"
        confidence = "n/a"
        reasons.append("support_metrics_data_state_no_data")
        if ci_enabled and ci_passed is None:
            reasons.append("ci_check_skipped")
    elif regression_state == "incompatible":
        decision = "collect_more_runs_before_deciding"
        confidence = "low"
        reasons.append("regression_incompatible")
    elif (
        isinstance(support_metrics_regression, dict)
        and data_state == "complete"
        and _is_strong_regression_warning(support_metrics_regression)
    ):
        decision = "reject_candidate_or_revert"
        confidence = "high"
        reasons.append("strong_regression_warning")
    elif quality_state == "warning":
        decision = "review_tradeoff_before_tuning"
        confidence = "medium"
        reasons.append("quality_warning")
    elif data_state == "partial" or quality_state == "incomplete":
        if support_gate_records <= 0:
            decision = "collect_support_gate_runs_first"
            reasons.append("support_gate_data_missing")
        else:
            decision = "collect_more_runs_before_deciding"
            reasons.append("partial_support_metrics_data")
        confidence = "low"
    elif regression_state == "no_baseline":
        decision = "collect_more_runs_before_deciding"
        confidence = "low"
        reasons.append("regression_no_baseline")
    elif regression_state == "warning":
        decision = "review_tradeoff_before_tuning"
        confidence = "medium"
        reasons.append("regression_warning")
    elif regression_state == "changed":
        decision = "review_tradeoff_before_tuning"
        confidence = "medium"
        reasons.append("regression_changed")
    elif regression_state == "stable" and data_state == "complete":
        decision = "keep_candidate_for_more_testing"
        confidence = "medium"
        reasons.append("stable_complete_data")
        if support_gate_records >= 10 and champion_records >= 10:
            confidence = "high"
            reasons.append("high_run_volume")
    else:
        decision = "collect_more_runs_before_deciding"
        confidence = "low"
        reasons.append("insufficient_decision_signals")

    if regression_state == "no_baseline":
        reasons.append("baseline_not_provided")
    if ci_enabled and ci_passed is None:
        reasons.append("ci_check_non_blocking_without_baseline")

    return {
        "decision": decision,
        "confidence": confidence,
        "reasons": list(dict.fromkeys(reasons)),
        "data_state": data_state,
        "is_blocking_decision": False,
    }


def build_final_decision(summary: dict[str, Any]) -> str:
    final_block = summary.get("support_metrics_final_decision")
    if isinstance(final_block, dict):
        decision = str(final_block.get("decision", "")).strip()
        mapped = FINAL_DECISION_TEXT_BY_CODE.get(decision)
        if mapped is not None:
            return mapped
    return _build_legacy_final_decision(summary)


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
    support_metrics_quality = summary.get("support_metrics_quality", {})
    support_metrics_regression = summary.get("support_metrics_regression", {})
    support_metrics_ci_check = summary.get("support_metrics_ci_check", {})
    support_metrics_final_decision = summary.get("support_metrics_final_decision", {})
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
    quality_warnings = support_metrics_quality.get("warnings", [])
    quality_warnings_label = "none"
    if isinstance(quality_warnings, list) and quality_warnings:
        quality_warnings_label = ", ".join(str(item) for item in quality_warnings)
    lines.append("Support metrics quality:")
    lines.append("- state: %s" % str(support_metrics_quality.get("state", "no_data")))
    lines.append("- warnings: %s" % quality_warnings_label)
    lines.append("- interpretation: %s" % str(support_metrics_quality.get("interpretation", "no_data")))
    regression_changed_fields = support_metrics_regression.get("changed_fields", [])
    regression_changed_fields_label = "none"
    if isinstance(regression_changed_fields, list) and regression_changed_fields:
        regression_changed_fields_label = ", ".join(str(item) for item in regression_changed_fields)
    regression_warning_delta = support_metrics_regression.get("warning_count_delta")
    regression_warning_delta_label = "n/a"
    if isinstance(regression_warning_delta, int):
        regression_warning_delta_label = f"{regression_warning_delta:+d}"
    lines.append("Support metrics regression:")
    lines.append("- state: %s" % str(support_metrics_regression.get("regression_state", "no_baseline")))
    lines.append("- changed fields: %s" % regression_changed_fields_label)
    lines.append("- warning delta: %s" % regression_warning_delta_label)
    lines.append("- interpretation: %s" % str(support_metrics_regression.get("interpretation", "no baseline summary provided; regression comparison skipped")))
    ci_enabled = bool(support_metrics_ci_check.get("enabled", False))
    if ci_enabled:
        ci_passed = support_metrics_ci_check.get("passed")
        ci_passed_label = "n/a" if ci_passed is None else ("true" if bool(ci_passed) else "false")
        ci_triggered_rules = support_metrics_ci_check.get("triggered_rules", [])
        ci_triggered_rules_label = "none"
        if isinstance(ci_triggered_rules, list) and ci_triggered_rules:
            ci_triggered_rules_label = ", ".join(str(item) for item in ci_triggered_rules)
        lines.append("Support metrics CI check:")
        lines.append("- enabled: true")
        lines.append("- passed: %s" % ci_passed_label)
        lines.append("- triggered rules: %s" % ci_triggered_rules_label)
        lines.append("- interpretation: %s" % str(support_metrics_ci_check.get("interpretation", "support metrics CI check executed")))
    lines.append("Recommendations:")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")
    final_decision_reasons = []
    if isinstance(support_metrics_final_decision, dict):
        reasons_value = support_metrics_final_decision.get("reasons", [])
        if isinstance(reasons_value, list):
            final_decision_reasons = [str(item) for item in reasons_value if str(item).strip() != ""]
    if isinstance(support_metrics_final_decision, dict) and support_metrics_final_decision:
        decision_code = str(
            support_metrics_final_decision.get("decision", "")
        ).strip() or "collect_more_runs_before_deciding"
        confidence_label = str(
            support_metrics_final_decision.get("confidence", "")
        ).strip() or "n/a"
        reasons_label = ", ".join(final_decision_reasons) if final_decision_reasons else "none"
        blocking_label = "yes" if bool(support_metrics_final_decision.get("is_blocking_decision", False)) else "no"
        lines.append("Final decision:")
        lines.append("- decision: %s" % decision_code)
        lines.append("- confidence: %s" % confidence_label)
        lines.append("- reasons: %s" % reasons_label)
        lines.append("- blocking: %s" % blocking_label)
        lines.append("- note: heuristic quick-read only (not statistical proof).")
    elif final_decision:
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
    support_metrics_quality = summary.get("support_metrics_quality", {})
    support_metrics_regression = summary.get("support_metrics_regression", {})
    support_metrics_ci_check = summary.get("support_metrics_ci_check", {})
    support_metrics_final_decision = summary.get("support_metrics_final_decision", {})
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
    quality_warnings = support_metrics_quality.get("warnings", [])
    quality_warnings_label = "none"
    if isinstance(quality_warnings, list) and quality_warnings:
        quality_warnings_label = ", ".join(str(item) for item in quality_warnings)
    lines.append("")
    lines.append("### Support metrics quality")
    lines.append("- state: %s" % str(support_metrics_quality.get("state", "no_data")))
    lines.append("- warnings: %s" % quality_warnings_label)
    lines.append("- interpretation: %s" % str(support_metrics_quality.get("interpretation", "no_data")))
    regression_changed_fields = support_metrics_regression.get("changed_fields", [])
    regression_changed_fields_label = "none"
    if isinstance(regression_changed_fields, list) and regression_changed_fields:
        regression_changed_fields_label = ", ".join(str(item) for item in regression_changed_fields)
    regression_warning_delta = support_metrics_regression.get("warning_count_delta")
    regression_warning_delta_label = "n/a"
    if isinstance(regression_warning_delta, int):
        regression_warning_delta_label = f"{regression_warning_delta:+d}"
    lines.append("")
    lines.append("### Support metrics regression")
    lines.append("- state: %s" % str(support_metrics_regression.get("regression_state", "no_baseline")))
    lines.append("- changed fields: %s" % regression_changed_fields_label)
    lines.append("- warning delta: %s" % regression_warning_delta_label)
    lines.append("- interpretation: %s" % str(support_metrics_regression.get("interpretation", "no baseline summary provided; regression comparison skipped")))
    ci_enabled = bool(support_metrics_ci_check.get("enabled", False))
    if ci_enabled:
        ci_passed = support_metrics_ci_check.get("passed")
        ci_passed_label = "n/a" if ci_passed is None else ("true" if bool(ci_passed) else "false")
        ci_triggered_rules = support_metrics_ci_check.get("triggered_rules", [])
        ci_triggered_rules_label = "none"
        if isinstance(ci_triggered_rules, list) and ci_triggered_rules:
            ci_triggered_rules_label = ", ".join(str(item) for item in ci_triggered_rules)
        lines.append("")
        lines.append("### Support metrics CI check")
        lines.append("- enabled: true")
        lines.append("- passed: %s" % ci_passed_label)
        lines.append("- triggered rules: %s" % ci_triggered_rules_label)
        lines.append("- interpretation: %s" % str(support_metrics_ci_check.get("interpretation", "support metrics CI check executed")))

    lines.append("")
    lines.append("## Recommendations")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            lines.append("- %s" % str(recommendation))
    else:
        lines.append("- Support gate tuning looks stable.")
    final_decision_reasons = []
    if isinstance(support_metrics_final_decision, dict):
        reasons_value = support_metrics_final_decision.get("reasons", [])
        if isinstance(reasons_value, list):
            final_decision_reasons = [str(item) for item in reasons_value if str(item).strip() != ""]
    if isinstance(support_metrics_final_decision, dict) and support_metrics_final_decision:
        decision_code = str(
            support_metrics_final_decision.get("decision", "")
        ).strip() or "collect_more_runs_before_deciding"
        confidence_label = str(
            support_metrics_final_decision.get("confidence", "")
        ).strip() or "n/a"
        reasons_label = ", ".join(final_decision_reasons) if final_decision_reasons else "none"
        blocking_label = "yes" if bool(support_metrics_final_decision.get("is_blocking_decision", False)) else "no"
        lines.append("")
        lines.append("## Final decision")
        lines.append("- decision: %s" % decision_code)
        lines.append("- confidence: %s" % confidence_label)
        lines.append("- reasons: %s" % reasons_label)
        lines.append("- blocking: %s" % blocking_label)
        lines.append("- note: heuristic quick-read only (not statistical proof).")
    elif final_decision:
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
    parser.add_argument(
        "--ci-check",
        action="store_true",
        help="Enable support metrics regression CI check.",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Return non-zero exit code if CI check detects regression signals.",
    )
    parser.add_argument(
        "--max-warning-delta",
        type=int,
        default=0,
        help="Maximum allowed increase of support metrics quality warnings.",
    )
    parser.add_argument(
        "--max-support-gate-success-rate-drop",
        type=float,
        default=0.05,
        help="Maximum allowed drop on support_gate average success rate (0..1 scale).",
    )
    parser.add_argument(
        "--max-rally-champion-success-rate-drop",
        type=float,
        default=0.05,
        help="Maximum allowed drop on rally_champion average success rate (0..1 scale).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path: Path = args.input
    objective = args.objective.strip()
    limit = int(args.limit)
    ci_check_enabled = bool(args.ci_check or args.fail_on_regression)
    fail_on_regression = bool(args.fail_on_regression)
    max_warning_delta = int(args.max_warning_delta)
    max_support_gate_success_rate_drop = float(args.max_support_gate_success_rate_drop)
    max_rally_champion_success_rate_drop = float(args.max_rally_champion_success_rate_drop)

    if limit < 0:
        print("ERROR: --limit must be >= 0")
        return 1
    if max_warning_delta < 0:
        print("ERROR: --max-warning-delta must be >= 0")
        return 1
    if max_support_gate_success_rate_drop < 0.0:
        print("ERROR: --max-support-gate-success-rate-drop must be >= 0")
        return 1
    if max_rally_champion_success_rate_drop < 0.0:
        print("ERROR: --max-rally-champion-success-rate-drop must be >= 0")
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
    summary["support_metrics_regression"] = build_support_metrics_regression(
        None,
        summary,
        baseline_label="n/a",
        current_label=input_path.name,
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
        summary["support_metrics_regression"] = build_support_metrics_regression(
            summary,
            candidate_summary,
            baseline_label=input_path.name,
            current_label=compare_input_path.name,
        )
    summary["support_metrics_ci_check"] = build_support_metrics_ci_check(
        summary.get("support_metrics_regression"),
        enabled=ci_check_enabled,
        fail_on_regression=fail_on_regression,
        max_warning_delta=max_warning_delta,
        max_support_gate_success_rate_drop=max_support_gate_success_rate_drop,
        max_rally_champion_success_rate_drop=max_rally_champion_success_rate_drop,
    )
    summary["support_metrics_final_decision"] = build_support_metrics_final_decision(summary)
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
    ci_exit_code = int(summary.get("support_metrics_ci_check", {}).get("exit_code", 0))
    return ci_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
