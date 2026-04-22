extends Node3D
class_name GameLoop

const TICK_RATE: float = 8.0
const MAX_EVENT_LOG: int = 14
const XP_ON_HIT: float = 1.5
const XP_ON_CAST: float = 0.75
const XP_ON_KILL: float = 5.0
const POI_INFLUENCE_ENERGY_REGEN_PER_SEC: float = 0.70
const POI_INFLUENCE_XP_INTERVAL: float = 6.0
const POI_INFLUENCE_XP_GAIN: float = 0.8

@onready var world_manager: WorldManager = $World
@onready var entities_root: Node3D = $Entities
@onready var combat_system: CombatSystem = $Systems/CombatSystem
@onready var magic_system: MagicSystem = $Systems/MagicSystem
@onready var sandbox_systems: SandboxSystems = $Systems/SandboxSystems
@onready var debug_overlay: DebugOverlay = $DebugOverlay

var ai: AgentAI = AgentAI.new()
var actors: Array = []

var tick_accumulator: float = 0.0
var tick_index: int = 0
var elapsed_time: float = 0.0

var spawns_total: int = 0
var deaths_total: int = 0
var kills_total: int = 0
var melee_hits_total: int = 0
var magic_hits_total: int = 0
var casts_total: int = 0
var bolt_casts_total: int = 0
var nova_casts_total: int = 0
var control_casts_total: int = 0
var control_applies_total: int = 0
var flee_events_total: int = 0
var engagements_total: int = 0
var poi_arrivals_total: int = 0
var poi_contests_total: int = 0
var poi_domination_changes_total: int = 0
var poi_influence_activation_events_total: int = 0
var poi_influence_deactivation_events_total: int = 0
var poi_influence_regen_ticks_total: int = 0
var poi_influence_xp_grants_total: int = 0
var level_ups_total: int = 0

var actor_poi_presence: Dictionary = {}
var poi_runtime_snapshot: Dictionary = {}
var _poi_influence_xp_timers: Dictionary = {}

var event_log: Array[String] = []


func _ready() -> void:
    randomize()
    world_manager.setup_world()
    sandbox_systems.setup(self, world_manager, entities_root)
    sandbox_systems.spawn_initial_population(actors)
    record_event("Sandbox boot complete.")


func _process(delta: float) -> void:
    tick_accumulator += delta
    var tick_dt: float = 1.0 / TICK_RATE

    while tick_accumulator >= tick_dt:
        tick_accumulator -= tick_dt
        _tick(tick_dt)


func _tick(delta: float) -> void:
    elapsed_time += delta
    tick_index += 1

    world_manager.tick_world(delta)

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        actor.tick_actor(delta, world_manager, actors, ai, combat_system, magic_system, self)

    magic_system.tick_projectiles(delta, actors, self)
    _update_poi_runtime()
    _apply_poi_influences(delta)
    _cleanup_dead_actors()
    sandbox_systems.tick_systems(delta, actors, self)

    debug_overlay.update_overlay(_build_snapshot(), event_log)


func register_spawn(actor: Actor) -> void:
    spawns_total += 1
    record_event("Spawn %s (%s)." % [_actor_label(actor), actor.faction])


func register_state_change(actor: Actor, from_state: String, to_state: String, reason: String) -> void:
    if from_state == to_state:
        return

    if to_state in ["detect", "chase", "attack", "cast", "cast_nova", "cast_control", "reposition"]:
        engagements_total += 1

    if to_state == "flee":
        flee_events_total += 1

    if to_state in ["attack", "cast", "cast_nova", "cast_control", "flee", "poi", "reposition"]:
        record_event("%s %s -> %s (%s)." % [_actor_label(actor), from_state, to_state, reason])


