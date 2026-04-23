extends Node3D
class_name GameLoop

const TICK_RATE: float = 8.0
const MAX_EVENT_LOG: int = 14
const XP_ON_HIT: float = 1.5
const XP_ON_CAST: float = 0.75
const XP_ON_KILL: float = 5.0
const CHAMPION_MIN_LEVEL: int = 3
const CHAMPION_MIN_KILLS: int = 2
const CHAMPION_MIN_AGE_SECONDS: float = 26.0
const CHAMPION_MIN_PROGRESS_XP: float = 42.0
const CHAMPION_MAX_RATIO: float = 0.16
const CHAMPION_MIN_POPULATION: int = 8
const POI_INFLUENCE_ENERGY_REGEN_PER_SEC: float = 0.70
const POI_STRUCTURE_EXTRA_ENERGY_REGEN_PER_SEC: float = 0.30
const POI_INFLUENCE_XP_INTERVAL: float = 6.0
const POI_INFLUENCE_XP_GAIN: float = 0.8
const WORLD_EVENT_START_DELAY: float = 22.0
const WORLD_EVENT_COOLDOWN_MIN: float = 28.0
const WORLD_EVENT_COOLDOWN_MAX: float = 52.0
const WORLD_EVENT_TYPES: Array[String] = ["mana_surge", "monster_frenzy", "sanctuary_calm"]
const SPECIAL_ARRIVAL_START_DELAY: float = 40.0
const SPECIAL_ARRIVAL_COOLDOWN: float = 78.0
const SPECIAL_ARRIVAL_CHECK_INTERVAL: float = 3.0
const SPECIAL_ARRIVAL_TRIGGER_CHANCE: float = 0.34
const SPECIAL_ARRIVAL_MIN_DOMINANCE_SECONDS: float = 15.0
const SPECIAL_ARRIVAL_MIN_POPULATION: int = 10
const SPECIAL_ARRIVAL_MAX_ACTIVE: int = 2
const SPECIAL_ARRIVAL_MAX_ACTIVE_PER_FACTION: int = 1
const RELIC_START_DELAY: float = 52.0
const RELIC_COOLDOWN: float = 88.0
const RELIC_CHECK_INTERVAL: float = 4.0
const RELIC_TRIGGER_CHANCE: float = 0.30
const RELIC_MIN_DOMINANCE_SECONDS: float = 16.0
const RELIC_MIN_POPULATION: int = 10
const RELIC_MAX_ACTIVE: int = 2
const RELIC_HOLDER_MAX_DISTANCE: float = 11.0
const RELIC_TYPES: Array[String] = ["arcane_sigil", "oath_standard"]
const BOUNTY_START_DELAY: float = 66.0
const BOUNTY_COOLDOWN: float = 94.0
const BOUNTY_CHECK_INTERVAL: float = 3.0
const BOUNTY_TRIGGER_CHANCE: float = 0.28
const BOUNTY_MIN_POPULATION: int = 12
const BOUNTY_MAX_ACTIVE: int = 1
const BOUNTY_DURATION: float = 24.0
const BOUNTY_CLEAR_XP: float = 1.6
const BOUNTY_CLEAR_XP_RADIUS: float = 20.0

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
var poi_structure_established_total: int = 0
var poi_structure_lost_total: int = 0
var poi_structure_regen_bonus_ticks_total: int = 0
var raid_started_total: int = 0
var raid_ended_total: int = 0
var raid_success_total: int = 0
var raid_interrupted_total: int = 0
var raid_timeout_total: int = 0
var allegiance_created_total: int = 0
var allegiance_removed_total: int = 0
var allegiance_assignments_total: int = 0
var allegiance_losses_total: int = 0
var level_ups_total: int = 0
var champion_promotions_total: int = 0
var rally_groups_formed_total: int = 0
var rally_groups_dissolved_total: int = 0
var rally_follow_ticks_total: int = 0
var rally_bonus_ticks_total: int = 0
var rally_leaders_active: int = 0
var rally_followers_active: int = 0
var rally_human_leaders_active: int = 0
var rally_monster_leaders_active: int = 0
var rally_human_followers_active: int = 0
var rally_monster_followers_active: int = 0
var rally_bonus_followers_active: int = 0
var world_event_active_id: String = ""
var world_event_remaining: float = 0.0
var world_event_next_in: float = WORLD_EVENT_START_DELAY
var world_event_started_total: int = 0
var world_event_ended_total: int = 0
var world_event_last_id: String = ""
var world_event_modifiers: Dictionary = {}
var special_arrivals_total: int = 0
var special_arrivals_human_total: int = 0
var special_arrivals_monster_total: int = 0
var special_arrivals_fallen_total: int = 0
var relic_appear_total: int = 0
var relic_acquired_total: int = 0
var relic_lost_total: int = 0
var bounty_started_total: int = 0
var bounty_cleared_total: int = 0
var bounty_expired_total: int = 0
var bounty_active: bool = false
var bounty_target_actor_id: int = 0
var bounty_target_faction: String = ""
var bounty_target_label: String = ""
var bounty_source_faction: String = ""
var bounty_source_allegiance_id: String = ""
var bounty_source_poi: String = ""
var bounty_target_position: Vector3 = Vector3.ZERO
var bounty_remaining: float = 0.0

var actor_poi_presence: Dictionary = {}
var poi_runtime_snapshot: Dictionary = {}
var active_raid_snapshot: Dictionary = {}
var _poi_influence_xp_timers: Dictionary = {}
var _champion_scan_timer: float = 0.0
var _prev_rally_leader_counts: Dictionary = {}
var _special_arrival_check_timer: float = 0.0
var _special_arrival_cooldown_left: float = SPECIAL_ARRIVAL_START_DELAY
var _relic_check_timer: float = 0.0
var _relic_cooldown_left: float = RELIC_START_DELAY
var _bounty_check_timer: float = 0.0
var _bounty_cooldown_left: float = BOUNTY_START_DELAY

var event_log: Array[String] = []


