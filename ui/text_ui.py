from __future__ import annotations

from typing import Dict


def print_run_header(config: Dict[str, float | int]) -> None:
    print("=== Evolution MVP Simulation ===")
    print(
        "map={width}x{height} creatures={creatures} initial_food={initial_food} steps={steps} dt={dt}".format(
            width=config["map_width"],
            height=config["map_height"],
            creatures=config["creature_count"],
            initial_food=config["initial_food_count"],
            steps=config["steps"],
            dt=config["dt"],
        )
    )
    print(
        "tick | population | vivants | morts | nourriture | energie_moy | age_moy | gen_moy | naissances(T/dT) | deces(T/dT) | vitesse_moy | metabolisme_moy | prudence_moy | dominance_moy | risque_moy | repro_moy | memoire_trait_moy | social_trait_moy | persistance_trait_moy | exploration_trait_moy | densite_trait_moy | efficacite_energie_moy | resistance_epuisement_moy"
    )


def format_stats_line(tick: int, stats: Dict[str, object]) -> str:
    births_block = f"T:{int(stats['total_births'])} dT:+{int(stats['births_last_tick'])}"
    deaths_block = f"T:{int(stats['total_deaths'])} dT:+{int(stats['deaths_last_tick'])}"

    return (
        f"{tick:4d} | "
        f"{int(stats['population']):10d} | "
        f"{int(stats['alive']):7d} | "
        f"{int(stats['dead']):5d} | "
        f"{float(stats['food_remaining']):10.1f} | "
        f"{float(stats['avg_energy']):11.2f} | "
        f"{float(stats['avg_age']):7.2f} | "
        f"{float(stats['avg_generation']):7.2f} | "
        f"{births_block:16s} | "
        f"{deaths_block:12s} | "
        f"{float(stats['avg_speed']):11.3f} | "
        f"{float(stats['avg_metabolism']):15.3f} | "
        f"{float(stats['avg_prudence']):12.3f} | "
        f"{float(stats['avg_dominance']):13.3f} | "
        f"{float(stats.get('avg_risk_taking', 0.0)):10.3f} | "
        f"{float(stats['avg_repro_drive']):9.3f} | "
        f"{float(stats.get('avg_memory_focus', 0.0)):17.3f} | "
        f"{float(stats.get('avg_social_sensitivity', 0.0)):16.3f} | "
        f"{float(stats.get('avg_behavior_persistence', 0.0)):21.3f} | "
        f"{float(stats.get('avg_exploration_bias', 0.0)):20.3f} | "
        f"{float(stats.get('avg_density_preference', 0.0)):16.3f} | "
        f"{float(stats.get('avg_energy_efficiency', 0.0)):22.3f} | "
        f"{float(stats.get('avg_exhaustion_resistance', 0.0)):25.3f}"
    )


