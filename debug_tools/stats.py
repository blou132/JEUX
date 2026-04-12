from __future__ import annotations

from typing import Dict, Iterable

from creatures import Creature
from simulation import HungerSimulation

_PROTO_GROUP_WIDTH_SPEED = 0.2
_PROTO_GROUP_WIDTH_METABOLISM = 0.15
_PROTO_GROUP_WIDTH_BEHAVIOR = 0.25
_PROTO_TREND_STABLE_DELTA = 0.02

_PROTO_TEMPORAL_STATUSES = ("stable", "en_hausse", "en_baisse", "nouveau")
_ZONE_NAMES = ("rich", "neutral", "poor")


def build_population_stats(
    simulation: HungerSimulation,
    world: object | None = None,
    previous_stats: Dict[str, object] | None = None,
) -> Dict[str, object]:
    total = simulation.get_total_count()
    alive = simulation.get_alive_count()
    dead = simulation.get_dead_count()

    alive_creatures = [creature for creature in simulation.creatures if creature.alive]
    food_memory_active_count = sum(1 for creature in alive_creatures if creature.has_food_memory)
    danger_memory_active_count = sum(1 for creature in alive_creatures if creature.has_danger_memory)
    (
        zone_distribution,
        dominant_proto_by_zone,
    ) = _build_proto_zone_observations(alive_creatures, world)

    food_memory_active_share = (food_memory_active_count / alive) if alive > 0 else 0.0
    danger_memory_active_share = (danger_memory_active_count / alive) if alive > 0 else 0.0

    avg_food_memory_distance_gain_total = (
        simulation.total_food_memory_distance_gain / simulation.total_food_memory_guided_moves
        if simulation.total_food_memory_guided_moves > 0
        else 0.0
    )
    avg_danger_memory_distance_gain_total = (
        simulation.total_danger_memory_distance_gain / simulation.total_danger_memory_avoid_moves
        if simulation.total_danger_memory_avoid_moves > 0
        else 0.0
    )

    if total == 0:
        return {
            "population": 0,
            "alive": 0,
            "dead": 0,
            "food_sources": simulation.food_field.get_food_count(),
            "food_remaining": 0.0,
            "avg_energy": 0.0,
            "avg_age": 0.0,
            "avg_generation": 0.0,
            "avg_speed": 0.0,
            "avg_metabolism": 0.0,
            "avg_prudence": 0.0,
            "avg_dominance": 0.0,
            "avg_repro_drive": 0.0,
            "proto_group_count": 0,
            "proto_groups_top": [],
            "dominant_proto_group_share": 0.0,
            "proto_group_temporal_trends": [],
            "proto_group_temporal_summary": _empty_proto_temporal_summary(),
            "creatures_by_fertility_zone": zone_distribution,
            "dominant_proto_group_by_fertility_zone": dominant_proto_by_zone,
            "births_last_tick": simulation.births_last_tick,
            "total_births": simulation.total_births,
            "deaths_last_tick": simulation.deaths_last_tick,
            "total_deaths": simulation.total_deaths,
            "flees_last_tick": simulation.flees_last_tick,
            "total_flees": simulation.total_flees,
            "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
            "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
            "creatures_with_food_memory": 0,
            "creatures_with_danger_memory": 0,
            "food_memory_active_share": 0.0,
            "danger_memory_active_share": 0.0,
            "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
            "total_food_memory_guided_moves": simulation.total_food_memory_guided_moves,
            "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
            "total_danger_memory_avoid_moves": simulation.total_danger_memory_avoid_moves,
            "food_memory_usage_per_alive_tick": 0.0,
            "danger_memory_usage_per_alive_tick": 0.0,
            "food_memory_usage_per_tick_total": 0.0,
            "danger_memory_usage_per_tick_total": 0.0,
            "food_memory_effect_avg_distance_tick": simulation.avg_food_memory_distance_gain_last_tick,
            "danger_memory_effect_avg_distance_tick": simulation.avg_danger_memory_distance_gain_last_tick,
            "food_memory_effect_avg_distance_total": avg_food_memory_distance_gain_total,
            "danger_memory_effect_avg_distance_total": avg_danger_memory_distance_gain_total,
            "death_causes_last_tick": dict(simulation.death_causes_last_tick),
            "death_causes_total": dict(simulation.total_death_causes),
        }

    avg_energy = sum(c.energy for c in simulation.creatures) / total
    avg_age = sum(c.age for c in simulation.creatures) / total
    avg_generation = sum(c.generation for c in simulation.creatures) / total
    avg_speed = sum(c.traits.speed for c in simulation.creatures) / total
    avg_metabolism = sum(c.traits.metabolism for c in simulation.creatures) / total
    avg_prudence = sum(c.traits.prudence for c in simulation.creatures) / total
    avg_dominance = sum(c.traits.dominance for c in simulation.creatures) / total
    avg_repro_drive = sum(c.traits.repro_drive for c in simulation.creatures) / total

    proto_group_count, proto_groups_top, dominant_proto_group_share = _build_proto_groups(
        alive_creatures,
        max_groups=3,
    )
    (
        proto_group_temporal_trends,
        proto_group_temporal_summary,
    ) = _build_proto_group_temporal_observations(
        proto_groups_top,
        previous_stats=previous_stats,
        max_groups=3,
    )

    return {
        "population": total,
        "alive": alive,
        "dead": dead,
        "food_sources": simulation.food_field.get_food_count(),
        "food_remaining": simulation.food_field.get_total_food_energy(),
        "avg_energy": avg_energy,
        "avg_age": avg_age,
        "avg_generation": avg_generation,
        "avg_speed": avg_speed,
        "avg_metabolism": avg_metabolism,
        "avg_prudence": avg_prudence,
        "avg_dominance": avg_dominance,
        "avg_repro_drive": avg_repro_drive,
        "proto_group_count": proto_group_count,
        "proto_groups_top": proto_groups_top,
        "dominant_proto_group_share": dominant_proto_group_share,
        "proto_group_temporal_trends": proto_group_temporal_trends,
        "proto_group_temporal_summary": proto_group_temporal_summary,
        "creatures_by_fertility_zone": zone_distribution,
        "dominant_proto_group_by_fertility_zone": dominant_proto_by_zone,
        "births_last_tick": simulation.births_last_tick,
        "total_births": simulation.total_births,
        "deaths_last_tick": simulation.deaths_last_tick,
        "total_deaths": simulation.total_deaths,
        "flees_last_tick": simulation.flees_last_tick,
        "total_flees": simulation.total_flees,
        "fleeing_creatures_last_tick": list(simulation.fleeing_creatures_last_tick),
        "avg_flee_threat_distance_last_tick": simulation.avg_flee_threat_distance_last_tick,
        "creatures_with_food_memory": food_memory_active_count,
        "creatures_with_danger_memory": danger_memory_active_count,
        "food_memory_active_share": food_memory_active_share,
        "danger_memory_active_share": danger_memory_active_share,
        "food_memory_guided_moves_last_tick": simulation.food_memory_guided_moves_last_tick,
        "total_food_memory_guided_moves": simulation.total_food_memory_guided_moves,
        "danger_memory_avoid_moves_last_tick": simulation.danger_memory_avoid_moves_last_tick,
        "total_danger_memory_avoid_moves": simulation.total_danger_memory_avoid_moves,
        "food_memory_usage_per_alive_tick": simulation.food_memory_guided_moves_last_tick / alive,
        "danger_memory_usage_per_alive_tick": simulation.danger_memory_avoid_moves_last_tick / alive,
        "food_memory_usage_per_tick_total": simulation.total_food_memory_guided_moves / max(1, simulation.tick_count),
        "danger_memory_usage_per_tick_total": simulation.total_danger_memory_avoid_moves / max(1, simulation.tick_count),
        "food_memory_effect_avg_distance_tick": simulation.avg_food_memory_distance_gain_last_tick,
        "danger_memory_effect_avg_distance_tick": simulation.avg_danger_memory_distance_gain_last_tick,
        "food_memory_effect_avg_distance_total": avg_food_memory_distance_gain_total,
        "danger_memory_effect_avg_distance_total": avg_danger_memory_distance_gain_total,
        "death_causes_last_tick": dict(simulation.death_causes_last_tick),
        "death_causes_total": dict(simulation.total_death_causes),
    }

