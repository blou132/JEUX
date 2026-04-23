extends Node3D
class_name WorldManager

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
var poi_raid_state: Dictionary = {}
var poi_raid_cooldown_until: float = 0.0
var poi_last_raid_attacker: String = ""


func setup_world() -> void:
    _build_ground()
    _build_spawn_points()
    _build_pois()


func tick_world(_delta: float) -> void:
    pass


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
        if str(poi.get("faction_hint", "")) == faction:
            selected = poi
            break

    if selected.is_empty():
        selected = _get_nearest_poi(actor_position)

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


func get_raid_guidance(actor_position: Vector3, faction: String) -> Dictionary:
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
    return {
        "reason": "raid_pressure:%s->%s" % [str(poi_raid_state.get("source_poi", "src")), target_name],
        "target_position": clamp_to_world(snap_to_nav_grid(target_position + jitter)),
        "distance": distance,
        "weight": 0.74
    }


func get_active_raid_state() -> Dictionary:
    return poi_raid_state.duplicate(true)


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
            "structure_seconds": structure_seconds
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

    var raid_runtime: Dictionary = _update_raid_runtime(snapshot, time_seconds)
    var raid_events: Array = raid_runtime.get("events", [])
    for raid_event in raid_events:
        events.append(raid_event)

    for poi_name in snapshot.keys():
        var details: Dictionary = snapshot.get(poi_name, {})
        details["raid_role"] = _get_raid_role_for_poi(str(poi_name))
        snapshot[poi_name] = details
        _apply_poi_visual_state(
            str(poi_name),
            str(details.get("status", "calm")),
            int(details.get("total", 0)),
            time_seconds,
            bool(details.get("influence_active", false)),
            str(details.get("structure_state", "")),
            str(details.get("raid_role", "none"))
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

    var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
    if ring != null:
        var pulse := create_tween()
        var base_scale := ring.scale
        pulse.tween_property(ring, "scale", base_scale * 1.18, 0.10)
        pulse.tween_property(ring, "scale", base_scale, 0.14)

    var flash := MeshInstance3D.new()
    flash.name = "EntryFlash"
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.3
    mesh.bottom_radius = 1.3
    mesh.height = 0.08
    flash.mesh = mesh
    flash.position = Vector3(0.0, 0.06, 0.0)
    flash.scale = Vector3(0.35, 1.0, 0.35)

    var color := Color(0.45, 0.75, 1.0) if faction == "human" else Color(1.0, 0.52, 0.46)
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

    poi_runtime_status.clear()
    poi_dominant_faction.clear()
    poi_dominance_started_at.clear()
    poi_influence_active.clear()
    poi_structure_state.clear()
    poi_structure_faction.clear()
    poi_structure_started_at.clear()
    poi_structure_unstable_started_at.clear()
    poi_raid_state.clear()
    poi_raid_cooldown_until = 0.0
    poi_last_raid_attacker = ""

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
    var ring := MeshInstance3D.new()
    var ring_mesh := CylinderMesh.new()
    ring_mesh.top_radius = 2.2
    ring_mesh.bottom_radius = 2.2
    ring_mesh.height = 0.1
    ring.mesh = ring_mesh
    ring.name = "Ring"
    ring.position.y = 0.05
    ring.material_override = _make_material(color * 0.85)
    poi_node.add_child(ring)

    var pillar := MeshInstance3D.new()
    var pillar_mesh := BoxMesh.new()
    pillar_mesh.size = Vector3(0.8, 2.0, 0.8)
    pillar.mesh = pillar_mesh
    pillar.name = "Pillar"
    pillar.position.y = 1.0
    pillar.material_override = _make_material(color)
    poi_node.add_child(pillar)

    var beacon := MeshInstance3D.new()
    var beacon_mesh := SphereMesh.new()
    beacon_mesh.radius = 0.32
    beacon_mesh.height = 0.64
    beacon.mesh = beacon_mesh
    beacon.name = "Beacon"
    beacon.position.y = 2.2
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

    return poi_node


func _make_material(color: Color) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.30
    material.roughness = 0.7
    return material


func _get_nearest_poi(position: Vector3) -> Dictionary:
    var selected: Dictionary = {}
    var closest_sq: float = INF
    for poi in pois:
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
    raid_role: String
) -> void:
    var poi_node: Node3D = poi_nodes.get(poi_name, null)
    if poi_node == null:
        return

    var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
    var pillar := poi_node.get_node_or_null("Pillar") as MeshInstance3D
    var beacon := poi_node.get_node_or_null("Beacon") as MeshInstance3D
    var structure_halo := poi_node.get_node_or_null("StructureHalo") as MeshInstance3D
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
        poi_structure_state[poi_name] = current_state
        poi_structure_faction[poi_name] = current_faction
        poi_structure_started_at[poi_name] = time_seconds
        poi_structure_unstable_started_at.erase(poi_name)
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


func _update_raid_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
    var events: Array[Dictionary] = []
    var has_outpost: bool = _find_structure_poi(snapshot, "human_outpost") != ""
    var has_lair: bool = _find_structure_poi(snapshot, "monster_lair") != ""

    var raid_active: bool = bool(poi_raid_state.get("active", false))
    if raid_active:
        var source_poi: String = str(poi_raid_state.get("source_poi", ""))
        var target_poi: String = str(poi_raid_state.get("target_poi", ""))
        var attacker_faction: String = str(poi_raid_state.get("attacker_faction", ""))
        var defender_faction: String = str(poi_raid_state.get("defender_faction", ""))
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
