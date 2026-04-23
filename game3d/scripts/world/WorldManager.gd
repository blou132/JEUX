extends Node3D
class_name WorldManager

const ALLEGIANCE_DOCTRINES: Array[String] = ["warlike", "steadfast", "arcane"]
const ALLEGIANCE_PROJECT_TYPES: Array[String] = ["fortify", "warband_muster", "ritual_focus"]

@export var map_size: float = 96.0
@export var nav_cell_size: float = 2.0
@export var wander_radius: float = 14.0
@export var poi_guidance_distance: float = 28.0
@export var poi_influence_activation_time: float = 8.0
@export var poi_structure_activation_time: float = 20.0
@export var poi_structure_loss_time: float = 10.0
@export var poi_structure_min_presence: int = 3
@export var poi_raid_duration: float = 18.0
@export var poi_raid_cooldown: float = 16.0
@export var poi_raid_success_hold: float = 5.0
@export var neutral_gate_open_duration: float = 18.0
@export var neutral_gate_cooldown_min: float = 62.0
@export var neutral_gate_cooldown_max: float = 104.0
@export var neutral_gate_retry_delay: float = 12.0
@export var neutral_gate_min_dominance_seconds: float = 16.0
@export var allegiance_project_duration_min: float = 20.0
@export var allegiance_project_duration_max: float = 34.0
@export var allegiance_project_cooldown: float = 26.0
@export var allegiance_project_check_interval: float = 5.0
@export var allegiance_project_start_chance: float = 0.32

var human_spawn_points: Array[Vector3] = []
var monster_spawn_points: Array[Vector3] = []
var pois: Array[Dictionary] = []
var poi_nodes: Dictionary = {}
var poi_runtime_status: Dictionary = {}
var poi_dominant_faction: Dictionary = {}
var poi_dominance_started_at: Dictionary = {}
var poi_influence_active: Dictionary = {}
var poi_structure_state: Dictionary = {}
var poi_structure_faction: Dictionary = {}
var poi_structure_started_at: Dictionary = {}
var poi_structure_unstable_started_at: Dictionary = {}
var poi_allegiance_id: Dictionary = {}
var poi_raid_state: Dictionary = {}
var poi_raid_cooldown_until: float = 0.0
var poi_last_raid_attacker: String = ""
var raid_pressure_global_multiplier: float = 1.0
var raid_pressure_human_multiplier: float = 1.0
var raid_pressure_monster_multiplier: float = 1.0
var world_event_visual_id: String = ""
var bounty_state: Dictionary = {}
var neutral_gate_status: String = "dormant"
var neutral_gate_open_until: float = 0.0
var neutral_gate_cooldown_until: float = 0.0
var neutral_gate_opened_total: int = 0
var neutral_gate_closed_total: int = 0
var neutral_gate_breaches_total: int = 0
var neutral_gate_breach_pending: bool = false
var allegiance_doctrine_by_id: Dictionary = {}
var allegiance_project_runtime_by_id: Dictionary = {}
var allegiance_project_cooldown_until_by_id: Dictionary = {}
var allegiance_project_next_attempt_at_by_id: Dictionary = {}


func setup_world() -> void:
    _build_ground()
    _build_spawn_points()
    _build_pois()


func tick_world(_delta: float) -> void:
    pass


func set_raid_pressure_modifiers(
    global_multiplier: float = 1.0,
    human_multiplier: float = 1.0,
    monster_multiplier: float = 1.0
) -> void:
    raid_pressure_global_multiplier = clampf(global_multiplier, 0.45, 1.35)
    raid_pressure_human_multiplier = clampf(human_multiplier, 0.45, 1.35)
    raid_pressure_monster_multiplier = clampf(monster_multiplier, 0.45, 1.35)


func set_world_event_visual(event_id: String) -> void:
    world_event_visual_id = event_id


func set_bounty_state(
    active: bool,
    source_faction: String = "",
    source_allegiance_id: String = "",
    source_poi: String = "",
    target_position: Vector3 = Vector3.ZERO,
    target_actor_id: int = 0,
    target_label: String = "",
    target_faction: String = ""
) -> void:
    if not active:
        bounty_state.clear()
        return
    bounty_state = {
        "active": true,
        "source_faction": source_faction,
        "source_allegiance_id": source_allegiance_id,
        "source_poi": source_poi,
        "target_position": target_position,
        "target_actor_id": target_actor_id,
        "target_label": target_label,
        "target_faction": target_faction
    }


func clamp_to_world(position: Vector3) -> Vector3:
    var half_size: float = (map_size * 0.5) - 1.0
    return Vector3(
        clamp(position.x, -half_size, half_size),
        0.0,
        clamp(position.z, -half_size, half_size)
    )


func snap_to_nav_grid(position: Vector3) -> Vector3:
    return Vector3(
        round(position.x / nav_cell_size) * nav_cell_size,
        0.0,
        round(position.z / nav_cell_size) * nav_cell_size
    )


func get_spawn_point(faction: String) -> Vector3:
    var points: Array[Vector3] = human_spawn_points if faction == "human" else monster_spawn_points
    if points.is_empty():
        return Vector3.ZERO

    var base_point: Vector3 = points[randi() % points.size()]
    var jitter := Vector3(randf_range(-2.0, 2.0), 0.0, randf_range(-2.0, 2.0))
    return clamp_to_world(snap_to_nav_grid(base_point + jitter))


func get_wander_point(origin: Vector3) -> Vector3:
    var offset := Vector3(randf_range(-wander_radius, wander_radius), 0.0, randf_range(-wander_radius, wander_radius))
    if offset.length() < 2.0:
        offset = offset.normalized() * 2.0
    return clamp_to_world(snap_to_nav_grid(origin + offset))


func find_nearest_enemy(source: Actor, all_actors: Array, max_distance: float) -> Actor:
    var closest: Actor = null
    var closest_distance_sq: float = max_distance * max_distance

    for other in all_actors:
        if other == null or other == source or other.is_dead:
            continue
        if not source.is_enemy(other):
            continue

        var dist_sq: float = source.global_position.distance_squared_to(other.global_position)
        if dist_sq <= closest_distance_sq:
            closest = other
            closest_distance_sq = dist_sq

    return closest


func get_poi_guidance(actor_position: Vector3, faction: String) -> Dictionary:
    if pois.is_empty():
        return {}

    var selected: Dictionary = {}
    for poi in pois:
        if _is_neutral_gate_poi(poi):
            continue
        if str(poi.get("faction_hint", "")) == faction:
            selected = poi
            break

    if selected.is_empty():
        selected = _get_nearest_poi(actor_position, true)

    if selected.is_empty():
        return {}

    var poi_position: Vector3 = selected.get("position", actor_position)
    var distance: float = actor_position.distance_to(poi_position)
    if distance > poi_guidance_distance:
        return {}

    var jitter := Vector3(randf_range(-2.0, 2.0), 0.0, randf_range(-2.0, 2.0))
    var target_position := clamp_to_world(snap_to_nav_grid(poi_position + jitter))
    return {
        "name": str(selected.get("name", "poi")),
        "target_position": target_position,
        "distance": distance
    }