def build_generation_distribution(simulation: HungerSimulation) -> Dict[int, int]:
    distribution: Dict[int, int] = {}
    for creature in simulation.creatures:
        distribution[creature.generation] = distribution.get(creature.generation, 0) + 1
    return distribution


def create_proto_temporal_tracker() -> Dict[str, object]:
    return {
        "observations": 0,
        "by_signature": {},
    }


def update_proto_temporal_tracker(tracker: Dict[str, object], stats: Dict[str, object]) -> None:
    tracker["observations"] = int(tracker.get("observations", 0)) + 1

    by_signature = tracker.get("by_signature")
    if not isinstance(by_signature, dict):
        by_signature = {}
        tracker["by_signature"] = by_signature

    raw_trends = stats.get("proto_group_temporal_trends")
    if not isinstance(raw_trends, list):
        return

    for trend in raw_trends:
        if not isinstance(trend, dict):
            continue

        signature = str(trend.get("signature", "?"))
        status = str(trend.get("status", ""))
        if status not in _PROTO_TEMPORAL_STATUSES:
            continue

        counts = by_signature.get(signature)
        if not isinstance(counts, dict):
            counts = _empty_proto_temporal_summary()
            by_signature[signature] = counts

        counts[status] = int(counts.get(status, 0)) + 1


