extends Node3D
class_name GameLoop

const TICK_RATE: float = 8.0
const MAX_EVENT_LOG: int = 14

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
var flee_events_total: int = 0
var engagements_total: int = 0

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
    _cleanup_dead_actors()
    sandbox_systems.tick_systems(delta, actors, self)

    debug_overlay.update_overlay(_build_snapshot(), event_log)


func register_spawn(actor: Actor) -> void:
    spawns_total += 1
    record_event("Spawn %s#%d (%s)." % [actor.actor_kind, actor.actor_id, actor.faction])


func register_state_change(actor: Actor, from_state: String, to_state: String, reason: String) -> void:
    if from_state == to_state:
        return

    if to_state in ["detect", "chase", "attack", "cast"]:
        engagements_total += 1

    if to_state == "flee":
        flee_events_total += 1

    if to_state in ["attack", "cast", "flee"]:
        record_event("%s#%d %s -> %s (%s)." % [actor.actor_kind, actor.actor_id, from_state, to_state, reason])


func register_attack(kind: String, attacker: Actor, target: Actor, damage: float) -> void:
    if kind == "melee":
        melee_hits_total += 1
    elif kind == "magic":
        magic_hits_total += 1

    record_event(
        "%s hit: %s#%d -> %s#%d (%.1f)."
        % [kind, attacker.actor_kind, attacker.actor_id, target.actor_kind, target.actor_id, damage]
    )


func register_cast(caster: Actor, target: Actor) -> void:
    casts_total += 1
    record_event("Cast: %s#%d -> %s#%d." % [caster.actor_kind, caster.actor_id, target.actor_kind, target.actor_id])


func register_death(victim: Actor, killer: Actor, reason: String) -> void:
    if victim == null or victim.death_reported:
        return

    victim.mark_death_reported()
    deaths_total += 1

    if killer != null:
        kills_total += 1
        record_event(
            "Death: %s#%d by %s#%d (%s)."
            % [victim.actor_kind, victim.actor_id, killer.actor_kind, killer.actor_id, reason]
        )
    else:
        record_event("Death: %s#%d (%s)." % [victim.actor_kind, victim.actor_id, reason])


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
            actor.queue_free()
            actors.remove_at(idx)


func _build_snapshot() -> Dictionary:
    var alive_total: int = 0
    var humans_alive: int = 0
    var monsters_alive: int = 0
    var hp_total: float = 0.0
    var energy_total: float = 0.0

    var state_counts := {
        "wander": 0,
        "detect": 0,
        "chase": 0,
        "attack": 0,
        "cast": 0,
        "flee": 0
    }

    for actor in actors:
        if actor == null or actor.is_dead:
            continue

        alive_total += 1
        hp_total += actor.hp
        energy_total += actor.energy

        if actor.faction == "human":
            humans_alive += 1
        elif actor.faction == "monster":
            monsters_alive += 1

        if state_counts.has(actor.state):
            state_counts[actor.state] += 1
        else:
            state_counts[actor.state] = 1

    var avg_hp: float = hp_total / alive_total if alive_total > 0 else 0.0
    var avg_energy: float = energy_total / alive_total if alive_total > 0 else 0.0

    return {
        "tick": tick_index,
        "time": elapsed_time,
        "alive_total": alive_total,
        "humans_alive": humans_alive,
        "monsters_alive": monsters_alive,
        "avg_hp": avg_hp,
        "avg_energy": avg_energy,
        "spawns_total": spawns_total,
        "deaths_total": deaths_total,
        "kills_total": kills_total,
        "melee_hits_total": melee_hits_total,
        "magic_hits_total": magic_hits_total,
        "casts_total": casts_total,
        "flee_events_total": flee_events_total,
        "engagements_total": engagements_total,
        "state_counts": state_counts
    }
