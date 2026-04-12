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

    global_summary = build_batch_history_global_summary(history)
    lines.append("--- Batch History Comparative Summary ---")
    lines.append(format_batch_history_global_summary(global_summary))

    parameter_summary = build_batch_history_parameter_impact_summary(history)
    lines.append("--- Batch History Parameter Impact ---")
    lines.append(format_batch_history_parameter_impact_summary(parameter_summary))

    return "\n".join(lines)


def build_batch_history_global_summary(history: Dict[str, object]) -> Dict[str, object]:
    experiments_raw = history.get("experiments")
    if not isinstance(experiments_raw, list):
        experiments_raw = []

    experiments = [item for item in experiments_raw if isinstance(item, dict)]
    campaign_count = len(experiments)

    tested_params = sorted(
        {
            str(item.get("batch_param", "?"))
            for item in experiments
            if str(item.get("batch_param", "")).strip() != ""
        }
    )

    campaign_metrics: list[Dict[str, object]] = []
    for entry in experiments:
        metrics = _extract_campaign_metrics(entry)
        if metrics is None:
            continue

        campaign_metrics.append(
            {
                "id": str(entry.get("id", "?")),
                "batch_param": str(entry.get("batch_param", "?")),
                **metrics,
            }
        )

    if len(campaign_metrics) == 0:
        return {
            "campaign_count": campaign_count,
            "tested_params": tested_params,
            "most_stable": _empty_global_metric(),
            "best_avg_max_generation": _empty_global_metric(),
            "best_avg_final_population": _empty_global_metric(),
            "lowest_extinction_rate": _empty_global_metric(),
        }

    stable_rank = sorted(
        campaign_metrics,
        key=lambda item: (
            float(item["stable_extinction_rate"]),
            -float(item["stable_avg_final_population"]),
            -float(item["stable_avg_max_generation"]),
            str(item["id"]),
        ),
    )
    best_stable = stable_rank[0]
    stable_winners = [
        str(item["id"])
        for item in campaign_metrics
        if _is_close(float(item["stable_extinction_rate"]), float(best_stable["stable_extinction_rate"]))
        and _is_close(float(item["stable_avg_final_population"]), float(best_stable["stable_avg_final_population"]))
        and _is_close(float(item["stable_avg_max_generation"]), float(best_stable["stable_avg_max_generation"]))
    ]

    best_gen_value = max(float(item["best_avg_max_generation"]) for item in campaign_metrics)
    best_gen_winners = [
        str(item["id"])
        for item in campaign_metrics
        if _is_close(float(item["best_avg_max_generation"]), best_gen_value)
    ]

    best_pop_value = max(float(item["best_avg_final_population"]) for item in campaign_metrics)
    best_pop_winners = [
        str(item["id"])
        for item in campaign_metrics
        if _is_close(float(item["best_avg_final_population"]), best_pop_value)
    ]

    lowest_ext_value = min(float(item["lowest_extinction_rate"]) for item in campaign_metrics)
    lowest_ext_winners = [
        str(item["id"])
        for item in campaign_metrics
        if _is_close(float(item["lowest_extinction_rate"]), lowest_ext_value)
    ]

    return {
        "campaign_count": campaign_count,
        "tested_params": tested_params,
        "most_stable": {
            "winners": sorted(stable_winners),
            "tie": len(stable_winners) > 1,
            "extinction_rate": float(best_stable["stable_extinction_rate"]),
            "avg_final_population": float(best_stable["stable_avg_final_population"]),
            "avg_max_generation": float(best_stable["stable_avg_max_generation"]),
        },
        "best_avg_max_generation": {
            "winners": sorted(best_gen_winners),
            "tie": len(best_gen_winners) > 1,
            "avg_max_generation": best_gen_value,
        },
        "best_avg_final_population": {
            "winners": sorted(best_pop_winners),
            "tie": len(best_pop_winners) > 1,
            "avg_final_population": best_pop_value,
        },
        "lowest_extinction_rate": {
            "winners": sorted(lowest_ext_winners),
            "tie": len(lowest_ext_winners) > 1,
            "extinction_rate": lowest_ext_value,
        },
    }


