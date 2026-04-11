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
        "tick | population | vivants | morts | nourriture | energie_moy | age_moy | gen_moy | naissances(T/dT) | deces(T/dT) | vitesse_moy | metabolisme_moy"
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
        f"{float(stats['avg_metabolism']):15.3f}"
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
    alive = int(stats.get("alive", 0))
    food_remaining = float(stats.get("food_remaining", 0.0))
    avg_energy = float(stats.get("avg_energy", 0.0))

    net_tick = births_tick - deaths_tick
    alive_delta = 0
    if previous_stats is not None:
        alive_delta = alive - int(previous_stats.get("alive", alive))

    if net_tick > 0 or alive_delta > 0:
        dynamic = "croissance"
    elif net_tick < 0 or alive_delta < 0:
        dynamic = "declin"
    else:
        dynamic = "stagnation"

    food_pressure = _classify_food_pressure(alive, food_remaining)
    energy_state = _classify_energy(avg_energy)

    causes = _read_cause_counts(stats.get("death_causes_last_tick"))
    dominant_cause = _dominant_death_cause(causes)

    if deaths_tick <= 0:
        mortality = "mortalite_tick:nulle"
    else:
        mortality = f"mortalite_tick:{deaths_tick} dominante:{dominant_cause}"

    return (
        f"dynamique:{dynamic} "
        f"delta_log_vivants:{alive_delta:+d} "
        f"net_tick_naissances_deces:{net_tick:+d} "
        f"pression_nourriture:{food_pressure} "
        f"energie:{energy_state} "
        f"{mortality}"
    )


def _classify_food_pressure(alive: int, food_remaining: float) -> str:
    if alive <= 0:
        return "n/a"

    food_per_alive = food_remaining / alive
    if food_per_alive < 15.0:
        return "forte"
    if food_per_alive < 35.0:
        return "moderee"
    return "faible"


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