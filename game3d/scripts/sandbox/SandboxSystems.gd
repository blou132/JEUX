extends Node
class_name SandboxSystems

@export var initial_humans: int = 8
@export var initial_monsters: int = 10
@export var min_humans: int = 5
@export var min_monsters: int = 6
@export var max_population: int = 40
@export var respawn_interval: float = 4.8
@export var brute_spawn_ratio: float = 0.20
@export var ranged_spawn_ratio: float = 0.24
@export var fighter_role_ratio: float = 0.42
@export var mage_role_ratio: float = 0.32
@export var scout_role_ratio: float = 0.26

var _respawn_timer: float = 0.0
var _loop: GameLoop = null
var _world: WorldManager = null
var _entities_root: Node3D = null
var _creature_profiles_by_id: Dictionary = {}


func setup(loop: GameLoop, world: WorldManager, entities_root: Node3D) -> void:
	_loop = loop
	_world = world
	_entities_root = entities_root


func set_creature_profiles(profiles_by_id: Dictionary) -> void:
	_creature_profiles_by_id = profiles_by_id.duplicate(true)


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

	var counts: Dictionary = _count_alive_by_faction(actors)
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
	var profile_id: String = ""

	if faction == "human":
		var human: HumanAgent = HumanAgent.new()
		human.assign_role(_pick_human_role())
		actor = human
		profile_id = "human_%s" % human.human_role
	else:
		actor = _spawn_monster_archetype()
		profile_id = _monster_profile_id(actor)

	_apply_profile_to_actor(actor, profile_id)

	var spawn_position: Vector3 = _world.get_spawn_point(faction)

	_entities_root.add_child(actor)
	actor.global_position = spawn_position

	actors.append(actor)
	_loop.register_spawn(actor)


func _spawn_monster_archetype() -> Actor:
	var brute_ratio: float = clamp(brute_spawn_ratio, 0.0, 1.0)
	var ranged_ratio: float = clamp(ranged_spawn_ratio, 0.0, 1.0 - brute_ratio)
	var roll: float = randf()

	if roll < brute_ratio:
		return BruteMonster.new()
	if roll < brute_ratio + ranged_ratio:
		return RangedMonster.new()
	return MonsterAgent.new()


func _monster_profile_id(actor: Actor) -> String:
	match actor.actor_kind:
		"brute_monster":
			return "monster_brute"
		"ranged_monster":
			return "monster_ranged"
		_:
			return "monster_standard"


func _apply_profile_to_actor(actor: Actor, profile_id: String) -> void:
	if profile_id == "" or not _creature_profiles_by_id.has(profile_id):
		return

	var profile: Dictionary = Dictionary(_creature_profiles_by_id[profile_id])
	for field in ["hp", "speed", "melee_damage", "magic_damage", "magic_range"]:
		if not profile.has(field):
			return

	actor.max_hp = float(profile["hp"])
	actor.hp = actor.max_hp
	actor.speed = float(profile["speed"])
	actor.melee_damage = float(profile["melee_damage"])
	actor.magic_damage = float(profile["magic_damage"])
	actor.magic_range = float(profile["magic_range"])


func _pick_human_role() -> String:
	var fighter: float = clamp(fighter_role_ratio, 0.0, 1.0)
	var mage: float = clamp(mage_role_ratio, 0.0, 1.0 - fighter)
	var scout: float = clamp(scout_role_ratio, 0.0, 1.0 - fighter - mage)
	var remainder: float = max(0.0, 1.0 - (fighter + mage + scout))

	fighter += remainder
	var roll: float = randf()
	if roll < fighter:
		return "fighter"
	if roll < fighter + mage:
		return "mage"
	return "scout"


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
