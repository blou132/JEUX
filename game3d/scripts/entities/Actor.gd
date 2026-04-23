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
var kill_count: int = 0
var is_champion: bool = false
var champion_reason: String = ""
var renown: float = 0.0
var notoriety: float = 0.0
var renown_decay_per_sec: float = 0.16
var notoriety_decay_per_sec: float = 0.14

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
var allegiance_id: String = ""
var home_poi: String = ""
var rally_leader_id: int = 0
var rally_bonus_active: bool = false
var rally_relic_bonus_active: bool = false
var special_arrival_id: String = ""
var special_arrival_title: String = ""
var relic_id: String = ""
var relic_title: String = ""
var bounty_marked: bool = false
var world_speed_multiplier: float = 1.0
var world_energy_regen_per_sec: float = 0.0

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
    _update_world_event_context(game_loop)
    decay_notability(delta)

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
    _update_rally_context_from_decision(decision)

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
        "raid":
            _move_towards(target_position, delta, world, 0.98)
        "hunt":
            _move_towards(target_position, delta, world, 1.00)
        "rally":
            if target_actor != null:
                _move_towards(target_actor.global_position, delta, world, 0.96)
            else:
                _move_towards(target_position, delta, world, 0.92)
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


func champion_tag() -> String:
    if not is_champion:
        return ""
    if faction == "human":
        return "[HERO]"
    return "[ELITE]"


func allegiance_tag() -> String:
    if allegiance_id == "":
        return ""
    var short_id := allegiance_id.replace(":", ".")
    return "[%s]" % short_id


func special_tag() -> String:
    match special_arrival_id:
        "summoned_hero":
            return "[SUMMONED]"
        "calamity_invader":
            return "[CALAMITY]"
        _:
            return ""


func relic_tag() -> String:
    match relic_id:
        "arcane_sigil":
            return "[ARCANE]"
        "oath_standard":
            return "[STANDARD]"
        _:
            return ""


func bounty_tag() -> String:
    if not bounty_marked:
        return ""
    return "[MARKED]"


func renown_tag() -> String:
    if renown >= 70.0:
        return "[RENOWN++]"
    if renown >= 40.0:
        return "[RENOWN+]"
    return ""


func notoriety_tag() -> String:
    if notoriety >= 70.0:
        return "[INFAMOUS]"
    if notoriety >= 40.0:
        return "[NOTORIOUS]"
    return ""


func can_lead_rally() -> bool:
    if is_dead:
        return false
    if is_champion or is_special_arrival() or has_relic():
        return true
    return renown >= 28.0


func has_high_notoriety() -> bool:
    return notoriety >= 52.0


func is_special_arrival() -> bool:
    return special_arrival_id != ""


func has_relic() -> bool:
    return relic_id != ""


func can_receive_relic() -> bool:
    return relic_id == ""


func set_special_arrival(origin_id: String, title: String) -> void:
    special_arrival_id = origin_id
    special_arrival_title = title
    _refresh_control_visual()


func apply_special_arrival_bonus(origin_id: String = "") -> void:
    if origin_id != "":
        special_arrival_id = origin_id
    if special_arrival_id == "" or is_dead:
        return

    var old_max_hp: float = max_hp
    var old_max_energy: float = max_energy

    match special_arrival_id:
        "summoned_hero":
            max_hp *= 1.07
            max_energy *= 1.09
            magic_damage *= 1.08
            control_duration += 0.12
            speed *= 1.02
        "calamity_invader":
            max_hp *= 1.12
            melee_damage *= 1.10
            speed *= 1.05
            vision_range += 0.9
            flee_health_ratio *= 0.82

    max_hp = min(max_hp, 330.0)
    max_energy = min(max_energy, 265.0)
    melee_damage = min(melee_damage, 49.0)
    magic_damage = min(magic_damage, 44.0)
    speed = min(speed, 8.1)
    control_duration = min(control_duration, 3.2)
    flee_health_ratio = clampf(flee_health_ratio, 0.08, 0.45)

    hp += max_hp - old_max_hp
    energy += max_energy - old_max_energy
    hp = clamp(hp, 0.0, max_hp)
    energy = clamp(energy, 0.0, max_energy)
    _spawn_special_arrival_signal()
    _refresh_control_visual()


