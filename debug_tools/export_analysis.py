from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict

from debug_tools.batch_comparative import (
    build_batch_comparative_summary,
    format_batch_comparative_summary,
)
from ui import format_final_run_summary, format_multi_run_summary


def load_export_payload(input_path: str, input_format: str = "auto") -> Dict[str, object]:
    path = Path(input_path)
    if not path.exists():
        raise ValueError(f"input file does not exist: {path}")

    selected_format = _resolve_input_format(path, input_format)

    if selected_format == "json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("json payload must be an object")
        return data

    if selected_format == "csv":
        return _load_csv_payload(path)

    raise ValueError("input_format must be auto, json or csv")


def summarize_export_payload(payload: Dict[str, object]) -> str:
    mode = str(payload.get("mode", "unknown"))

    if mode == "single":
        seed = int(payload.get("seed", 0))
        extinct = "yes" if bool(payload.get("extinct", False)) else "no"
        max_gen = int(payload.get("max_generation", 0))
        final_alive = int(payload.get("final_alive", 0))
        run_summary = payload.get("run_summary")

        lines = [
            "=== Export Analysis (single) ===",
            f"seed={seed} extinct={extinct} max_gen={max_gen} alive_final={final_alive}",
        ]

        if isinstance(run_summary, dict):
            lines.append(format_final_run_summary(run_summary))
        else:
            lines.append("synthese_run: n/a")

        return "\n".join(lines)

    if mode == "multi":
        seeds = _read_seed_list(payload.get("seeds"))
        run_count = int(payload.get("run_count", len(seeds)))
        multi_summary = payload.get("multi_run_summary")

        lines = [
            "=== Export Analysis (multi) ===",
            f"runs={run_count} seeds=" + ",".join(str(seed) for seed in seeds),
        ]

        if isinstance(multi_summary, dict):
            lines.append(format_multi_run_summary(multi_summary))
        else:
            lines.append("multi_runs: n/a")

        return "\n".join(lines)

    if mode == "batch":
        batch_param = str(payload.get("batch_param", "?"))
        batch_values = _read_float_list(payload.get("batch_values"))
        runs_per_value = int(payload.get("runs_per_value", 0))
        scenarios_raw = payload.get("scenarios")

        lines = [
            "=== Export Analysis (batch) ===",
            "param={param} values={values} runs_per_value={runs}".format(
                param=batch_param,
                values=",".join(_format_batch_value(value) for value in batch_values),
                runs=runs_per_value,
            ),
        ]

        if isinstance(scenarios_raw, list):
            for scenario_raw in scenarios_raw:
                if not isinstance(scenario_raw, dict):
                    continue
                value = float(scenario_raw.get("parameter_value", 0.0))
                summary_raw = scenario_raw.get("multi_run_summary")
                if isinstance(summary_raw, dict):
                    lines.append(
                        "{param}={value} -> {summary}".format(
                            param=batch_param,
                            value=_format_batch_value(value),
                            summary=format_multi_run_summary(summary_raw),
                        )
                    )
                else:
                    lines.append(f"{batch_param}={_format_batch_value(value)} -> n/a")

        comparative_raw = payload.get("comparative_summary")
        if isinstance(comparative_raw, dict):
            comparative = comparative_raw
        else:
            comparative = build_batch_comparative_summary(
                batch_param=batch_param,
                scenarios=scenarios_raw if isinstance(scenarios_raw, list) else [],
            )

        lines.append("--- Batch Comparative Summary ---")
        lines.append(format_batch_comparative_summary(comparative))

        return "\n".join(lines)

    return "=== Export Analysis ===\nmode non supporte"


def _resolve_input_format(path: Path, input_format: str) -> str:
    if input_format == "auto":
        suffix = path.suffix.lower()
        if suffix == ".json":
            return "json"
        if suffix == ".csv":
            return "csv"
        raise ValueError("cannot infer format from extension, use --format json|csv")

    if input_format in ("json", "csv"):
        return input_format

    raise ValueError("input_format must be auto, json or csv")


