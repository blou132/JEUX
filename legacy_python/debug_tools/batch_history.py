from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


_HISTORY_SCHEMA_VERSION = 1

_MEMORY_BATCH_PARAMS = {
    "food_memory_duration",
    "danger_memory_duration",
    "food_memory_recall_distance",
    "danger_memory_avoid_distance",
}

_SOCIAL_BATCH_PARAMS = {
    "social_influence_distance",
    "social_follow_strength",
    "social_flee_boost_per_neighbor",
    "social_flee_boost_max",
}

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

    mechanism_summary = build_batch_history_behavior_mechanic_comparison_summary(history)
    lines.append("--- Batch History Memory vs Social ---")
    lines.append(format_batch_history_behavior_mechanic_comparison_summary(mechanism_summary))

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


def build_batch_history_behavior_mechanic_comparison_summary(history: Dict[str, object]) -> Dict[str, object]:
    experiments_raw = history.get("experiments")
    if not isinstance(experiments_raw, list):
        experiments_raw = []

    experiments = [item for item in experiments_raw if isinstance(item, dict)]

    memory_campaigns = [
        entry
        for entry in experiments
        if str(entry.get("batch_param", "")).strip() in _MEMORY_BATCH_PARAMS
    ]
    social_campaigns = [
        entry
        for entry in experiments
        if str(entry.get("batch_param", "")).strip() in _SOCIAL_BATCH_PARAMS
    ]

    memory_general = _build_mechanic_general_effect(memory_campaigns)
    social_general = _build_mechanic_general_effect(social_campaigns)

    memory_behavior = _build_memory_behavior_effect(memory_campaigns)
    social_behavior = _build_social_behavior_effect(social_campaigns)

    return {
        "memory_campaign_count": len(memory_campaigns),
        "social_campaign_count": len(social_campaigns),
        "memory_general": memory_general,
        "social_general": social_general,
        "stability_effect": _compare_mechanic_metric(
            memory_general.get("avg_extinction_delta"),
            social_general.get("avg_extinction_delta"),
        ),
        "generation_effect": _compare_mechanic_metric(
            memory_general.get("avg_generation_delta"),
            social_general.get("avg_generation_delta"),
        ),
        "population_effect": _compare_mechanic_metric(
            memory_general.get("avg_population_delta"),
            social_general.get("avg_population_delta"),
        ),
        "memory_behavior": memory_behavior,
        "social_behavior": social_behavior,
        "comparability_note": (
            "les metriques comportementales memoire/social sont affichees separement "
            "(unites differentes, comparaison directe non stricte)"
        ),
    }


def format_batch_history_behavior_mechanic_comparison_summary(summary: Dict[str, object]) -> str:
    memory_campaigns = int(summary.get("memory_campaign_count", 0))
    social_campaigns = int(summary.get("social_campaign_count", 0))

    if memory_campaigns <= 0 and social_campaigns <= 0:
        return "historique_batch_memoire_vs_social: n/a"

    lines = [
        "historique_batch_memoire_vs_social:",
        f"campagnes_memoire={memory_campaigns} campagnes_sociales={social_campaigns}",
    ]

    memory_general_raw = summary.get("memory_general")
    social_general_raw = summary.get("social_general")
    memory_general = memory_general_raw if isinstance(memory_general_raw, dict) else {}
    social_general = social_general_raw if isinstance(social_general_raw, dict) else {}

    lines.append(
        "delta_moy_stabilite_taux_ext: memoire={m} social={s}".format(
            m=_format_optional_float(memory_general.get("avg_extinction_delta")),
            s=_format_optional_float(social_general.get("avg_extinction_delta")),
        )
    )
    lines.append(
        "delta_moy_gen_max: memoire={m} social={s}".format(
            m=_format_optional_float(memory_general.get("avg_generation_delta")),
            s=_format_optional_float(social_general.get("avg_generation_delta")),
        )
    )
    lines.append(
        "delta_moy_pop_finale: memoire={m} social={s}".format(
            m=_format_optional_float(memory_general.get("avg_population_delta")),
            s=_format_optional_float(social_general.get("avg_population_delta")),
        )
    )

    lines.append(
        "lecture_stabilite={label}".format(
            label=_format_mechanic_comparison_label(summary.get("stability_effect")),
        )
    )
    lines.append(
        "lecture_gen_max={label}".format(
            label=_format_mechanic_comparison_label(summary.get("generation_effect")),
        )
    )
    lines.append(
        "lecture_pop_finale={label}".format(
            label=_format_mechanic_comparison_label(summary.get("population_effect")),
        )
    )

    memory_behavior_raw = summary.get("memory_behavior")
    memory_behavior = memory_behavior_raw if isinstance(memory_behavior_raw, dict) else {}
    if bool(memory_behavior.get("available", False)):
        lines.append(
            "comportement_memoire: usage_utile_max_moy={food_u} usage_dangereuse_max_moy={danger_u} "
            "effet_utile_max_moy={food_e} effet_dangereuse_max_moy={danger_e}".format(
                food_u=_format_optional_float(memory_behavior.get("food_usage_total_avg")),
                danger_u=_format_optional_float(memory_behavior.get("danger_usage_total_avg")),
                food_e=_format_optional_float(memory_behavior.get("food_effect_avg_distance_avg")),
                danger_e=_format_optional_float(memory_behavior.get("danger_effect_avg_distance_avg")),
            )
        )
    else:
        lines.append(
            "comportement_memoire: n/a ({note})".format(
                note=str(memory_behavior.get("note", "donnees insuffisantes")),
            )
        )

    social_behavior_raw = summary.get("social_behavior")
    social_behavior = social_behavior_raw if isinstance(social_behavior_raw, dict) else {}
    if bool(social_behavior.get("available", False)):
        lines.append(
            "comportement_social: suivi_max_moy={follow} boost_fuite_max_moy={flee} "
            "part_influencee_max_moy={share} multiplicateur_fuite_max_moy={mult}".format(
                follow=_format_optional_float(social_behavior.get("follow_usage_per_tick_avg")),
                flee=_format_optional_float(social_behavior.get("flee_boost_usage_per_tick_avg")),
                share=_format_optional_float(social_behavior.get("influenced_share_last_tick_avg")),
                mult=_format_optional_float(social_behavior.get("flee_multiplier_avg_total_avg")),
            )
        )
    else:
        lines.append(
            "comportement_social: n/a ({note})".format(
                note=str(social_behavior.get("note", "donnees insuffisantes")),
            )
        )

    lines.append(f"note={str(summary.get('comparability_note', 'n/a'))}")

    return "\n".join(lines)