func set_relic(next_relic_id: String, next_relic_title: String) -> void:
    relic_id = next_relic_id
    relic_title = next_relic_title
    _spawn_relic_signal()
    _refresh_control_visual()


func clear_relic() -> void:
    relic_id = ""
    relic_title = ""
    rally_relic_bonus_active = false
    _refresh_control_visual()


func set_bounty_marked(enabled: bool) -> void:
    if bounty_marked == enabled:
        return
    bounty_marked = enabled
    if bounty_marked:
        _spawn_bounty_signal()
    _refresh_control_visual()


func set_allegiance(next_allegiance_id: String, next_home_poi: String) -> void:
    allegiance_id = next_allegiance_id
    home_poi = next_home_poi
    _refresh_control_visual()


func award_progress_xp(amount: float, reason: String, game_loop: GameLoop) -> void:
    if is_dead or amount <= 0.0:
        return

    progress_xp += amount
    _check_level_up(reason, game_loop)


func register_kill() -> void:
    kill_count += 1


func add_renown(amount: float) -> float:
    if is_dead or amount <= 0.0:
        return 0.0
    var before := renown
    renown = clampf(renown + amount, 0.0, 100.0)
    if not is_equal_approx(before, renown):
        _refresh_control_visual()
    return renown - before


func add_notoriety(amount: float) -> float:
    if is_dead or amount <= 0.0:
        return 0.0
    var before := notoriety
    notoriety = clampf(notoriety + amount, 0.0, 100.0)
    if not is_equal_approx(before, notoriety):
        _refresh_control_visual()
    return notoriety - before


func decay_notability(delta: float) -> void:
    if is_dead or delta <= 0.0:
        return

    var damping: float = 1.0
    if is_champion:
        damping *= 0.72
    if is_special_arrival():
        damping *= 0.68
    if has_relic():
        damping *= 0.74
    if bounty_marked:
        damping *= 0.58

    var renown_before := renown
    var notoriety_before := notoriety
    renown = max(0.0, renown - renown_decay_per_sec * damping * delta)
    notoriety = max(0.0, notoriety - notoriety_decay_per_sec * damping * delta)
    if absf(renown_before - renown) > 0.001 or absf(notoriety_before - notoriety) > 0.001:
        _refresh_control_visual()


func is_ready_for_champion(
    min_level: int,
    min_kills: int,
    min_age_seconds: float,
    min_progress_xp: float
) -> bool:
    if is_dead or is_champion:
        return false
    if level < min_level:
        return false
    if kill_count < min_kills:
        return false
    if age_seconds < min_age_seconds:
        return false
    if progress_xp < min_progress_xp:
        return false
    return true


func promote_to_champion(reason: String) -> void:
    if is_dead or is_champion:
        return

    is_champion = true
    champion_reason = reason
    _apply_champion_bonus()
    _spawn_champion_promotion_signal()
    _refresh_control_visual()


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

    var final_speed_multiplier := speed_multiplier * _movement_control_factor() * world_speed_multiplier
    var velocity := to_target.normalized() * speed * final_speed_multiplier
    var next_position := global_position + velocity * delta
    global_position = world.clamp_to_world(next_position)
    _spend_energy(energy_drain_rate * 0.30 * final_speed_multiplier * _rally_energy_drain_multiplier() * delta)


func _move_away_from(danger_position: Vector3, delta: float, world: WorldManager, speed_multiplier: float = 1.0) -> void:
    var away_vector := global_position - danger_position
    away_vector.y = 0.0

    if away_vector.length() < 0.05:
        away_vector = Vector3.RIGHT

    var final_speed_multiplier := speed_multiplier * _movement_control_factor() * world_speed_multiplier
    var velocity := away_vector.normalized() * speed * final_speed_multiplier
    var next_position := global_position + velocity * delta
    global_position = world.clamp_to_world(next_position)
    _spend_energy(energy_drain_rate * 0.42 * final_speed_multiplier * _rally_energy_drain_multiplier() * delta)


