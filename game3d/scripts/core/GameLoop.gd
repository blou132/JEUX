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
const BOUNTY_NOTORIETY_PRIORITY_MIN: float = 36.0
const DESTINY_START_DELAY: float = 74.0
const DESTINY_CHECK_INTERVAL: float = 2.8
const DESTINY_TRIGGER_CHANCE: float = 0.18
const DESTINY_GLOBAL_COOLDOWN: float = 16.0
const DESTINY_ACTOR_COOLDOWN: float = 52.0
const DESTINY_DURATION_MIN: float = 12.0
const DESTINY_DURATION_MAX: float = 22.0
const DESTINY_MAX_ACTIVE: int = 4
const DESTINY_MIN_POPULATION: int = 12
const DESTINY_HIGH_RENOWN_TRIGGER: float = 68.0
const DESTINY_TARGET_MAX_DISTANCE: float = 36.0
const DESTINY_FULFILL_RADIUS: float = 4.2
const DESTINY_FULFILL_HOLD: float = 1.3
const DESTINY_NEAR_ENERGY_BONUS_PER_SEC: float = 0.18
const CONVERGENCE_START_DELAY: float = 92.0
const CONVERGENCE_CHECK_INTERVAL: float = 3.2
const CONVERGENCE_TRIGGER_CHANCE: float = 0.20
const CONVERGENCE_GLOBAL_COOLDOWN: float = 58.0
const CONVERGENCE_DURATION_MIN: float = 9.0
const CONVERGENCE_DURATION_MAX: float = 15.0
const CONVERGENCE_MAX_ACTIVE: int = 1
const CONVERGENCE_MIN_POPULATION: int = 12
const CONVERGENCE_RADIUS: float = 8.4
const CONVERGENCE_PULSE_INTERVAL: float = 2.8
const CONVERGENCE_RENOWN_PULSE: float = 0.07
const CONVERGENCE_NOTORIETY_PULSE: float = 0.09
const MARKED_ZONE_START_DELAY: float = 104.0
const MARKED_ZONE_CHECK_INTERVAL: float = 3.4
const MARKED_ZONE_TRIGGER_CHANCE: float = 0.22
const MARKED_ZONE_GLOBAL_COOLDOWN: float = 42.0
const MARKED_ZONE_DURATION_MIN: float = 18.0
const MARKED_ZONE_DURATION_MAX: float = 30.0
const MARKED_ZONE_MAX_ACTIVE: int = 2
const MARKED_ZONE_MIN_POPULATION: int = 10
const MARKED_ZONE_RADIUS: float = 7.6
const MARKED_ZONE_PULSE_INTERVAL: float = 2.6
const SANCTIFIED_ZONE_ENERGY_PULSE: float = 0.24
const SANCTIFIED_ZONE_RENOWN_PULSE: float = 0.06
const CORRUPTED_ZONE_ENERGY_DRAIN_PULSE: float = 0.22
const CORRUPTED_ZONE_NOTORIETY_PULSE: float = 0.08
const RIVALRY_START_DELAY: float = 122.0
const RIVALRY_CHECK_INTERVAL: float = 3.6
const RIVALRY_TRIGGER_CHANCE: float = 0.18
const RIVALRY_GLOBAL_COOLDOWN: float = 24.0
const RIVALRY_ACTOR_COOLDOWN: float = 54.0
const RIVALRY_DURATION_MIN: float = 20.0
const RIVALRY_DURATION_MAX: float = 34.0
const RIVALRY_MAX_ACTIVE: int = 2
const RIVALRY_MIN_POPULATION: int = 12
const RIVALRY_ENGAGEMENT_WINDOW: float = 30.0
const RIVALRY_MIN_ENGAGEMENT_SCORE: float = 2.45
const RIVALRY_BASE_FOCUS_WEIGHT: float = 0.50
const RIVALRY_DUEL_FOCUS_WEIGHT: float = 0.70
const RIVALRY_DUEL_RANGE: float = 5.2
const RIVALRY_DUEL_HOLD: float = 1.0
const RIVALRY_DUEL_START_CHANCE: float = 0.44
const RIVALRY_DUEL_DURATION_MIN: float = 5.5
const RIVALRY_DUEL_DURATION_MAX: float = 8.4
const RIVALRY_DUEL_RENOWN_PULSE: float = 0.12
const RIVALRY_DUEL_NOTORIETY_PULSE: float = 0.14
const BOND_START_DELAY: float = 146.0
const BOND_GLOBAL_COOLDOWN: float = 32.0
const BOND_ACTOR_COOLDOWN: float = 62.0
const BOND_DURATION_MIN: float = 18.0
const BOND_DURATION_MAX: float = 30.0
const BOND_MAX_ACTIVE: int = 3
const BOND_MAX_PER_ALLEGIANCE: int = 1
const BOND_MIN_POPULATION: int = 10
const BOND_RADIUS: float = 7.8
const BOND_PULSE_INTERVAL: float = 3.2
const BOND_SHARED_RENOWN_PULSE: float = 0.05
const BOND_RALLY_BONUS_CHANCE_PER_SEC: float = 0.18
const BOND_RALLY_TRIGGER_MIN_FOLLOWERS: int = 3
const BOND_RALLY_TRIGGER_CHANCE: float = 0.26
const BOND_LEGACY_TRIGGER_CHANCE: float = 0.34
const BOND_RECOVERY_TRIGGER_CHANCE: float = 0.24
const NEUTRAL_GATE_BREACH_BOUNTY_COOLDOWN_CLAMP: float = 3.0
const GATE_RESPONSE_MIN_POPULATION: int = 10
const GATE_RESPONSE_CHECK_INTERVAL: float = 2.5
const GATE_RESPONSE_COOLDOWN: float = 34.0
const GATE_RESPONSE_DURATION_MIN: float = 11.0
const GATE_RESPONSE_DURATION_MAX: float = 17.0
const GATE_RESPONSE_PULL_BOOST: float = 1.22
const GATE_RESPONSE_SEAL_START_REDUCE: float = 2.2
const GATE_RESPONSE_EXPLOIT_START_EXTEND: float = 1.4
const GATE_RESPONSE_SEAL_BASE_CHANCE: float = 0.42
const GATE_RESPONSE_EXPLOIT_BASE_CHANCE: float = 0.40
const GATE_RESPONSE_NOTABLE_RADIUS: float = 12.0
const ALLEGIANCE_CRISIS_DURATION_MIN: float = 18.0
const ALLEGIANCE_CRISIS_DURATION_MAX: float = 30.0
const ALLEGIANCE_CRISIS_COOLDOWN: float = 46.0
const ALLEGIANCE_CRISIS_RAID_WEIGHT_MULT: float = 0.86
const ALLEGIANCE_CRISIS_RALLY_BONUS_SUPPRESS_CHANCE: float = 0.56
const ALLEGIANCE_CRISIS_START_CHANCE_BASE: float = 0.34
const ALLEGIANCE_CRISIS_RENOWN_TRIGGER: float = 54.0
const ALLEGIANCE_CRISIS_NOTORIETY_TRIGGER: float = 60.0
const ALLEGIANCE_RECOVERY_DURATION_MIN: float = 12.0
const ALLEGIANCE_RECOVERY_DURATION_MAX: float = 19.0
const ALLEGIANCE_RECOVERY_COOLDOWN: float = 34.0
const ALLEGIANCE_RECOVERY_START_CHANCE_BASE: float = 0.38
const ALLEGIANCE_RECOVERY_DEFENSE_WEIGHT_DELTA: float = 0.09
const ALLEGIANCE_RECOVERY_RALLY_BONUS_BOOST_CHANCE: float = 0.36
const ALLEGIANCE_RECOVERY_STRUCTURE_RESTABILIZE_WINDOW: float = 28.0
const NOTABILITY_LOG_THRESHOLDS: Array[float] = [20.0, 45.0, 70.0]
const RENOWN_GAIN_ON_KILL: float = 1.3
const RENOWN_GAIN_ON_LEVEL_UP: float = 4.5
const RENOWN_GAIN_ON_CHAMPION: float = 12.0
const RENOWN_GAIN_ON_SPECIAL_ARRIVAL: float = 14.0
const RENOWN_GAIN_ON_RELIC: float = 7.0
const RENOWN_GAIN_ON_BOUNTY_MARK: float = 1.8
const RENOWN_GAIN_ON_BOUNTY_CLEAR_KILL: float = 2.0
const NOTORIETY_GAIN_ON_KILL: float = 4.5
const NOTORIETY_GAIN_ON_CHAMPION: float = 8.0
const NOTORIETY_GAIN_ON_SPECIAL_ARRIVAL: float = 10.0
const NOTORIETY_GAIN_ON_RELIC: float = 4.0
const NOTORIETY_GAIN_ON_BOUNTY_MARK: float = 11.0
const NOTORIETY_GAIN_ON_BOUNTY_CLEAR_KILL: float = 2.2
const LEGACY_TRIGGER_CHANCE: float = 0.56
const LEGACY_COOLDOWN: float = 14.0
const LEGACY_SUCCESSOR_RADIUS: float = 11.5
const LEGACY_SUCCESSOR_DURATION: float = 24.0
const LEGACY_MAX_ACTIVE_SUCCESSORS: int = 4
const LEGACY_RENOWN_TRIGGER: float = 52.0
const LEGACY_NOTORIETY_TRIGGER: float = 58.0
const LEGACY_RENOWN_TRANSFER_RATIO: float = 0.12
const LEGACY_NOTORIETY_TRANSFER_RATIO: float = 0.10
const MEMORIAL_SCAR_MAX_ACTIVE: int = 4
const MEMORIAL_SCAR_DURATION_MIN: float = 24.0
const MEMORIAL_SCAR_DURATION_MAX: float = 38.0
const MEMORIAL_SCAR_RADIUS: float = 8.0
const MEMORIAL_SCAR_PULSE_INTERVAL: float = 3.0
const MEMORIAL_SITE_RENOWN_PULSE: float = 0.18
const SCAR_SITE_NOTORIETY_PULSE: float = 0.22
const MEMORIAL_SCAR_RENOWN_TRIGGER: float = 56.0
const MEMORIAL_SCAR_NOTORIETY_TRIGGER: float = 62.0

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
var destiny_started_total: int = 0
var destiny_ended_total: int = 0
var destiny_fulfilled_total: int = 0
var destiny_interrupted_total: int = 0
var convergence_started_total: int = 0
var convergence_ended_total: int = 0
var convergence_interrupted_total: int = 0
var marked_zone_started_total: int = 0
var marked_zone_faded_total: int = 0
var rivalry_started_total: int = 0
var rivalry_ended_total: int = 0
var rivalry_resolved_total: int = 0
var rivalry_expired_total: int = 0
var duel_started_total: int = 0
var bond_started_total: int = 0
var bond_ended_total: int = 0
var bond_broken_total: int = 0
var renown_rising_events_total: int = 0
var notoriety_rising_events_total: int = 0
var neutral_gate_opened_total: int = 0
var neutral_gate_closed_total: int = 0
var neutral_gate_breach_total: int = 0
var gate_response_started_total: int = 0
var gate_response_ended_total: int = 0
var gate_response_success_total: int = 0
var gate_response_interrupted_total: int = 0
var crisis_started_total: int = 0
var crisis_ended_total: int = 0
var crisis_resolved_total: int = 0
var crisis_expired_total: int = 0
var recovery_started_total: int = 0
var recovery_ended_total: int = 0
var recovery_interrupted_total: int = 0
var doctrine_assigned_total: int = 0
var project_started_total: int = 0
var project_ended_total: int = 0
var project_interrupted_total: int = 0
var vendetta_started_total: int = 0
var vendetta_ended_total: int = 0
var vendetta_resolved_total: int = 0
var vendetta_expired_total: int = 0
var legacy_triggered_total: int = 0
var legacy_successor_chosen_total: int = 0
var legacy_relic_inherited_total: int = 0
var legacy_faded_total: int = 0
var memorial_scar_born_total: int = 0
var memorial_scar_faded_total: int = 0
var bounty_active: bool = false
var bounty_target_actor_id: int = 0
var bounty_target_faction: String = ""
var bounty_target_allegiance_id: String = ""
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
var _destiny_check_timer: float = 0.0
var _destiny_global_cooldown_left: float = DESTINY_START_DELAY
var _destiny_runtime_by_actor: Dictionary = {}
var _destiny_cooldown_until_by_actor: Dictionary = {}
var _convergence_check_timer: float = 0.0
var _convergence_global_cooldown_left: float = CONVERGENCE_START_DELAY
var _convergence_runtime_by_id: Dictionary = {}
var _convergence_next_id: int = 1
var _convergence_signals_root: Node3D = null
var _marked_zone_check_timer: float = 0.0
var _marked_zone_global_cooldown_left: float = MARKED_ZONE_START_DELAY
var _marked_zone_runtime_by_id: Dictionary = {}
var _marked_zone_next_id: int = 1
var _marked_zone_signals_root: Node3D = null
var _rivalry_check_timer: float = 0.0
var _rivalry_global_cooldown_left: float = RIVALRY_START_DELAY
var _rivalry_runtime_by_id: Dictionary = {}
var _rivalry_next_id: int = 1
var _rivalry_id_by_actor: Dictionary = {}
var _rivalry_cooldown_until_by_actor: Dictionary = {}
var _rivalry_engagement_by_pair: Dictionary = {}
var _bond_global_cooldown_left: float = BOND_START_DELAY
var _bond_runtime_by_id: Dictionary = {}
var _bond_next_id: int = 1
var _bond_id_by_patron: Dictionary = {}
var _bond_cooldown_until_by_actor: Dictionary = {}
var _renown_tier_by_actor: Dictionary = {}
var _notoriety_tier_by_actor: Dictionary = {}
var _legacy_cooldown_left: float = 0.0
var _legacy_successor_runtime_by_actor: Dictionary = {}
var _gate_response_check_timer: float = 0.0
var _gate_response_cooldown_by_faction: Dictionary = {}
var _gate_response_runtime_by_faction: Dictionary = {}
var _gate_response_signals_root: Node3D = null
var _allegiance_crisis_runtime_by_id: Dictionary = {}
var _allegiance_crisis_cooldown_until_by_id: Dictionary = {}
var _allegiance_recovery_runtime_by_id: Dictionary = {}
var _allegiance_recovery_cooldown_until_by_id: Dictionary = {}
var _recent_structure_loss_until_by_poi: Dictionary = {}
var _memorial_scar_runtime: Dictionary = {}
var _memorial_scar_next_id: int = 1
var _memorial_scar_sites_root: Node3D = null

var event_log: Array[String] = []


func _ready() -> void:
    randomize()
    world_event_modifiers = _default_world_event_modifiers()
    world_manager.setup_world()
    _setup_gate_response_state()
    _setup_convergence_state()
    _setup_marked_zone_state()
    _setup_rivalry_state()
    _setup_bond_state()
    _setup_allegiance_crisis_state()
    _setup_allegiance_recovery_state()
    _setup_memorial_scar_sites_root()
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
    _update_bonds(delta)
    magic_system.tick_projectiles(delta, actors, self)
    _update_poi_runtime()
    _update_actor_allegiances()
    _update_allegiance_crisis_runtime(delta)
    _update_allegiance_recovery_runtime(delta)
    _update_gate_responses(delta)
    _update_bounty_system(delta)
    _update_special_arrivals(delta)
    _update_relic_system(delta)
    _update_destiny_pulls(delta)
    _update_convergence_events(delta)
    _update_marked_zones(delta)
    _update_rivalries(delta)
    _apply_poi_influences(delta)
    _scan_for_champion_promotion(delta)
    _update_legacy_runtime(delta)
    _update_memorial_scar_runtime(delta)
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
    _record_rivalry_engagement(attacker, target, kind)


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
            _apply_notability_gain(killer, RENOWN_GAIN_ON_KILL, NOTORIETY_GAIN_ON_KILL, "kill")
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
    _handle_rivalry_death(victim, killer)
    var legacy_result: Dictionary = _try_trigger_legacy(victim, killer, reason)
    var relic_inherited: bool = bool(legacy_result.get("relic_inherited", false))
    var had_relic: bool = victim.has_relic()
    if victim.has_relic():
        if not relic_inherited:
            var lost_title := victim.relic_title if victim.relic_title != "" else _relic_title(victim.relic_id)
            record_event("Relic LOST: %s from %s." % [lost_title, _actor_label(victim)])
            relic_lost_total += 1
            _relic_cooldown_left = max(_relic_cooldown_left, RELIC_COOLDOWN * 0.34)
        victim.clear_relic()
    _handle_bounty_target_death(victim, killer)
    _try_spawn_memorial_scar_site(victim, killer, reason, legacy_result, had_relic)
    _try_start_crisis_from_notable_fall(victim, reason, legacy_result, had_relic)


func register_level_up(actor: Actor, old_level: int, new_level: int, reason: String) -> void:
    if actor == null:
        return
    level_ups_total += 1
    var renown_gain: float = RENOWN_GAIN_ON_LEVEL_UP + max(0.0, float(new_level - 2)) * 1.2
    var notoriety_gain: float = 0.0
    if new_level >= actor.max_level:
        notoriety_gain = 1.1
    _apply_notability_gain(actor, renown_gain, notoriety_gain, "level_up:%s" % reason)
    record_event(
        "Level up: %s L%d -> L%d (%s)."
        % [_actor_label(actor), old_level, new_level, reason]
    )
    _try_promote_champion(actor, "level_up:%s" % reason)


func _setup_gate_response_state() -> void:
    _gate_response_cooldown_by_faction = {
        "human": 0.0,
        "monster": 0.0
    }
    _gate_response_runtime_by_faction.clear()

    if _gate_response_signals_root != null and is_instance_valid(_gate_response_signals_root):
        _gate_response_signals_root.queue_free()
    _gate_response_signals_root = Node3D.new()
    _gate_response_signals_root.name = "GateResponseSignals"
    world_manager.add_child(_gate_response_signals_root)
    world_manager.set_neutral_gate_response_pull_modifiers(1.0, 1.0)


func _update_gate_response_cooldowns(delta: float) -> void:
    var factions: Array[String] = ["human", "monster"]
    for faction in factions:
        var left: float = float(_gate_response_cooldown_by_faction.get(faction, 0.0))
        _gate_response_cooldown_by_faction[faction] = max(0.0, left - delta)


func _update_gate_responses(delta: float) -> void:
    _update_gate_response_cooldowns(delta)
    var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    var gate_open: bool = bool(gate_runtime.get("active", false))
    var gate_name: String = str(gate_runtime.get("poi", "rift_gate"))
    var gate_position: Vector3 = _get_poi_position_by_name(gate_name)

    _update_active_gate_responses(gate_open)
    _sync_gate_response_pull_modifiers()

    if not gate_open:
        _gate_response_check_timer = 0.0
        return
    if _count_alive_actors() < GATE_RESPONSE_MIN_POPULATION:
        return

    _gate_response_check_timer += delta
    if _gate_response_check_timer < GATE_RESPONSE_CHECK_INTERVAL:
        return
    _gate_response_check_timer = 0.0

    _try_start_gate_response("human", gate_name, gate_position)
    _try_start_gate_response("monster", gate_name, gate_position)
    _sync_gate_response_pull_modifiers()


func _update_active_gate_responses(gate_open: bool) -> void:
    if _gate_response_runtime_by_faction.is_empty():
        return

    var factions: Array = _gate_response_runtime_by_faction.keys()
    for faction_variant in factions:
        var faction: String = str(faction_variant)
        var runtime: Dictionary = _gate_response_runtime_by_faction.get(faction, {})
        if runtime.is_empty():
            continue

        if not gate_open:
            _end_gate_response(faction, "interrupted", "gate_closed")
            continue

        var allegiance_id: String = str(runtime.get("allegiance_id", ""))
        if allegiance_id == "" or not _is_gate_response_anchor_active(allegiance_id):
            _end_gate_response(faction, "interrupted", "anchor_lost")
            continue

        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        if elapsed_time >= ends_at:
            _end_gate_response(faction, "success", "duration_complete")


func _try_start_gate_response(faction: String, gate_name: String, gate_position: Vector3) -> void:
    if _gate_response_runtime_by_faction.has(faction):
        return
    if float(_gate_response_cooldown_by_faction.get(faction, 0.0)) > 0.0:
        return

    var candidate: Dictionary = _pick_gate_response_candidate(faction, gate_position)
    if candidate.is_empty():
        return

    var start_chance: float = _gate_response_start_chance(faction, candidate)
    if randf() > start_chance:
        return

    var response_id: String = "gate_seal" if faction == "human" else "gate_exploit"
    var duration: float = randf_range(
        min(GATE_RESPONSE_DURATION_MIN, GATE_RESPONSE_DURATION_MAX),
        max(GATE_RESPONSE_DURATION_MIN, GATE_RESPONSE_DURATION_MAX)
    )
    var allegiance_id: String = str(candidate.get("allegiance_id", ""))
    var project_id: String = str(candidate.get("project_id", ""))
    var doctrine: String = str(candidate.get("doctrine", ""))
    var notable_count: int = int(candidate.get("notable_count", 0))
    var gate_delta: float = 0.0
    var bonus_breach: bool = false

    if response_id == "gate_seal":
        gate_delta = world_manager.apply_neutral_gate_open_duration_delta(-GATE_RESPONSE_SEAL_START_REDUCE, elapsed_time)
    else:
        gate_delta = world_manager.apply_neutral_gate_open_duration_delta(GATE_RESPONSE_EXPLOIT_START_EXTEND, elapsed_time)
        bonus_breach = world_manager.request_neutral_gate_bonus_breach(elapsed_time)

    _gate_response_runtime_by_faction[faction] = {
        "response_id": response_id,
        "faction": faction,
        "allegiance_id": allegiance_id,
        "project_id": project_id,
        "doctrine": doctrine,
        "notable_count": notable_count,
        "started_at": elapsed_time,
        "ends_at": elapsed_time + duration,
        "gate_name": gate_name,
        "gate_delta": gate_delta,
        "bonus_breach": bonus_breach
    }

    gate_response_started_total += 1
    _gate_response_check_timer = 0.0
    _spawn_gate_response_signal(faction, gate_position, response_id)

    var allegiance_label := allegiance_id if allegiance_id != "" else faction
    var gate_label := gate_name if gate_name != "" else "rift_gate"
    var effect_label: String = ""
    if response_id == "gate_seal":
        effect_label = "gate_shift=%.1fs" % gate_delta
    else:
        effect_label = "gate_shift=%.1fs breach_bonus=%s" % [gate_delta, "yes" if bonus_breach else "no"]
    record_event(
        "Gate Response START: %s by %s at %s (%s, %.0fs, notables=%d)."
        % [response_id, allegiance_label, gate_label, effect_label, duration, notable_count]
    )