func register_attack(kind: String, attacker: Actor, target: Actor, damage: float) -> void:
    if kind == "melee":
        melee_hits_total += 1
    elif kind == "magic":
        magic_hits_total += 1

    record_event(
        "%s hit: %s -> %s (%.1f)."
        % [kind, _actor_label(attacker), _actor_label(target), damage]
    )

    if attacker != null and not attacker.is_dead:
        attacker.award_progress_xp(XP_ON_HIT, "%s_hit" % kind, self)


func register_cast(caster: Actor, target: Actor = null, spell_kind: String = "bolt") -> void:
    casts_total += 1
    if spell_kind == "nova":
        nova_casts_total += 1
        record_event("Cast[nova]: %s." % [_actor_label(caster)])
    elif spell_kind == "control":
        control_casts_total += 1
        if target != null:
            record_event("Cast[control]: %s -> %s." % [_actor_label(caster), _actor_label(target)])
        else:
            record_event("Cast[control]: %s." % [_actor_label(caster)])
    else:
        bolt_casts_total += 1
        if target != null:
            record_event("Cast[bolt]: %s -> %s." % [_actor_label(caster), _actor_label(target)])
        else:
            record_event("Cast[bolt]: %s." % [_actor_label(caster)])

    if caster != null and not caster.is_dead:
        caster.award_progress_xp(XP_ON_CAST, "cast_%s" % spell_kind, self)


func register_control(caster: Actor, target: Actor, duration: float, slow_multiplier: float) -> void:
    control_applies_total += 1
    var speed_loss_percent: int = int((1.0 - slow_multiplier) * 100.0)
    record_event(
        "Control[slow]: %s slowed %s (%ds, -%d%% speed)."
        % [_actor_label(caster), _actor_label(target), int(round(duration)), speed_loss_percent]
    )


func register_death(victim: Actor, killer: Actor, reason: String) -> void:
    if victim == null or victim.death_reported:
        return

    victim.mark_death_reported()
    deaths_total += 1

    if killer != null:
        kills_total += 1
        if not killer.is_dead:
            killer.award_progress_xp(XP_ON_KILL, "kill", self)
        record_event(
            "Death: %s by %s (%s)."
            % [_actor_label(victim), _actor_label(killer), reason]
        )
    else:
        record_event("Death: %s (%s)." % [_actor_label(victim), reason])


func register_level_up(actor: Actor, old_level: int, new_level: int, reason: String) -> void:
    if actor == null:
        return
    level_ups_total += 1
    record_event(
        "Level up: %s L%d -> L%d (%s)."
        % [_actor_label(actor), old_level, new_level, reason]
    )


func record_event(message: String) -> void:
    event_log.append("[%05d] %s" % [tick_index, message])
    while event_log.size() > MAX_EVENT_LOG:
        event_log.remove_at(0)


func _cleanup_dead_actors() -> void:
    for idx in range(actors.size() - 1, -1, -1):
        var actor: Actor = actors[idx]
        if actor == null:
            actors.remove_at(idx)
            continue

        if actor.is_dead:
            actor_poi_presence.erase(actor.actor_id)
            _clear_actor_influence_timers(actor.actor_id)
            actor.queue_free()
            actors.remove_at(idx)