func _update_energy_and_exhaustion(delta: float) -> void:
    _spend_energy(energy_drain_rate * _rally_energy_drain_multiplier() * delta)
    if world_energy_regen_per_sec > 0.0:
        energy = min(max_energy, energy + world_energy_regen_per_sec * delta)

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


func _update_rally_context_from_decision(decision: Dictionary) -> void:
    var rally_leader: Actor = decision.get("rally_leader", null)
    if rally_leader == null or rally_leader == self or rally_leader.is_dead or rally_leader.faction != faction or not rally_leader.can_lead_rally():
        rally_leader_id = 0
        rally_bonus_active = false
        rally_relic_bonus_active = false
        return

    rally_leader_id = rally_leader.actor_id
    rally_bonus_active = bool(decision.get("rally_bonus", false))


func _rally_energy_drain_multiplier() -> float:
    if is_champion:
        return 1.0
    var multiplier: float = 1.0
    if rally_bonus_active:
        multiplier *= 0.92
    if rally_relic_bonus_active:
        multiplier *= 0.93
    return multiplier


func _update_world_event_context(game_loop: GameLoop) -> void:
    if game_loop == null:
        world_speed_multiplier = 1.0
        world_energy_regen_per_sec = 0.0
        return
    world_speed_multiplier = clampf(game_loop.get_speed_multiplier(self), 0.72, 1.35)
    world_energy_regen_per_sec = max(0.0, game_loop.get_energy_regen_bonus_per_sec(self))


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


func _apply_champion_bonus() -> void:
    var old_max_hp: float = max_hp
    var old_max_energy: float = max_energy

    max_hp *= 1.08
    max_energy *= 1.06
    melee_damage *= 1.07
    magic_damage *= 1.07
    speed *= 1.03

    if faction == "human":
        if human_role == "fighter":
            melee_damage += 1.4
        elif human_role == "mage":
            magic_damage += 1.5
            control_duration += 0.10
        elif human_role == "scout":
            speed += 0.14
    elif actor_kind == "brute_monster":
        melee_damage += 1.8
        max_hp += 4.0
    elif actor_kind == "ranged_monster":
        magic_damage += 1.2
        magic_range += 0.7
    else:
        melee_damage += 1.0

    max_hp = min(max_hp, 285.0)
    max_energy = min(max_energy, 245.0)
    melee_damage = min(melee_damage, 44.0)
    magic_damage = min(magic_damage, 40.0)
    speed = min(speed, 7.6)

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
        if relic_id != "":
            var relic_glow := _relic_glow_color()
            if special_arrival_id != "":
                relic_glow = relic_glow.lerp(_special_glow_color(), 0.22)
            elif is_champion:
                relic_glow = relic_glow.lerp(_champion_glow_color(), 0.22)
            material.emission_enabled = true
            material.emission = relic_glow * 0.62
        elif special_arrival_id != "":
            var special_glow := _special_glow_color()
            if is_champion:
                special_glow = special_glow.lerp(_champion_glow_color(), 0.28)
            material.emission_enabled = true
            material.emission = special_glow * 0.58
        elif is_champion:
            var champion_glow := _champion_glow_color()
            material.emission_enabled = true
            material.emission = champion_glow * 0.42
        elif allegiance_id != "":
            var allegiance_glow := _allegiance_glow_color()
            material.emission_enabled = true
            material.emission = allegiance_glow * 0.16
        else:
            material.emission_enabled = false
        if bounty_marked:
            var bounty_glow := _bounty_glow_color()
            if material.emission_enabled:
                material.emission = material.emission.lerp(bounty_glow, 0.45)
            else:
                material.emission_enabled = true
                material.emission = bounty_glow * 0.34
        var renown_signal := _notability_signal_strength(renown)
        if renown_signal > 0.0:
            var renown_glow := _renown_glow_color()
            if material.emission_enabled:
                material.emission = material.emission.lerp(renown_glow, renown_signal * 0.24)
            else:
                material.emission_enabled = true
                material.emission = renown_glow * 0.28 * renown_signal
        var notoriety_signal := _notability_signal_strength(notoriety)
        if notoriety_signal > 0.0:
            var notoriety_glow := _notoriety_glow_color()
            if material.emission_enabled:
                material.emission = material.emission.lerp(notoriety_glow, notoriety_signal * 0.26)
            else:
                material.emission_enabled = true
                material.emission = notoriety_glow * 0.30 * notoriety_signal


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