func _pick_gate_response_candidate(faction: String, gate_position: Vector3) -> Dictionary:
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    if active_allegiances.is_empty():
        return {}

    var notable_count: int = _count_notables_near_gate(faction, gate_position, GATE_RESPONSE_NOTABLE_RADIUS)
    var selected: Dictionary = {}
    var best_score: float = -INF
    var max_anchor_distance: float = world_manager.poi_guidance_distance * 2.40

    for allegiance in active_allegiances:
        if str(allegiance.get("faction", "")) != faction:
            continue

        var doctrine: String = str(allegiance.get("doctrine", ""))
        if faction == "human" and doctrine != "arcane":
            continue
        if faction == "monster" and doctrine != "warlike":
            continue

        var anchor_position: Vector3 = allegiance.get("position", gate_position)
        var anchor_distance: float = anchor_position.distance_to(gate_position)
        if anchor_distance > max_anchor_distance:
            continue

        var project_id: String = str(allegiance.get("project", ""))
        var score: float = max(0.0, max_anchor_distance - anchor_distance) * 0.06
        score += float(notable_count) * 0.82
        if faction == "human":
            if project_id == "ritual_focus":
                score += 1.20
            elif project_id == "fortify":
                score += 0.64
        else:
            if project_id == "warband_muster":
                score += 1.10
            elif project_id == "ritual_focus":
                score += 0.52

        if score > best_score:
            best_score = score
            selected = {
                "allegiance_id": str(allegiance.get("allegiance_id", "")),
                "doctrine": doctrine,
                "project_id": project_id,
                "notable_count": notable_count
            }

    return selected


func _gate_response_start_chance(faction: String, candidate: Dictionary) -> float:
    var chance: float = GATE_RESPONSE_SEAL_BASE_CHANCE if faction == "human" else GATE_RESPONSE_EXPLOIT_BASE_CHANCE
    var project_id: String = str(candidate.get("project_id", ""))
    var notable_count: int = int(candidate.get("notable_count", 0))

    if faction == "human":
        if project_id == "ritual_focus":
            chance += 0.12
        elif project_id == "fortify":
            chance += 0.06
        if world_event_active_id == "mana_surge" or world_event_active_id == "sanctuary_calm":
            chance += 0.08
    else:
        if project_id == "warband_muster":
            chance += 0.10
        elif project_id == "ritual_focus":
            chance += 0.05
        if world_event_active_id == "monster_frenzy":
            chance += 0.08

    if notable_count > 0:
        chance += 0.06
    return clampf(chance, 0.20, 0.80)


func _count_notables_near_gate(faction: String, center: Vector3, radius: float) -> int:
    var total: int = 0
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction != faction:
            continue
        if actor.global_position.distance_to(center) > radius:
            continue
        if actor.is_champion or actor.is_special_arrival() or actor.has_relic():
            total += 1
            continue
        if actor.renown >= 40.0 or actor.notoriety >= 52.0:
            total += 1
    return total


func _is_gate_response_anchor_active(allegiance_id: String) -> bool:
    return _is_allegiance_anchor_active(allegiance_id)


func _end_gate_response(faction: String, outcome: String, reason: String) -> void:
    var runtime: Dictionary = _gate_response_runtime_by_faction.get(faction, {})
    if runtime.is_empty():
        return

    var response_id: String = str(runtime.get("response_id", "gate_response"))
    var allegiance_id: String = str(runtime.get("allegiance_id", faction))
    var label: String = allegiance_id if allegiance_id != "" else faction

    if outcome == "success":
        gate_response_success_total += 1
        record_event("Gate Response SUCCESS: %s by %s." % [response_id, label])
    elif outcome == "interrupted":
        gate_response_interrupted_total += 1
        record_event("Gate Response INTERRUPTED: %s by %s (%s)." % [response_id, label, reason])

    gate_response_ended_total += 1
    record_event("Gate Response END: %s by %s (%s)." % [response_id, label, reason])
    _gate_response_runtime_by_faction.erase(faction)
    _gate_response_cooldown_by_faction[faction] = GATE_RESPONSE_COOLDOWN


func _sync_gate_response_pull_modifiers() -> void:
    var human_mult: float = GATE_RESPONSE_PULL_BOOST if _gate_response_runtime_by_faction.has("human") else 1.0
    var monster_mult: float = GATE_RESPONSE_PULL_BOOST if _gate_response_runtime_by_faction.has("monster") else 1.0
    world_manager.set_neutral_gate_response_pull_modifiers(human_mult, monster_mult)


func _spawn_gate_response_signal(faction: String, position: Vector3, response_id: String) -> void:
    if _gate_response_signals_root == null or not is_instance_valid(_gate_response_signals_root):
        return

    var signal_node := MeshInstance3D.new()
    signal_node.name = "GateResponseSignal_%s_%d" % [response_id, tick_index]
    var mesh := CylinderMesh.new()
    mesh.top_radius = 2.10
    mesh.bottom_radius = 2.10
    mesh.height = 0.08
    signal_node.mesh = mesh
    signal_node.position = position + Vector3(0.0, 0.14, 0.0)
    signal_node.scale = Vector3.ONE * 0.22

    var color := Color(0.58, 0.86, 1.0) if faction == "human" else Color(1.0, 0.52, 0.34)
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.emission_enabled = true
    material.emission = color * 1.18
    signal_node.material_override = material
    _gate_response_signals_root.add_child(signal_node)

    var tween := create_tween()
    tween.tween_property(signal_node, "scale", Vector3.ONE * 1.52, 0.42)
    tween.finished.connect(signal_node.queue_free)


func _setup_convergence_state() -> void:
    if _convergence_signals_root != null and is_instance_valid(_convergence_signals_root):
        _convergence_signals_root.queue_free()
    _convergence_signals_root = Node3D.new()
    _convergence_signals_root.name = "ConvergenceSignals"
    world_manager.add_child(_convergence_signals_root)

    _convergence_runtime_by_id.clear()
    _convergence_next_id = 1
    _convergence_check_timer = 0.0
    _convergence_global_cooldown_left = CONVERGENCE_START_DELAY
    world_manager.set_convergence_state(false)


func _update_convergence_events(delta: float) -> void:
    _convergence_global_cooldown_left = max(0.0, _convergence_global_cooldown_left - delta)
    _convergence_check_timer += delta

    if not _convergence_runtime_by_id.is_empty():
        var event_ids: Array = _convergence_runtime_by_id.keys()
        for event_id_variant in event_ids:
            var event_id: int = int(event_id_variant)
            var runtime: Dictionary = _convergence_runtime_by_id.get(event_id, {})
            if runtime.is_empty():
                continue

            var gate_name: String = str(runtime.get("gate_name", "rift_gate"))
            var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
            if not bool(gate_runtime.get("active", false)) or str(gate_runtime.get("poi", "")) != gate_name:
                _end_convergence_event(event_id, true, "gate_closed")
                continue

            var center: Vector3 = runtime.get("center", Vector3.ZERO)
            var radius: float = float(runtime.get("radius", CONVERGENCE_RADIUS))
            var signal_counts: Dictionary = _collect_convergence_signal_counts(center, radius)
            if not bool(signal_counts.get("signals_ok", false)):
                _end_convergence_event(event_id, true, "signals_lost")
                continue

            runtime["destiny_count"] = int(signal_counts.get("destiny_count", 0))
            runtime["relic_count"] = int(signal_counts.get("relic_count", 0))
            runtime["notable_count"] = int(signal_counts.get("notable_count", 0))
            runtime["bounty_near"] = bool(signal_counts.get("bounty_near", false))

            var next_pulse_at: float = float(runtime.get("next_pulse_at", elapsed_time))
            if elapsed_time >= next_pulse_at:
                _apply_convergence_pulse(runtime)
                runtime["next_pulse_at"] = elapsed_time + CONVERGENCE_PULSE_INTERVAL

            var started_at: float = float(runtime.get("started_at", elapsed_time))
            var duration: float = max(0.01, float(runtime.get("duration", CONVERGENCE_DURATION_MIN)))
            var elapsed_ratio: float = clampf((elapsed_time - started_at) / duration, 0.0, 1.0)
            _animate_convergence_signal(runtime.get("visual_node", null) as Node3D, elapsed_ratio)

            _convergence_runtime_by_id[event_id] = runtime
            var ends_at: float = float(runtime.get("ends_at", elapsed_time))
            if elapsed_time >= ends_at:
                _end_convergence_event(event_id, false, "duration")

    _sync_convergence_state_to_world()

    if _convergence_check_timer < CONVERGENCE_CHECK_INTERVAL:
        return
    _convergence_check_timer = 0.0
    if _convergence_global_cooldown_left > 0.0:
        return
    if _count_alive_actors() < CONVERGENCE_MIN_POPULATION:
        return
    if _convergence_runtime_by_id.size() >= CONVERGENCE_MAX_ACTIVE:
        return
    if randf() > CONVERGENCE_TRIGGER_CHANCE:
        return

    var candidate: Dictionary = _build_convergence_candidate()
    if candidate.is_empty():
        return
    _start_convergence_event(candidate)
    _sync_convergence_state_to_world()


func _build_convergence_candidate() -> Dictionary:
    var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    if not bool(gate_runtime.get("active", false)):
        return {}

    var gate_name: String = str(gate_runtime.get("poi", "rift_gate"))
    if gate_name == "" or not _has_poi_named(gate_name):
        return {}
    var center: Vector3 = _get_poi_position_by_name(gate_name)

    var radius: float = CONVERGENCE_RADIUS
    var signal_counts: Dictionary = _collect_convergence_signal_counts(center, radius)
    if not bool(signal_counts.get("signals_ok", false)):
        return {}

    var destiny_count: int = int(signal_counts.get("destiny_count", 0))
    var relic_count: int = int(signal_counts.get("relic_count", 0))
    var notable_count: int = int(signal_counts.get("notable_count", 0))
    var bounty_near: bool = bool(signal_counts.get("bounty_near", false))
    var vendetta_active: bool = bool(signal_counts.get("vendetta_active", false))
    var score: float = float(
        destiny_count * 1.00
        + relic_count * 1.15
        + notable_count * 0.74
        + (0.42 if bounty_near else 0.0)
        + (0.32 if vendetta_active else 0.0)
    )
    if score < 2.0:
        return {}

    return {
        "label": gate_name if gate_name != "" else "rift_gate",
        "gate_name": gate_name,
        "center": center,
        "radius": radius,
        "score": score,
        "destiny_count": destiny_count,
        "relic_count": relic_count,
        "notable_count": notable_count,
        "bounty_near": bounty_near,
        "vendetta_active": vendetta_active
    }


func _collect_convergence_signal_counts(center: Vector3, radius: float) -> Dictionary:
    var destiny_count: int = 0
    var relic_count: int = 0
    var notable_count: int = 0
    var bounty_near: bool = false
    var scan_radius: float = radius * 1.35

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(center) > scan_radius:
            continue

        if actor.destiny_active:
            destiny_count += 1
        if actor.has_relic():
            relic_count += 1
        var is_successor: bool = _legacy_successor_runtime_by_actor.has(actor.actor_id)
        if actor.is_champion or actor.is_special_arrival() or is_successor:
            notable_count += 1
        if actor.bounty_marked:
            bounty_near = true

    var vendetta_active: bool = not world_manager.get_active_vendettas(elapsed_time).is_empty()
    var signals_ok: bool = destiny_count >= 1 and (relic_count >= 1 or notable_count >= 1)
    return {
        "signals_ok": signals_ok,
        "destiny_count": destiny_count,
        "relic_count": relic_count,
        "notable_count": notable_count,
        "bounty_near": bounty_near,
        "vendetta_active": vendetta_active
    }


func _start_convergence_event(candidate: Dictionary) -> void:
    if candidate.is_empty():
        return
    var event_id: int = _convergence_next_id
    _convergence_next_id += 1

    var duration: float = randf_range(
        min(CONVERGENCE_DURATION_MIN, CONVERGENCE_DURATION_MAX),
        max(CONVERGENCE_DURATION_MIN, CONVERGENCE_DURATION_MAX)
    )
    var center: Vector3 = candidate.get("center", Vector3.ZERO)
    var radius: float = float(candidate.get("radius", CONVERGENCE_RADIUS))
    var label: String = str(candidate.get("label", "crossroads"))
    var gate_name: String = str(candidate.get("gate_name", "rift_gate"))
    var signal_node: Node3D = _spawn_convergence_signal(center, event_id)

    _convergence_runtime_by_id[event_id] = {
        "id": event_id,
        "label": label,
        "gate_name": gate_name,
        "center": center,
        "radius": radius,
        "score": float(candidate.get("score", 2.0)),
        "destiny_count": int(candidate.get("destiny_count", 0)),
        "relic_count": int(candidate.get("relic_count", 0)),
        "notable_count": int(candidate.get("notable_count", 0)),
        "bounty_near": bool(candidate.get("bounty_near", false)),
        "vendetta_active": bool(candidate.get("vendetta_active", false)),
        "started_at": elapsed_time,
        "duration": duration,
        "ends_at": elapsed_time + duration,
        "next_pulse_at": elapsed_time + CONVERGENCE_PULSE_INTERVAL,
        "visual_node": signal_node
    }
    convergence_started_total += 1
    _convergence_global_cooldown_left = CONVERGENCE_GLOBAL_COOLDOWN
    _apply_convergence_pulse(_convergence_runtime_by_id[event_id])
    record_event(
        "Convergence START: %s at %s (destiny=%d relic=%d notable=%d, %.0fs)."
        % [
            label,
            _position_label_2d(center),
            int(candidate.get("destiny_count", 0)),
            int(candidate.get("relic_count", 0)),
            int(candidate.get("notable_count", 0)),
            duration
        ]
    )


func _spawn_convergence_signal(position: Vector3, event_id: int) -> Node3D:
    if _convergence_signals_root == null or not is_instance_valid(_convergence_signals_root):
        return null

    var node := Node3D.new()
    node.name = "Convergence_%d" % event_id
    node.position = position

    var ring := MeshInstance3D.new()
    ring.name = "Ring"
    var ring_mesh := CylinderMesh.new()
    ring_mesh.top_radius = 2.35
    ring_mesh.bottom_radius = 2.35
    ring_mesh.height = 0.09
    ring.mesh = ring_mesh
    ring.position = Vector3(0.0, 0.12, 0.0)
    var ring_mat := StandardMaterial3D.new()
    ring_mat.albedo_color = Color(0.82, 0.72, 0.34)
    ring_mat.emission_enabled = true
    ring_mat.emission = Color(0.82, 0.72, 0.34) * 1.08
    ring_mat.roughness = 0.68
    ring.material_override = ring_mat
    node.add_child(ring)

    var beacon := MeshInstance3D.new()
    beacon.name = "Beacon"
    var beacon_mesh := SphereMesh.new()
    beacon_mesh.radius = 0.26
    beacon_mesh.height = 0.52
    beacon.mesh = beacon_mesh
    beacon.position = Vector3(0.0, 1.25, 0.0)
    var beacon_mat := StandardMaterial3D.new()
    beacon_mat.albedo_color = Color(0.76, 0.52, 1.0)
    beacon_mat.emission_enabled = true
    beacon_mat.emission = Color(0.76, 0.52, 1.0) * 1.20
    beacon_mat.roughness = 0.66
    beacon.material_override = beacon_mat
    node.add_child(beacon)

    node.scale = Vector3.ONE * 0.20
    _convergence_signals_root.add_child(node)
    var tween := create_tween()
    tween.tween_property(node, "scale", Vector3.ONE, 0.34)
    return node


func _animate_convergence_signal(signal_node: Node3D, elapsed_ratio: float) -> void:
    if signal_node == null or not is_instance_valid(signal_node):
        return
    var ring := signal_node.get_node_or_null("Ring") as MeshInstance3D
    var beacon := signal_node.get_node_or_null("Beacon") as MeshInstance3D
    var seed: float = float(signal_node.get_instance_id() % 29)

    if ring != null:
        var pulse := 1.0 + 0.09 * sin(elapsed_time * 4.6 + seed)
        var fade := lerpf(1.0, 0.74, elapsed_ratio)
        ring.scale = Vector3.ONE * pulse * fade
    if beacon != null:
        beacon.position.y = 1.25 + 0.10 * sin(elapsed_time * 3.2 + seed * 0.45)
        var beacon_mat := beacon.material_override as StandardMaterial3D
        if beacon_mat != null:
            beacon_mat.emission = Color(0.76, 0.52, 1.0) * lerpf(1.20, 0.46, elapsed_ratio)


func _apply_convergence_pulse(runtime: Dictionary) -> void:
    var center: Vector3 = runtime.get("center", Vector3.ZERO)
    var radius: float = float(runtime.get("radius", CONVERGENCE_RADIUS))
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(center) > radius:
            continue
        _apply_notability_gain(actor, CONVERGENCE_RENOWN_PULSE, CONVERGENCE_NOTORIETY_PULSE, "convergence")


func _end_convergence_event(event_id: int, interrupted: bool, reason: String) -> void:
    var runtime: Dictionary = _convergence_runtime_by_id.get(event_id, {})
    if runtime.is_empty():
        return

    var label: String = str(runtime.get("label", "crossroads"))
    if interrupted:
        convergence_interrupted_total += 1
        record_event("Convergence INTERRUPTED: %s (%s)." % [label, reason])

    convergence_ended_total += 1
    record_event("Convergence END: %s (%s)." % [label, reason])

    var signal_node := runtime.get("visual_node", null) as Node3D
    if signal_node != null and is_instance_valid(signal_node):
        signal_node.queue_free()
    _convergence_runtime_by_id.erase(event_id)
    _sync_convergence_state_to_world()


func _sync_convergence_state_to_world() -> void:
    if _convergence_runtime_by_id.is_empty():
        world_manager.set_convergence_state(false)
        return
    var selected: Dictionary = {}
    var closest_end: float = INF
    for runtime_variant in _convergence_runtime_by_id.values():
        var runtime: Dictionary = runtime_variant
        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        if ends_at < closest_end:
            closest_end = ends_at
            selected = runtime
    if selected.is_empty():
        world_manager.set_convergence_state(false)
        return
    var pull_weight: float = 0.34 + min(0.18, float(selected.get("score", 2.0)) * 0.05)
    world_manager.set_convergence_state(
        true,
        selected.get("center", Vector3.ZERO),
        float(selected.get("radius", CONVERGENCE_RADIUS)),
        str(selected.get("label", "crossroads")),
        pull_weight
    )


func _setup_marked_zone_state() -> void:
    if _marked_zone_signals_root != null and is_instance_valid(_marked_zone_signals_root):
        _marked_zone_signals_root.queue_free()
    _marked_zone_signals_root = Node3D.new()
    _marked_zone_signals_root.name = "MarkedZoneSignals"
    world_manager.add_child(_marked_zone_signals_root)

    _marked_zone_runtime_by_id.clear()
    _marked_zone_next_id = 1
    _marked_zone_check_timer = 0.0
    _marked_zone_global_cooldown_left = MARKED_ZONE_START_DELAY


func _update_marked_zones(delta: float) -> void:
    _marked_zone_global_cooldown_left = max(0.0, _marked_zone_global_cooldown_left - delta)
    _marked_zone_check_timer += delta

    if not _marked_zone_runtime_by_id.is_empty():
        var zone_ids: Array = _marked_zone_runtime_by_id.keys()
        for zone_id_variant in zone_ids:
            var zone_id: int = int(zone_id_variant)
            var runtime: Dictionary = _marked_zone_runtime_by_id.get(zone_id, {})
            if runtime.is_empty():
                continue

            var source_site_id: int = int(runtime.get("source_site_id", 0))
            if source_site_id > 0 and not _memorial_scar_runtime.has(source_site_id):
                _fade_marked_zone(zone_id, "source_lost")
                continue

            var next_pulse_at: float = float(runtime.get("next_pulse_at", elapsed_time))
            if elapsed_time >= next_pulse_at:
                _apply_marked_zone_pulse(runtime)
                runtime["next_pulse_at"] = elapsed_time + MARKED_ZONE_PULSE_INTERVAL

            var started_at: float = float(runtime.get("started_at", elapsed_time))
            var duration: float = max(0.01, float(runtime.get("duration", MARKED_ZONE_DURATION_MIN)))
            var elapsed_ratio: float = clampf((elapsed_time - started_at) / duration, 0.0, 1.0)
            _animate_marked_zone_signal(
                runtime.get("visual_node", null) as Node3D,
                elapsed_ratio,
                str(runtime.get("zone_type", ""))
            )

            _marked_zone_runtime_by_id[zone_id] = runtime
            if elapsed_time >= float(runtime.get("ends_at", elapsed_time)):
                _fade_marked_zone(zone_id, "duration")

    if _marked_zone_check_timer < MARKED_ZONE_CHECK_INTERVAL:
        return
    _marked_zone_check_timer = 0.0
    if _marked_zone_global_cooldown_left > 0.0:
        return
    if _count_alive_actors() < MARKED_ZONE_MIN_POPULATION:
        return
    if _marked_zone_runtime_by_id.size() >= MARKED_ZONE_MAX_ACTIVE:
        return
    if randf() > MARKED_ZONE_TRIGGER_CHANCE:
        return

    var candidate: Dictionary = _build_marked_zone_candidate()
    if candidate.is_empty():
        return
    _start_marked_zone(candidate)