func _build_snapshot() -> Dictionary:
    var alive_total: int = 0
    var humans_alive: int = 0
    var monsters_alive: int = 0
    var brute_alive: int = 0
    var ranged_alive: int = 0
    var slowed_alive: int = 0
    var slowed_humans: int = 0
    var slowed_monsters: int = 0
    var human_role_counts := {
        "fighter": 0,
        "mage": 0,
        "scout": 0
    }
    var hp_total: float = 0.0
    var energy_total: float = 0.0
    var level_total: float = 0.0
    var level_counts := {
        "L1": 0,
        "L2": 0,
        "L3": 0
    }
    var human_level_counts := {
        "L1": 0,
        "L2": 0,
        "L3": 0
    }
    var monster_level_counts := {
        "L1": 0,
        "L2": 0,
        "L3": 0
    }

    var state_counts := {
        "wander": 0,
        "detect": 0,
        "chase": 0,
        "attack": 0,
        "cast": 0,
        "cast_control": 0,
        "cast_nova": 0,
        "reposition": 0,
        "poi": 0,
        "flee": 0
    }

    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        alive_total += 1
        hp_total += actor.hp
        energy_total += actor.energy
        level_total += float(actor.level)

        var level_key := "L%d" % clampi(actor.level, 1, 3)
        level_counts[level_key] += 1

        if actor.faction == "human":
            humans_alive += 1
            human_level_counts[level_key] += 1
            if human_role_counts.has(actor.human_role):
                human_role_counts[actor.human_role] += 1
            if actor.is_slowed():
                slowed_humans += 1
        elif actor.faction == "monster":
            monsters_alive += 1
            monster_level_counts[level_key] += 1
            if actor.actor_kind == "brute_monster":
                brute_alive += 1
            elif actor.actor_kind == "ranged_monster":
                ranged_alive += 1
            if actor.is_slowed():
                slowed_monsters += 1
        if actor.is_slowed():
            slowed_alive += 1

        if state_counts.has(actor.state):
            state_counts[actor.state] += 1
        else:
            state_counts[actor.state] = 1

    var avg_hp: float = hp_total / alive_total if alive_total > 0 else 0.0
    var avg_energy: float = energy_total / alive_total if alive_total > 0 else 0.0
    var avg_level: float = level_total / alive_total if alive_total > 0 else 0.0
    var poi_population := world_manager.get_poi_population_snapshot(actors)
    var poi_influence_active_count: int = 0
    for poi_name in poi_runtime_snapshot.keys():
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if bool(details.get("influence_active", false)):
            poi_influence_active_count += 1

    return {
        "tick": tick_index,
        "time": elapsed_time,
        "alive_total": alive_total,
        "humans_alive": humans_alive,
        "monsters_alive": monsters_alive,
        "brute_alive": brute_alive,
        "ranged_alive": ranged_alive,
        "slowed_alive": slowed_alive,
        "slowed_humans": slowed_humans,
        "slowed_monsters": slowed_monsters,
        "human_role_counts": human_role_counts,
        "level_counts": level_counts,
        "human_level_counts": human_level_counts,
        "monster_level_counts": monster_level_counts,
        "avg_level": avg_level,
        "avg_hp": avg_hp,
        "avg_energy": avg_energy,
        "spawns_total": spawns_total,
        "deaths_total": deaths_total,
        "kills_total": kills_total,
        "melee_hits_total": melee_hits_total,
        "magic_hits_total": magic_hits_total,
        "casts_total": casts_total,
        "bolt_casts_total": bolt_casts_total,
        "nova_casts_total": nova_casts_total,
        "control_casts_total": control_casts_total,
        "control_applies_total": control_applies_total,
        "flee_events_total": flee_events_total,
        "engagements_total": engagements_total,
        "poi_arrivals_total": poi_arrivals_total,
        "poi_contests_total": poi_contests_total,
        "poi_domination_changes_total": poi_domination_changes_total,
        "poi_influence_activation_events_total": poi_influence_activation_events_total,
        "poi_influence_deactivation_events_total": poi_influence_deactivation_events_total,
        "poi_influence_regen_ticks_total": poi_influence_regen_ticks_total,
        "poi_influence_xp_grants_total": poi_influence_xp_grants_total,
        "poi_influence_active_count": poi_influence_active_count,
        "level_ups_total": level_ups_total,
        "poi_population": poi_population,
        "poi_snapshot": poi_runtime_snapshot,
        "state_counts": state_counts
    }


