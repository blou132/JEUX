from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


_HISTORY_SCHEMA_VERSION = 1


def build_batch_history_entry(batch_id: str, batch_payload: Dict[str, object]) -> Dict[str, object]:
    if str(batch_payload.get("mode", "")) != "batch":
        raise ValueError("batch_payload mode must be 'batch'")

    scenarios_raw = batch_payload.get("scenarios")
    scenario_summaries: list[Dict[str, object]] = []
    if isinstance(scenarios_raw, list):
        for scenario in scenarios_raw:
            if not isinstance(scenario, dict):
                continue

            summary_raw = scenario.get("multi_run_summary")
            if not isinstance(summary_raw, dict):
                continue

            scenario_summaries.append(
                {
                    "parameter_value": float(scenario.get("parameter_value", 0.0)),
                    "runs": int(summary_raw.get("runs", 0)),
                    "extinction_rate": float(summary_raw.get("extinction_rate", 0.0)),
                    "avg_max_generation": float(summary_raw.get("avg_max_generation", 0.0)),
                    "avg_final_population": float(summary_raw.get("avg_final_population", 0.0)),
                }
            )

    comparative_raw = batch_payload.get("comparative_summary")
    comparative_summary = dict(comparative_raw) if isinstance(comparative_raw, dict) else {}

    return {
        "id": str(batch_id),
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "batch_param": str(batch_payload.get("batch_param", "?")),
        "batch_values": _read_float_list(batch_payload.get("batch_values")),
        "runs_per_value": int(batch_payload.get("runs_per_value", 0)),
        "base_seed": int(batch_payload.get("base_seed", 0)),
        "seed_step": int(batch_payload.get("seed_step", 1)),
        "comparative_summary": comparative_summary,
        "scenario_summaries": scenario_summaries,
    }


def append_batch_history(history_path: str, entry: Dict[str, object]) -> Path:
    output_path = Path(history_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    history = _load_or_init_history(output_path)
    experiments = history["experiments"]

    entry_id = str(entry.get("id", "")).strip()
    if entry_id == "":
        raise ValueError("entry id cannot be empty")

    existing_ids = {str(item.get("id", "")) for item in experiments if isinstance(item, dict)}
    if entry_id in existing_ids:
        raise ValueError(f"batch id already exists in history: {entry_id}")

    experiments.append(dict(entry))

    output_path.write_text(
        json.dumps(history, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path


def load_batch_history(history_path: str) -> Dict[str, object]:
    path = Path(history_path)
    if not path.exists():
        raise ValueError(f"history file does not exist: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("history file must contain a JSON object")

    experiments = raw.get("experiments")
    if not isinstance(experiments, list):
        raise ValueError("history file must contain an 'experiments' list")

    schema_version = int(raw.get("schema_version", _HISTORY_SCHEMA_VERSION))

    return {
        "schema_version": schema_version,
        "experiments": [dict(item) for item in experiments if isinstance(item, dict)],
    }


def format_batch_history_summary(history: Dict[str, object], max_entries: int = 20) -> str:
    if max_entries <= 0:
        raise ValueError("max_entries must be > 0")

    experiments_raw = history.get("experiments")
    if not isinstance(experiments_raw, list) or len(experiments_raw) == 0:
        return "historique_batch: vide"

    experiments = [item for item in experiments_raw if isinstance(item, dict)]
    total = len(experiments)

    shown = experiments[-max_entries:]

    lines = [
        "=== Batch History ===",
        "experiences={total} affichees={shown_count} schema={schema}".format(
            total=total,
            shown_count=len(shown),
            schema=int(history.get("schema_version", _HISTORY_SCHEMA_VERSION)),
        ),
    ]

    for entry in shown:
        batch_param = str(entry.get("batch_param", "?"))
        values_text = ",".join(_format_value(value) for value in _read_float_list(entry.get("batch_values")))

        lines.append(
            "id={id} date={date} param={param} valeurs={values} runs_par_valeur={runs}".format(
                id=str(entry.get("id", "?")),
                date=str(entry.get("recorded_at_utc", "?")),
                param=batch_param,
                values=values_text,
                runs=int(entry.get("runs_per_value", 0)),
            )
        )

        comparative_raw = entry.get("comparative_summary")
        comparative = comparative_raw if isinstance(comparative_raw, dict) else {}

        stable = _winner_label(batch_param, comparative.get("most_stable"))
        best_gen = _winner_label(batch_param, comparative.get("best_avg_max_generation"))
        best_pop = _winner_label(batch_param, comparative.get("best_avg_final_population"))
        low_ext = _winner_label(batch_param, comparative.get("lowest_extinction_rate"))

        lines.append(
            "  comparatif: stable={stable} gen={gen} pop={pop} extinction={ext}".format(
                stable=stable,
                gen=best_gen,
                pop=best_pop,
                ext=low_ext,
            )
        )

    return "\n".join(lines)


def _load_or_init_history(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {
            "schema_version": _HISTORY_SCHEMA_VERSION,
            "experiments": [],
        }

    loaded = load_batch_history(str(path))
    return {
        "schema_version": int(loaded.get("schema_version", _HISTORY_SCHEMA_VERSION)),
        "experiments": list(loaded.get("experiments", [])),
    }


def _winner_label(batch_param: str, metric_raw: object) -> str:
    if not isinstance(metric_raw, dict):
        return "n/a"

    winners_raw = metric_raw.get("winners")
    winners = _read_float_list(winners_raw)
    if len(winners) == 0:
        return "n/a"

    if len(winners) == 1:
        return f"{batch_param}={_format_value(winners[0])}"

    joined = ",".join(_format_value(value) for value in winners)
    return f"egalite[{batch_param}={joined}]"


def _read_float_list(raw: object) -> list[float]:
    if isinstance(raw, list):
        parsed: list[float] = []
        for value in raw:
            try:
                parsed.append(float(value))
            except (TypeError, ValueError):
                continue
        return parsed

    return []


def _format_value(value: float) -> str:
    if float(value).is_integer():
        return f"{value:.1f}"
    return f"{value:.6g}"