func _build_marked_zone_candidate() -> Dictionary:
    var best_candidate: Dictionary = {}
    var best_score: float = -INF

    for site_id_variant in _memorial_scar_runtime.keys():
        var site_id: int = int(site_id_variant)
        var site_runtime: Dictionary = _memorial_scar_runtime.get(site_id, {})
        if site_runtime.is_empty():
            continue

        var center: Vector3 = site_runtime.get("position", Vector3.ZERO)
        var signal_profile: Dictionary = _collect_marked_zone_signal_profile(center, MARKED_ZONE_RADIUS * 1.35)
        var site_type: String = str(site_runtime.get("type", ""))
        var source_short: String = str(site_runtime.get("source_short", "fallen"))
        var convergence_near: bool = bool(signal_profile.get("convergence_near", false))
        var score: float = -1.0
        var zone_type: String = ""
        var label: String = ""

        if site_type == "memorial_site":
            var heroic_count: int = int(signal_profile.get("heroic_count", 0))
            if heroic_count <= 0:
                continue
            score = float(
                heroic_count * 0.96
                + int(signal_profile.get("successor_count", 0)) * 0.44
                + int(signal_profile.get("renown_figures", 0)) * 0.28
                + (0.24 if convergence_near else 0.0)
            )
            zone_type = "sanctified_zone"
            label = "sanctified:%s" % source_short
        elif site_type == "scar_site":
            var corrupted_count: int = int(signal_profile.get("corrupted_count", 0))
            var gate_pressure: bool = bool(signal_profile.get("gate_pressure", false))
            if corrupted_count <= 0 and not gate_pressure:
                continue
            score = float(
                corrupted_count * 0.92
                + int(signal_profile.get("notoriety_figures", 0)) * 0.30
                + (0.38 if gate_pressure else 0.0)
                + (0.22 if convergence_near else 0.0)
            )
            zone_type = "corrupted_zone"
            label = "corrupted:%s" % source_short
        else:
            continue

        if score < 1.0:
            continue
        if not _can_start_marked_zone_at(center):
            continue
        if score <= best_score:
            continue

        best_score = score
        best_candidate = {
            "zone_type": zone_type,
            "label": label,
            "center": center,
            "radius": MARKED_ZONE_RADIUS,
            "score": score,
            "source_site_id": site_id
        }

    return best_candidate


func _collect_marked_zone_signal_profile(center: Vector3, radius: float) -> Dictionary:
    var heroic_count: int = 0
    var successor_count: int = 0
    var renown_figures: int = 0
    var corrupted_count: int = 0
    var notoriety_figures: int = 0

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(center) > radius:
            continue

        if actor.faction == "human":
            var is_successor: bool = _legacy_successor_runtime_by_actor.has(actor.actor_id)
            if is_successor:
                successor_count += 1
            if actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER:
                renown_figures += 1
            if (
                actor.is_champion
                or actor.special_arrival_id == "summoned_hero"
                or is_successor
                or actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER
            ):
                heroic_count += 1
        elif actor.faction == "monster":
            if actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN:
                notoriety_figures += 1
            if (
                actor.is_champion
                or actor.special_arrival_id == "calamity_invader"
                or actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN
            ):
                corrupted_count += 1

    var convergence_near: bool = _is_position_near_active_convergence(center, MARKED_ZONE_RADIUS * 1.9)
    var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    var gate_pressure: bool = false
    if bool(gate_runtime.get("active", false)):
        var gate_name: String = str(gate_runtime.get("poi", "rift_gate"))
        var gate_position: Vector3 = _get_poi_position_by_name(gate_name)
        gate_pressure = gate_position.distance_to(center) <= MARKED_ZONE_RADIUS * 1.9

    return {
        "heroic_count": heroic_count,
        "successor_count": successor_count,
        "renown_figures": renown_figures,
        "corrupted_count": corrupted_count,
        "notoriety_figures": notoriety_figures,
        "gate_pressure": gate_pressure,
        "convergence_near": convergence_near
    }


func _is_position_near_active_convergence(center: Vector3, max_distance: float) -> bool:
    for runtime_variant in _convergence_runtime_by_id.values():
        var runtime: Dictionary = runtime_variant
        var convergence_center: Vector3 = runtime.get("center", Vector3.ZERO)
        if convergence_center.distance_to(center) <= max_distance:
            return true
    return false


func _can_start_marked_zone_at(center: Vector3) -> bool:
    for runtime_variant in _marked_zone_runtime_by_id.values():
        var runtime: Dictionary = runtime_variant
        var other_center: Vector3 = runtime.get("center", Vector3.ZERO)
        var other_radius: float = float(runtime.get("radius", MARKED_ZONE_RADIUS))
        if other_center.distance_to(center) <= max(other_radius, MARKED_ZONE_RADIUS) * 0.82:
            return false
    return true


func _start_marked_zone(candidate: Dictionary) -> void:
    if candidate.is_empty():
        return
    var zone_id: int = _marked_zone_next_id
    _marked_zone_next_id += 1

    var duration: float = randf_range(
        min(MARKED_ZONE_DURATION_MIN, MARKED_ZONE_DURATION_MAX),
        max(MARKED_ZONE_DURATION_MIN, MARKED_ZONE_DURATION_MAX)
    )
    var center: Vector3 = candidate.get("center", Vector3.ZERO)
    var zone_type: String = str(candidate.get("zone_type", ""))
    var label: String = str(candidate.get("label", "zone"))
    var visual_node: Node3D = _spawn_marked_zone_signal(center, zone_type, zone_id)
    var source_site_id: int = int(candidate.get("source_site_id", 0))

    _marked_zone_runtime_by_id[zone_id] = {
        "id": zone_id,
        "zone_type": zone_type,
        "label": label,
        "center": center,
        "radius": float(candidate.get("radius", MARKED_ZONE_RADIUS)),
        "score": float(candidate.get("score", 1.0)),
        "source_site_id": source_site_id,
        "started_at": elapsed_time,
        "duration": duration,
        "ends_at": elapsed_time + duration,
        "next_pulse_at": elapsed_time + MARKED_ZONE_PULSE_INTERVAL,
        "visual_node": visual_node
    }

    marked_zone_started_total += 1
    _marked_zone_global_cooldown_left = MARKED_ZONE_GLOBAL_COOLDOWN
    _apply_marked_zone_pulse(_marked_zone_runtime_by_id[zone_id])
    if zone_type == "sanctified_zone":
        record_event("Zone SANCTIFIED: %s at %s (%.0fs)." % [label, _position_label_2d(center), duration])
    else:
        record_event("Zone CORRUPTED: %s at %s (%.0fs)." % [label, _position_label_2d(center), duration])


func _spawn_marked_zone_signal(center: Vector3, zone_type: String, zone_id: int) -> Node3D:
    if _marked_zone_signals_root == null or not is_instance_valid(_marked_zone_signals_root):
        return null

    var node := Node3D.new()
    node.name = "MarkedZone_%d" % zone_id
    node.position = center

    var colors := _marked_zone_colors(zone_type)

    var ring := MeshInstance3D.new()
    ring.name = "Ring"
    var ring_mesh := CylinderMesh.new()
    ring_mesh.top_radius = 2.25
    ring_mesh.bottom_radius = 2.25
    ring_mesh.height = 0.08
    ring.mesh = ring_mesh
    ring.position = Vector3(0.0, 0.11, 0.0)
    var ring_mat := StandardMaterial3D.new()
    ring_mat.albedo_color = colors.get("base", Color(0.9, 0.9, 0.9))
    ring_mat.emission_enabled = true
    ring_mat.emission = colors.get("base", Color(0.9, 0.9, 0.9)) * 1.06
    ring_mat.roughness = 0.68
    ring.material_override = ring_mat
    node.add_child(ring)

    var beacon := MeshInstance3D.new()
    beacon.name = "Beacon"
    var beacon_mesh := SphereMesh.new()
    beacon_mesh.radius = 0.22
    beacon_mesh.height = 0.44
    beacon.mesh = beacon_mesh
    beacon.position = Vector3(0.0, 1.10, 0.0)
    var beacon_mat := StandardMaterial3D.new()
    beacon_mat.albedo_color = colors.get("accent", Color(1.0, 1.0, 1.0))
    beacon_mat.emission_enabled = true
    beacon_mat.emission = colors.get("accent", Color(1.0, 1.0, 1.0)) * 1.16
    beacon_mat.roughness = 0.64
    beacon.material_override = beacon_mat
    node.add_child(beacon)

    node.scale = Vector3.ONE * 0.24
    _marked_zone_signals_root.add_child(node)
    var tween := create_tween()
    tween.tween_property(node, "scale", Vector3.ONE, 0.30)
    return node


func _animate_marked_zone_signal(node: Node3D, elapsed_ratio: float, zone_type: String) -> void:
    if node == null or not is_instance_valid(node):
        return
    var ring := node.get_node_or_null("Ring") as MeshInstance3D
    var beacon := node.get_node_or_null("Beacon") as MeshInstance3D
    var seed: float = float(node.get_instance_id() % 31)
    var colors := _marked_zone_colors(zone_type)

    if ring != null:
        var pulse := 1.0 + 0.08 * sin(elapsed_time * 4.0 + seed)
        var fade := lerpf(1.0, 0.70, elapsed_ratio)
        ring.scale = Vector3.ONE * pulse * fade
    if beacon != null:
        beacon.position.y = 1.10 + 0.09 * sin(elapsed_time * 3.0 + seed * 0.45)
        var beacon_mat := beacon.material_override as StandardMaterial3D
        if beacon_mat != null:
            var accent: Color = colors.get("accent", Color(1.0, 1.0, 1.0))
            beacon_mat.emission = accent * lerpf(1.16, 0.40, elapsed_ratio)


func _marked_zone_colors(zone_type: String) -> Dictionary:
    if zone_type == "sanctified_zone":
        return {
            "base": Color(0.52, 0.86, 1.0),
            "accent": Color(1.0, 0.92, 0.52)
        }
    return {
        "base": Color(0.96, 0.44, 0.42),
        "accent": Color(0.82, 0.46, 1.0)
    }


func _apply_marked_zone_pulse(runtime: Dictionary) -> void:
    var center: Vector3 = runtime.get("center", Vector3.ZERO)
    var radius: float = float(runtime.get("radius", MARKED_ZONE_RADIUS))
    var zone_type: String = str(runtime.get("zone_type", ""))
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(center) > radius:
            continue
        if zone_type == "sanctified_zone":
            if actor.faction != "human":
                continue
            actor.energy = min(actor.max_energy, actor.energy + SANCTIFIED_ZONE_ENERGY_PULSE)
            _apply_notability_gain(actor, SANCTIFIED_ZONE_RENOWN_PULSE, 0.0, "sanctified_zone")
        elif zone_type == "corrupted_zone":
            if actor.faction == "human":
                actor.energy = max(0.0, actor.energy - CORRUPTED_ZONE_ENERGY_DRAIN_PULSE)
            elif actor.faction == "monster":
                _apply_notability_gain(actor, 0.0, CORRUPTED_ZONE_NOTORIETY_PULSE, "corrupted_zone")


func _fade_marked_zone(zone_id: int, reason: String) -> void:
    var runtime: Dictionary = _marked_zone_runtime_by_id.get(zone_id, {})
    if runtime.is_empty():
        return

    var label: String = str(runtime.get("label", "zone"))
    var node := runtime.get("visual_node", null) as Node3D
    if node != null and is_instance_valid(node):
        node.queue_free()

    _marked_zone_runtime_by_id.erase(zone_id)
    marked_zone_faded_total += 1
    record_event("Zone FADED: %s (%s)." % [label, reason])


func _setup_allegiance_crisis_state() -> void:
    _allegiance_crisis_runtime_by_id.clear()
    _allegiance_crisis_cooldown_until_by_id.clear()
    _sync_allegiance_crisis_modifiers()


func _sync_allegiance_crisis_modifiers() -> void:
    var raid_modifiers: Dictionary = {}
    for allegiance_variant in _allegiance_crisis_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        if allegiance_id == "":
            continue
        raid_modifiers[allegiance_id] = ALLEGIANCE_CRISIS_RAID_WEIGHT_MULT
    world_manager.set_allegiance_crisis_raid_modifiers(raid_modifiers)


func _is_allegiance_anchor_active(allegiance_id: String) -> bool:
    if allegiance_id == "":
        return false
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    for allegiance in active_allegiances:
        if str(allegiance.get("allegiance_id", "")) == allegiance_id:
            return true
    return false


func _try_start_allegiance_crisis(
    allegiance_id: String,
    reason: String,
    chance_bonus: float = 0.0,
    duration_bonus: float = 0.0,
    source_label: String = ""
) -> bool:
    if allegiance_id == "":
        return false
    if _allegiance_crisis_runtime_by_id.has(allegiance_id):
        return false
    if _allegiance_recovery_runtime_by_id.has(allegiance_id):
        _end_allegiance_recovery(allegiance_id, "crisis_restart", true)
    if not _is_allegiance_anchor_active(allegiance_id):
        return false

    var cooldown_until: float = float(_allegiance_crisis_cooldown_until_by_id.get(allegiance_id, 0.0))
    if elapsed_time < cooldown_until:
        return false

    var faction: String = ""
    var doctrine: String = ""
    var home_poi: String = ""
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    for allegiance in active_allegiances:
        if str(allegiance.get("allegiance_id", "")) != allegiance_id:
            continue
        faction = str(allegiance.get("faction", ""))
        doctrine = str(allegiance.get("doctrine", ""))
        home_poi = str(allegiance.get("home_poi", ""))
        break
    if faction == "":
        return false

    var start_chance: float = ALLEGIANCE_CRISIS_START_CHANCE_BASE + chance_bonus
    if doctrine == "steadfast":
        start_chance -= 0.08
    elif doctrine == "warlike":
        start_chance += 0.05
    elif doctrine == "arcane":
        start_chance += 0.03
    start_chance = clampf(start_chance, 0.14, 0.82)
    if randf() > start_chance:
        return false

    var duration: float = randf_range(
        min(ALLEGIANCE_CRISIS_DURATION_MIN, ALLEGIANCE_CRISIS_DURATION_MAX),
        max(ALLEGIANCE_CRISIS_DURATION_MIN, ALLEGIANCE_CRISIS_DURATION_MAX)
    ) + duration_bonus
    if doctrine == "steadfast":
        duration -= 1.8
    elif doctrine == "arcane":
        duration += 1.0
    duration = clampf(duration, 12.0, 42.0)

    _allegiance_crisis_runtime_by_id[allegiance_id] = {
        "state": "crisis",
        "allegiance_id": allegiance_id,
        "faction": faction,
        "doctrine": doctrine,
        "home_poi": home_poi,
        "reason": reason,
        "source_label": source_label,
        "started_at": elapsed_time,
        "ends_at": elapsed_time + duration
    }
    crisis_started_total += 1
    _sync_allegiance_crisis_modifiers()
    var source_text: String = source_label if source_label != "" else allegiance_id
    record_event(
        "Crisis START: %s (%s, %.0fs, source=%s)."
        % [allegiance_id, reason, duration, source_text]
    )
    return true


func _is_crisis_notable_actor(actor: Actor, had_relic: bool = false) -> bool:
    if actor == null:
        return false
    if actor.is_champion or actor.is_special_arrival() or had_relic:
        return true
    if actor.renown >= ALLEGIANCE_CRISIS_RENOWN_TRIGGER:
        return true
    if actor.notoriety >= ALLEGIANCE_CRISIS_NOTORIETY_TRIGGER:
        return true
    return false


func _try_start_crisis_from_notable_fall(
    victim: Actor,
    reason: String,
    legacy_result: Dictionary,
    had_relic: bool
) -> void:
    if victim == null:
        return
    if victim.allegiance_id == "":
        return
    if not _is_crisis_notable_actor(victim, had_relic):
        return

    var chance_bonus: float = 0.06
    var duration_bonus: float = 0.0
    if victim.is_champion:
        chance_bonus += 0.16
        duration_bonus += 3.8
    if victim.is_special_arrival():
        chance_bonus += 0.12
        duration_bonus += 2.4
    if had_relic:
        chance_bonus += 0.10
        duration_bonus += 1.2
    if victim.renown >= ALLEGIANCE_CRISIS_RENOWN_TRIGGER:
        chance_bonus += 0.08
    if victim.notoriety >= ALLEGIANCE_CRISIS_NOTORIETY_TRIGGER:
        chance_bonus += 0.08
    if bool(legacy_result.get("triggered", false)):
        chance_bonus -= 0.10

    _try_start_allegiance_crisis(
        victim.allegiance_id,
        "leader_fall:%s" % reason,
        chance_bonus,
        duration_bonus,
        _actor_label(victim)
    )


func _try_start_crisis_from_project_interrupt(allegiance_id: String, project_id: String, reason: String) -> void:
    if allegiance_id == "":
        return
    var chance_bonus: float = 0.04
    var duration_bonus: float = 0.8
    if project_id == "ritual_focus":
        chance_bonus += 0.08
    elif project_id == "fortify":
        chance_bonus += 0.05
    if reason == "anchor_lost":
        chance_bonus += 0.10
        duration_bonus += 1.8
    _try_start_allegiance_crisis(
        allegiance_id,
        "project_interrupt:%s" % project_id,
        chance_bonus,
        duration_bonus,
        reason
    )


func _try_start_crisis_from_vendetta(source_allegiance_id: String, target_allegiance_id: String, reason: String) -> void:
    if source_allegiance_id == "":
        return
    var chance_bonus: float = 0.03
    var duration_bonus: float = 0.0
    if reason == "legacy_fall" or reason == "bounty_kill":
        chance_bonus += 0.12
        duration_bonus += 1.8
    _try_start_allegiance_crisis(
        source_allegiance_id,
        "vendetta:%s" % reason,
        chance_bonus,
        duration_bonus,
        target_allegiance_id
    )


func _try_start_crisis_from_bounty_pressure(target: Actor) -> void:
    if target == null or target.allegiance_id == "":
        return
    if not _is_crisis_notable_actor(target, target.has_relic()):
        return

    var chance_bonus: float = 0.02
    if target.is_champion:
        chance_bonus += 0.10
    if target.is_special_arrival():
        chance_bonus += 0.08
    if target.has_relic():
        chance_bonus += 0.06
    if target.renown >= ALLEGIANCE_CRISIS_RENOWN_TRIGGER:
        chance_bonus += 0.06
    if target.notoriety >= ALLEGIANCE_CRISIS_NOTORIETY_TRIGGER:
        chance_bonus += 0.06
    _try_start_allegiance_crisis(
        target.allegiance_id,
        "central_bounty",
        chance_bonus,
        0.0,
        _actor_label(target)
    )


func _try_resolve_allegiance_crisis(allegiance_id: String, reason: String) -> bool:
    if allegiance_id == "":
        return false
    if not _allegiance_crisis_runtime_by_id.has(allegiance_id):
        return false
    _end_allegiance_crisis(allegiance_id, "resolved", reason)
    return true


func _has_active_legacy_successor_for_allegiance(allegiance_id: String) -> bool:
    if allegiance_id == "":
        return false
    for actor_id_variant in _legacy_successor_runtime_by_actor.keys():
        var actor_id: int = int(actor_id_variant)
        var actor: Actor = _find_actor_by_id(actor_id)
        if actor == null or actor.is_dead:
            continue
        if actor.allegiance_id == allegiance_id:
            return true
    return false


func _update_allegiance_crisis_runtime(_delta: float) -> void:
    var cooldown_ids: Array = _allegiance_crisis_cooldown_until_by_id.keys()
    for allegiance_variant in cooldown_ids:
        var allegiance_id: String = str(allegiance_variant)
        var cooldown_until: float = float(_allegiance_crisis_cooldown_until_by_id.get(allegiance_id, 0.0))
        if elapsed_time >= cooldown_until:
            _allegiance_crisis_cooldown_until_by_id.erase(allegiance_id)

    if _allegiance_crisis_runtime_by_id.is_empty():
        _sync_allegiance_crisis_modifiers()
        return

    var to_resolve: Array[Dictionary] = []
    var to_expire: Array[Dictionary] = []
    for allegiance_variant in _allegiance_crisis_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        var runtime: Dictionary = _allegiance_crisis_runtime_by_id.get(allegiance_id, {})
        if runtime.is_empty():
            continue
        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        if not _is_allegiance_anchor_active(allegiance_id):
            to_expire.append({"allegiance_id": allegiance_id, "reason": "anchor_lost"})
            continue
        if elapsed_time >= ends_at:
            to_expire.append({"allegiance_id": allegiance_id, "reason": "duration_complete"})
            continue
        if _has_active_legacy_successor_for_allegiance(allegiance_id):
            to_resolve.append({"allegiance_id": allegiance_id, "reason": "successor_stabilized"})
            continue

        var faction: String = str(runtime.get("faction", ""))
        if faction == "human" and world_event_active_id == "sanctuary_calm" and randf() <= 0.018:
            to_resolve.append({"allegiance_id": allegiance_id, "reason": "world_event_calm"})
            continue
        if faction == "monster" and world_event_active_id == "monster_frenzy" and randf() <= 0.018:
            to_resolve.append({"allegiance_id": allegiance_id, "reason": "world_event_frenzy"})

    for entry in to_resolve:
        var allegiance_id: String = str(entry.get("allegiance_id", ""))
        var reason: String = str(entry.get("reason", "resolved"))
        if allegiance_id == "" or not _allegiance_crisis_runtime_by_id.has(allegiance_id):
            continue
        _end_allegiance_crisis(allegiance_id, "resolved", reason)

    for entry in to_expire:
        var allegiance_id: String = str(entry.get("allegiance_id", ""))
        var reason: String = str(entry.get("reason", "expired"))
        if allegiance_id == "" or not _allegiance_crisis_runtime_by_id.has(allegiance_id):
            continue
        _end_allegiance_crisis(allegiance_id, "expired", reason)

    _sync_allegiance_crisis_modifiers()


