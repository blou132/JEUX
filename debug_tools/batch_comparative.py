from __future__ import annotations

from typing import Dict, Iterable


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

_ENERGY_TRAIT_BATCH_PARAMS = {
    "energy_drain_rate",
    "reproduction_cost",
    "reproduction_threshold",
    "reproduction_min_age",
    "mutation_variation",
}

_TRAIT_RELATED_BATCH_PARAMS = _MEMORY_BATCH_PARAMS | _SOCIAL_BATCH_PARAMS


def build_batch_comparative_summary(
    batch_param: str,
    scenarios: Iterable[Dict[str, object]],
) -> Dict[str, object]:
    candidates: list[Dict[str, float]] = []
    memory_candidates: list[Dict[str, float]] = []
    social_candidates: list[Dict[str, float]] = []
    energy_candidates: list[Dict[str, float]] = []
    trait_candidates: list[Dict[str, float]] = []
    behavior_persistence_candidates: list[Dict[str, float]] = []
    perception_candidates: list[Dict[str, float]] = []
    risk_candidates: list[Dict[str, float]] = []
    exploration_candidates: list[Dict[str, float]] = []
    density_preference_candidates: list[Dict[str, float]] = []
    mobility_candidates: list[Dict[str, float]] = []
    longevity_candidates: list[Dict[str, float]] = []
    environmental_candidates: list[Dict[str, float]] = []
    reproduction_timing_candidates: list[Dict[str, float]] = []
    stress_candidates: list[Dict[str, float]] = []
    hunger_candidates: list[Dict[str, float]] = []

    is_memory_param = batch_param in _MEMORY_BATCH_PARAMS
    is_social_param = batch_param in _SOCIAL_BATCH_PARAMS
    is_energy_param = batch_param in _ENERGY_TRAIT_BATCH_PARAMS
    is_trait_related_param = batch_param in _TRAIT_RELATED_BATCH_PARAMS

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
            if memory_metrics is not None:
                memory_candidates.append({"value": value, **memory_metrics})

        if is_social_param:
            social_metrics = _read_social_metrics(summary_raw)
            if social_metrics is not None:
                social_candidates.append({"value": value, **social_metrics})

        if is_energy_param:
            energy_metrics = _read_energy_metrics(summary_raw)
            if energy_metrics is not None:
                energy_candidates.append({"value": value, **energy_metrics})

        if is_trait_related_param:
            trait_metrics = _read_trait_metrics(summary_raw)
            if trait_metrics is not None:
                trait_candidates.append({"value": value, **trait_metrics})

        behavior_persistence_metrics = _read_behavior_persistence_metrics(summary_raw)
        if behavior_persistence_metrics is not None:
            behavior_persistence_candidates.append({"value": value, **behavior_persistence_metrics})

        perception_metrics = _read_perception_metrics(summary_raw)
        if perception_metrics is not None:
            perception_candidates.append({"value": value, **perception_metrics})

        risk_metrics = _read_risk_metrics(summary_raw)
        if risk_metrics is not None:
            risk_candidates.append({"value": value, **risk_metrics})

        exploration_metrics = _read_exploration_metrics(summary_raw)
        if exploration_metrics is not None:
            exploration_candidates.append({"value": value, **exploration_metrics})

        density_preference_metrics = _read_density_preference_metrics(summary_raw)
        if density_preference_metrics is not None:
            density_preference_candidates.append({"value": value, **density_preference_metrics})

        mobility_metrics = _read_mobility_metrics(summary_raw)
        if mobility_metrics is not None:
            mobility_candidates.append({"value": value, **mobility_metrics})

        longevity_metrics = _read_longevity_metrics(summary_raw)
        if longevity_metrics is not None:
            longevity_candidates.append({"value": value, **longevity_metrics})

        environmental_metrics = _read_environmental_metrics(summary_raw)
        if environmental_metrics is not None:
            environmental_candidates.append({"value": value, **environmental_metrics})

        reproduction_timing_metrics = _read_reproduction_timing_metrics(summary_raw)
        if reproduction_timing_metrics is not None:
            reproduction_timing_candidates.append({"value": value, **reproduction_timing_metrics})

        stress_metrics = _read_stress_metrics(summary_raw)
        if stress_metrics is not None:
            stress_candidates.append({"value": value, **stress_metrics})

        hunger_metrics = _read_hunger_metrics(summary_raw)
        if hunger_metrics is not None:
            hunger_candidates.append({"value": value, **hunger_metrics})

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
        if is_social_param:
            empty["social_comparative"] = _build_social_comparative(social_candidates)
        if is_energy_param:
            empty["energy_comparative"] = _build_energy_comparative(
                energy_candidates,
                stable_metric=None,
            )
        if is_trait_related_param:
            empty["trait_comparative"] = _build_trait_comparative(
                trait_candidates,
                stable_metric=None,
            )
        empty["behavior_persistence_comparative"] = _build_behavior_persistence_comparative(
            behavior_persistence_candidates,
            stable_metric=None,
        )
        empty["perception_comparative"] = _build_perception_comparative(
            perception_candidates,
            stable_metric=None,
        )
        empty["risk_comparative"] = _build_risk_comparative(
            risk_candidates,
            stable_metric=None,
        )
        empty["exploration_comparative"] = _build_exploration_comparative(
            exploration_candidates,
            stable_metric=None,
        )
        empty["density_preference_comparative"] = _build_density_preference_comparative(
            density_preference_candidates,
            stable_metric=None,
        )
        empty["mobility_comparative"] = _build_mobility_comparative(
            mobility_candidates,
            stable_metric=None,
        )
        empty["longevity_comparative"] = _build_longevity_comparative(
            longevity_candidates,
            stable_metric=None,
        )
        empty["environmental_comparative"] = _build_environmental_comparative(
            environmental_candidates,
            stable_metric=None,
        )
        empty["reproduction_timing_comparative"] = _build_reproduction_timing_comparative(
            reproduction_timing_candidates,
            stable_metric=None,
        )
        empty["stress_comparative"] = _build_stress_comparative(
            stress_candidates,
            stable_metric=None,
        )
        empty["hunger_comparative"] = _build_hunger_comparative(
            hunger_candidates,
            stable_metric=None,
        )
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

    stable_winners = _sorted_unique_values(stable_candidates)
    summary: Dict[str, object] = {
        "batch_param": str(batch_param),
        "evaluated_values_count": len(candidates),
        "stability_rule": "extinction_rate asc, avg_final_population desc, avg_max_generation desc",
        "most_stable": {
            "winners": stable_winners,
            "tie": len(stable_winners) > 1,
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
    if is_social_param:
        summary["social_comparative"] = _build_social_comparative(social_candidates)
    if is_energy_param:
        summary["energy_comparative"] = _build_energy_comparative(
            energy_candidates,
            stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
        )
    if is_trait_related_param:
        summary["trait_comparative"] = _build_trait_comparative(
            trait_candidates,
            stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
        )
    summary["behavior_persistence_comparative"] = _build_behavior_persistence_comparative(
        behavior_persistence_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["perception_comparative"] = _build_perception_comparative(
        perception_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["risk_comparative"] = _build_risk_comparative(
        risk_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["exploration_comparative"] = _build_exploration_comparative(
        exploration_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["density_preference_comparative"] = _build_density_preference_comparative(
        density_preference_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["mobility_comparative"] = _build_mobility_comparative(
        mobility_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["longevity_comparative"] = _build_longevity_comparative(
        longevity_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["environmental_comparative"] = _build_environmental_comparative(
        environmental_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["reproduction_timing_comparative"] = _build_reproduction_timing_comparative(
        reproduction_timing_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["stress_comparative"] = _build_stress_comparative(
        stress_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )
    summary["hunger_comparative"] = _build_hunger_comparative(
        hunger_candidates,
        stable_metric=summary.get("most_stable") if isinstance(summary.get("most_stable"), dict) else None,
    )

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

    social_raw = summary.get("social_comparative")
    if isinstance(social_raw, dict):
        lines.extend(_format_social_comparative(batch_param, social_raw))

    energy_raw = summary.get("energy_comparative")
    if isinstance(energy_raw, dict):
        lines.extend(_format_energy_comparative(batch_param, energy_raw))

    trait_raw = summary.get("trait_comparative")
    if isinstance(trait_raw, dict):
        lines.extend(_format_trait_comparative(batch_param, trait_raw))

    behavior_persistence_raw = summary.get("behavior_persistence_comparative")
    if isinstance(behavior_persistence_raw, dict):
        lines.extend(_format_behavior_persistence_comparative(batch_param, behavior_persistence_raw))

    perception_raw = summary.get("perception_comparative")
    if isinstance(perception_raw, dict):
        lines.extend(_format_perception_comparative(batch_param, perception_raw))

    risk_raw = summary.get("risk_comparative")
    if isinstance(risk_raw, dict):
        lines.extend(_format_risk_comparative(batch_param, risk_raw))

    exploration_raw = summary.get("exploration_comparative")
    if isinstance(exploration_raw, dict):
        lines.extend(_format_exploration_comparative(batch_param, exploration_raw))

    density_preference_raw = summary.get("density_preference_comparative")
    if isinstance(density_preference_raw, dict):
        lines.extend(_format_density_preference_comparative(batch_param, density_preference_raw))

    mobility_raw = summary.get("mobility_comparative")
    if isinstance(mobility_raw, dict):
        lines.extend(_format_mobility_comparative(batch_param, mobility_raw))

    longevity_raw = summary.get("longevity_comparative")
    if isinstance(longevity_raw, dict):
        lines.extend(_format_longevity_comparative(batch_param, longevity_raw))

    environmental_raw = summary.get("environmental_comparative")
    if isinstance(environmental_raw, dict):
        lines.extend(_format_environmental_comparative(batch_param, environmental_raw))

    reproduction_timing_raw = summary.get("reproduction_timing_comparative")
    if isinstance(reproduction_timing_raw, dict):
        lines.extend(_format_reproduction_timing_comparative(batch_param, reproduction_timing_raw))

    stress_raw = summary.get("stress_comparative")
    if isinstance(stress_raw, dict):
        lines.extend(_format_stress_comparative(batch_param, stress_raw))

    hunger_raw = summary.get("hunger_comparative")
    if isinstance(hunger_raw, dict):
        lines.extend(_format_hunger_comparative(batch_param, hunger_raw))

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


def _format_social_comparative(batch_param: str, social_summary: Dict[str, object]) -> list[str]:
    lines = ["social_batch:"]

    if not bool(social_summary.get("available", False)):
        note = str(social_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_sociales: n/a ({note})")
        return lines

    follow_usage = _read_metric_result(social_summary.get("best_social_follow_usage"))
    flee_boost_usage = _read_metric_result(social_summary.get("best_social_flee_boost_usage"))
    influenced_share = _read_metric_result(social_summary.get("best_social_influenced_share"))
    flee_multiplier = _read_metric_result(social_summary.get("best_social_flee_multiplier_effect"))

    lines.append(
        "usage_suivi_social_max: {label} (usage_moy={value:.2f})".format(
            label=_winner_label(batch_param, follow_usage.get("winners")),
            value=float(follow_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_boost_fuite_social_max: {label} (usage_moy={value:.2f})".format(
            label=_winner_label(batch_param, flee_boost_usage.get("winners")),
            value=float(flee_boost_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "part_creatures_influencees_max: {label} (part_moy={value:.2f})".format(
            label=_winner_label(batch_param, influenced_share.get("winners")),
            value=float(influenced_share.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_multiplicateur_fuite_max: {label} (multiplicateur_moy={value:.2f})".format(
            label=_winner_label(batch_param, flee_multiplier.get("winners")),
            value=float(flee_multiplier.get("value", 0.0)),
        )
    )

    return lines


def _build_social_comparative(social_candidates: list[Dict[str, float]]) -> Dict[str, object]:
    if len(social_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact social",
            "best_social_follow_usage": _insufficient_metric_result(),
            "best_social_flee_boost_usage": _insufficient_metric_result(),
            "best_social_influenced_share": _insufficient_metric_result(),
            "best_social_flee_multiplier_effect": _insufficient_metric_result(),
        }

    return {
        "available": True,
        "best_social_follow_usage": _build_peak_metric(social_candidates, "follow_usage_per_tick"),
        "best_social_flee_boost_usage": _build_peak_metric(social_candidates, "flee_boost_usage_per_tick"),
        "best_social_influenced_share": _build_peak_metric(social_candidates, "influenced_share_last_tick"),
        "best_social_flee_multiplier_effect": _build_peak_metric(social_candidates, "flee_multiplier_avg_total"),
    }


def _format_energy_comparative(batch_param: str, energy_summary: Dict[str, object]) -> list[str]:
    lines = ["energie_batch:"]

    if not bool(energy_summary.get("available", False)):
        note = str(energy_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_energie: n/a ({note})")
        return lines

    drain_effect = _read_metric_result(energy_summary.get("best_energy_drain_effect"))
    repro_effect = _read_metric_result(energy_summary.get("best_reproduction_cost_effect"))
    dispersion = _read_metric_result(energy_summary.get("best_energy_trait_dispersion"))
    stable_config = _read_metric_result(energy_summary.get("most_stable_config"))

    lines.append(
        "effet_drain_energie_max: {label} (effet_moy={value:.3f})".format(
            label=_winner_label(batch_param, drain_effect.get("winners")),
            value=float(drain_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_cout_reproduction_max: {label} (effet_moy={value:.3f})".format(
            label=_winner_label(batch_param, repro_effect.get("winners")),
            value=float(repro_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_energie_max: {label} (disp_moy={value:.3f})".format(
            label=_winner_label(batch_param, dispersion.get("winners")),
            value=float(dispersion.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    lines.append(
        "note_energie: effet_drain=abs(drain_mult_obs-1) effet_repro=abs(repro_mult_obs-1) dispersion=(std_ee+std_er)/2"
    )
    return lines


def _build_energy_comparative(
    energy_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(energy_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact energetique",
            "best_energy_drain_effect": _insufficient_metric_result(),
            "best_reproduction_cost_effect": _insufficient_metric_result(),
            "best_energy_trait_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    return {
        "available": True,
        "best_energy_drain_effect": _build_peak_metric(energy_candidates, "energy_drain_effect_strength"),
        "best_reproduction_cost_effect": _build_peak_metric(
            energy_candidates,
            "reproduction_cost_effect_strength",
        ),
        "best_energy_trait_dispersion": _build_peak_metric(energy_candidates, "energy_trait_dispersion"),
        "most_stable_config": stable_result,
    }


def _format_trait_comparative(batch_param: str, trait_summary: Dict[str, object]) -> list[str]:
    lines = ["traits_batch:"]

    if not bool(trait_summary.get("available", False)):
        note = str(trait_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_traits: n/a ({note})")
        return lines

    memory_bias = _read_metric_result(trait_summary.get("best_memory_usage_bias"))
    social_bias = _read_metric_result(trait_summary.get("best_social_usage_bias"))
    dispersion = _read_metric_result(trait_summary.get("best_trait_dispersion"))
    stable_config = _read_metric_result(trait_summary.get("most_stable_config"))

    lines.append(
        "bias_usage_memoire_max: {label} (bias_moy={value:+.3f})".format(
            label=_winner_label(batch_param, memory_bias.get("winners")),
            value=float(memory_bias.get("value", 0.0)),
        )
    )
    lines.append(
        "bias_usage_social_max: {label} (bias_moy={value:+.3f})".format(
            label=_winner_label(batch_param, social_bias.get("winners")),
            value=float(social_bias.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_traits_max: {label} (disp_moy={value:.3f})".format(
            label=_winner_label(batch_param, dispersion.get("winners")),
            value=float(dispersion.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    lines.append(
        "note_traits: biais_memoire=(bias_food+bias_danger)/2 biais_social=(bias_suivi+bias_fuite)/2 dispersion=(std_mem+std_soc)/2"
    )
    return lines


def _build_trait_comparative(
    trait_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(trait_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact des biais individuels",
            "best_memory_usage_bias": _insufficient_metric_result(),
            "best_social_usage_bias": _insufficient_metric_result(),
            "best_trait_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    return {
        "available": True,
        "best_memory_usage_bias": _build_peak_metric(trait_candidates, "memory_usage_bias"),
        "best_social_usage_bias": _build_peak_metric(trait_candidates, "social_usage_bias"),
        "best_trait_dispersion": _build_peak_metric(trait_candidates, "trait_dispersion"),
        "most_stable_config": stable_result,
    }


def _format_behavior_persistence_comparative(
    batch_param: str,
    behavior_persistence_summary: Dict[str, object],
) -> list[str]:
    lines = ["behavior_persistence_batch:"]

    if not bool(behavior_persistence_summary.get("available", False)):
        note = str(behavior_persistence_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_behavior_persistence: n/a ({note})")
        return lines

    switches_prevented = _read_metric_result(
        behavior_persistence_summary.get("best_switches_prevented")
    )
    switch_rate = _read_metric_result(behavior_persistence_summary.get("lowest_switch_rate"))
    prevented_rate = _read_metric_result(behavior_persistence_summary.get("best_prevented_rate"))
    stable_config = _read_metric_result(behavior_persistence_summary.get("most_stable_config"))

    lines.append(
        "switchs_evites_max: {label} (switchs_evites_moy={value:.2f})".format(
            label=_winner_label(batch_param, switches_prevented.get("winners")),
            value=float(switches_prevented.get("value", 0.0)),
        )
    )
    lines.append(
        "taux_switch_min: {label} (taux_moy={value:.3f})".format(
            label=_winner_label(batch_param, switch_rate.get("winners")),
            value=float(switch_rate.get("value", 0.0)),
        )
    )
    lines.append(
        "taux_blocage_utile_max: {label} (taux_moy={value:.3f})".format(
            label=_winner_label(batch_param, prevented_rate.get("winners")),
            value=float(prevented_rate.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    oscillation_note = str(behavior_persistence_summary.get("oscillation_note", "")).strip()
    if oscillation_note:
        lines.append(f"note_behavior_persistence: {oscillation_note}")
    else:
        lines.append(
            "note_behavior_persistence: switchs_evites=events evites, taux_switch=switch/events, taux_blocage=evites/events"
        )
    return lines


def _build_behavior_persistence_comparative(
    behavior_persistence_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(behavior_persistence_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact behavior_persistence",
            "best_switches_prevented": _insufficient_metric_result(),
            "lowest_switch_rate": _insufficient_metric_result(),
            "best_prevented_rate": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "oscillation_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    oscillation_signal_max = max(candidate["oscillation_events_total"] for candidate in behavior_persistence_candidates)
    oscillation_note = ""
    if oscillation_signal_max <= 0.0:
        oscillation_note = (
            "oscillations search_food/wander absentes: interpretation limitee (taux et switchs evites peu representatifs)"
        )

    return {
        "available": True,
        "best_switches_prevented": _build_peak_metric(
            behavior_persistence_candidates,
            "switches_prevented_total",
        ),
        "lowest_switch_rate": _build_low_metric(
            behavior_persistence_candidates,
            "switch_rate",
        ),
        "best_prevented_rate": _build_peak_metric(
            behavior_persistence_candidates,
            "prevented_rate",
        ),
        "most_stable_config": stable_result,
        "oscillation_note": oscillation_note,
    }


def _format_perception_comparative(batch_param: str, perception_summary: Dict[str, object]) -> list[str]:
    lines = ["perception_batch:"]

    if not bool(perception_summary.get("available", False)):
        note = str(perception_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_perception: n/a ({note})")
        return lines

    food_usage = _read_metric_result(perception_summary.get("best_food_perception_usage"))
    threat_usage = _read_metric_result(perception_summary.get("best_threat_perception_usage"))
    dispersion = _read_metric_result(perception_summary.get("best_perception_dispersion"))
    stable_config = _read_metric_result(perception_summary.get("most_stable_config"))

    lines.append(
        "usage_food_perception_max: {label} (bias_usage_moy={value:+.3f})".format(
            label=_winner_label(batch_param, food_usage.get("winners")),
            value=float(food_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_threat_perception_max: {label} (bias_usage_moy={value:+.3f})".format(
            label=_winner_label(batch_param, threat_usage.get("winners")),
            value=float(threat_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_perception_max: {label} (disp_moy={value:.3f})".format(
            label=_winner_label(batch_param, dispersion.get("winners")),
            value=float(dispersion.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    lines.append(
        "note_perception: usage_food=(bias_detection+bias_consommation)/2 usage_threat=bias_fuite dispersion=(std_food_perception+std_threat_perception)/2"
    )
    return lines


def _build_perception_comparative(
    perception_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(perception_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact perception",
            "best_food_perception_usage": _insufficient_metric_result(),
            "best_threat_perception_usage": _insufficient_metric_result(),
            "best_perception_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    return {
        "available": True,
        "best_food_perception_usage": _build_peak_metric(perception_candidates, "food_perception_usage_bias"),
        "best_threat_perception_usage": _build_peak_metric(perception_candidates, "threat_perception_usage_bias"),
        "best_perception_dispersion": _build_peak_metric(perception_candidates, "perception_dispersion"),
        "most_stable_config": stable_result,
    }


def _format_risk_comparative(batch_param: str, risk_summary: Dict[str, object]) -> list[str]:
    lines = ["risque_batch:"]

    if not bool(risk_summary.get("available", False)):
        note = str(risk_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_risque: n/a ({note})")
        return lines

    flee_bias = _read_metric_result(risk_summary.get("best_risk_flee_usage_bias"))
    borderline_effect = _read_metric_result(risk_summary.get("best_borderline_risk_effect"))
    risk_dispersion = _read_metric_result(risk_summary.get("best_risk_dispersion"))
    borderline_flee_rate = _read_metric_result(risk_summary.get("best_borderline_flee_rate"))
    stable_config = _read_metric_result(risk_summary.get("most_stable_config"))

    lines.append(
        "usage_fuite_risque_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, flee_bias.get("winners")),
            value=float(flee_bias.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_borderline_risque_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, borderline_effect.get("winners")),
            value=float(borderline_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_risque_max: {label} (rk_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, risk_dispersion.get("winners")),
            value=float(risk_dispersion.get("value", 0.0)),
        )
    )
    lines.append(
        "taux_fuite_borderline_max: {label} (taux_moy={value:.3f})".format(
            label=_winner_label(batch_param, borderline_flee_rate.get("winners")),
            value=float(borderline_flee_rate.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    borderline_note = str(risk_summary.get("borderline_note", "")).strip()
    if borderline_note:
        lines.append(f"note_risque: {borderline_note}")
    else:
        lines.append(
            "note_risque: impact_abs=abs(bias_rk_fuite) et abs(rk_border_bias), dispersion=rk_sigma, interpretation_borderline via taux_fuite_borderline"
        )
    return lines


def _build_risk_comparative(
    risk_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(risk_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact risk_taking",
            "best_risk_flee_usage_bias": _insufficient_metric_result(),
            "best_borderline_risk_effect": _insufficient_metric_result(),
            "best_risk_dispersion": _insufficient_metric_result(),
            "best_borderline_flee_rate": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "borderline_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    borderline_signal_max = max(candidate["borderline_signal"] for candidate in risk_candidates)
    borderline_note = ""
    if borderline_signal_max <= 0.0:
        borderline_note = "cas borderline absents: interpretation limitee (taux_fuite_borderline non representatif)"

    return {
        "available": True,
        "best_risk_flee_usage_bias": _build_peak_metric(risk_candidates, "risk_flee_usage_bias_abs"),
        "best_borderline_risk_effect": _build_peak_metric(risk_candidates, "borderline_effect_abs"),
        "best_risk_dispersion": _build_peak_metric(risk_candidates, "risk_dispersion"),
        "best_borderline_flee_rate": _build_peak_metric(risk_candidates, "borderline_flee_rate"),
        "most_stable_config": stable_result,
        "borderline_note": borderline_note,
    }



def _format_exploration_comparative(batch_param: str, exploration_summary: Dict[str, object]) -> list[str]:
    lines = ["exploration_bias_batch:"]

    if not bool(exploration_summary.get("available", False)):
        note = str(exploration_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_exploration_bias: n/a ({note})")
        return lines

    explore_usage = _read_metric_result(exploration_summary.get("best_explore_usage"))
    settle_usage = _read_metric_result(exploration_summary.get("best_settle_usage"))
    guided_usage = _read_metric_result(exploration_summary.get("best_guided_usage"))
    stable_config = _read_metric_result(exploration_summary.get("most_stable_config"))

    lines.append(
        "usage_explore_max: {label} (part_explore_moy={value:.3f})".format(
            label=_winner_label(batch_param, explore_usage.get("winners")),
            value=float(explore_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_settle_max: {label} (part_settle_moy={value:.3f})".format(
            label=_winner_label(batch_param, settle_usage.get("winners")),
            value=float(settle_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_guided_max: {label} (guided_moy={value:.2f})".format(
            label=_winner_label(batch_param, guided_usage.get("winners")),
            value=float(guided_usage.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    guided_note = str(exploration_summary.get("guided_note", "")).strip()
    if guided_note:
        lines.append(f"note_exploration_bias: {guided_note}")
    else:
        lines.append("note_exploration_bias: part_settle=1-part_explore, guided=guides moyens observes")

    return lines


def _build_exploration_comparative(
    exploration_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(exploration_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact exploration_bias",
            "best_explore_usage": _insufficient_metric_result(),
            "best_settle_usage": _insufficient_metric_result(),
            "best_guided_usage": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "guided_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    guided_signal_max = max(candidate["guided_usage_total"] for candidate in exploration_candidates)
    guided_note = ""
    if guided_signal_max <= 0.0:
        guided_note = (
            "usage guided nul: interpretation explore/settle limitee (aucun guidage observe)"
        )

    return {
        "available": True,
        "best_explore_usage": _build_peak_metric(exploration_candidates, "explore_usage_share"),
        "best_settle_usage": _build_peak_metric(exploration_candidates, "settle_usage_share"),
        "best_guided_usage": _build_peak_metric(exploration_candidates, "guided_usage_total"),
        "most_stable_config": stable_result,
        "guided_note": guided_note,
    }


def _format_density_preference_comparative(
    batch_param: str,
    density_preference_summary: Dict[str, object],
) -> list[str]:
    lines = ["density_preference_batch:"]

    if not bool(density_preference_summary.get("available", False)):
        note = str(density_preference_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_density_preference: n/a ({note})")
        return lines

    seek_usage = _read_metric_result(density_preference_summary.get("best_seek_usage"))
    avoid_usage = _read_metric_result(density_preference_summary.get("best_avoid_usage"))
    avoid_share = _read_metric_result(density_preference_summary.get("best_avoid_share"))
    stable_config = _read_metric_result(density_preference_summary.get("most_stable_config"))

    lines.append(
        "usage_seek_max: {label} (freq_seek_moy={value:.3f})".format(
            label=_winner_label(batch_param, seek_usage.get("winners")),
            value=float(seek_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "usage_avoid_max: {label} (freq_avoid_moy={value:.3f})".format(
            label=_winner_label(batch_param, avoid_usage.get("winners")),
            value=float(avoid_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "part_avoid_max: {label} (part_avoid_moy={value:.3f})".format(
            label=_winner_label(batch_param, avoid_share.get("winners")),
            value=float(avoid_share.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    usage_note = str(density_preference_summary.get("usage_note", "")).strip()
    if usage_note:
        lines.append(f"note_density_preference: {usage_note}")
    else:
        lines.append("note_density_preference: freq_* en usages moyens/tick, part_avoid en part moyenne des usages guides")

    return lines


def _build_density_preference_comparative(
    density_preference_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(density_preference_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact density_preference",
            "best_seek_usage": _insufficient_metric_result(),
            "best_avoid_usage": _insufficient_metric_result(),
            "best_avoid_share": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "usage_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    guided_signal_max = max(candidate["guided_usage_total"] for candidate in density_preference_candidates)
    usage_note = ""
    if guided_signal_max <= 0.0:
        usage_note = "usage seek/avoid nul: interpretation limitee (aucun guidage density_preference observe)"

    return {
        "available": True,
        "best_seek_usage": _build_peak_metric(density_preference_candidates, "seek_usage_per_tick"),
        "best_avoid_usage": _build_peak_metric(density_preference_candidates, "avoid_usage_per_tick"),
        "best_avoid_share": _build_peak_metric(density_preference_candidates, "avoid_usage_share"),
        "most_stable_config": stable_result,
        "usage_note": usage_note,
    }


def _format_mobility_comparative(
    batch_param: str,
    mobility_summary: Dict[str, object],
) -> list[str]:
    lines = ["mobility_efficiency_batch:"]

    if not bool(mobility_summary.get("available", False)):
        note = str(mobility_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_mobility_efficiency: n/a ({note})")
        return lines

    movement_distance = _read_metric_result(
        mobility_summary.get("best_movement_distance_observed")
    )
    movement_usage = _read_metric_result(
        mobility_summary.get("best_movement_usage_frequency")
    )
    mobility_dispersion = _read_metric_result(
        mobility_summary.get("best_mobility_dispersion")
    )
    stable_config = _read_metric_result(mobility_summary.get("most_stable_config"))

    lines.append(
        "distance_deplacement_observee_max: {label} (dist_moy={value:.3f})".format(
            label=_winner_label(batch_param, movement_distance.get("winners")),
            value=float(movement_distance.get("value", 0.0)),
        )
    )
    lines.append(
        "frequence_mouvement_utile_max: {label} (freq_moy={value:.3f})".format(
            label=_winner_label(batch_param, movement_usage.get("winners")),
            value=float(movement_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_mobilite_max: {label} (mo_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, mobility_dispersion.get("winners")),
            value=float(mobility_dispersion.get("value", 0.0)),
        )
    )

    ambiguity_labels: list[str] = []
    if bool(movement_distance.get("tie", False)):
        ambiguity_labels.append("distance_deplacement_observee")
    if bool(movement_usage.get("tie", False)):
        ambiguity_labels.append("frequence_mouvement_utile")
    if bool(mobility_dispersion.get("tie", False)):
        ambiguity_labels.append("dispersion_mobilite")

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )
        if bool(stable_config.get("tie", False)):
            ambiguity_labels.append("configuration_plus_stable")

    if len(ambiguity_labels) > 0:
        lines.append(f"ambiguite_mobility_efficiency: {', '.join(ambiguity_labels)}")

    mobility_note = str(mobility_summary.get("mobility_note", "")).strip()
    if mobility_note:
        lines.append(f"note_mobility_efficiency: {mobility_note}")
    else:
        lines.append(
            "note_mobility_efficiency: distance=movement_distance_observed, frequence=movement_usage_per_tick, dispersion=mobility_efficiency_std"
        )

    return lines


def _build_mobility_comparative(
    mobility_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(mobility_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact mobility_efficiency",
            "best_movement_distance_observed": _insufficient_metric_result(),
            "best_movement_usage_frequency": _insufficient_metric_result(),
            "best_mobility_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "mobility_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    movement_distance_signal = max(
        candidate["movement_distance_observed"] for candidate in mobility_candidates
    )
    movement_usage_signal = max(
        candidate["movement_usage_per_tick"] for candidate in mobility_candidates
    )
    mobility_note = ""
    if movement_distance_signal <= 0.0 and movement_usage_signal <= 0.0:
        mobility_note = (
            "mouvement non observe: interpretation limitee (distance/frequence nulles)"
        )
    elif movement_distance_signal <= 0.0:
        mobility_note = (
            "distance deplacement observee nulle: lecture distance mobility_efficiency limitee"
        )
    elif movement_usage_signal <= 0.0:
        mobility_note = (
            "frequence de mouvement nulle: lecture usage mobility_efficiency limitee"
        )

    return {
        "available": True,
        "best_movement_distance_observed": _build_peak_metric(
            mobility_candidates,
            "movement_distance_observed",
        ),
        "best_movement_usage_frequency": _build_peak_metric(
            mobility_candidates,
            "movement_usage_per_tick",
        ),
        "best_mobility_dispersion": _build_peak_metric(
            mobility_candidates,
            "mobility_dispersion",
        ),
        "most_stable_config": stable_result,
        "mobility_note": mobility_note,
    }


def _format_longevity_comparative(
    batch_param: str,
    longevity_summary: Dict[str, object],
) -> list[str]:
    lines = ["longevity_factor_batch:"]

    if not bool(longevity_summary.get("available", False)):
        note = str(longevity_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_longevity_factor: n/a ({note})")
        return lines

    age_wear_effect = _read_metric_result(longevity_summary.get("best_age_wear_effect"))
    age_wear_reduction = _read_metric_result(longevity_summary.get("best_age_wear_reduction"))
    longevity_dispersion = _read_metric_result(longevity_summary.get("best_longevity_dispersion"))
    stable_config = _read_metric_result(longevity_summary.get("most_stable_config"))

    lines.append(
        "effet_usure_age_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, age_wear_effect.get("winners")),
            value=float(age_wear_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "reduction_drain_age_max: {label} (reduction_moy={value:.3f})".format(
            label=_winner_label(batch_param, age_wear_reduction.get("winners")),
            value=float(age_wear_reduction.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_longevite_max: {label} (lg_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, longevity_dispersion.get("winners")),
            value=float(longevity_dispersion.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    longevity_note = str(longevity_summary.get("longevity_note", "")).strip()
    if longevity_note:
        lines.append(f"note_longevity_factor: {longevity_note}")
    else:
        lines.append(
            "note_longevity_factor: effet_usure=abs(age_wear_mult_obs-1), reduction=max(0,1-age_wear_mult_obs), dispersion=std_longevity_factor"
        )

    return lines


def _build_longevity_comparative(
    longevity_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(longevity_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact longevity_factor",
            "best_age_wear_effect": _insufficient_metric_result(),
            "best_age_wear_reduction": _insufficient_metric_result(),
            "best_longevity_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "longevity_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    age_wear_signal_max = max(candidate["age_wear_usage_per_tick"] for candidate in longevity_candidates)
    age_wear_reduction_max = max(candidate["age_wear_reduction_strength"] for candidate in longevity_candidates)
    longevity_note = ""
    if age_wear_signal_max <= 0.0:
        longevity_note = (
            "usure d'age non observee: interpretation limitee (effets longevity_factor non representatifs)"
        )
    elif age_wear_reduction_max <= 0.0:
        longevity_note = (
            "aucune reduction age_wear observee (age_wear_mult_obs >= 1 pour toutes les configurations)"
        )

    return {
        "available": True,
        "best_age_wear_effect": _build_peak_metric(longevity_candidates, "age_wear_effect_strength"),
        "best_age_wear_reduction": _build_peak_metric(longevity_candidates, "age_wear_reduction_strength"),
        "best_longevity_dispersion": _build_peak_metric(longevity_candidates, "longevity_dispersion"),
        "most_stable_config": stable_result,
        "longevity_note": longevity_note,
    }


def _format_environmental_comparative(
    batch_param: str,
    environmental_summary: Dict[str, object],
) -> list[str]:
    lines = ["environmental_tolerance_batch:"]

    if not bool(environmental_summary.get("available", False)):
        note = str(environmental_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_environmental_tolerance: n/a ({note})")
        return lines

    poor_effect = _read_metric_result(environmental_summary.get("best_poor_zone_effect"))
    rich_effect = _read_metric_result(environmental_summary.get("best_rich_zone_effect"))
    env_dispersion = _read_metric_result(environmental_summary.get("best_environmental_dispersion"))
    stable_config = _read_metric_result(environmental_summary.get("most_stable_config"))

    lines.append(
        "effet_zone_pauvre_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, poor_effect.get("winners")),
            value=float(poor_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "effet_zone_riche_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, rich_effect.get("winners")),
            value=float(rich_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_tolerance_env_max: {label} (env_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, env_dispersion.get("winners")),
            value=float(env_dispersion.get("value", 0.0)),
        )
    )

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )

    environmental_note = str(environmental_summary.get("environmental_note", "")).strip()
    if environmental_note:
        lines.append(f"note_environmental_tolerance: {environmental_note}")
    else:
        lines.append(
            "note_environmental_tolerance: effet_zone_*=abs(env_*_drain_bias), dispersion=std_environmental_tolerance"
        )

    return lines


def _build_environmental_comparative(
    environmental_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(environmental_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact environmental_tolerance",
            "best_poor_zone_effect": _insufficient_metric_result(),
            "best_rich_zone_effect": _insufficient_metric_result(),
            "best_environmental_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "environmental_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    poor_signal_max = max(candidate["poor_zone_usage_per_tick"] for candidate in environmental_candidates)
    rich_signal_max = max(candidate["rich_zone_usage_per_tick"] for candidate in environmental_candidates)
    environmental_note = ""
    if poor_signal_max <= 0.0 and rich_signal_max <= 0.0:
        environmental_note = (
            "drain par zone non observe: interpretation limitee (aucune mesure en zone pauvre/riche)"
        )
    elif poor_signal_max <= 0.0:
        environmental_note = "signal zone pauvre absent: effet pauvre possiblement non representatif"
    elif rich_signal_max <= 0.0:
        environmental_note = "signal zone riche absent: effet riche possiblement non representatif"

    return {
        "available": True,
        "best_poor_zone_effect": _build_peak_metric(environmental_candidates, "poor_zone_effect_strength"),
        "best_rich_zone_effect": _build_peak_metric(environmental_candidates, "rich_zone_effect_strength"),
        "best_environmental_dispersion": _build_peak_metric(
            environmental_candidates,
            "environmental_dispersion",
        ),
        "most_stable_config": stable_result,
        "environmental_note": environmental_note,
    }


def _format_reproduction_timing_comparative(
    batch_param: str,
    reproduction_timing_summary: Dict[str, object],
) -> list[str]:
    lines = ["reproduction_timing_batch:"]

    if not bool(reproduction_timing_summary.get("available", False)):
        note = str(reproduction_timing_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_reproduction_timing: n/a ({note})")
        return lines

    threshold_effect = _read_metric_result(
        reproduction_timing_summary.get("best_reproduction_timing_threshold_effect")
    )
    earlier_repro = _read_metric_result(
        reproduction_timing_summary.get("best_earlier_reproduction")
    )
    prudent_repro = _read_metric_result(
        reproduction_timing_summary.get("best_prudent_reproduction")
    )
    stable_config = _read_metric_result(reproduction_timing_summary.get("most_stable_config"))

    lines.append(
        "effet_seuil_reproductif_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, threshold_effect.get("winners")),
            value=float(threshold_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "reproduction_plus_precoce_max: {label} (effet_moy={value:.3f})".format(
            label=_winner_label(batch_param, earlier_repro.get("winners")),
            value=float(earlier_repro.get("value", 0.0)),
        )
    )
    lines.append(
        "reproduction_plus_prudente_max: {label} (effet_moy={value:.3f})".format(
            label=_winner_label(batch_param, prudent_repro.get("winners")),
            value=float(prudent_repro.get("value", 0.0)),
        )
    )

    ambiguity_labels: list[str] = []
    if bool(threshold_effect.get("tie", False)):
        ambiguity_labels.append("effet_seuil_reproductif")
    if bool(earlier_repro.get("tie", False)):
        ambiguity_labels.append("reproduction_plus_precoce")
    if bool(prudent_repro.get("tie", False)):
        ambiguity_labels.append("reproduction_plus_prudente")

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )
        if bool(stable_config.get("tie", False)):
            ambiguity_labels.append("configuration_plus_stable")

    if len(ambiguity_labels) > 0:
        lines.append(f"ambiguite_reproduction_timing: {', '.join(ambiguity_labels)}")

    reproduction_timing_note = str(reproduction_timing_summary.get("reproduction_timing_note", "")).strip()
    if reproduction_timing_note:
        lines.append(f"note_reproduction_timing: {reproduction_timing_note}")
    else:
        lines.append(
            "note_reproduction_timing: effet_seuil=abs(repro_timing_mult-1), precoce=max(0,1-repro_timing_mult), prudente=max(0,repro_timing_mult-1)"
        )

    return lines


def _build_reproduction_timing_comparative(
    reproduction_timing_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(reproduction_timing_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact reproduction_timing",
            "best_reproduction_timing_threshold_effect": _insufficient_metric_result(),
            "best_earlier_reproduction": _insufficient_metric_result(),
            "best_prudent_reproduction": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "reproduction_timing_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    earlier_signal_max = max(
        candidate["earlier_reproduction_strength"] for candidate in reproduction_timing_candidates
    )
    prudent_signal_max = max(
        candidate["prudent_reproduction_strength"] for candidate in reproduction_timing_candidates
    )
    reproduction_timing_note = ""
    if earlier_signal_max <= 0.0 and prudent_signal_max <= 0.0:
        reproduction_timing_note = (
            "multiplicateur de seuil neutre/non observe (repro_timing_mult ~= 1): lecture precoce/prudente limitee"
        )
    elif earlier_signal_max <= 0.0:
        reproduction_timing_note = (
            "aucune tendance reproduction plus precoce observee (repro_timing_mult < 1 non detecte)"
        )
    elif prudent_signal_max <= 0.0:
        reproduction_timing_note = (
            "aucune tendance reproduction plus prudente observee (repro_timing_mult > 1 non detecte)"
        )

    return {
        "available": True,
        "best_reproduction_timing_threshold_effect": _build_peak_metric(
            reproduction_timing_candidates,
            "threshold_effect_strength",
        ),
        "best_earlier_reproduction": _build_peak_metric(
            reproduction_timing_candidates,
            "earlier_reproduction_strength",
        ),
        "best_prudent_reproduction": _build_peak_metric(
            reproduction_timing_candidates,
            "prudent_reproduction_strength",
        ),
        "most_stable_config": stable_result,
        "reproduction_timing_note": reproduction_timing_note,
    }


def _format_stress_comparative(
    batch_param: str,
    stress_summary: Dict[str, object],
) -> list[str]:
    lines = ["stress_tolerance_batch:"]

    if not bool(stress_summary.get("available", False)):
        note = str(stress_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_stress_tolerance: n/a ({note})")
        return lines

    pressure_effect = _read_metric_result(stress_summary.get("best_stress_pressure_effect"))
    flee_modulation = _read_metric_result(stress_summary.get("best_stress_flee_modulation"))
    stress_dispersion = _read_metric_result(stress_summary.get("best_stress_dispersion"))
    stable_config = _read_metric_result(stress_summary.get("most_stable_config"))

    lines.append(
        "effet_sous_pression_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, pressure_effect.get("winners")),
            value=float(pressure_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "modulation_fuite_tendue_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, flee_modulation.get("winners")),
            value=float(flee_modulation.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_stress_tolerance_max: {label} (st_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, stress_dispersion.get("winners")),
            value=float(stress_dispersion.get("value", 0.0)),
        )
    )

    ambiguity_labels: list[str] = []
    if bool(pressure_effect.get("tie", False)):
        ambiguity_labels.append("effet_sous_pression")
    if bool(flee_modulation.get("tie", False)):
        ambiguity_labels.append("modulation_fuite_tendue")
    if bool(stress_dispersion.get("tie", False)):
        ambiguity_labels.append("dispersion_stress_tolerance")

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )
        if bool(stable_config.get("tie", False)):
            ambiguity_labels.append("configuration_plus_stable")

    if len(ambiguity_labels) > 0:
        lines.append(f"ambiguite_stress_tolerance: {', '.join(ambiguity_labels)}")

    stress_note = str(stress_summary.get("stress_note", "")).strip()
    if stress_note:
        lines.append(f"note_stress_tolerance: {stress_note}")
    else:
        lines.append(
            "note_stress_tolerance: effet_sous_pression=abs(stress_tolerance_pressure_mean-1), modulation_fuite=abs(stress_tolerance_pressure_flee_bias), dispersion=stress_tolerance_std"
        )

    return lines


def _build_stress_comparative(
    stress_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(stress_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact stress_tolerance",
            "best_stress_pressure_effect": _insufficient_metric_result(),
            "best_stress_flee_modulation": _insufficient_metric_result(),
            "best_stress_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "stress_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    pressure_signal_max = max(candidate["stress_pressure_events"] for candidate in stress_candidates)
    flee_signal_max = max(candidate["stress_pressure_flee_rate"] for candidate in stress_candidates)
    stress_note = ""
    if pressure_signal_max <= 0.0:
        stress_note = "aucun cas sous pression observe: interpretation stress_tolerance limitee"
    elif flee_signal_max <= 0.0:
        stress_note = "fuite sous pression non observee: modulation stress_tolerance possiblement non representative"

    return {
        "available": True,
        "best_stress_pressure_effect": _build_peak_metric(
            stress_candidates,
            "pressure_effect_strength",
        ),
        "best_stress_flee_modulation": _build_peak_metric(
            stress_candidates,
            "flee_modulation_strength",
        ),
        "best_stress_dispersion": _build_peak_metric(
            stress_candidates,
            "stress_dispersion",
        ),
        "most_stable_config": stable_result,
        "stress_note": stress_note,
    }


def _format_hunger_comparative(
    batch_param: str,
    hunger_summary: Dict[str, object],
) -> list[str]:
    lines = ["hunger_sensitivity_batch:"]

    if not bool(hunger_summary.get("available", False)):
        note = str(hunger_summary.get("note", "donnees insuffisantes"))
        lines.append(f"donnees_hunger_sensitivity: n/a ({note})")
        return lines

    threshold_effect = _read_metric_result(hunger_summary.get("best_hunger_threshold_effect"))
    earlier_search = _read_metric_result(hunger_summary.get("best_earlier_food_search"))
    later_search = _read_metric_result(hunger_summary.get("best_later_food_search"))
    search_usage = _read_metric_result(hunger_summary.get("best_hunger_search_frequency"))
    hunger_dispersion = _read_metric_result(hunger_summary.get("best_hunger_dispersion"))
    stable_config = _read_metric_result(hunger_summary.get("most_stable_config"))

    lines.append(
        "effet_seuil_faim_max: {label} (impact_abs_moy={value:.3f})".format(
            label=_winner_label(batch_param, threshold_effect.get("winners")),
            value=float(threshold_effect.get("value", 0.0)),
        )
    )
    lines.append(
        "recherche_plus_precoce_max: {label} (impact_moy={value:.3f})".format(
            label=_winner_label(batch_param, earlier_search.get("winners")),
            value=float(earlier_search.get("value", 0.0)),
        )
    )
    lines.append(
        "recherche_plus_tardive_max: {label} (impact_moy={value:.3f})".format(
            label=_winner_label(batch_param, later_search.get("winners")),
            value=float(later_search.get("value", 0.0)),
        )
    )
    lines.append(
        "frequence_recherche_faim_max: {label} (freq_moy={value:.3f})".format(
            label=_winner_label(batch_param, search_usage.get("winners")),
            value=float(search_usage.get("value", 0.0)),
        )
    )
    lines.append(
        "dispersion_hunger_sensitivity_max: {label} (hs_sigma_moy={value:.3f})".format(
            label=_winner_label(batch_param, hunger_dispersion.get("winners")),
            value=float(hunger_dispersion.get("value", 0.0)),
        )
    )

    ambiguity_labels: list[str] = []
    if bool(threshold_effect.get("tie", False)):
        ambiguity_labels.append("effet_seuil_faim")
    if bool(earlier_search.get("tie", False)):
        ambiguity_labels.append("recherche_plus_precoce")
    if bool(later_search.get("tie", False)):
        ambiguity_labels.append("recherche_plus_tardive")
    if bool(search_usage.get("tie", False)):
        ambiguity_labels.append("frequence_recherche_faim")
    if bool(hunger_dispersion.get("tie", False)):
        ambiguity_labels.append("dispersion_hunger_sensitivity")

    if bool(stable_config.get("insufficient", False)):
        lines.append("configuration_plus_stable: n/a")
    else:
        lines.append(
            "configuration_plus_stable: {label} (taux_ext={ext:.2f}, pop_finale_moy={pop:.2f}, gen_max_moy={gen:.2f})".format(
                label=_winner_label(batch_param, stable_config.get("winners")),
                ext=float(stable_config.get("extinction_rate", 0.0)),
                pop=float(stable_config.get("avg_final_population", 0.0)),
                gen=float(stable_config.get("avg_max_generation", 0.0)),
            )
        )
        if bool(stable_config.get("tie", False)):
            ambiguity_labels.append("configuration_plus_stable")

    if len(ambiguity_labels) > 0:
        lines.append(f"ambiguite_hunger_sensitivity: {', '.join(ambiguity_labels)}")

    hunger_note = str(hunger_summary.get("hunger_note", "")).strip()
    if hunger_note:
        lines.append(f"note_hunger_sensitivity: {hunger_note}")
    else:
        lines.append(
            "note_hunger_sensitivity: effet_seuil_faim=abs(hunger_sensitivity_search_bias), precoce=max(0,bias_hs_search), tardive=max(0,-bias_hs_search), freq=hunger_search_usage_per_tick, dispersion=hunger_sensitivity_std"
        )

    return lines


def _build_hunger_comparative(
    hunger_candidates: list[Dict[str, float]],
    stable_metric: Dict[str, object] | None,
) -> Dict[str, object]:
    if len(hunger_candidates) == 0:
        return {
            "available": False,
            "note": "donnees insuffisantes pour comparer l'impact hunger_sensitivity",
            "best_hunger_threshold_effect": _insufficient_metric_result(),
            "best_earlier_food_search": _insufficient_metric_result(),
            "best_later_food_search": _insufficient_metric_result(),
            "best_hunger_search_frequency": _insufficient_metric_result(),
            "best_hunger_dispersion": _insufficient_metric_result(),
            "most_stable_config": _insufficient_metric_result(),
            "hunger_note": "",
        }

    if stable_metric is None:
        stable_result = _insufficient_metric_result()
    else:
        stable_result = {
            "winners": _read_winner_values(stable_metric.get("winners")),
            "tie": bool(stable_metric.get("tie", False)),
            "value": 0.0,
            "insufficient": False,
            "extinction_rate": float(stable_metric.get("extinction_rate", 0.0)),
            "avg_final_population": float(stable_metric.get("avg_final_population", 0.0)),
            "avg_max_generation": float(stable_metric.get("avg_max_generation", 0.0)),
        }

    earlier_signal_max = max(candidate["earlier_food_search_strength"] for candidate in hunger_candidates)
    later_signal_max = max(candidate["later_food_search_strength"] for candidate in hunger_candidates)
    usage_signal_max = max(candidate["hunger_search_usage_per_tick"] for candidate in hunger_candidates)
    hunger_note = ""
    if earlier_signal_max <= 0.0 and later_signal_max <= 0.0:
        hunger_note = (
            "biais de recherche faim non differenciant observe (bias_hs_search ~= 0): lecture precoce/tardive limitee"
        )
    elif earlier_signal_max <= 0.0:
        hunger_note = (
            "aucune tendance recherche plus precoce observee (bias_hs_search > 0 non detecte)"
        )
    elif later_signal_max <= 0.0:
        hunger_note = (
            "aucune tendance recherche plus tardive observee (bias_hs_search < 0 non detecte)"
        )
    elif usage_signal_max <= 0.0:
        hunger_note = (
            "frequence de recherche faim nulle/non observee: interpretation usage hunger_sensitivity limitee"
        )

    return {
        "available": True,
        "best_hunger_threshold_effect": _build_peak_metric(
            hunger_candidates,
            "hunger_threshold_effect_strength",
        ),
        "best_earlier_food_search": _build_peak_metric(
            hunger_candidates,
            "earlier_food_search_strength",
        ),
        "best_later_food_search": _build_peak_metric(
            hunger_candidates,
            "later_food_search_strength",
        ),
        "best_hunger_search_frequency": _build_peak_metric(
            hunger_candidates,
            "hunger_search_usage_per_tick",
        ),
        "best_hunger_dispersion": _build_peak_metric(
            hunger_candidates,
            "hunger_dispersion",
        ),
        "most_stable_config": stable_result,
        "hunger_note": hunger_note,
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


def _build_low_metric(candidates: list[Dict[str, float]], field: str) -> Dict[str, object]:
    best_value = min(candidate[field] for candidate in candidates)
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


def _read_social_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_social_raw = summary_raw.get("avg_social_impact")
    if not isinstance(avg_social_raw, dict):
        return None

    required = (
        "follow_usage_per_tick",
        "flee_boost_usage_per_tick",
        "influenced_share_last_tick",
        "flee_multiplier_avg_total",
    )
    if any(key not in avg_social_raw for key in required):
        return None

    return {
        "follow_usage_per_tick": float(avg_social_raw.get("follow_usage_per_tick", 0.0)),
        "flee_boost_usage_per_tick": float(avg_social_raw.get("flee_boost_usage_per_tick", 0.0)),
        "influenced_share_last_tick": float(avg_social_raw.get("influenced_share_last_tick", 0.0)),
        "flee_multiplier_avg_total": float(avg_social_raw.get("flee_multiplier_avg_total", 1.0)),
    }


def _read_trait_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "memory_focus_food_bias",
        "memory_focus_danger_bias",
        "social_sensitivity_follow_bias",
        "social_sensitivity_flee_boost_bias",
        "memory_focus_std",
        "social_sensitivity_std",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    memory_food_bias = float(avg_trait_raw.get("memory_focus_food_bias", 0.0))
    memory_danger_bias = float(avg_trait_raw.get("memory_focus_danger_bias", 0.0))
    social_follow_bias = float(avg_trait_raw.get("social_sensitivity_follow_bias", 0.0))
    social_flee_bias = float(avg_trait_raw.get("social_sensitivity_flee_boost_bias", 0.0))
    memory_std = float(avg_trait_raw.get("memory_focus_std", 0.0))
    social_std = float(avg_trait_raw.get("social_sensitivity_std", 0.0))

    return {
        "memory_usage_bias": (memory_food_bias + memory_danger_bias) / 2.0,
        "social_usage_bias": (social_follow_bias + social_flee_bias) / 2.0,
        "trait_dispersion": (memory_std + social_std) / 2.0,
    }


def _read_behavior_persistence_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "search_wander_switches_prevented_total",
        "behavior_persistence_oscillation_switch_rate",
        "behavior_persistence_oscillation_prevented_rate",
        "search_wander_oscillation_events_total",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    return {
        "switches_prevented_total": float(avg_trait_raw.get("search_wander_switches_prevented_total", 0.0)),
        "switch_rate": float(avg_trait_raw.get("behavior_persistence_oscillation_switch_rate", 0.0)),
        "prevented_rate": float(avg_trait_raw.get("behavior_persistence_oscillation_prevented_rate", 0.0)),
        "oscillation_events_total": float(avg_trait_raw.get("search_wander_oscillation_events_total", 0.0)),
    }


def _read_energy_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "energy_drain_multiplier_observed",
        "reproduction_cost_multiplier_observed",
        "energy_efficiency_std",
        "exhaustion_resistance_std",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    drain_multiplier = float(avg_trait_raw.get("energy_drain_multiplier_observed", 1.0))
    reproduction_multiplier = float(avg_trait_raw.get("reproduction_cost_multiplier_observed", 1.0))
    energy_efficiency_std = float(avg_trait_raw.get("energy_efficiency_std", 0.0))
    exhaustion_resistance_std = float(avg_trait_raw.get("exhaustion_resistance_std", 0.0))

    return {
        "energy_drain_effect_strength": abs(drain_multiplier - 1.0),
        "reproduction_cost_effect_strength": abs(reproduction_multiplier - 1.0),
        "energy_trait_dispersion": (energy_efficiency_std + exhaustion_resistance_std) / 2.0,
    }


def _read_perception_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "food_perception_detection_bias",
        "food_perception_consumption_bias",
        "threat_perception_flee_bias",
        "food_perception_std",
        "threat_perception_std",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    food_detection_bias = float(avg_trait_raw.get("food_perception_detection_bias", 0.0))
    food_consumption_bias = float(avg_trait_raw.get("food_perception_consumption_bias", 0.0))
    threat_flee_bias = float(avg_trait_raw.get("threat_perception_flee_bias", 0.0))
    food_std = float(avg_trait_raw.get("food_perception_std", 0.0))
    threat_std = float(avg_trait_raw.get("threat_perception_std", 0.0))

    return {
        "food_perception_usage_bias": (food_detection_bias + food_consumption_bias) / 2.0,
        "threat_perception_usage_bias": threat_flee_bias,
        "perception_dispersion": (food_std + threat_std) / 2.0,
    }


def _read_risk_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "risk_taking_flee_bias",
        "risk_taking_std",
        "risk_taking_borderline_flee_bias",
        "borderline_threat_flee_rate",
        "borderline_threat_encounters",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    risk_flee_bias = float(avg_trait_raw.get("risk_taking_flee_bias", 0.0))
    risk_std = float(avg_trait_raw.get("risk_taking_std", 0.0))
    borderline_bias = float(avg_trait_raw.get("risk_taking_borderline_flee_bias", 0.0))
    borderline_flee_rate = float(avg_trait_raw.get("borderline_threat_flee_rate", 0.0))
    borderline_signal = float(avg_trait_raw.get("borderline_threat_encounters", 0.0))

    return {
        "risk_flee_usage_bias_abs": abs(risk_flee_bias),
        "risk_dispersion": risk_std,
        "borderline_effect_abs": abs(borderline_bias),
        "borderline_flee_rate": borderline_flee_rate,
        "borderline_signal": borderline_signal,
    }



def _read_exploration_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "exploration_bias_guided_total",
        "exploration_bias_explore_share",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    explore_share = float(avg_trait_raw.get("exploration_bias_explore_share", 0.0))
    guided_total = float(avg_trait_raw.get("exploration_bias_guided_total", 0.0))

    # Keep shares in [0, 1] for robust comparison in case of malformed payloads.
    explore_share = max(0.0, min(1.0, explore_share))
    settle_share = 1.0 - explore_share

    return {
        "explore_usage_share": explore_share,
        "settle_usage_share": settle_share,
        "guided_usage_total": max(0.0, guided_total),
    }


def _read_density_preference_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "density_preference_guided_total",
        "density_preference_seek_usage_per_tick",
        "density_preference_avoid_usage_per_tick",
        "density_preference_avoid_share",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    guided_total = float(avg_trait_raw.get("density_preference_guided_total", 0.0))
    seek_usage = float(avg_trait_raw.get("density_preference_seek_usage_per_tick", 0.0))
    avoid_usage = float(avg_trait_raw.get("density_preference_avoid_usage_per_tick", 0.0))
    avoid_share = float(avg_trait_raw.get("density_preference_avoid_share", 0.0))

    return {
        "guided_usage_total": max(0.0, guided_total),
        "seek_usage_per_tick": max(0.0, seek_usage),
        "avoid_usage_per_tick": max(0.0, avoid_usage),
        "avoid_usage_share": max(0.0, min(1.0, avoid_share)),
    }


def _read_mobility_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "mobility_efficiency_std",
        "movement_distance_observed",
        "movement_usage_per_tick",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    mobility_std = float(avg_trait_raw.get("mobility_efficiency_std", 0.0))
    movement_distance = float(avg_trait_raw.get("movement_distance_observed", 0.0))
    movement_usage = float(avg_trait_raw.get("movement_usage_per_tick", 0.0))

    return {
        "mobility_dispersion": max(0.0, mobility_std),
        "movement_distance_observed": max(0.0, movement_distance),
        "movement_usage_per_tick": max(0.0, movement_usage),
    }


def _read_longevity_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "longevity_factor_std",
        "age_wear_usage_per_tick",
        "age_wear_multiplier_observed",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    longevity_std = float(avg_trait_raw.get("longevity_factor_std", 0.0))
    age_wear_usage = float(avg_trait_raw.get("age_wear_usage_per_tick", 0.0))
    age_wear_multiplier = float(avg_trait_raw.get("age_wear_multiplier_observed", 1.0))

    return {
        "longevity_dispersion": max(0.0, longevity_std),
        "age_wear_usage_per_tick": max(0.0, age_wear_usage),
        "age_wear_effect_strength": abs(age_wear_multiplier - 1.0),
        "age_wear_reduction_strength": max(0.0, 1.0 - age_wear_multiplier),
    }


def _read_environmental_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "environmental_tolerance_std",
        "poor_zone_drain_usage_per_tick",
        "rich_zone_drain_usage_per_tick",
        "environmental_tolerance_poor_drain_bias",
        "environmental_tolerance_rich_drain_bias",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    environmental_std = float(avg_trait_raw.get("environmental_tolerance_std", 0.0))
    poor_usage = float(avg_trait_raw.get("poor_zone_drain_usage_per_tick", 0.0))
    rich_usage = float(avg_trait_raw.get("rich_zone_drain_usage_per_tick", 0.0))
    poor_bias = float(avg_trait_raw.get("environmental_tolerance_poor_drain_bias", 0.0))
    rich_bias = float(avg_trait_raw.get("environmental_tolerance_rich_drain_bias", 0.0))

    return {
        "environmental_dispersion": max(0.0, environmental_std),
        "poor_zone_usage_per_tick": max(0.0, poor_usage),
        "rich_zone_usage_per_tick": max(0.0, rich_usage),
        "poor_zone_effect_strength": abs(poor_bias),
        "rich_zone_effect_strength": abs(rich_bias),
    }


def _read_reproduction_timing_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "reproduction_timing_std",
        "reproduction_timing_threshold_multiplier_observed",
        "reproduction_timing_reproduction_bias",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    timing_std = float(avg_trait_raw.get("reproduction_timing_std", 0.0))
    threshold_multiplier = float(
        avg_trait_raw.get("reproduction_timing_threshold_multiplier_observed", 1.0)
    )
    reproduction_bias = float(avg_trait_raw.get("reproduction_timing_reproduction_bias", 0.0))

    return {
        "timing_dispersion": max(0.0, timing_std),
        "threshold_effect_strength": abs(threshold_multiplier - 1.0),
        "earlier_reproduction_strength": max(0.0, 1.0 - threshold_multiplier),
        "prudent_reproduction_strength": max(0.0, threshold_multiplier - 1.0),
        # Kept for possible future reporting while staying purely observatory.
        "reproduction_usage_bias": reproduction_bias,
    }


def _read_stress_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "stress_tolerance_std",
        "stress_tolerance_pressure_mean",
        "stress_tolerance_pressure_flee_bias",
        "stress_pressure_events",
        "stress_pressure_flee_rate",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    stress_std = float(avg_trait_raw.get("stress_tolerance_std", 0.0))
    pressure_mean = float(avg_trait_raw.get("stress_tolerance_pressure_mean", 1.0))
    flee_bias = float(avg_trait_raw.get("stress_tolerance_pressure_flee_bias", 0.0))
    pressure_events = float(avg_trait_raw.get("stress_pressure_events", 0.0))
    pressure_flee_rate = float(avg_trait_raw.get("stress_pressure_flee_rate", 0.0))

    return {
        "stress_dispersion": max(0.0, stress_std),
        "pressure_effect_strength": abs(pressure_mean - 1.0),
        "flee_modulation_strength": abs(flee_bias),
        "stress_pressure_events": max(0.0, pressure_events),
        "stress_pressure_flee_rate": max(0.0, pressure_flee_rate),
    }


def _read_hunger_metrics(summary_raw: Dict[str, object]) -> Dict[str, float] | None:
    avg_trait_raw = summary_raw.get("avg_trait_impact")
    if not isinstance(avg_trait_raw, dict):
        return None

    required = (
        "hunger_sensitivity_std",
        "hunger_sensitivity_search_bias",
        "hunger_search_usage_per_tick",
    )
    if any(key not in avg_trait_raw for key in required):
        return None

    hunger_std = float(avg_trait_raw.get("hunger_sensitivity_std", 0.0))
    hunger_search_bias = float(avg_trait_raw.get("hunger_sensitivity_search_bias", 0.0))
    hunger_search_usage = float(avg_trait_raw.get("hunger_search_usage_per_tick", 0.0))

    return {
        "hunger_dispersion": max(0.0, hunger_std),
        "hunger_threshold_effect_strength": abs(hunger_search_bias),
        "earlier_food_search_strength": max(0.0, hunger_search_bias),
        "later_food_search_strength": max(0.0, -hunger_search_bias),
        "hunger_search_usage_per_tick": max(0.0, hunger_search_usage),
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

