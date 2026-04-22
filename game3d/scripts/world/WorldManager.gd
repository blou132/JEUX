extends Node3D
class_name WorldManager

@export var map_size: float = 96.0
@export var nav_cell_size: float = 2.0
@export var wander_radius: float = 14.0
@export var poi_guidance_distance: float = 28.0

var human_spawn_points: Array[Vector3] = []
var monster_spawn_points: Array[Vector3] = []
var pois: Array[Dictionary] = []
var poi_nodes: Dictionary = {}
var poi_runtime_status: Dictionary = {}


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


func update_poi_runtime(actors: Array, time_seconds: float) -> Dictionary:
    var snapshot: Dictionary = {}
    var events: Array[Dictionary] = []

    for poi in pois:
        var poi_name: String = str(poi.get("name", "poi"))
        var counts: Dictionary = _count_poi_occupancy(poi, actors)
        var human_count: int = int(counts.get("human", 0))
        var monster_count: int = int(counts.get("monster", 0))
        var total_count: int = human_count + monster_count
        var status: String = _compute_poi_status(human_count, monster_count)
        var activity: String = _compute_activity_level(total_count)

        snapshot[poi_name] = {
            "human": human_count,
            "monster": monster_count,
            "total": total_count,
            "status": status,
            "activity": activity
        }

        _apply_poi_visual_state(poi_name, status, total_count, time_seconds)

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

        poi_runtime_status[poi_name] = status

    return {
        "snapshot": snapshot,
        "events": events
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


func _count_poi_occupancy(poi: Dictionary, actors: Array) -> Dictionary:
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

    return {
        "human": humans,
        "monster": monsters
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


func _apply_poi_visual_state(poi_name: String, status: String, total_count: int, time_seconds: float) -> void:
    var poi_node: Node3D = poi_nodes.get(poi_name, null)
    if poi_node == null:
        return

    var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
    var pillar := poi_node.get_node_or_null("Pillar") as MeshInstance3D
    var beacon := poi_node.get_node_or_null("Beacon") as MeshInstance3D
    if ring == null or pillar == null or beacon == null:
        return

    var base_scale := 1.0 + min(total_count, 10) * 0.045
    if status == "contested":
        base_scale *= (1.0 + 0.06 * sin(time_seconds * 6.0))
    ring.scale = Vector3(base_scale, 1.0, base_scale)

    var status_color := _get_status_color(status)
    var intensity := 0.24 + min(total_count, 10) * 0.05

    _set_mesh_color(ring, status_color, intensity + 0.05)
    _set_mesh_color(beacon, status_color, intensity + 0.10)
    _set_mesh_color(pillar, status_color.darkened(0.18), intensity * 0.62)


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
