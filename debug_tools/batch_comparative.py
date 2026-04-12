from __future__ import annotations

from typing import Dict, Iterable


_MEMORY_BATCH_PARAMS = {
    "food_memory_duration",
    "danger_memory_duration",
    "food_memory_recall_distance",
    "danger_memory_avoid_distance",
}


def build_batch_comparative_summary(
    batch_param: str,
    scenarios: Iterable[Dict[str, object]],
) -> Dict[str, object]:
    candidates: list[Dict[str, float]] = []
    memory_candidates: list[Dict[str, float]] = []

    is_memory_param = batch_param in _MEMORY_BATCH_PARAMS

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue

        summary_raw = scenario.get("multi_run_summary")
        if not isinstance(summary_raw, dict):
            continue

        value = float(scenario.get("parameter_value", 0.0))
        candidates.append(
            {
                "value": value,
                "extinction_rate": float(summary_raw.get("extinction_rate", 0.0)),
                "avg_max_generation": float(summary_raw.get("avg_max_generation", 0.0)),
                "avg_final_population": float(summary_raw.get("avg_final_population", 0.0)),
            }
        )

        if is_memory_param:
            memory_metrics = _read_memory_metrics(summary_raw)
            if memory_metrics is None:
                continue
            memory_candidates.append({"value": value, **memory_metrics})

    if len(candidates) == 0:
        empty: Dict[str, object] = {
            "batch_param": str(batch_param),
            "evaluated_values_count": 0,
            "stability_rule": "extinction_rate asc, avg_final_population desc, avg_max_generation desc",
            "most_stable": _empty_metric_result(),
            "best_avg_max_generation": _empty_metric_result(),
            "best_avg_final_population": _empty_metric_result(),
            "lowest_extinction_rate": _empty_metric_result(),
        }
        if is_memory_param:
            empty["memory_comparative"] = _build_memory_comparative(memory_candidates)
        return empty

    lowest_ext_value = min(candidate["extinction_rate"] for candidate in candidates)
    lowest_ext_candidates = [
        candidate for candidate in candidates if _is_close(candidate["extinction_rate"], lowest_ext_value)
    ]

    stable_best_pop = max(candidate["avg_final_population"] for candidate in lowest_ext_candidates)
    stable_pop_candidates = [
        candidate for candidate in lowest_ext_candidates if _is_close(candidate["avg_final_population"], stable_best_pop)
    ]

    stable_best_gen = max(candidate["avg_max_generation"] for candidate in stable_pop_candidates)
    stable_candidates = [
        candidate for candidate in stable_pop_candidates if _is_close(candidate["avg_max_generation"], stable_best_gen)
    ]

    best_gen_value = max(candidate["avg_max_generation"] for candidate in candidates)
    best_gen_candidates = [
        candidate for candidate in candidates if _is_close(candidate["avg_max_generation"], best_gen_value)
    ]

    best_pop_value = max(candidate["avg_final_population"] for candidate in candidates)
    best_pop_candidates = [
        candidate for candidate in candidates if _is_close(candidate["avg_final_population"], best_pop_value)
    ]

    summary: Dict[str, object] = {
        "batch_param": str(batch_param),
        "evaluated_values_count": len(candidates),
        "stability_rule": "extinction_rate asc, avg_final_population desc, avg_max_generation desc",
        "most_stable": {
            "winners": _sorted_unique_values(stable_candidates),
            "tie": len(_sorted_unique_values(stable_candidates)) > 1,
            "extinction_rate": lowest_ext_value,
            "avg_final_population": stable_best_pop,
            "avg_max_generation": stable_best_gen,
        },
        "best_avg_max_generation": {
            "winners": _sorted_unique_values(best_gen_candidates),
            "tie": len(_sorted_unique_values(best_gen_candidates)) > 1,
            "avg_max_generation": best_gen_value,
        },
        "best_avg_final_population": {
            "winners": _sorted_unique_values(best_pop_candidates),
            "tie": len(_sorted_unique_values(best_pop_candidates)) > 1,
            "avg_final_population": best_pop_value,
        },
        "lowest_extinction_rate": {
            "winners": _sorted_unique_values(lowest_ext_candidates),
            "tie": len(_sorted_unique_values(lowest_ext_candidates)) > 1,
            "extinction_rate": lowest_ext_value,
        },
    }

    if is_memory_param:
        summary["memory_comparative"] = _build_memory_comparative(memory_candidates)

    return summary


def format_batch_comparative_summary(summary: Dict[str, object]) -> str:
    batch_param = str(summary.get("batch_param", "param"))
    evaluated = int(summary.get("evaluated_values_count", 0))

    if evaluated <= 0:
        return "batch_comparatif: n/a"

    stable_raw = summary.get("most_stable")
    best_gen_raw = summary.get("best_avg_max_generation")
    best_pop_raw = summary.get("best_avg_final_population")
    lowest_ext_raw = summary.get("lowest_extinction_rate")

    stable = stable_raw if isinstance(stable_raw, dict) else _empty_metric_result()
    best_gen = best_gen_raw if isinstance(best_gen_raw, dict) else _empty_metric_result()
    best_pop = best_pop_raw if isinstance(best_pop_raw, dict) else _empty_metric_result()
    lowest_ext = lowest_ext_raw if isinstance(lowest_ext_raw, dict) else _empty_metric_result()

    lines = [
        "batch_comparatif:",
        "plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
            label=_winner_label(batch_param, stable.get("winners")),
            ext=float(stable.get("extinction_rate", 0.0)),
            pop=float(stable.get("avg_final_population", 0.0)),
            gen=float(stable.get("avg_max_generation", 0.0)),
        ),
        "meilleure_gen_max_moy: {label} (gen_max_moy={gen:.2f})".format(
            label=_winner_label(batch_param, best_gen.get("winners")),
            gen=float(best_gen.get("avg_max_generation", 0.0)),
        ),
        "meilleure_pop_finale_moy: {label} (pop_finale_moy={pop:.2f})".format(
            label=_winner_label(batch_param, best_pop.get("winners")),
            pop=float(best_pop.get("avg_final_population", 0.0)),
        ),
        "plus_faible_taux_extinction: {label} (taux_ext={ext:.2f})".format(
            label=_winner_label(batch_param, lowest_ext.get("winners")),
            ext=float(lowest_ext.get("extinction_rate", 0.0)),
        ),
    ]

    memory_raw = summary.get("memory_comparative")
    if isinstance(memory_raw, dict):
        lines.extend(_format_memory_comparative(batch_param, memory_raw))

    return "\n".join(lines)