func _ready() -> void:
    randomize()
    world_event_modifiers = _default_world_event_modifiers()
    world_manager.setup_world()
    _apply_world_event_to_world_manager()
    world_manager.set_bounty_state(false)
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

    _update_world_events(delta)
    world_manager.tick_world(delta)

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        actor.tick_actor(delta, world_manager, actors, ai, combat_system, magic_system, self)

    _update_rally_runtime()
    magic_system.tick_projectiles(delta, actors, self)
    _update_poi_runtime()
    _update_actor_allegiances()
    _update_bounty_system(delta)
    _update_special_arrivals(delta)
    _update_relic_system(delta)
    _apply_poi_influences(delta)
    _scan_for_champion_promotion(delta)
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

    if to_state in ["attack", "cast", "cast_nova", "cast_control", "flee", "poi", "reposition", "rally", "raid", "hunt"]:
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
            killer.register_kill()
            killer.award_progress_xp(XP_ON_KILL, "kill", self)
            _try_promote_champion(killer, "kill")
        record_event(
            "Death: %s by %s (%s)."
            % [_actor_label(victim), _actor_label(killer), reason]
        )
    else:
        record_event("Death: %s (%s)." % [_actor_label(victim), reason])

    if victim.is_champion:
        record_event("Champion fallen: %s." % _actor_label(victim))
    if victim.is_special_arrival():
        special_arrivals_fallen_total += 1
        record_event("Special Arrival FALLEN: %s." % _actor_label(victim))
    if victim.has_relic():
        var lost_title := victim.relic_title if victim.relic_title != "" else _relic_title(victim.relic_id)
        record_event("Relic LOST: %s from %s." % [lost_title, _actor_label(victim)])
        relic_lost_total += 1
        _relic_cooldown_left = max(_relic_cooldown_left, RELIC_COOLDOWN * 0.34)
        victim.clear_relic()
    _handle_bounty_target_death(victim, killer)


func register_level_up(actor: Actor, old_level: int, new_level: int, reason: String) -> void:
    if actor == null:
        return
    level_ups_total += 1
    record_event(
        "Level up: %s L%d -> L%d (%s)."
        % [_actor_label(actor), old_level, new_level, reason]
    )
    _try_promote_champion(actor, "level_up:%s" % reason)


func record_event(message: String) -> void:
    event_log.append("[%05d] %s" % [tick_index, message])
    while event_log.size() > MAX_EVENT_LOG:
        event_log.remove_at(0)


func get_magic_modifiers(_caster: Actor) -> Dictionary:
    var damage_mult: float = float(world_event_modifiers.get("magic_damage_mult", 1.0))
    var energy_cost_mult: float = float(world_event_modifiers.get("magic_energy_cost_mult", 1.0))
    if _caster != null and _caster.has_relic():
        if _caster.relic_id == "arcane_sigil":
            damage_mult *= 1.10
            energy_cost_mult *= 0.90
    return {
        "damage_mult": damage_mult,
        "energy_cost_mult": energy_cost_mult
    }


func get_melee_damage_multiplier(attacker: Actor) -> float:
    var multiplier: float = 1.0
    if attacker == null or attacker.faction != "monster":
        if attacker != null and attacker.has_relic() and attacker.relic_id == "oath_standard":
            multiplier *= 1.08
        return multiplier
    multiplier *= float(world_event_modifiers.get("monster_melee_damage_mult", 1.0))
    if attacker.has_relic() and attacker.relic_id == "oath_standard":
        multiplier *= 1.08
    return multiplier


func get_speed_multiplier(actor: Actor) -> float:
    if actor == null or actor.faction != "monster":
        return 1.0
    return float(world_event_modifiers.get("monster_speed_mult", 1.0))


func get_energy_regen_bonus_per_sec(actor: Actor) -> float:
    if actor == null:
        return 0.0
    var bonus_per_sec: float = 0.0
    if actor.faction == "human":
        bonus_per_sec += float(world_event_modifiers.get("human_energy_regen_per_sec", 0.0))
    if actor.has_relic() and actor.relic_id == "oath_standard":
        bonus_per_sec += 0.22
    return bonus_per_sec


func _update_world_events(delta: float) -> void:
    if world_event_active_id == "":
        world_event_next_in = max(0.0, world_event_next_in - delta)
        if world_event_next_in <= 0.0:
            _start_world_event(_pick_next_world_event_id())
        return

    world_event_remaining = max(0.0, world_event_remaining - delta)
    if world_event_remaining <= 0.0:
        _end_world_event()


func _start_world_event(event_id: String) -> void:
    if event_id == "":
        return

    world_event_active_id = event_id
    world_event_last_id = event_id
    world_event_remaining = _world_event_duration(event_id)
    world_event_started_total += 1
    world_event_modifiers = _modifiers_for_world_event(event_id)
    _apply_world_event_to_world_manager()
    record_event(
        "World Event START: %s (%.0fs)."
        % [_world_event_label(event_id), world_event_remaining]
    )


func _end_world_event() -> void:
    if world_event_active_id == "":
        return

    var finished_id := world_event_active_id
    world_event_active_id = ""
    world_event_remaining = 0.0
    world_event_next_in = randf_range(WORLD_EVENT_COOLDOWN_MIN, WORLD_EVENT_COOLDOWN_MAX)
    world_event_modifiers = _default_world_event_modifiers()
    world_event_ended_total += 1
    _apply_world_event_to_world_manager()
    record_event(
        "World Event END: %s (next in ~%.0fs)."
        % [_world_event_label(finished_id), world_event_next_in]
    )


func _pick_next_world_event_id() -> String:
    var choices: Array = WORLD_EVENT_TYPES.duplicate()
    if choices.size() > 1 and world_event_last_id != "":
        choices.erase(world_event_last_id)
    if choices.is_empty():
        choices = WORLD_EVENT_TYPES.duplicate()
    if choices.is_empty():
        return ""
    return choices[randi() % choices.size()]


func _world_event_duration(event_id: String) -> float:
    match event_id:
        "mana_surge":
            return 18.0
        "monster_frenzy":
            return 16.0
        "sanctuary_calm":
            return 20.0
        _:
            return 15.0


func _default_world_event_modifiers() -> Dictionary:
    return {
        "magic_damage_mult": 1.0,
        "magic_energy_cost_mult": 1.0,
        "monster_melee_damage_mult": 1.0,
        "monster_speed_mult": 1.0,
        "human_energy_regen_per_sec": 0.0,
        "raid_pressure_global_mult": 1.0,
        "raid_pressure_human_mult": 1.0,
        "raid_pressure_monster_mult": 1.0
    }