func get_neutral_gate_guidance(actor: Actor) -> Dictionary:
    if actor == null or actor.is_dead:
        return {}
    if neutral_gate_status != "open":
        return {}

    var gate_name: String = _find_neutral_gate_poi_name()
    if gate_name == "":
        return {}
    var gate_poi: Dictionary = _get_poi_by_name(gate_name)
    if gate_poi.is_empty():
        return {}

    var gate_position: Vector3 = gate_poi.get("position", actor.global_position)
    var gate_radius: float = float(gate_poi.get("radius", 7.0))
    var distance: float = actor.global_position.distance_to(gate_position)
    if distance > poi_guidance_distance * 1.55:
        return {}

    var is_cautious: bool = (
        not actor.is_champion
        and not actor.has_relic()
        and not actor.is_special_arrival()
        and actor.notoriety < 44.0
        and (
            actor.hp <= actor.max_hp * 0.88
            or actor.energy <= actor.max_energy * 0.62
        )
    )

    if is_cautious and distance <= gate_radius * 1.35:
        var away_vector := actor.global_position - gate_position
        away_vector.y = 0.0
        if away_vector.length() < 0.1:
            away_vector = Vector3(randf_range(-1.0, 1.0), 0.0, randf_range(-1.0, 1.0))
        var avoid_target := actor.global_position + away_vector.normalized() * (gate_radius + 3.4)
        return {
            "kind": "avoid",
            "reason": "neutral_gate_avoid",
            "target_position": clamp_to_world(snap_to_nav_grid(avoid_target)),
            "distance": distance,
            "weight": 0.58
        }

    var pull_weight: float = 0.34
    if actor.is_champion or actor.has_relic() or actor.is_special_arrival() or actor.notoriety >= 48.0:
        pull_weight += 0.18
    if distance <= gate_radius * 1.20:
        pull_weight += 0.07
    if world_event_visual_id == "monster_frenzy" and actor.faction == "human":
        pull_weight += 0.06
    elif world_event_visual_id == "sanctuary_calm" and actor.faction == "monster":
        pull_weight += 0.06

    var jitter := Vector3(randf_range(-2.2, 2.2), 0.0, randf_range(-2.2, 2.2))
    return {
        "kind": "investigate",
        "reason": "neutral_gate_pull",
        "target_position": clamp_to_world(snap_to_nav_grid(gate_position + jitter)),
        "distance": distance,
        "weight": clampf(pull_weight, 0.24, 0.72)
    }


func get_poi_population_snapshot(actors: Array) -> Dictionary:
    var snapshot: Dictionary = {}

    for poi in pois:
        var poi_name: String = str(poi.get("name", "poi"))
        var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
        var poi_radius: float = float(poi.get("radius", 7.0))
        var humans: int = 0
        var monsters: int = 0

        for actor in actors:
            if actor == null or actor.is_dead:
                continue
            if actor.global_position.distance_to(poi_pos) > poi_radius:
                continue

            if actor.faction == "human":
                humans += 1
            elif actor.faction == "monster":
                monsters += 1

        snapshot[poi_name] = {
            "human": humans,
            "monster": monsters
        }

    return snapshot


func get_raid_guidance(
    actor_position: Vector3,
    faction: String,
    allegiance_id: String = "",
    home_poi: String = ""
) -> Dictionary:
    if not bool(poi_raid_state.get("active", false)):
        return {}
    if str(poi_raid_state.get("attacker_faction", "")) != faction:
        return {}

    var target_name: String = str(poi_raid_state.get("target_poi", ""))
    var target_poi: Dictionary = _get_poi_by_name(target_name)
    if target_poi.is_empty():
        return {}

    var target_position: Vector3 = target_poi.get("position", actor_position)
    var distance: float = actor_position.distance_to(target_position)
    if distance > poi_guidance_distance * 1.55:
        return {}

    var jitter := Vector3(randf_range(-2.3, 2.3), 0.0, randf_range(-2.3, 2.3))
    var source_poi: String = str(poi_raid_state.get("source_poi", ""))
    var weight: float = 0.74
    if allegiance_id != "":
        if home_poi == source_poi:
            weight += 0.12
        elif home_poi != "":
            weight -= 0.16
        var doctrine_modifiers: Dictionary = get_allegiance_doctrine_modifiers(allegiance_id)
        weight += float(doctrine_modifiers.get("raid_weight_delta", 0.0))
        var project_modifiers: Dictionary = get_allegiance_project_modifiers(allegiance_id)
        weight += float(project_modifiers.get("raid_weight_delta", 0.0))
    weight *= raid_pressure_global_multiplier
    if faction == "human":
        weight *= raid_pressure_human_multiplier
    elif faction == "monster":
        weight *= raid_pressure_monster_multiplier

    return {
        "reason": "raid_pressure:%s->%s" % [source_poi if source_poi != "" else "src", target_name],
        "target_position": clamp_to_world(snap_to_nav_grid(target_position + jitter)),
        "distance": distance,
        "weight": clampf(weight, 0.28, 0.92)
    }


func get_active_raid_state() -> Dictionary:
    return poi_raid_state.duplicate(true)


func get_bounty_guidance(
    actor_position: Vector3,
    faction: String,
    allegiance_id: String = "",
    home_poi: String = ""
) -> Dictionary:
    if not bool(bounty_state.get("active", false)):
        return {}
    if str(bounty_state.get("source_faction", "")) != faction:
        return {}

    var target_position: Vector3 = bounty_state.get("target_position", actor_position)
    var distance: float = actor_position.distance_to(target_position)
    if distance > poi_guidance_distance * 1.90:
        return {}

    var weight: float = 0.56
    var source_allegiance_id: String = str(bounty_state.get("source_allegiance_id", ""))
    var source_poi: String = str(bounty_state.get("source_poi", ""))
    if allegiance_id != "" and source_allegiance_id != "" and allegiance_id == source_allegiance_id:
        weight += 0.14
    if home_poi != "" and source_poi != "" and home_poi == source_poi:
        weight += 0.07
    if bool(poi_raid_state.get("active", false)) and str(poi_raid_state.get("attacker_faction", "")) == faction:
        weight += 0.06

    var jitter := Vector3(randf_range(-1.8, 1.8), 0.0, randf_range(-1.8, 1.8))
    return {
        "reason": "bounty_hunt:%s" % str(bounty_state.get("target_label", "marked_target")),
        "target_position": clamp_to_world(snap_to_nav_grid(target_position + jitter)),
        "distance": distance,
        "weight": clampf(weight, 0.26, 0.88)
    }


func get_allegiance_defense_guidance(
    actor_position: Vector3,
    faction: String,
    home_poi: String
) -> Dictionary:
    if home_poi == "":
        return {}
    if not bool(poi_raid_state.get("active", false)):
        return {}
    if str(poi_raid_state.get("defender_faction", "")) != faction:
        return {}
    if str(poi_raid_state.get("target_poi", "")) != home_poi:
        return {}

    var home := _get_poi_by_name(home_poi)
    if home.is_empty():
        return {}
    if str(poi_structure_state.get(home_poi, "")) == "":
        return {}

    var home_pos: Vector3 = home.get("position", actor_position)
    if actor_position.distance_to(home_pos) > poi_guidance_distance * 1.35:
        return {}

    var jitter := Vector3(randf_range(-1.8, 1.8), 0.0, randf_range(-1.8, 1.8))
    var weight: float = 0.68
    var home_allegiance_id: String = str(poi_allegiance_id.get(home_poi, ""))
    if home_allegiance_id != "":
        var doctrine_modifiers: Dictionary = get_allegiance_doctrine_modifiers(home_allegiance_id)
        weight += float(doctrine_modifiers.get("defense_weight_delta", 0.0))
        var project_modifiers: Dictionary = get_allegiance_project_modifiers(home_allegiance_id)
        weight += float(project_modifiers.get("defense_weight_delta", 0.0))
    return {
        "reason": "allegiance_defend:%s" % home_poi,
        "target_position": clamp_to_world(snap_to_nav_grid(home_pos + jitter)),
        "weight": clampf(weight, 0.24, 0.92)
    }


func get_active_allegiances(time_seconds: float = -1.0) -> Array[Dictionary]:
    var active: Array[Dictionary] = []
    for poi in pois:
        var poi_name: String = str(poi.get("name", ""))
        if poi_name == "":
            continue
        var structure_state: String = str(poi_structure_state.get(poi_name, ""))
        if structure_state == "":
            continue
        var allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))
        if allegiance_id == "":
            continue
        active.append({
            "allegiance_id": allegiance_id,
            "faction": str(poi_structure_faction.get(poi_name, "")),
            "home_poi": poi_name,
            "position": poi.get("position", Vector3.ZERO),
            "structure_state": structure_state,
            "doctrine": get_allegiance_doctrine(allegiance_id),
            "project": get_allegiance_project(allegiance_id),
            "project_remaining": get_allegiance_project_remaining(allegiance_id, time_seconds)
        })
    return active