def build_final_run_summary(
    final_stats: Dict[str, object],
    temporal_tracker: Dict[str, object],
) -> Dict[str, object]:
    dominant_signature = "-"
    dominant_share = 0.0

    raw_top_groups = final_stats.get("proto_groups_top")
    if isinstance(raw_top_groups, list) and len(raw_top_groups) > 0:
        first = raw_top_groups[0]
        if isinstance(first, dict):
            dominant_signature = str(first.get("signature", "-"))
            dominant_share = float(first.get("share", 0.0))

    by_signature = _read_status_counts(temporal_tracker)
    stable_signature, stable_count = _pick_signature_by_status(by_signature, "stable")
    rising_signature, rising_count = _pick_signature_by_status(by_signature, "en_hausse")

    memory_impact = {
        "food_usage_total": int(final_stats.get("total_food_memory_guided_moves", 0)),
        "danger_usage_total": int(final_stats.get("total_danger_memory_avoid_moves", 0)),
        "food_active_share": float(final_stats.get("food_memory_active_share", 0.0)),
        "danger_active_share": float(final_stats.get("danger_memory_active_share", 0.0)),
        "food_effect_avg_distance": float(final_stats.get("food_memory_effect_avg_distance_total", 0.0)),
        "danger_effect_avg_distance": float(final_stats.get("danger_memory_effect_avg_distance_total", 0.0)),
        "food_usage_per_tick": float(final_stats.get("food_memory_usage_per_tick_total", 0.0)),
        "danger_usage_per_tick": float(final_stats.get("danger_memory_usage_per_tick_total", 0.0)),
    }

    return {
        "final_dominant_group_signature": dominant_signature,
        "final_dominant_group_share": dominant_share,
        "most_stable_group_signature": stable_signature,
        "most_stable_group_count": stable_count,
        "most_rising_group_signature": rising_signature,
        "most_rising_group_count": rising_count,
        "final_zone_distribution": _normalize_zone_distribution(
            final_stats.get("creatures_by_fertility_zone")
        ),
        "avg_traits": _read_avg_traits(final_stats),
        "memory_impact": memory_impact,
        "observed_logs": int(temporal_tracker.get("observations", 0)),
    }