func _modifiers_for_world_event(event_id: String) -> Dictionary:
    var modifiers: Dictionary = _default_world_event_modifiers()
    match event_id:
        "mana_surge":
            modifiers["magic_damage_mult"] = 1.18
            modifiers["magic_energy_cost_mult"] = 0.86
            modifiers["raid_pressure_global_mult"] = 1.03
        "monster_frenzy":
            modifiers["monster_melee_damage_mult"] = 1.14
            modifiers["monster_speed_mult"] = 1.08
            modifiers["raid_pressure_monster_mult"] = 1.16
        "sanctuary_calm":
            modifiers["human_energy_regen_per_sec"] = 0.55
            modifiers["raid_pressure_global_mult"] = 0.90
            modifiers["raid_pressure_monster_mult"] = 0.78
    return modifiers


func _apply_world_event_to_world_manager() -> void:
    world_manager.set_raid_pressure_modifiers(
        float(world_event_modifiers.get("raid_pressure_global_mult", 1.0)),
        float(world_event_modifiers.get("raid_pressure_human_mult", 1.0)),
        float(world_event_modifiers.get("raid_pressure_monster_mult", 1.0))
    )
    world_manager.set_world_event_visual(world_event_active_id)


func _world_event_label(event_id: String) -> String:
    match event_id:
        "mana_surge":
            return "Mana Surge"
        "monster_frenzy":
            return "Monster Frenzy"
        "sanctuary_calm":
            return "Sanctuary Calm"
        _:
            return "None"


func _update_special_arrivals(delta: float) -> void:
    _special_arrival_cooldown_left = max(0.0, _special_arrival_cooldown_left - delta)
    _special_arrival_check_timer += delta
    if _special_arrival_check_timer < SPECIAL_ARRIVAL_CHECK_INTERVAL:
        return
    _special_arrival_check_timer = 0.0

    if world_event_active_id == "":
        return
    if _special_arrival_cooldown_left > 0.0:
        return
    if _count_alive_actors() < SPECIAL_ARRIVAL_MIN_POPULATION:
        return
    if _count_alive_special_arrivals("") >= SPECIAL_ARRIVAL_MAX_ACTIVE:
        return

    var candidates: Array[Dictionary] = _collect_special_arrival_candidates()
    if candidates.is_empty():
        return
    if randf() > SPECIAL_ARRIVAL_TRIGGER_CHANCE:
        return

    var picked: Dictionary = candidates[randi() % candidates.size()]
    _spawn_special_arrival(picked)
    _special_arrival_cooldown_left = SPECIAL_ARRIVAL_COOLDOWN


func _collect_special_arrival_candidates() -> Array[Dictionary]:
    var candidates: Array[Dictionary] = []

    if world_event_active_id == "sanctuary_calm":
        if _count_alive_special_arrivals("human") < SPECIAL_ARRIVAL_MAX_ACTIVE_PER_FACTION:
            var human_anchor: Dictionary = _find_special_arrival_anchor("human_outpost")
            if not human_anchor.is_empty():
                human_anchor["variant_id"] = "summoned_hero"
                human_anchor["faction"] = "human"
                human_anchor["title"] = "Summoned Hero"
                candidates.append(human_anchor)

    if world_event_active_id == "monster_frenzy":
        if _count_alive_special_arrivals("monster") < SPECIAL_ARRIVAL_MAX_ACTIVE_PER_FACTION:
            var monster_anchor: Dictionary = _find_special_arrival_anchor("monster_lair")
            if not monster_anchor.is_empty():
                monster_anchor["variant_id"] = "calamity_invader"
                monster_anchor["faction"] = "monster"
                monster_anchor["title"] = "Calamity Invader"
                candidates.append(monster_anchor)

    return candidates


func _find_special_arrival_anchor(structure_state: String) -> Dictionary:
    var selected: Dictionary = {}
    var best_dominance_seconds: float = -1.0

    for poi_name_variant in poi_runtime_snapshot.keys():
        var poi_name: String = str(poi_name_variant)
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if not bool(details.get("structure_active", false)):
            continue
        if str(details.get("structure_state", "")) != structure_state:
            continue

        var dominance_seconds: float = float(details.get("dominance_seconds", 0.0))
        if dominance_seconds < SPECIAL_ARRIVAL_MIN_DOMINANCE_SECONDS:
            continue
        if dominance_seconds <= best_dominance_seconds:
            continue

        selected = {
            "poi_name": poi_name,
            "position": _get_poi_position_by_name(poi_name),
            "dominance_seconds": dominance_seconds,
            "allegiance_id": str(details.get("allegiance_id", ""))
        }
        best_dominance_seconds = dominance_seconds

    return selected


func _get_poi_position_by_name(poi_name: String) -> Vector3:
    for poi in world_manager.pois:
        if str(poi.get("name", "")) != poi_name:
            continue
        return poi.get("position", Vector3.ZERO)
    return Vector3.ZERO


func _spawn_special_arrival(candidate: Dictionary) -> void:
    var variant_id: String = str(candidate.get("variant_id", ""))
    var faction: String = str(candidate.get("faction", ""))
    var title: String = str(candidate.get("title", "Special Arrival"))
    var poi_name: String = str(candidate.get("poi_name", ""))
    var anchor_position: Vector3 = candidate.get("position", Vector3.ZERO)
    var allegiance_id: String = str(candidate.get("allegiance_id", ""))

    var actor: Actor = _make_special_arrival_actor(variant_id)
    if actor == null:
        return

    actor.global_position = _special_arrival_spawn_position(anchor_position, faction)
    actor.set_special_arrival(variant_id, title)
    actor.promote_to_champion("special_arrival:%s" % variant_id)
    actor.apply_special_arrival_bonus(variant_id)
    if allegiance_id != "":
        actor.set_allegiance(allegiance_id, poi_name)

    entities_root.add_child(actor)
    actors.append(actor)
    register_spawn(actor)

    special_arrivals_total += 1
    if faction == "human":
        special_arrivals_human_total += 1
    elif faction == "monster":
        special_arrivals_monster_total += 1

    var poi_label := poi_name if poi_name != "" else "wilds"
    record_event(
        "Special Arrival START: %s at %s (%s)."
        % [title, poi_label, _world_event_label(world_event_active_id)]
    )


func _make_special_arrival_actor(variant_id: String) -> Actor:
    if variant_id == "summoned_hero":
        var hero := HumanAgent.new()
        hero.assign_role(_pick_special_human_role())
        hero.level = hero.max_level
        hero.progress_xp = 38.0
        hero.kill_count = CHAMPION_MIN_KILLS
        hero.age_seconds = CHAMPION_MIN_AGE_SECONDS
        return hero
    if variant_id == "calamity_invader":
        var invader := BruteMonster.new()
        invader.level = invader.max_level
        invader.progress_xp = 38.0
        invader.kill_count = CHAMPION_MIN_KILLS
        invader.age_seconds = CHAMPION_MIN_AGE_SECONDS
        return invader
    return null