func _end_allegiance_crisis(allegiance_id: String, outcome: String, reason: String) -> void:
    var runtime: Dictionary = _allegiance_crisis_runtime_by_id.get(allegiance_id, {})
    if runtime.is_empty():
        return

    var should_seed_recovery: bool = outcome == "resolved"
    if outcome == "resolved":
        crisis_resolved_total += 1
        record_event("Crisis RESOLVED: %s (%s)." % [allegiance_id, reason])
    else:
        crisis_expired_total += 1
        record_event("Crisis EXPIRED: %s (%s)." % [allegiance_id, reason])

    crisis_ended_total += 1
    record_event("Crisis END: %s (%s)." % [allegiance_id, reason])
    _allegiance_crisis_runtime_by_id.erase(allegiance_id)
    _allegiance_crisis_cooldown_until_by_id[allegiance_id] = elapsed_time + ALLEGIANCE_CRISIS_COOLDOWN
    _sync_allegiance_crisis_modifiers()
    if should_seed_recovery:
        _try_start_allegiance_recovery(allegiance_id, "crisis_resolved", 0.24, 1.8, reason)


func _is_actor_in_allegiance_crisis(actor: Actor) -> bool:
    if actor == null:
        return false
    if actor.allegiance_id == "":
        return false
    return _allegiance_crisis_runtime_by_id.has(actor.allegiance_id)


func _setup_allegiance_recovery_state() -> void:
    _allegiance_recovery_runtime_by_id.clear()
    _allegiance_recovery_cooldown_until_by_id.clear()
    _recent_structure_loss_until_by_poi.clear()
    _sync_allegiance_recovery_modifiers()


func _sync_allegiance_recovery_modifiers() -> void:
    var defense_modifiers: Dictionary = {}
    for allegiance_variant in _allegiance_recovery_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        if allegiance_id == "":
            continue
        defense_modifiers[allegiance_id] = ALLEGIANCE_RECOVERY_DEFENSE_WEIGHT_DELTA
    world_manager.set_allegiance_recovery_defense_modifiers(defense_modifiers)


func _try_start_allegiance_recovery(
    allegiance_id: String,
    reason: String,
    chance_bonus: float = 0.0,
    duration_bonus: float = 0.0,
    source_label: String = ""
) -> bool:
    if allegiance_id == "":
        return false
    if _allegiance_recovery_runtime_by_id.has(allegiance_id):
        return false
    if _allegiance_crisis_runtime_by_id.has(allegiance_id):
        return false
    if not _is_allegiance_anchor_active(allegiance_id):
        return false

    var cooldown_until: float = float(_allegiance_recovery_cooldown_until_by_id.get(allegiance_id, 0.0))
    if elapsed_time < cooldown_until:
        return false

    var faction: String = ""
    var doctrine: String = ""
    var home_poi: String = ""
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    for allegiance in active_allegiances:
        if str(allegiance.get("allegiance_id", "")) != allegiance_id:
            continue
        faction = str(allegiance.get("faction", ""))
        doctrine = str(allegiance.get("doctrine", ""))
        home_poi = str(allegiance.get("home_poi", ""))
        break
    if faction == "":
        return false

    var start_chance: float = ALLEGIANCE_RECOVERY_START_CHANCE_BASE + chance_bonus
    if doctrine == "steadfast":
        start_chance += 0.06
    elif doctrine == "warlike":
        start_chance -= 0.03
    elif doctrine == "arcane":
        start_chance += 0.02
    start_chance = clampf(start_chance, 0.16, 0.86)
    if randf() > start_chance:
        return false

    var duration: float = randf_range(
        min(ALLEGIANCE_RECOVERY_DURATION_MIN, ALLEGIANCE_RECOVERY_DURATION_MAX),
        max(ALLEGIANCE_RECOVERY_DURATION_MIN, ALLEGIANCE_RECOVERY_DURATION_MAX)
    ) + duration_bonus
    if doctrine == "steadfast":
        duration += 1.2
    elif doctrine == "warlike":
        duration -= 0.8
    duration = clampf(duration, 8.0, 32.0)

    _allegiance_recovery_runtime_by_id[allegiance_id] = {
        "state": "recovery",
        "allegiance_id": allegiance_id,
        "faction": faction,
        "doctrine": doctrine,
        "home_poi": home_poi,
        "reason": reason,
        "source_label": source_label,
        "started_at": elapsed_time,
        "ends_at": elapsed_time + duration
    }
    recovery_started_total += 1
    _sync_allegiance_recovery_modifiers()
    var source_text: String = source_label if source_label != "" else allegiance_id
    record_event(
        "Recovery START: %s (%s, %.0fs, source=%s)."
        % [allegiance_id, reason, duration, source_text]
    )
    return true


func _update_allegiance_recovery_runtime(_delta: float) -> void:
    var cooldown_ids: Array = _allegiance_recovery_cooldown_until_by_id.keys()
    for allegiance_variant in cooldown_ids:
        var allegiance_id: String = str(allegiance_variant)
        var cooldown_until: float = float(_allegiance_recovery_cooldown_until_by_id.get(allegiance_id, 0.0))
        if elapsed_time >= cooldown_until:
            _allegiance_recovery_cooldown_until_by_id.erase(allegiance_id)

    var poi_ids: Array = _recent_structure_loss_until_by_poi.keys()
    for poi_variant in poi_ids:
        var poi_name: String = str(poi_variant)
        var until_time: float = float(_recent_structure_loss_until_by_poi.get(poi_name, 0.0))
        if elapsed_time >= until_time:
            _recent_structure_loss_until_by_poi.erase(poi_name)

    if _allegiance_recovery_runtime_by_id.is_empty():
        _sync_allegiance_recovery_modifiers()
        return

    var to_end: Array[Dictionary] = []
    for allegiance_variant in _allegiance_recovery_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        var runtime: Dictionary = _allegiance_recovery_runtime_by_id.get(allegiance_id, {})
        if runtime.is_empty():
            continue
        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        if not _is_allegiance_anchor_active(allegiance_id):
            to_end.append({"allegiance_id": allegiance_id, "reason": "anchor_lost", "interrupted": true})
            continue
        if _allegiance_crisis_runtime_by_id.has(allegiance_id):
            to_end.append({"allegiance_id": allegiance_id, "reason": "crisis_restart", "interrupted": true})
            continue
        if elapsed_time >= ends_at:
            to_end.append({"allegiance_id": allegiance_id, "reason": "duration_complete", "interrupted": false})

    for entry in to_end:
        var allegiance_id: String = str(entry.get("allegiance_id", ""))
        var reason: String = str(entry.get("reason", "ended"))
        var interrupted: bool = bool(entry.get("interrupted", false))
        if allegiance_id == "" or not _allegiance_recovery_runtime_by_id.has(allegiance_id):
            continue
        _end_allegiance_recovery(allegiance_id, reason, interrupted)

    _sync_allegiance_recovery_modifiers()


func _end_allegiance_recovery(allegiance_id: String, reason: String, interrupted: bool = false) -> void:
    var runtime: Dictionary = _allegiance_recovery_runtime_by_id.get(allegiance_id, {})
    if runtime.is_empty():
        return

    var should_seed_bond: bool = not interrupted
    if interrupted:
        recovery_interrupted_total += 1
        record_event("Recovery INTERRUPTED: %s (%s)." % [allegiance_id, reason])
    recovery_ended_total += 1
    record_event("Recovery END: %s (%s)." % [allegiance_id, reason])
    _allegiance_recovery_runtime_by_id.erase(allegiance_id)
    _allegiance_recovery_cooldown_until_by_id[allegiance_id] = elapsed_time + ALLEGIANCE_RECOVERY_COOLDOWN
    _sync_allegiance_recovery_modifiers()
    if should_seed_bond:
        _try_start_bond_from_recovery(allegiance_id, reason)


func _is_actor_in_allegiance_recovery(actor: Actor) -> bool:
    if actor == null:
        return false
    if actor.allegiance_id == "":
        return false
    return _allegiance_recovery_runtime_by_id.has(actor.allegiance_id)


func _setup_memorial_scar_sites_root() -> void:
    if _memorial_scar_sites_root != null and is_instance_valid(_memorial_scar_sites_root):
        _memorial_scar_sites_root.queue_free()

    _memorial_scar_sites_root = Node3D.new()
    _memorial_scar_sites_root.name = "MemorialScarSites"
    world_manager.add_child(_memorial_scar_sites_root)
    _memorial_scar_runtime.clear()
    _memorial_scar_next_id = 1


func _memorial_scar_trigger_kind(victim: Actor, legacy_result: Dictionary, had_relic: bool) -> String:
    if victim == null:
        return ""
    if bool(legacy_result.get("triggered", false)):
        return "legacy_trigger"
    if victim.is_champion:
        return "champion"
    if victim.is_special_arrival():
        return "special_arrival"
    if had_relic:
        return "relic_carrier"
    if victim.renown >= MEMORIAL_SCAR_RENOWN_TRIGGER:
        return "high_renown"
    if victim.notoriety >= MEMORIAL_SCAR_NOTORIETY_TRIGGER:
        return "high_notoriety"
    return ""


func _memorial_scar_site_type_for(victim: Actor) -> String:
    if victim == null:
        return ""
    if victim.faction == "human":
        return "memorial_site"
    if victim.special_arrival_id == "calamity_invader" or victim.special_arrival_id == "rift_gate_breach":
        return "scar_site"
    if victim.faction == "monster":
        return "scar_site"
    return "scar_site"


func _try_spawn_memorial_scar_site(
    victim: Actor,
    _killer: Actor,
    _reason: String,
    legacy_result: Dictionary,
    had_relic: bool
) -> void:
    if victim == null:
        return
    var trigger_kind: String = _memorial_scar_trigger_kind(victim, legacy_result, had_relic)
    if trigger_kind == "":
        return

    var site_type: String = _memorial_scar_site_type_for(victim)
    if site_type == "":
        return
    if _memorial_scar_sites_root == null or not is_instance_valid(_memorial_scar_sites_root):
        _setup_memorial_scar_sites_root()

    _trim_memorial_scar_capacity()
    if _memorial_scar_runtime.size() >= MEMORIAL_SCAR_MAX_ACTIVE:
        return

    var site_id: int = _memorial_scar_next_id
    _memorial_scar_next_id += 1

    var position: Vector3 = world_manager.clamp_to_world(world_manager.snap_to_nav_grid(victim.global_position))
    var duration: float = randf_range(
        min(MEMORIAL_SCAR_DURATION_MIN, MEMORIAL_SCAR_DURATION_MAX),
        max(MEMORIAL_SCAR_DURATION_MIN, MEMORIAL_SCAR_DURATION_MAX)
    )
    var ends_at: float = elapsed_time + duration
    var source_label: String = _actor_label(victim)
    var source_short := "%s#%d" % [victim.actor_kind, victim.actor_id]
    var visual_node: Node3D = _spawn_memorial_scar_visual(site_type, position, site_id)

    _memorial_scar_runtime[site_id] = {
        "id": site_id,
        "type": site_type,
        "faction": victim.faction,
        "position": position,
        "radius": MEMORIAL_SCAR_RADIUS,
        "source_label": source_label,
        "source_short": source_short,
        "trigger_kind": trigger_kind,
        "created_at": elapsed_time,
        "duration": duration,
        "ends_at": ends_at,
        "next_pulse_at": elapsed_time + MEMORIAL_SCAR_PULSE_INTERVAL,
        "label": "%s:%s" % [_memorial_scar_type_short(site_type), source_short],
        "visual_node": visual_node
    }
    memorial_scar_born_total += 1
    record_event(
        "Memorial/Scar BORN: %s at %s from %s (%s, %.0fs)."
        % [site_type, _position_label_2d(position), source_label, trigger_kind, duration]
    )


func _trim_memorial_scar_capacity() -> void:
    while _memorial_scar_runtime.size() >= MEMORIAL_SCAR_MAX_ACTIVE:
        var oldest_id: int = 0
        var oldest_end: float = INF
        for site_id_variant in _memorial_scar_runtime.keys():
            var site_id: int = int(site_id_variant)
            var runtime: Dictionary = _memorial_scar_runtime.get(site_id, {})
            var ends_at: float = float(runtime.get("ends_at", elapsed_time))
            if ends_at < oldest_end:
                oldest_end = ends_at
                oldest_id = site_id
        if oldest_id == 0:
            return
        _fade_memorial_scar_site(oldest_id, "cap")


func _spawn_memorial_scar_visual(site_type: String, position: Vector3, site_id: int) -> Node3D:
    if _memorial_scar_sites_root == null:
        return null

    var colors: Dictionary = _memorial_scar_colors(site_type)
    var base_color: Color = colors.get("base", Color(0.82, 0.82, 0.82))
    var accent_color: Color = colors.get("accent", Color(0.95, 0.95, 0.95))

    var site_node := Node3D.new()
    site_node.name = "Site_%d" % site_id
    site_node.position = position

    var ring := MeshInstance3D.new()
    ring.name = "Ring"
    var ring_mesh := CylinderMesh.new()
    ring_mesh.top_radius = 1.85 if site_type == "memorial_site" else 2.05
    ring_mesh.bottom_radius = ring_mesh.top_radius
    ring_mesh.height = 0.08
    ring.mesh = ring_mesh
    ring.position = Vector3(0.0, 0.05, 0.0)
    ring.material_override = _make_memorial_scar_material(base_color, 0.74)
    site_node.add_child(ring)

    var pillar := MeshInstance3D.new()
    pillar.name = "Pillar"
    var pillar_mesh := BoxMesh.new()
    pillar_mesh.size = Vector3(0.24, 1.1, 0.24)
    pillar.mesh = pillar_mesh
    pillar.position = Vector3(0.0, 0.60, 0.0)
    pillar.material_override = _make_memorial_scar_material(base_color.darkened(0.16), 0.52)
    site_node.add_child(pillar)

    var beacon := MeshInstance3D.new()
    beacon.name = "Beacon"
    var beacon_mesh := SphereMesh.new()
    beacon_mesh.radius = 0.24
    beacon_mesh.height = 0.48
    beacon.mesh = beacon_mesh
    beacon.position = Vector3(0.0, 1.2, 0.0)
    beacon.material_override = _make_memorial_scar_material(accent_color, 1.08)
    site_node.add_child(beacon)

    _memorial_scar_sites_root.add_child(site_node)
    site_node.scale = Vector3.ONE * 0.24
    var tween := create_tween()
    tween.tween_property(site_node, "scale", Vector3.ONE, 0.34)
    return site_node


func _make_memorial_scar_material(color: Color, emission_strength: float) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.roughness = 0.68
    material.emission_enabled = true
    material.emission = color * emission_strength
    return material


func _update_memorial_scar_runtime(_delta: float) -> void:
    if _memorial_scar_runtime.is_empty():
        return

    var faded_ids: Array[int] = []
    for site_id_variant in _memorial_scar_runtime.keys():
        var site_id: int = int(site_id_variant)
        var runtime: Dictionary = _memorial_scar_runtime.get(site_id, {})
        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        var duration: float = max(0.01, float(runtime.get("duration", MEMORIAL_SCAR_DURATION_MIN)))
        var remaining: float = max(0.0, ends_at - elapsed_time)
        var elapsed_ratio: float = clampf(1.0 - (remaining / duration), 0.0, 1.0)

        var site_node := runtime.get("visual_node", null) as Node3D
        if site_node != null and is_instance_valid(site_node):
            _animate_memorial_scar_visual(site_node, str(runtime.get("type", "")), elapsed_ratio)

        if elapsed_time >= ends_at:
            faded_ids.append(site_id)
            continue

        var next_pulse_at: float = float(runtime.get("next_pulse_at", elapsed_time))
        if elapsed_time < next_pulse_at:
            continue
        runtime["next_pulse_at"] = elapsed_time + MEMORIAL_SCAR_PULSE_INTERVAL
        _memorial_scar_runtime[site_id] = runtime
        _apply_memorial_scar_pulse(runtime)

    for site_id in faded_ids:
        _fade_memorial_scar_site(site_id, "duration")


func _apply_memorial_scar_pulse(runtime: Dictionary) -> void:
    var site_type: String = str(runtime.get("type", ""))
    var center: Vector3 = runtime.get("position", Vector3.ZERO)
    var radius: float = float(runtime.get("radius", MEMORIAL_SCAR_RADIUS))
    var site_faction: String = str(runtime.get("faction", ""))
    if site_type == "" or radius <= 0.0:
        return

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.global_position.distance_to(center) > radius:
            continue

        if site_type == "memorial_site":
            if actor.faction != site_faction:
                continue
            _apply_notability_gain(actor, MEMORIAL_SITE_RENOWN_PULSE, 0.0, "memorial_site")
        elif site_type == "scar_site":
            if actor.faction == site_faction:
                continue
            _apply_notability_gain(actor, 0.0, SCAR_SITE_NOTORIETY_PULSE, "scar_site")


func _fade_memorial_scar_site(site_id: int, reason: String) -> void:
    var runtime: Dictionary = _memorial_scar_runtime.get(site_id, {})
    if runtime.is_empty():
        return

    var label: String = str(runtime.get("label", "site"))
    record_event("Memorial/Scar FADED: %s (%s)." % [label, reason])
    memorial_scar_faded_total += 1

    var site_node := runtime.get("visual_node", null) as Node3D
    if site_node != null and is_instance_valid(site_node):
        site_node.queue_free()
    _memorial_scar_runtime.erase(site_id)


func _animate_memorial_scar_visual(site_node: Node3D, site_type: String, elapsed_ratio: float) -> void:
    var ring := site_node.get_node_or_null("Ring") as MeshInstance3D
    var beacon := site_node.get_node_or_null("Beacon") as MeshInstance3D
    var pulse_speed: float = 4.2 if site_type == "memorial_site" else 6.2
    var instance_seed: float = float(site_node.get_instance_id() % 17)

    if ring != null:
        var pulse: float = 1.0 + 0.08 * sin((elapsed_time * pulse_speed) + instance_seed)
        var fade_scale: float = lerpf(1.0, 0.72, elapsed_ratio)
        ring.scale = Vector3.ONE * pulse * fade_scale

    if beacon != null:
        var float_speed: float = 2.9 if site_type == "memorial_site" else 4.0
        beacon.position.y = 1.2 + 0.08 * sin((elapsed_time * float_speed) + instance_seed * 0.6)
        var material := beacon.material_override as StandardMaterial3D
        if material != null:
            var colors: Dictionary = _memorial_scar_colors(site_type)
            var accent: Color = colors.get("accent", Color(0.9, 0.9, 0.9))
            material.emission = accent * lerpf(1.08, 0.42, elapsed_ratio)


func _memorial_scar_colors(site_type: String) -> Dictionary:
    if site_type == "memorial_site":
        return {
            "base": Color(0.56, 0.82, 1.0),
            "accent": Color(1.0, 0.88, 0.40)
        }
    return {
        "base": Color(1.0, 0.44, 0.38),
        "accent": Color(0.82, 0.42, 1.0)
    }


func _memorial_scar_type_short(site_type: String) -> String:
    return "M" if site_type == "memorial_site" else "S"


func _position_label_2d(position: Vector3) -> String:
    return "(%.1f, %.1f)" % [position.x, position.z]


func record_event(message: String) -> void:
    event_log.append("[%05d] %s" % [tick_index, message])
    while event_log.size() > MAX_EVENT_LOG:
        event_log.remove_at(0)


func get_magic_modifiers(_caster: Actor) -> Dictionary:
    var damage_mult: float = float(world_event_modifiers.get("magic_damage_mult", 1.0))
    var energy_cost_mult: float = float(world_event_modifiers.get("magic_energy_cost_mult", 1.0))
    if _caster != null and _caster.allegiance_id != "":
        var doctrine_modifiers: Dictionary = world_manager.get_allegiance_doctrine_modifiers(_caster.allegiance_id)
        damage_mult *= float(doctrine_modifiers.get("magic_damage_mult", 1.0))
        energy_cost_mult *= float(doctrine_modifiers.get("magic_energy_cost_mult", 1.0))
        var project_modifiers: Dictionary = world_manager.get_allegiance_project_modifiers(_caster.allegiance_id)
        damage_mult *= float(project_modifiers.get("magic_damage_mult", 1.0))
        energy_cost_mult *= float(project_modifiers.get("magic_energy_cost_mult", 1.0))
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


func _has_poi_named(poi_name: String) -> bool:
    if poi_name == "":
        return false
    for poi in world_manager.pois:
        if str(poi.get("name", "")) == poi_name:
            return true
    return false


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
    var arrival_renown_gain: float = RENOWN_GAIN_ON_SPECIAL_ARRIVAL
    var arrival_notoriety_gain: float = NOTORIETY_GAIN_ON_SPECIAL_ARRIVAL
    if variant_id == "summoned_hero":
        arrival_notoriety_gain *= 0.72
    elif variant_id == "calamity_invader":
        arrival_notoriety_gain *= 1.12
    _apply_notability_gain(
        actor,
        arrival_renown_gain,
        arrival_notoriety_gain,
        "special_arrival:%s" % variant_id
    )

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
    _apply_notability_gain(holder, RENOWN_GAIN_ON_RELIC, NOTORIETY_GAIN_ON_RELIC, "relic:%s" % relic_id)
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


func _spawn_neutral_gate_breach(transition: Dictionary) -> Actor:
    var poi_name: String = str(transition.get("poi", "rift_gate"))
    var gate_position: Vector3 = transition.get("position", _get_poi_position_by_name(poi_name))
    if gate_position == Vector3.ZERO:
        gate_position = _get_poi_position_by_name("rift_gate")

    var breach := RangedMonster.new()
    var jitter := Vector3(randf_range(-1.8, 1.8), 0.0, randf_range(-1.8, 1.8))
    breach.global_position = world_manager.clamp_to_world(world_manager.snap_to_nav_grid(gate_position + jitter))
    breach.set_special_arrival("rift_gate_breach", "Rift Breacher")
    breach.apply_special_arrival_bonus("rift_gate_breach")

    entities_root.add_child(breach)
    actors.append(breach)
    register_spawn(breach)
    _apply_notability_gain(
        breach,
        RENOWN_GAIN_ON_SPECIAL_ARRIVAL * 0.48,
        NOTORIETY_GAIN_ON_SPECIAL_ARRIVAL * 0.62,
        "gate_breach"
    )

    if not bounty_active:
        _bounty_cooldown_left = min(_bounty_cooldown_left, NEUTRAL_GATE_BREACH_BOUNTY_COOLDOWN_CLAMP)
        _bounty_check_timer = max(_bounty_check_timer, BOUNTY_CHECK_INTERVAL)

    return breach


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
    var source_allegiance_id: String = str(source.get("allegiance_id", ""))
    var target: Actor = _pick_bounty_target(source_faction, source_position, source_allegiance_id)
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


