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
        "tick | total | alive | dead | food_left | avg_energy | avg_age | births(T/+d) | deaths(T/+d) | avg_speed | avg_metabolism"
    )


def format_stats_line(tick: int, stats: Dict[str, float | int]) -> str:
    births_block = f"{int(stats['total_births'])}(+{int(stats['births_last_tick'])})"
    deaths_block = f"{int(stats['total_deaths'])}(+{int(stats['deaths_last_tick'])})"

    return (
        f"{tick:4d} | "
        f"{int(stats['population']):5d} | "
        f"{int(stats['alive']):5d} | "
        f"{int(stats['dead']):4d} | "
        f"{float(stats['food_remaining']):9.1f} | "
        f"{float(stats['avg_energy']):10.2f} | "
        f"{float(stats['avg_age']):7.2f} | "
        f"{births_block:11s} | "
        f"{deaths_block:11s} | "
        f"{float(stats['avg_speed']):9.3f} | "
        f"{float(stats['avg_metabolism']):13.3f}"
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