func _pick_special_human_role() -> String:
    var roll := randf()
    if roll < 0.46:
        return "fighter"
    if roll < 0.84:
        return "mage"
    return "scout"


func _special_arrival_spawn_position(anchor_position: Vector3, faction: String) -> Vector3:
    var base_position: Vector3 = anchor_position
    if base_position == Vector3.ZERO:
        base_position = world_manager.get_spawn_point(faction)
    var jitter := Vector3(randf_range(-2.2, 2.2), 0.0, randf_range(-2.2, 2.2))
    return world_manager.clamp_to_world(world_manager.snap_to_nav_grid(base_position + jitter))


func _update_relic_system(delta: float) -> void:
    _relic_cooldown_left = max(0.0, _relic_cooldown_left - delta)
    _relic_check_timer += delta
    if _relic_check_timer < RELIC_CHECK_INTERVAL:
        return
    _relic_check_timer = 0.0

    if world_event_active_id == "":
        return
    if _relic_cooldown_left > 0.0:
        return
    if _count_alive_actors() < RELIC_MIN_POPULATION:
        return
    if _count_alive_relic_carriers("") >= RELIC_MAX_ACTIVE:
        return

    var candidates: Array[Dictionary] = _collect_relic_candidates()
    if candidates.is_empty():
        return
    if randf() > RELIC_TRIGGER_CHANCE:
        return

    var selected: Dictionary = candidates[randi() % candidates.size()]
    _award_relic_to_holder(selected)
    _relic_cooldown_left = RELIC_COOLDOWN


func _collect_relic_candidates() -> Array[Dictionary]:
    var candidates: Array[Dictionary] = []

    for relic_id in RELIC_TYPES:
        var next_relic_id: String = str(relic_id)
        if _is_relic_active(next_relic_id):
            continue

        if next_relic_id == "arcane_sigil":
            var arcane_candidate: Dictionary = _build_relic_candidate_for(
                next_relic_id,
                "mana_surge",
                "human_outpost",
                "human",
                true,
                true
            )
            if not arcane_candidate.is_empty():
                candidates.append(arcane_candidate)
        elif next_relic_id == "oath_standard":
            var oath_candidate: Dictionary = _build_relic_candidate_for(
                next_relic_id,
                "monster_frenzy",
                "monster_lair",
                "monster",
                true,
                false
            )
            if not oath_candidate.is_empty():
                candidates.append(oath_candidate)

    return candidates


func _build_relic_candidate_for(
    relic_id: String,
    required_world_event_id: String,
    required_structure_state: String,
    faction: String,
    prefer_special_arrival: bool,
    require_magic: bool
) -> Dictionary:
    if world_event_active_id != required_world_event_id:
        return {}

    var anchor: Dictionary = _find_relic_anchor(required_structure_state)
    if anchor.is_empty():
        return {}

    var holder: Actor = _pick_relic_holder(
        faction,
        anchor.get("position", Vector3.ZERO),
        prefer_special_arrival,
        require_magic
    )
    if holder == null:
        return {}

    return {
        "relic_id": relic_id,
        "relic_title": _relic_title(relic_id),
        "faction": faction,
        "poi_name": str(anchor.get("poi_name", "")),
        "anchor_position": anchor.get("position", Vector3.ZERO),
        "holder": holder
    }


func _find_relic_anchor(structure_state: String) -> Dictionary:
    var selected: Dictionary = {}
    var best_dominance_seconds: float = -1.0

    for poi_name_variant in poi_runtime_snapshot.keys():
        var poi_name: String = str(poi_name_variant)
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if not bool(details.get("structure_active", false)):
            continue
        if str(details.get("structure_state", "")) != structure_state:
            continue
        var dominance_seconds: float = float(details.get("dominance_seconds", 0.0))
        if dominance_seconds < RELIC_MIN_DOMINANCE_SECONDS:
            continue
        if dominance_seconds <= best_dominance_seconds:
            continue
        selected = {
            "poi_name": poi_name,
            "position": _get_poi_position_by_name(poi_name),
            "dominance_seconds": dominance_seconds
        }
        best_dominance_seconds = dominance_seconds

    return selected


func _pick_relic_holder(
    faction: String,
    anchor_position: Vector3,
    prefer_special_arrival: bool,
    require_magic: bool
) -> Actor:
    var fallback: Actor = null
    var best_distance: float = RELIC_HOLDER_MAX_DISTANCE

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction != faction:
            continue
        if not actor.can_receive_relic():
            continue
        if require_magic and not actor.magic_enabled:
            continue

        var distance: float = actor.global_position.distance_to(anchor_position)
        if distance > RELIC_HOLDER_MAX_DISTANCE:
            continue

        var eligible_leader: bool = actor.is_champion or actor.is_special_arrival()
        if not eligible_leader:
            continue

        if prefer_special_arrival and actor.is_special_arrival():
            if fallback == null or distance < best_distance:
                fallback = actor
                best_distance = distance
            continue

        if fallback == null or distance < best_distance:
            fallback = actor
            best_distance = distance

    return fallback


func _award_relic_to_holder(candidate: Dictionary) -> void:
    var relic_id: String = str(candidate.get("relic_id", ""))
    var relic_title: String = str(candidate.get("relic_title", _relic_title(relic_id)))
    var poi_name: String = str(candidate.get("poi_name", "wilds"))
    var holder: Actor = candidate.get("holder", null)
    if holder == null or holder.is_dead:
        return
    if not holder.can_receive_relic():
        return

    relic_appear_total += 1
    record_event(
        "Relic APPEAR: %s near %s (%s)."
        % [relic_title, poi_name, _world_event_label(world_event_active_id)]
    )

    holder.set_relic(relic_id, relic_title)
    relic_acquired_total += 1
    record_event("Relic ACQUIRED: %s by %s." % [relic_title, _actor_label(holder)])


func _is_relic_active(relic_id: String) -> bool:
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.relic_id == relic_id:
            return true
    return false


func _count_alive_relic_carriers(faction_filter: String) -> int:
    var total := 0
    for actor in actors:
        if actor == null or actor.is_dead or not actor.has_relic():
            continue
        if faction_filter != "" and actor.faction != faction_filter:
            continue
        total += 1
    return total


func _relic_title(relic_id: String) -> String:
    match relic_id:
        "arcane_sigil":
            return "Arcane Sigil"
        "oath_standard":
            return "Oath Standard"
        _:
            return "Relic"


