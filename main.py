from __future__ import annotations

import argparse
import random
from typing import Dict

from ai import HungerAI
from creatures import create_initial_population
from debug_tools import (
    build_final_run_summary,
    build_generation_distribution,
    build_multi_run_export,
    build_multi_run_summary,
    build_population_stats,
    build_single_run_export,
    create_proto_temporal_tracker,
    export_results,
    update_proto_temporal_tracker,
)
from player import PlayerRunConfig
from simulation import HungerSimulation
from ui import (
    format_death_causes,
    format_final_run_summary,
    format_generation_distribution,
    format_multi_run_summary,
    format_population_dynamics,
    format_proto_group_temporal,
    format_proto_groups,
    format_proto_groups_by_fertility_zone,
    format_stats_line,
    print_run_header,
)
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


_DEF_EXPORT_FORMATS = ("json", "csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the MVP evolutionary simulation.")
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--dt", type=float, default=1.0)
    parser.add_argument("--log-interval", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--seed-step", type=int, default=1)

    parser.add_argument("--export-path", type=str, default=None)
    parser.add_argument("--export-format", type=str, choices=_DEF_EXPORT_FORMATS, default="json")

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

    if args.runs <= 0:
        raise ValueError("runs must be > 0")
    if args.seed_step <= 0:
        raise ValueError("seed_step must be > 0")

    if args.export_path is not None and str(args.export_path).strip() == "":
        raise ValueError("export_path cannot be empty")
    if args.export_format not in _DEF_EXPORT_FORMATS:
        raise ValueError("export_format must be json or csv")

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


def _build_seed_list(base_seed: int, runs: int, seed_step: int) -> list[int]:
    return [base_seed + (idx * seed_step) for idx in range(runs)]


def _emit_export_if_needed(args: argparse.Namespace, payload: Dict[str, object]) -> None:
    if args.export_path is None:
        return

    output_path = export_results(payload, args.export_path, args.export_format)
    print(f"export: {output_path} ({args.export_format})")


def _run_single(args: argparse.Namespace, seed: int, verbose: bool) -> Dict[str, object]:
    random_source = random.Random(seed)

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

    if verbose:
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
    proto_temporal_tracker = create_proto_temporal_tracker()

    for tick in range(1, run_config.steps + 1):
        world.tick()
        simulation.tick(run_config.dt)

        if tick == 1 or tick % run_config.log_interval == 0:
            stats = build_population_stats(
                simulation,
                world=world,
                previous_stats=previous_logged_stats,
            )
            update_proto_temporal_tracker(proto_temporal_tracker, stats)

            if verbose:
                generations = build_generation_distribution(simulation)
                print(format_stats_line(tick, stats))
                print("     " + format_generation_distribution(generations, max_bins=10))
                print("     " + format_proto_groups(stats, max_groups=3))
                print("     " + format_proto_group_temporal(stats, max_items=6))
                print("     " + format_proto_groups_by_fertility_zone(stats))
                print("     " + format_death_causes(stats, include_tick=True))
                print("     " + format_population_dynamics(stats, previous_logged_stats))
                zone_stats = world.get_food_zone_stats()
                print(
                    "     zones_nourriture: riches={rich} neutres={neutral} pauvres={poor} fert_moy={avg:.2f}".format(
                        rich=int(zone_stats["rich"]),
                        neutral=int(zone_stats["neutral"]),
                        poor=int(zone_stats["poor"]),
                        avg=float(zone_stats["avg_fertility"]),
                    )
                )

            previous_logged_stats = stats

        if simulation.get_alive_count() == 0:
            if verbose:
                print(f"All creatures are dead at tick {tick}.")
            break

    final_stats = build_population_stats(
        simulation,
        world=world,
        previous_stats=previous_logged_stats,
    )
    final_zone_stats = world.get_food_zone_stats()
    generations = build_generation_distribution(simulation)
    run_summary = build_final_run_summary(final_stats, proto_temporal_tracker)

    if verbose:
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
        print(
            "zones_nourriture: riches={rich} neutres={neutral} pauvres={poor} fert_moy={avg:.2f}".format(
                rich=int(final_zone_stats["rich"]),
                neutral=int(final_zone_stats["neutral"]),
                poor=int(final_zone_stats["poor"]),
                avg=float(final_zone_stats["avg_fertility"]),
            )
        )
        print(format_generation_distribution(generations, max_bins=30))
        print(format_proto_groups(final_stats, max_groups=6))
        print(format_proto_group_temporal(final_stats, max_items=10))
        print(format_proto_groups_by_fertility_zone(final_stats))
        print(format_death_causes(final_stats, include_tick=False))
        print(format_population_dynamics(final_stats, previous_logged_stats))

        print("--- Run Summary ---")
        print(format_final_run_summary(run_summary))

    max_generation = max((creature.generation for creature in simulation.creatures), default=0)
    return {
        "seed": seed,
        "extinct": simulation.get_alive_count() == 0,
        "max_generation": max_generation,
        "final_alive": int(final_stats["alive"]),
        "final_population": int(final_stats["population"]),
        "final_stats": final_stats,
        "run_summary": run_summary,
    }


def _run_multi(args: argparse.Namespace) -> None:
    seeds = _build_seed_list(args.seed, args.runs, args.seed_step)

    print("=== Multi-Run Mode ===")
    print(
        "runs={runs} steps={steps} dt={dt} log_interval={log_interval}".format(
            runs=args.runs,
            steps=args.steps,
            dt=args.dt,
            log_interval=args.log_interval,
        )
    )
    print("seeds: " + ",".join(str(seed) for seed in seeds))

    results: list[Dict[str, object]] = []

    for idx, seed in enumerate(seeds, start=1):
        result = _run_single(args, seed=seed, verbose=False)
        results.append(result)

        run_summary = result.get("run_summary")
        dominant_signature = "-"
        dominant_share = 0.0
        if isinstance(run_summary, dict):
            dominant_signature = str(run_summary.get("final_dominant_group_signature", "-"))
            dominant_share = float(run_summary.get("final_dominant_group_share", 0.0))

        print(
            "run {idx}/{total} seed={seed} extinct={extinct} max_gen={max_gen} alive_final={alive} dominant={dominant} part={part:.2f}".format(
                idx=idx,
                total=args.runs,
                seed=seed,
                extinct="yes" if bool(result.get("extinct", False)) else "no",
                max_gen=int(result.get("max_generation", 0)),
                alive=int(result.get("final_alive", 0)),
                dominant=dominant_signature,
                part=dominant_share,
            )
        )

    summary = build_multi_run_summary(results)
    print("--- Multi-Run Summary ---")
    print(format_multi_run_summary(summary))

    export_payload = build_multi_run_export(seeds, results, summary)
    _emit_export_if_needed(args, export_payload)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    if args.runs <= 1:
        result = _run_single(args, seed=args.seed, verbose=True)
        export_payload = build_single_run_export(args.seed, result)
        _emit_export_if_needed(args, export_payload)
        return

    _run_multi(args)


if __name__ == "__main__":
    main()