func _pick_bounty_target(source_faction: String, source_position: Vector3, source_allegiance_id: String = "") -> Actor:
    var selected: Actor = null
    var best_priority: int = 0
    var best_distance: float = INF
    var vendetta_target_allegiance_id: String = ""
    if source_allegiance_id != "":
        vendetta_target_allegiance_id = world_manager.get_allegiance_vendetta_target(source_allegiance_id)

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction == source_faction:
            continue

        var priority: int = _bounty_priority(actor)
        if priority > 0 and vendetta_target_allegiance_id != "" and actor.allegiance_id == vendetta_target_allegiance_id:
            priority += 1
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
    var priority: int = 0
    if actor.notoriety >= 72.0:
        priority = max(priority, 3)
    elif actor.notoriety >= 52.0:
        priority = max(priority, 2)
    elif actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN:
        priority = max(priority, 1)
    if actor.has_relic():
        priority = max(priority, 3)
    if actor.is_special_arrival():
        priority = max(priority, 2)
    if actor.is_champion:
        priority = max(priority, 1)
    return priority


func _start_bounty(source: Dictionary, target: Actor) -> void:
    if target == null or target.is_dead:
        return

    bounty_active = true
    bounty_target_actor_id = target.actor_id
    bounty_target_faction = target.faction
    bounty_target_allegiance_id = target.allegiance_id
    bounty_source_faction = str(source.get("faction", ""))
    bounty_source_allegiance_id = str(source.get("allegiance_id", ""))
    bounty_source_poi = str(source.get("home_poi", ""))
    bounty_target_position = target.global_position
    bounty_remaining = BOUNTY_DURATION
    bounty_started_total += 1
    _bounty_cooldown_left = BOUNTY_COOLDOWN

    target.set_bounty_marked(true)
    _apply_notability_gain(
        target,
        RENOWN_GAIN_ON_BOUNTY_MARK,
        NOTORIETY_GAIN_ON_BOUNTY_MARK,
        "bounty_marked"
    )
    _try_start_crisis_from_bounty_pressure(target)
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
    if victim.allegiance_id != "" and bounty_source_allegiance_id != "" and victim.allegiance_id != bounty_source_allegiance_id:
        var vendetta_event: Dictionary = world_manager.register_vendetta_incident(
            victim.allegiance_id,
            bounty_source_allegiance_id,
            "bounty_kill",
            elapsed_time
        )
        if not vendetta_event.is_empty():
            _handle_vendetta_transition(vendetta_event)
    if killer != null and not killer.is_dead:
        _apply_notability_gain(
            killer,
            RENOWN_GAIN_ON_BOUNTY_CLEAR_KILL,
            NOTORIETY_GAIN_ON_BOUNTY_CLEAR_KILL,
            "bounty_clear_kill"
        )
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
    bounty_target_allegiance_id = ""
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
        bounty_target_faction,
        bounty_target_allegiance_id
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
    if actor.notoriety >= 52.0:
        return "high_notoriety"
    if actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN:
        return "notoriety"
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


func _update_destiny_pulls(delta: float) -> void:
    _destiny_global_cooldown_left = max(0.0, _destiny_global_cooldown_left - delta)
    _destiny_check_timer += delta

    if not _destiny_runtime_by_actor.is_empty():
        var runtime_ids: Array = _destiny_runtime_by_actor.keys()
        for actor_id_variant in runtime_ids:
            var actor_id: int = int(actor_id_variant)
            var runtime: Dictionary = _destiny_runtime_by_actor.get(actor_id, {})
            if runtime.is_empty():
                continue

            var actor: Actor = _find_actor_by_id(actor_id)
            if actor == null or actor.is_dead:
                _end_destiny_pull(actor_id, "interrupted", "actor_unavailable")
                continue

            var refreshed: Dictionary = _refresh_destiny_runtime_target(runtime, actor)
            if not bool(refreshed.get("valid", false)):
                _end_destiny_pull(actor_id, "interrupted", str(refreshed.get("reason", "context_lost")))
                continue

            var target_position: Vector3 = refreshed.get("target_position", actor.global_position)
            var target_label: String = str(refreshed.get("target_label", str(runtime.get("target_label", "target"))))
            runtime["target_position"] = target_position
            runtime["target_label"] = target_label
            runtime["target_actor_id"] = int(refreshed.get("target_actor_id", int(runtime.get("target_actor_id", 0))))
            runtime["target_poi"] = str(refreshed.get("target_poi", str(runtime.get("target_poi", ""))))
            runtime["target_allegiance_id"] = str(
                refreshed.get("target_allegiance_id", str(runtime.get("target_allegiance_id", "")))
            )

            var distance: float = actor.global_position.distance_to(target_position)
            var near_time: float = float(runtime.get("near_time", 0.0))
            if distance <= DESTINY_FULFILL_RADIUS:
                near_time += delta
                actor.energy = min(actor.max_energy, actor.energy + DESTINY_NEAR_ENERGY_BONUS_PER_SEC * delta)
            else:
                near_time = max(0.0, near_time - delta * 0.40)
            runtime["near_time"] = near_time

            actor.set_destiny_pull(
                true,
                str(runtime.get("type", "")),
                target_position,
                int(runtime.get("target_actor_id", 0)),
                target_label,
                float(runtime.get("guidance_weight", 0.56))
            )
            _destiny_runtime_by_actor[actor_id] = runtime

            if near_time >= DESTINY_FULFILL_HOLD:
                _end_destiny_pull(actor_id, "fulfilled", "near_objective")
                continue

            var ends_at: float = float(runtime.get("ends_at", elapsed_time))
            if elapsed_time >= ends_at:
                _end_destiny_pull(actor_id, "ended", "timeout")

    if _destiny_check_timer < DESTINY_CHECK_INTERVAL:
        return
    _destiny_check_timer = 0.0

    if _destiny_global_cooldown_left > 0.0:
        return
    if _count_alive_actors() < DESTINY_MIN_POPULATION:
        return
    if _destiny_runtime_by_actor.size() >= DESTINY_MAX_ACTIVE:
        return
    if randf() > DESTINY_TRIGGER_CHANCE:
        return

    var picked: Dictionary = _pick_destiny_start_candidate()
    if picked.is_empty():
        return
    var actor: Actor = picked.get("actor", null)
    var option: Dictionary = picked.get("option", {})
    if actor == null or actor.is_dead or option.is_empty():
        return
    _start_destiny_pull(actor, option)


func _pick_destiny_start_candidate() -> Dictionary:
    var weighted_candidates: Array[Dictionary] = []
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if _destiny_runtime_by_actor.has(actor.actor_id):
            continue
        if not _is_destiny_candidate(actor):
            continue

        var actor_cooldown_until: float = float(_destiny_cooldown_until_by_actor.get(actor.actor_id, 0.0))
        if actor_cooldown_until > elapsed_time:
            continue

        var actor_options: Array[Dictionary] = _collect_destiny_options(actor)
        if actor_options.is_empty():
            continue
        var selected_option: Dictionary = _pick_weighted_entry(actor_options)
        if selected_option.is_empty():
            continue

        var start_score: float = max(0.10, float(selected_option.get("score", 1.0)) + _destiny_candidate_bias(actor))
        weighted_candidates.append({
            "actor_id": actor.actor_id,
            "option": selected_option,
            "score": start_score
        })

    if weighted_candidates.is_empty():
        return {}

    var selected: Dictionary = _pick_weighted_entry(weighted_candidates)
    if selected.is_empty():
        return {}
    var selected_actor: Actor = _find_actor_by_id(int(selected.get("actor_id", 0)))
    if selected_actor == null or selected_actor.is_dead:
        return {}
    return {
        "actor": selected_actor,
        "option": selected.get("option", {})
    }


func _is_destiny_candidate(actor: Actor) -> bool:
    if actor == null or actor.is_dead:
        return false
    if actor.bounty_marked:
        return false
    if actor.is_champion or actor.is_special_arrival() or actor.has_relic():
        return true
    if _legacy_successor_runtime_by_actor.has(actor.actor_id):
        return true
    return actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER


func _destiny_candidate_bias(actor: Actor) -> float:
    if actor == null:
        return 0.0
    var bias: float = 0.0
    if actor.is_champion:
        bias += 0.95
    if actor.is_special_arrival():
        bias += 1.20
    if actor.has_relic():
        bias += 1.35
    if _legacy_successor_runtime_by_actor.has(actor.actor_id):
        bias += 1.05
    if actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER:
        bias += 0.75
    return bias


func _collect_destiny_options(actor: Actor) -> Array[Dictionary]:
    var options: Array[Dictionary] = []
    if actor == null or actor.is_dead:
        return options

    var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    if bool(gate_runtime.get("active", false)):
        var gate_name: String = str(gate_runtime.get("poi", "rift_gate"))
        var gate_position: Vector3 = _get_poi_position_by_name(gate_name)
        if gate_position != Vector3.ZERO:
            var gate_distance: float = actor.global_position.distance_to(gate_position)
            var gate_max_distance: float = DESTINY_TARGET_MAX_DISTANCE * 1.15
            if gate_distance <= gate_max_distance:
                var gate_closeness: float = clampf((gate_max_distance - gate_distance) / gate_max_distance, 0.0, 1.0)
                var gate_score: float = 1.0 + gate_closeness * 0.9
                if actor.is_champion or actor.is_special_arrival():
                    gate_score += 0.45
                if actor.has_relic():
                    gate_score += 0.25
                var gate_jitter := Vector3(randf_range(-1.4, 1.4), 0.0, randf_range(-1.4, 1.4))
                options.append({
                    "type": "rift_call",
                    "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(gate_position + gate_jitter)),
                    "target_poi": gate_name,
                    "target_label": gate_name if gate_name != "" else "rift_gate",
                    "guidance_weight": 0.62,
                    "score": gate_score
                })

    var relic_target: Actor = _pick_destiny_relic_target(actor)
    if relic_target != null:
        var relic_distance: float = actor.global_position.distance_to(relic_target.global_position)
        var relic_max_distance: float = DESTINY_TARGET_MAX_DISTANCE * 1.10
        if relic_distance <= relic_max_distance:
            var relic_closeness: float = clampf((relic_max_distance - relic_distance) / relic_max_distance, 0.0, 1.0)
            var relic_score: float = 1.10 + relic_closeness * 1.00
            if relic_target.faction != actor.faction:
                relic_score += 0.24
            var relic_jitter := Vector3(randf_range(-1.2, 1.2), 0.0, randf_range(-1.2, 1.2))
            options.append({
                "type": "relic_call",
                "target_actor_id": relic_target.actor_id,
                "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(relic_target.global_position + relic_jitter)),
                "target_label": _actor_label(relic_target),
                "guidance_weight": 0.58,
                "score": relic_score
            })

    if actor.allegiance_id != "":
        var vendetta_target_id: String = world_manager.get_allegiance_vendetta_target(actor.allegiance_id)
        if vendetta_target_id != "":
            var target_anchor: Dictionary = _find_active_allegiance_anchor(vendetta_target_id)
            if not target_anchor.is_empty():
                var target_position: Vector3 = target_anchor.get("position", actor.global_position)
                var vendetta_distance: float = actor.global_position.distance_to(target_position)
                var vendetta_max_distance: float = DESTINY_TARGET_MAX_DISTANCE * 1.25
                if vendetta_distance <= vendetta_max_distance:
                    var vendetta_closeness: float = clampf((vendetta_max_distance - vendetta_distance) / vendetta_max_distance, 0.0, 1.0)
                    var vendetta_score: float = 1.15 + vendetta_closeness * 0.95
                    if _legacy_successor_runtime_by_actor.has(actor.actor_id):
                        vendetta_score += 0.42
                    var target_poi: String = str(target_anchor.get("home_poi", ""))
                    var target_label: String = vendetta_target_id if target_poi == "" else ("%s@%s" % [vendetta_target_id, target_poi])
                    var vendetta_jitter := Vector3(randf_range(-1.4, 1.4), 0.0, randf_range(-1.4, 1.4))
                    options.append({
                        "type": "vendetta_call",
                        "target_allegiance_id": vendetta_target_id,
                        "target_poi": target_poi,
                        "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(target_position + vendetta_jitter)),
                        "target_label": target_label,
                        "guidance_weight": 0.64,
                        "score": vendetta_score
                    })

    return options


func _pick_destiny_relic_target(actor: Actor) -> Actor:
    if actor == null:
        return null
    var selected: Actor = null
    var best_score: float = -INF
    var max_distance: float = DESTINY_TARGET_MAX_DISTANCE * 1.10
    for other in actors:
        if other == null or other == actor or other.is_dead:
            continue
        if not other.has_relic():
            continue
        var distance: float = actor.global_position.distance_to(other.global_position)
        if distance > max_distance:
            continue
        var closeness: float = clampf((max_distance - distance) / max_distance, 0.0, 1.0)
        var score: float = 0.80 + closeness * 0.90
        if other.faction != actor.faction:
            score += 0.30
        if other.relic_id == "arcane_sigil":
            score += 0.12
        elif other.relic_id == "oath_standard":
            score += 0.16
        if score > best_score:
            best_score = score
            selected = other
    return selected


func _find_active_allegiance_anchor(allegiance_id: String) -> Dictionary:
    if allegiance_id == "":
        return {}
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    for allegiance in active_allegiances:
        if str(allegiance.get("allegiance_id", "")) == allegiance_id:
            return allegiance
    return {}


func _pick_weighted_entry(entries: Array[Dictionary]) -> Dictionary:
    if entries.is_empty():
        return {}
    var total_weight: float = 0.0
    for entry in entries:
        total_weight += max(0.01, float(entry.get("score", 1.0)))
    if total_weight <= 0.0:
        return entries[0]
    var roll: float = randf() * total_weight
    var cursor: float = 0.0
    for entry in entries:
        cursor += max(0.01, float(entry.get("score", 1.0)))
        if roll <= cursor:
            return entry
    return entries[entries.size() - 1]


func _start_destiny_pull(actor: Actor, option: Dictionary) -> void:
    if actor == null or actor.is_dead:
        return
    var destiny_type: String = str(option.get("type", ""))
    if destiny_type == "":
        return
    var duration: float = randf_range(
        min(DESTINY_DURATION_MIN, DESTINY_DURATION_MAX),
        max(DESTINY_DURATION_MIN, DESTINY_DURATION_MAX)
    )
    var ends_at: float = elapsed_time + duration
    var target_position: Vector3 = option.get("target_position", actor.global_position)
    var target_label: String = str(option.get("target_label", "target"))
    var guidance_weight: float = float(option.get("guidance_weight", 0.56))
    var runtime := {
        "type": destiny_type,
        "started_at": elapsed_time,
        "ends_at": ends_at,
        "target_position": target_position,
        "target_actor_id": int(option.get("target_actor_id", 0)),
        "target_poi": str(option.get("target_poi", "")),
        "target_allegiance_id": str(option.get("target_allegiance_id", "")),
        "target_label": target_label,
        "guidance_weight": guidance_weight,
        "near_time": 0.0
    }
    _destiny_runtime_by_actor[actor.actor_id] = runtime
    actor.set_destiny_pull(
        true,
        destiny_type,
        target_position,
        int(runtime.get("target_actor_id", 0)),
        target_label,
        guidance_weight
    )
    destiny_started_total += 1
    _destiny_global_cooldown_left = DESTINY_GLOBAL_COOLDOWN
    record_event(
        "Destiny START: %s -> %s (%s, %.0fs)."
        % [ _actor_label(actor), target_label, _destiny_type_label(destiny_type), duration ]
    )


func _refresh_destiny_runtime_target(runtime: Dictionary, actor: Actor) -> Dictionary:
    var destiny_type: String = str(runtime.get("type", ""))
    if destiny_type == "rift_call":
        var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
        if not bool(gate_runtime.get("active", false)):
            return {
                "valid": false,
                "reason": "gate_closed"
            }
        var gate_name: String = str(gate_runtime.get("poi", str(runtime.get("target_poi", "rift_gate"))))
        var gate_position: Vector3 = _get_poi_position_by_name(gate_name)
        if gate_position == Vector3.ZERO:
            return {
                "valid": false,
                "reason": "gate_missing"
            }
        var gate_jitter := Vector3(randf_range(-1.3, 1.3), 0.0, randf_range(-1.3, 1.3))
        return {
            "valid": true,
            "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(gate_position + gate_jitter)),
            "target_poi": gate_name,
            "target_label": gate_name if gate_name != "" else "rift_gate",
            "target_actor_id": 0,
            "target_allegiance_id": ""
        }

    if destiny_type == "relic_call":
        var target_actor_id: int = int(runtime.get("target_actor_id", 0))
        var target_actor: Actor = _find_actor_by_id(target_actor_id)
        if target_actor == null or target_actor.is_dead or not target_actor.has_relic():
            return {
                "valid": false,
                "reason": "relic_target_lost"
            }
        var relic_jitter := Vector3(randf_range(-1.1, 1.1), 0.0, randf_range(-1.1, 1.1))
        return {
            "valid": true,
            "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(target_actor.global_position + relic_jitter)),
            "target_label": _actor_label(target_actor),
            "target_actor_id": target_actor.actor_id,
            "target_poi": "",
            "target_allegiance_id": ""
        }

    if destiny_type == "vendetta_call":
        var source_allegiance_id: String = actor.allegiance_id
        if source_allegiance_id == "":
            return {
                "valid": false,
                "reason": "source_allegiance_lost"
            }
        var target_allegiance_id: String = world_manager.get_allegiance_vendetta_target(source_allegiance_id)
        if target_allegiance_id == "":
            return {
                "valid": false,
                "reason": "vendetta_resolved"
            }
        var target_anchor: Dictionary = _find_active_allegiance_anchor(target_allegiance_id)
        if target_anchor.is_empty():
            return {
                "valid": false,
                "reason": "vendetta_anchor_lost"
            }
        var target_position: Vector3 = target_anchor.get("position", actor.global_position)
        if target_position == Vector3.ZERO:
            return {
                "valid": false,
                "reason": "vendetta_anchor_missing"
            }
        var target_poi: String = str(target_anchor.get("home_poi", ""))
        var target_label: String = target_allegiance_id if target_poi == "" else ("%s@%s" % [target_allegiance_id, target_poi])
        var vendetta_jitter := Vector3(randf_range(-1.3, 1.3), 0.0, randf_range(-1.3, 1.3))
        return {
            "valid": true,
            "target_position": world_manager.clamp_to_world(world_manager.snap_to_nav_grid(target_position + vendetta_jitter)),
            "target_label": target_label,
            "target_actor_id": 0,
            "target_poi": target_poi,
            "target_allegiance_id": target_allegiance_id
        }

    return {
        "valid": false,
        "reason": "unknown_type"
    }


func _end_destiny_pull(actor_id: int, outcome: String, reason: String) -> void:
    var runtime: Dictionary = _destiny_runtime_by_actor.get(actor_id, {})
    if runtime.is_empty():
        return
    var actor: Actor = _find_actor_by_id(actor_id)
    if actor != null:
        actor.set_destiny_pull(false)
    var label: String = _actor_label(actor) if actor != null else ("actor#%d" % actor_id)
    var destiny_type: String = str(runtime.get("type", ""))
    var target_label: String = str(runtime.get("target_label", "target"))
    if outcome == "fulfilled":
        destiny_fulfilled_total += 1
        record_event(
            "Destiny FULFILLED: %s reached %s (%s)."
            % [label, target_label, _destiny_type_label(destiny_type)]
        )
    elif outcome == "interrupted":
        destiny_interrupted_total += 1
        record_event(
            "Destiny INTERRUPTED: %s (%s, %s)."
            % [label, _destiny_type_label(destiny_type), reason]
        )

    destiny_ended_total += 1
    record_event(
        "Destiny END: %s (%s)."
        % [label, reason]
    )
    _destiny_runtime_by_actor.erase(actor_id)
    _destiny_cooldown_until_by_actor[actor_id] = elapsed_time + DESTINY_ACTOR_COOLDOWN


func _destiny_type_label(destiny_type: String) -> String:
    match destiny_type:
        "rift_call":
            return "rift_call"
        "relic_call":
            return "relic_call"
        "vendetta_call":
            return "vendetta_call"
        _:
            return "destiny"


func _destiny_type_short(destiny_type: String) -> String:
    match destiny_type:
        "rift_call":
            return "gate"
        "relic_call":
            return "relic"
        "vendetta_call":
            return "vendetta"
        _:
            return "destiny"


func _setup_rivalry_state() -> void:
    _rivalry_check_timer = 0.0
    _rivalry_global_cooldown_left = RIVALRY_START_DELAY
    _rivalry_runtime_by_id.clear()
    _rivalry_next_id = 1
    _rivalry_id_by_actor.clear()
    _rivalry_cooldown_until_by_actor.clear()
    _rivalry_engagement_by_pair.clear()


func _update_rivalries(delta: float) -> void:
    _rivalry_global_cooldown_left = max(0.0, _rivalry_global_cooldown_left - delta)
    _rivalry_check_timer += delta
    _prune_rivalry_engagements()

    if not _rivalry_runtime_by_id.is_empty():
        var rivalry_ids: Array = _rivalry_runtime_by_id.keys()
        for rivalry_id_variant in rivalry_ids:
            var rivalry_id: int = int(rivalry_id_variant)
            var runtime: Dictionary = _rivalry_runtime_by_id.get(rivalry_id, {})
            if runtime.is_empty():
                continue
            _update_active_rivalry(rivalry_id, runtime, delta)

    if _rivalry_check_timer < RIVALRY_CHECK_INTERVAL:
        return
    _rivalry_check_timer = 0.0

    if _rivalry_global_cooldown_left > 0.0:
        return
    if _count_alive_actors() < RIVALRY_MIN_POPULATION:
        return
    if _rivalry_runtime_by_id.size() >= RIVALRY_MAX_ACTIVE:
        return
    if randf() > RIVALRY_TRIGGER_CHANCE:
        return
    _attempt_start_rivalry()