func _update_bounty_system(delta: float) -> void:
    _bounty_cooldown_left = max(0.0, _bounty_cooldown_left - delta)
    _bounty_check_timer += delta

    if bounty_active:
        bounty_remaining = max(0.0, bounty_remaining - delta)
        var target: Actor = _find_actor_by_id(bounty_target_actor_id)
        if target == null or target.is_dead:
            _expire_bounty("target_lost")
            return

        bounty_target_position = target.global_position
        bounty_target_label = _actor_label(target)
        _push_bounty_state_to_world()
        if bounty_remaining <= 0.0:
            _expire_bounty("timeout")
        return

    if _bounty_check_timer < BOUNTY_CHECK_INTERVAL:
        return
    _bounty_check_timer = 0.0
    if _bounty_cooldown_left > 0.0:
        return
    if _count_alive_actors() < BOUNTY_MIN_POPULATION:
        return
    if _count_active_bounties() >= BOUNTY_MAX_ACTIVE:
        return
    if randf() > BOUNTY_TRIGGER_CHANCE:
        return

    var source: Dictionary = _pick_bounty_source()
    if source.is_empty():
        return
    var source_faction: String = str(source.get("faction", ""))
    if source_faction == "":
        return
    var source_position: Vector3 = source.get("position", Vector3.ZERO)
    var target: Actor = _pick_bounty_target(source_faction, source_position)
    if target == null:
        return

    _start_bounty(source, target)


func _count_active_bounties() -> int:
    return 1 if bounty_active else 0


func _pick_bounty_source() -> Dictionary:
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances()
    if active_allegiances.is_empty():
        return {}

    var raid_state: Dictionary = world_manager.get_active_raid_state()
    var raid_attacker: String = str(raid_state.get("attacker_faction", ""))
    var raid_sources: Array[Dictionary] = []
    for allegiance in active_allegiances:
        if raid_attacker != "" and str(allegiance.get("faction", "")) == raid_attacker:
            raid_sources.append(allegiance)

    var pool: Array[Dictionary] = raid_sources if not raid_sources.is_empty() else active_allegiances
    return pool[randi() % pool.size()]


func _pick_bounty_target(source_faction: String, source_position: Vector3) -> Actor:
    var selected: Actor = null
    var best_priority: int = 0
    var best_distance: float = INF

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction == source_faction:
            continue

        var priority: int = _bounty_priority(actor)
        if priority <= 0:
            continue

        var distance: float = actor.global_position.distance_to(source_position)
        if priority > best_priority or (priority == best_priority and distance < best_distance):
            selected = actor
            best_priority = priority
            best_distance = distance

    return selected


func _bounty_priority(actor: Actor) -> int:
    if actor == null or actor.is_dead:
        return 0
    if actor.has_relic():
        return 3
    if actor.is_special_arrival():
        return 2
    if actor.is_champion:
        return 1
    return 0


func _start_bounty(source: Dictionary, target: Actor) -> void:
    if target == null or target.is_dead:
        return

    bounty_active = true
    bounty_target_actor_id = target.actor_id
    bounty_target_faction = target.faction
    bounty_source_faction = str(source.get("faction", ""))
    bounty_source_allegiance_id = str(source.get("allegiance_id", ""))
    bounty_source_poi = str(source.get("home_poi", ""))
    bounty_target_position = target.global_position
    bounty_remaining = BOUNTY_DURATION
    bounty_started_total += 1
    _bounty_cooldown_left = BOUNTY_COOLDOWN

    target.set_bounty_marked(true)
    bounty_target_label = _actor_label(target)
    _push_bounty_state_to_world()

    record_event(
        "Bounty START: %s marked by %s (%s, %.0fs)."
        % [
            bounty_target_label,
            _bounty_source_label(),
            _bounty_target_kind_label(target),
            bounty_remaining
        ]
    )


func _expire_bounty(reason: String) -> void:
    if not bounty_active:
        return
    var target: Actor = _find_actor_by_id(bounty_target_actor_id)
    if target != null:
        target.set_bounty_marked(false)

    bounty_expired_total += 1
    record_event(
        "Bounty EXPIRED: %s (%s)."
        % [bounty_target_label if bounty_target_label != "" else "unknown", reason]
    )
    _clear_bounty_state()


func _handle_bounty_target_death(victim: Actor, killer: Actor) -> void:
    if victim == null or not bounty_active:
        return
    if victim.actor_id != bounty_target_actor_id:
        return

    victim.set_bounty_marked(false)
    var rewarded_allies: int = _grant_bounty_clear_reward()
    bounty_cleared_total += 1
    var killer_label := _actor_label(killer) if killer != null else "unknown"
    record_event(
        "Bounty CLEARED: %s by %s for %s (+%.1f XP to %d allies)."
        % [
            bounty_target_label if bounty_target_label != "" else _actor_label(victim),
            killer_label,
            _bounty_source_label(),
            BOUNTY_CLEAR_XP,
            rewarded_allies
        ]
    )
    _clear_bounty_state()


func _grant_bounty_clear_reward() -> int:
    var center: Vector3 = _get_poi_position_by_name(bounty_source_poi)
    if center == Vector3.ZERO:
        center = bounty_target_position

    var rewarded: int = 0
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction != bounty_source_faction:
            continue
        if center != Vector3.ZERO and actor.global_position.distance_to(center) > BOUNTY_CLEAR_XP_RADIUS:
            continue
        actor.award_progress_xp(BOUNTY_CLEAR_XP, "bounty_clear", self)
        rewarded += 1
    return rewarded


func _clear_bounty_state() -> void:
    bounty_active = false
    bounty_target_actor_id = 0
    bounty_target_faction = ""
    bounty_target_label = ""
    bounty_source_faction = ""
    bounty_source_allegiance_id = ""
    bounty_source_poi = ""
    bounty_target_position = Vector3.ZERO
    bounty_remaining = 0.0
    _push_bounty_state_to_world()


func _push_bounty_state_to_world() -> void:
    world_manager.set_bounty_state(
        bounty_active,
        bounty_source_faction,
        bounty_source_allegiance_id,
        bounty_source_poi,
        bounty_target_position,
        bounty_target_actor_id,
        bounty_target_label,
        bounty_target_faction
    )


func _find_actor_by_id(actor_id: int) -> Actor:
    if actor_id == 0:
        return null
    for actor in actors:
        if actor == null:
            continue
        if actor.actor_id == actor_id:
            return actor
    return null