func resolve_actor_allegiance(actor: Actor) -> Dictionary:
    var active_allegiances: Array[Dictionary] = get_active_allegiances()
    var current_id: String = actor.allegiance_id
    var current_home: String = actor.home_poi

    var by_id: Dictionary = {}
    for allegiance in active_allegiances:
        by_id[str(allegiance.get("allegiance_id", ""))] = allegiance

    if current_id != "":
        var current := by_id.get(current_id, {})
        if current.is_empty() or str(current.get("faction", "")) != actor.faction:
            return {
                "allegiance_id": "",
                "home_poi": "",
                "changed": true,
                "reason": "anchor_lost"
            }
        var expected_home: String = str(current.get("home_poi", current_home))
        if current_home != expected_home:
            return {
                "allegiance_id": current_id,
                "home_poi": expected_home,
                "changed": true,
                "reason": "home_sync"
            }
        return {
            "allegiance_id": current_id,
            "home_poi": current_home,
            "changed": false,
            "reason": "stable"
        }

    var selected: Dictionary = {}
    var best_distance: float = INF
    var assign_distance: float = poi_guidance_distance * 1.15
    for allegiance in active_allegiances:
        if str(allegiance.get("faction", "")) != actor.faction:
            continue
        var center: Vector3 = allegiance.get("position", actor.global_position)
        var distance: float = actor.global_position.distance_to(center)
        if distance <= assign_distance and distance < best_distance:
            selected = allegiance
            best_distance = distance

    if selected.is_empty():
        return {
            "allegiance_id": "",
            "home_poi": "",
            "changed": false,
            "reason": "no_anchor"
        }

    return {
        "allegiance_id": str(selected.get("allegiance_id", "")),
        "home_poi": str(selected.get("home_poi", "")),
        "changed": true,
        "reason": "assigned_near_anchor"
    }


func update_poi_runtime(actors: Array, time_seconds: float) -> Dictionary:
    var snapshot: Dictionary = {}
    var events: Array[Dictionary] = []

    for poi in pois:
        var poi_name: String = str(poi.get("name", "poi"))
        var counts: Dictionary = _count_poi_occupancy(poi, actors)
        var human_count: int = int(counts.get("human", 0))
        var monster_count: int = int(counts.get("monster", 0))
        var human_champions: int = int(counts.get("human_champions", 0))
        var monster_champions: int = int(counts.get("monster_champions", 0))
        var total_count: int = human_count + monster_count
        var status: String = _compute_poi_status(human_count, monster_count)
        var activity: String = _compute_activity_level(total_count)
        var dominant_faction: String = _dominant_faction_from_status(status)
        var dominance_seconds: float = _update_dominance_duration(poi_name, dominant_faction, time_seconds)
        var influence_kind: String = _compute_influence_kind(str(poi.get("kind", "")), dominant_faction, dominance_seconds)
        var influence_active: bool = influence_kind != ""
        var dominant_presence: int = human_count if dominant_faction == "human" else monster_count
        var dominant_champions: int = human_champions if dominant_faction == "human" else monster_champions
        var structure_runtime: Dictionary = _update_structure_runtime(
            poi_name,
            str(poi.get("kind", "")),
            dominant_faction,
            dominance_seconds,
            influence_active,
            dominant_presence,
            dominant_champions,
            time_seconds
        )
        var structure_state: String = str(structure_runtime.get("state", ""))
        var structure_active: bool = bool(structure_runtime.get("active", false))
        var structure_seconds: float = float(structure_runtime.get("structure_seconds", 0.0))
        var allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))

        snapshot[poi_name] = {
            "human": human_count,
            "monster": monster_count,
            "total": total_count,
            "status": status,
            "activity": activity,
            "dominant_faction": dominant_faction,
            "dominance_seconds": dominance_seconds,
            "influence_active": influence_active,
            "influence_kind": influence_kind,
            "structure_state": structure_state,
            "structure_active": structure_active,
            "structure_seconds": structure_seconds,
            "allegiance_id": allegiance_id,
            "allegiance_doctrine": get_allegiance_doctrine(allegiance_id),
            "allegiance_project": get_allegiance_project(allegiance_id),
            "allegiance_project_remaining": get_allegiance_project_remaining(allegiance_id, time_seconds)
        }

        var previous_status: String = str(poi_runtime_status.get(poi_name, ""))
        if previous_status != "" and previous_status != status:
            if status == "contested":
                events.append({
                    "kind": "contest_started",
                    "poi": poi_name,
                    "from": previous_status,
                    "to": status
                })
            elif status in ["human_dominant", "monster_dominant"]:
                events.append({
                    "kind": "domination_changed",
                    "poi": poi_name,
                    "from": previous_status,
                    "to": status
                })
            elif previous_status == "contested" and status == "calm":
                events.append({
                    "kind": "contest_resolved",
                    "poi": poi_name,
                    "from": previous_status,
                    "to": status
                })

        var previous_active: bool = bool(poi_influence_active.get(poi_name, false))
        if previous_active != influence_active:
            if influence_active:
                events.append({
                    "kind": "influence_activated",
                    "poi": poi_name,
                    "faction": dominant_faction,
                    "influence_kind": influence_kind,
                    "dominance_seconds": dominance_seconds
                })
            else:
                events.append({
                    "kind": "influence_deactivated",
                    "poi": poi_name
                })

        var structure_events: Array = structure_runtime.get("events", [])
        for structure_event in structure_events:
            events.append(structure_event)

        poi_runtime_status[poi_name] = status
        poi_influence_active[poi_name] = influence_active

    var project_runtime: Dictionary = _update_allegiance_projects_runtime(snapshot, time_seconds)
    var project_events: Array = project_runtime.get("events", [])
    for project_event in project_events:
        events.append(project_event)

    var gate_runtime: Dictionary = _update_neutral_gate_runtime(snapshot, time_seconds)
    var gate_events: Array = gate_runtime.get("events", [])
    for gate_event in gate_events:
        events.append(gate_event)

    var raid_runtime: Dictionary = _update_raid_runtime(snapshot, time_seconds)
    var raid_events: Array = raid_runtime.get("events", [])
    for raid_event in raid_events:
        events.append(raid_event)

    for poi_name in snapshot.keys():
        var details: Dictionary = snapshot.get(poi_name, {})
        var details_allegiance_id: String = str(details.get("allegiance_id", ""))
        details["allegiance_doctrine"] = get_allegiance_doctrine(details_allegiance_id)
        details["allegiance_project"] = get_allegiance_project(details_allegiance_id)
        details["allegiance_project_remaining"] = get_allegiance_project_remaining(details_allegiance_id, time_seconds)
        if str(poi_name) == str(gate_runtime.get("poi", "")):
            details["gate_status"] = str(gate_runtime.get("status", "dormant"))
            details["gate_active"] = bool(gate_runtime.get("active", false))
            details["gate_remaining"] = float(gate_runtime.get("remaining", 0.0))
            details["gate_cooldown"] = float(gate_runtime.get("cooldown", 0.0))
            details["gate_open_count"] = int(gate_runtime.get("opened_total", 0))
            details["gate_close_count"] = int(gate_runtime.get("closed_total", 0))
            details["gate_breach_count"] = int(gate_runtime.get("breaches_total", 0))
        details["raid_role"] = _get_raid_role_for_poi(str(poi_name))
        snapshot[poi_name] = details
        _apply_poi_visual_state(
            str(poi_name),
            str(details.get("status", "calm")),
            int(details.get("total", 0)),
            time_seconds,
            bool(details.get("influence_active", false)),
            str(details.get("structure_state", "")),
            str(details.get("raid_role", "none")),
            str(details.get("gate_status", "dormant")),
            bool(details.get("gate_active", false))
        )

    return {
        "snapshot": snapshot,
        "events": events,
        "raid": poi_raid_state.duplicate(true)
    }


func get_active_poi_influences() -> Array[Dictionary]:
    var active: Array[Dictionary] = []

    for poi in pois:
        var poi_name: String = str(poi.get("name", "poi"))
        if not bool(poi_influence_active.get(poi_name, false)):
            continue

        var faction: String = str(poi_dominant_faction.get(poi_name, ""))
        var influence_kind: String = _compute_influence_kind(
            str(poi.get("kind", "")),
            faction,
            poi_influence_activation_time
        )
        if influence_kind == "":
            continue

        var structure_state: String = str(poi_structure_state.get(poi_name, ""))
        var structure_active: bool = structure_state != ""
        active.append({
            "name": poi_name,
            "position": poi.get("position", Vector3.ZERO),
            "radius": float(poi.get("radius", 7.0)),
            "faction": faction,
            "influence_kind": influence_kind,
            "structure_state": structure_state,
            "structure_active": structure_active
        })

    return active