def _build_mechanic_general_effect(campaigns: list[Dict[str, object]]) -> Dict[str, object]:
    deltas: list[Dict[str, float]] = []
    for campaign in campaigns:
        delta = _extract_scenario_effect_deltas(campaign)
        if delta is None:
            continue
        deltas.append(delta)

    if len(deltas) == 0:
        return {
            "comparable_campaigns": 0,
            "avg_extinction_delta": None,
            "avg_generation_delta": None,
            "avg_population_delta": None,
        }

    return {
        "comparable_campaigns": len(deltas),
        "avg_extinction_delta": sum(item["extinction_delta"] for item in deltas) / len(deltas),
        "avg_generation_delta": sum(item["generation_delta"] for item in deltas) / len(deltas),
        "avg_population_delta": sum(item["population_delta"] for item in deltas) / len(deltas),
    }


def _build_memory_behavior_effect(campaigns: list[Dict[str, object]]) -> Dict[str, object]:
    food_usage: list[float] = []
    danger_usage: list[float] = []
    food_effect: list[float] = []
    danger_effect: list[float] = []

    for campaign in campaigns:
        memory = _extract_memory_comparative(campaign)
        if memory is None:
            continue

        _append_metric_value(food_usage, memory, "best_food_memory_usage")
        _append_metric_value(danger_usage, memory, "best_danger_memory_usage")
        _append_metric_value(food_effect, memory, "best_food_memory_effect")
        _append_metric_value(danger_effect, memory, "best_danger_memory_effect")

    if len(food_usage) == 0 and len(danger_usage) == 0 and len(food_effect) == 0 and len(danger_effect) == 0:
        return {
            "available": False,
            "note": "donnees memoire insuffisantes dans l'historique",
        }

    return {
        "available": True,
        "food_usage_total_avg": _avg_or_none(food_usage),
        "danger_usage_total_avg": _avg_or_none(danger_usage),
        "food_effect_avg_distance_avg": _avg_or_none(food_effect),
        "danger_effect_avg_distance_avg": _avg_or_none(danger_effect),
        "campaigns_with_data": max(len(food_usage), len(danger_usage), len(food_effect), len(danger_effect)),
    }


