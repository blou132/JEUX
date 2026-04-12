from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable


def build_single_run_export(seed: int, result: Dict[str, object]) -> Dict[str, object]:
    run_summary_raw = result.get("run_summary")
    run_summary = dict(run_summary_raw) if isinstance(run_summary_raw, dict) else {}

    return {
        "mode": "single",
        "seed": int(seed),
        "extinct": bool(result.get("extinct", False)),
        "max_generation": int(result.get("max_generation", 0)),
        "final_alive": int(result.get("final_alive", 0)),
        "final_population": int(result.get("final_population", 0)),
        "run_summary": run_summary,
    }


def build_multi_run_export(
    seeds: Iterable[int],
    run_results: Iterable[Dict[str, object]],
    multi_run_summary: Dict[str, object],
) -> Dict[str, object]:
    runs: list[Dict[str, object]] = []

    for result in run_results:
        run_summary_raw = result.get("run_summary")
        run_summary = dict(run_summary_raw) if isinstance(run_summary_raw, dict) else {}

        runs.append(
            {
                "seed": int(result.get("seed", 0)),
                "extinct": bool(result.get("extinct", False)),
                "max_generation": int(result.get("max_generation", 0)),
                "final_alive": int(result.get("final_alive", 0)),
                "final_population": int(result.get("final_population", 0)),
                "run_summary": run_summary,
            }
        )

    return {
        "mode": "multi",
        "seeds": [int(seed) for seed in seeds],
        "run_count": len(runs),
        "multi_run_summary": dict(multi_run_summary),
        "per_run": runs,
    }


def build_batch_experiment_export(
    batch_param: str,
    batch_values: Iterable[float | int],
    runs_per_value: int,
    base_seed: int,
    seed_step: int,
    scenarios: Iterable[Dict[str, object]],
    comparative_summary: Dict[str, object] | None = None,
) -> Dict[str, object]:
    parsed_scenarios: list[Dict[str, object]] = []
    for scenario in scenarios:
        parsed = dict(scenario)

        seeds_raw = scenario.get("seeds")
        if isinstance(seeds_raw, list):
            parsed["seeds"] = [int(seed) for seed in seeds_raw]

        summary_raw = scenario.get("multi_run_summary")
        if isinstance(summary_raw, dict):
            parsed["multi_run_summary"] = dict(summary_raw)

        per_run_raw = scenario.get("per_run")
        if isinstance(per_run_raw, list):
            parsed["per_run"] = [dict(item) if isinstance(item, dict) else item for item in per_run_raw]

        parsed_scenarios.append(parsed)

    payload: Dict[str, object] = {
        "mode": "batch",
        "batch_param": str(batch_param),
        "batch_values": [float(value) for value in batch_values],
        "runs_per_value": int(runs_per_value),
        "base_seed": int(base_seed),
        "seed_step": int(seed_step),
        "scenarios": parsed_scenarios,
    }

    if comparative_summary is not None:
        payload["comparative_summary"] = dict(comparative_summary)

    return payload


def export_results(payload: Dict[str, object], export_path: str, export_format: str) -> Path:
    output_path = Path(export_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if export_format == "json":
        output_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return output_path

    if export_format == "csv":
        rows = _build_csv_rows(payload)
        _write_csv_rows(output_path, rows)
        return output_path

    raise ValueError("export_format must be 'json' or 'csv'")


def _build_csv_rows(payload: Dict[str, object]) -> list[Dict[str, object]]:
    mode = str(payload.get("mode", "unknown"))

    if mode == "single":
        row: Dict[str, object] = {"row_type": "single"}
        row.update(_flatten_to_row(payload))
        return [row]

    if mode == "multi":
        rows: list[Dict[str, object]] = []

        aggregate_payload = {key: value for key, value in payload.items() if key != "per_run"}
        aggregate_row: Dict[str, object] = {"row_type": "aggregate"}
        aggregate_row.update(_flatten_to_row(aggregate_payload))
        rows.append(aggregate_row)

        per_run_raw = payload.get("per_run")
        if isinstance(per_run_raw, list):
            for index, run_data in enumerate(per_run_raw, start=1):
                if not isinstance(run_data, dict):
                    continue
                run_row: Dict[str, object] = {
                    "row_type": "run",
                    "run_index": index,
                }
                run_row.update(_flatten_to_row(run_data))
                rows.append(run_row)

        return rows

    if mode == "batch":
        rows: list[Dict[str, object]] = []

        scenarios_raw = payload.get("scenarios")
        scenario_count = len(scenarios_raw) if isinstance(scenarios_raw, list) else 0
        aggregate_payload = dict(payload)
        aggregate_payload.pop("scenarios", None)
        aggregate_payload["scenario_count"] = scenario_count

        aggregate_row: Dict[str, object] = {"row_type": "batch_aggregate"}
        aggregate_row.update(_flatten_to_row(aggregate_payload))
        rows.append(aggregate_row)

        if isinstance(scenarios_raw, list):
            for scenario_index, scenario_raw in enumerate(scenarios_raw, start=1):
                if not isinstance(scenario_raw, dict):
                    continue

                scenario_payload = dict(scenario_raw)
                scenario_payload.pop("per_run", None)
                scenario_row: Dict[str, object] = {
                    "row_type": "batch_scenario",
                    "scenario_index": scenario_index,
                }
                scenario_row.update(_flatten_to_row(scenario_payload))
                rows.append(scenario_row)

                per_run_raw = scenario_raw.get("per_run")
                if not isinstance(per_run_raw, list):
                    continue

                for run_index, run_data in enumerate(per_run_raw, start=1):
                    if not isinstance(run_data, dict):
                        continue
                    run_row: Dict[str, object] = {
                        "row_type": "batch_run",
                        "scenario_index": scenario_index,
                        "run_index": run_index,
                    }
                    run_row.update(_flatten_to_row(run_data))
                    rows.append(run_row)

        return rows

    row: Dict[str, object] = {"row_type": "unknown"}
    row.update(_flatten_to_row(payload))
    return [row]


def _write_csv_rows(output_path: Path, rows: list[Dict[str, object]]) -> None:
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    header_keys: list[str] = sorted({key for row in rows for key in row.keys()})

    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=header_keys)
        writer.writeheader()

        for row in rows:
            rendered = {key: _render_csv_value(row.get(key)) for key in header_keys}
            writer.writerow(rendered)


def _render_csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _flatten_to_row(payload: Dict[str, object]) -> Dict[str, object]:
    flattened: Dict[str, object] = {}
    _flatten_value(prefix="", value=payload, output=flattened)
    return flattened


def _flatten_value(prefix: str, value: object, output: Dict[str, object]) -> None:
    if isinstance(value, dict):
        if not value:
            output[prefix] = ""
            return
        for key in sorted(value.keys()):
            child_prefix = str(key) if prefix == "" else f"{prefix}.{key}"
            _flatten_value(child_prefix, value[key], output)
        return

    if isinstance(value, list):
        if not value:
            output[prefix] = ""
            return

        primitive_only = all(not isinstance(item, (dict, list)) for item in value)
        if primitive_only:
            output[prefix] = "|".join(str(item) for item in value)
            return

        for index, item in enumerate(value):
            child_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            _flatten_value(child_prefix, item, output)
        return

    output[prefix] = value
