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

var actor_poi_presence: Dictionary = {}
var poi_runtime_snapshot: Dictionary = {}
var _poi_influence_xp_timers: Dictionary = {}
var _champion_scan_timer: float = 0.0
var _prev_rally_leader_counts: Dictionary = {}

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

    _update_rally_runtime()
    magic_system.tick_projectiles(delta, actors, self)
    _update_poi_runtime()
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

    if to_state in ["attack", "cast", "cast_nova", "cast_control", "flee", "poi", "reposition", "rally"]:
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

        var level_key := "L%d" % clampi(actor.level, 1, 3)
        level_counts[level_key] += 1

        if actor.faction == "human":
            humans_alive += 1
            if actor.is_champion:
                human_champions_alive += 1
            human_level_counts[level_key] += 1
            if human_role_counts.has(actor.human_role):
                human_role_counts[actor.human_role] += 1
            if actor.is_slowed():
                slowed_humans += 1
        elif actor.faction == "monster":
            monsters_alive += 1
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
    var poi_influence_active_count: int = 0
    var poi_structure_active_count: int = 0
    for poi_name in poi_runtime_snapshot.keys():
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if bool(details.get("influence_active", false)):
            poi_influence_active_count += 1
        if bool(details.get("structure_active", false)):
            poi_structure_active_count += 1

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
            continue

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


func _actor_label(actor: Actor) -> String:
    if actor == null:
        return "unknown"
    var role_suffix := actor.role_tag()
    var level_suffix := actor.level_tag()
    var champion_suffix := actor.champion_tag()
    return "%s%s%s%s#%d" % [actor.actor_kind, role_suffix, level_suffix, champion_suffix, actor.actor_id]