func _prune_rivalry_engagements() -> void:
    if _rivalry_engagement_by_pair.is_empty():
        return
    var stale_keys: Array[String] = []
    for pair_key_variant in _rivalry_engagement_by_pair.keys():
        var pair_key: String = str(pair_key_variant)
        var entry: Dictionary = _rivalry_engagement_by_pair.get(pair_key, {})
        var last_at: float = float(entry.get("last_at", -INF))
        if elapsed_time - last_at > RIVALRY_ENGAGEMENT_WINDOW:
            stale_keys.append(pair_key)
    for pair_key in stale_keys:
        _rivalry_engagement_by_pair.erase(pair_key)


func _attempt_start_rivalry() -> void:
    var candidate: Dictionary = _pick_rivalry_candidate()
    if candidate.is_empty():
        return
    _start_rivalry(candidate)


func _pick_rivalry_candidate() -> Dictionary:
    var selected: Dictionary = {}
    var best_score: float = -INF
    var stale_keys: Array[String] = []

    for pair_key_variant in _rivalry_engagement_by_pair.keys():
        var pair_key: String = str(pair_key_variant)
        var entry: Dictionary = _rivalry_engagement_by_pair.get(pair_key, {})
        if entry.is_empty():
            stale_keys.append(pair_key)
            continue
        if elapsed_time - float(entry.get("last_at", -INF)) > RIVALRY_ENGAGEMENT_WINDOW:
            stale_keys.append(pair_key)
            continue

        var ids: PackedInt32Array = _rivalry_pair_ids(pair_key)
        if ids.size() != 2:
            stale_keys.append(pair_key)
            continue
        var actor_a: Actor = _find_actor_by_id(ids[0])
        var actor_b: Actor = _find_actor_by_id(ids[1])
        if actor_a == null or actor_b == null or actor_a.is_dead or actor_b.is_dead:
            stale_keys.append(pair_key)
            continue
        if actor_a.faction == actor_b.faction:
            continue
        if _rivalry_id_by_actor.has(actor_a.actor_id) or _rivalry_id_by_actor.has(actor_b.actor_id):
            continue
        if not _is_rivalry_actor_ready(actor_a) or not _is_rivalry_actor_ready(actor_b):
            continue
        if not _is_rivalry_notable_actor(actor_a) or not _is_rivalry_notable_actor(actor_b):
            continue

        var base_score: float = float(entry.get("score", 0.0))
        if base_score < RIVALRY_MIN_ENGAGEMENT_SCORE:
            continue

        var scored: Dictionary = _score_rivalry_candidate(actor_a, actor_b, base_score)
        var score: float = float(scored.get("score", base_score))
        if score <= best_score:
            continue

        best_score = score
        selected = {
            "pair_key": pair_key,
            "actor_a_id": actor_a.actor_id,
            "actor_b_id": actor_b.actor_id,
            "score": score,
            "context": str(scored.get("context", "engagement"))
        }

    for pair_key in stale_keys:
        _rivalry_engagement_by_pair.erase(pair_key)
    return selected


func _score_rivalry_candidate(actor_a: Actor, actor_b: Actor, base_score: float) -> Dictionary:
    var score: float = base_score
    var context_parts: Array[String] = ["engagement"]
    if bounty_active and (actor_a.actor_id == bounty_target_actor_id or actor_b.actor_id == bounty_target_actor_id):
        score += 0.92
        context_parts.append("bounty")
    if _is_rivalry_vendetta_pair(actor_a, actor_b):
        score += 0.88
        context_parts.append("vendetta")
    if actor_a.destiny_active or actor_b.destiny_active:
        score += 0.22
        context_parts.append("destiny")
    if _legacy_successor_runtime_by_actor.has(actor_a.actor_id) or _legacy_successor_runtime_by_actor.has(actor_b.actor_id):
        score += 0.18
        context_parts.append("legacy")

    var center: Vector3 = (actor_a.global_position + actor_b.global_position) * 0.5
    if _is_position_near_active_convergence(center, CONVERGENCE_RADIUS * 1.60):
        score += 0.28
        context_parts.append("convergence")

    var gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    if bool(gate_runtime.get("active", false)):
        var gate_name: String = str(gate_runtime.get("poi", "rift_gate"))
        var gate_position: Vector3 = _get_poi_position_by_name(gate_name)
        if gate_position.distance_to(center) <= CONVERGENCE_RADIUS * 2.10:
            score += 0.24
            context_parts.append("gate")

    return {
        "score": score,
        "context": "+".join(context_parts)
    }


func _is_rivalry_actor_ready(actor: Actor) -> bool:
    if actor == null or actor.is_dead:
        return false
    if _rivalry_id_by_actor.has(actor.actor_id):
        return false
    var cooldown_until: float = float(_rivalry_cooldown_until_by_actor.get(actor.actor_id, 0.0))
    return elapsed_time >= cooldown_until


func _is_rivalry_notable_actor(actor: Actor) -> bool:
    if actor == null or actor.is_dead:
        return false
    if actor.is_champion or actor.is_special_arrival() or actor.has_relic():
        return true
    if actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER:
        return true
    if actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN:
        return true
    return false


func _is_rivalry_vendetta_pair(actor_a: Actor, actor_b: Actor) -> bool:
    if actor_a == null or actor_b == null:
        return false
    if actor_a.allegiance_id == "" or actor_b.allegiance_id == "":
        return false
    var a_target: String = world_manager.get_allegiance_vendetta_target(actor_a.allegiance_id)
    var b_target: String = world_manager.get_allegiance_vendetta_target(actor_b.allegiance_id)
    if a_target != "" and a_target == actor_b.allegiance_id:
        return true
    if b_target != "" and b_target == actor_a.allegiance_id:
        return true
    return false


func _start_rivalry(candidate: Dictionary) -> void:
    if candidate.is_empty():
        return
    var actor_a: Actor = _find_actor_by_id(int(candidate.get("actor_a_id", 0)))
    var actor_b: Actor = _find_actor_by_id(int(candidate.get("actor_b_id", 0)))
    if actor_a == null or actor_b == null or actor_a.is_dead or actor_b.is_dead:
        return
    if actor_a.faction == actor_b.faction:
        return
    if _rivalry_id_by_actor.has(actor_a.actor_id) or _rivalry_id_by_actor.has(actor_b.actor_id):
        return

    var rivalry_id: int = _rivalry_next_id
    _rivalry_next_id += 1
    var duration: float = randf_range(
        min(RIVALRY_DURATION_MIN, RIVALRY_DURATION_MAX),
        max(RIVALRY_DURATION_MIN, RIVALRY_DURATION_MAX)
    )
    var label: String = "%s<->%s" % [_actor_label(actor_a), _actor_label(actor_b)]
    var runtime := {
        "id": rivalry_id,
        "actor_a_id": actor_a.actor_id,
        "actor_b_id": actor_b.actor_id,
        "label": label,
        "context": str(candidate.get("context", "engagement")),
        "score": float(candidate.get("score", 0.0)),
        "started_at": elapsed_time,
        "ends_at": elapsed_time + duration,
        "duel_active": false,
        "duel_hold": 0.0,
        "duel_ends_at": 0.0
    }
    _rivalry_runtime_by_id[rivalry_id] = runtime
    _rivalry_id_by_actor[actor_a.actor_id] = rivalry_id
    _rivalry_id_by_actor[actor_b.actor_id] = rivalry_id
    actor_a.set_rivalry_state(true, actor_b.actor_id, _actor_label(actor_b), RIVALRY_BASE_FOCUS_WEIGHT, false)
    actor_b.set_rivalry_state(true, actor_a.actor_id, _actor_label(actor_a), RIVALRY_BASE_FOCUS_WEIGHT, false)

    var pair_key: String = str(candidate.get("pair_key", ""))
    if pair_key != "" and _rivalry_engagement_by_pair.has(pair_key):
        var damped: Dictionary = _rivalry_engagement_by_pair.get(pair_key, {}).duplicate()
        damped["score"] = max(0.0, float(damped.get("score", 0.0)) * 0.48)
        damped["last_at"] = elapsed_time
        _rivalry_engagement_by_pair[pair_key] = damped

    rivalry_started_total += 1
    _rivalry_global_cooldown_left = RIVALRY_GLOBAL_COOLDOWN
    record_event(
        "Rivalry START: %s (%s, %.0fs)."
        % [label, str(runtime.get("context", "engagement")), duration]
    )


func _update_active_rivalry(rivalry_id: int, runtime: Dictionary, delta: float) -> void:
    var actor_a_id: int = int(runtime.get("actor_a_id", 0))
    var actor_b_id: int = int(runtime.get("actor_b_id", 0))
    var actor_a: Actor = _find_actor_by_id(actor_a_id)
    var actor_b: Actor = _find_actor_by_id(actor_b_id)
    if actor_a == null or actor_b == null or actor_a.is_dead or actor_b.is_dead:
        _end_rivalry(rivalry_id, "ended", "actor_unavailable")
        return
    if actor_a.faction == actor_b.faction:
        _end_rivalry(rivalry_id, "ended", "hostility_lost")
        return

    var distance: float = actor_a.global_position.distance_to(actor_b.global_position)
    var duel_active: bool = bool(runtime.get("duel_active", false))
    if duel_active:
        var duel_ends_at: float = float(runtime.get("duel_ends_at", elapsed_time))
        if elapsed_time >= duel_ends_at or distance > RIVALRY_DUEL_RANGE * 1.90:
            _end_rivalry_duel(rivalry_id, runtime, "distance_or_timeout")
            runtime = _rivalry_runtime_by_id.get(rivalry_id, {})
            if runtime.is_empty():
                return
    else:
        var duel_hold: float = float(runtime.get("duel_hold", 0.0))
        if distance <= RIVALRY_DUEL_RANGE:
            duel_hold += delta
        else:
            duel_hold = max(0.0, duel_hold - delta * 0.45)
        runtime["duel_hold"] = duel_hold
        _rivalry_runtime_by_id[rivalry_id] = runtime

        if duel_hold >= RIVALRY_DUEL_HOLD:
            _try_start_rivalry_duel(rivalry_id, runtime, actor_a, actor_b)
            runtime = _rivalry_runtime_by_id.get(rivalry_id, {})
            if runtime.is_empty():
                return

    var ends_at: float = float(runtime.get("ends_at", elapsed_time))
    if elapsed_time >= ends_at:
        _end_rivalry(rivalry_id, "expired", "timeout")


func _try_start_rivalry_duel(rivalry_id: int, runtime: Dictionary, actor_a: Actor, actor_b: Actor) -> void:
    if actor_a == null or actor_b == null:
        return
    if randf() > RIVALRY_DUEL_START_CHANCE:
        runtime["duel_hold"] = 0.0
        _rivalry_runtime_by_id[rivalry_id] = runtime
        return

    var duel_duration: float = randf_range(
        min(RIVALRY_DUEL_DURATION_MIN, RIVALRY_DUEL_DURATION_MAX),
        max(RIVALRY_DUEL_DURATION_MIN, RIVALRY_DUEL_DURATION_MAX)
    )
    runtime["duel_active"] = true
    runtime["duel_hold"] = 0.0
    runtime["duel_ends_at"] = elapsed_time + duel_duration
    _rivalry_runtime_by_id[rivalry_id] = runtime

    actor_a.set_rivalry_state(true, actor_b.actor_id, _actor_label(actor_b), RIVALRY_DUEL_FOCUS_WEIGHT, true)
    actor_b.set_rivalry_state(true, actor_a.actor_id, _actor_label(actor_a), RIVALRY_DUEL_FOCUS_WEIGHT, true)
    _apply_notability_gain(actor_a, RIVALRY_DUEL_RENOWN_PULSE, RIVALRY_DUEL_NOTORIETY_PULSE, "duel_start")
    _apply_notability_gain(actor_b, RIVALRY_DUEL_RENOWN_PULSE, RIVALRY_DUEL_NOTORIETY_PULSE, "duel_start")
    duel_started_total += 1
    record_event(
        "Duel START: %s (%.0fs)."
        % [str(runtime.get("label", "rivals")), duel_duration]
    )


func _end_rivalry_duel(rivalry_id: int, runtime: Dictionary, _reason: String) -> void:
    if runtime.is_empty():
        return
    var actor_a: Actor = _find_actor_by_id(int(runtime.get("actor_a_id", 0)))
    var actor_b: Actor = _find_actor_by_id(int(runtime.get("actor_b_id", 0)))
    runtime["duel_active"] = false
    runtime["duel_hold"] = 0.0
    runtime["duel_ends_at"] = 0.0
    _rivalry_runtime_by_id[rivalry_id] = runtime
    if actor_a != null and not actor_a.is_dead:
        actor_a.set_rivalry_state(true, int(runtime.get("actor_b_id", 0)), _actor_label(actor_b), RIVALRY_BASE_FOCUS_WEIGHT, false)
    if actor_b != null and not actor_b.is_dead:
        actor_b.set_rivalry_state(true, int(runtime.get("actor_a_id", 0)), _actor_label(actor_a), RIVALRY_BASE_FOCUS_WEIGHT, false)


func _end_rivalry(rivalry_id: int, outcome: String, reason: String) -> void:
    var runtime: Dictionary = _rivalry_runtime_by_id.get(rivalry_id, {})
    if runtime.is_empty():
        return

    var actor_a_id: int = int(runtime.get("actor_a_id", 0))
    var actor_b_id: int = int(runtime.get("actor_b_id", 0))
    var actor_a: Actor = _find_actor_by_id(actor_a_id)
    var actor_b: Actor = _find_actor_by_id(actor_b_id)
    var label: String = str(runtime.get("label", "rivals"))

    if outcome == "resolved":
        rivalry_resolved_total += 1
        record_event("Rivalry RESOLVED: %s (%s)." % [label, reason])
    elif outcome == "expired":
        rivalry_expired_total += 1
        record_event("Rivalry EXPIRED: %s (%s)." % [label, reason])

    rivalry_ended_total += 1
    record_event("Rivalry END: %s (%s)." % [label, reason])

    if actor_a != null:
        actor_a.set_rivalry_state(false)
        _rivalry_cooldown_until_by_actor[actor_a_id] = elapsed_time + RIVALRY_ACTOR_COOLDOWN
    if actor_b != null:
        actor_b.set_rivalry_state(false)
        _rivalry_cooldown_until_by_actor[actor_b_id] = elapsed_time + RIVALRY_ACTOR_COOLDOWN

    _rivalry_id_by_actor.erase(actor_a_id)
    _rivalry_id_by_actor.erase(actor_b_id)
    _rivalry_runtime_by_id.erase(rivalry_id)


func _record_rivalry_engagement(attacker: Actor, target: Actor, kind: String) -> void:
    if attacker == null or target == null:
        return
    if attacker.is_dead or target.is_dead:
        return
    if attacker.faction == target.faction:
        return

    var pair_key: String = _rivalry_pair_key(attacker.actor_id, target.actor_id)
    var runtime: Dictionary = _rivalry_engagement_by_pair.get(pair_key, {
        "score": 0.0,
        "last_at": elapsed_time,
        "a_id": min(attacker.actor_id, target.actor_id),
        "b_id": max(attacker.actor_id, target.actor_id)
    })

    var score: float = float(runtime.get("score", 0.0))
    if kind == "magic":
        score += 1.12
    else:
        score += 1.00
    if attacker.is_special_arrival() or target.is_special_arrival():
        score += 0.12
    if attacker.has_relic() or target.has_relic():
        score += 0.10
    if attacker.bounty_marked or target.bounty_marked:
        score += 0.14
    if attacker.destiny_active or target.destiny_active:
        score += 0.08

    runtime["score"] = min(score, RIVALRY_MIN_ENGAGEMENT_SCORE * 4.2)
    runtime["last_at"] = elapsed_time
    _rivalry_engagement_by_pair[pair_key] = runtime


func _rivalry_pair_key(actor_a_id: int, actor_b_id: int) -> String:
    var first_id: int = min(actor_a_id, actor_b_id)
    var second_id: int = max(actor_a_id, actor_b_id)
    return "%d:%d" % [first_id, second_id]


func _rivalry_pair_ids(pair_key: String) -> PackedInt32Array:
    var parts: PackedStringArray = pair_key.split(":")
    if parts.size() != 2:
        return PackedInt32Array()
    var first_id: int = int(parts[0])
    var second_id: int = int(parts[1])
    return PackedInt32Array([first_id, second_id])


func _clear_actor_rivalry_tracking(actor_id: int) -> void:
    var rivalry_id: int = int(_rivalry_id_by_actor.get(actor_id, 0))
    if rivalry_id != 0 and _rivalry_runtime_by_id.has(rivalry_id):
        _end_rivalry(rivalry_id, "ended", "actor_removed")
    _rivalry_id_by_actor.erase(actor_id)
    _rivalry_cooldown_until_by_actor.erase(actor_id)
    var to_remove: Array[String] = []
    for pair_key_variant in _rivalry_engagement_by_pair.keys():
        var pair_key: String = str(pair_key_variant)
        if pair_key.begins_with("%d:" % actor_id) or pair_key.ends_with(":%d" % actor_id):
            to_remove.append(pair_key)
    for pair_key in to_remove:
        _rivalry_engagement_by_pair.erase(pair_key)


func _handle_rivalry_death(victim: Actor, killer: Actor) -> void:
    if victim == null:
        return
    var rivalry_id: int = int(_rivalry_id_by_actor.get(victim.actor_id, 0))
    if rivalry_id == 0:
        return
    var runtime: Dictionary = _rivalry_runtime_by_id.get(rivalry_id, {})
    if runtime.is_empty():
        return
    var actor_a_id: int = int(runtime.get("actor_a_id", 0))
    var actor_b_id: int = int(runtime.get("actor_b_id", 0))
    var rival_id: int = actor_b_id if victim.actor_id == actor_a_id else actor_a_id
    if killer != null and killer.actor_id == rival_id:
        _end_rivalry(rivalry_id, "resolved", "rival_fall")
        return
    _end_rivalry(rivalry_id, "ended", "actor_fallen")


func _setup_bond_state() -> void:
    _bond_global_cooldown_left = BOND_START_DELAY
    _bond_runtime_by_id.clear()
    _bond_next_id = 1
    _bond_id_by_patron.clear()
    _bond_cooldown_until_by_actor.clear()


func _update_bonds(delta: float) -> void:
    _bond_global_cooldown_left = max(0.0, _bond_global_cooldown_left - delta)
    if _bond_runtime_by_id.is_empty():
        return

    var bond_ids: Array = _bond_runtime_by_id.keys()
    for bond_id_variant in bond_ids:
        var bond_id: int = int(bond_id_variant)
        var runtime: Dictionary = _bond_runtime_by_id.get(bond_id, {})
        if runtime.is_empty():
            continue
        _update_active_bond(bond_id, runtime, delta)


func _update_active_bond(bond_id: int, runtime: Dictionary, delta: float) -> void:
    var patron_id: int = int(runtime.get("patron_actor_id", 0))
    var patron: Actor = _find_actor_by_id(patron_id)
    if patron == null or patron.is_dead:
        _break_bond(bond_id, "patron_fallen")
        return

    var allegiance_id: String = str(runtime.get("allegiance_id", ""))
    if allegiance_id != "":
        if patron.allegiance_id != allegiance_id:
            _break_bond(bond_id, "allegiance_shift")
            return
        if not _is_allegiance_anchor_active(allegiance_id):
            _break_bond(bond_id, "anchor_lost")
            return

    var ends_at: float = float(runtime.get("ends_at", elapsed_time))
    if elapsed_time >= ends_at:
        _end_bond(bond_id, "duration")
        return

    _apply_bond_effects(runtime, patron, delta)


func _apply_bond_effects(runtime: Dictionary, patron: Actor, delta: float) -> void:
    if patron == null or patron.is_dead:
        return
    var allegiance_id: String = str(runtime.get("allegiance_id", ""))
    var radius: float = float(runtime.get("radius", BOND_RADIUS))
    var nearby_allies: Array[Actor] = []

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction != patron.faction:
            continue
        if allegiance_id != "" and actor.allegiance_id != allegiance_id:
            continue
        if actor.global_position.distance_to(patron.global_position) > radius:
            continue
        nearby_allies.append(actor)

        if actor == patron:
            continue
        if actor.rally_leader_id != patron.actor_id:
            continue
        if actor.rally_bonus_active:
            continue
        var bonus_chance: float = clampf(BOND_RALLY_BONUS_CHANCE_PER_SEC * delta, 0.0, 0.44)
        if randf() <= bonus_chance:
            actor.rally_bonus_active = true

    var next_pulse_at: float = float(runtime.get("next_pulse_at", elapsed_time))
    if elapsed_time < next_pulse_at:
        return

    _apply_notability_gain(patron, BOND_SHARED_RENOWN_PULSE, 0.0, "bond_patron")
    var shared_slots: int = 2
    for actor in nearby_allies:
        if actor == patron:
            continue
        if actor.rally_leader_id != patron.actor_id:
            continue
        _apply_notability_gain(actor, BOND_SHARED_RENOWN_PULSE * 0.72, 0.0, "bond_shared")
        shared_slots -= 1
        if shared_slots <= 0:
            break

    runtime["next_pulse_at"] = elapsed_time + BOND_PULSE_INTERVAL
    _bond_runtime_by_id[int(runtime.get("id", 0))] = runtime


func _is_bond_candidate(actor: Actor) -> bool:
    if actor == null or actor.is_dead:
        return false
    if actor.is_champion or actor.is_special_arrival() or actor.has_relic():
        return true
    if _legacy_successor_runtime_by_actor.has(actor.actor_id):
        return true
    return actor.renown >= DESTINY_HIGH_RENOWN_TRIGGER


func _count_active_bonds_for_allegiance(allegiance_id: String) -> int:
    if allegiance_id == "":
        return 0
    var total: int = 0
    for runtime_variant in _bond_runtime_by_id.values():
        var runtime: Dictionary = runtime_variant
        if str(runtime.get("allegiance_id", "")) == allegiance_id:
            total += 1
    return total


