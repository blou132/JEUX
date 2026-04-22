extends Node3D
class_name MagicSystem

@export var projectile_speed: float = 13.0
@export var projectile_radius: float = 0.70
@export var projectile_lifetime: float = 2.8
@export var nova_visual_duration: float = 0.30
@export var control_visual_duration: float = 0.32

var projectiles: Array[Dictionary] = []


func try_cast(caster: Actor, target: Actor, game_loop: GameLoop) -> bool:
    if caster == null or target == null:
        return false
    if caster.is_dead or target.is_dead:
        return false
    if not caster.can_cast_magic():
        return false
    if not caster.is_enemy(target):
        return false

    var distance: float = caster.global_position.distance_to(target.global_position)
    if distance > caster.magic_range:
        return false

    var direction := (target.global_position - caster.global_position)
    direction.y = 0.0
    if direction.length() < 0.01:
        return false
    direction = direction.normalized()

    caster.magic_cooldown_left = caster.magic_cooldown
    caster.energy = max(0.0, caster.energy - caster.magic_energy_cost)

    var visual := _create_projectile_visual(caster.faction)
    visual.global_position = caster.global_position + Vector3(0.0, 1.2, 0.0)
    add_child(visual)

    projectiles.append({
        "node": visual,
        "position": visual.global_position,
        "direction": direction,
        "lifetime": projectile_lifetime,
        "damage": caster.magic_damage,
        "caster": caster,
        "faction": caster.faction
    })

    game_loop.register_cast(caster, target, "bolt")
    return true


func try_cast_nova(caster: Actor, actors: Array, game_loop: GameLoop) -> bool:
    if caster == null or caster.is_dead:
        return false
    if not caster.can_cast_nova():
        return false

    var hits: int = 0
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if not caster.is_enemy(actor):
            continue

        var distance: float = caster.global_position.distance_to(actor.global_position)
        if distance > caster.nova_radius:
            continue

        var falloff := clamp(1.0 - (distance / max(0.001, caster.nova_radius)) * 0.25, 0.75, 1.0)
        var damage: float = caster.nova_damage * falloff
        actor.apply_damage(damage, caster, "nova")
        game_loop.register_attack("magic", caster, actor, damage)
        hits += 1

        if actor.is_dead:
            game_loop.register_death(actor, caster, "nova")

    if hits == 0:
        return false

    caster.magic_cooldown_left = caster.magic_cooldown * 1.15
    caster.energy = max(0.0, caster.energy - caster.nova_energy_cost)
    _spawn_nova_visual(caster.global_position + Vector3(0.0, 0.25, 0.0), caster.nova_radius, caster.faction)
    game_loop.register_cast(caster, null, "nova")
    return true


func try_cast_control(caster: Actor, target: Actor, game_loop: GameLoop) -> bool:
    if caster == null or target == null:
        return false
    if caster.is_dead or target.is_dead:
        return false
    if not caster.can_cast_control():
        return false
    if not caster.is_enemy(target):
        return false
    if target.is_slowed():
        return false

    var distance: float = caster.global_position.distance_to(target.global_position)
    if distance > caster.control_range:
        return false

    caster.magic_cooldown_left = caster.magic_cooldown * 0.95
    caster.energy = max(0.0, caster.energy - caster.control_energy_cost)

    target.apply_slow(caster.control_slow_multiplier, caster.control_duration)
    _spawn_control_visual(target.global_position + Vector3(0.0, 0.06, 0.0), caster.faction)

    game_loop.register_cast(caster, target, "control")
    game_loop.register_control(caster, target, caster.control_duration, caster.control_slow_multiplier)
    return true


func tick_projectiles(delta: float, actors: Array, game_loop: GameLoop) -> void:
    for idx in range(projectiles.size() - 1, -1, -1):
        var projectile: Dictionary = projectiles[idx]
        var node: Node3D = projectile["node"]
        if node == null:
            projectiles.remove_at(idx)
            continue

        var position: Vector3 = projectile["position"]
        var direction: Vector3 = projectile["direction"]
        position += direction * projectile_speed * delta
        projectile["position"] = position
        node.global_position = position

        projectile["lifetime"] = float(projectile["lifetime"]) - delta
        if float(projectile["lifetime"]) <= 0.0:
            _remove_projectile(idx)
            continue

        var hit_target: Actor = _find_collision_target(projectile, actors)
        if hit_target != null:
            var caster: Actor = projectile["caster"]
            var damage: float = float(projectile["damage"])
            hit_target.apply_damage(damage, caster, "magic")
            game_loop.register_attack("magic", caster, hit_target, damage)

            if hit_target.is_dead:
                game_loop.register_death(hit_target, caster, "magic")

            _remove_projectile(idx)
            continue

        projectiles[idx] = projectile


func _find_collision_target(projectile: Dictionary, actors: Array) -> Actor:
    var position: Vector3 = projectile["position"]
    var faction: String = str(projectile["faction"])

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction == faction:
            continue

        var check_position: Vector3 = actor.global_position + Vector3(0.0, 1.0, 0.0)
        if position.distance_to(check_position) <= projectile_radius:
            return actor

    return null


func _remove_projectile(index: int) -> void:
    var projectile: Dictionary = projectiles[index]
    var node: Node3D = projectile["node"]
    if node != null:
        node.queue_free()
    projectiles.remove_at(index)


func _create_projectile_visual(faction: String) -> MeshInstance3D:
    var projectile := MeshInstance3D.new()
    var sphere := SphereMesh.new()
    sphere.radius = 0.20
    sphere.height = 0.40
    projectile.mesh = sphere

    var color := Color(0.35, 0.78, 1.0) if faction == "human" else Color(1.0, 0.45, 0.45)
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.65
    projectile.material_override = material

    return projectile


func _spawn_nova_visual(center: Vector3, radius: float, faction: String) -> void:
    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius
    mesh.height = 0.12
    ring.mesh = mesh
    ring.global_position = center
    ring.scale = Vector3(0.05, 1.0, 0.05)

    var color := Color(0.40, 0.78, 1.0) if faction == "human" else Color(1.0, 0.45, 0.45)
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.95
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE, nova_visual_duration)
    tween.finished.connect(ring.queue_free)


func _spawn_control_visual(center: Vector3, faction: String) -> void:
    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.1
    mesh.bottom_radius = 1.1
    mesh.height = 0.10
    ring.mesh = mesh
    ring.global_position = center
    ring.scale = Vector3(0.45, 1.0, 0.45)

    var color := Color(0.30, 0.86, 0.92) if faction == "human" else Color(0.98, 0.55, 0.32)
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 0.95
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.24, control_visual_duration)
    tween.finished.connect(ring.queue_free)