def format_batch_history_global_summary(summary: Dict[str, object]) -> str:
    campaign_count = int(summary.get("campaign_count", 0))
    tested_params_raw = summary.get("tested_params")
    tested_params = tested_params_raw if isinstance(tested_params_raw, list) else []

    params_text = "-" if len(tested_params) == 0 else ",".join(str(param) for param in tested_params)

    most_stable_raw = summary.get("most_stable")
    best_gen_raw = summary.get("best_avg_max_generation")
    best_pop_raw = summary.get("best_avg_final_population")
    lowest_ext_raw = summary.get("lowest_extinction_rate")

    most_stable = most_stable_raw if isinstance(most_stable_raw, dict) else _empty_global_metric()
    best_gen = best_gen_raw if isinstance(best_gen_raw, dict) else _empty_global_metric()
    best_pop = best_pop_raw if isinstance(best_pop_raw, dict) else _empty_global_metric()
    lowest_ext = lowest_ext_raw if isinstance(lowest_ext_raw, dict) else _empty_global_metric()

    if campaign_count <= 0:
        return "historique_batch_comparatif: n/a"

    lines = [
        "historique_batch_comparatif:",
        f"campagnes_archivees={campaign_count}",
        f"parametres_testes={params_text}",
        "campagne_plus_stable={label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
            label=_campaign_label(most_stable.get("winners")),
            ext=float(most_stable.get("extinction_rate", 0.0)),
            pop=float(most_stable.get("avg_final_population", 0.0)),
            gen=float(most_stable.get("avg_max_generation", 0.0)),
        ),
        "campagne_meilleure_gen_max_moy={label} (gen_max_moy={gen:.2f})".format(
            label=_campaign_label(best_gen.get("winners")),
            gen=float(best_gen.get("avg_max_generation", 0.0)),
        ),
        "campagne_meilleure_pop_finale_moy={label} (pop_finale_moy={pop:.2f})".format(
            label=_campaign_label(best_pop.get("winners")),
            pop=float(best_pop.get("avg_final_population", 0.0)),
        ),
        "campagne_plus_faible_taux_extinction={label} (taux_ext={ext:.2f})".format(
            label=_campaign_label(lowest_ext.get("winners")),
            ext=float(lowest_ext.get("extinction_rate", 0.0)),
        ),
    ]

    return "\n".join(lines)


def build_batch_history_parameter_impact_summary(history: Dict[str, object]) -> Dict[str, object]:
    experiments_raw = history.get("experiments")
    if not isinstance(experiments_raw, list):
        experiments_raw = []

    grouped_by_param: dict[str, list[Dict[str, object]]] = {}
    for entry in experiments_raw:
        if not isinstance(entry, dict):
            continue

        param = str(entry.get("batch_param", "")).strip()
        if param == "":
            continue

        grouped_by_param.setdefault(param, []).append(entry)

    parameter_summaries: list[Dict[str, object]] = []
    for param in sorted(grouped_by_param.keys()):
        campaigns = grouped_by_param[param]

        stable_counts: dict[float, int] = {}
        gen_counts: dict[float, int] = {}
        pop_counts: dict[float, int] = {}

        stable_with_data = 0
        gen_with_data = 0
        pop_with_data = 0

        for campaign in campaigns:
            stable_winners = _extract_campaign_value_winners(campaign, metric="stable")
            if len(stable_winners) > 0:
                stable_with_data += 1
                _accumulate_value_counts(stable_counts, stable_winners)

            gen_winners = _extract_campaign_value_winners(campaign, metric="best_gen")
            if len(gen_winners) > 0:
                gen_with_data += 1
                _accumulate_value_counts(gen_counts, gen_winners)

            pop_winners = _extract_campaign_value_winners(campaign, metric="best_pop")
            if len(pop_winners) > 0:
                pop_with_data += 1
                _accumulate_value_counts(pop_counts, pop_winners)

        parameter_summaries.append(
            {
                "batch_param": param,
                "campaign_count": len(campaigns),
                "stable_value": _build_value_frequency_summary(stable_counts, stable_with_data),
                "best_gen_value": _build_value_frequency_summary(gen_counts, gen_with_data),
                "best_pop_value": _build_value_frequency_summary(pop_counts, pop_with_data),
            }
        )

    return {
        "parameter_count": len(parameter_summaries),
        "parameters": parameter_summaries,
    }


