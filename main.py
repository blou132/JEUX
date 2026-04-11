from __future__ import annotations

import argparse
import random
from typing import Dict

from ai import HungerAI
from creatures import create_initial_population
from debug_tools import build_generation_distribution, build_population_stats
from player import PlayerRunConfig
from simulation import HungerSimulation
from ui import (
    format_death_causes,
    format_generation_distribution,
    format_population_dynamics,
    format_proto_groups,
    format_stats_line,
    print_run_header,
)
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the MVP evolutionary simulation.")
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--dt", type=float, default=1.0)
    parser.add_argument("--log-interval", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument("--map-width", type=float, default=60.0)
    parser.add_argument("--map-height", type=float, default=40.0)

    parser.add_argument("--creatures", type=int, default=20)
    parser.add_argument("--initial-food", type=int, default=50)
    parser.add_argument("--min-food", type=int, default=30)

    parser.add_argument("--energy-drain-rate", type=float, default=1.2)
    parser.add_argument("--movement-speed", type=float, default=1.0)
    parser.add_argument("--eat-rate", type=float, default=26.0)
    parser.add_argument("--hunger-threshold", type=float, default=0.6)

    parser.add_argument("--reproduction-threshold", type=float, default=58.0)
    parser.add_argument("--reproduction-cost", type=float, default=12.0)
    parser.add_argument("--reproduction-distance", type=float, default=15.0)
    parser.add_argument("--reproduction-min-age", type=float, default=0.0)
    parser.add_argument("--mutation-variation", type=float, default=0.1)

    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.steps <= 0:
        raise ValueError("steps must be > 0")
    if args.dt <= 0:
        raise ValueError("dt must be > 0")
    if args.log_interval <= 0:
        raise ValueError("log_interval must be > 0")

    if args.map_width <= 0 or args.map_height <= 0:
        raise ValueError("map_width and map_height must be > 0")

    if args.creatures <= 0:
        raise ValueError("creatures must be > 0")
    if args.initial_food < 0 or args.min_food < 0:
        raise ValueError("initial_food and min_food must be >= 0")

    if args.energy_drain_rate < 0 or args.movement_speed < 0 or args.eat_rate < 0:
        raise ValueError("energy_drain_rate, movement_speed and eat_rate must be >= 0")
    if not 0.0 <= args.hunger_threshold <= 1.0:
        raise ValueError("hunger_threshold must be in [0, 1]")

    if (
        args.reproduction_threshold < 0
        or args.reproduction_cost < 0
        or args.reproduction_distance < 0
        or args.reproduction_min_age < 0
        or args.mutation_variation < 0
    ):
        raise ValueError(
            "reproduction_threshold, reproduction_cost, reproduction_distance, reproduction_min_age and mutation_variation must be >= 0"
        )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    random_source = random.Random(args.seed)

    world_map = SimpleMap(width=args.map_width, height=args.map_height)
    world = SimpleWorld(
        world_map=world_map,
        spawn_config=FoodSpawnConfig(
            initial_food_count=args.initial_food,
            min_food_count=args.min_food,
        ),
        random_source=random_source,
    )

    population = create_initial_population(
        count=args.creatures,
        world_map=world_map,
        random_source=random_source,
    )

    ai_system = HungerAI(hunger_seek_threshold=args.hunger_threshold)
    simulation = HungerSimulation(
        creatures=population,
        food_field=world.food_field,
        ai_system=ai_system,
        energy_drain_rate=args.energy_drain_rate,
        movement_speed=args.movement_speed,
        eat_rate=args.eat_rate,
        reproduction_energy_threshold=args.reproduction_threshold,
        reproduction_cost=args.reproduction_cost,
        reproduction_distance=args.reproduction_distance,
        reproduction_min_age=args.reproduction_min_age,
        mutation_variation=args.mutation_variation,
        random_source=random_source,
        world_map=world_map,
    )

    run_config = PlayerRunConfig(
        steps=args.steps,
        dt=args.dt,
        log_interval=args.log_interval,
    )

    header_config: Dict[str, float | int] = {
        "map_width": world_map.width,
        "map_height": world_map.height,
        "creature_count": args.creatures,
        "initial_food_count": args.initial_food,
        "steps": run_config.steps,
        "dt": run_config.dt,
    }
    print_run_header(header_config)

    previous_logged_stats: Dict[str, object] | None = None

    for tick in range(1, run_config.steps + 1):
        world.tick()
        simulation.tick(run_config.dt)

        if tick == 1 or tick % run_config.log_interval == 0:
            stats = build_population_stats(simulation)
            generations = build_generation_distribution(simulation)
            print(format_stats_line(tick, stats))
            print("     " + format_generation_distribution(generations, max_bins=10))
            print("     " + format_proto_groups(stats, max_groups=3))
            print("     " + format_death_causes(stats, include_tick=True))
            print("     " + format_population_dynamics(stats, previous_logged_stats))
            previous_logged_stats = stats

        if simulation.get_alive_count() == 0:
            print(f"All creatures are dead at tick {tick}.")
            break

    final_stats = build_population_stats(simulation)
    generations = build_generation_distribution(simulation)

    print("--- Final Stats ---")
    print(
        "population={population} alive={alive} dead={dead} food_left={food_left:.1f} births={births} deaths={deaths}".format(
            population=final_stats["population"],
            alive=final_stats["alive"],
            dead=final_stats["dead"],
            food_left=float(final_stats["food_remaining"]),
            births=final_stats["total_births"],
            deaths=final_stats["total_deaths"],
        )
    )
    print(
        "avg_energy={avg_energy:.2f} avg_age={avg_age:.2f} avg_generation={avg_generation:.2f} avg_speed={avg_speed:.3f} avg_metabolism={avg_metabolism:.3f}".format(
            avg_energy=float(final_stats["avg_energy"]),
            avg_age=float(final_stats["avg_age"]),
            avg_generation=float(final_stats["avg_generation"]),
            avg_speed=float(final_stats["avg_speed"]),
            avg_metabolism=float(final_stats["avg_metabolism"]),
        )
    )
    print(format_generation_distribution(generations, max_bins=30))
    print(format_proto_groups(final_stats, max_groups=6))
    print(format_death_causes(final_stats, include_tick=False))
    print(format_population_dynamics(final_stats, previous_logged_stats))


if __name__ == "__main__":
    main()