func get_neutral_gate_runtime_state(time_seconds: float = 0.0) -> Dictionary:
    var gate_name: String = _find_neutral_gate_poi_name()
    var remaining: float = 0.0
    var cooldown: float = 0.0
    if neutral_gate_status == "open":
        remaining = max(0.0, neutral_gate_open_until - time_seconds)
    else:
        cooldown = max(0.0, neutral_gate_cooldown_until - time_seconds)
    return {
        "poi": gate_name,
        "status": neutral_gate_status,
        "active": neutral_gate_status == "open",
        "remaining": remaining,
        "cooldown": cooldown,
        "open_until": neutral_gate_open_until,
        "cooldown_until": neutral_gate_cooldown_until,
        "opened_total": neutral_gate_opened_total,
        "closed_total": neutral_gate_closed_total,
        "breaches_total": neutral_gate_breaches_total
    }


func get_allegiance_doctrine(allegiance_id: String) -> String:
    if allegiance_id == "":
        return ""
    var doctrine: String = str(allegiance_doctrine_by_id.get(allegiance_id, ""))
    if doctrine in ALLEGIANCE_DOCTRINES:
        return doctrine
    return ""


func get_allegiance_doctrine_modifiers(allegiance_id: String) -> Dictionary:
    var doctrine: String = get_allegiance_doctrine(allegiance_id)
    match doctrine:
        "warlike":
            return {
                "doctrine": doctrine,
                "raid_weight_delta": 0.11,
                "defense_weight_delta": -0.05,
                "rally_regroup_delta": -0.05,
                "rally_pressure_delta": 0.08,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }
        "steadfast":
            return {
                "doctrine": doctrine,
                "raid_weight_delta": -0.08,
                "defense_weight_delta": 0.12,
                "rally_regroup_delta": 0.08,
                "rally_pressure_delta": -0.04,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }
        "arcane":
            return {
                "doctrine": doctrine,
                "raid_weight_delta": 0.02,
                "defense_weight_delta": 0.04,
                "rally_regroup_delta": 0.03,
                "rally_pressure_delta": 0.01,
                "magic_damage_mult": 1.06,
                "magic_energy_cost_mult": 0.94
            }
        _:
            return {
                "doctrine": "",
                "raid_weight_delta": 0.0,
                "defense_weight_delta": 0.0,
                "rally_regroup_delta": 0.0,
                "rally_pressure_delta": 0.0,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }


func get_allegiance_project(allegiance_id: String) -> String:
    if allegiance_id == "":
        return ""
    var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
    if runtime.is_empty():
        return ""
    var project_id: String = str(runtime.get("project_id", ""))
    if project_id in ALLEGIANCE_PROJECT_TYPES:
        return project_id
    return ""


func get_allegiance_project_remaining(allegiance_id: String, time_seconds: float = -1.0) -> float:
    if allegiance_id == "" or time_seconds < 0.0:
        return 0.0
    var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
    if runtime.is_empty():
        return 0.0
    var end_at: float = float(runtime.get("end_at", time_seconds))
    return max(0.0, end_at - time_seconds)


func get_allegiance_project_modifiers(allegiance_id: String) -> Dictionary:
    var project_id: String = get_allegiance_project(allegiance_id)
    match project_id:
        "fortify":
            return {
                "project_id": project_id,
                "raid_weight_delta": -0.06,
                "defense_weight_delta": 0.12,
                "rally_regroup_delta": 0.0,
                "rally_pressure_delta": 0.0,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }
        "warband_muster":
            return {
                "project_id": project_id,
                "raid_weight_delta": 0.09,
                "defense_weight_delta": 0.0,
                "rally_regroup_delta": 0.07,
                "rally_pressure_delta": 0.0,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }
        "ritual_focus":
            return {
                "project_id": project_id,
                "raid_weight_delta": 0.0,
                "defense_weight_delta": 0.0,
                "rally_regroup_delta": 0.0,
                "rally_pressure_delta": 0.0,
                "magic_damage_mult": 1.05,
                "magic_energy_cost_mult": 0.95
            }
        _:
            return {
                "project_id": "",
                "raid_weight_delta": 0.0,
                "defense_weight_delta": 0.0,
                "rally_regroup_delta": 0.0,
                "rally_pressure_delta": 0.0,
                "magic_damage_mult": 1.00,
                "magic_energy_cost_mult": 1.00
            }


func get_poi_name_for_position(position: Vector3) -> String:
    for poi in pois:
        var poi_name: String = str(poi.get("name", "poi"))
        var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
        var poi_radius: float = float(poi.get("radius", 7.0))
        if position.distance_to(poi_pos) <= poi_radius:
            return poi_name
    return ""


func trigger_poi_entry_effect(poi_name: String, faction: String) -> void:
    var poi_node: Node3D = poi_nodes.get(poi_name, null)
    if poi_node == null:
        return
    var poi_kind: String = str(_get_poi_by_name(poi_name).get("kind", ""))

    var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
    if ring != null:
        var pulse := create_tween()
        var base_scale := ring.scale
        pulse.tween_property(ring, "scale", base_scale * 1.18, 0.10)
        pulse.tween_property(ring, "scale", base_scale, 0.14)

    var flash := MeshInstance3D.new()
    flash.name = "EntryFlash"
    var mesh := CylinderMesh.new()
    if poi_kind == "rift_gate":
        mesh.top_radius = 1.6
        mesh.bottom_radius = 1.6
    else:
        mesh.top_radius = 1.3
        mesh.bottom_radius = 1.3
    mesh.height = 0.08
    flash.mesh = mesh
    flash.position = Vector3(0.0, 0.06, 0.0)
    flash.scale = Vector3(0.35, 1.0, 0.35)

    var color := Color(0.45, 0.75, 1.0) if faction == "human" else Color(1.0, 0.52, 0.46)
    if poi_kind == "rift_gate":
        color = Color(0.82, 0.46, 1.0)
    var material := _make_material(color)
    material.emission = color * 1.05
    flash.material_override = material

    poi_node.add_child(flash)
    var tween := create_tween()
    tween.tween_property(flash, "scale", Vector3.ONE * 1.25, 0.22)
    tween.finished.connect(flash.queue_free)


func _build_ground() -> void:
    var old_ground := get_node_or_null("Ground")
    if old_ground:
        old_ground.queue_free()

    var ground := MeshInstance3D.new()
    ground.name = "Ground"
    var plane := PlaneMesh.new()
    plane.size = Vector2(map_size, map_size)
    ground.mesh = plane

    var ground_material := StandardMaterial3D.new()
    ground_material.albedo_color = Color(0.16, 0.34, 0.20)
    ground_material.roughness = 1.0
    ground.material_override = ground_material
    add_child(ground)


func _build_spawn_points() -> void:
    human_spawn_points.clear()
    monster_spawn_points.clear()

    var side: float = map_size * 0.35
    var lane_values := [-18.0, -9.0, 0.0, 9.0, 18.0]

    for lane in lane_values:
        human_spawn_points.append(Vector3(-side, 0.0, lane))
        monster_spawn_points.append(Vector3(side, 0.0, lane))

    _refresh_markers()


func _build_pois() -> void:
    pois.clear()
    pois.append({
        "name": "camp",
        "kind": "camp",
        "faction_hint": "human",
        "position": Vector3(-10.0, 0.0, -6.0),
        "radius": 8.0,
        "color": Color(0.40, 0.72, 1.0)
    })
    pois.append({
        "name": "ruins",
        "kind": "ruins",
        "faction_hint": "monster",
        "position": Vector3(10.0, 0.0, 6.0),
        "radius": 8.0,
        "color": Color(0.95, 0.60, 0.35)
    })
    pois.append({
        "name": "rift_gate",
        "kind": "rift_gate",
        "faction_hint": "",
        "position": Vector3(0.0, 0.0, 0.0),
        "radius": 7.2,
        "color": Color(0.76, 0.40, 0.96)
    })

    poi_runtime_status.clear()
    poi_dominant_faction.clear()
    poi_dominance_started_at.clear()
    poi_influence_active.clear()
    poi_structure_state.clear()
    poi_structure_faction.clear()
    poi_structure_started_at.clear()
    poi_structure_unstable_started_at.clear()
    poi_allegiance_id.clear()
    allegiance_doctrine_by_id.clear()
    allegiance_project_runtime_by_id.clear()
    allegiance_project_cooldown_until_by_id.clear()
    allegiance_project_next_attempt_at_by_id.clear()
    poi_raid_state.clear()
    poi_raid_cooldown_until = 0.0
    poi_last_raid_attacker = ""
    bounty_state.clear()
    neutral_gate_status = "dormant"
    neutral_gate_open_until = 0.0
    neutral_gate_cooldown_until = randf_range(
        neutral_gate_cooldown_min * 0.55,
        neutral_gate_cooldown_max * 0.72
    )
    neutral_gate_opened_total = 0
    neutral_gate_closed_total = 0
    neutral_gate_breaches_total = 0
    neutral_gate_breach_pending = false

    _refresh_poi_markers()


