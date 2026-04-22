extends Node3D
class_name Actor

static var _next_actor_id: int = 1

var actor_id: int = 0
var actor_kind: String = "actor"
var faction: String = "neutral"
var human_role: String = ""

var max_hp: float = 100.0
var hp: float = 100.0
var max_energy: float = 100.0
var energy: float = 100.0
var progress_xp: float = 0.0
var level: int = 1
var max_level: int = 3
var level_xp_thresholds: Array[float] = [0.0, 14.0, 34.0]
var survival_xp_interval: float = 7.5
var _survival_xp_timer: float = 0.0

var speed: float = 4.0
var vision_range: float = 16.0
var attack_range: float = 1.9
var flee_health_ratio: float = 0.30

var melee_damage: float = 12.0
var melee_cooldown: float = 1.0
var melee_cooldown_left: float = 0.0

var magic_enabled: bool = false
var magic_damage: float = 10.0
var magic_range: float = 12.0
var magic_cooldown: float = 3.0
var magic_cooldown_left: float = 0.0
var magic_energy_cost: float = 10.0
var nova_enabled: bool = false
var nova_damage: float = 14.0
var nova_radius: float = 3.2
var nova_energy_cost: float = 16.0
var control_enabled: bool = false
var control_range: float = 10.0
var control_duration: float = 2.0
var control_slow_multiplier: float = 0.62
var control_energy_cost: float = 10.0
var magic_usage_bias: float = 0.55
var nova_usage_bias: float = 0.45
var control_usage_bias: float = 0.35
var slow_time_left: float = 0.0
var slow_multiplier: float = 1.0

var energy_drain_rate: float = 2.0
var exhaustion_damage_rate: float = 6.0

var state: String = "wander"
var last_reason: String = "spawned"
var target_actor: Actor = null
var target_position: Vector3 = Vector3.ZERO

var has_wander_target: bool = false
var wander_target: Vector3 = Vector3.ZERO
var age_seconds: float = 0.0

var is_dead: bool = false
var death_reason: String = ""
var death_reported: bool = false
var last_attacker: Actor = null
var _body_visual: MeshInstance3D = null
var _base_body_color: Color = Color(0.75, 0.75, 0.75)


func _ready() -> void:
    if actor_id == 0:
        actor_id = _next_actor_id
        _next_actor_id += 1

    hp = clamp(hp, 0.0, max_hp)
    energy = clamp(energy, 0.0, max_energy)
    _build_visual()


func _enter_tree() -> void:
    if actor_id == 0:
        actor_id = _next_actor_id
        _next_actor_id += 1


func tick_actor(
    delta: float,
    world: WorldManager,
    all_actors: Array,
    ai: AgentAI,
    combat: CombatSystem,
    magic: MagicSystem,
    game_loop: GameLoop
) -> void:
    if is_dead:
        _report_death_if_needed(game_loop)
        return

    age_seconds += delta
    melee_cooldown_left = max(0.0, melee_cooldown_left - delta)
    magic_cooldown_left = max(0.0, magic_cooldown_left - delta)
    _update_control_state(delta)
    _update_survival_progress(delta, game_loop)

    _update_energy_and_exhaustion(delta)
    if is_dead:
        _report_death_if_needed(game_loop)
        return

    var previous_state := state
    var decision: Dictionary = ai.decide_action(self, world, all_actors)
    state = str(decision.get("state", "wander"))
    last_reason = str(decision.get("reason", "none"))
    target_actor = decision.get("target", null)
    target_position = decision.get("target_position", global_position)

    if previous_state != state:
        game_loop.register_state_change(self, previous_state, state, last_reason)

    match state:
        "flee":
            if target_actor != null:
                _move_away_from(target_actor.global_position, delta, world, 1.18)
            else:
                _wander(delta, world)
        "reposition":
            if target_actor != null:
                _move_away_from(target_actor.global_position, delta, world, 1.06)
            else:
                _wander(delta, world)
        "detect":
            if target_actor != null:
                _move_towards(target_actor.global_position, delta, world, 0.95)
            else:
                _wander(delta, world)
        "chase":
            if target_actor != null:
                _move_towards(target_actor.global_position, delta, world, 1.05)
            else:
                _wander(delta, world)
        "attack":
            if target_actor != null and not combat.try_melee(self, target_actor, game_loop):
                _move_towards(target_actor.global_position, delta, world, 1.0)
            else:
                _spend_energy(delta * 0.20)
        "cast":
            if target_actor != null and not magic.try_cast(self, target_actor, game_loop):
                _move_towards(target_actor.global_position, delta, world, 1.0)
        "cast_control":
            if target_actor != null and not magic.try_cast_control(self, target_actor, game_loop):
                _move_towards(target_actor.global_position, delta, world, 0.95)
        "cast_nova":
            if not magic.try_cast_nova(self, all_actors, game_loop):
                if target_actor != null:
                    _move_towards(target_actor.global_position, delta, world, 1.0)
                else:
                    _wander(delta, world)
        "poi":
            _move_towards(target_position, delta, world, 0.90)
        "wander":
            _wander(delta, world)
        _:
            _wander(delta, world)

    _report_death_if_needed(game_loop)


