from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict

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
    }

    run_count = _parse_int(row.get("run_count"), default=multi_summary["runs"])

    return {
        "mode": "multi",
        "seeds": seeds,
        "run_count": run_count,
        "multi_run_summary": multi_summary,
    }


def _read_seed_list(raw: object) -> list[int]:
    if isinstance(raw, list):
        return [int(seed) for seed in raw]

    text = "" if raw is None else str(raw).strip()
    if text == "":
        return []

    parts = [part.strip() for part in text.split("|") if part.strip() != ""]
    return [int(part) for part in parts]


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