def format_batch_history_parameter_impact_summary(summary: Dict[str, object]) -> str:
    parameter_count = int(summary.get("parameter_count", 0))
    parameters_raw = summary.get("parameters")
    parameters = parameters_raw if isinstance(parameters_raw, list) else []

    if parameter_count <= 0 or len(parameters) == 0:
        return "historique_batch_parametres: n/a"

    lines = [
        "historique_batch_parametres:",
        f"parametres={parameter_count}",
    ]

    for param_summary_raw in parameters:
        if not isinstance(param_summary_raw, dict):
            continue

        param = str(param_summary_raw.get("batch_param", "?"))
        campaigns = int(param_summary_raw.get("campaign_count", 0))

        stable_value_raw = param_summary_raw.get("stable_value")
        best_gen_value_raw = param_summary_raw.get("best_gen_value")
        best_pop_value_raw = param_summary_raw.get("best_pop_value")

        stable_value = stable_value_raw if isinstance(stable_value_raw, dict) else _empty_parameter_metric_summary()
        best_gen_value = best_gen_value_raw if isinstance(best_gen_value_raw, dict) else _empty_parameter_metric_summary()
        best_pop_value = best_pop_value_raw if isinstance(best_pop_value_raw, dict) else _empty_parameter_metric_summary()

        lines.append(f"parametre={param} campagnes={campaigns}")
        lines.append(
            "  valeur_plus_frequente_stabilite={label}".format(
                label=_format_parameter_metric_choice(stable_value),
            )
        )
        lines.append(
            "  valeur_plus_frequente_gen_max={label}".format(
                label=_format_parameter_metric_choice(best_gen_value),
            )
        )
        lines.append(
            "  valeur_plus_frequente_pop_finale={label}".format(
                label=_format_parameter_metric_choice(best_pop_value),
            )
        )

    return "\n".join(lines)


def _extract_campaign_metrics(entry: Dict[str, object]) -> Dict[str, float] | None:
    scenarios_raw = entry.get("scenario_summaries")
    scenario_candidates: list[Dict[str, float]] = []

    if isinstance(scenarios_raw, list):
        for scenario in scenarios_raw:
            if not isinstance(scenario, dict):
                continue
            scenario_candidates.append(
                {
                    "extinction_rate": float(scenario.get("extinction_rate", 0.0)),
                    "avg_max_generation": float(scenario.get("avg_max_generation", 0.0)),
                    "avg_final_population": float(scenario.get("avg_final_population", 0.0)),
                }
            )

    if len(scenario_candidates) > 0:
        stable_rank = sorted(
            scenario_candidates,
            key=lambda item: (
                float(item["extinction_rate"]),
                -float(item["avg_final_population"]),
                -float(item["avg_max_generation"]),
            ),
        )
        stable_best = stable_rank[0]

        return {
            "stable_extinction_rate": float(stable_best["extinction_rate"]),
            "stable_avg_final_population": float(stable_best["avg_final_population"]),
            "stable_avg_max_generation": float(stable_best["avg_max_generation"]),
            "best_avg_max_generation": max(float(item["avg_max_generation"]) for item in scenario_candidates),
            "best_avg_final_population": max(float(item["avg_final_population"]) for item in scenario_candidates),
            "lowest_extinction_rate": min(float(item["extinction_rate"]) for item in scenario_candidates),
        }

    comparative_raw = entry.get("comparative_summary")
    if not isinstance(comparative_raw, dict):
        return None

    most_stable_raw = comparative_raw.get("most_stable")
    best_gen_raw = comparative_raw.get("best_avg_max_generation")
    best_pop_raw = comparative_raw.get("best_avg_final_population")
    low_ext_raw = comparative_raw.get("lowest_extinction_rate")

    if (
        not isinstance(most_stable_raw, dict)
        or not isinstance(best_gen_raw, dict)
        or not isinstance(best_pop_raw, dict)
        or not isinstance(low_ext_raw, dict)
    ):
        return None

    return {
        "stable_extinction_rate": float(most_stable_raw.get("extinction_rate", 0.0)),
        "stable_avg_final_population": float(most_stable_raw.get("avg_final_population", 0.0)),
        "stable_avg_max_generation": float(most_stable_raw.get("avg_max_generation", 0.0)),
        "best_avg_max_generation": float(best_gen_raw.get("avg_max_generation", 0.0)),
        "best_avg_final_population": float(best_pop_raw.get("avg_final_population", 0.0)),
        "lowest_extinction_rate": float(low_ext_raw.get("extinction_rate", 0.0)),
    }


