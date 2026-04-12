from __future__ import annotations

from typing import Dict, Iterable


def build_batch_comparative_summary(
    batch_param: str,
    scenarios: Iterable[Dict[str, object]],
) -> Dict[str, object]:
    candidates: list[Dict[str, float]] = []

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue

        summary_raw = scenario.get("multi_run_summary")
        if not isinstance(summary_raw, dict):
            continue

        candidates.append(
            {
                "value": float(scenario.get("parameter_value", 0.0)),
                "extinction_rate": float(summary_raw.get("extinction_rate", 0.0)),
                "avg_max_generation": float(summary_raw.get("avg_max_generation", 0.0)),
                "avg_final_population": float(summary_raw.get("avg_final_population", 0.0)),
            }
        )

    if len(candidates) == 0:
        return {
            "batch_param": str(batch_param),
            "evaluated_values_count": 0,
            "stability_rule": "extinction_rate asc, avg_final_population desc, avg_max_generation desc",
            "most_stable": _empty_metric_result(),
            "best_avg_max_generation": _empty_metric_result(),
            "best_avg_final_population": _empty_metric_result(),
            "lowest_extinction_rate": _empty_metric_result(),
        }

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

    return {
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

    return "\n".join(lines)


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