def _load_csv_payload(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        rows = list(reader)

    if len(rows) == 0:
        raise ValueError("csv export is empty")

    batch_aggregate_row = _find_row_by_type(rows, "batch_aggregate")
    if batch_aggregate_row is not None:
        return _build_batch_payload_from_csv(rows, batch_aggregate_row)

    aggregate_row = _find_row_by_type(rows, "aggregate")
    if aggregate_row is not None:
        return _build_multi_payload_from_csv(aggregate_row)

    single_row = _find_row_by_type(rows, "single")
    if single_row is None:
        single_row = rows[0]
    return _build_single_payload_from_csv(single_row)


def _find_row_by_type(rows: list[Dict[str, str]], row_type: str) -> Dict[str, str] | None:
    for row in rows:
        if str(row.get("row_type", "")).strip() == row_type:
            return row
    return None


def _find_rows_by_type(rows: list[Dict[str, str]], row_type: str) -> list[Dict[str, str]]:
    return [row for row in rows if str(row.get("row_type", "")).strip() == row_type]


def _build_single_payload_from_csv(row: Dict[str, str]) -> Dict[str, object]:
    run_summary = {
        "final_dominant_group_signature": row.get("run_summary.final_dominant_group_signature", "-"),
        "final_dominant_group_share": _parse_float(row.get("run_summary.final_dominant_group_share")),
        "most_stable_group_signature": row.get("run_summary.most_stable_group_signature", "-"),
        "most_stable_group_count": _parse_int(row.get("run_summary.most_stable_group_count")),
        "most_rising_group_signature": row.get("run_summary.most_rising_group_signature", "-"),
        "most_rising_group_count": _parse_int(row.get("run_summary.most_rising_group_count")),
        "final_zone_distribution": {
            "rich": _parse_int(row.get("run_summary.final_zone_distribution.rich")),
            "neutral": _parse_int(row.get("run_summary.final_zone_distribution.neutral")),
            "poor": _parse_int(row.get("run_summary.final_zone_distribution.poor")),
        },
        "avg_traits": {
            "speed": _parse_float(row.get("run_summary.avg_traits.speed")),
            "metabolism": _parse_float(row.get("run_summary.avg_traits.metabolism")),
            "prudence": _parse_float(row.get("run_summary.avg_traits.prudence")),
            "dominance": _parse_float(row.get("run_summary.avg_traits.dominance")),
            "repro_drive": _parse_float(row.get("run_summary.avg_traits.repro_drive")),
            "food_perception": _parse_float(row.get("run_summary.avg_traits.food_perception")),
            "threat_perception": _parse_float(row.get("run_summary.avg_traits.threat_perception")),
            "energy_efficiency": _parse_float(row.get("run_summary.avg_traits.energy_efficiency")),
            "exhaustion_resistance": _parse_float(row.get("run_summary.avg_traits.exhaustion_resistance")),
        },
        "memory_impact": {
            "food_usage_total": _parse_int(row.get("run_summary.memory_impact.food_usage_total")),
            "danger_usage_total": _parse_int(row.get("run_summary.memory_impact.danger_usage_total")),
            "food_active_share": _parse_float(row.get("run_summary.memory_impact.food_active_share")),
            "danger_active_share": _parse_float(row.get("run_summary.memory_impact.danger_active_share")),
            "food_effect_avg_distance": _parse_float(row.get("run_summary.memory_impact.food_effect_avg_distance")),
            "danger_effect_avg_distance": _parse_float(row.get("run_summary.memory_impact.danger_effect_avg_distance")),
            "food_usage_per_tick": _parse_float(row.get("run_summary.memory_impact.food_usage_per_tick")),
            "danger_usage_per_tick": _parse_float(row.get("run_summary.memory_impact.danger_usage_per_tick")),
        },
        "social_impact": {
            "follow_usage_total": _parse_float(row.get("run_summary.social_impact.follow_usage_total")),
            "flee_boost_usage_total": _parse_float(row.get("run_summary.social_impact.flee_boost_usage_total")),
            "influenced_count_last_tick": _parse_float(row.get("run_summary.social_impact.influenced_count_last_tick")),
            "influenced_share_last_tick": _parse_float(row.get("run_summary.social_impact.influenced_share_last_tick")),
            "influenced_per_tick": _parse_float(row.get("run_summary.social_impact.influenced_per_tick")),
            "follow_usage_per_tick": _parse_float(row.get("run_summary.social_impact.follow_usage_per_tick")),
            "flee_boost_usage_per_tick": _parse_float(row.get("run_summary.social_impact.flee_boost_usage_per_tick")),
            "flee_multiplier_avg_tick": _parse_float(row.get("run_summary.social_impact.flee_multiplier_avg_tick"), default=1.0),
            "flee_multiplier_avg_total": _parse_float(row.get("run_summary.social_impact.flee_multiplier_avg_total"), default=1.0),
        },
        "trait_impact": {
            "memory_focus_mean": _parse_float(row.get("run_summary.trait_impact.memory_focus_mean")),
            "memory_focus_std": _parse_float(row.get("run_summary.trait_impact.memory_focus_std")),
            "social_sensitivity_mean": _parse_float(row.get("run_summary.trait_impact.social_sensitivity_mean")),
            "social_sensitivity_std": _parse_float(row.get("run_summary.trait_impact.social_sensitivity_std")),
            "food_perception_mean": _parse_float(row.get("run_summary.trait_impact.food_perception_mean")),
            "food_perception_std": _parse_float(row.get("run_summary.trait_impact.food_perception_std")),
            "threat_perception_mean": _parse_float(row.get("run_summary.trait_impact.threat_perception_mean")),
            "threat_perception_std": _parse_float(row.get("run_summary.trait_impact.threat_perception_std")),
            "energy_efficiency_mean": _parse_float(row.get("run_summary.trait_impact.energy_efficiency_mean")),
            "energy_efficiency_std": _parse_float(row.get("run_summary.trait_impact.energy_efficiency_std")),
            "exhaustion_resistance_mean": _parse_float(row.get("run_summary.trait_impact.exhaustion_resistance_mean")),
            "exhaustion_resistance_std": _parse_float(row.get("run_summary.trait_impact.exhaustion_resistance_std")),
            "memory_focus_food_bias": _parse_float(row.get("run_summary.trait_impact.memory_focus_food_bias")),
            "memory_focus_danger_bias": _parse_float(row.get("run_summary.trait_impact.memory_focus_danger_bias")),
            "social_sensitivity_follow_bias": _parse_float(row.get("run_summary.trait_impact.social_sensitivity_follow_bias")),
            "social_sensitivity_flee_boost_bias": _parse_float(row.get("run_summary.trait_impact.social_sensitivity_flee_boost_bias")),
            "food_perception_detection_bias": _parse_float(row.get("run_summary.trait_impact.food_perception_detection_bias")),
            "food_perception_consumption_bias": _parse_float(row.get("run_summary.trait_impact.food_perception_consumption_bias")),
            "threat_perception_flee_bias": _parse_float(row.get("run_summary.trait_impact.threat_perception_flee_bias")),
        },
        "observed_logs": _parse_int(row.get("run_summary.observed_logs")),
    }

    return {
        "mode": "single",
        "seed": _parse_int(row.get("seed")),
        "extinct": _parse_bool(row.get("extinct")),
        "max_generation": _parse_int(row.get("max_generation")),
        "final_alive": _parse_int(row.get("final_alive")),
        "run_summary": run_summary,
    }


def _build_multi_payload_from_csv(row: Dict[str, str]) -> Dict[str, object]:
    seeds = _read_seed_list(row.get("seeds") or row.get("multi_run_summary.seeds"))

    multi_summary = {
        "runs": _parse_int(row.get("multi_run_summary.runs")),
        "seeds": _read_seed_list(row.get("multi_run_summary.seeds")),
        "extinction_count": _parse_int(row.get("multi_run_summary.extinction_count")),
        "extinction_rate": _parse_float(row.get("multi_run_summary.extinction_rate")),
        "avg_max_generation": _parse_float(row.get("multi_run_summary.avg_max_generation")),
        "avg_final_population": _parse_float(row.get("multi_run_summary.avg_final_population")),
        "avg_final_traits": {
            "speed": _parse_float(row.get("multi_run_summary.avg_final_traits.speed")),
            "metabolism": _parse_float(row.get("multi_run_summary.avg_final_traits.metabolism")),
            "prudence": _parse_float(row.get("multi_run_summary.avg_final_traits.prudence")),
            "dominance": _parse_float(row.get("multi_run_summary.avg_final_traits.dominance")),
            "repro_drive": _parse_float(row.get("multi_run_summary.avg_final_traits.repro_drive")),
            "food_perception": _parse_float(row.get("multi_run_summary.avg_final_traits.food_perception")),
            "threat_perception": _parse_float(row.get("multi_run_summary.avg_final_traits.threat_perception")),
            "energy_efficiency": _parse_float(row.get("multi_run_summary.avg_final_traits.energy_efficiency")),
            "exhaustion_resistance": _parse_float(row.get("multi_run_summary.avg_final_traits.exhaustion_resistance")),
        },
        "most_frequent_final_dominant_group": row.get(
            "multi_run_summary.most_frequent_final_dominant_group",
            "-",
        ),
        "most_frequent_final_dominant_group_count": _parse_int(
            row.get("multi_run_summary.most_frequent_final_dominant_group_count")
        ),
        "most_frequent_final_dominant_group_share": _parse_float(
            row.get("multi_run_summary.most_frequent_final_dominant_group_share")
        ),
        "avg_memory_impact": {
            "food_usage_total": _parse_float(row.get("multi_run_summary.avg_memory_impact.food_usage_total")),
            "danger_usage_total": _parse_float(row.get("multi_run_summary.avg_memory_impact.danger_usage_total")),
            "food_active_share": _parse_float(row.get("multi_run_summary.avg_memory_impact.food_active_share")),
            "danger_active_share": _parse_float(row.get("multi_run_summary.avg_memory_impact.danger_active_share")),
            "food_effect_avg_distance": _parse_float(row.get("multi_run_summary.avg_memory_impact.food_effect_avg_distance")),
            "danger_effect_avg_distance": _parse_float(row.get("multi_run_summary.avg_memory_impact.danger_effect_avg_distance")),
            "food_usage_per_tick": _parse_float(row.get("multi_run_summary.avg_memory_impact.food_usage_per_tick")),
            "danger_usage_per_tick": _parse_float(row.get("multi_run_summary.avg_memory_impact.danger_usage_per_tick")),
        },
        "avg_social_impact": {
            "follow_usage_total": _parse_float(row.get("multi_run_summary.avg_social_impact.follow_usage_total")),
            "flee_boost_usage_total": _parse_float(row.get("multi_run_summary.avg_social_impact.flee_boost_usage_total")),
            "influenced_count_last_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.influenced_count_last_tick")),
            "influenced_share_last_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.influenced_share_last_tick")),
            "influenced_per_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.influenced_per_tick")),
            "follow_usage_per_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.follow_usage_per_tick")),
            "flee_boost_usage_per_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.flee_boost_usage_per_tick")),
            "flee_multiplier_avg_tick": _parse_float(row.get("multi_run_summary.avg_social_impact.flee_multiplier_avg_tick"), default=1.0),
            "flee_multiplier_avg_total": _parse_float(row.get("multi_run_summary.avg_social_impact.flee_multiplier_avg_total"), default=1.0),
        },
        "avg_trait_impact": {
            "memory_focus_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.memory_focus_mean")),
            "memory_focus_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.memory_focus_std")),
            "social_sensitivity_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.social_sensitivity_mean")),
            "social_sensitivity_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.social_sensitivity_std")),
            "food_perception_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.food_perception_mean")),
            "food_perception_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.food_perception_std")),
            "threat_perception_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.threat_perception_mean")),
            "threat_perception_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.threat_perception_std")),
            "energy_efficiency_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.energy_efficiency_mean")),
            "energy_efficiency_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.energy_efficiency_std")),
            "exhaustion_resistance_mean": _parse_float(row.get("multi_run_summary.avg_trait_impact.exhaustion_resistance_mean")),
            "exhaustion_resistance_std": _parse_float(row.get("multi_run_summary.avg_trait_impact.exhaustion_resistance_std")),
            "memory_focus_food_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.memory_focus_food_bias")),
            "memory_focus_danger_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.memory_focus_danger_bias")),
            "social_sensitivity_follow_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.social_sensitivity_follow_bias")),
            "social_sensitivity_flee_boost_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.social_sensitivity_flee_boost_bias")),
            "food_perception_detection_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.food_perception_detection_bias")),
            "food_perception_consumption_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.food_perception_consumption_bias")),
            "threat_perception_flee_bias": _parse_float(row.get("multi_run_summary.avg_trait_impact.threat_perception_flee_bias")),
        },
    }
    run_count = _parse_int(row.get("run_count"), default=multi_summary["runs"])

    return {
        "mode": "multi",
        "seeds": seeds,
        "run_count": run_count,
        "multi_run_summary": multi_summary,
    }