func apply_damage(amount: float, source: Actor, damage_type: String) -> void:
    if is_dead or amount <= 0.0:
        return

    hp -= amount
    if source != null:
        last_attacker = source

    if hp <= 0.0:
        hp = 0.0
        is_dead = true
        state = "dead"
        death_reason = damage_type


func can_cast_magic() -> bool:
    return magic_enabled and magic_cooldown_left <= 0.0 and energy >= magic_energy_cost


func can_cast_nova() -> bool:
    return nova_enabled and magic_cooldown_left <= 0.0 and energy >= nova_energy_cost


func can_cast_control() -> bool:
    return control_enabled and magic_cooldown_left <= 0.0 and energy >= control_energy_cost


func apply_slow(multiplier: float, duration: float) -> void:
    var new_multiplier := clamp(multiplier, 0.35, 1.0)
    var new_duration := max(0.1, duration)
    if slow_time_left <= 0.0 or new_multiplier < slow_multiplier:
        slow_multiplier = new_multiplier
    slow_time_left = max(slow_time_left, new_duration)
    _refresh_control_visual()


func is_slowed() -> bool:
    return slow_time_left > 0.0


func is_enemy(other: Actor) -> bool:
    return other != null and other.faction != faction


func mark_death_reported() -> void:
    death_reported = true


func role_tag() -> String:
    if human_role == "":
        return ""
    return "[%s]" % human_role


func level_tag() -> String:
    return "[L%d]" % level


func award_progress_xp(amount: float, reason: String, game_loop: GameLoop) -> void:
    if is_dead or amount <= 0.0:
        return

    progress_xp += amount
    _check_level_up(reason, game_loop)


func _build_visual() -> void:
    var body := MeshInstance3D.new()
    body.name = "Body"
    var capsule := CapsuleMesh.new()
    capsule.radius = 0.45
    capsule.height = 1.4
    if actor_kind == "brute_monster":
        capsule.radius = 0.60
        capsule.height = 1.9
    elif actor_kind == "ranged_monster":
        capsule.radius = 0.38
        capsule.height = 1.25
    body.mesh = capsule
    if actor_kind == "brute_monster":
        body.position.y = 1.2
    elif actor_kind == "ranged_monster":
        body.position.y = 0.92
    else:
        body.position.y = 1.0

    var material := StandardMaterial3D.new()
    material.roughness = 0.8

    if faction == "human":
        material.albedo_color = _human_role_color()
    elif actor_kind == "brute_monster":
        material.albedo_color = Color(0.78, 0.20, 0.20)
    elif actor_kind == "ranged_monster":
        material.albedo_color = Color(0.86, 0.73, 0.30)
    elif faction == "monster":
        material.albedo_color = Color(0.95, 0.40, 0.40)
    else:
        material.albedo_color = Color(0.75, 0.75, 0.75)

    body.material_override = material
    add_child(body)
    _body_visual = body
    _base_body_color = material.albedo_color
    _refresh_control_visual()


func _wander(delta: float, world: WorldManager) -> void:
    if not has_wander_target or global_position.distance_to(wander_target) < 1.0:
        wander_target = world.get_wander_point(global_position)
        has_wander_target = true

    _move_towards(wander_target, delta, world, 0.82)


func _move_towards(target_position: Vector3, delta: float, world: WorldManager, speed_multiplier: float = 1.0) -> void:
    var to_target := target_position - global_position
    to_target.y = 0.0

    if to_target.length() < 0.05:
        return

    var final_speed_multiplier := speed_multiplier * _movement_control_factor()
    var velocity := to_target.normalized() * speed * final_speed_multiplier
    var next_position := global_position + velocity * delta
    global_position = world.clamp_to_world(next_position)
    _spend_energy(energy_drain_rate * 0.30 * final_speed_multiplier * delta)


