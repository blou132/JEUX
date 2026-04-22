extends Node3D
class_name MagicSystem

@export var projectile_speed: float = 15.0
@export var projectile_radius: float = 0.80
@export var projectile_lifetime: float = 2.5

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

    game_loop.register_cast(caster, target)
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