def build_multi_run_summary(run_results: Iterable[Dict[str, object]]) -> Dict[str, object]:
    runs = list(run_results)
    run_count = len(runs)
    if run_count == 0:
        return {
            "runs": 0,
            "seeds": [],
            "extinction_count": 0,
            "extinction_rate": 0.0,
            "avg_max_generation": 0.0,
            "avg_final_population": 0.0,
            "avg_final_traits": {
                "speed": 0.0,
                "metabolism": 0.0,
                "prudence": 0.0,
                "dominance": 0.0,
                "repro_drive": 0.0,
            },
            "avg_memory_impact": {
                "food_usage_total": 0.0,
                "danger_usage_total": 0.0,
                "food_active_share": 0.0,
                "danger_active_share": 0.0,
                "food_effect_avg_distance": 0.0,
                "danger_effect_avg_distance": 0.0,
                "food_usage_per_tick": 0.0,
                "danger_usage_per_tick": 0.0,
            },
            "most_frequent_final_dominant_group": "-",
            "most_frequent_final_dominant_group_count": 0,
            "most_frequent_final_dominant_group_share": 0.0,
        }

    seeds: list[int] = []
    extinction_count = 0
    max_generation_sum = 0.0
    final_population_sum = 0.0

    avg_traits_acc = {
        "speed": 0.0,
        "metabolism": 0.0,
        "prudence": 0.0,
        "dominance": 0.0,
        "repro_drive": 0.0,
    }
    avg_memory_acc = {
        "food_usage_total": 0.0,
        "danger_usage_total": 0.0,
        "food_active_share": 0.0,
        "danger_active_share": 0.0,
        "food_effect_avg_distance": 0.0,
        "danger_effect_avg_distance": 0.0,
        "food_usage_per_tick": 0.0,
        "danger_usage_per_tick": 0.0,
    }

    dominant_frequency: Dict[str, int] = {}

    for run in runs:
        seeds.append(int(run.get("seed", 0)))

        if bool(run.get("extinct", False)):
            extinction_count += 1

        max_generation_sum += float(run.get("max_generation", 0.0))
        final_population_sum += float(run.get("final_alive", 0.0))

        run_summary = run.get("run_summary")
        if isinstance(run_summary, dict):
            signature = str(run_summary.get("final_dominant_group_signature", "-"))
            if signature != "-":
                dominant_frequency[signature] = dominant_frequency.get(signature, 0) + 1

            traits_raw = run_summary.get("avg_traits")
            if isinstance(traits_raw, dict):
                avg_traits_acc["speed"] += float(traits_raw.get("speed", 0.0))
                avg_traits_acc["metabolism"] += float(traits_raw.get("metabolism", 0.0))
                avg_traits_acc["prudence"] += float(traits_raw.get("prudence", 0.0))
                avg_traits_acc["dominance"] += float(traits_raw.get("dominance", 0.0))
                avg_traits_acc["repro_drive"] += float(traits_raw.get("repro_drive", 0.0))

            memory_raw = run_summary.get("memory_impact")
            if isinstance(memory_raw, dict):
                avg_memory_acc["food_usage_total"] += float(memory_raw.get("food_usage_total", 0.0))
                avg_memory_acc["danger_usage_total"] += float(memory_raw.get("danger_usage_total", 0.0))
                avg_memory_acc["food_active_share"] += float(memory_raw.get("food_active_share", 0.0))
                avg_memory_acc["danger_active_share"] += float(memory_raw.get("danger_active_share", 0.0))
                avg_memory_acc["food_effect_avg_distance"] += float(memory_raw.get("food_effect_avg_distance", 0.0))
                avg_memory_acc["danger_effect_avg_distance"] += float(memory_raw.get("danger_effect_avg_distance", 0.0))
                avg_memory_acc["food_usage_per_tick"] += float(memory_raw.get("food_usage_per_tick", 0.0))
                avg_memory_acc["danger_usage_per_tick"] += float(memory_raw.get("danger_usage_per_tick", 0.0))

    if dominant_frequency:
        dominant_signature, dominant_count = sorted(
            dominant_frequency.items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
    else:
        dominant_signature, dominant_count = "-", 0

    return {
        "runs": run_count,
        "seeds": seeds,
        "extinction_count": extinction_count,
        "extinction_rate": extinction_count / run_count,
        "avg_max_generation": max_generation_sum / run_count,
        "avg_final_population": final_population_sum / run_count,
        "avg_final_traits": {
            "speed": avg_traits_acc["speed"] / run_count,
            "metabolism": avg_traits_acc["metabolism"] / run_count,
            "prudence": avg_traits_acc["prudence"] / run_count,
            "dominance": avg_traits_acc["dominance"] / run_count,
            "repro_drive": avg_traits_acc["repro_drive"] / run_count,
        },
        "avg_memory_impact": {
            "food_usage_total": avg_memory_acc["food_usage_total"] / run_count,
            "danger_usage_total": avg_memory_acc["danger_usage_total"] / run_count,
            "food_active_share": avg_memory_acc["food_active_share"] / run_count,
            "danger_active_share": avg_memory_acc["danger_active_share"] / run_count,
            "food_effect_avg_distance": avg_memory_acc["food_effect_avg_distance"] / run_count,
            "danger_effect_avg_distance": avg_memory_acc["danger_effect_avg_distance"] / run_count,
            "food_usage_per_tick": avg_memory_acc["food_usage_per_tick"] / run_count,
            "danger_usage_per_tick": avg_memory_acc["danger_usage_per_tick"] / run_count,
        },
        "most_frequent_final_dominant_group": dominant_signature,
        "most_frequent_final_dominant_group_count": dominant_count,
        "most_frequent_final_dominant_group_share": dominant_count / run_count,
    }

def _build_proto_zone_observations(
    creatures: Iterable[Creature],
    world: object | None,
) -> tuple[Dict[str, int], Dict[str, Dict[str, object] | None]]:
    zone_distribution = _empty_zone_distribution()
    dominant_proto_by_zone = _empty_zone_dominants()

    if world is None:
        return zone_distribution, dominant_proto_by_zone

    get_zone = getattr(world, "get_fertility_zone", None)
    if not callable(get_zone):
        return zone_distribution, dominant_proto_by_zone

    grouped_by_zone: Dict[str, Dict[str, int]] = {zone: {} for zone in _ZONE_NAMES}

    for creature in creatures:
        zone_name = str(get_zone(creature.x, creature.y))
        if zone_name not in zone_distribution:
            continue

        zone_distribution[zone_name] += 1
        signature = _proto_signature(_proto_group_key(creature))

        bucket = grouped_by_zone[zone_name]
        bucket[signature] = bucket.get(signature, 0) + 1

    for zone_name in _ZONE_NAMES:
        zone_count = zone_distribution[zone_name]
        bucket = grouped_by_zone[zone_name]

        if zone_count <= 0 or not bucket:
            dominant_proto_by_zone[zone_name] = None
            continue

        signature, dominant_count = sorted(bucket.items(), key=lambda item: (-item[1], item[0]))[0]
        dominant_proto_by_zone[zone_name] = {
            "signature": signature,
            "count": dominant_count,
            "share": dominant_count / zone_count,
        }

    return zone_distribution, dominant_proto_by_zone


def _empty_zone_distribution() -> Dict[str, int]:
    return {zone: 0 for zone in _ZONE_NAMES}


def _empty_zone_dominants() -> Dict[str, Dict[str, object] | None]:
    return {zone: None for zone in _ZONE_NAMES}


def _build_proto_group_temporal_observations(
    current_top_groups: list[Dict[str, object]],
    previous_stats: Dict[str, object] | None,
    max_groups: int,
) -> tuple[list[Dict[str, object]], Dict[str, int]]:
    if max_groups <= 0:
        raise ValueError("max_groups must be > 0")

    previous_top_groups = _read_top_groups(previous_stats, max_groups)
    current_groups = _read_top_groups_from_list(current_top_groups, max_groups)

    previous_share_by_signature = {
        str(group["signature"]): float(group["share"]) for group in previous_top_groups
    }
    current_share_by_signature = {
        str(group["signature"]): float(group["share"]) for group in current_groups
    }

    trends: list[Dict[str, object]] = []
    for group in current_groups:
        signature = str(group["signature"])
        current_share = float(group["share"])
        previous_share = previous_share_by_signature.get(signature)

        if previous_share is None:
            status = "nouveau"
            delta_share = current_share
        else:
            delta_share = current_share - previous_share
            if abs(delta_share) <= _PROTO_TREND_STABLE_DELTA:
                status = "stable"
            elif delta_share > 0:
                status = "en_hausse"
            else:
                status = "en_baisse"

        trends.append(
            {
                "signature": signature,
                "status": status,
                "current_share": current_share,
                "previous_share": 0.0 if previous_share is None else previous_share,
                "delta_share": delta_share,
            }
        )

    for signature, previous_share in previous_share_by_signature.items():
        if signature in current_share_by_signature:
            continue
        trends.append(
            {
                "signature": signature,
                "status": "en_baisse",
                "current_share": 0.0,
                "previous_share": previous_share,
                "delta_share": -previous_share,
            }
        )

    summary = _empty_proto_temporal_summary()
    for trend in trends:
        status = str(trend["status"])
        if status in summary:
            summary[status] += 1

    return trends, summary


def _read_top_groups(
    stats: Dict[str, object] | None,
    max_groups: int,
) -> list[Dict[str, object]]:
    if stats is None:
        return []
    raw = stats.get("proto_groups_top")
    if not isinstance(raw, list):
        return []
    return _read_top_groups_from_list(raw, max_groups)


def _read_top_groups_from_list(
    groups: list[Dict[str, object]],
    max_groups: int,
) -> list[Dict[str, object]]:
    parsed: list[Dict[str, object]] = []
    for group in groups[:max_groups]:
        if not isinstance(group, dict):
            continue
        parsed.append(
            {
                "signature": str(group.get("signature", "?")),
                "share": float(group.get("share", 0.0)),
            }
        )
    return parsed


def _empty_proto_temporal_summary() -> Dict[str, int]:
    return {
        "stable": 0,
        "en_hausse": 0,
        "en_baisse": 0,
        "nouveau": 0,
    }


def _read_status_counts(temporal_tracker: Dict[str, object]) -> Dict[str, Dict[str, int]]:
    by_signature_raw = temporal_tracker.get("by_signature")
    if not isinstance(by_signature_raw, dict):
        return {}

    parsed: Dict[str, Dict[str, int]] = {}
    for signature, counts_raw in by_signature_raw.items():
        if not isinstance(counts_raw, dict):
            continue
        parsed[str(signature)] = {
            "stable": int(counts_raw.get("stable", 0)),
            "en_hausse": int(counts_raw.get("en_hausse", 0)),
            "en_baisse": int(counts_raw.get("en_baisse", 0)),
            "nouveau": int(counts_raw.get("nouveau", 0)),
        }
    return parsed


def _pick_signature_by_status(
    by_signature: Dict[str, Dict[str, int]],
    status_name: str,
) -> tuple[str, int]:
    if status_name not in _PROTO_TEMPORAL_STATUSES:
        return "-", 0

    candidates: list[tuple[int, int, str]] = []
    for signature, counts in by_signature.items():
        primary = int(counts.get(status_name, 0))
        if primary <= 0:
            continue

        secondary_name = "en_hausse" if status_name == "stable" else "stable"
        secondary = int(counts.get(secondary_name, 0))
        candidates.append((primary, secondary, signature))

    if not candidates:
        return "-", 0

    best = sorted(candidates, key=lambda item: (-item[0], -item[1], item[2]))[0]
    return best[2], best[0]


def _normalize_zone_distribution(raw: object) -> Dict[str, int]:
    result = {
        "rich": 0,
        "neutral": 0,
        "poor": 0,
    }
    if not isinstance(raw, dict):
        return result

    result["rich"] = int(raw.get("rich", 0))
    result["neutral"] = int(raw.get("neutral", 0))
    result["poor"] = int(raw.get("poor", 0))
    return result


def _read_avg_traits(final_stats: Dict[str, object]) -> Dict[str, float]:
    return {
        "speed": float(final_stats.get("avg_speed", 0.0)),
        "metabolism": float(final_stats.get("avg_metabolism", 0.0)),
        "prudence": float(final_stats.get("avg_prudence", 0.0)),
        "dominance": float(final_stats.get("avg_dominance", 0.0)),
        "repro_drive": float(final_stats.get("avg_repro_drive", 0.0)),
    }


def _build_proto_groups(
    creatures: Iterable[Creature],
    max_groups: int,
) -> tuple[int, list[Dict[str, object]], float]:
    grouped: Dict[tuple[int, int, int, int, int], Dict[str, float | int]] = {}

    for creature in creatures:
        key = _proto_group_key(creature)
        if key not in grouped:
            grouped[key] = {
                "size": 0,
                "sum_speed": 0.0,
                "sum_metabolism": 0.0,
                "sum_prudence": 0.0,
                "sum_dominance": 0.0,
                "sum_repro_drive": 0.0,
            }

        bucket = grouped[key]
        bucket["size"] = int(bucket["size"]) + 1
        bucket["sum_speed"] = float(bucket["sum_speed"]) + creature.traits.speed
        bucket["sum_metabolism"] = float(bucket["sum_metabolism"]) + creature.traits.metabolism
        bucket["sum_prudence"] = float(bucket["sum_prudence"]) + creature.traits.prudence
        bucket["sum_dominance"] = float(bucket["sum_dominance"]) + creature.traits.dominance
        bucket["sum_repro_drive"] = float(bucket["sum_repro_drive"]) + creature.traits.repro_drive

    group_count = len(grouped)
    if group_count == 0:
        return 0, [], 0.0

    total = sum(int(bucket["size"]) for bucket in grouped.values())
    ordered_keys = sorted(grouped.keys(), key=lambda key: (-int(grouped[key]["size"]), key))

    top_groups: list[Dict[str, object]] = []
    for key in ordered_keys[:max_groups]:
        bucket = grouped[key]
        size = int(bucket["size"])
        top_groups.append(
            {
                "signature": _proto_signature(key),
                "size": size,
                "share": size / total,
                "avg_speed": float(bucket["sum_speed"]) / size,
                "avg_metabolism": float(bucket["sum_metabolism"]) / size,
                "avg_prudence": float(bucket["sum_prudence"]) / size,
                "avg_dominance": float(bucket["sum_dominance"]) / size,
                "avg_repro_drive": float(bucket["sum_repro_drive"]) / size,
            }
        )

    dominant_share = float(top_groups[0]["share"]) if top_groups else 0.0
    return group_count, top_groups, dominant_share


def _proto_group_key(creature: Creature) -> tuple[int, int, int, int, int]:
    return (
        _quantize(creature.traits.speed, _PROTO_GROUP_WIDTH_SPEED),
        _quantize(creature.traits.metabolism, _PROTO_GROUP_WIDTH_METABOLISM),
        _quantize(creature.traits.prudence, _PROTO_GROUP_WIDTH_BEHAVIOR),
        _quantize(creature.traits.dominance, _PROTO_GROUP_WIDTH_BEHAVIOR),
        _quantize(creature.traits.repro_drive, _PROTO_GROUP_WIDTH_BEHAVIOR),
    )


def _quantize(value: float, width: float) -> int:
    return int(round(value / width))


def _proto_signature(key: tuple[int, int, int, int, int]) -> str:
    return f"s{key[0]}m{key[1]}p{key[2]}d{key[3]}r{key[4]}"
