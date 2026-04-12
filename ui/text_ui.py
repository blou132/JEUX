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
        "tick | population | vivants | morts | nourriture | energie_moy | age_moy | gen_moy | naissances(T/dT) | deces(T/dT) | vitesse_moy | metabolisme_moy | prudence_moy | dominance_moy | repro_moy"
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
        f"{float(stats['avg_repro_drive']):9.3f}"
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
        "repro_drive": 0.0,
    }
    if isinstance(traits_raw, dict):
        traits["speed"] = float(traits_raw.get("speed", 0.0))
        traits["metabolism"] = float(traits_raw.get("metabolism", 0.0))
        traits["prudence"] = float(traits_raw.get("prudence", 0.0))
        traits["dominance"] = float(traits_raw.get("dominance", 0.0))
        traits["repro_drive"] = float(traits_raw.get("repro_drive", 0.0))

    return (
        "synthese_run: "
        "dominant_final={dominant}(part={dominant_share:.2f}) "
        "plus_stable={stable}(n={stable_count}) "
        "plus_hausse={rising}(n={rising_count}) "
        "zones_finales:riches={rich} neutres={neutral} pauvres={poor} "
        "traits_moy:s={speed:.3f},m={metabolism:.3f},p={prudence:.3f},d={dominance:.3f},r={repro:.3f} "
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
        repro=traits["repro_drive"],
        observed_logs=int(summary.get("observed_logs", 0)),
    )
def format_multi_run_summary(summary: Dict[str, object]) -> str:
    seeds_raw = summary.get("seeds")
    traits_raw = summary.get("avg_final_traits")

    seeds: list[int] = []
    if isinstance(seeds_raw, list):
        seeds = [int(seed) for seed in seeds_raw]

    traits = {
        "speed": 0.0,
        "metabolism": 0.0,
        "prudence": 0.0,
        "dominance": 0.0,
        "repro_drive": 0.0,
    }
    if isinstance(traits_raw, dict):
        traits["speed"] = float(traits_raw.get("speed", 0.0))
        traits["metabolism"] = float(traits_raw.get("metabolism", 0.0))
        traits["prudence"] = float(traits_raw.get("prudence", 0.0))
        traits["dominance"] = float(traits_raw.get("dominance", 0.0))
        traits["repro_drive"] = float(traits_raw.get("repro_drive", 0.0))

    seeds_text = ",".join(str(seed) for seed in seeds)

    return (
        "multi_runs: runs={runs} seeds=[{seeds}] "
        "extinctions={ext_count}/{runs} (taux={ext_rate:.2f}) "
        "gen_max_moy={avg_gen:.2f} "
        "pop_finale_moy={avg_pop:.2f} "
        "traits_finaux_moy:s={speed:.3f},m={metabolism:.3f},p={prudence:.3f},d={dominance:.3f},r={repro:.3f} "
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
        repro=traits["repro_drive"],
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

    fleeing_creatures_tick = _read_fleeing_ids(stats.get("fleeing_creatures_last_tick"))
    avg_flee_threat_distance_tick = float(stats.get("avg_flee_threat_distance_last_tick", 0.0))

    food_memory_active = int(stats.get("creatures_with_food_memory", 0))
    danger_memory_active = int(stats.get("creatures_with_danger_memory", 0))
    food_memory_guided_tick = int(stats.get("food_memory_guided_moves_last_tick", 0))
    danger_memory_avoid_tick = int(stats.get("danger_memory_avoid_moves_last_tick", 0))

    avg_prudence = float(stats.get("avg_prudence", 0.0))
    avg_dominance = float(stats.get("avg_dominance", 0.0))
    avg_repro_drive = float(stats.get("avg_repro_drive", 0.0))

    alive_delta = 0
    births_log = births_tick
    deaths_log = deaths_tick
    flees_log = flees_tick
    food_memory_guided_log = food_memory_guided_tick
    danger_memory_avoid_log = danger_memory_avoid_tick

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

        alive_delta = alive - previous_alive
        births_log = max(0, current_total_births - previous_total_births)
        deaths_log = max(0, current_total_deaths - previous_total_deaths)
        flees_log = max(0, current_total_flees - previous_total_flees)
        food_memory_guided_log = max(0, current_total_food_memory_guided - previous_total_food_memory_guided)
        danger_memory_avoid_log = max(0, current_total_danger_memory_avoid - previous_total_danger_memory_avoid)

    net_log = births_log - deaths_log
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
        f"memoire_log:utile={food_memory_guided_log} danger={danger_memory_avoid_log} "
        f"memoire_tick:utile={food_memory_guided_tick} danger={danger_memory_avoid_tick} "
        f"traits_comp_moy:pru={avg_prudence:.2f},dom={avg_dominance:.2f},rep={avg_repro_drive:.2f} "
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