def _format_memory_comparative(batch_param: str, memory_summary: Dict[str, object]) -> list[str]:
    lines = ["memoire_batch:"]

    if not bool(memory_summary.get("available", False)):
        note = str(memory_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_memoire: n/a ({note})")
        return lines

    food_usage = _read_metric_result(memory_summary.get("best_food_memory_usage"))
    danger_usage = _read_metric_result(memory_summary.get("best_danger_memory_usage"))
    food_effect = _read_metric_result(memory_summary.get("best_food_memory_effect"))
    danger_effect = _read_metric_result(memory_summary.get("best_danger_memory_effect"))

    lines.append(
        "usage_memoire_utile_max: {label} (usage_moy={value:.2f})".format(
            label=_winner_label(batch_param, food_usage.get("winners")),
            value=float(food_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_memoire_dangereuse_max: {label} (usage_moy={value:.2f})".format(
            label=_winner_label(batch_param, danger_usage.get("winners")),
            value=float(danger_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_memoire_utile_max: {label} (effet_moy={value:.2f})".format(
            label=_winner_label(batch_param, food_effect.get("winners")),
            value=float(food_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_memoire_dangereuse_max: {label} (effet_moy={value:.2f})".format(
            label=_winner_label(batch_param, danger_effect.get("winners")),
            value=float(danger_effect.get("value", 0.0)),
        )
    )

    return lines


def _build_memory_comparative(memory_candidates: list[Dict[str, float]]) -> Dict[str, object]:
    if len(memory_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact memoire",
            "best_food_memory_usage": _insufficient_metric_result(),
            "best_danger_memory_usage": _insufficient_metric_result(),
            "best_food_memory_effect": _insufficient_metric_result(),
            "best_danger_memory_effect": _insufficient_metric_result(),
        }

    return {
        "available": True,
        "best_food_memory_usage": _build_peak_metric(memory_candidates, "food_usage_total"),
        "best_danger_memory_usage": _build_peak_metric(memory_candidates, "danger_usage_total"),
        "best_food_memory_effect": _build_peak_metric(memory_candidates, "food_effect_avg_distance"),
        "best_danger_memory_effect": _build_peak_metric(memory_candidates, "danger_effect_avg_distance"),
    }


def _build_peak_metric(candidates: list[Dict[str, float]], field: str) -> Dict[str, object]:
    best_value = max(candidate[field] for candidate in candidates)
    winners = [candidate for candidate in candidates if _is_close(candidate[field], best_value)]
    winner_values = _sorted_unique_values(winners)

    return {
        "winners": winner_values,
        "tie": len(winner_values) > 1,
        "value": best_value,
        "insufficient": False,
    }


def _insufficient_metric_result() -> Dict[str, object]:
    return {
        "winners": [],
        "tie": False,
        "value": 0.0,
        "insufficient": True,
    }


def _read_memory_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_memory_raw = summary_raw.get("avg_memory_impact")
    if not isinstance(avg_memory_raw, dict):
        return None

    required = (
        "food_usage_total",
        "danger_usage_total",
        "food_effect_avg_distance",
        "danger_effect_avg_distance",
    )
    if any(key not in avg_memory_raw for key in required):
        return None

    return {
        "food_usage_total": float(avg_memory_raw.get("food_usage_total", 0.0)),
        "danger_usage_total": float(avg_memory_raw.get("danger_usage_total", 0.0)),
        "food_effect_avg_distance": float(avg_memory_raw.get("food_effect_avg_distance", 0.0)),
        "danger_effect_avg_distance": float(avg_memory_raw.get("danger_effect_avg_distance", 0.0)),
    }


def _read_metric_result(raw: object) -> Dict[str, object]:
    if isinstance(raw, dict):
        return raw
    return _insufficient_metric_result()


def _winner_label(batch_param: str, winners_raw: object) -> str:
    winners = _read_winner_values(winners_raw)
    if len(winners) == 0:
        return "n/a"

    if len(winners) == 1:
        return f"{batch_param}={_format_value(winners[0])}"

    joined = ",".join(_format_value(value) for value in winners)
    return f"egalite[{batch_param}={joined}]"


def _sorted_unique_values(candidates: Iterable[Dict[str, float]]) -> list[float]:
    values = {float(candidate["value"]) for candidate in candidates}
    return sorted(values)


def _read_winner_values(raw: object) -> list[float]:
    if not isinstance(raw, list):
        return []
    return [float(value) for value in raw]


def _format_value(value: float) -> str:
    if float(value).is_integer():
        return f"{value:.1f}"
    return f"{value:.6g}"


def _empty_metric_result() -> Dict[str, object]:
    return {
        "winners": [],
        "tie": False,
    }


def _is_close(a: float, b: float, tolerance: float = 1e-9) -> bool:
    return abs(a - b) <= tolerance