def format_generation_distribution(distribution: Dict[int, int], max_bins: int = 8) -> str:
    if max_bins <= 0:
        raise ValueError("max_bins must be > 0")
    if not distribution:
        return "generations: (none)"

    ordered = sorted(distribution.items())
    if len(ordered) <= max_bins:
        parts = [f"g{generation}:{count}" for generation, count in ordered]
        return "generations: " + " ".join(parts)

    # Keep both history start and latest generations for readability.
    head_bins = max(1, max_bins // 2)
    tail_bins = max(1, max_bins - head_bins)
    head = ordered[:head_bins]
    tail = ordered[-tail_bins:]

    parts = [f"g{generation}:{count}" for generation, count in head]
    parts.append("...")
    parts.extend(f"g{generation}:{count}" for generation, count in tail)

    hidden = len(ordered) - len(head) - len(tail)
    suffix = "" if hidden <= 0 else f" (+{hidden} hidden)"
    return "generations: " + " ".join(parts) + suffix


def format_proto_groups(stats: Dict[str, object], max_groups: int = 3) -> str:
    if max_groups <= 0:
        raise ValueError("max_groups must be > 0")

    group_count = int(stats.get("proto_group_count", 0))
    dominant_share = float(stats.get("dominant_proto_group_share", 0.0))
    raw_top_groups = stats.get("proto_groups_top")

    if group_count <= 0 or not isinstance(raw_top_groups, list) or len(raw_top_groups) == 0:
        return "proto_groupes:0"

    parts: list[str] = []
    for group in raw_top_groups[:max_groups]:
        if not isinstance(group, dict):
            continue
        parts.append(
            "{signature}(n={size},part={share:.2f},s={speed:.2f},m={metabolism:.2f},p={prudence:.2f},d={dominance:.2f},r={repro:.2f})".format(
                signature=str(group.get("signature", "?")),
                size=int(group.get("size", 0)),
                share=float(group.get("share", 0.0)),
                speed=float(group.get("avg_speed", 0.0)),
                metabolism=float(group.get("avg_metabolism", 0.0)),
                prudence=float(group.get("avg_prudence", 0.0)),
                dominance=float(group.get("avg_dominance", 0.0)),
                repro=float(group.get("avg_repro_drive", 0.0)),
            )
        )

    if not parts:
        return f"proto_groupes:{group_count}"

    return f"proto_groupes:{group_count} dominant_part:{dominant_share:.2f} top: " + " ".join(parts)


def format_proto_groups_by_fertility_zone(stats: Dict[str, object]) -> str:
    zone_counts_raw = stats.get("creatures_by_fertility_zone")
    zone_dominants_raw = stats.get("dominant_proto_group_by_fertility_zone")

    zone_counts = {"rich": 0, "neutral": 0, "poor": 0}
    if isinstance(zone_counts_raw, dict):
        zone_counts["rich"] = int(zone_counts_raw.get("rich", 0))
        zone_counts["neutral"] = int(zone_counts_raw.get("neutral", 0))
        zone_counts["poor"] = int(zone_counts_raw.get("poor", 0))

    def dominant_label(zone_name: str) -> str:
        if not isinstance(zone_dominants_raw, dict):
            return "-"
        dominant = zone_dominants_raw.get(zone_name)
        if not isinstance(dominant, dict):
            return "-"
        signature = str(dominant.get("signature", "?"))
        count = int(dominant.get("count", 0))
        share = float(dominant.get("share", 0.0))
        return f"{signature}(n={count},part={share:.2f})"

    return (
        "proto_zones_creatures: riches={rich} neutres={neutral} pauvres={poor} "
        "dominants: riches={dom_rich} neutres={dom_neutral} pauvres={dom_poor}"
    ).format(
        rich=zone_counts["rich"],
        neutral=zone_counts["neutral"],
        poor=zone_counts["poor"],
        dom_rich=dominant_label("rich"),
        dom_neutral=dominant_label("neutral"),
        dom_poor=dominant_label("poor"),
    )


def format_proto_group_temporal(stats: Dict[str, object], max_items: int = 6) -> str:
    if max_items <= 0:
        raise ValueError("max_items must be > 0")

    raw_trends = stats.get("proto_group_temporal_trends")
    raw_summary = stats.get("proto_group_temporal_summary")

    if not isinstance(raw_trends, list):
        return "proto_tendance: n/a"

    summary = {
        "stable": 0,
        "en_hausse": 0,
        "en_baisse": 0,
        "nouveau": 0,
    }
    if isinstance(raw_summary, dict):
        summary["stable"] = int(raw_summary.get("stable", 0))
        summary["en_hausse"] = int(raw_summary.get("en_hausse", 0))
        summary["en_baisse"] = int(raw_summary.get("en_baisse", 0))
        summary["nouveau"] = int(raw_summary.get("nouveau", 0))

    if len(raw_trends) == 0:
        return (
            "proto_tendance: aucune "
            f"(stable={summary['stable']} hausse={summary['en_hausse']} "
            f"baisse={summary['en_baisse']} nouveau={summary['nouveau']})"
        )

    def label_for_status(status: str) -> str:
        if status == "en_hausse":
            return "hausse"
        if status == "en_baisse":
            return "baisse"
        return status

    parts: list[str] = []
    for trend in raw_trends[:max_items]:
        if not isinstance(trend, dict):
            continue
        signature = str(trend.get("signature", "?"))
        status = label_for_status(str(trend.get("status", "?")))
        current_share = float(trend.get("current_share", 0.0))
        previous_share = float(trend.get("previous_share", 0.0))
        delta_share = float(trend.get("delta_share", 0.0))
        parts.append(
            f"{signature}:{status}({previous_share:.2f}->{current_share:.2f},{delta_share:+.2f})"
        )

    if not parts:
        return (
            "proto_tendance: aucune "
            f"(stable={summary['stable']} hausse={summary['en_hausse']} "
            f"baisse={summary['en_baisse']} nouveau={summary['nouveau']})"
        )

    return (
        "proto_tendance: "
        + " ".join(parts)
        + " "
        + "(stable={stable} hausse={hausse} baisse={baisse} nouveau={nouveau})".format(
            stable=summary["stable"],
            hausse=summary["en_hausse"],
            baisse=summary["en_baisse"],
            nouveau=summary["nouveau"],
        )
    )



def format_final_run_summary(summary: Dict[str, object]) -> str:
    zones_raw = summary.get("final_zone_distribution")
    traits_raw = summary.get("avg_traits")
    memory_raw = summary.get("memory_impact")
    social_raw = summary.get("social_impact")
    trait_impact_raw = summary.get("trait_impact")

    zones = {"rich": 0, "neutral": 0, "poor": 0}
    if isinstance(zones_raw, dict):
        zones["rich"] = int(zones_raw.get("rich", 0))
        zones["neutral"] = int(zones_raw.get("neutral", 0))
        zones["poor"] = int(zones_raw.get("poor", 0))

    traits = {
        "speed": 0.0,
        "metabolism": 0.0,
        "prudence": 0.0,
        "dominance": 0.0,
        "risk_taking": 0.0,
        "repro_drive": 0.0,
        "food_perception": 0.0,
        "threat_perception": 0.0,
        "behavior_persistence": 0.0,
        "exploration_bias": 0.0,
        "density_preference": 0.0,
        "energy_efficiency": 0.0,
        "exhaustion_resistance": 0.0,
    }
    if isinstance(traits_raw, dict):
        traits["speed"] = float(traits_raw.get("speed", 0.0))
        traits["metabolism"] = float(traits_raw.get("metabolism", 0.0))
        traits["prudence"] = float(traits_raw.get("prudence", 0.0))
        traits["dominance"] = float(traits_raw.get("dominance", 0.0))
        traits["risk_taking"] = float(traits_raw.get("risk_taking", 0.0))
        traits["repro_drive"] = float(traits_raw.get("repro_drive", 0.0))
        traits["food_perception"] = float(traits_raw.get("food_perception", 0.0))
        traits["threat_perception"] = float(traits_raw.get("threat_perception", 0.0))
        traits["behavior_persistence"] = float(traits_raw.get("behavior_persistence", 0.0))
        traits["exploration_bias"] = float(traits_raw.get("exploration_bias", 0.0))
        traits["density_preference"] = float(traits_raw.get("density_preference", 0.0))
        traits["energy_efficiency"] = float(traits_raw.get("energy_efficiency", 0.0))
        traits["exhaustion_resistance"] = float(traits_raw.get("exhaustion_resistance", 0.0))

    memory = {
        "food_usage_total": 0,
        "danger_usage_total": 0,
        "food_active_share": 0.0,
        "danger_active_share": 0.0,
        "food_effect_avg_distance": 0.0,
        "danger_effect_avg_distance": 0.0,
        "food_usage_per_tick": 0.0,
        "danger_usage_per_tick": 0.0,
    }
    if isinstance(memory_raw, dict):
        memory["food_usage_total"] = int(memory_raw.get("food_usage_total", 0))
        memory["danger_usage_total"] = int(memory_raw.get("danger_usage_total", 0))
        memory["food_active_share"] = float(memory_raw.get("food_active_share", 0.0))
        memory["danger_active_share"] = float(memory_raw.get("danger_active_share", 0.0))
        memory["food_effect_avg_distance"] = float(memory_raw.get("food_effect_avg_distance", 0.0))
        memory["danger_effect_avg_distance"] = float(memory_raw.get("danger_effect_avg_distance", 0.0))
        memory["food_usage_per_tick"] = float(memory_raw.get("food_usage_per_tick", 0.0))
        memory["danger_usage_per_tick"] = float(memory_raw.get("danger_usage_per_tick", 0.0))

    social = {
        "follow_usage_total": 0,
        "flee_boost_usage_total": 0,
        "influenced_count_last_tick": 0,
        "influenced_share_last_tick": 0.0,
        "influenced_per_tick": 0.0,
        "follow_usage_per_tick": 0.0,
        "flee_boost_usage_per_tick": 0.0,
        "flee_multiplier_avg_tick": 1.0,
        "flee_multiplier_avg_total": 1.0,
    }
    if isinstance(social_raw, dict):
        social["follow_usage_total"] = int(social_raw.get("follow_usage_total", 0))
        social["flee_boost_usage_total"] = int(social_raw.get("flee_boost_usage_total", 0))
        social["influenced_count_last_tick"] = int(social_raw.get("influenced_count_last_tick", 0))
        social["influenced_share_last_tick"] = float(social_raw.get("influenced_share_last_tick", 0.0))
        social["influenced_per_tick"] = float(social_raw.get("influenced_per_tick", 0.0))
        social["follow_usage_per_tick"] = float(social_raw.get("follow_usage_per_tick", 0.0))
        social["flee_boost_usage_per_tick"] = float(social_raw.get("flee_boost_usage_per_tick", 0.0))
        social["flee_multiplier_avg_tick"] = float(social_raw.get("flee_multiplier_avg_tick", 1.0))
        social["flee_multiplier_avg_total"] = float(social_raw.get("flee_multiplier_avg_total", 1.0))

    trait_impact = {
        "memory_focus_mean": 0.0,
        "memory_focus_std": 0.0,
        "social_sensitivity_mean": 0.0,
        "social_sensitivity_std": 0.0,
        "food_perception_mean": 0.0,
        "food_perception_std": 0.0,
        "threat_perception_mean": 0.0,
        "threat_perception_std": 0.0,
        "risk_taking_mean": 0.0,
        "risk_taking_std": 0.0,
        "behavior_persistence_mean": 0.0,
        "behavior_persistence_std": 0.0,
        "exploration_bias_mean": 0.0,
        "exploration_bias_std": 0.0,
        "density_preference_mean": 0.0,
        "density_preference_std": 0.0,
        "energy_efficiency_mean": 0.0,
        "energy_efficiency_std": 0.0,
        "exhaustion_resistance_mean": 0.0,
        "exhaustion_resistance_std": 0.0,
        "energy_efficiency_drain_bias": 0.0,
        "exhaustion_resistance_reproduction_bias": 0.0,
        "energy_drain_multiplier_observed": 0.0,
        "reproduction_cost_multiplier_observed": 0.0,
        "energy_drain_amount_observed": 0.0,
        "reproduction_cost_amount_observed": 0.0,
        "memory_focus_food_bias": 0.0,
        "memory_focus_danger_bias": 0.0,
        "social_sensitivity_follow_bias": 0.0,
        "social_sensitivity_flee_boost_bias": 0.0,
        "food_perception_detection_bias": 0.0,
        "food_perception_consumption_bias": 0.0,
        "threat_perception_flee_bias": 0.0,
        "risk_taking_flee_bias": 0.0,
        "behavior_persistence_hold_bias": 0.0,
        "exploration_bias_guided_bias": 0.0,
        "exploration_bias_guided_total": 0.0,
        "exploration_bias_explore_share": 0.0,
        "exploration_bias_explore_users_avg": 0.0,
        "exploration_bias_explore_usage_bias": 0.0,
        "exploration_bias_settle_users_avg": 0.0,
        "exploration_bias_settle_usage_bias": 0.0,
        "exploration_bias_anchor_distance_delta": 0.0,
        "density_preference_guided_bias": 0.0,
        "density_preference_guided_total": 0.0,
        "density_preference_seek_share": 0.0,
        "density_preference_seek_users_avg": 0.0,
        "density_preference_seek_usage_bias": 0.0,
        "density_preference_avoid_users_avg": 0.0,
        "density_preference_avoid_usage_bias": 0.0,
        "density_preference_neighbor_count_avg": 0.0,
        "density_preference_center_distance_delta": 0.0,
        "persistence_holds_total": 0.0,
        "behavior_persistence_oscillation_switch_rate": 0.0,
        "behavior_persistence_oscillation_prevented_rate": 0.0,
        "search_wander_switches_total": 0.0,
        "search_wander_switches_prevented_total": 0.0,
        "search_wander_oscillation_events_total": 0.0,
        "borderline_threat_encounters": 0.0,
        "borderline_threat_flees": 0.0,
        "borderline_threat_flee_rate": 0.0,
        "risk_taking_borderline_encounter_mean": 0.0,
        "risk_taking_borderline_flee_mean": 0.0,
        "risk_taking_borderline_flee_bias": 0.0,
    }
    if isinstance(trait_impact_raw, dict):
        trait_impact["memory_focus_mean"] = float(trait_impact_raw.get("memory_focus_mean", 0.0))
        trait_impact["memory_focus_std"] = float(trait_impact_raw.get("memory_focus_std", 0.0))
        trait_impact["social_sensitivity_mean"] = float(trait_impact_raw.get("social_sensitivity_mean", 0.0))
        trait_impact["social_sensitivity_std"] = float(trait_impact_raw.get("social_sensitivity_std", 0.0))
        trait_impact["food_perception_mean"] = float(trait_impact_raw.get("food_perception_mean", 0.0))
        trait_impact["food_perception_std"] = float(trait_impact_raw.get("food_perception_std", 0.0))
        trait_impact["threat_perception_mean"] = float(trait_impact_raw.get("threat_perception_mean", 0.0))
        trait_impact["threat_perception_std"] = float(trait_impact_raw.get("threat_perception_std", 0.0))
        trait_impact["risk_taking_mean"] = float(trait_impact_raw.get("risk_taking_mean", 0.0))
        trait_impact["risk_taking_std"] = float(trait_impact_raw.get("risk_taking_std", 0.0))
        trait_impact["behavior_persistence_mean"] = float(
            trait_impact_raw.get("behavior_persistence_mean", 0.0)
        )
        trait_impact["behavior_persistence_std"] = float(
            trait_impact_raw.get("behavior_persistence_std", 0.0)
        )
        trait_impact["exploration_bias_mean"] = float(
            trait_impact_raw.get("exploration_bias_mean", 0.0)
        )
        trait_impact["exploration_bias_std"] = float(
            trait_impact_raw.get("exploration_bias_std", 0.0)
        )
        trait_impact["density_preference_mean"] = float(
            trait_impact_raw.get("density_preference_mean", 0.0)
        )
        trait_impact["density_preference_std"] = float(
            trait_impact_raw.get("density_preference_std", 0.0)
        )
        trait_impact["energy_efficiency_mean"] = float(trait_impact_raw.get("energy_efficiency_mean", 0.0))
        trait_impact["energy_efficiency_std"] = float(trait_impact_raw.get("energy_efficiency_std", 0.0))
        trait_impact["exhaustion_resistance_mean"] = float(trait_impact_raw.get("exhaustion_resistance_mean", 0.0))
        trait_impact["exhaustion_resistance_std"] = float(trait_impact_raw.get("exhaustion_resistance_std", 0.0))
        trait_impact["energy_efficiency_drain_bias"] = float(
            trait_impact_raw.get("energy_efficiency_drain_bias", 0.0)
        )
        trait_impact["exhaustion_resistance_reproduction_bias"] = float(
            trait_impact_raw.get("exhaustion_resistance_reproduction_bias", 0.0)
        )
        trait_impact["energy_drain_multiplier_observed"] = float(
            trait_impact_raw.get("energy_drain_multiplier_observed", 0.0)
        )
        trait_impact["reproduction_cost_multiplier_observed"] = float(
            trait_impact_raw.get("reproduction_cost_multiplier_observed", 0.0)
        )
        trait_impact["energy_drain_amount_observed"] = float(
            trait_impact_raw.get("energy_drain_amount_observed", 0.0)
        )
        trait_impact["reproduction_cost_amount_observed"] = float(
            trait_impact_raw.get("reproduction_cost_amount_observed", 0.0)
        )
        trait_impact["memory_focus_food_bias"] = float(trait_impact_raw.get("memory_focus_food_bias", 0.0))
        trait_impact["memory_focus_danger_bias"] = float(trait_impact_raw.get("memory_focus_danger_bias", 0.0))
        trait_impact["social_sensitivity_follow_bias"] = float(trait_impact_raw.get("social_sensitivity_follow_bias", 0.0))
        trait_impact["social_sensitivity_flee_boost_bias"] = float(trait_impact_raw.get("social_sensitivity_flee_boost_bias", 0.0))
        trait_impact["food_perception_detection_bias"] = float(trait_impact_raw.get("food_perception_detection_bias", 0.0))
        trait_impact["food_perception_consumption_bias"] = float(trait_impact_raw.get("food_perception_consumption_bias", 0.0))
        trait_impact["threat_perception_flee_bias"] = float(trait_impact_raw.get("threat_perception_flee_bias", 0.0))
        trait_impact["risk_taking_flee_bias"] = float(trait_impact_raw.get("risk_taking_flee_bias", 0.0))
        trait_impact["behavior_persistence_hold_bias"] = float(
            trait_impact_raw.get("behavior_persistence_hold_bias", 0.0)
        )
        trait_impact["exploration_bias_guided_bias"] = float(
            trait_impact_raw.get("exploration_bias_guided_bias", 0.0)
        )
        trait_impact["exploration_bias_guided_total"] = float(
            trait_impact_raw.get("exploration_bias_guided_total", 0.0)
        )
        trait_impact["exploration_bias_explore_share"] = float(
            trait_impact_raw.get("exploration_bias_explore_share", 0.0)
        )
        trait_impact["exploration_bias_explore_users_avg"] = float(
            trait_impact_raw.get("exploration_bias_explore_users_avg", 0.0)
        )
        trait_impact["exploration_bias_explore_usage_bias"] = float(
            trait_impact_raw.get("exploration_bias_explore_usage_bias", 0.0)
        )
        trait_impact["exploration_bias_settle_users_avg"] = float(
            trait_impact_raw.get("exploration_bias_settle_users_avg", 0.0)
        )
        trait_impact["exploration_bias_settle_usage_bias"] = float(
            trait_impact_raw.get("exploration_bias_settle_usage_bias", 0.0)
        )
        trait_impact["exploration_bias_anchor_distance_delta"] = float(
            trait_impact_raw.get("exploration_bias_anchor_distance_delta", 0.0)
        )
        trait_impact["density_preference_guided_bias"] = float(
            trait_impact_raw.get("density_preference_guided_bias", 0.0)
        )
        trait_impact["density_preference_guided_total"] = float(
            trait_impact_raw.get("density_preference_guided_total", 0.0)
        )
        trait_impact["density_preference_seek_share"] = float(
            trait_impact_raw.get("density_preference_seek_share", 0.0)
        )
        trait_impact["density_preference_seek_users_avg"] = float(
            trait_impact_raw.get("density_preference_seek_users_avg", 0.0)
        )
        trait_impact["density_preference_seek_usage_bias"] = float(
            trait_impact_raw.get("density_preference_seek_usage_bias", 0.0)
        )
        trait_impact["density_preference_avoid_users_avg"] = float(
            trait_impact_raw.get("density_preference_avoid_users_avg", 0.0)
        )
        trait_impact["density_preference_avoid_usage_bias"] = float(
            trait_impact_raw.get("density_preference_avoid_usage_bias", 0.0)
        )
        trait_impact["density_preference_neighbor_count_avg"] = float(
            trait_impact_raw.get("density_preference_neighbor_count_avg", 0.0)
        )
        trait_impact["density_preference_center_distance_delta"] = float(
            trait_impact_raw.get("density_preference_center_distance_delta", 0.0)
        )
        trait_impact["persistence_holds_total"] = float(
            trait_impact_raw.get("persistence_holds_total", 0.0)
        )
        trait_impact["behavior_persistence_oscillation_switch_rate"] = float(
            trait_impact_raw.get("behavior_persistence_oscillation_switch_rate", 0.0)
        )
        trait_impact["behavior_persistence_oscillation_prevented_rate"] = float(
            trait_impact_raw.get("behavior_persistence_oscillation_prevented_rate", 0.0)
        )
        trait_impact["search_wander_switches_total"] = float(
            trait_impact_raw.get("search_wander_switches_total", 0.0)
        )
        trait_impact["search_wander_switches_prevented_total"] = float(
            trait_impact_raw.get("search_wander_switches_prevented_total", 0.0)
        )
        trait_impact["search_wander_oscillation_events_total"] = float(
            trait_impact_raw.get("search_wander_oscillation_events_total", 0.0)
        )
        trait_impact["borderline_threat_encounters"] = float(
            trait_impact_raw.get("borderline_threat_encounters", 0.0)
        )
        trait_impact["borderline_threat_flees"] = float(
            trait_impact_raw.get("borderline_threat_flees", 0.0)
        )
        trait_impact["borderline_threat_flee_rate"] = float(
            trait_impact_raw.get("borderline_threat_flee_rate", 0.0)
        )
        trait_impact["risk_taking_borderline_encounter_mean"] = float(
            trait_impact_raw.get("risk_taking_borderline_encounter_mean", 0.0)
        )
        trait_impact["risk_taking_borderline_flee_mean"] = float(
            trait_impact_raw.get("risk_taking_borderline_flee_mean", 0.0)
        )
        trait_impact["risk_taking_borderline_flee_bias"] = float(
            trait_impact_raw.get("risk_taking_borderline_flee_bias", 0.0)
        )

    return (
        "synthese_run: "
        "dominant_final={dominant}(part={dominant_share:.2f}) "
        "plus_stable={stable}(n={stable_count}) "
        "plus_hausse={rising}(n={rising_count}) "
        "zones_finales:riches={rich} neutres={neutral} pauvres={poor} "
        "traits_moy:s={speed:.3f},m={metabolism:.3f},p={prudence:.3f},d={dominance:.3f},rk={risk_taking:.3f},r={repro:.3f},fp={food_perception:.3f},tp={threat_perception:.3f},bp={behavior_persistence:.3f},ex={exploration_bias:.3f},dp={density_preference:.3f},ee={energy_efficiency:.3f},er={exhaustion_resistance:.3f} "
        "memoire:util={mem_food} dang={mem_danger} act_u={mem_food_share:.2f} act_d={mem_danger_share:.2f} "
        "freq_u={mem_food_freq:.2f} freq_d={mem_danger_freq:.2f} "
        "effet_u={mem_food_effect:.2f} effet_d={mem_danger_effect:.2f} "
        "social:suivi={social_follow} fuite_boost={social_flee_boost} "
        "part_infl_tick={social_infl_share:.2f} infl_tick={social_infl_count} infl_moy_tick={social_infl_tick:.2f} "
        "freq_suivi={social_follow_freq:.2f} freq_boost={social_boost_freq:.2f} "
        "mult_tick={social_mult_tick:.2f} mult_moy={social_mult_total:.2f} "
        "traits_impact:mem_mu={mem_mu:.3f} mem_sigma={mem_sigma:.3f} soc_mu={soc_mu:.3f} soc_sigma={soc_sigma:.3f} fp_mu={fp_mu:.3f} fp_sigma={fp_sigma:.3f} tp_mu={tp_mu:.3f} tp_sigma={tp_sigma:.3f} rk_mu={rk_mu:.3f} rk_sigma={rk_sigma:.3f} bp_mu={bp_mu:.3f} bp_sigma={bp_sigma:.3f} ex_mu={ex_mu:.3f} ex_sigma={ex_sigma:.3f} dp_mu={dp_mu:.3f} dp_sigma={dp_sigma:.3f} ee_mu={ee_mu:.3f} ee_sigma={ee_sigma:.3f} er_mu={er_mu:.3f} er_sigma={er_sigma:.3f} "
        "energy_obs:drain_mult={drain_mult_obs:.3f} repro_mult={repro_mult_obs:.3f} drain_amt={drain_amt_obs:.3f} repro_amt={repro_amt_obs:.3f} "
        "bias_mem_u={bias_mem_u:+.3f} bias_mem_d={bias_mem_d:+.3f} "
        "bias_soc_suivi={bias_soc_follow:+.3f} bias_soc_fuite={bias_soc_flee:+.3f} bias_fp_det={bias_fp_det:+.3f} bias_fp_eat={bias_fp_eat:+.3f} bias_tp_fuite={bias_tp_flee:+.3f} bias_rk_fuite={bias_rk_flee:+.3f} bias_bp_inertie={bias_bp_hold:+.3f} bias_explore={bias_explore:+.3f} inertie_total={bp_holds_total:.0f} "
        "osc_bp:switch={bp_sw_total:.0f} bloc={bp_prev_total:.0f} events={bp_events_total:.0f} taux_switch={bp_sw_rate:.3f} taux_bloc={bp_prev_rate:.3f} "
        "exploration:guides={ex_guided_total:.0f} part_explore={ex_explore_share:.3f} ex_mu={ex_explore_mu:.3f} st_mu={ex_settle_mu:.3f} ex_bias={ex_explore_bias:+.3f} st_bias={ex_settle_bias:+.3f} delta_ancre={ex_anchor_delta:+.3f} "
        "densite:guides={dp_guided_total:.0f} part_seek={dp_seek_share:.3f} seek_mu={dp_seek_mu:.3f} avoid_mu={dp_avoid_mu:.3f} dp_bias={dp_guided_bias:+.3f} seek_bias={dp_seek_bias:+.3f} avoid_bias={dp_avoid_bias:+.3f} dens_voisins={dp_neighbors:.2f} delta_centre={dp_center_delta:+.3f} "
        "borderline:cas={rk_border_cases:.0f} fuite={rk_border_flees:.0f} taux={rk_border_rate:.3f} rk_border_mu={rk_border_mu:.3f} rk_fuite_mu={rk_border_flee_mu:.3f} rk_border_bias={rk_border_bias:+.3f} "
        "bias_ee_drain={bias_ee_drain:+.3f} bias_er_repro={bias_er_repro:+.3f} "
        "logs_obs={observed_logs}"
    ).format(
        dominant=str(summary.get("final_dominant_group_signature", "-")),
        dominant_share=float(summary.get("final_dominant_group_share", 0.0)),
        stable=str(summary.get("most_stable_group_signature", "-")),
        stable_count=int(summary.get("most_stable_group_count", 0)),
        rising=str(summary.get("most_rising_group_signature", "-")),
        rising_count=int(summary.get("most_rising_group_count", 0)),
        rich=zones["rich"],
        neutral=zones["neutral"],
        poor=zones["poor"],
        speed=traits["speed"],
        metabolism=traits["metabolism"],
        prudence=traits["prudence"],
        dominance=traits["dominance"],
        risk_taking=traits["risk_taking"],
        repro=traits["repro_drive"],
        food_perception=traits["food_perception"],
        threat_perception=traits["threat_perception"],
        behavior_persistence=traits["behavior_persistence"],
        exploration_bias=traits["exploration_bias"],
        density_preference=traits["density_preference"],
        energy_efficiency=traits["energy_efficiency"],
        exhaustion_resistance=traits["exhaustion_resistance"],
        mem_food=memory["food_usage_total"],
        mem_danger=memory["danger_usage_total"],
        mem_food_share=memory["food_active_share"],
        mem_danger_share=memory["danger_active_share"],
        mem_food_freq=memory["food_usage_per_tick"],
        mem_danger_freq=memory["danger_usage_per_tick"],
        mem_food_effect=memory["food_effect_avg_distance"],
        mem_danger_effect=memory["danger_effect_avg_distance"],
        social_follow=social["follow_usage_total"],
        social_flee_boost=social["flee_boost_usage_total"],
        social_infl_share=social["influenced_share_last_tick"],
        social_infl_count=social["influenced_count_last_tick"],
        social_infl_tick=social["influenced_per_tick"],
        social_follow_freq=social["follow_usage_per_tick"],
        social_boost_freq=social["flee_boost_usage_per_tick"],
        social_mult_tick=social["flee_multiplier_avg_tick"],
        social_mult_total=social["flee_multiplier_avg_total"],
        mem_mu=trait_impact["memory_focus_mean"],
        mem_sigma=trait_impact["memory_focus_std"],
        soc_mu=trait_impact["social_sensitivity_mean"],
        soc_sigma=trait_impact["social_sensitivity_std"],
        fp_mu=trait_impact["food_perception_mean"],
        fp_sigma=trait_impact["food_perception_std"],
        tp_mu=trait_impact["threat_perception_mean"],
        tp_sigma=trait_impact["threat_perception_std"],
        rk_mu=trait_impact["risk_taking_mean"],
        rk_sigma=trait_impact["risk_taking_std"],
        bp_mu=trait_impact["behavior_persistence_mean"],
        bp_sigma=trait_impact["behavior_persistence_std"],
        ex_mu=trait_impact["exploration_bias_mean"],
        ex_sigma=trait_impact["exploration_bias_std"],
        dp_mu=trait_impact["density_preference_mean"],
        dp_sigma=trait_impact["density_preference_std"],
        ee_mu=trait_impact["energy_efficiency_mean"],
        ee_sigma=trait_impact["energy_efficiency_std"],
        er_mu=trait_impact["exhaustion_resistance_mean"],
        er_sigma=trait_impact["exhaustion_resistance_std"],
        drain_mult_obs=trait_impact["energy_drain_multiplier_observed"],
        repro_mult_obs=trait_impact["reproduction_cost_multiplier_observed"],
        drain_amt_obs=trait_impact["energy_drain_amount_observed"],
        repro_amt_obs=trait_impact["reproduction_cost_amount_observed"],
        bias_mem_u=trait_impact["memory_focus_food_bias"],
        bias_mem_d=trait_impact["memory_focus_danger_bias"],
        bias_soc_follow=trait_impact["social_sensitivity_follow_bias"],
        bias_soc_flee=trait_impact["social_sensitivity_flee_boost_bias"],
        bias_fp_det=trait_impact["food_perception_detection_bias"],
        bias_fp_eat=trait_impact["food_perception_consumption_bias"],
        bias_tp_flee=trait_impact["threat_perception_flee_bias"],
        bias_rk_flee=trait_impact["risk_taking_flee_bias"],
        bias_bp_hold=trait_impact["behavior_persistence_hold_bias"],
        bias_explore=trait_impact["exploration_bias_guided_bias"],
        bp_holds_total=trait_impact["persistence_holds_total"],
        bp_sw_total=trait_impact["search_wander_switches_total"],
        bp_prev_total=trait_impact["search_wander_switches_prevented_total"],
        bp_events_total=trait_impact["search_wander_oscillation_events_total"],
        bp_sw_rate=trait_impact["behavior_persistence_oscillation_switch_rate"],
        bp_prev_rate=trait_impact["behavior_persistence_oscillation_prevented_rate"],
        ex_guided_total=trait_impact["exploration_bias_guided_total"],
        ex_explore_share=trait_impact["exploration_bias_explore_share"],
        ex_explore_mu=trait_impact["exploration_bias_explore_users_avg"],
        ex_settle_mu=trait_impact["exploration_bias_settle_users_avg"],
        ex_explore_bias=trait_impact["exploration_bias_explore_usage_bias"],
        ex_settle_bias=trait_impact["exploration_bias_settle_usage_bias"],
        ex_anchor_delta=trait_impact["exploration_bias_anchor_distance_delta"],
        dp_guided_total=trait_impact["density_preference_guided_total"],
        dp_seek_share=trait_impact["density_preference_seek_share"],
        dp_seek_mu=trait_impact["density_preference_seek_users_avg"],
        dp_avoid_mu=trait_impact["density_preference_avoid_users_avg"],
        dp_guided_bias=trait_impact["density_preference_guided_bias"],
        dp_seek_bias=trait_impact["density_preference_seek_usage_bias"],
        dp_avoid_bias=trait_impact["density_preference_avoid_usage_bias"],
        dp_neighbors=trait_impact["density_preference_neighbor_count_avg"],
        dp_center_delta=trait_impact["density_preference_center_distance_delta"],
        rk_border_cases=trait_impact["borderline_threat_encounters"],
        rk_border_flees=trait_impact["borderline_threat_flees"],
        rk_border_rate=trait_impact["borderline_threat_flee_rate"],
        rk_border_mu=trait_impact["risk_taking_borderline_encounter_mean"],
        rk_border_flee_mu=trait_impact["risk_taking_borderline_flee_mean"],
        rk_border_bias=trait_impact["risk_taking_borderline_flee_bias"],
        bias_ee_drain=trait_impact["energy_efficiency_drain_bias"],
        bias_er_repro=trait_impact["exhaustion_resistance_reproduction_bias"],
        observed_logs=int(summary.get("observed_logs", 0)),
    )

def format_multi_run_summary(summary: Dict[str, object]) -> str:
    seeds_raw = summary.get("seeds")
    traits_raw = summary.get("avg_final_traits")
    memory_raw = summary.get("avg_memory_impact")
    social_raw = summary.get("avg_social_impact")
    trait_impact_raw = summary.get("avg_trait_impact")

    seeds: list[int] = []
    if isinstance(seeds_raw, list):
        seeds = [int(seed) for seed in seeds_raw]

    traits = {
        "speed": 0.0,
        "metabolism": 0.0,
        "prudence": 0.0,
        "dominance": 0.0,
        "risk_taking": 0.0,
        "repro_drive": 0.0,
        "food_perception": 0.0,
        "threat_perception": 0.0,
        "behavior_persistence": 0.0,
        "exploration_bias": 0.0,
        "density_preference": 0.0,
        "energy_efficiency": 0.0,
        "exhaustion_resistance": 0.0,
    }
    if isinstance(traits_raw, dict):
        traits["speed"] = float(traits_raw.get("speed", 0.0))
        traits["metabolism"] = float(traits_raw.get("metabolism", 0.0))
        traits["prudence"] = float(traits_raw.get("prudence", 0.0))
        traits["dominance"] = float(traits_raw.get("dominance", 0.0))
        traits["risk_taking"] = float(traits_raw.get("risk_taking", 0.0))
        traits["repro_drive"] = float(traits_raw.get("repro_drive", 0.0))
        traits["food_perception"] = float(traits_raw.get("food_perception", 0.0))
        traits["threat_perception"] = float(traits_raw.get("threat_perception", 0.0))
        traits["behavior_persistence"] = float(traits_raw.get("behavior_persistence", 0.0))
        traits["exploration_bias"] = float(traits_raw.get("exploration_bias", 0.0))
        traits["density_preference"] = float(traits_raw.get("density_preference", 0.0))
        traits["energy_efficiency"] = float(traits_raw.get("energy_efficiency", 0.0))
        traits["exhaustion_resistance"] = float(traits_raw.get("exhaustion_resistance", 0.0))

    memory = {
        "food_usage_total": 0.0,
        "danger_usage_total": 0.0,
        "food_active_share": 0.0,
        "danger_active_share": 0.0,
        "food_effect_avg_distance": 0.0,
        "danger_effect_avg_distance": 0.0,
        "food_usage_per_tick": 0.0,
        "danger_usage_per_tick": 0.0,
    }
    if isinstance(memory_raw, dict):
        memory["food_usage_total"] = float(memory_raw.get("food_usage_total", 0.0))
        memory["danger_usage_total"] = float(memory_raw.get("danger_usage_total", 0.0))
        memory["food_active_share"] = float(memory_raw.get("food_active_share", 0.0))
        memory["danger_active_share"] = float(memory_raw.get("danger_active_share", 0.0))
        memory["food_effect_avg_distance"] = float(memory_raw.get("food_effect_avg_distance", 0.0))
        memory["danger_effect_avg_distance"] = float(memory_raw.get("danger_effect_avg_distance", 0.0))
        memory["food_usage_per_tick"] = float(memory_raw.get("food_usage_per_tick", 0.0))
        memory["danger_usage_per_tick"] = float(memory_raw.get("danger_usage_per_tick", 0.0))

    social = {
        "follow_usage_total": 0.0,
        "flee_boost_usage_total": 0.0,
        "influenced_count_last_tick": 0.0,
        "influenced_share_last_tick": 0.0,
        "influenced_per_tick": 0.0,
        "follow_usage_per_tick": 0.0,
        "flee_boost_usage_per_tick": 0.0,
        "flee_multiplier_avg_tick": 1.0,
        "flee_multiplier_avg_total": 1.0,
    }
    if isinstance(social_raw, dict):
        social["follow_usage_total"] = float(social_raw.get("follow_usage_total", 0.0))
        social["flee_boost_usage_total"] = float(social_raw.get("flee_boost_usage_total", 0.0))
        social["influenced_count_last_tick"] = float(social_raw.get("influenced_count_last_tick", 0.0))
        social["influenced_share_last_tick"] = float(social_raw.get("influenced_share_last_tick", 0.0))
        social["influenced_per_tick"] = float(social_raw.get("influenced_per_tick", 0.0))
        social["follow_usage_per_tick"] = float(social_raw.get("follow_usage_per_tick", 0.0))
        social["flee_boost_usage_per_tick"] = float(social_raw.get("flee_boost_usage_per_tick", 0.0))
        social["flee_multiplier_avg_tick"] = float(social_raw.get("flee_multiplier_avg_tick", 1.0))
        social["flee_multiplier_avg_total"] = float(social_raw.get("flee_multiplier_avg_total", 1.0))

    trait_impact = {
        "memory_focus_mean": 0.0,
        "memory_focus_std": 0.0,
        "social_sensitivity_mean": 0.0,
        "social_sensitivity_std": 0.0,
        "food_perception_mean": 0.0,
        "food_perception_std": 0.0,
        "threat_perception_mean": 0.0,
        "threat_perception_std": 0.0,
        "risk_taking_mean": 0.0,
        "risk_taking_std": 0.0,
        "behavior_persistence_mean": 0.0,
        "behavior_persistence_std": 0.0,
        "exploration_bias_mean": 0.0,
        "exploration_bias_std": 0.0,
        "density_preference_mean": 0.0,
        "density_preference_std": 0.0,
        "energy_efficiency_mean": 0.0,
        "energy_efficiency_std": 0.0,
        "exhaustion_resistance_mean": 0.0,
        "exhaustion_resistance_std": 0.0,
        "energy_efficiency_drain_bias": 0.0,
        "exhaustion_resistance_reproduction_bias": 0.0,
        "energy_drain_multiplier_observed": 0.0,
        "reproduction_cost_multiplier_observed": 0.0,
        "energy_drain_amount_observed": 0.0,
        "reproduction_cost_amount_observed": 0.0,
        "memory_focus_food_bias": 0.0,
        "memory_focus_danger_bias": 0.0,
        "social_sensitivity_follow_bias": 0.0,
        "social_sensitivity_flee_boost_bias": 0.0,
        "food_perception_detection_bias": 0.0,
        "food_perception_consumption_bias": 0.0,
        "threat_perception_flee_bias": 0.0,
        "risk_taking_flee_bias": 0.0,
        "behavior_persistence_hold_bias": 0.0,
        "exploration_bias_guided_bias": 0.0,
        "exploration_bias_guided_total": 0.0,
        "exploration_bias_explore_share": 0.0,
        "exploration_bias_explore_users_avg": 0.0,
        "exploration_bias_explore_usage_bias": 0.0,
        "exploration_bias_settle_users_avg": 0.0,
        "exploration_bias_settle_usage_bias": 0.0,
        "exploration_bias_anchor_distance_delta": 0.0,
        "density_preference_guided_bias": 0.0,
        "density_preference_guided_total": 0.0,
        "density_preference_seek_share": 0.0,
        "density_preference_seek_users_avg": 0.0,
        "density_preference_seek_usage_bias": 0.0,
        "density_preference_avoid_users_avg": 0.0,
        "density_preference_avoid_usage_bias": 0.0,
        "density_preference_neighbor_count_avg": 0.0,
        "density_preference_center_distance_delta": 0.0,
        "persistence_holds_total": 0.0,
        "behavior_persistence_oscillation_switch_rate": 0.0,
        "behavior_persistence_oscillation_prevented_rate": 0.0,
        "search_wander_switches_total": 0.0,
        "search_wander_switches_prevented_total": 0.0,
        "search_wander_oscillation_events_total": 0.0,
    }
    if isinstance(trait_impact_raw, dict):
        trait_impact["memory_focus_mean"] = float(trait_impact_raw.get("memory_focus_mean", 0.0))
        trait_impact["memory_focus_std"] = float(trait_impact_raw.get("memory_focus_std", 0.0))
        trait_impact["social_sensitivity_mean"] = float(trait_impact_raw.get("social_sensitivity_mean", 0.0))
        trait_impact["social_sensitivity_std"] = float(trait_impact_raw.get("social_sensitivity_std", 0.0))
        trait_impact["food_perception_mean"] = float(trait_impact_raw.get("food_perception_mean", 0.0))
        trait_impact["food_perception_std"] = float(trait_impact_raw.get("food_perception_std", 0.0))
        trait_impact["threat_perception_mean"] = float(trait_impact_raw.get("threat_perception_mean", 0.0))
        trait_impact["threat_perception_std"] = float(trait_impact_raw.get("threat_perception_std", 0.0))
        trait_impact["risk_taking_mean"] = float(trait_impact_raw.get("risk_taking_mean", 0.0))
        trait_impact["risk_taking_std"] = float(trait_impact_raw.get("risk_taking_std", 0.0))
        trait_impact["behavior_persistence_mean"] = float(
            trait_impact_raw.get("behavior_persistence_mean", 0.0)
        )
        trait_impact["behavior_persistence_std"] = float(
            trait_impact_raw.get("behavior_persistence_std", 0.0)
        )
        trait_impact["exploration_bias_mean"] = float(
            trait_impact_raw.get("exploration_bias_mean", 0.0)
        )
        trait_impact["exploration_bias_std"] = float(
            trait_impact_raw.get("exploration_bias_std", 0.0)
        )
        trait_impact["density_preference_mean"] = float(
            trait_impact_raw.get("density_preference_mean", 0.0)
        )
        trait_impact["density_preference_std"] = float(
            trait_impact_raw.get("density_preference_std", 0.0)
        )
        trait_impact["energy_efficiency_mean"] = float(trait_impact_raw.get("energy_efficiency_mean", 0.0))
        trait_impact["energy_efficiency_std"] = float(trait_impact_raw.get("energy_efficiency_std", 0.0))
        trait_impact["exhaustion_resistance_mean"] = float(trait_impact_raw.get("exhaustion_resistance_mean", 0.0))
        trait_impact["exhaustion_resistance_std"] = float(trait_impact_raw.get("exhaustion_resistance_std", 0.0))
        trait_impact["energy_efficiency_drain_bias"] = float(
            trait_impact_raw.get("energy_efficiency_drain_bias", 0.0)
        )
        trait_impact["exhaustion_resistance_reproduction_bias"] = float(
            trait_impact_raw.get("exhaustion_resistance_reproduction_bias", 0.0)
        )
        trait_impact["energy_drain_multiplier_observed"] = float(
            trait_impact_raw.get("energy_drain_multiplier_observed", 0.0)
        )
        trait_impact["reproduction_cost_multiplier_observed"] = float(
            trait_impact_raw.get("reproduction_cost_multiplier_observed", 0.0)
        )
        trait_impact["energy_drain_amount_observed"] = float(
            trait_impact_raw.get("energy_drain_amount_observed", 0.0)
        )
        trait_impact["reproduction_cost_amount_observed"] = float(
            trait_impact_raw.get("reproduction_cost_amount_observed", 0.0)
        )
        trait_impact["memory_focus_food_bias"] = float(trait_impact_raw.get("memory_focus_food_bias", 0.0))
        trait_impact["memory_focus_danger_bias"] = float(trait_impact_raw.get("memory_focus_danger_bias", 0.0))
        trait_impact["social_sensitivity_follow_bias"] = float(trait_impact_raw.get("social_sensitivity_follow_bias", 0.0))
        trait_impact["social_sensitivity_flee_boost_bias"] = float(trait_impact_raw.get("social_sensitivity_flee_boost_bias", 0.0))
        trait_impact["food_perception_detection_bias"] = float(trait_impact_raw.get("food_perception_detection_bias", 0.0))
        trait_impact["food_perception_consumption_bias"] = float(trait_impact_raw.get("food_perception_consumption_bias", 0.0))
        trait_impact["threat_perception_flee_bias"] = float(trait_impact_raw.get("threat_perception_flee_bias", 0.0))
        trait_impact["risk_taking_flee_bias"] = float(trait_impact_raw.get("risk_taking_flee_bias", 0.0))
        trait_impact["behavior_persistence_hold_bias"] = float(
            trait_impact_raw.get("behavior_persistence_hold_bias", 0.0)
        )
        trait_impact["exploration_bias_guided_bias"] = float(
            trait_impact_raw.get("exploration_bias_guided_bias", 0.0)
        )
        trait_impact["exploration_bias_guided_total"] = float(
            trait_impact_raw.get("exploration_bias_guided_total", 0.0)
        )
        trait_impact["exploration_bias_explore_share"] = float(
            trait_impact_raw.get("exploration_bias_explore_share", 0.0)
        )
        trait_impact["exploration_bias_explore_users_avg"] = float(
            trait_impact_raw.get("exploration_bias_explore_users_avg", 0.0)
        )
        trait_impact["exploration_bias_explore_usage_bias"] = float(
            trait_impact_raw.get("exploration_bias_explore_usage_bias", 0.0)
        )
        trait_impact["exploration_bias_settle_users_avg"] = float(
            trait_impact_raw.get("exploration_bias_settle_users_avg", 0.0)
        )
        trait_impact["exploration_bias_settle_usage_bias"] = float(
            trait_impact_raw.get("exploration_bias_settle_usage_bias", 0.0)
        )
        trait_impact["exploration_bias_anchor_distance_delta"] = float(
            trait_impact_raw.get("exploration_bias_anchor_distance_delta", 0.0)
        )
        trait_impact["density_preference_guided_bias"] = float(
            trait_impact_raw.get("density_preference_guided_bias", 0.0)
        )
        trait_impact["density_preference_guided_total"] = float(
            trait_impact_raw.get("density_preference_guided_total", 0.0)
        )
        trait_impact["density_preference_seek_share"] = float(
            trait_impact_raw.get("density_preference_seek_share", 0.0)
        )
        trait_impact["density_preference_seek_users_avg"] = float(
            trait_impact_raw.get("density_preference_seek_users_avg", 0.0)
        )
        trait_impact["density_preference_seek_usage_bias"] = float(
            trait_impact_raw.get("density_preference_seek_usage_bias", 0.0)
        )
        trait_impact["density_preference_avoid_users_avg"] = float(
            trait_impact_raw.get("density_preference_avoid_users_avg", 0.0)
        )
        trait_impact["density_preference_avoid_usage_bias"] = float(
            trait_impact_raw.get("density_preference_avoid_usage_bias", 0.0)
        )
        trait_impact["density_preference_neighbor_count_avg"] = float(
            trait_impact_raw.get("density_preference_neighbor_count_avg", 0.0)
        )
        trait_impact["density_preference_center_distance_delta"] = float(
            trait_impact_raw.get("density_preference_center_distance_delta", 0.0)
        )
        trait_impact["persistence_holds_total"] = float(
            trait_impact_raw.get("persistence_holds_total", 0.0)
        )
        trait_impact["behavior_persistence_oscillation_switch_rate"] = float(
            trait_impact_raw.get("behavior_persistence_oscillation_switch_rate", 0.0)
        )
        trait_impact["behavior_persistence_oscillation_prevented_rate"] = float(
            trait_impact_raw.get("behavior_persistence_oscillation_prevented_rate", 0.0)
        )
        trait_impact["search_wander_switches_total"] = float(
            trait_impact_raw.get("search_wander_switches_total", 0.0)
        )
        trait_impact["search_wander_switches_prevented_total"] = float(
            trait_impact_raw.get("search_wander_switches_prevented_total", 0.0)
        )
        trait_impact["search_wander_oscillation_events_total"] = float(
            trait_impact_raw.get("search_wander_oscillation_events_total", 0.0)
        )

    seeds_text = ",".join(str(seed) for seed in seeds)

    return (
        "multi_runs: runs={runs} seeds=[{seeds}] "
        "extinctions={ext_count}/{runs} (taux={ext_rate:.2f}) "
        "gen_max_moy={avg_gen:.2f} "
        "pop_finale_moy={avg_pop:.2f} "
        "traits_finaux_moy:s={speed:.3f},m={metabolism:.3f},p={prudence:.3f},d={dominance:.3f},rk={risk_taking:.3f},r={repro:.3f},fp={food_perception:.3f},tp={threat_perception:.3f},bp={behavior_persistence:.3f},ex={exploration_bias:.3f},dp={density_preference:.3f},ee={energy_efficiency:.3f},er={exhaustion_resistance:.3f} "
        "memoire_moy:util={mem_food:.2f} dang={mem_danger:.2f} "
        "act_u={mem_food_share:.2f} act_d={mem_danger_share:.2f} "
        "freq_u={mem_food_freq:.2f} freq_d={mem_danger_freq:.2f} "
        "effet_u={mem_food_effect:.2f} effet_d={mem_danger_effect:.2f} "
        "social_moy:suivi={social_follow:.2f} fuite_boost={social_flee_boost:.2f} "
        "part_infl_tick={social_infl_share:.2f} infl_tick={social_infl_count:.2f} infl_moy_tick={social_infl_tick:.2f} "
        "freq_suivi={social_follow_freq:.2f} freq_boost={social_boost_freq:.2f} "
        "mult_tick={social_mult_tick:.2f} mult_moy={social_mult_total:.2f} "
        "traits_impact_moy:mem_mu={mem_mu:.3f} mem_sigma={mem_sigma:.3f} soc_mu={soc_mu:.3f} soc_sigma={soc_sigma:.3f} fp_mu={fp_mu:.3f} fp_sigma={fp_sigma:.3f} tp_mu={tp_mu:.3f} tp_sigma={tp_sigma:.3f} rk_mu={rk_mu:.3f} rk_sigma={rk_sigma:.3f} bp_mu={bp_mu:.3f} bp_sigma={bp_sigma:.3f} ex_mu={ex_mu:.3f} ex_sigma={ex_sigma:.3f} dp_mu={dp_mu:.3f} dp_sigma={dp_sigma:.3f} ee_mu={ee_mu:.3f} ee_sigma={ee_sigma:.3f} er_mu={er_mu:.3f} er_sigma={er_sigma:.3f} "
        "energy_obs_moy:drain_mult={drain_mult_obs:.3f} repro_mult={repro_mult_obs:.3f} drain_amt={drain_amt_obs:.3f} repro_amt={repro_amt_obs:.3f} "
        "bias_mem_u={bias_mem_u:+.3f} bias_mem_d={bias_mem_d:+.3f} "
        "bias_soc_suivi={bias_soc_follow:+.3f} bias_soc_fuite={bias_soc_flee:+.3f} bias_fp_det={bias_fp_det:+.3f} bias_fp_eat={bias_fp_eat:+.3f} bias_tp_fuite={bias_tp_flee:+.3f} bias_rk_fuite={bias_rk_flee:+.3f} bias_bp_inertie={bias_bp_hold:+.3f} bias_explore={bias_explore:+.3f} inertie_total_moy={bp_holds_total:.2f} "
        "osc_bp_moy:switch={bp_sw_total:.2f} bloc={bp_prev_total:.2f} events={bp_events_total:.2f} taux_switch={bp_sw_rate:.3f} taux_bloc={bp_prev_rate:.3f} "
        "exploration_moy:guides={ex_guided_total:.2f} part_explore={ex_explore_share:.3f} ex_mu={ex_explore_mu:.3f} st_mu={ex_settle_mu:.3f} ex_bias={ex_explore_bias:+.3f} st_bias={ex_settle_bias:+.3f} delta_ancre={ex_anchor_delta:+.3f} "
        "densite_moy:guides={dp_guided_total:.2f} part_seek={dp_seek_share:.3f} seek_mu={dp_seek_mu:.3f} avoid_mu={dp_avoid_mu:.3f} dp_bias={dp_guided_bias:+.3f} seek_bias={dp_seek_bias:+.3f} avoid_bias={dp_avoid_bias:+.3f} dens_voisins={dp_neighbors:.2f} delta_centre={dp_center_delta:+.3f} "
        "bias_ee_drain={bias_ee_drain:+.3f} bias_er_repro={bias_er_repro:+.3f} "
        "dominant_final_freq={dominant}(n={dom_count},part={dom_share:.2f})"
    ).format(
        runs=int(summary.get("runs", 0)),
        seeds=seeds_text,
        ext_count=int(summary.get("extinction_count", 0)),
        ext_rate=float(summary.get("extinction_rate", 0.0)),
        avg_gen=float(summary.get("avg_max_generation", 0.0)),
        avg_pop=float(summary.get("avg_final_population", 0.0)),
        speed=traits["speed"],
        metabolism=traits["metabolism"],
        prudence=traits["prudence"],
        dominance=traits["dominance"],
        risk_taking=traits["risk_taking"],
        repro=traits["repro_drive"],
        food_perception=traits["food_perception"],
        threat_perception=traits["threat_perception"],
        behavior_persistence=traits["behavior_persistence"],
        exploration_bias=traits["exploration_bias"],
        density_preference=traits["density_preference"],
        energy_efficiency=traits["energy_efficiency"],
        exhaustion_resistance=traits["exhaustion_resistance"],
        mem_food=memory["food_usage_total"],
        mem_danger=memory["danger_usage_total"],
        mem_food_share=memory["food_active_share"],
        mem_danger_share=memory["danger_active_share"],
        mem_food_freq=memory["food_usage_per_tick"],
        mem_danger_freq=memory["danger_usage_per_tick"],
        mem_food_effect=memory["food_effect_avg_distance"],
        mem_danger_effect=memory["danger_effect_avg_distance"],
        social_follow=social["follow_usage_total"],
        social_flee_boost=social["flee_boost_usage_total"],
        social_infl_share=social["influenced_share_last_tick"],
        social_infl_count=social["influenced_count_last_tick"],
        social_infl_tick=social["influenced_per_tick"],
        social_follow_freq=social["follow_usage_per_tick"],
        social_boost_freq=social["flee_boost_usage_per_tick"],
        social_mult_tick=social["flee_multiplier_avg_tick"],
        social_mult_total=social["flee_multiplier_avg_total"],
        mem_mu=trait_impact["memory_focus_mean"],
        mem_sigma=trait_impact["memory_focus_std"],
        soc_mu=trait_impact["social_sensitivity_mean"],
        soc_sigma=trait_impact["social_sensitivity_std"],
        fp_mu=trait_impact["food_perception_mean"],
        fp_sigma=trait_impact["food_perception_std"],
        tp_mu=trait_impact["threat_perception_mean"],
        tp_sigma=trait_impact["threat_perception_std"],
        rk_mu=trait_impact["risk_taking_mean"],
        rk_sigma=trait_impact["risk_taking_std"],
        bp_mu=trait_impact["behavior_persistence_mean"],
        bp_sigma=trait_impact["behavior_persistence_std"],
        ex_mu=trait_impact["exploration_bias_mean"],
        ex_sigma=trait_impact["exploration_bias_std"],
        dp_mu=trait_impact["density_preference_mean"],
        dp_sigma=trait_impact["density_preference_std"],
        ee_mu=trait_impact["energy_efficiency_mean"],
        ee_sigma=trait_impact["energy_efficiency_std"],
        er_mu=trait_impact["exhaustion_resistance_mean"],
        er_sigma=trait_impact["exhaustion_resistance_std"],
        drain_mult_obs=trait_impact["energy_drain_multiplier_observed"],
        repro_mult_obs=trait_impact["reproduction_cost_multiplier_observed"],
        drain_amt_obs=trait_impact["energy_drain_amount_observed"],
        repro_amt_obs=trait_impact["reproduction_cost_amount_observed"],
        bias_mem_u=trait_impact["memory_focus_food_bias"],
        bias_mem_d=trait_impact["memory_focus_danger_bias"],
        bias_soc_follow=trait_impact["social_sensitivity_follow_bias"],
        bias_soc_flee=trait_impact["social_sensitivity_flee_boost_bias"],
        bias_fp_det=trait_impact["food_perception_detection_bias"],
        bias_fp_eat=trait_impact["food_perception_consumption_bias"],
        bias_tp_flee=trait_impact["threat_perception_flee_bias"],
        bias_rk_flee=trait_impact["risk_taking_flee_bias"],
        bias_bp_hold=trait_impact["behavior_persistence_hold_bias"],
        bias_explore=trait_impact["exploration_bias_guided_bias"],
        bp_holds_total=trait_impact["persistence_holds_total"],
        bp_sw_total=trait_impact["search_wander_switches_total"],
        bp_prev_total=trait_impact["search_wander_switches_prevented_total"],
        bp_events_total=trait_impact["search_wander_oscillation_events_total"],
        bp_sw_rate=trait_impact["behavior_persistence_oscillation_switch_rate"],
        bp_prev_rate=trait_impact["behavior_persistence_oscillation_prevented_rate"],
        ex_guided_total=trait_impact["exploration_bias_guided_total"],
        ex_explore_share=trait_impact["exploration_bias_explore_share"],
        ex_explore_mu=trait_impact["exploration_bias_explore_users_avg"],
        ex_settle_mu=trait_impact["exploration_bias_settle_users_avg"],
        ex_explore_bias=trait_impact["exploration_bias_explore_usage_bias"],
        ex_settle_bias=trait_impact["exploration_bias_settle_usage_bias"],
        ex_anchor_delta=trait_impact["exploration_bias_anchor_distance_delta"],
        dp_guided_total=trait_impact["density_preference_guided_total"],
        dp_seek_share=trait_impact["density_preference_seek_share"],
        dp_seek_mu=trait_impact["density_preference_seek_users_avg"],
        dp_avoid_mu=trait_impact["density_preference_avoid_users_avg"],
        dp_guided_bias=trait_impact["density_preference_guided_bias"],
        dp_seek_bias=trait_impact["density_preference_seek_usage_bias"],
        dp_avoid_bias=trait_impact["density_preference_avoid_usage_bias"],
        dp_neighbors=trait_impact["density_preference_neighbor_count_avg"],
        dp_center_delta=trait_impact["density_preference_center_distance_delta"],
        bias_ee_drain=trait_impact["energy_efficiency_drain_bias"],
        bias_er_repro=trait_impact["exhaustion_resistance_reproduction_bias"],
        dominant=str(summary.get("most_frequent_final_dominant_group", "-")),
        dom_count=int(summary.get("most_frequent_final_dominant_group_count", 0)),
        dom_share=float(summary.get("most_frequent_final_dominant_group_share", 0.0)),
    )

def format_death_causes(stats: Dict[str, object], include_tick: bool = True) -> str:
    total = _read_cause_counts(stats.get("death_causes_total"))
    last_tick = _read_cause_counts(stats.get("death_causes_last_tick"))

    total_block = _format_cause_block(total, with_plus=False)
    if not include_tick:
        return f"causes_deces total[{total_block}]"

    tick_block = _format_cause_block(last_tick, with_plus=True)
    return f"causes_deces total[{total_block}] tick[{tick_block}]"


def format_population_dynamics(
    stats: Dict[str, object],
    previous_stats: Dict[str, object] | None = None,
) -> str:
    births_tick = int(stats.get("births_last_tick", 0))
    deaths_tick = int(stats.get("deaths_last_tick", 0))
    flees_tick = int(stats.get("flees_last_tick", 0))
    net_tick = births_tick - deaths_tick

    alive = int(stats.get("alive", 0))
    food_remaining = float(stats.get("food_remaining", 0.0))
    avg_energy = float(stats.get("avg_energy", 0.0))

    current_total_births = int(stats.get("total_births", 0))
    current_total_deaths = int(stats.get("total_deaths", 0))
    current_total_flees = int(stats.get("total_flees", 0))
    current_total_food_memory_guided = int(stats.get("total_food_memory_guided_moves", 0))
    current_total_danger_memory_avoid = int(stats.get("total_danger_memory_avoid_moves", 0))
    current_total_social_follow = int(stats.get("total_social_follow_moves", 0))
    current_total_social_flee_boost = int(stats.get("total_social_flee_boosted", 0))
    current_total_social_influenced = int(stats.get("total_social_influenced_creatures", 0))
    current_total_food_detection = int(stats.get("total_food_detection_moves", 0))
    current_total_food_consumption = int(stats.get("total_food_consumptions", 0))
    current_total_threat_detection = int(stats.get("total_threat_detection_flee", 0))
    current_total_persistence_holds = int(stats.get("total_persistence_holds", 0))
    current_total_exploration_guided = int(stats.get("total_exploration_bias_guided_moves", 0))
    current_total_exploration_explore = int(stats.get("total_exploration_bias_explore_moves", 0))
    current_total_exploration_settle = int(stats.get("total_exploration_bias_settle_moves", 0))
    current_total_density_guided = int(stats.get("total_density_preference_guided_moves", 0))
    current_total_density_seek = int(stats.get("total_density_preference_seek_moves", 0))
    current_total_density_avoid = int(stats.get("total_density_preference_avoid_moves", 0))
    current_total_search_wander_switches = int(stats.get("total_search_wander_switches", 0))
    current_total_search_wander_switches_prevented = int(
        stats.get("total_search_wander_switches_prevented", 0)
    )

    fleeing_creatures_tick = _read_fleeing_ids(stats.get("fleeing_creatures_last_tick"))
    avg_flee_threat_distance_tick = float(stats.get("avg_flee_threat_distance_last_tick", 0.0))

    food_memory_active = int(stats.get("creatures_with_food_memory", 0))
    danger_memory_active = int(stats.get("creatures_with_danger_memory", 0))
    food_memory_active_share = float(stats.get("food_memory_active_share", 0.0))
    danger_memory_active_share = float(stats.get("danger_memory_active_share", 0.0))
    food_memory_guided_tick = int(stats.get("food_memory_guided_moves_last_tick", 0))
    danger_memory_avoid_tick = int(stats.get("danger_memory_avoid_moves_last_tick", 0))
    food_memory_usage_alive_tick = float(stats.get("food_memory_usage_per_alive_tick", 0.0))
    danger_memory_usage_alive_tick = float(stats.get("danger_memory_usage_per_alive_tick", 0.0))
    food_memory_effect_tick = float(stats.get("food_memory_effect_avg_distance_tick", 0.0))
    danger_memory_effect_tick = float(stats.get("danger_memory_effect_avg_distance_tick", 0.0))

    social_follow_tick = int(stats.get("social_follow_moves_last_tick", 0))
    social_flee_boost_tick = int(stats.get("social_flee_boosted_last_tick", 0))
    social_influenced_tick = int(stats.get("social_influenced_creatures_last_tick", 0))
    social_influenced_share_tick = float(stats.get("social_influenced_share_last_tick", 0.0))
    social_influenced_rate_total = float(stats.get("social_influenced_per_tick_total", 0.0))
    avg_social_flee_multiplier_tick = float(stats.get("avg_social_flee_multiplier_last_tick", 1.0))
    avg_social_flee_multiplier_total = float(stats.get("social_flee_multiplier_avg_total", 1.0))

    food_detection_tick = int(stats.get("food_detection_moves_last_tick", 0))
    food_consumption_tick = int(stats.get("food_consumptions_last_tick", 0))
    threat_detection_tick = int(stats.get("threat_detection_flee_last_tick", 0))
    persistence_holds_tick = int(stats.get("persistence_holds_last_tick", 0))
    exploration_guided_tick = int(stats.get("exploration_bias_guided_moves_last_tick", 0))
    exploration_explore_tick = int(stats.get("exploration_bias_explore_moves_last_tick", 0))
    exploration_settle_tick = int(stats.get("exploration_bias_settle_moves_last_tick", 0))
    exploration_explore_share_tick = float(stats.get("exploration_bias_explore_share_last_tick", 0.0))
    exploration_explore_users_avg_tick = float(stats.get("exploration_bias_explore_users_avg_tick", 0.0))
    exploration_settle_users_avg_tick = float(stats.get("exploration_bias_settle_users_avg_tick", 0.0))
    exploration_explore_usage_bias_tick = float(stats.get("exploration_bias_explore_usage_bias_tick", 0.0))
    exploration_settle_usage_bias_tick = float(stats.get("exploration_bias_settle_usage_bias_tick", 0.0))
    exploration_anchor_delta_tick = float(
        stats.get("avg_exploration_bias_anchor_distance_delta_last_tick", 0.0)
    )
    density_guided_tick = int(stats.get("density_preference_guided_moves_last_tick", 0))
    density_seek_tick = int(stats.get("density_preference_seek_moves_last_tick", 0))
    density_avoid_tick = int(stats.get("density_preference_avoid_moves_last_tick", 0))
    density_seek_share_tick = float(stats.get("density_preference_seek_share_last_tick", 0.0))
    density_seek_users_avg_tick = float(stats.get("density_preference_seek_users_avg_tick", 0.0))
    density_avoid_users_avg_tick = float(stats.get("density_preference_avoid_users_avg_tick", 0.0))
    density_guided_usage_bias_tick = float(stats.get("density_preference_guided_usage_bias_tick", 0.0))
    density_seek_usage_bias_tick = float(stats.get("density_preference_seek_usage_bias_tick", 0.0))
    density_avoid_usage_bias_tick = float(stats.get("density_preference_avoid_usage_bias_tick", 0.0))
    density_neighbor_count_tick = float(stats.get("avg_density_preference_neighbor_count_last_tick", 0.0))
    density_center_delta_tick = float(
        stats.get("avg_density_preference_center_distance_delta_last_tick", 0.0)
    )
    search_wander_switches_tick = int(stats.get("search_wander_switches_last_tick", 0))
    search_wander_switches_prevented_tick = int(
        stats.get("search_wander_switches_prevented_last_tick", 0)
    )
    search_wander_events_tick = int(stats.get("search_wander_oscillation_events_last_tick", 0))
    search_wander_switch_rate_tick = float(stats.get("search_wander_switch_rate_last_tick", 0.0))
    search_wander_prevented_rate_tick = float(stats.get("search_wander_prevented_rate_last_tick", 0.0))
    food_detection_usage_alive_tick = float(stats.get("food_detection_usage_per_alive_tick", 0.0))
    food_consumption_usage_alive_tick = float(stats.get("food_consumption_usage_per_alive_tick", 0.0))
    threat_detection_usage_alive_tick = float(stats.get("threat_detection_usage_per_alive_tick", 0.0))

    avg_prudence = float(stats.get("avg_prudence", 0.0))
    avg_dominance = float(stats.get("avg_dominance", 0.0))
    avg_risk_taking = float(stats.get("avg_risk_taking", 0.0))
    avg_repro_drive = float(stats.get("avg_repro_drive", 0.0))
    avg_memory_focus = float(stats.get("avg_memory_focus", 0.0))
    avg_social_sensitivity = float(stats.get("avg_social_sensitivity", 0.0))
    avg_food_perception = float(stats.get("avg_food_perception", 0.0))
    avg_threat_perception = float(stats.get("avg_threat_perception", 0.0))
    avg_behavior_persistence = float(stats.get("avg_behavior_persistence", 0.0))
    avg_exploration_bias = float(stats.get("avg_exploration_bias", 0.0))
    avg_density_preference = float(stats.get("avg_density_preference", 0.0))
    avg_energy_efficiency = float(stats.get("avg_energy_efficiency", 0.0))
    avg_exhaustion_resistance = float(stats.get("avg_exhaustion_resistance", 0.0))
    std_memory_focus = float(stats.get("std_memory_focus", 0.0))
    std_social_sensitivity = float(stats.get("std_social_sensitivity", 0.0))
    std_food_perception = float(stats.get("std_food_perception", 0.0))
    std_threat_perception = float(stats.get("std_threat_perception", 0.0))
    std_risk_taking = float(stats.get("std_risk_taking", 0.0))
    std_behavior_persistence = float(stats.get("std_behavior_persistence", 0.0))
    std_exploration_bias = float(stats.get("std_exploration_bias", 0.0))
    std_density_preference = float(stats.get("std_density_preference", 0.0))
    std_energy_efficiency = float(stats.get("std_energy_efficiency", 0.0))
    std_exhaustion_resistance = float(stats.get("std_exhaustion_resistance", 0.0))
    avg_effective_energy_drain_multiplier = float(stats.get("avg_effective_energy_drain_multiplier", 0.0))
    avg_reproduction_cost_multiplier = float(stats.get("avg_reproduction_cost_multiplier", 0.0))
    avg_energy_drain_multiplier_observed_tick = float(
        stats.get("avg_energy_drain_multiplier_observed_last_tick", 0.0)
    )
    avg_reproduction_cost_multiplier_observed_tick = float(
        stats.get("avg_reproduction_cost_multiplier_observed_last_tick", 0.0)
    )
    avg_energy_drain_amount_last_tick = float(stats.get("avg_energy_drain_amount_last_tick", 0.0))
    avg_reproduction_cost_amount_last_tick = float(stats.get("avg_reproduction_cost_amount_last_tick", 0.0))
    energy_efficiency_drain_bias_tick = float(stats.get("energy_efficiency_drain_usage_bias_tick", 0.0))
    exhaustion_resistance_reproduction_bias_tick = float(
        stats.get("exhaustion_resistance_reproduction_usage_bias_tick", 0.0)
    )
    memory_focus_food_bias_tick = float(stats.get("memory_focus_food_usage_bias_tick", 0.0))
    memory_focus_danger_bias_tick = float(stats.get("memory_focus_danger_usage_bias_tick", 0.0))
    social_sensitivity_follow_bias_tick = float(stats.get("social_sensitivity_follow_usage_bias_tick", 0.0))
    social_sensitivity_flee_boost_bias_tick = float(stats.get("social_sensitivity_flee_boost_usage_bias_tick", 0.0))
    food_perception_detection_bias_tick = float(stats.get("food_perception_detection_usage_bias_tick", 0.0))
    food_perception_consumption_bias_tick = float(stats.get("food_perception_consumption_usage_bias_tick", 0.0))
    threat_perception_flee_bias_tick = float(stats.get("threat_perception_flee_usage_bias_tick", 0.0))
    risk_taking_flee_bias_tick = float(stats.get("risk_taking_flee_usage_bias_tick", 0.0))
    behavior_persistence_hold_bias_tick = float(
        stats.get("behavior_persistence_hold_usage_bias_tick", 0.0)
    )
    exploration_bias_guided_usage_bias_tick = float(
        stats.get("exploration_bias_guided_usage_bias_tick", 0.0)
    )

    alive_delta = 0
    births_log = births_tick
    deaths_log = deaths_tick
    flees_log = flees_tick
    food_memory_guided_log = food_memory_guided_tick
    danger_memory_avoid_log = danger_memory_avoid_tick
    social_follow_log = social_follow_tick
    social_flee_boost_log = social_flee_boost_tick
    social_influenced_log = social_influenced_tick
    food_detection_log = food_detection_tick
    food_consumption_log = food_consumption_tick
    threat_detection_log = threat_detection_tick
    persistence_holds_log = persistence_holds_tick
    exploration_guided_log = exploration_guided_tick
    exploration_explore_log = exploration_explore_tick
    exploration_settle_log = exploration_settle_tick
    density_guided_log = density_guided_tick
    density_seek_log = density_seek_tick
    density_avoid_log = density_avoid_tick
    search_wander_switches_log = search_wander_switches_tick
    search_wander_switches_prevented_log = search_wander_switches_prevented_tick

    if previous_stats is not None:
        previous_alive = int(previous_stats.get("alive", alive))
        previous_total_births = int(previous_stats.get("total_births", current_total_births))
        previous_total_deaths = int(previous_stats.get("total_deaths", current_total_deaths))
        previous_total_flees = int(previous_stats.get("total_flees", current_total_flees))
        previous_total_food_memory_guided = int(
            previous_stats.get("total_food_memory_guided_moves", current_total_food_memory_guided)
        )
        previous_total_danger_memory_avoid = int(
            previous_stats.get("total_danger_memory_avoid_moves", current_total_danger_memory_avoid)
        )
        previous_total_social_follow = int(
            previous_stats.get("total_social_follow_moves", current_total_social_follow)
        )
        previous_total_social_flee_boost = int(
            previous_stats.get("total_social_flee_boosted", current_total_social_flee_boost)
        )
        previous_total_social_influenced = int(
            previous_stats.get("total_social_influenced_creatures", current_total_social_influenced)
        )

        previous_total_food_detection = int(
            previous_stats.get("total_food_detection_moves", current_total_food_detection)
        )
        previous_total_food_consumption = int(
            previous_stats.get("total_food_consumptions", current_total_food_consumption)
        )
        previous_total_threat_detection = int(
            previous_stats.get("total_threat_detection_flee", current_total_threat_detection)
        )
        previous_total_persistence_holds = int(
            previous_stats.get("total_persistence_holds", current_total_persistence_holds)
        )
        previous_total_exploration_guided = int(
            previous_stats.get("total_exploration_bias_guided_moves", current_total_exploration_guided)
        )
        previous_total_exploration_explore = int(
            previous_stats.get("total_exploration_bias_explore_moves", current_total_exploration_explore)
        )
        previous_total_exploration_settle = int(
            previous_stats.get("total_exploration_bias_settle_moves", current_total_exploration_settle)
        )
        previous_total_density_guided = int(
            previous_stats.get("total_density_preference_guided_moves", current_total_density_guided)
        )
        previous_total_density_seek = int(
            previous_stats.get("total_density_preference_seek_moves", current_total_density_seek)
        )
        previous_total_density_avoid = int(
            previous_stats.get("total_density_preference_avoid_moves", current_total_density_avoid)
        )
        previous_total_search_wander_switches = int(
            previous_stats.get("total_search_wander_switches", current_total_search_wander_switches)
        )
        previous_total_search_wander_switches_prevented = int(
            previous_stats.get(
                "total_search_wander_switches_prevented",
                current_total_search_wander_switches_prevented,
            )
        )
        alive_delta = alive - previous_alive
        births_log = max(0, current_total_births - previous_total_births)
        deaths_log = max(0, current_total_deaths - previous_total_deaths)
        flees_log = max(0, current_total_flees - previous_total_flees)
        food_memory_guided_log = max(0, current_total_food_memory_guided - previous_total_food_memory_guided)
        danger_memory_avoid_log = max(0, current_total_danger_memory_avoid - previous_total_danger_memory_avoid)
        social_follow_log = max(0, current_total_social_follow - previous_total_social_follow)
        social_flee_boost_log = max(0, current_total_social_flee_boost - previous_total_social_flee_boost)
        social_influenced_log = max(0, current_total_social_influenced - previous_total_social_influenced)
        food_detection_log = max(0, current_total_food_detection - previous_total_food_detection)
        food_consumption_log = max(0, current_total_food_consumption - previous_total_food_consumption)
        threat_detection_log = max(0, current_total_threat_detection - previous_total_threat_detection)
        persistence_holds_log = max(
            0,
            current_total_persistence_holds - previous_total_persistence_holds,
        )
        exploration_guided_log = max(
            0,
            current_total_exploration_guided - previous_total_exploration_guided,
        )
        exploration_explore_log = max(
            0,
            current_total_exploration_explore - previous_total_exploration_explore,
        )
        exploration_settle_log = max(
            0,
            current_total_exploration_settle - previous_total_exploration_settle,
        )
        density_guided_log = max(0, current_total_density_guided - previous_total_density_guided)
        density_seek_log = max(0, current_total_density_seek - previous_total_density_seek)
        density_avoid_log = max(0, current_total_density_avoid - previous_total_density_avoid)
        search_wander_switches_log = max(
            0,
            current_total_search_wander_switches - previous_total_search_wander_switches,
        )
        search_wander_switches_prevented_log = max(
            0,
            current_total_search_wander_switches_prevented - previous_total_search_wander_switches_prevented,
        )

    net_log = births_log - deaths_log
    search_wander_events_log = search_wander_switches_log + search_wander_switches_prevented_log
    search_wander_switch_rate_log = (
        search_wander_switches_log / search_wander_events_log if search_wander_events_log > 0 else 0.0
    )
    search_wander_prevented_rate_log = (
        search_wander_switches_prevented_log / search_wander_events_log if search_wander_events_log > 0 else 0.0
    )
    dynamic_log = _classify_trend(primary=alive_delta, secondary=net_log)
    dynamic_tick = _classify_trend(primary=net_tick, secondary=net_tick)

    food_pressure = _classify_food_pressure(alive, food_remaining)
    food_per_alive = _format_food_per_alive(alive, food_remaining)
    energy_state = _classify_energy(avg_energy)

    causes_tick = _read_cause_counts(stats.get("death_causes_last_tick"))
    causes_log = causes_tick
    if previous_stats is not None:
        current_total_causes = _read_cause_counts(stats.get("death_causes_total"))
        previous_total_causes = _read_cause_counts(previous_stats.get("death_causes_total"))
        causes_log = _delta_cause_counts(current_total_causes, previous_total_causes)

    dominant_tick = _dominant_death_cause(causes_tick)
    dominant_log = _dominant_death_cause(causes_log)

    if deaths_tick <= 0:
        mortality_tick = "mortalite_tick:nulle"
    else:
        mortality_tick = f"mortalite_tick:{deaths_tick} dominante_tick:{dominant_tick}"

    if deaths_log <= 0:
        mortality_log = "mortalite_log:nulle"
    else:
        mortality_log = f"mortalite_log:{deaths_log} dominante_log:{dominant_log}"

    fleeing_block = _format_fleeing_ids(fleeing_creatures_tick, max_ids=6)
    threat_distance_block = "n/a" if flees_tick <= 0 else f"{avg_flee_threat_distance_tick:.2f}"

    return (
        f"dynamique_log:{dynamic_log} "
        f"dynamique_tick:{dynamic_tick} "
        f"delta_log_vivants:{alive_delta:+d} "
        f"net_log_naissances_deces:{net_log:+d} "
        f"net_tick_naissances_deces:{net_tick:+d} "
        f"fuites_log:{flees_log} "
        f"fuites_tick:{flees_tick} "
        f"fuyards_tick:{fleeing_block} "
        f"dist_menace_moy_tick:{threat_distance_block} "
        f"memoire_active:utile={food_memory_active} danger={danger_memory_active} "
        f"memoire_part:utile={food_memory_active_share:.2f} danger={danger_memory_active_share:.2f} "
        f"memoire_log:utile={food_memory_guided_log} danger={danger_memory_avoid_log} "
        f"memoire_tick:utile={food_memory_guided_tick} danger={danger_memory_avoid_tick} "
        f"memoire_freq_tick:utile={food_memory_usage_alive_tick:.2f} danger={danger_memory_usage_alive_tick:.2f} "
        f"memoire_effet_tick:utile={food_memory_effect_tick:.2f} danger={danger_memory_effect_tick:.2f} "
        f"social_log:suivi={social_follow_log} fuite_boost={social_flee_boost_log} infl={social_influenced_log} "
        f"social_tick:suivi={social_follow_tick} fuite_boost={social_flee_boost_tick} infl={social_influenced_tick} "
        f"perception_log:det={food_detection_log} eat={food_consumption_log} fuite={threat_detection_log} "
        f"perception_tick:det={food_detection_tick} eat={food_consumption_tick} fuite={threat_detection_tick} "
        f"exploration_log:guides={exploration_guided_log} explore={exploration_explore_log} settle={exploration_settle_log} "
        f"exploration_tick:guides={exploration_guided_tick} explore={exploration_explore_tick} settle={exploration_settle_tick} part_explore={exploration_explore_share_tick:.2f} ex_mu={exploration_explore_users_avg_tick:.2f} st_mu={exploration_settle_users_avg_tick:.2f} ex_bias={exploration_explore_usage_bias_tick:+.2f} st_bias={exploration_settle_usage_bias_tick:+.2f} delta_ancre={exploration_anchor_delta_tick:+.2f} "
        f"densite_log:guides={density_guided_log} seek={density_seek_log} avoid={density_avoid_log} "
        f"densite_tick:guides={density_guided_tick} seek={density_seek_tick} avoid={density_avoid_tick} part_seek={density_seek_share_tick:.2f} seek_mu={density_seek_users_avg_tick:.2f} avoid_mu={density_avoid_users_avg_tick:.2f} dp_bias={density_guided_usage_bias_tick:+.2f} seek_bias={density_seek_usage_bias_tick:+.2f} avoid_bias={density_avoid_usage_bias_tick:+.2f} dens_voisins={density_neighbor_count_tick:.2f} delta_centre={density_center_delta_tick:+.2f} "
        f"inertie_log:{persistence_holds_log} inertie_tick:{persistence_holds_tick} "
        f"oscill_log:sw={search_wander_switches_log} bloc={search_wander_switches_prevented_log} evts={search_wander_events_log} taux_sw={search_wander_switch_rate_log:.2f} taux_bloc={search_wander_prevented_rate_log:.2f} "
        f"oscill_tick:sw={search_wander_switches_tick} bloc={search_wander_switches_prevented_tick} evts={search_wander_events_tick} taux_sw={search_wander_switch_rate_tick:.2f} taux_bloc={search_wander_prevented_rate_tick:.2f} "
        f"perception_freq_tick:det={food_detection_usage_alive_tick:.2f} eat={food_consumption_usage_alive_tick:.2f} fuite={threat_detection_usage_alive_tick:.2f} "
        f"part_infl={social_influenced_share_tick:.2f} infl_moy_tick={social_influenced_rate_total:.2f} "
        f"mult_fuite={avg_social_flee_multiplier_tick:.2f} mult_fuite_moy={avg_social_flee_multiplier_total:.2f} "
        f"traits_comp_moy:pru={avg_prudence:.2f},dom={avg_dominance:.2f},rk={avg_risk_taking:.2f},rep={avg_repro_drive:.2f},mem={avg_memory_focus:.2f},soc={avg_social_sensitivity:.2f},fp={avg_food_perception:.2f},tp={avg_threat_perception:.2f},bp={avg_behavior_persistence:.2f},ex={avg_exploration_bias:.2f},dp={avg_density_preference:.2f},ee={avg_energy_efficiency:.2f},er={avg_exhaustion_resistance:.2f} "
        f"traits_disp:mem_sigma={std_memory_focus:.2f} soc_sigma={std_social_sensitivity:.2f} fp_sigma={std_food_perception:.2f} tp_sigma={std_threat_perception:.2f} rk_sigma={std_risk_taking:.2f} bp_sigma={std_behavior_persistence:.2f} ex_sigma={std_exploration_bias:.2f} dp_sigma={std_density_preference:.2f} ee_sigma={std_energy_efficiency:.2f} er_sigma={std_exhaustion_resistance:.2f} "
        f"energie_traits_effets:drain_mult={avg_effective_energy_drain_multiplier:.2f} repro_mult={avg_reproduction_cost_multiplier:.2f} "
        f"drain_obs_mult={avg_energy_drain_multiplier_observed_tick:.2f} repro_obs_mult={avg_reproduction_cost_multiplier_observed_tick:.2f} "
        f"drain_obs={avg_energy_drain_amount_last_tick:.2f} repro_obs={avg_reproduction_cost_amount_last_tick:.2f} "
        f"traits_bias_tick:mem_u={memory_focus_food_bias_tick:+.2f} mem_d={memory_focus_danger_bias_tick:+.2f} "
        f"soc_suivi={social_sensitivity_follow_bias_tick:+.2f} soc_fuite={social_sensitivity_flee_boost_bias_tick:+.2f} "
        f"bp_inertie={behavior_persistence_hold_bias_tick:+.2f} ex_guide={exploration_bias_guided_usage_bias_tick:+.2f} ex_explore={exploration_explore_usage_bias_tick:+.2f} ex_settle={exploration_settle_usage_bias_tick:+.2f} dp_guide={density_guided_usage_bias_tick:+.2f} dp_seek={density_seek_usage_bias_tick:+.2f} dp_avoid={density_avoid_usage_bias_tick:+.2f} ee_drain={energy_efficiency_drain_bias_tick:+.2f} er_repro={exhaustion_resistance_reproduction_bias_tick:+.2f} "
        f"perception_bias_tick:fp_det={food_perception_detection_bias_tick:+.2f} fp_eat={food_perception_consumption_bias_tick:+.2f} tp_fuite={threat_perception_flee_bias_tick:+.2f} rk_fuite={risk_taking_flee_bias_tick:+.2f} "
        f"nourriture_par_vivant:{food_per_alive} "
        f"pression_nourriture:{food_pressure} "
        f"energie:{energy_state} "
        f"{mortality_log} "
        f"{mortality_tick}"
    )

def _classify_trend(primary: int, secondary: int) -> str:
    if primary > 0 or secondary > 0:
        return "croissance"
    if primary < 0 or secondary < 0:
        return "declin"
    return "stagnation"


def _classify_food_pressure(alive: int, food_remaining: float) -> str:
    if alive <= 0:
        return "n/a"

    food_per_alive = food_remaining / alive
    if food_per_alive < 15.0:
        return "forte"
    if food_per_alive < 35.0:
        return "moderee"
    return "faible"


def _format_food_per_alive(alive: int, food_remaining: float) -> str:
    if alive <= 0:
        return "n/a"
    return f"{(food_remaining / alive):.1f}"


def _classify_energy(avg_energy: float) -> str:
    if avg_energy < 20.0:
        return "basse"
    if avg_energy < 45.0:
        return "moyenne"
    return "haute"


def _read_cause_counts(raw: object) -> Dict[str, int]:
    if not isinstance(raw, dict):
        return {"starvation": 0, "exhaustion": 0, "unknown": 0}
    return {
        "starvation": int(raw.get("starvation", 0)),
        "exhaustion": int(raw.get("exhaustion", 0)),
        "unknown": int(raw.get("unknown", 0)),
    }


def _delta_cause_counts(current: Dict[str, int], previous: Dict[str, int]) -> Dict[str, int]:
    return {
        "starvation": max(0, current["starvation"] - previous["starvation"]),
        "exhaustion": max(0, current["exhaustion"] - previous["exhaustion"]),
        "unknown": max(0, current["unknown"] - previous["unknown"]),
    }


def _dominant_death_cause(causes: Dict[str, int]) -> str:
    labels = {
        "starvation": "faim",
        "exhaustion": "epuisement",
        "unknown": "autre",
    }
    cause_name = max(causes, key=causes.get)
    return labels.get(cause_name, "autre")


def _format_cause_block(causes: Dict[str, int], with_plus: bool) -> str:
    sign = "+" if with_plus else ""
    return (
        f"faim:{sign}{causes['starvation']} "
        f"epuisement:{sign}{causes['exhaustion']} "
        f"autre:{sign}{causes['unknown']}"
    )


def _read_fleeing_ids(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(value) for value in raw]


def _format_fleeing_ids(creature_ids: list[str], max_ids: int) -> str:
    if max_ids <= 0:
        raise ValueError("max_ids must be > 0")
    if not creature_ids:
        return "none"

    shown = creature_ids[:max_ids]
    hidden = len(creature_ids) - len(shown)
    if hidden <= 0:
        return ",".join(shown)
    return f"{','.join(shown)},+{hidden}"