func _refresh_markers() -> void:
    var old_markers := get_node_or_null("SpawnMarkers")
    if old_markers:
        old_markers.queue_free()

    var marker_root := Node3D.new()
    marker_root.name = "SpawnMarkers"
    add_child(marker_root)

    for point in human_spawn_points:
        marker_root.add_child(_make_marker(point, Color(0.45, 0.75, 1.0)))
    for point in monster_spawn_points:
        marker_root.add_child(_make_marker(point, Color(0.95, 0.45, 0.45)))


func _make_marker(position: Vector3, color: Color) -> MeshInstance3D:
    var marker := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 0.30
    mesh.bottom_radius = 0.30
    mesh.height = 0.15
    marker.mesh = mesh
    marker.position = position + Vector3(0.0, 0.075, 0.0)

    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.35
    marker.material_override = material

    return marker


func _refresh_poi_markers() -> void:
    var old_root := get_node_or_null("PoiMarkers")
    if old_root:
        old_root.queue_free()

    var poi_root := Node3D.new()
    poi_root.name = "PoiMarkers"
    add_child(poi_root)

    poi_nodes.clear()
    for poi in pois:
        var marker := _make_poi_marker(poi)
        poi_root.add_child(marker)
        poi_nodes[str(poi.get("name", "poi"))] = marker


func _make_poi_marker(poi: Dictionary) -> Node3D:
    var poi_node := Node3D.new()
    poi_node.name = str(poi.get("name", "poi"))
    poi_node.position = poi.get("position", Vector3.ZERO)

    var color: Color = poi.get("color", Color(0.9, 0.9, 0.9))
    var poi_kind: String = str(poi.get("kind", ""))
    var ring := MeshInstance3D.new()
    var ring_mesh := CylinderMesh.new()
    ring_mesh.top_radius = 2.6 if poi_kind == "rift_gate" else 2.2
    ring_mesh.bottom_radius = ring_mesh.top_radius
    ring_mesh.height = 0.1
    ring.mesh = ring_mesh
    ring.name = "Ring"
    ring.position.y = 0.05
    ring.material_override = _make_material(color * 0.85)
    poi_node.add_child(ring)

    var pillar := MeshInstance3D.new()
    var pillar_mesh := BoxMesh.new()
    if poi_kind == "rift_gate":
        pillar_mesh.size = Vector3(1.0, 2.6, 1.0)
    else:
        pillar_mesh.size = Vector3(0.8, 2.0, 0.8)
    pillar.mesh = pillar_mesh
    pillar.name = "Pillar"
    pillar.position.y = 1.3 if poi_kind == "rift_gate" else 1.0
    pillar.material_override = _make_material(color)
    poi_node.add_child(pillar)

    var beacon := MeshInstance3D.new()
    var beacon_mesh := SphereMesh.new()
    if poi_kind == "rift_gate":
        beacon_mesh.radius = 0.42
        beacon_mesh.height = 0.84
    else:
        beacon_mesh.radius = 0.32
        beacon_mesh.height = 0.64
    beacon.mesh = beacon_mesh
    beacon.name = "Beacon"
    beacon.position.y = 3.0 if poi_kind == "rift_gate" else 2.2
    beacon.material_override = _make_material(Color(0.65, 0.65, 0.65))
    poi_node.add_child(beacon)

    var structure_halo := MeshInstance3D.new()
    var halo_mesh := CylinderMesh.new()
    halo_mesh.top_radius = 1.05
    halo_mesh.bottom_radius = 1.05
    halo_mesh.height = 0.06
    structure_halo.mesh = halo_mesh
    structure_halo.name = "StructureHalo"
    structure_halo.position.y = 2.72
    structure_halo.material_override = _make_material(Color(0.85, 0.85, 0.85))
    structure_halo.visible = false
    poi_node.add_child(structure_halo)

    if poi_kind == "rift_gate":
        var gate_halo := MeshInstance3D.new()
        var gate_halo_mesh := CylinderMesh.new()
        gate_halo_mesh.top_radius = 1.45
        gate_halo_mesh.bottom_radius = 1.45
        gate_halo_mesh.height = 0.07
        gate_halo.mesh = gate_halo_mesh
        gate_halo.name = "GateHalo"
        gate_halo.position.y = 3.42
        gate_halo.material_override = _make_material(Color(0.82, 0.48, 1.0))
        gate_halo.visible = false
        poi_node.add_child(gate_halo)

    return poi_node


func _make_material(color: Color) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.30
    material.roughness = 0.7
    return material


func _get_nearest_poi(position: Vector3, skip_neutral_gate: bool = false) -> Dictionary:
    var selected: Dictionary = {}
    var closest_sq: float = INF
    for poi in pois:
        if skip_neutral_gate and _is_neutral_gate_poi(poi):
            continue
        var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
        var d_sq: float = position.distance_squared_to(poi_pos)
        if d_sq < closest_sq:
            selected = poi
            closest_sq = d_sq
    return selected


func _get_poi_by_name(poi_name: String) -> Dictionary:
    for poi in pois:
        if str(poi.get("name", "")) == poi_name:
            return poi
    return {}


func _count_poi_occupancy(poi: Dictionary, actors: Array) -> Dictionary:
    var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
    var poi_radius: float = float(poi.get("radius", 7.0))
    var humans: int = 0
    var monsters: int = 0
    var human_champions: int = 0
    var monster_champions: int = 0

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(poi_pos) > poi_radius:
            continue

        if actor.faction == "human":
            humans += 1
            if actor.is_champion:
                human_champions += 1
        elif actor.faction == "monster":
            monsters += 1
            if actor.is_champion:
                monster_champions += 1

    return {
        "human": humans,
        "monster": monsters,
        "human_champions": human_champions,
        "monster_champions": monster_champions
    }


func _compute_poi_status(human_count: int, monster_count: int) -> String:
    if human_count == 0 and monster_count == 0:
        return "calm"
    if human_count > 0 and monster_count > 0:
        return "contested"
    if human_count > 0:
        return "human_dominant"
    return "monster_dominant"


func _compute_activity_level(total_count: int) -> String:
    if total_count <= 1:
        return "low"
    if total_count <= 4:
        return "medium"
    return "high"