def _build_batch_payload_from_csv(
    rows: list[Dict[str, str]],
    aggregate_row: Dict[str, str],
) -> Dict[str, object]:
    scenarios: list[Dict[str, object]] = []

    for scenario_row in _find_rows_by_type(rows, "batch_scenario"):
        summary = {
            "runs": _parse_int(scenario_row.get("multi_run_summary.runs")),
            "seeds": _read_seed_list(scenario_row.get("multi_run_summary.seeds")),
            "extinction_count": _parse_int(scenario_row.get("multi_run_summary.extinction_count")),
            "extinction_rate": _parse_float(scenario_row.get("multi_run_summary.extinction_rate")),
            "avg_max_generation": _parse_float(scenario_row.get("multi_run_summary.avg_max_generation")),
            "avg_final_population": _parse_float(scenario_row.get("multi_run_summary.avg_final_population")),
            "avg_final_traits": {
                "speed": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.speed")),
                "metabolism": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.metabolism")),
                "prudence": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.prudence")),
                "dominance": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.dominance")),
                "repro_drive": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.repro_drive")),
                "food_perception": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.food_perception")),
                "threat_perception": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.threat_perception")),
                "energy_efficiency": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.energy_efficiency")),
                "exhaustion_resistance": _parse_float(scenario_row.get("multi_run_summary.avg_final_traits.exhaustion_resistance")),
            },
            "most_frequent_final_dominant_group": scenario_row.get(
                "multi_run_summary.most_frequent_final_dominant_group",
                "-",
            ),
            "most_frequent_final_dominant_group_count": _parse_int(
                scenario_row.get("multi_run_summary.most_frequent_final_dominant_group_count")
            ),
            "most_frequent_final_dominant_group_share": _parse_float(
                scenario_row.get("multi_run_summary.most_frequent_final_dominant_group_share")
            ),
            "avg_memory_impact": {
                "food_usage_total": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.food_usage_total")),
                "danger_usage_total": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.danger_usage_total")),
                "food_active_share": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.food_active_share")),
                "danger_active_share": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.danger_active_share")),
                "food_effect_avg_distance": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.food_effect_avg_distance")),
                "danger_effect_avg_distance": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.danger_effect_avg_distance")),
                "food_usage_per_tick": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.food_usage_per_tick")),
                "danger_usage_per_tick": _parse_float(scenario_row.get("multi_run_summary.avg_memory_impact.danger_usage_per_tick")),
            },
            "avg_social_impact": {
                "follow_usage_total": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.follow_usage_total")),
                "flee_boost_usage_total": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.flee_boost_usage_total")),
                "influenced_count_last_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.influenced_count_last_tick")),
                "influenced_share_last_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.influenced_share_last_tick")),
                "influenced_per_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.influenced_per_tick")),
                "follow_usage_per_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.follow_usage_per_tick")),
                "flee_boost_usage_per_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.flee_boost_usage_per_tick")),
                "flee_multiplier_avg_tick": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.flee_multiplier_avg_tick"), default=1.0),
                "flee_multiplier_avg_total": _parse_float(scenario_row.get("multi_run_summary.avg_social_impact.flee_multiplier_avg_total"), default=1.0),
            },
            "avg_trait_impact": {
                "memory_focus_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.memory_focus_mean")),
                "memory_focus_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.memory_focus_std")),
                "social_sensitivity_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.social_sensitivity_mean")),
                "social_sensitivity_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.social_sensitivity_std")),
                "food_perception_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.food_perception_mean")),
                "food_perception_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.food_perception_std")),
                "threat_perception_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.threat_perception_mean")),
                "threat_perception_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.threat_perception_std")),
                "energy_efficiency_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.energy_efficiency_mean")),
                "energy_efficiency_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.energy_efficiency_std")),
                "exhaustion_resistance_mean": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.exhaustion_resistance_mean")),
                "exhaustion_resistance_std": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.exhaustion_resistance_std")),
                "memory_focus_food_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.memory_focus_food_bias")),
                "memory_focus_danger_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.memory_focus_danger_bias")),
                "social_sensitivity_follow_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.social_sensitivity_follow_bias")),
                "social_sensitivity_flee_boost_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.social_sensitivity_flee_boost_bias")),
                "food_perception_detection_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.food_perception_detection_bias")),
                "food_perception_consumption_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.food_perception_consumption_bias")),
                "threat_perception_flee_bias": _parse_float(scenario_row.get("multi_run_summary.avg_trait_impact.threat_perception_flee_bias")),
            },
        }
        scenarios.append(
            {
                "parameter_value": _parse_float(scenario_row.get("parameter_value")),
                "seeds": _read_seed_list(scenario_row.get("seeds")),
                "multi_run_summary": summary,
            }
        )

    return {
        "mode": "batch",
        "batch_param": str(aggregate_row.get("batch_param", "?")),
        "batch_values": _read_float_list(aggregate_row.get("batch_values")),
        "runs_per_value": _parse_int(aggregate_row.get("runs_per_value")),
        "base_seed": _parse_int(aggregate_row.get("base_seed")),
        "seed_step": _parse_int(aggregate_row.get("seed_step")),
        "scenarios": scenarios,
    }