func _try_start_bond(
    patron: Actor,
    allegiance_id: String,
    reason: String,
    trigger_chance: float,
    target_label: String = ""
) -> bool:
    if patron == null or patron.is_dead:
        return false
    if _count_alive_actors() < BOND_MIN_POPULATION:
        return false
    if _bond_runtime_by_id.size() >= BOND_MAX_ACTIVE:
        return false
    if _bond_global_cooldown_left > 0.0:
        return false
    if not _is_bond_candidate(patron):
        return false
    if _bond_id_by_patron.has(patron.actor_id):
        return false
    var actor_cooldown_until: float = float(_bond_cooldown_until_by_actor.get(patron.actor_id, 0.0))
    if elapsed_time < actor_cooldown_until:
        return false
    if allegiance_id != "" and _count_active_bonds_for_allegiance(allegiance_id) >= BOND_MAX_PER_ALLEGIANCE:
        return false
    if randf() > clampf(trigger_chance, 0.06, 0.80):
        return false

    var bond_id: int = _bond_next_id
    _bond_next_id += 1
    var duration: float = randf_range(
        min(BOND_DURATION_MIN, BOND_DURATION_MAX),
        max(BOND_DURATION_MIN, BOND_DURATION_MAX)
    )
    var group_label: String = target_label if target_label != "" else (
        allegiance_id if allegiance_id != "" else patron.faction
    )
    var label: String = "%s->%s" % [_actor_label(patron), group_label]
    _bond_runtime_by_id[bond_id] = {
        "id": bond_id,
        "patron_actor_id": patron.actor_id,
        "patron_label": _actor_label(patron),
        "allegiance_id": allegiance_id,
        "group_label": group_label,
        "label": label,
        "reason": reason,
        "radius": BOND_RADIUS,
        "started_at": elapsed_time,
        "ends_at": elapsed_time + duration,
        "next_pulse_at": elapsed_time + BOND_PULSE_INTERVAL
    }
    _bond_id_by_patron[patron.actor_id] = bond_id
    _bond_cooldown_until_by_actor[patron.actor_id] = elapsed_time + BOND_ACTOR_COOLDOWN
    patron.set_bond_state(true, label)
    bond_started_total += 1
    _bond_global_cooldown_left = BOND_GLOBAL_COOLDOWN
    record_event(
        "Bond START: %s (%s, %.0fs)."
        % [label, reason, duration]
    )
    return true


func _end_bond(bond_id: int, reason: String) -> void:
    var runtime: Dictionary = _bond_runtime_by_id.get(bond_id, {})
    if runtime.is_empty():
        return
    var patron_id: int = int(runtime.get("patron_actor_id", 0))
    var patron: Actor = _find_actor_by_id(patron_id)
    if patron != null:
        patron.set_bond_state(false)
    _bond_id_by_patron.erase(patron_id)
    _bond_runtime_by_id.erase(bond_id)
    bond_ended_total += 1
    record_event("Bond END: %s (%s)." % [str(runtime.get("label", "bond")), reason])


func _break_bond(bond_id: int, reason: String) -> void:
    var runtime: Dictionary = _bond_runtime_by_id.get(bond_id, {})
    if runtime.is_empty():
        return
    bond_broken_total += 1
    record_event("Bond BROKEN: %s (%s)." % [str(runtime.get("label", "bond")), reason])
    _end_bond(bond_id, reason)


func _clear_actor_bond_tracking(actor_id: int) -> void:
    var bond_id: int = int(_bond_id_by_patron.get(actor_id, 0))
    if bond_id != 0 and _bond_runtime_by_id.has(bond_id):
        _break_bond(bond_id, "patron_removed")
    _bond_id_by_patron.erase(actor_id)
    _bond_cooldown_until_by_actor.erase(actor_id)


func _try_start_bond_from_legacy(successor: Actor, source_label: String) -> void:
    if successor == null or successor.is_dead:
        return
    var allegiance_id: String = successor.allegiance_id
    var reason: String = "legacy:%s" % source_label
    _try_start_bond(successor, allegiance_id, reason, BOND_LEGACY_TRIGGER_CHANCE, allegiance_id)


func _try_start_bond_from_recovery(allegiance_id: String, source_reason: String) -> void:
    if allegiance_id == "":
        return
    var patron: Actor = _pick_bond_patron_for_allegiance(allegiance_id)
    if patron == null:
        return
    _try_start_bond(
        patron,
        allegiance_id,
        "recovery:%s" % source_reason,
        BOND_RECOVERY_TRIGGER_CHANCE,
        allegiance_id
    )


func _pick_bond_patron_for_allegiance(allegiance_id: String) -> Actor:
    var selected: Actor = null
    var best_score: float = -INF
    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.allegiance_id != allegiance_id:
            continue
        if not _is_bond_candidate(actor):
            continue
        var score: float = actor.renown * 0.04 + actor.notoriety * 0.02
        if actor.is_champion:
            score += 2.2
        if actor.is_special_arrival():
            score += 1.5
        if actor.has_relic():
            score += 1.3
        if _legacy_successor_runtime_by_actor.has(actor.actor_id):
            score += 1.8
        score += float(_prev_rally_leader_counts.get(actor.actor_id, 0)) * 0.36
        if score > best_score:
            best_score = score
            selected = actor
    return selected


func _try_start_bond_from_rally(leader: Actor, follower_count: int) -> void:
    if leader == null or leader.is_dead:
        return
    if follower_count < BOND_RALLY_TRIGGER_MIN_FOLLOWERS:
        return
    var allegiance_id: String = leader.allegiance_id
    var source_reason: String = "rally:%d" % follower_count
    _try_start_bond(leader, allegiance_id, source_reason, BOND_RALLY_TRIGGER_CHANCE, allegiance_id)


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
            _clear_actor_destiny_tracking(actor.actor_id)
            _clear_actor_rivalry_tracking(actor.actor_id)
            _clear_actor_bond_tracking(actor.actor_id)
            _clear_actor_notability_tracking(actor.actor_id)
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
    var destiny_active_labels: Array[String] = []
    var destiny_active_total: int = 0
    var convergence_active_labels: Array[String] = []
    var convergence_active_total: int = 0
    var marked_zone_active_labels: Array[String] = []
    var marked_zone_active_total: int = 0
    var marked_zone_sanctified_active_total: int = 0
    var marked_zone_corrupted_active_total: int = 0
    var rivalry_active_labels: Array[String] = []
    var rivalry_active_total: int = 0
    var duel_active_total: int = 0
    var bond_active_labels: Array[String] = []
    var bond_active_total: int = 0
    var bounty_marked_total: int = 0
    var bounty_marked_humans: int = 0
    var bounty_marked_monsters: int = 0
    var allegiance_affiliated_total: int = 0
    var allegiance_affiliated_humans: int = 0
    var allegiance_affiliated_monsters: int = 0
    var allegiance_member_counts: Dictionary = {}
    var renown_total: float = 0.0
    var notoriety_total: float = 0.0
    var renown_figures_total: int = 0
    var renown_figures_humans: int = 0
    var renown_figures_monsters: int = 0
    var notoriety_figures_total: int = 0
    var notoriety_figures_humans: int = 0
    var notoriety_figures_monsters: int = 0
    var renown_entries: Array[Dictionary] = []
    var notoriety_entries: Array[Dictionary] = []
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
        renown_total += actor.renown
        notoriety_total += actor.notoriety
        if actor.renown >= 28.0:
            renown_figures_total += 1
            if actor.faction == "human":
                renown_figures_humans += 1
            elif actor.faction == "monster":
                renown_figures_monsters += 1
        if actor.notoriety >= BOUNTY_NOTORIETY_PRIORITY_MIN:
            notoriety_figures_total += 1
            if actor.faction == "human":
                notoriety_figures_humans += 1
            elif actor.faction == "monster":
                notoriety_figures_monsters += 1
        if actor.renown >= 1.0:
            renown_entries.append({
                "score": actor.renown,
                "label": _actor_label(actor)
            })
        if actor.notoriety >= 1.0:
            notoriety_entries.append({
                "score": actor.notoriety,
                "label": _actor_label(actor)
            })
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
    var avg_renown: float = renown_total / alive_total if alive_total > 0 else 0.0
    var avg_notoriety: float = notoriety_total / alive_total if alive_total > 0 else 0.0
    var poi_population := world_manager.get_poi_population_snapshot(actors)
    var active_allegiances: Array[Dictionary] = world_manager.get_active_allegiances(elapsed_time)
    var allegiance_structure_labels: Array[String] = []
    var allegiance_doctrine_labels: Array[String] = []
    var allegiance_doctrine_counts := {
        "warlike": 0,
        "steadfast": 0,
        "arcane": 0
    }
    var allegiance_project_labels: Array[String] = []
    var allegiance_project_counts := {
        "fortify": 0,
        "warband_muster": 0,
        "ritual_focus": 0
    }
    var allegiance_project_active_count: int = 0
    var allegiance_vendetta_labels: Array[String] = []
    var allegiance_vendetta_active_count: int = 0
    var legacy_successor_labels: Array[String] = []
    var legacy_successor_active_count: int = 0
    var allegiance_crisis_active_count: int = 0
    var allegiance_crisis_labels: Array[String] = []
    var allegiance_recovery_active_count: int = 0
    var allegiance_recovery_labels: Array[String] = []
    var memorial_scar_active_total: int = 0
    var memorial_site_active_count: int = 0
    var scar_site_active_count: int = 0
    var memorial_scar_labels: Array[String] = []
    var gate_response_human_id: String = ""
    var gate_response_human_label: String = "none"
    var gate_response_human_remaining: float = 0.0
    var gate_response_monster_id: String = ""
    var gate_response_monster_label: String = "none"
    var gate_response_monster_remaining: float = 0.0
    for allegiance in active_allegiances:
        var doctrine: String = str(allegiance.get("doctrine", ""))
        var project_id: String = str(allegiance.get("project", ""))
        var project_remaining: float = float(allegiance.get("project_remaining", 0.0))
        var vendetta_target: String = str(allegiance.get("vendetta_target", ""))
        var vendetta_remaining: float = float(allegiance.get("vendetta_remaining", 0.0))
        var project_label: String = project_id if project_id != "" else "none"
        if project_id != "":
            project_label = "%s@%.0fs" % [project_id, project_remaining]
        var vendetta_label: String = vendetta_target if vendetta_target != "" else "none"
        if vendetta_target != "":
            vendetta_label = "%s@%.0fs" % [vendetta_target, vendetta_remaining]
        allegiance_structure_labels.append(
            "%s[%s,%s,%s,%s,%s]"
            % [
                str(allegiance.get("allegiance_id", "")),
                str(allegiance.get("home_poi", "")),
                str(allegiance.get("structure_state", "")),
                doctrine if doctrine != "" else "none",
                project_label,
                vendetta_label
            ]
        )
        if doctrine != "":
            allegiance_doctrine_labels.append("%s=%s" % [str(allegiance.get("allegiance_id", "")), doctrine])
            if allegiance_doctrine_counts.has(doctrine):
                allegiance_doctrine_counts[doctrine] += 1
        if project_id != "":
            allegiance_project_active_count += 1
            allegiance_project_labels.append(
                "%s=%s(%.0fs)"
                % [str(allegiance.get("allegiance_id", "")), project_id, project_remaining]
            )
            if allegiance_project_counts.has(project_id):
                allegiance_project_counts[project_id] += 1
        if vendetta_target != "":
            allegiance_vendetta_active_count += 1
            allegiance_vendetta_labels.append(
                "%s->%s(%.0fs)"
                % [str(allegiance.get("allegiance_id", "")), vendetta_target, vendetta_remaining]
            )
    allegiance_structure_labels.sort()
    allegiance_doctrine_labels.sort()
    allegiance_project_labels.sort()
    allegiance_vendetta_labels.sort()
    for actor_id_variant in _legacy_successor_runtime_by_actor.keys():
        var actor_id: int = int(actor_id_variant)
        var runtime: Dictionary = _legacy_successor_runtime_by_actor.get(actor_id, {})
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var source_label: String = str(runtime.get("source_label", "legacy"))
        var successor: Actor = _find_actor_by_id(actor_id)
        var successor_label: String = _actor_label(successor) if successor != null else ("actor#%d" % actor_id)
        legacy_successor_labels.append("%s<=%s(%.0fs)" % [successor_label, source_label, remaining])
    legacy_successor_labels.sort()
    legacy_successor_active_count = legacy_successor_labels.size()
    for actor_id_variant in _destiny_runtime_by_actor.keys():
        var actor_id: int = int(actor_id_variant)
        var runtime: Dictionary = _destiny_runtime_by_actor.get(actor_id, {})
        if runtime.is_empty():
            continue
        var actor: Actor = _find_actor_by_id(actor_id)
        var actor_label: String = _actor_label(actor) if actor != null else ("actor#%d" % actor_id)
        var type_short: String = _destiny_type_short(str(runtime.get("type", "")))
        var target_label: String = str(runtime.get("target_label", "target"))
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        destiny_active_labels.append("%s:%s->%s(%.0fs)" % [type_short, actor_label, target_label, remaining])
    destiny_active_labels.sort()
    destiny_active_total = destiny_active_labels.size()
    for event_id_variant in _convergence_runtime_by_id.keys():
        var event_id: int = int(event_id_variant)
        var runtime: Dictionary = _convergence_runtime_by_id.get(event_id, {})
        if runtime.is_empty():
            continue
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var label: String = str(runtime.get("label", "crossroads"))
        var destiny_count: int = int(runtime.get("destiny_count", 0))
        var relic_count: int = int(runtime.get("relic_count", 0))
        var notable_count: int = int(runtime.get("notable_count", 0))
        convergence_active_labels.append(
            "%s[d%d r%d n%d](%.0fs)" % [label, destiny_count, relic_count, notable_count, remaining]
        )
    convergence_active_labels.sort()
    convergence_active_total = convergence_active_labels.size()
    for zone_id_variant in _marked_zone_runtime_by_id.keys():
        var zone_id: int = int(zone_id_variant)
        var runtime: Dictionary = _marked_zone_runtime_by_id.get(zone_id, {})
        if runtime.is_empty():
            continue
        var zone_type: String = str(runtime.get("zone_type", ""))
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var label: String = str(runtime.get("label", "zone"))
        var short_type: String = "S" if zone_type == "sanctified_zone" else "C"
        marked_zone_active_labels.append("%s:%s(%.0fs)" % [short_type, label, remaining])
        if zone_type == "sanctified_zone":
            marked_zone_sanctified_active_total += 1
        elif zone_type == "corrupted_zone":
            marked_zone_corrupted_active_total += 1
    marked_zone_active_labels.sort()
    marked_zone_active_total = marked_zone_active_labels.size()
    for rivalry_id_variant in _rivalry_runtime_by_id.keys():
        var rivalry_id: int = int(rivalry_id_variant)
        var runtime: Dictionary = _rivalry_runtime_by_id.get(rivalry_id, {})
        if runtime.is_empty():
            continue
        var label: String = str(runtime.get("label", "rivals"))
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var duel_active: bool = bool(runtime.get("duel_active", false))
        if duel_active:
            duel_active_total += 1
            rivalry_active_labels.append("%s[DUEL](%.0fs)" % [label, remaining])
        else:
            rivalry_active_labels.append("%s(%.0fs)" % [label, remaining])
    rivalry_active_labels.sort()
    rivalry_active_total = rivalry_active_labels.size()
    for bond_id_variant in _bond_runtime_by_id.keys():
        var bond_id: int = int(bond_id_variant)
        var runtime: Dictionary = _bond_runtime_by_id.get(bond_id, {})
        if runtime.is_empty():
            continue
        var bond_label: String = str(runtime.get("label", "bond"))
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        bond_active_labels.append("%s(%.0fs)" % [bond_label, remaining])
    bond_active_labels.sort()
    bond_active_total = bond_active_labels.size()
    for allegiance_variant in _allegiance_crisis_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        var runtime: Dictionary = _allegiance_crisis_runtime_by_id.get(allegiance_id, {})
        if runtime.is_empty():
            continue
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var reason: String = str(runtime.get("reason", "crisis"))
        allegiance_crisis_labels.append("%s:%s@%.0fs" % [allegiance_id, reason, remaining])
    allegiance_crisis_labels.sort()
    allegiance_crisis_active_count = allegiance_crisis_labels.size()
    for allegiance_variant in _allegiance_recovery_runtime_by_id.keys():
        var allegiance_id: String = str(allegiance_variant)
        var runtime: Dictionary = _allegiance_recovery_runtime_by_id.get(allegiance_id, {})
        if runtime.is_empty():
            continue
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var reason: String = str(runtime.get("reason", "recovery"))
        allegiance_recovery_labels.append("%s:%s@%.0fs" % [allegiance_id, reason, remaining])
    allegiance_recovery_labels.sort()
    allegiance_recovery_active_count = allegiance_recovery_labels.size()
    for site_id_variant in _memorial_scar_runtime.keys():
        var site_id: int = int(site_id_variant)
        var runtime: Dictionary = _memorial_scar_runtime.get(site_id, {})
        var site_type: String = str(runtime.get("type", ""))
        var remaining: float = max(0.0, float(runtime.get("ends_at", elapsed_time)) - elapsed_time)
        var source_short: String = str(runtime.get("source_short", "fallen"))
        if site_type == "memorial_site":
            memorial_site_active_count += 1
        elif site_type == "scar_site":
            scar_site_active_count += 1
        memorial_scar_labels.append("%s:%s(%.0fs)" % [_memorial_scar_type_short(site_type), source_short, remaining])
    memorial_scar_labels.sort()
    memorial_scar_active_total = memorial_site_active_count + scar_site_active_count
    var human_response: Dictionary = _gate_response_runtime_by_faction.get("human", {})
    if not human_response.is_empty():
        gate_response_human_id = str(human_response.get("response_id", "gate_seal"))
        gate_response_human_remaining = max(0.0, float(human_response.get("ends_at", elapsed_time)) - elapsed_time)
        gate_response_human_label = "%s@%.0fs" % [gate_response_human_id, gate_response_human_remaining]
    var monster_response: Dictionary = _gate_response_runtime_by_faction.get("monster", {})
    if not monster_response.is_empty():
        gate_response_monster_id = str(monster_response.get("response_id", "gate_exploit"))
        gate_response_monster_remaining = max(0.0, float(monster_response.get("ends_at", elapsed_time)) - elapsed_time)
        gate_response_monster_label = "%s@%.0fs" % [gate_response_monster_id, gate_response_monster_remaining]
    var poi_influence_active_count: int = 0
    var poi_structure_active_count: int = 0
    for poi_name in poi_runtime_snapshot.keys():
        var details: Dictionary = poi_runtime_snapshot.get(poi_name, {})
        if bool(details.get("influence_active", false)):
            poi_influence_active_count += 1
        if bool(details.get("structure_active", false)):
            poi_structure_active_count += 1
    relic_active_labels.sort()
    var top_renown_labels: Array[String] = _top_notability_labels(renown_entries, 4)
    var top_notoriety_labels: Array[String] = _top_notability_labels(notoriety_entries, 4)
    var neutral_gate_runtime: Dictionary = world_manager.get_neutral_gate_runtime_state(elapsed_time)
    var neutral_gate_status: String = str(neutral_gate_runtime.get("status", "dormant"))
    var neutral_gate_poi: String = str(neutral_gate_runtime.get("poi", ""))
    var neutral_gate_remaining: float = float(neutral_gate_runtime.get("remaining", 0.0))
    var neutral_gate_cooldown: float = float(neutral_gate_runtime.get("cooldown", 0.0))

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
        "avg_renown": avg_renown,
        "avg_notoriety": avg_notoriety,
        "renown_figures_total": renown_figures_total,
        "renown_figures_humans": renown_figures_humans,
        "renown_figures_monsters": renown_figures_monsters,
        "notoriety_figures_total": notoriety_figures_total,
        "notoriety_figures_humans": notoriety_figures_humans,
        "notoriety_figures_monsters": notoriety_figures_monsters,
        "top_renown_labels": top_renown_labels,
        "top_notoriety_labels": top_notoriety_labels,
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
        "destiny_active_total": destiny_active_total,
        "destiny_active_labels": destiny_active_labels,
        "destiny_started_total": destiny_started_total,
        "destiny_ended_total": destiny_ended_total,
        "destiny_fulfilled_total": destiny_fulfilled_total,
        "destiny_interrupted_total": destiny_interrupted_total,
        "convergence_active_total": convergence_active_total,
        "convergence_active_labels": convergence_active_labels,
        "convergence_started_total": convergence_started_total,
        "convergence_ended_total": convergence_ended_total,
        "convergence_interrupted_total": convergence_interrupted_total,
        "marked_zone_active_total": marked_zone_active_total,
        "marked_zone_sanctified_active_total": marked_zone_sanctified_active_total,
        "marked_zone_corrupted_active_total": marked_zone_corrupted_active_total,
        "marked_zone_active_labels": marked_zone_active_labels,
        "marked_zone_started_total": marked_zone_started_total,
        "marked_zone_faded_total": marked_zone_faded_total,
        "rivalry_active_total": rivalry_active_total,
        "rivalry_active_labels": rivalry_active_labels,
        "duel_active_total": duel_active_total,
        "rivalry_started_total": rivalry_started_total,
        "rivalry_ended_total": rivalry_ended_total,
        "rivalry_resolved_total": rivalry_resolved_total,
        "rivalry_expired_total": rivalry_expired_total,
        "duel_started_total": duel_started_total,
        "bond_active_total": bond_active_total,
        "bond_active_labels": bond_active_labels,
        "bond_started_total": bond_started_total,
        "bond_ended_total": bond_ended_total,
        "bond_broken_total": bond_broken_total,
        "bounty_active": bounty_active,
        "bounty_remaining": bounty_remaining,
        "bounty_target_label": bounty_target_label,
        "bounty_target_allegiance_id": bounty_target_allegiance_id,
        "bounty_source_faction": bounty_source_faction,
        "bounty_source_poi": bounty_source_poi,
        "bounty_marked_total": bounty_marked_total,
        "bounty_marked_humans": bounty_marked_humans,
        "bounty_marked_monsters": bounty_marked_monsters,
        "bounty_started_total": bounty_started_total,
        "bounty_cleared_total": bounty_cleared_total,
        "bounty_expired_total": bounty_expired_total,
        "renown_rising_events_total": renown_rising_events_total,
        "notoriety_rising_events_total": notoriety_rising_events_total,
        "allegiance_active_count": active_allegiances.size(),
        "allegiance_affiliated_total": allegiance_affiliated_total,
        "allegiance_affiliated_humans": allegiance_affiliated_humans,
        "allegiance_affiliated_monsters": allegiance_affiliated_monsters,
        "allegiance_unaffiliated_total": max(0, alive_total - allegiance_affiliated_total),
        "allegiance_member_counts": allegiance_member_counts,
        "allegiance_structure_labels": allegiance_structure_labels,
        "allegiance_doctrine_labels": allegiance_doctrine_labels,
        "allegiance_doctrine_counts": allegiance_doctrine_counts,
        "doctrine_assigned_total": doctrine_assigned_total,
        "allegiance_project_active_count": allegiance_project_active_count,
        "allegiance_project_labels": allegiance_project_labels,
        "allegiance_project_counts": allegiance_project_counts,
        "project_started_total": project_started_total,
        "project_ended_total": project_ended_total,
        "project_interrupted_total": project_interrupted_total,
        "allegiance_vendetta_active_count": allegiance_vendetta_active_count,
        "allegiance_vendetta_labels": allegiance_vendetta_labels,
        "vendetta_started_total": vendetta_started_total,
        "vendetta_ended_total": vendetta_ended_total,
        "vendetta_resolved_total": vendetta_resolved_total,
        "vendetta_expired_total": vendetta_expired_total,
        "allegiance_crisis_active_count": allegiance_crisis_active_count,
        "allegiance_crisis_labels": allegiance_crisis_labels,
        "crisis_started_total": crisis_started_total,
        "crisis_ended_total": crisis_ended_total,
        "crisis_resolved_total": crisis_resolved_total,
        "crisis_expired_total": crisis_expired_total,
        "allegiance_recovery_active_count": allegiance_recovery_active_count,
        "allegiance_recovery_labels": allegiance_recovery_labels,
        "recovery_started_total": recovery_started_total,
        "recovery_ended_total": recovery_ended_total,
        "recovery_interrupted_total": recovery_interrupted_total,
        "legacy_triggered_total": legacy_triggered_total,
        "legacy_successor_chosen_total": legacy_successor_chosen_total,
        "legacy_relic_inherited_total": legacy_relic_inherited_total,
        "legacy_faded_total": legacy_faded_total,
        "legacy_cooldown_left": _legacy_cooldown_left,
        "legacy_successor_active_count": legacy_successor_active_count,
        "legacy_successor_labels": legacy_successor_labels,
        "memorial_scar_active_total": memorial_scar_active_total,
        "memorial_site_active_count": memorial_site_active_count,
        "scar_site_active_count": scar_site_active_count,
        "memorial_scar_born_total": memorial_scar_born_total,
        "memorial_scar_faded_total": memorial_scar_faded_total,
        "memorial_scar_labels": memorial_scar_labels,
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
        "neutral_gate_poi": neutral_gate_poi,
        "neutral_gate_status": neutral_gate_status,
        "neutral_gate_active": neutral_gate_status == "open",
        "neutral_gate_remaining": neutral_gate_remaining,
        "neutral_gate_cooldown": neutral_gate_cooldown,
        "neutral_gate_opened_total": neutral_gate_opened_total,
        "neutral_gate_closed_total": neutral_gate_closed_total,
        "neutral_gate_breach_total": neutral_gate_breach_total,
        "gate_response_human_active": gate_response_human_id != "",
        "gate_response_human_id": gate_response_human_id,
        "gate_response_human_label": gate_response_human_label,
        "gate_response_human_remaining": gate_response_human_remaining,
        "gate_response_monster_active": gate_response_monster_id != "",
        "gate_response_monster_id": gate_response_monster_id,
        "gate_response_monster_label": gate_response_monster_label,
        "gate_response_monster_remaining": gate_response_monster_remaining,
        "gate_response_started_total": gate_response_started_total,
        "gate_response_ended_total": gate_response_ended_total,
        "gate_response_success_total": gate_response_success_total,
        "gate_response_interrupted_total": gate_response_interrupted_total,
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
            if leader == null or leader.is_dead or not leader.can_lead_rally() or leader.faction != actor.faction:
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
        var crisis_penalty_active: bool = _is_actor_in_allegiance_crisis(actor)
        if not crisis_penalty_active and leader_for_bonus != null:
            crisis_penalty_active = _is_actor_in_allegiance_crisis(leader_for_bonus)
        if crisis_penalty_active and actor.rally_bonus_active and randf() <= ALLEGIANCE_CRISIS_RALLY_BONUS_SUPPRESS_CHANCE:
            actor.rally_bonus_active = false
        var recovery_pulse_active: bool = _is_actor_in_allegiance_recovery(actor)
        if not recovery_pulse_active and leader_for_bonus != null:
            recovery_pulse_active = _is_actor_in_allegiance_recovery(leader_for_bonus)
        if recovery_pulse_active and not actor.rally_bonus_active and randf() <= ALLEGIANCE_RECOVERY_RALLY_BONUS_BOOST_CHANCE:
            actor.rally_bonus_active = true

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
        if previous_followers < BOND_RALLY_TRIGGER_MIN_FOLLOWERS and current_followers >= BOND_RALLY_TRIGGER_MIN_FOLLOWERS:
            _try_start_bond_from_rally(leader, current_followers)

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
            if poi_name != "":
                _recent_structure_loss_until_by_poi[poi_name] = elapsed_time + ALLEGIANCE_RECOVERY_STRUCTURE_RESTABILIZE_WINDOW
        elif kind == "allegiance_created":
            allegiance_created_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var allegiance_faction: String = str(transition.get("faction", ""))
            record_event("Allegiance UP: %s at %s (%s)." % [allegiance_id, poi_name, allegiance_faction])
            var doctrine: String = str(transition.get("doctrine", ""))
            if doctrine != "":
                doctrine_assigned_total += 1
                record_event("Doctrine assigned: %s -> %s." % [allegiance_id, doctrine])
            var recent_loss_until: float = float(_recent_structure_loss_until_by_poi.get(poi_name, 0.0))
            if recent_loss_until > elapsed_time:
                _try_start_allegiance_recovery(allegiance_id, "anchor_restabilized", 0.20, 1.4, poi_name)
                _recent_structure_loss_until_by_poi.erase(poi_name)
        elif kind == "allegiance_removed":
            allegiance_removed_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var allegiance_faction: String = str(transition.get("faction", ""))
            record_event("Allegiance DOWN: %s at %s (%s)." % [allegiance_id, poi_name, allegiance_faction])
        elif kind == "allegiance_project_started":
            project_started_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var project_id: String = str(transition.get("project_id", "project"))
            var duration: float = float(transition.get("duration", 0.0))
            record_event("Project START: %s -> %s at %s (%.0fs)." % [allegiance_id, project_id, poi_name, duration])
            _try_resolve_allegiance_crisis(allegiance_id, "project_restarted:%s" % project_id)
        elif kind == "allegiance_project_ended":
            project_ended_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var project_id: String = str(transition.get("project_id", "project"))
            record_event("Project END: %s -> %s at %s." % [allegiance_id, project_id, poi_name])
        elif kind == "allegiance_project_interrupted":
            project_interrupted_total += 1
            var allegiance_id: String = str(transition.get("allegiance_id", "allegiance"))
            var project_id: String = str(transition.get("project_id", "project"))
            var reason: String = str(transition.get("reason", "interrupted"))
            var poi_label: String = poi_name if poi_name != "" else "unknown"
            record_event("Project INTERRUPTED: %s -> %s at %s (%s)." % [allegiance_id, project_id, poi_label, reason])
            _try_start_crisis_from_project_interrupt(allegiance_id, project_id, reason)
        elif kind == "vendetta_started" or kind == "vendetta_resolved" or kind == "vendetta_expired":
            _handle_vendetta_transition(transition)
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
            var defender_allegiance_id: String = str(transition.get("defender_allegiance_id", ""))
            if outcome == "success":
                raid_success_total += 1
            elif outcome == "interrupted":
                raid_interrupted_total += 1
            elif outcome == "timeout":
                raid_timeout_total += 1
            record_event("Raid END: %s (%s %s -> %s)." % [outcome, attacker_faction, source_poi, target_poi])
            if defender_allegiance_id != "" and (outcome == "interrupted" or outcome == "timeout"):
                _try_start_allegiance_recovery(
                    defender_allegiance_id,
                    "raid_end:%s" % outcome,
                    0.12,
                    0.8,
                    target_poi
                )
        elif kind == "neutral_gate_opened":
            neutral_gate_opened_total += 1
            var open_seconds: float = float(transition.get("open_seconds", 0.0))
            var event_id: String = str(transition.get("world_event", ""))
            record_event(
                "Dungeon/Gate OPEN: %s (%.0fs, %s)."
                % [poi_name, open_seconds, _world_event_label(event_id)]
            )
        elif kind == "neutral_gate_closed":
            neutral_gate_closed_total += 1
            var cooldown_seconds: float = float(transition.get("cooldown_seconds", 0.0))
            record_event("Dungeon/Gate CLOSED: %s (next in ~%.0fs)." % [poi_name, cooldown_seconds])
        elif kind == "neutral_gate_breach":
            neutral_gate_breach_total += 1
            var breach_actor: Actor = _spawn_neutral_gate_breach(transition)
            var breach_label := _actor_label(breach_actor) if breach_actor != null else "none"
            record_event("Dungeon/Gate BREACH: %s -> %s." % [poi_name, breach_label])

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


