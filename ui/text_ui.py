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
        "tick | pop(alive/total) | food_left | avg_energy | avg_age | deaths | births | avg_speed | avg_metabolism"
    )


def format_stats_line(tick: int, stats: Dict[str, float | int]) -> str:
    return (
        f"{tick:4d} | "
        f"{int(stats['alive']):3d}/{int(stats['population']):3d} | "
        f"{float(stats['food_remaining']):9.1f} | "
        f"{float(stats['avg_energy']):10.2f} | "
        f"{float(stats['avg_age']):7.2f} | "
        f"{int(stats['total_deaths']):6d} | "
        f"{int(stats['total_births']):6d} | "
        f"{float(stats['avg_speed']):9.3f} | "
        f"{float(stats['avg_metabolism']):13.3f}"
    )