def _extract_campaign_value_winners(entry: Dict[str, object], metric: str) -> list[float]:
    scenarios_raw = entry.get("scenario_summaries")
    scenarios: list[Dict[str, float]] = []

    if isinstance(scenarios_raw, list):
        for scenario in scenarios_raw:
            if not isinstance(scenario, dict):
                continue

            scenarios.append(
                {
                    "parameter_value": float(scenario.get("parameter_value", 0.0)),
                    "extinction_rate": float(scenario.get("extinction_rate", 0.0)),
                    "avg_max_generation": float(scenario.get("avg_max_generation", 0.0)),
                    "avg_final_population": float(scenario.get("avg_final_population", 0.0)),
                }
            )

    if len(scenarios) > 0:
        if metric == "stable":
            best = min(
                scenarios,
                key=lambda item: (
                    float(item["extinction_rate"]),
                    -float(item["avg_final_population"]),
                    -float(item["avg_max_generation"]),
                ),
            )
            winners = [
                float(item["parameter_value"])
                for item in scenarios
                if _is_close(float(item["extinction_rate"]), float(best["extinction_rate"]))
                and _is_close(float(item["avg_final_population"]), float(best["avg_final_population"]))
                and _is_close(float(item["avg_max_generation"]), float(best["avg_max_generation"]))
            ]
            return _unique_sorted_values(winners)

        if metric == "best_gen":
            best_value = max(float(item["avg_max_generation"]) for item in scenarios)
            winners = [
                float(item["parameter_value"])
                for item in scenarios
                if _is_close(float(item["avg_max_generation"]), best_value)
            ]
            return _unique_sorted_values(winners)

        if metric == "best_pop":
            best_value = max(float(item["avg_final_population"]) for item in scenarios)
            winners = [
                float(item["parameter_value"])
                for item in scenarios
                if _is_close(float(item["avg_final_population"]), best_value)
            ]
            return _unique_sorted_values(winners)

        raise ValueError(f"unsupported metric: {metric}")

    comparative_raw = entry.get("comparative_summary")
    if not isinstance(comparative_raw, dict):
        return []

    if metric == "stable":
        metric_raw = comparative_raw.get("most_stable")
    elif metric == "best_gen":
        metric_raw = comparative_raw.get("best_avg_max_generation")
    elif metric == "best_pop":
        metric_raw = comparative_raw.get("best_avg_final_population")
    else:
        raise ValueError(f"unsupported metric: {metric}")

    if not isinstance(metric_raw, dict):
        return []

    winners_raw = metric_raw.get("winners")
    return _unique_sorted_values(_read_float_list(winners_raw))


def _build_value_frequency_summary(value_counts: Dict[float, int], campaigns_with_data: int) -> Dict[str, object]:
    if campaigns_with_data <= 0 or len(value_counts) == 0:
        return {
            "status": "insufficient",
            "values": [],
            "count": 0,
            "campaigns_with_data": campaigns_with_data,
        }

    top_count = max(int(count) for count in value_counts.values())
    winners = _unique_sorted_values(
        [float(value) for value, count in value_counts.items() if int(count) == top_count]
    )

    return {
        "status": "ambiguous" if len(winners) > 1 else "ok",
        "values": winners,
        "count": top_count,
        "campaigns_with_data": campaigns_with_data,
    }


def _format_parameter_metric_choice(metric_summary_raw: object) -> str:
    if not isinstance(metric_summary_raw, dict):
        return "insuffisant"

    status = str(metric_summary_raw.get("status", "insufficient"))
    values = _read_float_list(metric_summary_raw.get("values"))
    top_count = int(metric_summary_raw.get("count", 0))
    campaigns_with_data = int(metric_summary_raw.get("campaigns_with_data", 0))

    if status == "insufficient" or len(values) == 0 or campaigns_with_data <= 0:
        return "insuffisant"

    values_text = ",".join(_format_value(value) for value in values)
    freq_text = f"{top_count}/{campaigns_with_data}"

    if status == "ambiguous" or len(values) > 1:
        return f"ambigu[{values_text}] (freq={freq_text})"

    return f"{values_text} (freq={freq_text})"


def _accumulate_value_counts(target: Dict[float, int], values: list[float]) -> None:
    for value in values:
        target[float(value)] = int(target.get(float(value), 0)) + 1


def _unique_sorted_values(values: list[float]) -> list[float]:
    if len(values) == 0:
        return []

    sorted_values = sorted(float(value) for value in values)
    unique_values: list[float] = []
    for value in sorted_values:
        if len(unique_values) == 0 or not _is_close(value, unique_values[-1]):
            unique_values.append(value)

    return unique_values


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


def _campaign_label(winners_raw: object) -> str:
    winners: list[str] = []
    if isinstance(winners_raw, list):
        winners = [str(value) for value in winners_raw]

    if len(winners) == 0:
        return "n/a"
    if len(winners) == 1:
        return winners[0]
    return "egalite[" + ",".join(winners) + "]"


def _empty_global_metric() -> Dict[str, object]:
    return {
        "winners": [],
        "tie": False,
    }


def _empty_parameter_metric_summary() -> Dict[str, object]:
    return {
        "status": "insufficient",
        "values": [],
        "count": 0,
        "campaigns_with_data": 0,
    }


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


def _is_close(a: float, b: float, tolerance: float = 1e-9) -> bool:
    return abs(a - b) <= tolerance