func _bounty_target_kind_label(actor: Actor) -> String:
    if actor == null:
        return "notable"
    if actor.has_relic():
        return "relic_carrier"
    if actor.is_special_arrival():
        return "special_arrival"
    if actor.is_champion:
        return "champion"
    return "notable"


func _bounty_source_label() -> String:
    if bounty_source_allegiance_id != "":
        return bounty_source_allegiance_id
    if bounty_source_poi != "":
        return bounty_source_poi
    if bounty_source_faction != "":
        return bounty_source_faction
    return "unknown"


func _cleanup_dead_actors() -> void:
    for idx in range(actors.size() - 1, -1, -1):
        var actor: Actor = actors[idx]
        if actor == null:
            actors.remove_at(idx)
            continue

        if actor.is_dead:
            actor_poi_presence.erase(actor.actor_id)
            _clear_actor_influence_timers(actor.actor_id)
            _clear_actor_rally_tracking(actor.actor_id)
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
    var champion_alive_total: int = 0
    var human_champions_alive: int = 0
    var monster_champions_alive: int = 0
    var champion_kills_total: int = 0
    var special_arrivals_active_total: int = 0
    var special_arrivals_active_humans: int = 0
    var special_arrivals_active_monsters: int = 0
    var relic_active_total: int = 0
    var relic_active_humans: int = 0
    var relic_active_monsters: int = 0
    var relic_active_labels: Array[String] = []
    var bounty_marked_total: int = 0
    var bounty_marked_humans: int = 0
    var bounty_marked_monsters: int = 0
    var allegiance_affiliated_total: int = 0
    var allegiance_affiliated_humans: int = 0
    var allegiance_affiliated_monsters: int = 0
    var allegiance_member_counts: Dictionary = {}
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
        "raid": 0,
        "hunt": 0,
        "rally": 0,
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
        if actor.is_champion:
            champion_alive_total += 1
            champion_kills_total += actor.kill_count
        if actor.is_special_arrival():
            special_arrivals_active_total += 1
            if actor.faction == "human":
                special_arrivals_active_humans += 1
            elif actor.faction == "monster":
                special_arrivals_active_monsters += 1
        if actor.has_relic():
            relic_active_total += 1
            if actor.faction == "human":
                relic_active_humans += 1
            elif actor.faction == "monster":
                relic_active_monsters += 1
            var relic_name := actor.relic_title if actor.relic_title != "" else _relic_title(actor.relic_id)
            relic_active_labels.append("%s->%s" % [relic_name, _actor_label(actor)])
        if actor.bounty_marked:
            bounty_marked_total += 1
            if actor.faction == "human":
                bounty_marked_humans += 1
            elif actor.faction == "monster":
                bounty_marked_monsters += 1
        if actor.allegiance_id != "":
            allegiance_affiliated_total += 1
            allegiance_member_counts[actor.allegiance_id] = int(allegiance_member_counts.get(actor.allegiance_id, 0)) + 1

        var level_key := "L%d" % clampi(actor.level, 1, 3)
        level_counts[level_key] += 1

        if actor.faction == "human":
            humans_alive += 1
            if actor.allegiance_id != "":
                allegiance_affiliated_humans += 1
            if actor.is_champion:
                human_champions_alive += 1
            human_level_counts[level_key] += 1
            if human_role_counts.has(actor.human_role):
                human_role_counts[actor.human_role] += 1
            if actor.is_slowed():
                slowed_humans += 1
        elif actor.faction == "monster":
            monsters_alive += 1
            if actor.allegiance_id != "":
                allegiance_affiliated_monsters += 1
            if actor.is_champion:
                monster_champions_alive += 1
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
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances()
    var allegiance_structure_labels: Array[String] = []
    for allegiance in active_allegiances:
        allegiance_structure_labels.append(
            "%s[%s,%s]"
            % [
                str(allegiance.get("allegiance_id", "")),
                str(allegiance.get("home_poi", "")),
                str(allegiance.get("structure_state", ""))
            ]
        )
    allegiance_structure_labels.sort()
    var poi_influence_active_count: int = 0
    var poi_structure_active_count: int = 0
    for poi_name in poi_runtime_snapshot.keys():
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if bool(details.get("influence_active", false)):
            poi_influence_active_count += 1
        if bool(details.get("structure_active", false)):
            poi_structure_active_count += 1
    relic_active_labels.sort()

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
        "champion_alive_total": champion_alive_total,
        "human_champions_alive": human_champions_alive,
        "monster_champions_alive": monster_champions_alive,
        "champion_kills_total": champion_kills_total,
        "special_arrivals_active_total": special_arrivals_active_total,
        "special_arrivals_active_humans": special_arrivals_active_humans,
        "special_arrivals_active_monsters": special_arrivals_active_monsters,
        "special_arrivals_total": special_arrivals_total,
        "special_arrivals_human_total": special_arrivals_human_total,
        "special_arrivals_monster_total": special_arrivals_monster_total,
        "special_arrivals_fallen_total": special_arrivals_fallen_total,
        "relic_active_total": relic_active_total,
        "relic_active_humans": relic_active_humans,
        "relic_active_monsters": relic_active_monsters,
        "relic_active_labels": relic_active_labels,
        "relic_appear_total": relic_appear_total,
        "relic_acquired_total": relic_acquired_total,
        "relic_lost_total": relic_lost_total,
        "bounty_active": bounty_active,
        "bounty_remaining": bounty_remaining,
        "bounty_target_label": bounty_target_label,
        "bounty_source_faction": bounty_source_faction,
        "bounty_source_poi": bounty_source_poi,
        "bounty_marked_total": bounty_marked_total,
        "bounty_marked_humans": bounty_marked_humans,
        "bounty_marked_monsters": bounty_marked_monsters,
        "bounty_started_total": bounty_started_total,
        "bounty_cleared_total": bounty_cleared_total,
        "bounty_expired_total": bounty_expired_total,
        "allegiance_active_count": active_allegiances.size(),
        "allegiance_affiliated_total": allegiance_affiliated_total,
        "allegiance_affiliated_humans": allegiance_affiliated_humans,
        "allegiance_affiliated_monsters": allegiance_affiliated_monsters,
        "allegiance_unaffiliated_total": max(0, alive_total - allegiance_affiliated_total),
        "allegiance_member_counts": allegiance_member_counts,
        "allegiance_structure_labels": allegiance_structure_labels,
        "rally_leaders_active": rally_leaders_active,
        "rally_followers_active": rally_followers_active,
        "rally_human_leaders_active": rally_human_leaders_active,
        "rally_monster_leaders_active": rally_monster_leaders_active,
        "rally_human_followers_active": rally_human_followers_active,
        "rally_monster_followers_active": rally_monster_followers_active,
        "rally_bonus_followers_active": rally_bonus_followers_active,
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
        "poi_structure_active_count": poi_structure_active_count,
        "poi_structure_established_total": poi_structure_established_total,
        "poi_structure_lost_total": poi_structure_lost_total,
        "poi_structure_regen_bonus_ticks_total": poi_structure_regen_bonus_ticks_total,
        "raid_active": bool(active_raid_snapshot.get("active", false)),
        "raid_attacker_faction": str(active_raid_snapshot.get("attacker_faction", "")),
        "raid_source_poi": str(active_raid_snapshot.get("source_poi", "")),
        "raid_target_poi": str(active_raid_snapshot.get("target_poi", "")),
        "raid_started_total": raid_started_total,
        "raid_ended_total": raid_ended_total,
        "raid_success_total": raid_success_total,
        "raid_interrupted_total": raid_interrupted_total,
        "raid_timeout_total": raid_timeout_total,
        "world_event_active_id": world_event_active_id,
        "world_event_active_name": _world_event_label(world_event_active_id),
        "world_event_remaining": world_event_remaining,
        "world_event_next_in": world_event_next_in,
        "world_event_started_total": world_event_started_total,
        "world_event_ended_total": world_event_ended_total,
        "allegiance_created_total": allegiance_created_total,
        "allegiance_removed_total": allegiance_removed_total,
        "allegiance_assignments_total": allegiance_assignments_total,
        "allegiance_losses_total": allegiance_losses_total,
        "level_ups_total": level_ups_total,
        "champion_promotions_total": champion_promotions_total,
        "rally_groups_formed_total": rally_groups_formed_total,
        "rally_groups_dissolved_total": rally_groups_dissolved_total,
        "rally_follow_ticks_total": rally_follow_ticks_total,
        "rally_bonus_ticks_total": rally_bonus_ticks_total,
        "poi_population": poi_population,
        "poi_snapshot": poi_runtime_snapshot,
        "state_counts": state_counts
    }


