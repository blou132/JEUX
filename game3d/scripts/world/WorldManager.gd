extends Node3D
class_name WorldManager

@export var map_size: float = 96.0
@export var nav_cell_size: float = 2.0
@export var wander_radius: float = 14.0
@export var poi_guidance_distance: float = 28.0

var human_spawn_points: Array[Vector3] = []
var monster_spawn_points: Array[Vector3] = []
var pois: Array[Dictionary] = []


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

    for poi in pois:
        poi_root.add_child(_make_poi_marker(poi))


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
    ring.position.y = 0.05
    ring.material_override = _make_material(color * 0.85)
    poi_node.add_child(ring)

    var pillar := MeshInstance3D.new()
    var pillar_mesh := BoxMesh.new()
    pillar_mesh.size = Vector3(0.8, 2.0, 0.8)
    pillar.mesh = pillar_mesh
    pillar.position.y = 1.0
    pillar.material_override = _make_material(color)
    poi_node.add_child(pillar)

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