func _apply_poi_visual_state(
    poi_name: String,
    status: String,
    total_count: int,
    time_seconds: float,
    influence_active: bool,
    structure_state: String,
    raid_role: String,
    gate_status: String,
    gate_active: bool
) -> void:
    var poi_node: Node3D = poi_nodes.get(poi_name, null)
    if poi_node == null:
        return

    var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
    var pillar := poi_node.get_node_or_null("Pillar") as MeshInstance3D
    var beacon := poi_node.get_node_or_null("Beacon") as MeshInstance3D
    var structure_halo := poi_node.get_node_or_null("StructureHalo") as MeshInstance3D
    var gate_halo := poi_node.get_node_or_null("GateHalo") as MeshInstance3D
    if ring == null or pillar == null or beacon == null or structure_halo == null:
        return

    var base_scale := 1.0 + min(total_count, 10) * 0.045
    if status == "contested":
        base_scale *= (1.0 + 0.06 * sin(time_seconds * 6.0))
    elif influence_active:
        base_scale *= (1.0 + 0.04 * sin(time_seconds * 4.0))
    ring.scale = Vector3(base_scale, 1.0, base_scale)

    var status_color := _get_status_color(status)
    var intensity := 0.24 + min(total_count, 10) * 0.05
    if influence_active:
        intensity += 0.16

    _set_mesh_color(ring, status_color, intensity + 0.05)
    _set_mesh_color(beacon, status_color, intensity + 0.10)
    _set_mesh_color(pillar, status_color.darkened(0.18), intensity * 0.62)

    if structure_state != "":
        structure_halo.visible = true
        var halo_scale := 1.0 + 0.06 * sin(time_seconds * 3.0)
        structure_halo.scale = Vector3(halo_scale, 1.0, halo_scale)
        _set_mesh_color(structure_halo, _structure_color(structure_state), 0.82)
    else:
        structure_halo.visible = false

    _apply_world_event_visual_bias(ring, beacon, status_color, intensity, time_seconds)

    if gate_halo != null:
        if gate_active:
            gate_halo.visible = true
            var gate_halo_scale := 1.0 + 0.10 * sin(time_seconds * 8.4)
            gate_halo.scale = Vector3(gate_halo_scale, 1.0, gate_halo_scale)
            _set_mesh_color(gate_halo, Color(0.84, 0.46, 1.0), 1.05)
            var gate_mix := 0.44 + 0.10 * sin(time_seconds * 7.8)
            _set_mesh_color(ring, status_color.lerp(Color(0.84, 0.42, 1.0), gate_mix), intensity + 0.34)
            _set_mesh_color(beacon, Color(0.86, 0.56, 1.0), intensity + 0.42)
            var gate_pulse := 1.0 + 0.14 * sin(time_seconds * 8.0)
            ring.scale *= Vector3(gate_pulse, 1.0, gate_pulse)
        else:
            gate_halo.visible = false
            if gate_status == "dormant":
                _set_mesh_color(beacon, status_color.darkened(0.10), max(0.16, intensity * 0.72))

    if raid_role == "source":
        var source_pulse := 1.0 + 0.10 * sin(time_seconds * 5.0)
        ring.scale *= Vector3(source_pulse, 1.0, source_pulse)
        _set_mesh_color(beacon, status_color.lightened(0.20), intensity + 0.26)
    elif raid_role == "target":
        var target_pulse := 1.0 + 0.08 * sin(time_seconds * 7.0)
        ring.scale *= Vector3(target_pulse, 1.0, target_pulse)
        _set_mesh_color(ring, Color(1.0, 0.62, 0.30), intensity + 0.24)


func _dominant_faction_from_status(status: String) -> String:
    if status == "human_dominant":
        return "human"
    if status == "monster_dominant":
        return "monster"
    return ""


func _update_dominance_duration(poi_name: String, dominant_faction: String, time_seconds: float) -> float:
    var previous_faction: String = str(poi_dominant_faction.get(poi_name, ""))
    if dominant_faction == "":
        poi_dominant_faction[poi_name] = ""
        poi_dominance_started_at[poi_name] = time_seconds
        return 0.0

    if previous_faction != dominant_faction:
        poi_dominant_faction[poi_name] = dominant_faction
        poi_dominance_started_at[poi_name] = time_seconds
        return 0.0

    var started_at: float = float(poi_dominance_started_at.get(poi_name, time_seconds))
    var duration: float = max(0.0, time_seconds - started_at)
    return duration


func _compute_influence_kind(poi_kind: String, dominant_faction: String, dominance_seconds: float) -> String:
    if dominant_faction == "":
        return ""
    if dominance_seconds < poi_influence_activation_time:
        return ""
    if poi_kind == "camp" and dominant_faction == "human":
        return "human_camp_influence"
    if poi_kind == "ruins" and dominant_faction == "monster":
        return "monster_ruins_influence"
    return ""


func _compute_structure_kind(poi_kind: String, dominant_faction: String) -> String:
    if poi_kind == "camp" and dominant_faction == "human":
        return "human_outpost"
    if poi_kind == "ruins" and dominant_faction == "monster":
        return "monster_lair"
    return ""


func _update_structure_runtime(
    poi_name: String,
    poi_kind: String,
    dominant_faction: String,
    dominance_seconds: float,
    influence_active: bool,
    dominant_presence: int,
    dominant_champions: int,
    time_seconds: float
) -> Dictionary:
    var events: Array[Dictionary] = []
    var current_state: String = str(poi_structure_state.get(poi_name, ""))
    var current_faction: String = str(poi_structure_faction.get(poi_name, ""))
    var can_structure_kind: String = _compute_structure_kind(poi_kind, dominant_faction)

    var required_presence: int = poi_structure_min_presence
    if dominant_champions > 0:
        required_presence = max(1, poi_structure_min_presence - 1)

    var eligible: bool = (
        can_structure_kind != ""
        and influence_active
        and dominance_seconds >= poi_structure_activation_time
        and dominant_presence >= required_presence
    )

    if current_state == "" and eligible:
        current_state = can_structure_kind
        current_faction = dominant_faction
        var allegiance_id: String = _ensure_allegiance_for_poi(poi_name, current_faction)
        var doctrine: String = _assign_doctrine_for_allegiance(
            allegiance_id,
            current_faction,
            current_state,
            dominant_champions
        )
        poi_structure_state[poi_name] = current_state
        poi_structure_faction[poi_name] = current_faction
        poi_structure_started_at[poi_name] = time_seconds
        poi_structure_unstable_started_at.erase(poi_name)
        events.append({
            "kind": "allegiance_created",
            "poi": poi_name,
            "allegiance_id": allegiance_id,
            "faction": current_faction,
            "doctrine": doctrine
        })
        events.append({
            "kind": "structure_established",
            "poi": poi_name,
            "structure_state": current_state,
            "faction": current_faction
        })
    elif current_state != "":
        var stable_for_current_structure: bool = (
            dominant_faction == current_faction
            and can_structure_kind == current_state
            and influence_active
            and dominant_presence >= max(1, poi_structure_min_presence - 1)
        )

        if stable_for_current_structure:
            poi_structure_unstable_started_at.erase(poi_name)
        else:
            if not poi_structure_unstable_started_at.has(poi_name):
                poi_structure_unstable_started_at[poi_name] = time_seconds
            var unstable_since: float = float(poi_structure_unstable_started_at.get(poi_name, time_seconds))
            if time_seconds - unstable_since >= poi_structure_loss_time:
                var previous_allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))
                if previous_allegiance_id != "":
                    var interrupted_project_id: String = _interrupt_allegiance_project(previous_allegiance_id, time_seconds)
                    if interrupted_project_id != "":
                        events.append({
                            "kind": "allegiance_project_interrupted",
                            "poi": poi_name,
                            "allegiance_id": previous_allegiance_id,
                            "project_id": interrupted_project_id,
                            "reason": "anchor_lost"
                        })
                    var doctrine_lost: String = _clear_allegiance_doctrine(previous_allegiance_id)
                    events.append({
                        "kind": "allegiance_removed",
                        "poi": poi_name,
                        "allegiance_id": previous_allegiance_id,
                        "faction": current_faction,
                        "doctrine": doctrine_lost
                    })
                    poi_allegiance_id.erase(poi_name)
                events.append({
                    "kind": "structure_lost",
                    "poi": poi_name,
                    "structure_state": current_state,
                    "faction": current_faction
                })
                current_state = ""
                current_faction = ""
                poi_structure_state[poi_name] = ""
                poi_structure_faction[poi_name] = ""
                poi_structure_started_at.erase(poi_name)
                poi_structure_unstable_started_at.erase(poi_name)

    var structure_seconds: float = 0.0
    if current_state != "":
        var started_at: float = float(poi_structure_started_at.get(poi_name, time_seconds))
        structure_seconds = max(0.0, time_seconds - started_at)

    return {
        "state": current_state,
        "active": current_state != "",
        "faction": current_faction,
        "structure_seconds": structure_seconds,
        "events": events
    }


func _ensure_allegiance_for_poi(poi_name: String, faction: String) -> String:
    var current: String = str(poi_allegiance_id.get(poi_name, ""))
    if current != "":
        return current
    var next_id := "%s:%s" % [faction, poi_name]
    poi_allegiance_id[poi_name] = next_id
    return next_id


