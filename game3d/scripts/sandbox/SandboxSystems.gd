extends Node
class_name SandboxSystems

@export var initial_humans: int = 8
@export var initial_monsters: int = 10
@export var min_humans: int = 5
@export var min_monsters: int = 6
@export var max_population: int = 40
@export var respawn_interval: float = 4.0

var _respawn_timer: float = 0.0
var _loop: GameLoop = null
var _world: WorldManager = null
var _entities_root: Node3D = null


func setup(loop: GameLoop, world: WorldManager, entities_root: Node3D) -> void:
    _loop = loop
    _world = world
    _entities_root = entities_root


func spawn_initial_population(actors: Array) -> void:
    for _i in range(initial_humans):
        _spawn_actor("human", actors)
    for _i in range(initial_monsters):
        _spawn_actor("monster", actors)


func tick_systems(delta: float, actors: Array, loop: GameLoop) -> void:
    _respawn_timer += delta
    if _respawn_timer < respawn_interval:
        return
    _respawn_timer = 0.0

    var counts := _count_alive_by_faction(actors)
    var current_population: int = counts["human"] + counts["monster"]
    if current_population >= max_population:
        return

    if counts["human"] < min_humans:
        _spawn_actor("human", actors)
        loop.record_event("Respawn trigger: humans below minimum.")

    counts = _count_alive_by_faction(actors)
    current_population = counts["human"] + counts["monster"]
    if current_population >= max_population:
        return

    if counts["monster"] < min_monsters:
        _spawn_actor("monster", actors)
        loop.record_event("Respawn trigger: monsters below minimum.")


func _spawn_actor(faction: String, actors: Array) -> void:
    if _world == null or _entities_root == null or _loop == null:
        return

    var actor: Actor
    if faction == "human":
        actor = HumanAgent.new()
    else:
        actor = MonsterAgent.new()

    actor.global_position = _world.get_spawn_point(faction)
    _entities_root.add_child(actor)
    actors.append(actor)
    _loop.register_spawn(actor)


func _count_alive_by_faction(actors: Array) -> Dictionary:
    var human_count: int = 0
    var monster_count: int = 0

    for actor in actors:
        if actor == null or actor.is_dead:
            continue
        if actor.faction == "human":
            human_count += 1
        elif actor.faction == "monster":
            monster_count += 1

    return {
        "human": human_count,
        "monster": monster_count
    }