func _update_poi_runtime() -> void:
    var runtime_data: Dictionary = world_manager.update_poi_runtime(actors, elapsed_time)
    poi_runtime_snapshot = runtime_data.get("snapshot", {})

    var transitions: Array = runtime_data.get("events", [])
    for transition in transitions:
        var kind: String = str(transition.get("kind", ""))
        var poi_name: String = str(transition.get("poi", "poi"))
        var from_state: String = str(transition.get("from", ""))
        var to_state: String = str(transition.get("to", ""))

        if kind == "contest_started":
            poi_contests_total += 1
            record_event("POI contested: %s (%s -> %s)." % [poi_name, from_state, to_state])
        elif kind == "domination_changed":
            poi_domination_changes_total += 1
            record_event("POI domination shift: %s (%s -> %s)." % [poi_name, from_state, to_state])
        elif kind == "contest_resolved":
            record_event("POI calm again: %s." % poi_name)
        elif kind == "influence_activated":
            poi_influence_activation_events_total += 1
            var faction: String = str(transition.get("faction", ""))
            var influence_kind: String = str(transition.get("influence_kind", "influence"))
            var held_for: float = float(transition.get("dominance_seconds", 0.0))
            record_event(
                "POI influence ON: %s (%s, %s, %.1fs held)."
                % [poi_name, faction, influence_kind, held_for]
            )
        elif kind == "influence_deactivated":
            poi_influence_deactivation_events_total += 1
            record_event("POI influence OFF: %s." % poi_name)

    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        var previous_poi: String = str(actor_poi_presence.get(actor.actor_id, ""))
        var current_poi: String = world_manager.get_poi_name_for_position(actor.global_position)

        if current_poi != previous_poi:
            if current_poi != "":
                poi_arrivals_total += 1
                world_manager.trigger_poi_entry_effect(current_poi, actor.faction)
                record_event("POI arrival: %s -> %s." % [_actor_label(actor), current_poi])

            if current_poi == "":
                actor_poi_presence.erase(actor.actor_id)
            else:
                actor_poi_presence[actor.actor_id] = current_poi


func _apply_poi_influences(delta: float) -> void:
    var influences: Array[Dictionary] = world_manager.get_active_poi_influences()
    if influences.is_empty():
        _poi_influence_xp_timers.clear()
        return

    var next_timers: Dictionary = {}
    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        for influence in influences:
            var faction: String = str(influence.get("faction", ""))
            if faction == "" or actor.faction != faction:
                continue

            var center: Vector3 = influence.get("position", Vector3.ZERO)
            var radius: float = float(influence.get("radius", 0.0))
            if actor.global_position.distance_to(center) > radius:
                continue

            actor.energy = min(actor.max_energy, actor.energy + POI_INFLUENCE_ENERGY_REGEN_PER_SEC * delta)
            poi_influence_regen_ticks_total += 1

            var timer_key := "%d:%s" % [actor.actor_id, str(influence.get("name", "poi"))]
            var timer_value: float = float(_poi_influence_xp_timers.get(timer_key, 0.0))
            timer_value += delta
            if timer_value >= POI_INFLUENCE_XP_INTERVAL:
                timer_value -= POI_INFLUENCE_XP_INTERVAL
                actor.award_progress_xp(
                    POI_INFLUENCE_XP_GAIN,
                    "poi_influence:%s" % str(influence.get("name", "poi")),
                    self
                )
                poi_influence_xp_grants_total += 1
            next_timers[timer_key] = timer_value

    _poi_influence_xp_timers = next_timers


func _clear_actor_influence_timers(actor_id: int) -> void:
    var prefix := "%d:" % actor_id
    var to_remove: Array[String] = []
    for key_variant in _poi_influence_xp_timers.keys():
        var key_text := str(key_variant)
        if key_text.begins_with(prefix):
            to_remove.append(key_text)
    for key_text in to_remove:
        _poi_influence_xp_timers.erase(key_text)


func _actor_label(actor: Actor) -> String:
    if actor == null:
        return "unknown"
    var role_suffix := actor.role_tag()
    var level_suffix := actor.level_tag()
    return "%s%s%s#%d" % [actor.actor_kind, role_suffix, level_suffix, actor.actor_id]