def _read_seed_list(raw: object) -> list[int]:
    if isinstance(raw, list):
        return [int(seed) for seed in raw]

    text = "" if raw is None else str(raw).strip()
    if text == "":
        return []

    parts = [part.strip() for part in text.split("|") if part.strip() != ""]
    return [int(float(part)) for part in parts]


def _read_float_list(raw: object) -> list[float]:
    if isinstance(raw, list):
        return [float(value) for value in raw]

    text = "" if raw is None else str(raw).strip()
    if text == "":
        return []

    parts = [part.strip() for part in text.split("|") if part.strip() != ""]
    return [float(part) for part in parts]


def _parse_int(raw: object, default: int = 0) -> int:
    text = "" if raw is None else str(raw).strip()
    if text == "":
        return default
    return int(float(text))


def _parse_float(raw: object, default: float = 0.0) -> float:
    text = "" if raw is None else str(raw).strip()
    if text == "":
        return default
    return float(text)


def _parse_bool(raw: object, default: bool = False) -> bool:
    text = "" if raw is None else str(raw).strip().lower()
    if text == "":
        return default
    if text in ("1", "true", "yes"):
        return True
    if text in ("0", "false", "no"):
        return False
    return default


def _format_batch_value(value: float) -> str:
    if float(value).is_integer():
        return f"{value:.1f}"
    return f"{value:.6g}"