func _spawn_champion_promotion_signal() -> void:
    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.35
    mesh.bottom_radius = 1.35
    mesh.height = 0.12
    ring.mesh = mesh
    ring.position = Vector3(0.0, 0.14, 0.0)
    ring.scale = Vector3(0.18, 1.0, 0.18)

    var color := _champion_glow_color()
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.35
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.52, 0.42)
    tween.finished.connect(ring.queue_free)


func _spawn_special_arrival_signal() -> void:
    if special_arrival_id == "":
        return

    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.55
    mesh.bottom_radius = 1.55
    mesh.height = 0.12
    ring.mesh = mesh
    ring.position = Vector3(0.0, 0.16, 0.0)
    ring.scale = Vector3(0.16, 1.0, 0.16)

    var color := _special_glow_color()
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.45
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.64, 0.46)
    tween.finished.connect(ring.queue_free)


func _spawn_relic_signal() -> void:
    if relic_id == "":
        return

    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.45
    mesh.bottom_radius = 1.45
    mesh.height = 0.10
    ring.mesh = mesh
    ring.position = Vector3(0.0, 0.22, 0.0)
    ring.scale = Vector3(0.12, 1.0, 0.12)

    var color := _relic_glow_color()
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.55
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.58, 0.40)
    tween.finished.connect(ring.queue_free)


func _spawn_bounty_signal() -> void:
    if not bounty_marked:
        return

    var ring := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 1.65
    mesh.bottom_radius = 1.65
    mesh.height = 0.10
    ring.mesh = mesh
    ring.position = Vector3(0.0, 0.28, 0.0)
    ring.scale = Vector3(0.14, 1.0, 0.14)

    var color := _bounty_glow_color()
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.60
    ring.material_override = material
    add_child(ring)

    var tween := create_tween()
    tween.tween_property(ring, "scale", Vector3.ONE * 1.70, 0.34)
    tween.finished.connect(ring.queue_free)


func _champion_glow_color() -> Color:
    if faction == "human":
        return Color(1.0, 0.88, 0.34)
    return Color(1.0, 0.44, 0.58)


func _special_glow_color() -> Color:
    match special_arrival_id:
        "summoned_hero":
            return Color(0.52, 0.82, 1.0)
        "calamity_invader":
            return Color(1.0, 0.36, 0.32)
        _:
            return Color(0.88, 0.88, 0.88)


func _relic_glow_color() -> Color:
    match relic_id:
        "arcane_sigil":
            return Color(0.60, 0.70, 1.0)
        "oath_standard":
            return Color(1.0, 0.58, 0.32)
        _:
            return Color(0.90, 0.90, 0.90)


func _allegiance_glow_color() -> Color:
    if faction == "human":
        return Color(0.44, 0.78, 1.0)
    return Color(1.0, 0.56, 0.50)


func _bounty_glow_color() -> Color:
    if faction == "human":
        return Color(1.0, 0.38, 0.38)
    return Color(1.0, 0.74, 0.24)


func _renown_glow_color() -> Color:
    if faction == "human":
        return Color(0.64, 0.86, 1.0)
    return Color(1.0, 0.68, 0.78)


func _notoriety_glow_color() -> Color:
    if faction == "human":
        return Color(1.0, 0.52, 0.52)
    return Color(1.0, 0.66, 0.26)


func _notability_signal_strength(score: float) -> float:
    if score <= 35.0:
        return 0.0
    return clampf((score - 35.0) / 50.0, 0.0, 1.0)


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