func _update_rally_runtime() -> void:
    var alive_by_id: Dictionary = {}
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        alive_by_id[actor.actor_id] = actor

    var followers_by_leader: Dictionary = {}
    var followers_total: int = 0
    var human_followers: int = 0
    var monster_followers: int = 0
    var bonus_followers: int = 0

    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        var leader_id: int = actor.rally_leader_id
        if leader_id == actor.actor_id:
            leader_id = 0

        if leader_id != 0:
            var leader: Actor = alive_by_id.get(leader_id, null)
            if leader == null or leader.is_dead or not leader.is_champion or leader.faction != actor.faction:
                leader_id = 0

        actor.rally_leader_id = leader_id
        if leader_id == 0:
            actor.rally_bonus_active = false
            actor.rally_relic_bonus_active = false
            continue

        var leader_for_bonus: Actor = alive_by_id.get(leader_id, null)
        actor.rally_relic_bonus_active = (
            leader_for_bonus != null
            and not leader_for_bonus.is_dead
            and leader_for_bonus.has_relic()
            and leader_for_bonus.relic_id == "oath_standard"
        )

        followers_total += 1
        if actor.faction == "human":
            human_followers += 1
        elif actor.faction == "monster":
            monster_followers += 1

        if actor.rally_bonus_active:
            bonus_followers += 1
            rally_bonus_ticks_total += 1
        rally_follow_ticks_total += 1

        followers_by_leader[leader_id] = int(followers_by_leader.get(leader_id, 0)) + 1

    var leaders_total: int = 0
    var human_leaders: int = 0
    var monster_leaders: int = 0
    for leader_id_variant in followers_by_leader.keys():
        var leader_id: int = int(leader_id_variant)
        var leader: Actor = alive_by_id.get(leader_id, null)
        if leader == null:
            continue

        leaders_total += 1
        if leader.faction == "human":
            human_leaders += 1
        elif leader.faction == "monster":
            monster_leaders += 1

        var current_followers: int = int(followers_by_leader.get(leader_id, 0))
        var previous_followers: int = int(_prev_rally_leader_counts.get(leader_id, 0))
        if previous_followers <= 0 and current_followers > 0:
            rally_groups_formed_total += 1
            record_event("Rally formed: %s (+%d allies)." % [_actor_label(leader), current_followers])

    for leader_id_variant in _prev_rally_leader_counts.keys():
        var leader_id: int = int(leader_id_variant)
        if followers_by_leader.has(leader_id):
            continue
        var previous_followers: int = int(_prev_rally_leader_counts.get(leader_id, 0))
        if previous_followers <= 0:
            continue
        rally_groups_dissolved_total += 1
        var label := "champion#%d" % leader_id
        var leader: Actor = alive_by_id.get(leader_id, null)
        if leader != null:
            label = _actor_label(leader)
        record_event("Rally dissolved: %s (-%d allies)." % [label, previous_followers])

    rally_leaders_active = leaders_total
    rally_followers_active = followers_total
    rally_human_leaders_active = human_leaders
    rally_monster_leaders_active = monster_leaders
    rally_human_followers_active = human_followers
    rally_monster_followers_active = monster_followers
    rally_bonus_followers_active = bonus_followers
    _prev_rally_leader_counts = followers_by_leader


