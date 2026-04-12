from __future__ import annotations

from typing import Dict, Iterable

from creatures import Creature
from simulation import HungerSimulation

_PROTO_GROUP_WIDTH_SPEED = 0.2
_PROTO_GROUP_WIDTH_METABOLISM = 0.15
_PROTO_GROUP_WIDTH_BEHAVIOR = 0.25
_PROTO_TREND_STABLE_DELTA = 0.02

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
    (
        zone_distribution,
        dominant_proto_by_zone,
    ) = _build_proto_zone_observations(alive_creatures, world)

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
        "death_causes_last_tick": dict(simulation.death_causes_last_tick),
        "death_causes_total": dict(simulation.total_death_causes),
    }


def build_generation_distribution(simulation: HungerSimulation) -> Dict[int, int]:
    distribution: Dict[int, int] = {}
    for creature in simulation.creatures:
        distribution[creature.generation] = distribution.get(creature.generation, 0) + 1
    return distribution


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