func _handle_vendetta_transition(transition: Dictionary) -> void:
    var kind: String = str(transition.get("kind", ""))
    var source_allegiance_id: String = str(transition.get("source_allegiance_id", "allegiance"))
    var target_allegiance_id: String = str(transition.get("target_allegiance_id", "target"))
    var reason: String = str(transition.get("reason", "vendetta"))

    if kind == "vendetta_started":
        vendetta_started_total += 1
        var duration: float = float(transition.get("duration", 0.0))
        record_event(
            "Vendetta START: %s -> %s (%s, %.0fs)."
            % [source_allegiance_id, target_allegiance_id, reason, duration]
        )
        _try_start_crisis_from_vendetta(source_allegiance_id, target_allegiance_id, reason)
        return

    if kind == "vendetta_resolved":
        vendetta_resolved_total += 1
        vendetta_ended_total += 1
        record_event("Vendetta RESOLVED: %s vs %s (%s)." % [source_allegiance_id, target_allegiance_id, reason])
        record_event("Vendetta END: %s -> %s (resolved)." % [source_allegiance_id, target_allegiance_id])
        _try_start_allegiance_recovery(source_allegiance_id, "vendetta_resolved", 0.16, 0.9, target_allegiance_id)
        return

    if kind == "vendetta_expired":
        vendetta_expired_total += 1
        vendetta_ended_total += 1
        record_event("Vendetta EXPIRED: %s vs %s (%s)." % [source_allegiance_id, target_allegiance_id, reason])
        record_event("Vendetta END: %s -> %s (expired)." % [source_allegiance_id, target_allegiance_id])
        _try_start_allegiance_recovery(source_allegiance_id, "vendetta_expired", 0.08, 0.4, target_allegiance_id)


func _try_trigger_legacy(victim: Actor, killer: Actor, reason: String) -> Dictionary:
    if victim == null:
        return {}
    if not _is_legacy_candidate(victim):
        return {}
    if _legacy_cooldown_left > 0.0:
        return {}

    var guaranteed: bool = victim.is_champion or victim.is_special_arrival() or victim.has_relic()
    if not guaranteed and randf() > LEGACY_TRIGGER_CHANCE:
        return {}

    legacy_triggered_total += 1
    _legacy_cooldown_left = LEGACY_COOLDOWN
    record_event("Legacy Triggered: %s (%s)." % [_actor_label(victim), reason])

    var successor: Actor = null
    if _legacy_successor_runtime_by_actor.size() < LEGACY_MAX_ACTIVE_SUCCESSORS:
        successor = _pick_legacy_successor(victim)
    if successor == null:
        _try_legacy_vendetta_impulse(victim, killer)
        return {
            "triggered": true,
            "relic_inherited": false
        }

    var source_label: String = _actor_label(victim)
    var duration: float = LEGACY_SUCCESSOR_DURATION + randf_range(-4.0, 4.0)
    var successor_ends_at: float = elapsed_time + max(12.0, duration)
    _legacy_successor_runtime_by_actor[successor.actor_id] = {
        "source_label": source_label,
        "source_actor_id": victim.actor_id,
        "ends_at": successor_ends_at
    }
    legacy_successor_chosen_total += 1
    record_event(
        "Successor Chosen: %s <= %s (%.0fs)."
        % [_actor_label(successor), source_label, max(0.0, successor_ends_at - elapsed_time)]
    )
    _try_start_allegiance_recovery(successor.allegiance_id, "legacy_successor", 0.22, 1.2, source_label)
    _try_start_bond_from_legacy(successor, source_label)

    var renown_transfer: float = clampf(victim.renown * LEGACY_RENOWN_TRANSFER_RATIO, 1.0, 6.0)
    var notoriety_transfer: float = clampf(victim.notoriety * LEGACY_NOTORIETY_TRANSFER_RATIO, 0.6, 5.0)
    if victim.is_champion:
        renown_transfer += 0.8
    if victim.is_special_arrival():
        renown_transfer += 1.1
        notoriety_transfer += 0.6
    _apply_notability_gain(successor, renown_transfer, notoriety_transfer, "legacy_successor")

    var relic_inherited: bool = false
    if victim.has_relic() and successor.can_receive_relic():
        var inherited_id: String = victim.relic_id
        var inherited_title: String = victim.relic_title if victim.relic_title != "" else _relic_title(victim.relic_id)
        successor.set_relic(inherited_id, inherited_title)
        _apply_notability_gain(
            successor,
            RENOWN_GAIN_ON_RELIC * 0.45,
            NOTORIETY_GAIN_ON_RELIC * 0.32,
            "legacy_relic_inherit"
        )
        relic_acquired_total += 1
        legacy_relic_inherited_total += 1
        relic_inherited = true
        record_event("Relic INHERITED: %s by %s." % [inherited_title, _actor_label(successor)])

    _try_legacy_vendetta_impulse(victim, killer)
    return {
        "triggered": true,
        "successor_actor_id": successor.actor_id,
        "relic_inherited": relic_inherited
    }


func _try_legacy_vendetta_impulse(victim: Actor, killer: Actor) -> void:
    if victim == null or killer == null or killer.is_dead:
        return
    if victim.allegiance_id == "" or killer.allegiance_id == "":
        return
    if victim.allegiance_id == killer.allegiance_id:
        return

    var transition: Dictionary = world_manager.register_vendetta_incident(
        victim.allegiance_id,
        killer.allegiance_id,
        "legacy_fall",
        elapsed_time
    )
    if not transition.is_empty():
        _handle_vendetta_transition(transition)


func _is_legacy_candidate(victim: Actor) -> bool:
    if victim == null:
        return false
    if victim.is_champion or victim.is_special_arrival() or victim.has_relic():
        return true
    if victim.renown >= LEGACY_RENOWN_TRIGGER:
        return true
    if victim.notoriety >= LEGACY_NOTORIETY_TRIGGER:
        return true
    return false


func _pick_legacy_successor(victim: Actor) -> Actor:
    if victim == null:
        return null
    var same_faction: Array[Actor] = []
    var same_allegiance: Array[Actor] = []
    var max_distance: float = LEGACY_SUCCESSOR_RADIUS

    for actor in actors:
        if actor == null or actor == victim or actor.is_dead:
            continue
        if actor.faction != victim.faction:
            continue
        var distance: float = actor.global_position.distance_to(victim.global_position)
        if distance > max_distance:
            continue
        same_faction.append(actor)
        if victim.allegiance_id != "" and actor.allegiance_id == victim.allegiance_id:
            same_allegiance.append(actor)

    var pool: Array[Actor] = same_allegiance if not same_allegiance.is_empty() else same_faction
    if pool.is_empty():
        return null

    var selected: Actor = null
    var best_score: float = -INF
    for candidate in pool:
        var distance: float = candidate.global_position.distance_to(victim.global_position)
        var score: float = 0.0
        score += (LEGACY_SUCCESSOR_RADIUS - distance) * 0.8
        score += candidate.renown * 0.08
        score += candidate.notoriety * 0.05
        if candidate.can_lead_rally():
            score += 2.5
        if candidate.is_champion:
            score += 1.8
        if candidate.is_special_arrival():
            score += 1.4
        if candidate.has_relic():
            score += 0.8
        if score > best_score:
            best_score = score
            selected = candidate
    return selected


func _update_legacy_runtime(delta: float) -> void:
    _legacy_cooldown_left = max(0.0, _legacy_cooldown_left - delta)
    if _legacy_successor_runtime_by_actor.is_empty():
        return

    var to_remove: Array[int] = []
    for actor_id_variant in _legacy_successor_runtime_by_actor.keys():
        var actor_id: int = int(actor_id_variant)
        var runtime: Dictionary = _legacy_successor_runtime_by_actor.get(actor_id, {})
        var ends_at: float = float(runtime.get("ends_at", elapsed_time))
        var actor: Actor = _find_actor_by_id(actor_id)
        if actor == null or actor.is_dead or elapsed_time >= ends_at:
            to_remove.append(actor_id)

    for actor_id in to_remove:
        var runtime: Dictionary = _legacy_successor_runtime_by_actor.get(actor_id, {})
        var actor: Actor = _find_actor_by_id(actor_id)
        var label: String = _actor_label(actor) if actor != null else ("actor#%d" % actor_id)
        record_event("Legacy Faded: %s." % label)
        legacy_faded_total += 1
        _legacy_successor_runtime_by_actor.erase(actor_id)


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


func _clear_actor_destiny_tracking(actor_id: int) -> void:
    if _destiny_runtime_by_actor.has(actor_id):
        _end_destiny_pull(actor_id, "interrupted", "actor_removed")
    _destiny_cooldown_until_by_actor.erase(actor_id)


func _clear_actor_notability_tracking(actor_id: int) -> void:
    _renown_tier_by_actor.erase(actor_id)
    _notoriety_tier_by_actor.erase(actor_id)


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
    _apply_notability_gain(actor, RENOWN_GAIN_ON_CHAMPION, NOTORIETY_GAIN_ON_CHAMPION, "champion:%s" % promotion_reason)
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


func _apply_notability_gain(actor: Actor, renown_gain: float, notoriety_gain: float, reason: String) -> void:
    if actor == null or actor.is_dead:
        return
    var renown_before: float = actor.renown
    var notoriety_before: float = actor.notoriety
    if renown_gain > 0.0:
        actor.add_renown(renown_gain)
    if notoriety_gain > 0.0:
        actor.add_notoriety(notoriety_gain)
    _emit_notability_threshold_events(actor, renown_before, notoriety_before, reason)


func _emit_notability_threshold_events(actor: Actor, renown_before: float, notoriety_before: float, reason: String) -> void:
    var actor_id: int = actor.actor_id
    var renown_tier_before: int = _notability_tier(renown_before)
    var renown_tier_after: int = _notability_tier(actor.renown)
    var renown_peak_tier: int = int(_renown_tier_by_actor.get(actor_id, 0))
    if renown_tier_after > renown_tier_before and renown_tier_after > renown_peak_tier:
        _renown_tier_by_actor[actor_id] = renown_tier_after
        renown_rising_events_total += 1
        record_event("Renown Rising: %s -> %.1f (%s)." % [_actor_label(actor), actor.renown, reason])

    var notoriety_tier_before: int = _notability_tier(notoriety_before)
    var notoriety_tier_after: int = _notability_tier(actor.notoriety)
    var notoriety_peak_tier: int = int(_notoriety_tier_by_actor.get(actor_id, 0))
    if notoriety_tier_after > notoriety_tier_before and notoriety_tier_after > notoriety_peak_tier:
        _notoriety_tier_by_actor[actor_id] = notoriety_tier_after
        notoriety_rising_events_total += 1
        record_event("Notoriety Rising: %s -> %.1f (%s)." % [_actor_label(actor), actor.notoriety, reason])


func _notability_tier(score: float) -> int:
    var tier: int = 0
    for threshold in NOTABILITY_LOG_THRESHOLDS:
        if score >= float(threshold):
            tier += 1
    return tier


func _top_notability_labels(entries: Array[Dictionary], limit: int = 4) -> Array[String]:
    if entries.is_empty():
        return []
    var sorted_entries: Array[Dictionary] = entries.duplicate(true)
    sorted_entries.sort_custom(func(a, b):
        var score_a: float = float(a.get("score", 0.0))
        var score_b: float = float(b.get("score", 0.0))
        if is_equal_approx(score_a, score_b):
            return str(a.get("label", "")) < str(b.get("label", ""))
        return score_a > score_b
    )
    var labels: Array[String] = []
    for idx in range(min(limit, sorted_entries.size())):
        var item: Dictionary = sorted_entries[idx]
        labels.append("%s(%.0f)" % [str(item.get("label", "unknown")), float(item.get("score", 0.0))])
    return labels


func _actor_label(actor: Actor) -> String:
    if actor == null:
        return "unknown"
    var role_suffix := actor.role_tag()
    var level_suffix := actor.level_tag()
    var champion_suffix := actor.champion_tag()
    var special_suffix := actor.special_tag()
    var relic_suffix := actor.relic_tag()
    var bounty_suffix := actor.bounty_tag()
    var destiny_suffix := actor.destiny_tag()
    var rivalry_suffix := actor.rivalry_tag()
    var bond_suffix := actor.bond_tag()
    var renown_suffix := actor.renown_tag()
    var notoriety_suffix := actor.notoriety_tag()
    var allegiance_suffix := actor.allegiance_tag()
    var legacy_suffix := "[HEIR]" if _legacy_successor_runtime_by_actor.has(actor.actor_id) else ""
    return "%s%s%s%s%s%s%s%s%s%s%s%s%s%s#%d" % [actor.actor_kind, role_suffix, level_suffix, champion_suffix, special_suffix, relic_suffix, bounty_suffix, destiny_suffix, rivalry_suffix, bond_suffix, renown_suffix, notoriety_suffix, allegiance_suffix, legacy_suffix, actor.actor_id]