func _update_poi_runtime() -> void:
    var runtime_data: Dictionary = world_manager.update_poi_runtime(actors, elapsed_time)
    poi_runtime_snapshot = runtime_data.get("snapshot", {})
    active_raid_snapshot = runtime_data.get("raid", {})

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
        elif kind == "structure_established":
            poi_structure_established_total += 1
            var structure_state: String = str(transition.get("structure_state", "structure"))
            var structure_faction: String = str(transition.get("faction", ""))
            record_event("POI structure UP: %s -> %s (%s)." % [poi_name, structure_state, structure_faction])
        elif kind == "structure_lost":
            poi_structure_lost_total += 1
            var structure_state: String = str(transition.get("structure_state", "structure"))
            record_event("POI structure DOWN: %s lost %s." % [poi_name, structure_state])
        elif kind == "allegiance_created":
            allegiance_created_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var allegiance_faction: String = str(transition.get("faction", ""))
            record_event("Allegiance UP: %s at %s (%s)." % [allegiance_id, poi_name, allegiance_faction])
        elif kind == "allegiance_removed":
            allegiance_removed_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var allegiance_faction: String = str(transition.get("faction", ""))
            record_event("Allegiance DOWN: %s at %s (%s)." % [allegiance_id, poi_name, allegiance_faction])
        elif kind == "raid_started":
            raid_started_total += 1
            var attacker_faction: String = str(transition.get("attacker_faction", ""))
            var source_poi: String = str(transition.get("source_poi", ""))
            var target_poi: String = str(transition.get("target_poi", ""))
            record_event("Raid START: %s from %s -> %s." % [attacker_faction, source_poi, target_poi])
        elif kind == "raid_ended":
            raid_ended_total += 1
            var outcome: String = str(transition.get("outcome", "ended"))
            var attacker_faction: String = str(transition.get("attacker_faction", ""))
            var source_poi: String = str(transition.get("source_poi", ""))
            var target_poi: String = str(transition.get("target_poi", ""))
            if outcome == "success":
                raid_success_total += 1
            elif outcome == "interrupted":
                raid_interrupted_total += 1
            elif outcome == "timeout":
                raid_timeout_total += 1
            record_event("Raid END: %s (%s %s -> %s)." % [outcome, attacker_faction, source_poi, target_poi])

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

            var regen_per_sec: float = POI_INFLUENCE_ENERGY_REGEN_PER_SEC
            var structure_active: bool = bool(influence.get("structure_active", false))
            if structure_active:
                regen_per_sec += POI_STRUCTURE_EXTRA_ENERGY_REGEN_PER_SEC
                poi_structure_regen_bonus_ticks_total += 1

            actor.energy = min(actor.max_energy, actor.energy + regen_per_sec * delta)
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


func _update_actor_allegiances() -> void:
    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        var old_id: String = actor.allegiance_id
        var old_home: String = actor.home_poi
        var resolved: Dictionary = world_manager.resolve_actor_allegiance(actor)
        var next_id: String = str(resolved.get("allegiance_id", ""))
        var next_home: String = str(resolved.get("home_poi", ""))
        var changed: bool = bool(resolved.get("changed", false))
        var reason: String = str(resolved.get("reason", "none"))
        if not changed:
            continue

        actor.set_allegiance(next_id, next_home)

        if old_id == "" and next_id != "":
            allegiance_assignments_total += 1
            record_event("Allegiance assign: %s -> %s (%s)." % [_actor_label(actor), next_id, reason])
        elif old_id != "" and next_id == "":
            allegiance_losses_total += 1
            record_event("Allegiance lost: %s from %s (%s)." % [_actor_label(actor), old_id, reason])
        elif old_id != next_id:
            allegiance_assignments_total += 1
            record_event("Allegiance shift: %s %s -> %s (%s)." % [_actor_label(actor), old_id, next_id, reason])
        elif old_home != next_home:
            record_event("Allegiance home update: %s %s -> %s." % [_actor_label(actor), old_home, next_home])


func _clear_actor_influence_timers(actor_id: int) -> void:
    var prefix := "%d:" % actor_id
    var to_remove: Array[String] = []
    for key_variant in _poi_influence_xp_timers.keys():
        var key_text := str(key_variant)
        if key_text.begins_with(prefix):
            to_remove.append(key_text)
    for key_text in to_remove:
        _poi_influence_xp_timers.erase(key_text)


func _clear_actor_rally_tracking(actor_id: int) -> void:
    _prev_rally_leader_counts.erase(actor_id)
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.rally_leader_id == actor_id:
            actor.rally_leader_id = 0
            actor.rally_bonus_active = false
            actor.rally_relic_bonus_active = false


func _scan_for_champion_promotion(delta: float) -> void:
    _champion_scan_timer += delta
    if _champion_scan_timer < 2.0:
        return
    _champion_scan_timer = 0.0

    for actor in actors:
        if actor == null or actor.is_dead or actor.is_champion:
            continue
        var was_champion := actor.is_champion
        _try_promote_champion(actor, "periodic_scan")
        if not was_champion and actor.is_champion:
            return
        if not _can_promote_new_champion():
            return


func _try_promote_champion(actor: Actor, promotion_reason: String) -> void:
    if actor == null:
        return
    if not actor.is_ready_for_champion(
        CHAMPION_MIN_LEVEL,
        CHAMPION_MIN_KILLS,
        CHAMPION_MIN_AGE_SECONDS,
        CHAMPION_MIN_PROGRESS_XP
    ):
        return
    if not _can_promote_new_champion():
        return

    actor.promote_to_champion(promotion_reason)
    champion_promotions_total += 1
    record_event(
        "Champion promoted: %s (%s, kills=%d, age=%.1fs)."
        % [_actor_label(actor), promotion_reason, actor.kill_count, actor.age_seconds]
    )


func _can_promote_new_champion() -> bool:
    var alive_total: int = _count_alive_actors()
    if alive_total < CHAMPION_MIN_POPULATION:
        return false
    var champion_alive: int = _count_alive_champions("")
    var champion_cap: int = max(1, int(floor(float(alive_total) * CHAMPION_MAX_RATIO)))
    return champion_alive < champion_cap


func _count_alive_actors() -> int:
    var total := 0
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        total += 1
    return total


func _count_alive_champions(faction_filter: String) -> int:
    var total := 0
    for actor in actors:
        if actor == null or actor.is_dead or not actor.is_champion:
            continue
        if faction_filter != "" and actor.faction != faction_filter:
            continue
        total += 1
    return total


func _count_alive_special_arrivals(faction_filter: String) -> int:
    var total := 0
    for actor in actors:
        if actor == null or actor.is_dead or not actor.is_special_arrival():
            continue
        if faction_filter != "" and actor.faction != faction_filter:
            continue
        total += 1
    return total


func _actor_label(actor: Actor) -> String:
    if actor == null:
        return "unknown"
    var role_suffix := actor.role_tag()
    var level_suffix := actor.level_tag()
    var champion_suffix := actor.champion_tag()
    var special_suffix := actor.special_tag()
    var relic_suffix := actor.relic_tag()
    var bounty_suffix := actor.bounty_tag()
    var allegiance_suffix := actor.allegiance_tag()
    return "%s%s%s%s%s%s%s%s#%d" % [actor.actor_kind, role_suffix, level_suffix, champion_suffix, special_suffix, relic_suffix, bounty_suffix, allegiance_suffix, actor.actor_id]