func _pick_doctrine_for_allegiance(
    faction: String,
    structure_state: String,
    dominant_champions: int
) -> String:
    if world_event_visual_id == "mana_surge" and dominant_champions > 0:
        return "arcane"
    if structure_state == "human_outpost":
        if world_event_visual_id == "mana_surge":
            return "arcane"
        return "steadfast"
    if structure_state == "monster_lair":
        return "warlike"
    if faction == "human":
        return "steadfast"
    if faction == "monster":
        return "warlike"
    return "steadfast"


func _assign_doctrine_for_allegiance(
    allegiance_id: String,
    faction: String,
    structure_state: String,
    dominant_champions: int
) -> String:
    if allegiance_id == "":
        return ""
    var doctrine: String = _pick_doctrine_for_allegiance(faction, structure_state, dominant_champions)
    allegiance_doctrine_by_id[allegiance_id] = doctrine
    return doctrine


func _clear_allegiance_doctrine(allegiance_id: String) -> String:
    var doctrine: String = get_allegiance_doctrine(allegiance_id)
    if allegiance_id != "":
        allegiance_doctrine_by_id.erase(allegiance_id)
    return doctrine


func _pick_project_for_allegiance(
    allegiance_id: String,
    faction: String,
    home_poi: String,
    structure_state: String,
    doctrine: String
) -> String:
    if bool(poi_raid_state.get("active", false)):
        if str(poi_raid_state.get("target_poi", "")) == home_poi:
            return "fortify"
        if str(poi_raid_state.get("source_poi", "")) == home_poi:
            return "warband_muster"

    if doctrine == "arcane" and world_event_visual_id == "mana_surge":
        return "ritual_focus"

    if doctrine == "steadfast":
        return "fortify"
    if doctrine == "warlike":
        return "warband_muster"
    if doctrine == "arcane":
        return "ritual_focus"

    if structure_state == "human_outpost":
        return "fortify"
    if structure_state == "monster_lair":
        return "warband_muster"
    if faction == "monster":
        return "warband_muster"
    if allegiance_id == "":
        return ""
    return "fortify"


func _interrupt_allegiance_project(allegiance_id: String, time_seconds: float) -> String:
    var project_id: String = get_allegiance_project(allegiance_id)
    if allegiance_id != "":
        allegiance_project_runtime_by_id.erase(allegiance_id)
        allegiance_project_cooldown_until_by_id[allegiance_id] = time_seconds + allegiance_project_cooldown * 0.60
        allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
    return project_id


func _update_allegiance_projects_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
    var events: Array[Dictionary] = []
    var active_allegiances: Dictionary = {}

    for poi_name_variant in snapshot.keys():
        var poi_name: String = str(poi_name_variant)
        var details: Dictionary = snapshot.get(poi_name, {})
        var allegiance_id: String = str(details.get("allegiance_id", ""))
        if allegiance_id == "":
            continue
        if not bool(details.get("structure_active", false)):
            continue
        active_allegiances[allegiance_id] = {
            "home_poi": poi_name,
            "faction": str(details.get("dominant_faction", "")),
            "structure_state": str(details.get("structure_state", "")),
            "doctrine": get_allegiance_doctrine(allegiance_id)
        }

    var runtime_ids: Array = allegiance_project_runtime_by_id.keys()
    for allegiance_variant in runtime_ids:
        var allegiance_id: String = str(allegiance_variant)
        if active_allegiances.has(allegiance_id):
            continue
        var interrupted_project: String = _interrupt_allegiance_project(allegiance_id, time_seconds)
        if interrupted_project != "":
            events.append({
                "kind": "allegiance_project_interrupted",
                "poi": "",
                "allegiance_id": allegiance_id,
                "project_id": interrupted_project,
                "reason": "allegiance_lost"
            })

    var cleanup_attempt_ids: Array = allegiance_project_next_attempt_at_by_id.keys()
    for allegiance_variant in cleanup_attempt_ids:
        var allegiance_id: String = str(allegiance_variant)
        if not active_allegiances.has(allegiance_id):
            allegiance_project_next_attempt_at_by_id.erase(allegiance_id)

    var cleanup_cooldown_ids: Array = allegiance_project_cooldown_until_by_id.keys()
    for allegiance_variant in cleanup_cooldown_ids:
        var allegiance_id: String = str(allegiance_variant)
        if not active_allegiances.has(allegiance_id):
            allegiance_project_cooldown_until_by_id.erase(allegiance_id)

    for allegiance_variant in active_allegiances.keys():
        var allegiance_id: String = str(allegiance_variant)
        var context: Dictionary = active_allegiances.get(allegiance_id, {})
        var home_poi: String = str(context.get("home_poi", ""))
        var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
        if not runtime.is_empty():
            var project_id: String = str(runtime.get("project_id", ""))
            var end_at: float = float(runtime.get("end_at", time_seconds))
            if project_id == "" or not (project_id in ALLEGIANCE_PROJECT_TYPES):
                allegiance_project_runtime_by_id.erase(allegiance_id)
                continue
            if time_seconds >= end_at:
                allegiance_project_runtime_by_id.erase(allegiance_id)
                allegiance_project_cooldown_until_by_id[allegiance_id] = time_seconds + allegiance_project_cooldown
                allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
                events.append({
                    "kind": "allegiance_project_ended",
                    "poi": home_poi,
                    "allegiance_id": allegiance_id,
                    "project_id": project_id
                })
            continue

        var cooldown_until: float = float(allegiance_project_cooldown_until_by_id.get(allegiance_id, 0.0))
        if time_seconds < cooldown_until:
            continue

        var next_attempt_at: float = float(allegiance_project_next_attempt_at_by_id.get(allegiance_id, 0.0))
        if time_seconds < next_attempt_at:
            continue

        allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
        if randf() > clampf(allegiance_project_start_chance, 0.05, 0.80):
            continue

        var project_id: String = _pick_project_for_allegiance(
            allegiance_id,
            str(context.get("faction", "")),
            home_poi,
            str(context.get("structure_state", "")),
            str(context.get("doctrine", ""))
        )
        if not (project_id in ALLEGIANCE_PROJECT_TYPES):
            continue

        var duration: float = randf_range(
            min(allegiance_project_duration_min, allegiance_project_duration_max),
            max(allegiance_project_duration_min, allegiance_project_duration_max)
        )
        var end_at: float = time_seconds + duration
        allegiance_project_runtime_by_id[allegiance_id] = {
            "project_id": project_id,
            "home_poi": home_poi,
            "started_at": time_seconds,
            "end_at": end_at
        }
        events.append({
            "kind": "allegiance_project_started",
            "poi": home_poi,
            "allegiance_id": allegiance_id,
            "project_id": project_id,
            "duration": duration
        })

    return {
        "events": events
    }


func _is_neutral_gate_kind(poi_kind: String) -> bool:
    return poi_kind == "rift_gate"


func _is_neutral_gate_poi(poi: Dictionary) -> bool:
    return _is_neutral_gate_kind(str(poi.get("kind", "")))


func _find_neutral_gate_poi_name() -> String:
    for poi in pois:
        if _is_neutral_gate_poi(poi):
            return str(poi.get("name", ""))
    return ""


func _can_open_neutral_gate(snapshot: Dictionary, gate_name: String) -> bool:
    if world_event_visual_id == "":
        return false

    var stable_anchor_found: bool = false
    for poi_name_variant in snapshot.keys():
        var poi_name: String = str(poi_name_variant)
        if poi_name == gate_name:
            continue
        var details: Dictionary = snapshot.get(poi_name, {})
        if not bool(details.get("structure_active", false)):
            continue
        var dominance_seconds: float = float(details.get("dominance_seconds", 0.0))
        if dominance_seconds < neutral_gate_min_dominance_seconds:
            continue
        stable_anchor_found = true
        break

    return stable_anchor_found