def _build_social_behavior_effect(campaigns: list[Dict[str, object]]) -> Dict[str, object]:
    follow_usage: list[float] = []
    flee_usage: list[float] = []
    influenced_share: list[float] = []
    flee_multiplier: list[float] = []

    for campaign in campaigns:
        social = _extract_social_comparative(campaign)
        if social is None:
            continue

        _append_metric_value(follow_usage, social, "best_social_follow_usage")
        _append_metric_value(flee_usage, social, "best_social_flee_boost_usage")
        _append_metric_value(influenced_share, social, "best_social_influenced_share")
        _append_metric_value(flee_multiplier, social, "best_social_flee_multiplier_effect")

    if len(follow_usage) == 0 and len(flee_usage) == 0 and len(influenced_share) == 0 and len(flee_multiplier) == 0:
        return {
            "available": False,
            "note": "donnees sociales insuffisantes dans l'historique",
        }

    return {
        "available": True,
        "follow_usage_per_tick_avg": _avg_or_none(follow_usage),
        "flee_boost_usage_per_tick_avg": _avg_or_none(flee_usage),
        "influenced_share_last_tick_avg": _avg_or_none(influenced_share),
        "flee_multiplier_avg_total_avg": _avg_or_none(flee_multiplier),
        "campaigns_with_data": max(len(follow_usage), len(flee_usage), len(influenced_share), len(flee_multiplier)),
    }


def _extract_scenario_effect_deltas(entry: Dict[str, object]) -> Dict[str, float] | None:
    scenarios_raw = entry.get("scenario_summaries")
    if not isinstance(scenarios_raw, list):
        return None

    ext_rates: list[float] = []
    generations: list[float] = []
    populations: list[float] = []

    for scenario in scenarios_raw:
        if not isinstance(scenario, dict):
            continue

        ext_rates.append(float(scenario.get("extinction_rate", 0.0)))
        generations.append(float(scenario.get("avg_max_generation", 0.0)))
        populations.append(float(scenario.get("avg_final_population", 0.0)))

    if len(ext_rates) == 0:
        return None

    return {
        "extinction_delta": max(ext_rates) - min(ext_rates),
        "generation_delta": max(generations) - min(generations),
        "population_delta": max(populations) - min(populations),
    }


def _extract_memory_comparative(entry: Dict[str, object]) -> Dict[str, object] | None:
    comparative_raw = entry.get("comparative_summary")
    if not isinstance(comparative_raw, dict):
        return None

    memory_raw = comparative_raw.get("memory_comparative")
    if not isinstance(memory_raw, dict):
        return None

    if not bool(memory_raw.get("available", False)):
        return None

    return memory_raw


def _extract_social_comparative(entry: Dict[str, object]) -> Dict[str, object] | None:
    comparative_raw = entry.get("comparative_summary")
    if not isinstance(comparative_raw, dict):
        return None

    social_raw = comparative_raw.get("social_comparative")
    if not isinstance(social_raw, dict):
        return None

    if not bool(social_raw.get("available", False)):
        return None

    return social_raw


def _append_metric_value(target: list[float], comparative: Dict[str, object], field: str) -> None:
    metric_raw = comparative.get(field)
    if not isinstance(metric_raw, dict):
        return

    if bool(metric_raw.get("insufficient", False)):
        return

    try:
        target.append(float(metric_raw.get("value")))
    except (TypeError, ValueError):
        return


def _compare_mechanic_metric(memory_value_raw: object, social_value_raw: object) -> Dict[str, object]:
    memory_value = _parse_optional_float(memory_value_raw)
    social_value = _parse_optional_float(social_value_raw)

    if memory_value is None and social_value is None:
        return {
            "status": "insufficient",
            "winner": "n/a",
            "memory": None,
            "social": None,
            "note": "donnees insuffisantes",
        }

    if memory_value is None or social_value is None:
        return {
            "status": "non_comparable",
            "winner": "n/a",
            "memory": memory_value,
            "social": social_value,
            "note": "donnees non comparables entre mecaniques",
        }

    if _is_close(memory_value, social_value):
        return {
            "status": "tie",
            "winner": "egalite",
            "memory": memory_value,
            "social": social_value,
            "note": "egalite",
        }

    winner = "memory" if memory_value > social_value else "social"
    return {
        "status": "ok",
        "winner": winner,
        "memory": memory_value,
        "social": social_value,
        "note": "",
    }


def _format_mechanic_comparison_label(metric_raw: object) -> str:
    if not isinstance(metric_raw, dict):
        return "n/a (donnees insuffisantes)"

    winner = str(metric_raw.get("winner", "n/a"))
    status = str(metric_raw.get("status", "insufficient"))

    if status == "ok":
        return winner
    if status == "tie":
        return "egalite"

    note = str(metric_raw.get("note", "donnees insuffisantes"))
    return f"n/a ({note})"


def _avg_or_none(values: list[float]) -> float | None:
    if len(values) == 0:
        return None
    return sum(values) / len(values)


def _parse_optional_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_optional_float(value: object) -> str:
    parsed = _parse_optional_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:.2f}"


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
