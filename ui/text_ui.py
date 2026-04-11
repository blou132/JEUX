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
    fleeing_creatures_tick = _read_fleeing_ids(stats.get("fleeing_creatures_last_tick"))
    avg_flee_threat_distance_tick = float(stats.get("avg_flee_threat_distance_last_tick", 0.0))

    avg_prudence = float(stats.get("avg_prudence", 0.0))
    avg_dominance = float(stats.get("avg_dominance", 0.0))
    avg_repro_drive = float(stats.get("avg_repro_drive", 0.0))

    alive_delta = 0
    births_log = births_tick
    deaths_log = deaths_tick
    flees_log = flees_tick

    if previous_stats is not None:
        previous_alive = int(previous_stats.get("alive", alive))
        previous_total_births = int(previous_stats.get("total_births", current_total_births))
        previous_total_deaths = int(previous_stats.get("total_deaths", current_total_deaths))
        previous_total_flees = int(previous_stats.get("total_flees", current_total_flees))

        alive_delta = alive - previous_alive
        births_log = max(0, current_total_births - previous_total_births)
        deaths_log = max(0, current_total_deaths - previous_total_deaths)
        flees_log = max(0, current_total_flees - previous_total_flees)

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