func _update_neutral_gate_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
    var gate_name: String = _find_neutral_gate_poi_name()
    var events: Array[Dictionary] = []

    if gate_name == "":
        neutral_gate_status = "dormant"
        neutral_gate_open_until = 0.0
        neutral_gate_cooldown_until = 0.0
        neutral_gate_breach_pending = false
        return {
            "poi": "",
            "status": neutral_gate_status,
            "active": false,
            "remaining": 0.0,
            "cooldown": 0.0,
            "opened_total": neutral_gate_opened_total,
            "closed_total": neutral_gate_closed_total,
            "breaches_total": neutral_gate_breaches_total,
            "events": events
        }

    if neutral_gate_status == "open":
        if time_seconds >= neutral_gate_open_until:
            neutral_gate_status = "dormant"
            neutral_gate_open_until = 0.0
            neutral_gate_breach_pending = false
            neutral_gate_closed_total += 1
            neutral_gate_cooldown_until = time_seconds + randf_range(neutral_gate_cooldown_min, neutral_gate_cooldown_max)
            events.append({
                "kind": "neutral_gate_closed",
                "poi": gate_name,
                "cooldown_seconds": max(0.0, neutral_gate_cooldown_until - time_seconds)
            })
    else:
        if neutral_gate_cooldown_until <= 0.0:
            neutral_gate_cooldown_until = time_seconds + randf_range(
                neutral_gate_cooldown_min * 0.55,
                neutral_gate_cooldown_max * 0.72
            )
        elif time_seconds >= neutral_gate_cooldown_until:
            if _can_open_neutral_gate(snapshot, gate_name):
                neutral_gate_status = "open"
                neutral_gate_open_until = time_seconds + neutral_gate_open_duration
                neutral_gate_opened_total += 1
                neutral_gate_breach_pending = true
                events.append({
                    "kind": "neutral_gate_opened",
                    "poi": gate_name,
                    "open_seconds": neutral_gate_open_duration,
                    "world_event": world_event_visual_id
                })
            else:
                neutral_gate_cooldown_until = time_seconds + neutral_gate_retry_delay

    if neutral_gate_status == "open" and neutral_gate_breach_pending:
        neutral_gate_breach_pending = false
        neutral_gate_breaches_total += 1
        var gate_position: Vector3 = _get_poi_by_name(gate_name).get("position", Vector3.ZERO)
        events.append({
            "kind": "neutral_gate_breach",
            "poi": gate_name,
            "position": gate_position,
            "world_event": world_event_visual_id
        })

    var remaining: float = 0.0
    var cooldown: float = 0.0
    if neutral_gate_status == "open":
        remaining = max(0.0, neutral_gate_open_until - time_seconds)
    else:
        cooldown = max(0.0, neutral_gate_cooldown_until - time_seconds)

    return {
        "poi": gate_name,
        "status": neutral_gate_status,
        "active": neutral_gate_status == "open",
        "remaining": remaining,
        "cooldown": cooldown,
        "opened_total": neutral_gate_opened_total,
        "closed_total": neutral_gate_closed_total,
        "breaches_total": neutral_gate_breaches_total,
        "events": events
    }


func _update_raid_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
    var events: Array[Dictionary] = []
    var has_outpost: bool = _find_structure_poi(snapshot, "human_outpost") != ""
    var has_lair: bool = _find_structure_poi(snapshot, "monster_lair") != ""

    var raid_active: bool = bool(poi_raid_state.get("active", false))
    if raid_active:
        var source_poi: String = str(poi_raid_state.get("source_poi", ""))
        var target_poi: String = str(poi_raid_state.get("target_poi", ""))
        var attacker_faction: String = str(poi_raid_state.get("attacker_faction", ""))
        var started_at: float = float(poi_raid_state.get("started_at", time_seconds))

        var source_details: Dictionary = snapshot.get(source_poi, {})
        var target_details: Dictionary = snapshot.get(target_poi, {})
        var source_structure_ok: bool = bool(source_details.get("structure_active", false))
        var target_structure_ok: bool = bool(target_details.get("structure_active", false))

        if not source_structure_ok or not target_structure_ok:
            events.append(_end_raid("interrupted", time_seconds))
        else:
            var target_dominant_faction: String = str(target_details.get("dominant_faction", ""))
            var target_dom_seconds: float = float(target_details.get("dominance_seconds", 0.0))
            if target_dominant_faction == attacker_faction and target_dom_seconds >= poi_raid_success_hold:
                events.append(_end_raid("success", time_seconds))
            elif time_seconds - started_at >= poi_raid_duration:
                events.append(_end_raid("timeout", time_seconds))
    else:
        if time_seconds >= poi_raid_cooldown_until and has_outpost and has_lair:
            var next_attacker: String = "human"
            if poi_last_raid_attacker == "human":
                next_attacker = "monster"

            var source_poi_name: String = _find_structure_poi(snapshot, "human_outpost") if next_attacker == "human" else _find_structure_poi(snapshot, "monster_lair")
            var target_poi_name: String = _find_structure_poi(snapshot, "monster_lair") if next_attacker == "human" else _find_structure_poi(snapshot, "human_outpost")
            if source_poi_name != "" and target_poi_name != "":
                poi_raid_state = {
                    "active": true,
                    "attacker_faction": next_attacker,
                    "defender_faction": "monster" if next_attacker == "human" else "human",
                    "source_poi": source_poi_name,
                    "target_poi": target_poi_name,
                    "started_at": time_seconds
                }
                poi_last_raid_attacker = next_attacker
                events.append({
                    "kind": "raid_started",
                    "attacker_faction": next_attacker,
                    "defender_faction": str(poi_raid_state.get("defender_faction", "")),
                    "source_poi": source_poi_name,
                    "target_poi": target_poi_name
                })

    return {
        "state": poi_raid_state.duplicate(true),
        "events": events
    }


func _end_raid(outcome: String, time_seconds: float) -> Dictionary:
    var event := {
        "kind": "raid_ended",
        "outcome": outcome,
        "attacker_faction": str(poi_raid_state.get("attacker_faction", "")),
        "defender_faction": str(poi_raid_state.get("defender_faction", "")),
        "source_poi": str(poi_raid_state.get("source_poi", "")),
        "target_poi": str(poi_raid_state.get("target_poi", "")),
        "duration": max(0.0, time_seconds - float(poi_raid_state.get("started_at", time_seconds)))
    }
    poi_raid_state.clear()
    poi_raid_cooldown_until = time_seconds + poi_raid_cooldown
    return event


func _find_structure_poi(snapshot: Dictionary, structure_state: String) -> String:
    for poi_name_variant in snapshot.keys():
        var poi_name: String = str(poi_name_variant)
        var details: Dictionary = snapshot.get(poi_name, {})
        if str(details.get("structure_state", "")) == structure_state and bool(details.get("structure_active", false)):
            return poi_name
    return ""


func _get_raid_role_for_poi(poi_name: String) -> String:
    if not bool(poi_raid_state.get("active", false)):
        return "none"
    if str(poi_raid_state.get("source_poi", "")) == poi_name:
        return "source"
    if str(poi_raid_state.get("target_poi", "")) == poi_name:
        return "target"
    return "none"


func _structure_color(structure_state: String) -> Color:
    match structure_state:
        "human_outpost":
            return Color(0.52, 0.80, 1.0)
        "monster_lair":
            return Color(1.0, 0.52, 0.64)
        _:
            return Color(0.8, 0.8, 0.8)


func _get_status_color(status: String) -> Color:
    match status:
        "human_dominant":
            return Color(0.43, 0.76, 1.0)
        "monster_dominant":
            return Color(1.0, 0.45, 0.42)
        "contested":
            return Color(1.0, 0.86, 0.36)
        _:
            return Color(0.62, 0.62, 0.62)


func _set_mesh_color(mesh: MeshInstance3D, color: Color, emission_strength: float) -> void:
    var material := mesh.material_override as StandardMaterial3D
    if material == null:
        return
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * emission_strength


func _apply_world_event_visual_bias(
    ring: MeshInstance3D,
    beacon: MeshInstance3D,
    status_color: Color,
    intensity: float,
    time_seconds: float
) -> void:
    match world_event_visual_id:
        "mana_surge":
            var surge_mix := 0.22 + 0.06 * sin(time_seconds * 5.0)
            _set_mesh_color(beacon, status_color.lerp(Color(0.74, 0.56, 1.0), surge_mix), intensity + 0.22)
        "monster_frenzy":
            var frenzy_mix := 0.24 + 0.05 * sin(time_seconds * 6.2)
            _set_mesh_color(ring, status_color.lerp(Color(1.0, 0.38, 0.30), frenzy_mix), intensity + 0.18)
        "sanctuary_calm":
            var calm_mix := 0.20 + 0.04 * sin(time_seconds * 3.4)
            _set_mesh_color(ring, status_color.lerp(Color(0.52, 0.82, 1.0), calm_mix), intensity + 0.10)