func _move_away_from(danger_position: Vector3, delta: float, world: WorldManager, speed_multiplier: float = 1.0) -> void:
    var away_vector := global_position - danger_position
    away_vector.y = 0.0

    if away_vector.length() < 0.05:
        away_vector = Vector3.RIGHT

    var final_speed_multiplier := speed_multiplier * _movement_control_factor()
    var velocity := away_vector.normalized() * speed * final_speed_multiplier
    var next_position := global_position + velocity * delta
    global_position = world.clamp_to_world(next_position)
    _spend_energy(energy_drain_rate * 0.42 * final_speed_multiplier * delta)


func _update_energy_and_exhaustion(delta: float) -> void:
    _spend_energy(energy_drain_rate * delta)

    if energy <= 0.0:
        apply_damage(exhaustion_damage_rate * delta, null, "exhaustion")


func _spend_energy(amount: float) -> void:
    energy = clamp(energy - amount, 0.0, max_energy)


func _update_control_state(delta: float) -> void:
    if slow_time_left <= 0.0:
        slow_multiplier = 1.0
        _refresh_control_visual()
        return

    slow_time_left = max(0.0, slow_time_left - delta)
    if slow_time_left <= 0.0:
        slow_multiplier = 1.0
    _refresh_control_visual()


func _movement_control_factor() -> float:
    return slow_multiplier if slow_time_left > 0.0 else 1.0


func _update_survival_progress(delta: float, game_loop: GameLoop) -> void:
    if level >= max_level:
        return
    _survival_xp_timer += delta
    if _survival_xp_timer < survival_xp_interval:
        return

    _survival_xp_timer -= survival_xp_interval
    award_progress_xp(1.0, "survival", game_loop)


func _check_level_up(reason: String, game_loop: GameLoop) -> void:
    while level < max_level:
        var next_threshold: float = level_xp_thresholds[level]
        if progress_xp < next_threshold:
            return

        var old_level := level
        level += 1
        _apply_level_bonus()
        _spawn_level_up_signal()
        if game_loop != null:
            game_loop.register_level_up(self, old_level, level, reason)


func _apply_level_bonus() -> void:
    var old_max_hp: float = max_hp
    var old_max_energy: float = max_energy

    max_hp *= 1.055
    max_energy *= 1.04
    melee_damage *= 1.045
    magic_damage *= 1.05
    speed *= 1.018
    vision_range *= 1.01

    max_hp = min(max_hp, 240.0)
    max_energy = min(max_energy, 220.0)
    melee_damage = min(melee_damage, 38.0)
    magic_damage = min(magic_damage, 34.0)
    speed = min(speed, 7.1)

    hp += max_hp - old_max_hp
    energy += max_energy - old_max_energy
    hp = clamp(hp, 0.0, max_hp)
    energy = clamp(energy, 0.0, max_energy)


func _refresh_control_visual() -> void:
    if _body_visual == null:
        return
    var material := _body_visual.material_override as StandardMaterial3D
    if material == null:
        return

    if slow_time_left > 0.0:
        var slow_color := _base_body_color.lerp(Color(0.46, 0.92, 1.0), 0.35)
        material.albedo_color = slow_color
        material.emission_enabled = true
        material.emission = Color(0.42, 0.90, 1.0) * 0.28
    else:
        material.albedo_color = _base_body_color
        material.emission_enabled = false


func _spawn_level_up_signal() -> void:
    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.2
    mesh.bottom_radius = 1.2
    mesh.height = 0.10
    ring.mesh = mesh
    ring.position = Vector3(0.0, 0.1, 0.0)
    ring.scale = Vector3(0.15, 1.0, 0.15)

    var material := StandardMaterial3D.new()
    var color := Color(1.0, 0.90, 0.32)
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.2
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.4, 0.34)
    tween.finished.connect(ring.queue_free)


func _human_role_color() -> Color:
    match human_role:
        "mage":
            return Color(0.55, 0.58, 1.0)
        "scout":
            return Color(0.42, 0.95, 0.62)
        _:
            return Color(0.45, 0.70, 1.00)


func _report_death_if_needed(game_loop: GameLoop) -> void:
    if is_dead and not death_reported:
        var reason := death_reason if death_reason != "" else "unknown"
        game_loop.register_death(self, last_attacker, reason)
