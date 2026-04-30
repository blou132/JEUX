extends Node3D
class_name WorldManager

const ALLEGIANCE_DOCTRINES: Array[String] = ["warlike", "steadfast", "arcane"]
const ALLEGIANCE_PROJECT_TYPES: Array[String] = ["fortify", "warband_muster", "ritual_focus"]

@export var map_size: float = 96.0
@export var nav_cell_size: float = 2.0
@export var wander_radius: float = 14.0
@export var poi_guidance_distance: float = 28.0
@export var poi_influence_activation_time: float = 8.0
@export var poi_structure_activation_time: float = 20.0
@export var poi_structure_loss_time: float = 10.0
@export var poi_structure_min_presence: int = 3
@export var poi_raid_duration: float = 18.0
@export var poi_raid_cooldown: float = 16.0
@export var poi_raid_success_hold: float = 5.0
@export var neutral_gate_open_duration: float = 18.0
@export var neutral_gate_cooldown_min: float = 62.0
@export var neutral_gate_cooldown_max: float = 104.0
@export var neutral_gate_retry_delay: float = 12.0
@export var neutral_gate_min_dominance_seconds: float = 16.0
@export var allegiance_project_duration_min: float = 20.0
@export var allegiance_project_duration_max: float = 34.0
@export var allegiance_project_cooldown: float = 26.0
@export var allegiance_project_check_interval: float = 5.0
@export var allegiance_project_start_chance: float = 0.32
@export var allegiance_vendetta_duration_min: float = 24.0
@export var allegiance_vendetta_duration_max: float = 40.0
@export var allegiance_vendetta_cooldown: float = 26.0

var human_spawn_points: Array[Vector3] = []
var monster_spawn_points: Array[Vector3] = []
var pois: Array[Dictionary] = []
var poi_nodes: Dictionary = {}
var poi_runtime_status: Dictionary = {}
var poi_dominant_faction: Dictionary = {}
var poi_dominance_started_at: Dictionary = {}
var poi_influence_active: Dictionary = {}
var poi_structure_state: Dictionary = {}
var poi_structure_faction: Dictionary = {}
var poi_structure_started_at: Dictionary = {}
var poi_structure_unstable_started_at: Dictionary = {}
var poi_allegiance_id: Dictionary = {}
var poi_raid_state: Dictionary = {}
var poi_raid_cooldown_until: float = 0.0
var poi_last_raid_attacker: String = ""
var raid_pressure_global_multiplier: float = 1.0
var raid_pressure_human_multiplier: float = 1.0
var raid_pressure_monster_multiplier: float = 1.0
var world_event_visual_id: String = ""
var bounty_state: Dictionary = {}
var convergence_state: Dictionary = {}
var alert_state_by_allegiance: Dictionary = {}
var sanctuary_bastion_state_by_id: Dictionary = {}
var taboo_state_by_id: Dictionary = {}
var neutral_gate_status: String = "dormant"
var neutral_gate_open_until: float = 0.0
var neutral_gate_cooldown_until: float = 0.0
var neutral_gate_opened_total: int = 0
var neutral_gate_closed_total: int = 0
var neutral_gate_breaches_total: int = 0
var neutral_gate_breach_pending: bool = false
var neutral_gate_bonus_breach_used: bool = false
var neutral_gate_response_pull_human_mult: float = 1.0
var neutral_gate_response_pull_monster_mult: float = 1.0
var allegiance_crisis_raid_mult_by_id: Dictionary = {}
var allegiance_recovery_defense_delta_by_id: Dictionary = {}
var allegiance_mending_modifiers_by_id: Dictionary = {}
var vendetta_suppressed_pair_keys: Dictionary = {}
var allegiance_doctrine_by_id: Dictionary = {}
var doctrine_invalid_by_allegiance: Dictionary = {}
var faction_template_by_id: Dictionary = {}
var faction_template_by_kind: Dictionary = {}
var faction_template_id_by_allegiance: Dictionary = {}
var doctrine_template_by_id: Dictionary = {}
var location_template_by_id: Dictionary = {}
var location_template_by_kind: Dictionary = {}
var allegiance_project_runtime_by_id: Dictionary = {}
var allegiance_project_cooldown_until_by_id: Dictionary = {}
var allegiance_project_next_attempt_at_by_id: Dictionary = {}
var allegiance_vendetta_runtime_by_id: Dictionary = {}
var allegiance_vendetta_cooldown_until_by_id: Dictionary = {}


func setup_world() -> void:
	_build_ground()
	_build_spawn_points()
	_build_pois()


func tick_world(_delta: float) -> void:
	pass


func set_raid_pressure_modifiers(
	global_multiplier: float = 1.0,
	human_multiplier: float = 1.0,
	monster_multiplier: float = 1.0
) -> void:
	raid_pressure_global_multiplier = clampf(global_multiplier, 0.45, 1.35)
	raid_pressure_human_multiplier = clampf(human_multiplier, 0.45, 1.35)
	raid_pressure_monster_multiplier = clampf(monster_multiplier, 0.45, 1.35)


func set_world_event_visual(event_id: String) -> void:
	world_event_visual_id = event_id


func set_faction_templates(templates_by_id: Dictionary = {}) -> void:
	faction_template_by_id.clear()
	faction_template_by_kind.clear()
	faction_template_id_by_allegiance.clear()

	for template_variant in templates_by_id.values():
		if typeof(template_variant) != TYPE_DICTIONARY:
			continue
		var sanitized: Dictionary = _sanitize_faction_template_entry(template_variant)
		if sanitized.is_empty():
			continue
		var template_id: String = str(sanitized.get("id", ""))
		var kind: String = str(sanitized.get("kind", ""))
		if template_id == "" or kind == "":
			continue
		faction_template_by_id[template_id] = sanitized
		if not faction_template_by_kind.has(kind):
			faction_template_by_kind[kind] = sanitized

	for poi_name_variant in poi_allegiance_id.keys():
		var poi_name: String = str(poi_name_variant)
		var allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))
		var faction: String = str(poi_structure_faction.get(poi_name, ""))
		if allegiance_id == "" or faction == "":
			continue
		var template_id: String = _resolve_faction_template_id_for_faction(faction)
		if template_id != "":
			faction_template_id_by_allegiance[allegiance_id] = template_id


func set_doctrine_templates(templates_by_id: Dictionary = {}) -> void:
	doctrine_template_by_id.clear()

	for template_variant in templates_by_id.values():
		if typeof(template_variant) != TYPE_DICTIONARY:
			continue
		var sanitized: Dictionary = _sanitize_doctrine_template_entry(template_variant)
		if sanitized.is_empty():
			continue
		var template_id: String = str(sanitized.get("id", ""))
		if template_id == "":
			continue
		doctrine_template_by_id[template_id] = sanitized


func set_location_templates(templates_by_id: Dictionary = {}) -> void:
	location_template_by_id.clear()
	location_template_by_kind.clear()

	for template_variant in templates_by_id.values():
		if typeof(template_variant) != TYPE_DICTIONARY:
			continue
		var sanitized: Dictionary = _sanitize_location_template_entry(template_variant)
		if sanitized.is_empty():
			continue
		var template_id: String = str(sanitized.get("id", ""))
		var kind: String = str(sanitized.get("kind", ""))
		if template_id == "" or kind == "":
			continue
		location_template_by_id[template_id] = sanitized
		if not location_template_by_kind.has(kind):
			location_template_by_kind[kind] = sanitized

	_apply_location_templates_to_existing_pois()


func set_allegiance_crisis_raid_modifiers(modifiers_by_allegiance: Dictionary = {}) -> void:
	allegiance_crisis_raid_mult_by_id.clear()
	for allegiance_variant in modifiers_by_allegiance.keys():
		var allegiance_id: String = str(allegiance_variant)
		if allegiance_id == "":
			continue
		var raid_mult: float = float(modifiers_by_allegiance.get(allegiance_variant, 1.0))
		allegiance_crisis_raid_mult_by_id[allegiance_id] = clampf(raid_mult, 0.65, 1.0)


func get_allegiance_crisis_raid_multiplier(allegiance_id: String) -> float:
	if allegiance_id == "":
		return 1.0
	return clampf(float(allegiance_crisis_raid_mult_by_id.get(allegiance_id, 1.0)), 0.65, 1.0)


func set_allegiance_recovery_defense_modifiers(modifiers_by_allegiance: Dictionary = {}) -> void:
	allegiance_recovery_defense_delta_by_id.clear()
	for allegiance_variant in modifiers_by_allegiance.keys():
		var allegiance_id: String = str(allegiance_variant)
		if allegiance_id == "":
			continue
		var defense_delta: float = float(modifiers_by_allegiance.get(allegiance_variant, 0.0))
		allegiance_recovery_defense_delta_by_id[allegiance_id] = clampf(defense_delta, 0.0, 0.24)


func get_allegiance_recovery_defense_delta(allegiance_id: String) -> float:
	if allegiance_id == "":
		return 0.0
	return clampf(float(allegiance_recovery_defense_delta_by_id.get(allegiance_id, 0.0)), 0.0, 0.24)


func set_mending_state(modifiers_by_allegiance: Dictionary = {}, suppressed_pairs: Array = []) -> void:
	allegiance_mending_modifiers_by_id.clear()
	for allegiance_variant in modifiers_by_allegiance.keys():
		var allegiance_id: String = str(allegiance_variant)
		if allegiance_id == "":
			continue
		var raw_modifiers: Dictionary = modifiers_by_allegiance.get(allegiance_variant, {})
		var target_allegiance_id: String = str(raw_modifiers.get("target_allegiance_id", ""))
		allegiance_mending_modifiers_by_id[allegiance_id] = {
			"target_allegiance_id": target_allegiance_id,
			"raid_weight_delta": clampf(float(raw_modifiers.get("raid_weight_delta", 0.0)), -0.18, 0.0),
			"bounty_weight_delta": clampf(float(raw_modifiers.get("bounty_weight_delta", 0.0)), -0.20, 0.0)
		}

	vendetta_suppressed_pair_keys.clear()
	for pair_variant in suppressed_pairs:
		var pair: Dictionary = pair_variant
		var source_allegiance_id: String = str(pair.get("source_allegiance_id", ""))
		var target_allegiance_id: String = str(pair.get("target_allegiance_id", ""))
		if source_allegiance_id == "" or target_allegiance_id == "":
			continue
		vendetta_suppressed_pair_keys[_mending_pair_key(source_allegiance_id, target_allegiance_id)] = true


func get_allegiance_mending_modifiers(
	source_allegiance_id: String,
	target_allegiance_id: String = ""
) -> Dictionary:
	if source_allegiance_id == "":
		return {
			"active": false,
			"target_allegiance_id": "",
			"raid_weight_delta": 0.0,
			"bounty_weight_delta": 0.0
		}
	var modifiers: Dictionary = allegiance_mending_modifiers_by_id.get(source_allegiance_id, {})
	if modifiers.is_empty():
		return {
			"active": false,
			"target_allegiance_id": "",
			"raid_weight_delta": 0.0,
			"bounty_weight_delta": 0.0
		}

	var linked_target: String = str(modifiers.get("target_allegiance_id", ""))
	if target_allegiance_id != "" and linked_target != "" and linked_target != target_allegiance_id:
		return {
			"active": false,
			"target_allegiance_id": linked_target,
			"raid_weight_delta": 0.0,
			"bounty_weight_delta": 0.0
		}

	return {
		"active": true,
		"target_allegiance_id": linked_target,
		"raid_weight_delta": float(modifiers.get("raid_weight_delta", 0.0)),
		"bounty_weight_delta": float(modifiers.get("bounty_weight_delta", 0.0))
	}


func set_neutral_gate_response_pull_modifiers(
	human_multiplier: float = 1.0,
	monster_multiplier: float = 1.0
) -> void:
	neutral_gate_response_pull_human_mult = clampf(human_multiplier, 0.80, 1.35)
	neutral_gate_response_pull_monster_mult = clampf(monster_multiplier, 0.80, 1.35)


func apply_neutral_gate_open_duration_delta(delta_seconds: float, time_seconds: float) -> float:
	if neutral_gate_status != "open":
		return 0.0

	var before_remaining: float = max(0.0, neutral_gate_open_until - time_seconds)
	var next_open_until: float = neutral_gate_open_until + delta_seconds
	var max_open_until: float = time_seconds + neutral_gate_open_duration * 1.55
	var min_open_until: float = time_seconds + 0.70
	neutral_gate_open_until = clampf(next_open_until, min_open_until, max_open_until)
	var after_remaining: float = max(0.0, neutral_gate_open_until - time_seconds)
	return after_remaining - before_remaining


func request_neutral_gate_bonus_breach(_time_seconds: float) -> bool:
	if neutral_gate_status != "open":
		return false
	if neutral_gate_breach_pending:
		return false
	if neutral_gate_bonus_breach_used:
		return false
	neutral_gate_breach_pending = true
	neutral_gate_bonus_breach_used = true
	return true


func set_bounty_state(
	active: bool,
	source_faction: String = "",
	source_allegiance_id: String = "",
	source_poi: String = "",
	target_position: Vector3 = Vector3.ZERO,
	target_actor_id: int = 0,
	target_label: String = "",
	target_faction: String = "",
	target_allegiance_id: String = ""
) -> void:
	if not active:
		bounty_state.clear()
		return
	bounty_state = {
		"active": true,
		"source_faction": source_faction,
		"source_allegiance_id": source_allegiance_id,
		"source_poi": source_poi,
		"target_position": target_position,
		"target_actor_id": target_actor_id,
		"target_label": target_label,
		"target_faction": target_faction,
		"target_allegiance_id": target_allegiance_id
	}


func set_convergence_state(
	active: bool,
	center_position: Vector3 = Vector3.ZERO,
	radius: float = 0.0,
	label: String = "",
	pull_weight: float = 0.0
) -> void:
	if not active:
		convergence_state.clear()
		return
	convergence_state = {
		"active": true,
		"center_position": center_position,
		"radius": max(0.0, radius),
		"label": label,
		"pull_weight": clampf(pull_weight, 0.20, 0.74)
	}


func set_alert_state(alert_entries: Array = []) -> void:
	alert_state_by_allegiance.clear()
	for entry_variant in alert_entries:
		var entry: Dictionary = entry_variant
		var allegiance_id: String = str(entry.get("allegiance_id", ""))
		if allegiance_id == "":
			continue
		alert_state_by_allegiance[allegiance_id] = {
			"active": true,
			"allegiance_id": allegiance_id,
			"faction": str(entry.get("faction", "")),
			"home_poi": str(entry.get("home_poi", "")),
			"center_position": entry.get("center_position", Vector3.ZERO),
			"radius": clampf(float(entry.get("radius", poi_guidance_distance * 0.50)), 4.0, poi_guidance_distance * 1.20),
			"cause": str(entry.get("cause", "")),
			"score": max(0.0, float(entry.get("score", 0.0))),
			"started_at": float(entry.get("started_at", 0.0)),
			"ends_at": float(entry.get("ends_at", 0.0)),
			"defense_weight_delta": clampf(float(entry.get("defense_weight_delta", 0.0)), 0.0, 0.18),
			"offense_weight_delta": clampf(float(entry.get("offense_weight_delta", 0.0)), -0.22, 0.0),
			"expedition_start_mult": clampf(float(entry.get("expedition_start_mult", 1.0)), 0.55, 1.0),
			"guidance_weight": clampf(float(entry.get("guidance_weight", 0.42)), 0.22, 0.78)
		}


func set_sanctuary_bastion_state(entries: Array = []) -> void:
	sanctuary_bastion_state_by_id.clear()
	for entry_variant in entries:
		var entry: Dictionary = entry_variant
		var site_id: int = int(entry.get("site_id", 0))
		if site_id <= 0:
			continue
		sanctuary_bastion_state_by_id[str(site_id)] = {
			"active": true,
			"site_id": site_id,
			"site_type": str(entry.get("site_type", "")),
			"label": str(entry.get("label", "site")),
			"faction": str(entry.get("faction", "")),
			"center_position": entry.get("center_position", Vector3.ZERO),
			"radius": clampf(float(entry.get("radius", poi_guidance_distance * 0.45)), 4.0, poi_guidance_distance * 1.25),
			"cause": str(entry.get("cause", "")),
			"score": max(0.0, float(entry.get("score", 0.0))),
			"started_at": float(entry.get("started_at", 0.0)),
			"ends_at": float(entry.get("ends_at", 0.0)),
			"guidance_weight": clampf(float(entry.get("guidance_weight", 0.40)), 0.18, 0.72)
		}


func set_taboo_state(entries: Array = []) -> void:
	taboo_state_by_id.clear()
	for entry_variant in entries:
		var entry: Dictionary = entry_variant
		var taboo_id: int = int(entry.get("taboo_id", 0))
		if taboo_id <= 0:
			continue
		taboo_state_by_id[str(taboo_id)] = {
			"active": true,
			"taboo_id": taboo_id,
			"taboo_type": str(entry.get("taboo_type", "")),
			"label": str(entry.get("label", "taboo")),
			"center_position": entry.get("center_position", Vector3.ZERO),
			"radius": clampf(float(entry.get("radius", poi_guidance_distance * 0.42)), 4.0, poi_guidance_distance * 1.20),
			"cause": str(entry.get("cause", "")),
			"score": max(0.0, float(entry.get("score", 0.0))),
			"started_at": float(entry.get("started_at", 0.0)),
			"ends_at": float(entry.get("ends_at", 0.0)),
			"guidance_weight": clampf(float(entry.get("guidance_weight", 0.34)), 0.18, 0.72)
		}


func get_taboo_avoidance_guidance(actor: Actor) -> Dictionary:
	if actor == null or actor.is_dead:
		return {}
	if taboo_state_by_id.is_empty():
		return {}

	var best: Dictionary = {}
	var best_weight: float = 0.0
	for runtime_variant in taboo_state_by_id.values():
		var runtime: Dictionary = runtime_variant
		var taboo_type: String = str(runtime.get("taboo_type", ""))
		if taboo_type not in ["forbidden_site", "cursed_warning"]:
			continue

		var center: Vector3 = runtime.get("center_position", actor.global_position)
		var radius: float = clampf(float(runtime.get("radius", poi_guidance_distance * 0.42)), 4.0, poi_guidance_distance * 1.20)
		var distance: float = actor.global_position.distance_to(center)
		if distance > radius * 1.95:
			continue

		var low_resources: bool = actor.hp <= actor.max_hp * 0.72 or actor.energy <= actor.max_energy * 0.52
		var prudent_profile: bool = actor.faction == "human" or low_resources
		if taboo_type == "forbidden_site" and actor.faction != "human" and not low_resources:
			continue
		if taboo_type == "cursed_warning" and actor.faction == "monster" and actor.is_champion and not low_resources:
			continue
		if taboo_type == "cursed_warning" and not prudent_profile and actor.faction != "human":
			continue

		var pull_weight: float = clampf(float(runtime.get("guidance_weight", 0.34)), 0.18, 0.72)
		if taboo_type == "forbidden_site":
			if actor.faction == "human":
				pull_weight += 0.06
			else:
				pull_weight += 0.02
		else:
			if actor.faction == "human":
				pull_weight += 0.10
			else:
				pull_weight += 0.04
		if distance <= radius * 0.95:
			pull_weight += 0.08
		if low_resources:
			pull_weight += 0.08
		if actor.is_champion and not low_resources:
			pull_weight -= 0.06
		pull_weight = clampf(pull_weight, 0.18, 0.78)
		if pull_weight <= best_weight:
			continue

		var away_dir: Vector3 = actor.global_position - center
		if away_dir.length_squared() <= 0.01:
			away_dir = Vector3(randf_range(-1.0, 1.0), 0.0, randf_range(-1.0, 1.0))
		away_dir.y = 0.0
		var avoid_step: float = clampf(radius * 0.90, 3.0, 9.0)
		best_weight = pull_weight
		best = {
			"reason": "taboo:%s" % taboo_type,
			"target_position": clamp_to_world(snap_to_nav_grid(actor.global_position + away_dir.normalized() * avoid_step)),
			"distance": distance,
			"weight": pull_weight
		}

	return best


func get_sanctuary_bastion_guidance(actor: Actor) -> Dictionary:
	if actor == null or actor.is_dead:
		return {}
	if sanctuary_bastion_state_by_id.is_empty():
		return {}

	var best: Dictionary = {}
	var best_weight: float = 0.0
	for runtime_variant in sanctuary_bastion_state_by_id.values():
		var runtime: Dictionary = runtime_variant
		var site_type: String = str(runtime.get("site_type", ""))
		if site_type == "":
			continue
		if site_type == "sanctuary_site" and actor.faction != "human":
			continue
		if site_type == "dark_bastion" and actor.faction != "monster":
			continue

		var center: Vector3 = runtime.get("center_position", actor.global_position)
		var distance: float = actor.global_position.distance_to(center)
		var radius: float = clampf(float(runtime.get("radius", poi_guidance_distance * 0.45)), 4.0, poi_guidance_distance * 1.25)
		if distance > radius * 2.0:
			continue

		var pull_weight: float = clampf(float(runtime.get("guidance_weight", 0.40)), 0.18, 0.72)
		if distance > radius * 1.05:
			pull_weight += 0.06
		if site_type == "sanctuary_site" and (
			actor.hp <= actor.max_hp * 0.74 or actor.energy <= actor.max_energy * 0.52
		):
			pull_weight += 0.05
		if site_type == "dark_bastion" and actor.hp >= actor.max_hp * 0.62:
			pull_weight += 0.04
		pull_weight = clampf(pull_weight, 0.18, 0.78)
		if pull_weight <= best_weight:
			continue

		best_weight = pull_weight
		var jitter := Vector3(randf_range(-1.4, 1.4), 0.0, randf_range(-1.4, 1.4))
		var base_reason: String = "sanctuary" if site_type == "sanctuary_site" else "bastion"
		best = {
			"reason": "%s:%s" % [base_reason, str(runtime.get("cause", "watch"))],
			"target_position": clamp_to_world(snap_to_nav_grid(center + jitter)),
			"distance": distance,
			"weight": pull_weight
		}

	return best


func get_alert_defense_delta(allegiance_id: String, time_seconds: float = 0.0) -> float:
	var runtime: Dictionary = _get_alert_runtime_for_allegiance(allegiance_id, time_seconds)
	if runtime.is_empty():
		return 0.0
	return clampf(float(runtime.get("defense_weight_delta", 0.0)), 0.0, 0.18)


func get_alert_offense_weight_delta(allegiance_id: String, time_seconds: float = 0.0) -> float:
	var runtime: Dictionary = _get_alert_runtime_for_allegiance(allegiance_id, time_seconds)
	if runtime.is_empty():
		return 0.0
	return clampf(float(runtime.get("offense_weight_delta", 0.0)), -0.22, 0.0)


func get_alert_expedition_start_multiplier(allegiance_id: String, time_seconds: float = 0.0) -> float:
	var runtime: Dictionary = _get_alert_runtime_for_allegiance(allegiance_id, time_seconds)
	if runtime.is_empty():
		return 1.0
	return clampf(float(runtime.get("expedition_start_mult", 1.0)), 0.55, 1.0)


func get_alert_guidance(actor: Actor) -> Dictionary:
	if actor == null or actor.is_dead:
		return {}
	if actor.allegiance_id == "":
		return {}

	var runtime: Dictionary = _get_alert_runtime_for_allegiance(actor.allegiance_id)
	if runtime.is_empty():
		return {}

	var center: Vector3 = runtime.get("center_position", actor.global_position)
	var distance: float = actor.global_position.distance_to(center)
	if distance > poi_guidance_distance * 2.10:
		return {}

	var radius: float = clampf(float(runtime.get("radius", poi_guidance_distance * 0.50)), 4.0, poi_guidance_distance * 1.20)
	var pull_weight: float = clampf(float(runtime.get("guidance_weight", 0.42)), 0.22, 0.78)
	if distance > radius * 1.08:
		pull_weight += 0.08
	if actor.hp <= actor.max_hp * 0.76 or actor.energy <= actor.max_energy * 0.50:
		pull_weight += 0.08

	var jitter := Vector3(randf_range(-1.6, 1.6), 0.0, randf_range(-1.6, 1.6))
	return {
		"reason": "alert:%s" % str(runtime.get("cause", "watch")),
		"target_position": clamp_to_world(snap_to_nav_grid(center + jitter)),
		"distance": distance,
		"weight": clampf(pull_weight, 0.22, 0.84)
	}


func clamp_to_world(position: Vector3) -> Vector3:
	var half_size: float = (map_size * 0.5) - 1.0
	return Vector3(
		clamp(position.x, -half_size, half_size),
		0.0,
		clamp(position.z, -half_size, half_size)
	)


func snap_to_nav_grid(position: Vector3) -> Vector3:
	return Vector3(
		round(position.x / nav_cell_size) * nav_cell_size,
		0.0,
		round(position.z / nav_cell_size) * nav_cell_size
	)


func get_spawn_point(faction: String) -> Vector3:
	var points: Array[Vector3] = human_spawn_points if faction == "human" else monster_spawn_points
	if points.is_empty():
		return Vector3.ZERO

	var base_point: Vector3 = points[randi() % points.size()]
	var jitter := Vector3(randf_range(-2.0, 2.0), 0.0, randf_range(-2.0, 2.0))
	return clamp_to_world(snap_to_nav_grid(base_point + jitter))


func get_wander_point(origin: Vector3) -> Vector3:
	var offset := Vector3(randf_range(-wander_radius, wander_radius), 0.0, randf_range(-wander_radius, wander_radius))
	if offset.length() < 2.0:
		offset = offset.normalized() * 2.0
	return clamp_to_world(snap_to_nav_grid(origin + offset))


func find_nearest_enemy(source: Actor, all_actors: Array, max_distance: float) -> Actor:
	var closest: Actor = null
	var closest_distance_sq: float = max_distance * max_distance

	for other in all_actors:
		if other == null or other == source or other.is_dead:
			continue
		if not source.is_enemy(other):
			continue

		var dist_sq: float = source.global_position.distance_squared_to(other.global_position)
		if dist_sq <= closest_distance_sq:
			closest = other
			closest_distance_sq = dist_sq

	return closest


func get_poi_guidance(actor_position: Vector3, faction: String) -> Dictionary:
	if pois.is_empty():
		return {}

	var selected: Dictionary = {}
	for poi in pois:
		if _is_neutral_gate_poi(poi):
			continue
		if str(poi.get("faction_hint", "")) == faction:
			selected = poi
			break

	if selected.is_empty():
		selected = _get_nearest_poi(actor_position, true)

	if selected.is_empty():
		return {}

	var poi_position: Vector3 = selected.get("position", actor_position)
	var distance: float = actor_position.distance_to(poi_position)
	if distance > poi_guidance_distance:
		return {}

	var jitter := Vector3(randf_range(-2.0, 2.0), 0.0, randf_range(-2.0, 2.0))
	var target_position := clamp_to_world(snap_to_nav_grid(poi_position + jitter))
	return {
		"name": str(selected.get("name", "poi")),
		"target_position": target_position,
		"distance": distance
	}


func get_neutral_gate_guidance(actor: Actor) -> Dictionary:
	if actor == null or actor.is_dead:
		return {}
	if neutral_gate_status != "open":
		return {}

	var gate_name: String = _find_neutral_gate_poi_name()
	if gate_name == "":
		return {}
	var gate_poi: Dictionary = _get_poi_by_name(gate_name)
	if gate_poi.is_empty():
		return {}

	var gate_position: Vector3 = gate_poi.get("position", actor.global_position)
	var gate_radius: float = float(gate_poi.get("radius", 7.0))
	var distance: float = actor.global_position.distance_to(gate_position)
	if distance > poi_guidance_distance * 1.55:
		return {}

	var is_cautious: bool = (
		not actor.is_champion
		and not actor.has_relic()
		and not actor.is_special_arrival()
		and actor.notoriety < 44.0
		and (
			actor.hp <= actor.max_hp * 0.88
			or actor.energy <= actor.max_energy * 0.62
		)
	)

	if is_cautious and distance <= gate_radius * 1.35:
		var away_vector := actor.global_position - gate_position
		away_vector.y = 0.0
		if away_vector.length() < 0.1:
			away_vector = Vector3(randf_range(-1.0, 1.0), 0.0, randf_range(-1.0, 1.0))
		var avoid_target := actor.global_position + away_vector.normalized() * (gate_radius + 3.4)
		return {
			"kind": "avoid",
			"reason": "neutral_gate_avoid",
			"target_position": clamp_to_world(snap_to_nav_grid(avoid_target)),
			"distance": distance,
			"weight": 0.58
		}

	var pull_weight: float = 0.34
	if actor.is_champion or actor.has_relic() or actor.is_special_arrival() or actor.notoriety >= 48.0:
		pull_weight += 0.18
	if distance <= gate_radius * 1.20:
		pull_weight += 0.07
	if world_event_visual_id == "monster_frenzy" and actor.faction == "human":
		pull_weight += 0.06
	elif world_event_visual_id == "sanctuary_calm" and actor.faction == "monster":
		pull_weight += 0.06
	if actor.faction == "human":
		pull_weight *= neutral_gate_response_pull_human_mult
	elif actor.faction == "monster":
		pull_weight *= neutral_gate_response_pull_monster_mult

	var jitter := Vector3(randf_range(-2.2, 2.2), 0.0, randf_range(-2.2, 2.2))
	return {
		"kind": "investigate",
		"reason": "neutral_gate_pull",
		"target_position": clamp_to_world(snap_to_nav_grid(gate_position + jitter)),
		"distance": distance,
		"weight": clampf(pull_weight, 0.24, 0.72)
	}


func get_poi_population_snapshot(actors: Array) -> Dictionary:
	var snapshot: Dictionary = {}

	for poi in pois:
		var poi_name: String = str(poi.get("name", "poi"))
		var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
		var poi_radius: float = float(poi.get("radius", 7.0))
		var humans: int = 0
		var monsters: int = 0

		for actor in actors:
			if actor == null or actor.is_dead:
				continue
			if actor.global_position.distance_to(poi_pos) > poi_radius:
				continue

			if actor.faction == "human":
				humans += 1
			elif actor.faction == "monster":
				monsters += 1

		snapshot[poi_name] = {
			"human": humans,
			"monster": monsters
		}

	return snapshot


func get_raid_guidance(
	actor_position: Vector3,
	faction: String,
	allegiance_id: String = "",
	home_poi: String = ""
) -> Dictionary:
	if not bool(poi_raid_state.get("active", false)):
		return {}
	if str(poi_raid_state.get("attacker_faction", "")) != faction:
		return {}

	var target_name: String = str(poi_raid_state.get("target_poi", ""))
	var target_poi: Dictionary = _get_poi_by_name(target_name)
	if target_poi.is_empty():
		return {}

	var target_position: Vector3 = target_poi.get("position", actor_position)
	var distance: float = actor_position.distance_to(target_position)
	if distance > poi_guidance_distance * 1.55:
		return {}

	var jitter := Vector3(randf_range(-2.3, 2.3), 0.0, randf_range(-2.3, 2.3))
	var source_poi: String = str(poi_raid_state.get("source_poi", ""))
	var target_allegiance_id: String = str(poi_allegiance_id.get(target_name, ""))
	var weight: float = 0.74
	if allegiance_id != "":
		if home_poi == source_poi:
			weight += 0.12
		elif home_poi != "":
			weight -= 0.16
		var doctrine_modifiers: Dictionary = get_allegiance_doctrine_modifiers(allegiance_id)
		weight += float(doctrine_modifiers.get("raid_weight_delta", 0.0))
		var project_modifiers: Dictionary = get_allegiance_project_modifiers(allegiance_id)
		weight += float(project_modifiers.get("raid_weight_delta", 0.0))
		var vendetta_modifiers: Dictionary = get_allegiance_vendetta_modifiers(allegiance_id, target_allegiance_id)
		weight += float(vendetta_modifiers.get("raid_weight_delta", 0.0))
		var mending_modifiers: Dictionary = get_allegiance_mending_modifiers(allegiance_id, target_allegiance_id)
		weight += float(mending_modifiers.get("raid_weight_delta", 0.0))
		weight *= get_allegiance_crisis_raid_multiplier(allegiance_id)
		weight += get_alert_offense_weight_delta(allegiance_id)
	weight *= raid_pressure_global_multiplier
	if faction == "human":
		weight *= raid_pressure_human_multiplier
	elif faction == "monster":
		weight *= raid_pressure_monster_multiplier

	return {
		"reason": "raid_pressure:%s->%s" % [source_poi if source_poi != "" else "src", target_name],
		"target_position": clamp_to_world(snap_to_nav_grid(target_position + jitter)),
		"distance": distance,
		"weight": clampf(weight, 0.28, 0.92)
	}


func get_active_raid_state() -> Dictionary:
	return poi_raid_state.duplicate(true)


func get_bounty_guidance(
	actor_position: Vector3,
	faction: String,
	allegiance_id: String = "",
	home_poi: String = ""
) -> Dictionary:
	if not bool(bounty_state.get("active", false)):
		return {}
	if str(bounty_state.get("source_faction", "")) != faction:
		return {}

	var target_position: Vector3 = bounty_state.get("target_position", actor_position)
	var distance: float = actor_position.distance_to(target_position)
	if distance > poi_guidance_distance * 1.90:
		return {}

	var weight: float = 0.56
	var source_allegiance_id: String = str(bounty_state.get("source_allegiance_id", ""))
	var source_poi: String = str(bounty_state.get("source_poi", ""))
	var target_allegiance_id: String = str(bounty_state.get("target_allegiance_id", ""))
	if allegiance_id != "" and source_allegiance_id != "" and allegiance_id == source_allegiance_id:
		weight += 0.14
	if home_poi != "" and source_poi != "" and home_poi == source_poi:
		weight += 0.07
	if bool(poi_raid_state.get("active", false)) and str(poi_raid_state.get("attacker_faction", "")) == faction:
		weight += 0.06
	if allegiance_id != "":
		var vendetta_modifiers: Dictionary = get_allegiance_vendetta_modifiers(allegiance_id, target_allegiance_id)
		weight += float(vendetta_modifiers.get("bounty_weight_delta", 0.0))
		var mending_modifiers: Dictionary = get_allegiance_mending_modifiers(allegiance_id, target_allegiance_id)
		weight += float(mending_modifiers.get("bounty_weight_delta", 0.0))
		weight += get_alert_offense_weight_delta(allegiance_id)

	var jitter := Vector3(randf_range(-1.8, 1.8), 0.0, randf_range(-1.8, 1.8))
	return {
		"reason": "bounty_hunt:%s" % str(bounty_state.get("target_label", "marked_target")),
		"target_position": clamp_to_world(snap_to_nav_grid(target_position + jitter)),
		"distance": distance,
		"weight": clampf(weight, 0.26, 0.88)
	}


func get_convergence_guidance(actor: Actor) -> Dictionary:
	if actor == null or actor.is_dead:
		return {}
	if not bool(convergence_state.get("active", false)):
		return {}

	var center: Vector3 = convergence_state.get("center_position", actor.global_position)
	var distance: float = actor.global_position.distance_to(center)
	if distance > poi_guidance_distance * 1.85:
		return {}

	var pull_weight: float = float(convergence_state.get("pull_weight", 0.40))
	var radius: float = max(0.0, float(convergence_state.get("radius", 0.0)))
	if radius > 0.0 and distance <= radius * 1.18:
		pull_weight += 0.07
	if actor.is_champion or actor.has_relic() or actor.is_special_arrival():
		pull_weight += 0.05

	var jitter := Vector3(randf_range(-1.6, 1.6), 0.0, randf_range(-1.6, 1.6))
	return {
		"reason": "convergence_pull:%s" % str(convergence_state.get("label", "crossroads")),
		"target_position": clamp_to_world(snap_to_nav_grid(center + jitter)),
		"distance": distance,
		"weight": clampf(pull_weight, 0.20, 0.78)
	}


func get_allegiance_defense_guidance(
	actor_position: Vector3,
	faction: String,
	home_poi: String
) -> Dictionary:
	if home_poi == "":
		return {}
	if not bool(poi_raid_state.get("active", false)):
		return {}
	if str(poi_raid_state.get("defender_faction", "")) != faction:
		return {}
	if str(poi_raid_state.get("target_poi", "")) != home_poi:
		return {}

	var home := _get_poi_by_name(home_poi)
	if home.is_empty():
		return {}
	if str(poi_structure_state.get(home_poi, "")) == "":
		return {}

	var home_pos: Vector3 = home.get("position", actor_position)
	if actor_position.distance_to(home_pos) > poi_guidance_distance * 1.35:
		return {}

	var jitter := Vector3(randf_range(-1.8, 1.8), 0.0, randf_range(-1.8, 1.8))
	var weight: float = 0.68
	var home_allegiance_id: String = str(poi_allegiance_id.get(home_poi, ""))
	if home_allegiance_id != "":
		var doctrine_modifiers: Dictionary = get_allegiance_doctrine_modifiers(home_allegiance_id)
		weight += float(doctrine_modifiers.get("defense_weight_delta", 0.0))
		var project_modifiers: Dictionary = get_allegiance_project_modifiers(home_allegiance_id)
		weight += float(project_modifiers.get("defense_weight_delta", 0.0))
		weight += get_allegiance_recovery_defense_delta(home_allegiance_id)
		weight += get_alert_defense_delta(home_allegiance_id)
	return {
		"reason": "allegiance_defend:%s" % home_poi,
		"target_position": clamp_to_world(snap_to_nav_grid(home_pos + jitter)),
		"weight": clampf(weight, 0.24, 0.92)
	}


func get_active_allegiances(time_seconds: float = -1.0) -> Array[Dictionary]:
	var active: Array[Dictionary] = []
	for poi in pois:
		var poi_name: String = str(poi.get("name", ""))
		if poi_name == "":
			continue
		var structure_state: String = str(poi_structure_state.get(poi_name, ""))
		if structure_state == "":
			continue
		var allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))
		if allegiance_id == "":
			continue
		var alert_runtime: Dictionary = _get_alert_runtime_for_allegiance(allegiance_id, time_seconds)
		var alert_active: bool = not alert_runtime.is_empty()
		var alert_remaining: float = 0.0
		if time_seconds >= 0.0:
			alert_remaining = max(0.0, float(alert_runtime.get("ends_at", time_seconds)) - time_seconds)
		var faction_template: Dictionary = get_allegiance_faction_template(allegiance_id)
		var template_tags: Array = faction_template.get("tags", [])
		var poi_tags_variant: Variant = poi.get("tags", [])
		var poi_tags: Array = []
		if typeof(poi_tags_variant) == TYPE_ARRAY:
			poi_tags = poi_tags_variant
			poi_tags = poi_tags.duplicate(true)
		var doctrine_id: String = get_allegiance_doctrine(allegiance_id)
		active.append({
			"allegiance_id": allegiance_id,
			"faction": str(poi_structure_faction.get(poi_name, "")),
			"home_poi": poi_name,
			"home_poi_label": str(poi.get("label", poi_name)),
			"home_poi_tags": poi_tags,
			"position": poi.get("position", Vector3.ZERO),
			"structure_state": structure_state,
			"doctrine": doctrine_id,
			"doctrine_label": get_doctrine_label(doctrine_id, doctrine_id),
			"doctrine_tags": get_doctrine_tags(doctrine_id),
			"project": get_allegiance_project(allegiance_id),
			"project_remaining": get_allegiance_project_remaining(allegiance_id, time_seconds),
			"vendetta_target": get_allegiance_vendetta_target(allegiance_id),
			"vendetta_remaining": get_allegiance_vendetta_remaining(allegiance_id, time_seconds),
			"faction_template_id": str(faction_template.get("id", "")),
			"faction_template_label": str(faction_template.get("label", "")),
			"faction_template_tags": template_tags.duplicate(true),
			"alert_active": alert_active,
			"alert_cause": str(alert_runtime.get("cause", "")),
			"alert_remaining": alert_remaining
		})
	return active


func resolve_actor_allegiance(actor: Actor) -> Dictionary:
	var active_allegiances: Array[Dictionary] = get_active_allegiances()
	var current_id: String = actor.allegiance_id
	var current_home: String = actor.home_poi

	var by_id: Dictionary = {}
	for allegiance in active_allegiances:
		by_id[str(allegiance.get("allegiance_id", ""))] = allegiance

	if current_id != "":
		var current: Dictionary = by_id.get(current_id, {})
		if current.is_empty() or str(current.get("faction", "")) != actor.faction:
			return {
				"allegiance_id": "",
				"home_poi": "",
				"changed": true,
				"reason": "anchor_lost"
			}
		var expected_home: String = str(current.get("home_poi", current_home))
		if current_home != expected_home:
			return {
				"allegiance_id": current_id,
				"home_poi": expected_home,
				"changed": true,
				"reason": "home_sync"
			}
		return {
			"allegiance_id": current_id,
			"home_poi": current_home,
			"changed": false,
			"reason": "stable"
		}

	var selected: Dictionary = {}
	var best_distance: float = INF
	var assign_distance: float = poi_guidance_distance * 1.15
	for allegiance in active_allegiances:
		if str(allegiance.get("faction", "")) != actor.faction:
			continue
		var center: Vector3 = allegiance.get("position", actor.global_position)
		var distance: float = actor.global_position.distance_to(center)
		if distance <= assign_distance and distance < best_distance:
			selected = allegiance
			best_distance = distance

	if selected.is_empty():
		return {
			"allegiance_id": "",
			"home_poi": "",
			"changed": false,
			"reason": "no_anchor"
		}

	return {
		"allegiance_id": str(selected.get("allegiance_id", "")),
		"home_poi": str(selected.get("home_poi", "")),
		"changed": true,
		"reason": "assigned_near_anchor"
	}


func update_poi_runtime(actors: Array, time_seconds: float) -> Dictionary:
	var snapshot: Dictionary = {}
	var events: Array[Dictionary] = []

	for poi in pois:
		var poi_name: String = str(poi.get("name", "poi"))
		var counts: Dictionary = _count_poi_occupancy(poi, actors)
		var human_count: int = int(counts.get("human", 0))
		var monster_count: int = int(counts.get("monster", 0))
		var human_champions: int = int(counts.get("human_champions", 0))
		var monster_champions: int = int(counts.get("monster_champions", 0))
		var total_count: int = human_count + monster_count
		var status: String = _compute_poi_status(human_count, monster_count)
		var activity: String = _compute_activity_level(total_count)
		var dominant_faction: String = _dominant_faction_from_status(status)
		var dominance_seconds: float = _update_dominance_duration(poi_name, dominant_faction, time_seconds)
		var influence_kind: String = _compute_influence_kind(str(poi.get("kind", "")), dominant_faction, dominance_seconds)
		var influence_active: bool = influence_kind != ""
		var dominant_presence: int = human_count if dominant_faction == "human" else monster_count
		var dominant_champions: int = human_champions if dominant_faction == "human" else monster_champions
		var structure_runtime: Dictionary = _update_structure_runtime(
			poi_name,
			str(poi.get("kind", "")),
			dominant_faction,
			dominance_seconds,
			influence_active,
			dominant_presence,
			dominant_champions,
			time_seconds
		)
		var structure_state: String = str(structure_runtime.get("state", ""))
		var structure_active: bool = bool(structure_runtime.get("active", false))
		var structure_seconds: float = float(structure_runtime.get("structure_seconds", 0.0))
		var allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))

		snapshot[poi_name] = {
			"human": human_count,
			"monster": monster_count,
			"total": total_count,
			"status": status,
			"activity": activity,
			"dominant_faction": dominant_faction,
			"dominance_seconds": dominance_seconds,
			"influence_active": influence_active,
			"influence_kind": influence_kind,
			"structure_state": structure_state,
			"structure_active": structure_active,
			"structure_seconds": structure_seconds,
			"allegiance_id": allegiance_id,
			"faction_template_id": _get_faction_template_id_for_allegiance(allegiance_id),
			"allegiance_doctrine": get_allegiance_doctrine(allegiance_id),
			"allegiance_project": get_allegiance_project(allegiance_id),
			"allegiance_project_remaining": get_allegiance_project_remaining(allegiance_id, time_seconds),
			"allegiance_vendetta_target": get_allegiance_vendetta_target(allegiance_id),
			"allegiance_vendetta_remaining": get_allegiance_vendetta_remaining(allegiance_id, time_seconds)
		}

		var previous_status: String = str(poi_runtime_status.get(poi_name, ""))
		if previous_status != "" and previous_status != status:
			if status == "contested":
				events.append({
					"kind": "contest_started",
					"poi": poi_name,
					"from": previous_status,
					"to": status
				})
			elif status in ["human_dominant", "monster_dominant"]:
				events.append({
					"kind": "domination_changed",
					"poi": poi_name,
					"from": previous_status,
					"to": status
				})
			elif previous_status == "contested" and status == "calm":
				events.append({
					"kind": "contest_resolved",
					"poi": poi_name,
					"from": previous_status,
					"to": status
				})

		var previous_active: bool = bool(poi_influence_active.get(poi_name, false))
		if previous_active != influence_active:
			if influence_active:
				events.append({
					"kind": "influence_activated",
					"poi": poi_name,
					"faction": dominant_faction,
					"influence_kind": influence_kind,
					"dominance_seconds": dominance_seconds
				})
			else:
				events.append({
					"kind": "influence_deactivated",
					"poi": poi_name
				})

		var structure_events: Array = structure_runtime.get("events", [])
		for structure_event in structure_events:
			events.append(structure_event)

		poi_runtime_status[poi_name] = status
		poi_influence_active[poi_name] = influence_active

	var project_runtime: Dictionary = _update_allegiance_projects_runtime(snapshot, time_seconds)
	var project_events: Array = project_runtime.get("events", [])
	for project_event in project_events:
		events.append(project_event)

	var gate_runtime: Dictionary = _update_neutral_gate_runtime(snapshot, time_seconds)
	var gate_events: Array = gate_runtime.get("events", [])
	for gate_event in gate_events:
		events.append(gate_event)

	var raid_runtime: Dictionary = _update_raid_runtime(snapshot, time_seconds)
	var raid_events: Array = raid_runtime.get("events", [])
	for raid_event in raid_events:
		events.append(raid_event)

	var vendetta_runtime: Dictionary = _update_vendetta_runtime(snapshot, time_seconds)
	var vendetta_events: Array = vendetta_runtime.get("events", [])
	for vendetta_event in vendetta_events:
		events.append(vendetta_event)

	for poi_name in snapshot.keys():
		var details: Dictionary = snapshot.get(poi_name, {})
		var details_allegiance_id: String = str(details.get("allegiance_id", ""))
		var alert_runtime: Dictionary = _get_alert_runtime_for_allegiance(details_allegiance_id, time_seconds)
		details["allegiance_doctrine"] = get_allegiance_doctrine(details_allegiance_id)
		details["allegiance_project"] = get_allegiance_project(details_allegiance_id)
		details["allegiance_project_remaining"] = get_allegiance_project_remaining(details_allegiance_id, time_seconds)
		details["allegiance_vendetta_target"] = get_allegiance_vendetta_target(details_allegiance_id)
		details["allegiance_vendetta_remaining"] = get_allegiance_vendetta_remaining(details_allegiance_id, time_seconds)
		details["allegiance_alert_active"] = not alert_runtime.is_empty()
		details["allegiance_alert_cause"] = str(alert_runtime.get("cause", ""))
		details["allegiance_alert_remaining"] = max(
			0.0,
			float(alert_runtime.get("ends_at", time_seconds)) - time_seconds
		)
		if str(poi_name) == str(gate_runtime.get("poi", "")):
			details["gate_status"] = str(gate_runtime.get("status", "dormant"))
			details["gate_active"] = bool(gate_runtime.get("active", false))
			details["gate_remaining"] = float(gate_runtime.get("remaining", 0.0))
			details["gate_cooldown"] = float(gate_runtime.get("cooldown", 0.0))
			details["gate_open_count"] = int(gate_runtime.get("opened_total", 0))
			details["gate_close_count"] = int(gate_runtime.get("closed_total", 0))
			details["gate_breach_count"] = int(gate_runtime.get("breaches_total", 0))
		details["raid_role"] = _get_raid_role_for_poi(str(poi_name))
		snapshot[poi_name] = details
		_apply_poi_visual_state(
			str(poi_name),
			str(details.get("status", "calm")),
			int(details.get("total", 0)),
			time_seconds,
			bool(details.get("influence_active", false)),
			str(details.get("structure_state", "")),
			str(details.get("raid_role", "none")),
			str(details.get("gate_status", "dormant")),
			bool(details.get("gate_active", false))
		)

	return {
		"snapshot": snapshot,
		"events": events,
		"raid": poi_raid_state.duplicate(true)
	}


func get_active_poi_influences() -> Array[Dictionary]:
	var active: Array[Dictionary] = []

	for poi in pois:
		var poi_name: String = str(poi.get("name", "poi"))
		if not bool(poi_influence_active.get(poi_name, false)):
			continue

		var faction: String = str(poi_dominant_faction.get(poi_name, ""))
		var influence_kind: String = _compute_influence_kind(
			str(poi.get("kind", "")),
			faction,
			poi_influence_activation_time
		)
		if influence_kind == "":
			continue

		var structure_state: String = str(poi_structure_state.get(poi_name, ""))
		var structure_active: bool = structure_state != ""
		active.append({
			"name": poi_name,
			"position": poi.get("position", Vector3.ZERO),
			"radius": float(poi.get("radius", 7.0)),
			"faction": faction,
			"influence_kind": influence_kind,
			"structure_state": structure_state,
			"structure_active": structure_active
		})

	return active


func get_neutral_gate_runtime_state(time_seconds: float = 0.0) -> Dictionary:
	var gate_name: String = _find_neutral_gate_poi_name()
	var remaining: float = 0.0
	var cooldown: float = 0.0
	if neutral_gate_status == "open":
		remaining = max(0.0, neutral_gate_open_until - time_seconds)
	else:
		cooldown = max(0.0, neutral_gate_cooldown_until - time_seconds)
	return {
		"poi": gate_name,
		"status": neutral_gate_status,
		"active": neutral_gate_status == "open",
		"remaining": remaining,
		"cooldown": cooldown,
		"open_until": neutral_gate_open_until,
		"cooldown_until": neutral_gate_cooldown_until,
		"opened_total": neutral_gate_opened_total,
		"closed_total": neutral_gate_closed_total,
		"breaches_total": neutral_gate_breaches_total
	}


func get_allegiance_faction_template(allegiance_id: String) -> Dictionary:
	var template_id: String = _get_faction_template_id_for_allegiance(allegiance_id)
	if template_id == "":
		return {}
	if not faction_template_by_id.has(template_id):
		return {}
	return Dictionary(faction_template_by_id[template_id]).duplicate(true)


func _get_faction_template_id_for_allegiance(allegiance_id: String) -> String:
	if allegiance_id == "":
		return ""
	var linked_template_id: String = str(faction_template_id_by_allegiance.get(allegiance_id, ""))
	if linked_template_id != "" and faction_template_by_id.has(linked_template_id):
		return linked_template_id

	var allegiance_faction: String = ""
	for poi_name_variant in poi_allegiance_id.keys():
		var poi_name: String = str(poi_name_variant)
		if str(poi_allegiance_id.get(poi_name, "")) != allegiance_id:
			continue
		allegiance_faction = str(poi_structure_faction.get(poi_name, ""))
		if allegiance_faction != "":
			break
	if allegiance_faction == "":
		return ""

	var resolved_template_id: String = _resolve_faction_template_id_for_faction(allegiance_faction)
	if resolved_template_id != "":
		faction_template_id_by_allegiance[allegiance_id] = resolved_template_id
	return resolved_template_id


func _resolve_faction_template_id_for_faction(faction: String) -> String:
	if faction == "":
		return ""
	var template: Dictionary = faction_template_by_kind.get(faction, {})
	if template.is_empty():
		return ""
	return str(template.get("id", ""))


func _get_faction_doctrine_pool_for_kind(faction: String) -> Array[String]:
	if faction == "":
		return []
	var template: Dictionary = faction_template_by_kind.get(faction, {})
	if template.is_empty():
		return []
	var pool_variant: Variant = template.get("default_doctrine_pool", [])
	if typeof(pool_variant) != TYPE_ARRAY:
		return []
	var pool: Array = pool_variant
	var sanitized_pool: Array[String] = []
	for doctrine_variant in pool:
		if typeof(doctrine_variant) != TYPE_STRING:
			continue
		var doctrine: String = str(doctrine_variant)
		if not (doctrine in ALLEGIANCE_DOCTRINES):
			continue
		if doctrine in sanitized_pool:
			continue
		sanitized_pool.append(doctrine)
	return sanitized_pool


func _sanitize_faction_template_entry(template_data: Dictionary) -> Dictionary:
	var template_id: String = str(template_data.get("id", "")).strip_edges()
	var label: String = str(template_data.get("label", "")).strip_edges()
	var kind: String = str(template_data.get("kind", "")).strip_edges()
	if template_id == "" or label == "" or kind == "":
		return {}
	if kind not in ["human", "monster"]:
		return {}

	var doctrine_pool_variant: Variant = template_data.get("default_doctrine_pool", [])
	if typeof(doctrine_pool_variant) != TYPE_ARRAY:
		return {}
	var doctrine_pool_raw: Array = doctrine_pool_variant
	var doctrine_pool: Array[String] = []
	for doctrine_variant in doctrine_pool_raw:
		if typeof(doctrine_variant) != TYPE_STRING:
			continue
		var doctrine: String = str(doctrine_variant).strip_edges()
		if not (doctrine in ALLEGIANCE_DOCTRINES):
			continue
		if doctrine in doctrine_pool:
			continue
		doctrine_pool.append(doctrine)
	if doctrine_pool.is_empty():
		return {}

	var project_bias: String = str(template_data.get("project_bias", "")).strip_edges()
	if project_bias != "" and not (project_bias in ALLEGIANCE_PROJECT_TYPES):
		project_bias = ""

	var tags_variant: Variant = template_data.get("tags", [])
	var tags: Array[String] = []
	if typeof(tags_variant) == TYPE_ARRAY:
		var tags_array: Array = tags_variant
		for tag_variant in tags_array:
			if typeof(tag_variant) != TYPE_STRING:
				continue
			var tag: String = str(tag_variant).strip_edges()
			if tag == "":
				continue
			tags.append(tag)

	var raid_bias: float = clampf(float(template_data.get("raid_bias", 0.0)), -0.25, 0.25)
	var defense_bias: float = clampf(float(template_data.get("defense_bias", 0.0)), -0.25, 0.25)
	var rally_bias: float = clampf(float(template_data.get("rally_bias", 0.0)), -0.25, 0.25)

	return {
		"id": template_id,
		"label": label,
		"kind": kind,
		"default_doctrine_pool": doctrine_pool,
		"project_bias": project_bias,
		"raid_bias": raid_bias,
		"defense_bias": defense_bias,
		"rally_bias": rally_bias,
		"tags": tags
	}


func _sanitize_doctrine_template_entry(template_data: Dictionary) -> Dictionary:
	var template_id: String = str(template_data.get("id", "")).strip_edges()
	var label: String = str(template_data.get("label", "")).strip_edges()
	var kind: String = str(template_data.get("kind", "")).strip_edges()
	if template_id == "" or label == "" or kind == "":
		return {}
	if not (template_id in ALLEGIANCE_DOCTRINES):
		return {}
	if kind not in ["offense", "defense", "arcane"]:
		return {}

	for numeric_field in ["raid_bias", "defense_bias", "rally_bias", "magic_bias"]:
		var numeric_value: Variant = template_data.get(numeric_field, null)
		if typeof(numeric_value) != TYPE_INT and typeof(numeric_value) != TYPE_FLOAT:
			return {}

	var raid_bias: float = clampf(float(template_data.get("raid_bias", 0.0)), -0.25, 0.25)
	var defense_bias: float = clampf(float(template_data.get("defense_bias", 0.0)), -0.25, 0.25)
	var rally_bias: float = clampf(float(template_data.get("rally_bias", 0.0)), -0.25, 0.25)
	var magic_bias: float = clampf(float(template_data.get("magic_bias", 0.0)), -0.12, 0.12)

	var tags_variant: Variant = template_data.get("tags", [])
	var tags: Array[String] = []
	if typeof(tags_variant) == TYPE_ARRAY:
		var tags_array: Array = tags_variant
		for tag_variant in tags_array:
			if typeof(tag_variant) != TYPE_STRING:
				continue
			var tag: String = str(tag_variant).strip_edges()
			if tag == "":
				continue
			tags.append(tag)

	return {
		"id": template_id,
		"label": label,
		"kind": kind,
		"raid_bias": raid_bias,
		"defense_bias": defense_bias,
		"rally_bias": rally_bias,
		"magic_bias": magic_bias,
		"tags": tags
	}


func _sanitize_location_template_entry(template_data: Dictionary) -> Dictionary:
	var template_id: String = str(template_data.get("id", "")).strip_edges()
	var label: String = str(template_data.get("label", "")).strip_edges()
	var kind: String = str(template_data.get("kind", "")).strip_edges()
	if template_id == "" or label == "" or kind == "":
		return {}
	if kind not in ["camp", "ruins", "rift_gate"]:
		return {}

	var faction_affinity: String = str(template_data.get("faction_affinity", "")).strip_edges()
	if faction_affinity not in ["human", "monster", "neutral"]:
		return {}

	var influence_radius_variant: Variant = template_data.get("influence_radius", null)
	if typeof(influence_radius_variant) != TYPE_INT and typeof(influence_radius_variant) != TYPE_FLOAT:
		return {}
	var influence_radius: float = float(influence_radius_variant)
	if influence_radius <= 0.0:
		return {}

	var alert_radius_variant: Variant = template_data.get("alert_radius", null)
	if typeof(alert_radius_variant) != TYPE_INT and typeof(alert_radius_variant) != TYPE_FLOAT:
		return {}
	var alert_radius: float = float(alert_radius_variant)
	if alert_radius <= 0.0:
		return {}

	var can_upgrade_to: String = str(template_data.get("can_upgrade_to", "")).strip_edges()
	if can_upgrade_to not in ["", "human_outpost", "monster_lair"]:
		return {}

	var tags_variant: Variant = template_data.get("tags", [])
	var tags: Array[String] = []
	if typeof(tags_variant) == TYPE_ARRAY:
		var tags_array: Array = tags_variant
		for tag_variant in tags_array:
			if typeof(tag_variant) != TYPE_STRING:
				continue
			var tag: String = str(tag_variant).strip_edges()
			if tag == "":
				continue
			tags.append(tag)

	return {
		"id": template_id,
		"label": label,
		"kind": kind,
		"faction_affinity": faction_affinity,
		"influence_radius": influence_radius,
		"alert_radius": alert_radius,
		"can_upgrade_to": can_upgrade_to,
		"tags": tags
	}


func _location_template_for(poi_name: String, poi_kind: String) -> Dictionary:
	if poi_name != "" and location_template_by_id.has(poi_name):
		return Dictionary(location_template_by_id[poi_name]).duplicate(true)
	if poi_kind != "" and location_template_by_kind.has(poi_kind):
		return Dictionary(location_template_by_kind[poi_kind]).duplicate(true)
	return {}


func _apply_location_template_to_poi(base_poi: Dictionary) -> Dictionary:
	var poi: Dictionary = base_poi.duplicate(true)
	var poi_name: String = str(poi.get("name", ""))
	var poi_kind: String = str(poi.get("kind", ""))
	var template: Dictionary = _location_template_for(poi_name, poi_kind)
	if template.is_empty():
		return poi

	var label: String = str(template.get("label", "")).strip_edges()
	if label != "":
		poi["label"] = label

	var faction_affinity: String = str(template.get("faction_affinity", "")).strip_edges()
	if faction_affinity == "human" or faction_affinity == "monster":
		poi["faction_hint"] = faction_affinity
	elif faction_affinity == "neutral":
		poi["faction_hint"] = ""

	poi["radius"] = max(1.0, float(template.get("influence_radius", float(poi.get("radius", 7.0)))))
	poi["alert_radius"] = max(1.0, float(template.get("alert_radius", float(poi.get("alert_radius", 13.0)))))
	poi["upgrade_target"] = str(template.get("can_upgrade_to", str(poi.get("upgrade_target", ""))))

	var tags_variant: Variant = template.get("tags", [])
	if typeof(tags_variant) == TYPE_ARRAY:
		var tags: Array = tags_variant
		poi["tags"] = tags.duplicate(true)

	return poi


func _apply_location_templates_to_existing_pois() -> void:
	if pois.is_empty():
		return
	for index in range(pois.size()):
		var current_variant: Variant = pois[index]
		if typeof(current_variant) != TYPE_DICTIONARY:
			continue
		var current: Dictionary = current_variant
		pois[index] = _apply_location_template_to_poi(current)
	_refresh_poi_markers()


func get_allegiance_doctrine(allegiance_id: String) -> String:
	if allegiance_id == "":
		return ""
	var doctrine: String = str(allegiance_doctrine_by_id.get(allegiance_id, ""))
	if doctrine in ALLEGIANCE_DOCTRINES:
		doctrine_invalid_by_allegiance.erase(allegiance_id)
		return doctrine
	if doctrine != "" and not doctrine_invalid_by_allegiance.has(allegiance_id):
		push_warning("WorldManager: ignored invalid doctrine '%s' for allegiance '%s'." % [doctrine, allegiance_id])
		doctrine_invalid_by_allegiance[allegiance_id] = doctrine
	return ""


func get_doctrine_template(doctrine_id: String) -> Dictionary:
	if doctrine_id == "":
		return {}
	if not doctrine_template_by_id.has(doctrine_id):
		return {}
	return Dictionary(doctrine_template_by_id[doctrine_id]).duplicate(true)


func get_doctrine_label(doctrine_id: String, fallback_label: String = "") -> String:
	var template: Dictionary = get_doctrine_template(doctrine_id)
	if not template.is_empty():
		var label: String = str(template.get("label", "")).strip_edges()
		if label != "":
			return label
	return fallback_label if fallback_label != "" else doctrine_id


func get_doctrine_tags(doctrine_id: String) -> Array:
	var template: Dictionary = get_doctrine_template(doctrine_id)
	if template.is_empty():
		return []
	var tags_variant: Variant = template.get("tags", [])
	if typeof(tags_variant) != TYPE_ARRAY:
		return []
	var tags: Array = tags_variant
	return tags.duplicate(true)


func get_allegiance_doctrine_source(allegiance_id: String) -> String:
	var doctrine: String = get_allegiance_doctrine(allegiance_id)
	if doctrine == "":
		return "fallback"
	if doctrine_template_by_id.has(doctrine):
		return "json"
	return "fallback"


func get_allegiance_doctrine_label(allegiance_id: String, fallback_label: String = "") -> String:
	var doctrine: String = get_allegiance_doctrine(allegiance_id)
	if doctrine == "":
		return fallback_label
	return get_doctrine_label(doctrine, doctrine if fallback_label == "" else fallback_label)


func get_allegiance_doctrine_tags(allegiance_id: String) -> Array:
	var doctrine: String = get_allegiance_doctrine(allegiance_id)
	if doctrine == "":
		return []
	return get_doctrine_tags(doctrine)


func get_doctrine_project_bias(doctrine_id: String, doctrine_source: String = "fallback") -> Dictionary:
	var normalized_source: String = doctrine_source if doctrine_source in ["json", "fallback"] else "fallback"
	var preferred_project: String = ""
	var influence_strength: float = 0.0
	match doctrine_id:
		"warlike":
			preferred_project = "warband_muster"
			influence_strength = 0.18
		"steadfast":
			preferred_project = "fortify"
			influence_strength = 0.18
		"arcane":
			preferred_project = "ritual_focus"
			influence_strength = 0.16
			if world_event_visual_id == "mana_surge":
				influence_strength += 0.04
		_:
			pass

	if normalized_source != "json":
		influence_strength = 0.0

	return {
		"doctrine": doctrine_id,
		"preferred_project": preferred_project,
		"influence_strength": clampf(influence_strength, 0.0, 0.32),
		"source": normalized_source
	}


func get_allegiance_doctrine_project_bias(allegiance_id: String) -> Dictionary:
	var doctrine_id: String = get_allegiance_doctrine(allegiance_id)
	var doctrine_source: String = get_allegiance_doctrine_source(allegiance_id)
	var project_bias: Dictionary = get_doctrine_project_bias(doctrine_id, doctrine_source)
	project_bias["allegiance_id"] = allegiance_id
	project_bias["label"] = get_allegiance_doctrine_label(allegiance_id, doctrine_id)
	return project_bias


func get_doctrine_vendetta_bias(doctrine_id: String, doctrine_source: String = "fallback") -> Dictionary:
	var normalized_source: String = doctrine_source if doctrine_source in ["json", "fallback"] else "fallback"
	var vendetta_start_delta: float = 0.0
	match doctrine_id:
		"warlike":
			vendetta_start_delta = 0.03
		"steadfast":
			vendetta_start_delta = -0.03
		"arcane":
			if world_event_visual_id == "mana_surge":
				vendetta_start_delta = 0.01
			else:
				vendetta_start_delta = 0.0
		_:
			pass

	if normalized_source != "json":
		vendetta_start_delta = 0.0

	return {
		"doctrine": doctrine_id,
		"vendetta_start_delta": clampf(vendetta_start_delta, -0.10, 0.10),
		"source": normalized_source
	}


func get_allegiance_doctrine_vendetta_bias(allegiance_id: String) -> Dictionary:
	var doctrine_id: String = get_allegiance_doctrine(allegiance_id)
	var doctrine_source: String = get_allegiance_doctrine_source(allegiance_id)
	var vendetta_bias: Dictionary = get_doctrine_vendetta_bias(doctrine_id, doctrine_source)
	vendetta_bias["allegiance_id"] = allegiance_id
	vendetta_bias["label"] = get_allegiance_doctrine_label(allegiance_id, doctrine_id)
	return vendetta_bias


func get_allegiance_doctrine_modifiers(allegiance_id: String) -> Dictionary:
	var doctrine: String = get_allegiance_doctrine(allegiance_id)
	var modifiers: Dictionary = _default_doctrine_modifiers(doctrine)
	if doctrine == "":
		modifiers["source"] = "fallback"
		modifiers["uses_fallback"] = true
		return modifiers

	var template: Dictionary = get_doctrine_template(doctrine)
	if template.is_empty():
		modifiers["source"] = "fallback"
		modifiers["uses_fallback"] = true
		return modifiers

	modifiers["doctrine_label"] = get_doctrine_label(doctrine, doctrine)
	modifiers["doctrine_tags"] = get_doctrine_tags(doctrine)
	modifiers["raid_weight_delta"] = clampf(float(template.get("raid_bias", modifiers.get("raid_weight_delta", 0.0))), -0.25, 0.25)
	modifiers["defense_weight_delta"] = clampf(float(template.get("defense_bias", modifiers.get("defense_weight_delta", 0.0))), -0.25, 0.25)
	modifiers["rally_regroup_delta"] = clampf(float(template.get("rally_bias", modifiers.get("rally_regroup_delta", 0.0))), -0.25, 0.25)
	var magic_bias: float = clampf(float(template.get("magic_bias", 0.0)), -0.12, 0.12)
	modifiers["magic_damage_mult"] = max(0.88, 1.0 + magic_bias)
	modifiers["magic_energy_cost_mult"] = max(0.88, 1.0 - magic_bias)
	modifiers["source"] = "json"
	modifiers["uses_fallback"] = false
	return modifiers


func get_allegiance_doctrine_biases(allegiance_id: String) -> Dictionary:
	var modifiers: Dictionary = get_allegiance_doctrine_modifiers(allegiance_id)
	var magic_damage_mult: float = float(modifiers.get("magic_damage_mult", 1.0))
	var magic_energy_cost_mult: float = float(modifiers.get("magic_energy_cost_mult", 1.0))
	var magic_bias: float = clampf((magic_damage_mult - magic_energy_cost_mult) * 0.5, -0.12, 0.12)
	return {
		"raid_bias": float(modifiers.get("raid_weight_delta", 0.0)),
		"defense_bias": float(modifiers.get("defense_weight_delta", 0.0)),
		"rally_bias": float(modifiers.get("rally_regroup_delta", 0.0)),
		"magic_bias": magic_bias,
		"magic_damage_mult": magic_damage_mult,
		"magic_energy_cost_mult": magic_energy_cost_mult,
		"source": str(modifiers.get("source", "fallback"))
	}


func get_doctrine_runtime_snapshot(active_allegiances: Array[Dictionary] = []) -> Dictionary:
	var allegiances: Array[Dictionary] = active_allegiances
	if allegiances.is_empty():
		allegiances = get_active_allegiances()

	var doctrine_by_allegiance: Dictionary = {}
	var doctrine_labels: Array[String] = []
	var doctrine_counts := {
		"warlike": 0,
		"steadfast": 0,
		"arcane": 0
	}
	var source_counts := {
		"json": 0,
		"fallback": 0
	}
	var project_bias_counts := {
		"fortify": 0,
		"warband_muster": 0,
		"ritual_focus": 0
	}
	var missing_template_doctrines: Array[String] = []
	var fallback_allegiances: Array[String] = []
	var bias_totals := {
		"raid_bias": 0.0,
		"defense_bias": 0.0,
		"rally_bias": 0.0,
		"magic_bias": 0.0
	}
	var vendetta_bias_total: float = 0.0
	var doctrine_total: int = 0

	for allegiance_variant in allegiances:
		if typeof(allegiance_variant) != TYPE_DICTIONARY:
			continue
		var allegiance: Dictionary = allegiance_variant
		var allegiance_id: String = str(allegiance.get("allegiance_id", ""))
		if allegiance_id == "":
			continue
		var doctrine_id: String = get_allegiance_doctrine(allegiance_id)
		if doctrine_id == "":
			continue

		var source: String = get_allegiance_doctrine_source(allegiance_id)
		var doctrine_label: String = get_allegiance_doctrine_label(allegiance_id, doctrine_id)
		var doctrine_tags: Array = get_allegiance_doctrine_tags(allegiance_id)
		var biases: Dictionary = get_allegiance_doctrine_biases(allegiance_id)
		var doctrine_project_bias: Dictionary = get_allegiance_doctrine_project_bias(allegiance_id)
		var doctrine_vendetta_bias: Dictionary = get_allegiance_doctrine_vendetta_bias(allegiance_id)
		doctrine_total += 1
		doctrine_labels.append("%s=%s[%s]" % [allegiance_id, doctrine_id, source])
		if doctrine_counts.has(doctrine_id):
			doctrine_counts[doctrine_id] += 1
		if source_counts.has(source):
			source_counts[source] += 1
		if source == "fallback":
			fallback_allegiances.append("%s=%s" % [allegiance_id, doctrine_id])
			if not (doctrine_id in missing_template_doctrines):
				missing_template_doctrines.append(doctrine_id)

		bias_totals["raid_bias"] += float(biases.get("raid_bias", 0.0))
		bias_totals["defense_bias"] += float(biases.get("defense_bias", 0.0))
		bias_totals["rally_bias"] += float(biases.get("rally_bias", 0.0))
		bias_totals["magic_bias"] += float(biases.get("magic_bias", 0.0))
		vendetta_bias_total += float(doctrine_vendetta_bias.get("vendetta_start_delta", 0.0))
		var preferred_project: String = str(doctrine_project_bias.get("preferred_project", ""))
		if project_bias_counts.has(preferred_project):
			project_bias_counts[preferred_project] += 1
		doctrine_by_allegiance[allegiance_id] = {
			"doctrine": doctrine_id,
			"label": doctrine_label,
			"tags": doctrine_tags,
			"source": source,
			"biases": biases,
			"project_bias": doctrine_project_bias,
			"vendetta_bias": doctrine_vendetta_bias
		}

	doctrine_labels.sort()
	fallback_allegiances.sort()
	missing_template_doctrines.sort()
	var avg_divisor: float = max(1.0, float(doctrine_total))
	var average_biases: Dictionary = {
		"raid_bias": float(bias_totals.get("raid_bias", 0.0)) / avg_divisor,
		"defense_bias": float(bias_totals.get("defense_bias", 0.0)) / avg_divisor,
		"rally_bias": float(bias_totals.get("rally_bias", 0.0)) / avg_divisor,
		"magic_bias": float(bias_totals.get("magic_bias", 0.0)) / avg_divisor
	}
	var vendetta_bias_avg: float = vendetta_bias_total / avg_divisor

	var dominant_doctrine: String = ""
	var dominant_count: int = 0
	for doctrine_id in ALLEGIANCE_DOCTRINES:
		var count: int = int(doctrine_counts.get(doctrine_id, 0))
		if count > dominant_count:
			dominant_doctrine = doctrine_id
			dominant_count = count

	return {
		"by_allegiance": doctrine_by_allegiance,
		"labels": doctrine_labels,
		"counts": doctrine_counts,
		"sources": source_counts,
		"project_bias_counts": project_bias_counts,
		"vendetta_bias_avg": vendetta_bias_avg,
		"fallback_used_count": int(source_counts.get("fallback", 0)),
		"fallback_allegiances": fallback_allegiances,
		"missing_template_doctrines": missing_template_doctrines,
		"average_biases": average_biases,
		"dominant_doctrine": dominant_doctrine,
		"dominant_count": dominant_count,
		"doctrine_assigned_total": doctrine_total
	}


func _default_doctrine_modifiers(doctrine: String) -> Dictionary:
	match doctrine:
		"warlike":
			return {
				"doctrine": doctrine,
				"doctrine_label": doctrine,
				"doctrine_tags": [],
				"raid_weight_delta": 0.11,
				"defense_weight_delta": -0.05,
				"rally_regroup_delta": -0.05,
				"rally_pressure_delta": 0.08,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00,
				"source": "fallback",
				"uses_fallback": true
			}
		"steadfast":
			return {
				"doctrine": doctrine,
				"doctrine_label": doctrine,
				"doctrine_tags": [],
				"raid_weight_delta": -0.08,
				"defense_weight_delta": 0.12,
				"rally_regroup_delta": 0.08,
				"rally_pressure_delta": -0.04,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00,
				"source": "fallback",
				"uses_fallback": true
			}
		"arcane":
			return {
				"doctrine": doctrine,
				"doctrine_label": doctrine,
				"doctrine_tags": [],
				"raid_weight_delta": 0.02,
				"defense_weight_delta": 0.04,
				"rally_regroup_delta": 0.03,
				"rally_pressure_delta": 0.01,
				"magic_damage_mult": 1.06,
				"magic_energy_cost_mult": 0.94,
				"source": "fallback",
				"uses_fallback": true
			}
		_:
			return {
				"doctrine": "",
				"doctrine_label": "",
				"doctrine_tags": [],
				"raid_weight_delta": 0.0,
				"defense_weight_delta": 0.0,
				"rally_regroup_delta": 0.0,
				"rally_pressure_delta": 0.0,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00,
				"source": "fallback",
				"uses_fallback": true
			}


func get_allegiance_project(allegiance_id: String) -> String:
	if allegiance_id == "":
		return ""
	var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
	if runtime.is_empty():
		return ""
	var project_id: String = str(runtime.get("project_id", ""))
	if project_id in ALLEGIANCE_PROJECT_TYPES:
		return project_id
	return ""


func get_allegiance_project_remaining(allegiance_id: String, time_seconds: float = -1.0) -> float:
	if allegiance_id == "" or time_seconds < 0.0:
		return 0.0
	var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
	if runtime.is_empty():
		return 0.0
	var end_at: float = float(runtime.get("end_at", time_seconds))
	return max(0.0, end_at - time_seconds)


func get_allegiance_project_modifiers(allegiance_id: String) -> Dictionary:
	var project_id: String = get_allegiance_project(allegiance_id)
	match project_id:
		"fortify":
			return {
				"project_id": project_id,
				"raid_weight_delta": -0.06,
				"defense_weight_delta": 0.12,
				"rally_regroup_delta": 0.0,
				"rally_pressure_delta": 0.0,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00
			}
		"warband_muster":
			return {
				"project_id": project_id,
				"raid_weight_delta": 0.09,
				"defense_weight_delta": 0.0,
				"rally_regroup_delta": 0.07,
				"rally_pressure_delta": 0.0,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00
			}
		"ritual_focus":
			return {
				"project_id": project_id,
				"raid_weight_delta": 0.0,
				"defense_weight_delta": 0.0,
				"rally_regroup_delta": 0.0,
				"rally_pressure_delta": 0.0,
				"magic_damage_mult": 1.05,
				"magic_energy_cost_mult": 0.95
			}
		_:
			return {
				"project_id": "",
				"raid_weight_delta": 0.0,
				"defense_weight_delta": 0.0,
				"rally_regroup_delta": 0.0,
				"rally_pressure_delta": 0.0,
				"magic_damage_mult": 1.00,
				"magic_energy_cost_mult": 1.00
			}


func get_allegiance_vendetta_target(allegiance_id: String) -> String:
	if allegiance_id == "":
		return ""
	var runtime: Dictionary = allegiance_vendetta_runtime_by_id.get(allegiance_id, {})
	if runtime.is_empty():
		return ""
	return str(runtime.get("target_allegiance_id", ""))


func get_allegiance_vendetta_remaining(allegiance_id: String, time_seconds: float = -1.0) -> float:
	if allegiance_id == "" or time_seconds < 0.0:
		return 0.0
	var runtime: Dictionary = allegiance_vendetta_runtime_by_id.get(allegiance_id, {})
	if runtime.is_empty():
		return 0.0
	var end_at: float = float(runtime.get("end_at", time_seconds))
	return max(0.0, end_at - time_seconds)


func get_allegiance_vendetta_modifiers(
	source_allegiance_id: String,
	target_allegiance_id: String = ""
) -> Dictionary:
	var vendetta_target_id: String = get_allegiance_vendetta_target(source_allegiance_id)
	var target_match: bool = (
		vendetta_target_id != ""
		and target_allegiance_id != ""
		and vendetta_target_id == target_allegiance_id
	)
	if target_match:
		return {
			"active": true,
			"target_allegiance_id": vendetta_target_id,
			"raid_weight_delta": 0.10,
			"bounty_weight_delta": 0.12
		}
	return {
		"active": vendetta_target_id != "",
		"target_allegiance_id": vendetta_target_id,
		"raid_weight_delta": 0.0,
		"bounty_weight_delta": 0.0
	}


func get_active_vendettas(time_seconds: float = -1.0) -> Array[Dictionary]:
	var active: Array[Dictionary] = []
	for allegiance_variant in allegiance_vendetta_runtime_by_id.keys():
		var source_allegiance_id: String = str(allegiance_variant)
		var runtime: Dictionary = allegiance_vendetta_runtime_by_id.get(source_allegiance_id, {})
		if runtime.is_empty():
			continue
		active.append({
			"source_allegiance_id": source_allegiance_id,
			"target_allegiance_id": str(runtime.get("target_allegiance_id", "")),
			"reason": str(runtime.get("reason", "")),
			"remaining": get_allegiance_vendetta_remaining(source_allegiance_id, time_seconds)
		})
	return active


func register_vendetta_incident(
	source_allegiance_id: String,
	target_allegiance_id: String,
	reason: String,
	time_seconds: float
) -> Dictionary:
	return _try_start_vendetta(source_allegiance_id, target_allegiance_id, reason, time_seconds)


func get_poi_name_for_position(position: Vector3) -> String:
	for poi in pois:
		var poi_name: String = str(poi.get("name", "poi"))
		var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
		var poi_radius: float = float(poi.get("radius", 7.0))
		if position.distance_to(poi_pos) <= poi_radius:
			return poi_name
	return ""


func get_poi_label(poi_name: String, fallback_label: String = "") -> String:
	if poi_name == "":
		return fallback_label
	var poi: Dictionary = _get_poi_by_name(poi_name)
	if poi.is_empty():
		return fallback_label
	var label: String = str(poi.get("label", "")).strip_edges()
	if label != "":
		return label
	return fallback_label if fallback_label != "" else poi_name


func get_poi_alert_radius(poi_name: String, fallback_radius: float = 13.0) -> float:
	if poi_name == "":
		return max(1.0, fallback_radius)
	var poi: Dictionary = _get_poi_by_name(poi_name)
	if poi.is_empty():
		return max(1.0, fallback_radius)
	var radius: float = float(poi.get("alert_radius", fallback_radius))
	return max(1.0, radius)


func trigger_poi_entry_effect(poi_name: String, faction: String) -> void:
	var poi_node: Node3D = poi_nodes.get(poi_name, null)
	if poi_node == null:
		return
	var poi_kind: String = str(_get_poi_by_name(poi_name).get("kind", ""))

	var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
	if ring != null:
		var pulse := create_tween()
		var base_scale := ring.scale
		pulse.tween_property(ring, "scale", base_scale * 1.18, 0.10)
		pulse.tween_property(ring, "scale", base_scale, 0.14)

	var flash := MeshInstance3D.new()
	flash.name = "EntryFlash"
	var mesh := CylinderMesh.new()
	if poi_kind == "rift_gate":
		mesh.top_radius = 1.6
		mesh.bottom_radius = 1.6
	else:
		mesh.top_radius = 1.3
		mesh.bottom_radius = 1.3
	mesh.height = 0.08
	flash.mesh = mesh
	flash.position = Vector3(0.0, 0.06, 0.0)
	flash.scale = Vector3(0.35, 1.0, 0.35)

	var color := Color(0.45, 0.75, 1.0) if faction == "human" else Color(1.0, 0.52, 0.46)
	if poi_kind == "rift_gate":
		color = Color(0.82, 0.46, 1.0)
	var material := _make_material(color)
	material.emission = color * 1.05
	flash.material_override = material

	poi_node.add_child(flash)
	var tween := create_tween()
	tween.tween_property(flash, "scale", Vector3.ONE * 1.25, 0.22)
	tween.finished.connect(flash.queue_free)


func _build_ground() -> void:
	var old_ground := get_node_or_null("Ground")
	if old_ground:
		old_ground.queue_free()

	var ground := MeshInstance3D.new()
	ground.name = "Ground"
	var plane := PlaneMesh.new()
	plane.size = Vector2(map_size, map_size)
	ground.mesh = plane

	var ground_material := StandardMaterial3D.new()
	ground_material.albedo_color = Color(0.16, 0.34, 0.20)
	ground_material.roughness = 1.0
	ground.material_override = ground_material
	add_child(ground)


func _build_spawn_points() -> void:
	human_spawn_points.clear()
	monster_spawn_points.clear()

	var side: float = map_size * 0.35
	var lane_values := [-18.0, -9.0, 0.0, 9.0, 18.0]

	for lane in lane_values:
		human_spawn_points.append(Vector3(-side, 0.0, lane))
		monster_spawn_points.append(Vector3(side, 0.0, lane))

	_refresh_markers()


func _build_pois() -> void:
	pois.clear()
	pois.append(_apply_location_template_to_poi({
		"name": "camp",
		"label": "Camp",
		"kind": "camp",
		"faction_hint": "human",
		"position": Vector3(-10.0, 0.0, -6.0),
		"radius": 8.0,
		"alert_radius": 13.0,
		"upgrade_target": "human_outpost",
		"tags": ["poi", "anchor", "human", "upgrade_human_outpost"],
		"color": Color(0.40, 0.72, 1.0)
	}))
	pois.append(_apply_location_template_to_poi({
		"name": "ruins",
		"label": "Ruins",
		"kind": "ruins",
		"faction_hint": "monster",
		"position": Vector3(10.0, 0.0, 6.0),
		"radius": 8.0,
		"alert_radius": 13.0,
		"upgrade_target": "monster_lair",
		"tags": ["poi", "anchor", "monster", "upgrade_monster_lair"],
		"color": Color(0.95, 0.60, 0.35)
	}))
	pois.append(_apply_location_template_to_poi({
		"name": "rift_gate",
		"label": "Rift Gate",
		"kind": "rift_gate",
		"faction_hint": "",
		"position": Vector3(0.0, 0.0, 0.0),
		"radius": 7.2,
		"alert_radius": 16.5,
		"upgrade_target": "",
		"tags": ["poi", "neutral", "gate", "volatile"],
		"color": Color(0.76, 0.40, 0.96)
	}))

	poi_runtime_status.clear()
	poi_dominant_faction.clear()
	poi_dominance_started_at.clear()
	poi_influence_active.clear()
	poi_structure_state.clear()
	poi_structure_faction.clear()
	poi_structure_started_at.clear()
	poi_structure_unstable_started_at.clear()
	poi_allegiance_id.clear()
	allegiance_doctrine_by_id.clear()
	allegiance_project_runtime_by_id.clear()
	allegiance_project_cooldown_until_by_id.clear()
	allegiance_project_next_attempt_at_by_id.clear()
	allegiance_vendetta_runtime_by_id.clear()
	allegiance_vendetta_cooldown_until_by_id.clear()
	poi_raid_state.clear()
	poi_raid_cooldown_until = 0.0
	poi_last_raid_attacker = ""
	bounty_state.clear()
	convergence_state.clear()
	neutral_gate_status = "dormant"
	neutral_gate_open_until = 0.0
	neutral_gate_cooldown_until = randf_range(
		neutral_gate_cooldown_min * 0.55,
		neutral_gate_cooldown_max * 0.72
	)
	neutral_gate_opened_total = 0
	neutral_gate_closed_total = 0
	neutral_gate_breaches_total = 0
	neutral_gate_breach_pending = false
	neutral_gate_bonus_breach_used = false
	neutral_gate_response_pull_human_mult = 1.0
	neutral_gate_response_pull_monster_mult = 1.0
	allegiance_crisis_raid_mult_by_id.clear()
	allegiance_recovery_defense_delta_by_id.clear()
	allegiance_mending_modifiers_by_id.clear()
	vendetta_suppressed_pair_keys.clear()
	alert_state_by_allegiance.clear()
	sanctuary_bastion_state_by_id.clear()
	taboo_state_by_id.clear()

	_refresh_poi_markers()


func _refresh_markers() -> void:
	var old_markers := get_node_or_null("SpawnMarkers")
	if old_markers:
		old_markers.queue_free()

	var marker_root := Node3D.new()
	marker_root.name = "SpawnMarkers"
	add_child(marker_root)

	for point in human_spawn_points:
		marker_root.add_child(_make_marker(point, Color(0.45, 0.75, 1.0)))
	for point in monster_spawn_points:
		marker_root.add_child(_make_marker(point, Color(0.95, 0.45, 0.45)))


func _make_marker(position: Vector3, color: Color) -> MeshInstance3D:
	var marker := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0.30
	mesh.bottom_radius = 0.30
	mesh.height = 0.15
	marker.mesh = mesh
	marker.position = position + Vector3(0.0, 0.075, 0.0)

	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color * 0.35
	marker.material_override = material

	return marker


func _refresh_poi_markers() -> void:
	var old_root := get_node_or_null("PoiMarkers")
	if old_root:
		old_root.queue_free()

	var poi_root := Node3D.new()
	poi_root.name = "PoiMarkers"
	add_child(poi_root)

	poi_nodes.clear()
	for poi in pois:
		var marker := _make_poi_marker(poi)
		poi_root.add_child(marker)
		poi_nodes[str(poi.get("name", "poi"))] = marker


func _make_poi_marker(poi: Dictionary) -> Node3D:
	var poi_node := Node3D.new()
	poi_node.name = str(poi.get("name", "poi"))
	poi_node.position = poi.get("position", Vector3.ZERO)

	var color: Color = poi.get("color", Color(0.9, 0.9, 0.9))
	var poi_kind: String = str(poi.get("kind", ""))
	var ring := MeshInstance3D.new()
	var ring_mesh := CylinderMesh.new()
	ring_mesh.top_radius = 2.6 if poi_kind == "rift_gate" else 2.2
	ring_mesh.bottom_radius = ring_mesh.top_radius
	ring_mesh.height = 0.1
	ring.mesh = ring_mesh
	ring.name = "Ring"
	ring.position.y = 0.05
	ring.material_override = _make_material(color * 0.85)
	poi_node.add_child(ring)

	var pillar := MeshInstance3D.new()
	var pillar_mesh := BoxMesh.new()
	if poi_kind == "rift_gate":
		pillar_mesh.size = Vector3(1.0, 2.6, 1.0)
	else:
		pillar_mesh.size = Vector3(0.8, 2.0, 0.8)
	pillar.mesh = pillar_mesh
	pillar.name = "Pillar"
	pillar.position.y = 1.3 if poi_kind == "rift_gate" else 1.0
	pillar.material_override = _make_material(color)
	poi_node.add_child(pillar)

	var beacon := MeshInstance3D.new()
	var beacon_mesh := SphereMesh.new()
	if poi_kind == "rift_gate":
		beacon_mesh.radius = 0.42
		beacon_mesh.height = 0.84
	else:
		beacon_mesh.radius = 0.32
		beacon_mesh.height = 0.64
	beacon.mesh = beacon_mesh
	beacon.name = "Beacon"
	beacon.position.y = 3.0 if poi_kind == "rift_gate" else 2.2
	beacon.material_override = _make_material(Color(0.65, 0.65, 0.65))
	poi_node.add_child(beacon)

	var structure_halo := MeshInstance3D.new()
	var halo_mesh := CylinderMesh.new()
	halo_mesh.top_radius = 1.05
	halo_mesh.bottom_radius = 1.05
	halo_mesh.height = 0.06
	structure_halo.mesh = halo_mesh
	structure_halo.name = "StructureHalo"
	structure_halo.position.y = 2.72
	structure_halo.material_override = _make_material(Color(0.85, 0.85, 0.85))
	structure_halo.visible = false
	poi_node.add_child(structure_halo)

	if poi_kind == "rift_gate":
		var gate_halo := MeshInstance3D.new()
		var gate_halo_mesh := CylinderMesh.new()
		gate_halo_mesh.top_radius = 1.45
		gate_halo_mesh.bottom_radius = 1.45
		gate_halo_mesh.height = 0.07
		gate_halo.mesh = gate_halo_mesh
		gate_halo.name = "GateHalo"
		gate_halo.position.y = 3.42
		gate_halo.material_override = _make_material(Color(0.82, 0.48, 1.0))
		gate_halo.visible = false
		poi_node.add_child(gate_halo)

	return poi_node


func _make_material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color * 0.30
	material.roughness = 0.7
	return material


func _get_nearest_poi(position: Vector3, skip_neutral_gate: bool = false) -> Dictionary:
	var selected: Dictionary = {}
	var closest_sq: float = INF
	for poi in pois:
		if skip_neutral_gate and _is_neutral_gate_poi(poi):
			continue
		var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
		var d_sq: float = position.distance_squared_to(poi_pos)
		if d_sq < closest_sq:
			selected = poi
			closest_sq = d_sq
	return selected


func _get_poi_by_name(poi_name: String) -> Dictionary:
	for poi in pois:
		if str(poi.get("name", "")) == poi_name:
			return poi
	return {}


func _count_poi_occupancy(poi: Dictionary, actors: Array) -> Dictionary:
	var poi_pos: Vector3 = poi.get("position", Vector3.ZERO)
	var poi_radius: float = float(poi.get("radius", 7.0))
	var humans: int = 0
	var monsters: int = 0
	var human_champions: int = 0
	var monster_champions: int = 0

	for actor in actors:
		if actor == null or actor.is_dead:
			continue
		if actor.global_position.distance_to(poi_pos) > poi_radius:
			continue

		if actor.faction == "human":
			humans += 1
			if actor.is_champion:
				human_champions += 1
		elif actor.faction == "monster":
			monsters += 1
			if actor.is_champion:
				monster_champions += 1

	return {
		"human": humans,
		"monster": monsters,
		"human_champions": human_champions,
		"monster_champions": monster_champions
	}


func _compute_poi_status(human_count: int, monster_count: int) -> String:
	if human_count == 0 and monster_count == 0:
		return "calm"
	if human_count > 0 and monster_count > 0:
		return "contested"
	if human_count > 0:
		return "human_dominant"
	return "monster_dominant"


func _compute_activity_level(total_count: int) -> String:
	if total_count <= 1:
		return "low"
	if total_count <= 4:
		return "medium"
	return "high"


func _apply_poi_visual_state(
	poi_name: String,
	status: String,
	total_count: int,
	time_seconds: float,
	influence_active: bool,
	structure_state: String,
	raid_role: String,
	gate_status: String,
	gate_active: bool
) -> void:
	var poi_node: Node3D = poi_nodes.get(poi_name, null)
	if poi_node == null:
		return

	var ring := poi_node.get_node_or_null("Ring") as MeshInstance3D
	var pillar := poi_node.get_node_or_null("Pillar") as MeshInstance3D
	var beacon := poi_node.get_node_or_null("Beacon") as MeshInstance3D
	var structure_halo := poi_node.get_node_or_null("StructureHalo") as MeshInstance3D
	var gate_halo := poi_node.get_node_or_null("GateHalo") as MeshInstance3D
	if ring == null or pillar == null or beacon == null or structure_halo == null:
		return

	var base_scale: float = 1.0 + min(total_count, 10) * 0.045
	if status == "contested":
		base_scale *= (1.0 + 0.06 * sin(time_seconds * 6.0))
	elif influence_active:
		base_scale *= (1.0 + 0.04 * sin(time_seconds * 4.0))
	ring.scale = Vector3(base_scale, 1.0, base_scale)

	var status_color := _get_status_color(status)
	var intensity: float = 0.24 + min(total_count, 10) * 0.05
	if influence_active:
		intensity += 0.16

	_set_mesh_color(ring, status_color, intensity + 0.05)
	_set_mesh_color(beacon, status_color, intensity + 0.10)
	_set_mesh_color(pillar, status_color.darkened(0.18), intensity * 0.62)

	if structure_state != "":
		structure_halo.visible = true
		var halo_scale := 1.0 + 0.06 * sin(time_seconds * 3.0)
		structure_halo.scale = Vector3(halo_scale, 1.0, halo_scale)
		_set_mesh_color(structure_halo, _structure_color(structure_state), 0.82)
	else:
		structure_halo.visible = false

	_apply_world_event_visual_bias(ring, beacon, status_color, intensity, time_seconds)

	if gate_halo != null:
		if gate_active:
			gate_halo.visible = true
			var gate_halo_scale := 1.0 + 0.10 * sin(time_seconds * 8.4)
			gate_halo.scale = Vector3(gate_halo_scale, 1.0, gate_halo_scale)
			_set_mesh_color(gate_halo, Color(0.84, 0.46, 1.0), 1.05)
			var gate_mix := 0.44 + 0.10 * sin(time_seconds * 7.8)
			_set_mesh_color(ring, status_color.lerp(Color(0.84, 0.42, 1.0), gate_mix), intensity + 0.34)
			_set_mesh_color(beacon, Color(0.86, 0.56, 1.0), intensity + 0.42)
			var gate_pulse := 1.0 + 0.14 * sin(time_seconds * 8.0)
			ring.scale *= Vector3(gate_pulse, 1.0, gate_pulse)
		else:
			gate_halo.visible = false
			if gate_status == "dormant":
				_set_mesh_color(beacon, status_color.darkened(0.10), max(0.16, intensity * 0.72))

	if raid_role == "source":
		var source_pulse := 1.0 + 0.10 * sin(time_seconds * 5.0)
		ring.scale *= Vector3(source_pulse, 1.0, source_pulse)
		_set_mesh_color(beacon, status_color.lightened(0.20), intensity + 0.26)
	elif raid_role == "target":
		var target_pulse := 1.0 + 0.08 * sin(time_seconds * 7.0)
		ring.scale *= Vector3(target_pulse, 1.0, target_pulse)
		_set_mesh_color(ring, Color(1.0, 0.62, 0.30), intensity + 0.24)


func _dominant_faction_from_status(status: String) -> String:
	if status == "human_dominant":
		return "human"
	if status == "monster_dominant":
		return "monster"
	return ""


func _update_dominance_duration(poi_name: String, dominant_faction: String, time_seconds: float) -> float:
	var previous_faction: String = str(poi_dominant_faction.get(poi_name, ""))
	if dominant_faction == "":
		poi_dominant_faction[poi_name] = ""
		poi_dominance_started_at[poi_name] = time_seconds
		return 0.0

	if previous_faction != dominant_faction:
		poi_dominant_faction[poi_name] = dominant_faction
		poi_dominance_started_at[poi_name] = time_seconds
		return 0.0

	var started_at: float = float(poi_dominance_started_at.get(poi_name, time_seconds))
	var duration: float = max(0.0, time_seconds - started_at)
	return duration


func _compute_influence_kind(poi_kind: String, dominant_faction: String, dominance_seconds: float) -> String:
	if dominant_faction == "":
		return ""
	if dominance_seconds < poi_influence_activation_time:
		return ""
	if poi_kind == "camp" and dominant_faction == "human":
		return "human_camp_influence"
	if poi_kind == "ruins" and dominant_faction == "monster":
		return "monster_ruins_influence"
	return ""


func _compute_structure_kind(poi_name: String, poi_kind: String, dominant_faction: String) -> String:
	var poi: Dictionary = _get_poi_by_name(poi_name)
	var configured_upgrade: String = str(poi.get("upgrade_target", "")).strip_edges()
	if configured_upgrade == "human_outpost" and dominant_faction == "human":
		return configured_upgrade
	if configured_upgrade == "monster_lair" and dominant_faction == "monster":
		return configured_upgrade

	if poi_kind == "camp" and dominant_faction == "human":
		return "human_outpost"
	if poi_kind == "ruins" and dominant_faction == "monster":
		return "monster_lair"
	return ""


func _update_structure_runtime(
	poi_name: String,
	poi_kind: String,
	dominant_faction: String,
	dominance_seconds: float,
	influence_active: bool,
	dominant_presence: int,
	dominant_champions: int,
	time_seconds: float
) -> Dictionary:
	var events: Array[Dictionary] = []
	var current_state: String = str(poi_structure_state.get(poi_name, ""))
	var current_faction: String = str(poi_structure_faction.get(poi_name, ""))
	var can_structure_kind: String = _compute_structure_kind(poi_name, poi_kind, dominant_faction)

	var required_presence: int = poi_structure_min_presence
	if dominant_champions > 0:
		required_presence = max(1, poi_structure_min_presence - 1)

	var eligible: bool = (
		can_structure_kind != ""
		and influence_active
		and dominance_seconds >= poi_structure_activation_time
		and dominant_presence >= required_presence
	)

	if current_state == "" and eligible:
		current_state = can_structure_kind
		current_faction = dominant_faction
		var allegiance_id: String = _ensure_allegiance_for_poi(poi_name, current_faction)
		var faction_template_id: String = _resolve_faction_template_id_for_faction(current_faction)
		if faction_template_id != "":
			faction_template_id_by_allegiance[allegiance_id] = faction_template_id
		else:
			faction_template_id_by_allegiance.erase(allegiance_id)
		var doctrine: String = _assign_doctrine_for_allegiance(
			allegiance_id,
			current_faction,
			current_state,
			dominant_champions
		)
		poi_structure_state[poi_name] = current_state
		poi_structure_faction[poi_name] = current_faction
		poi_structure_started_at[poi_name] = time_seconds
		poi_structure_unstable_started_at.erase(poi_name)
		events.append({
			"kind": "allegiance_created",
			"poi": poi_name,
			"allegiance_id": allegiance_id,
			"faction": current_faction,
			"doctrine": doctrine
		})
		events.append({
			"kind": "structure_established",
			"poi": poi_name,
			"structure_state": current_state,
			"faction": current_faction
		})
	elif current_state != "":
		var stable_for_current_structure: bool = (
			dominant_faction == current_faction
			and can_structure_kind == current_state
			and influence_active
			and dominant_presence >= max(1, poi_structure_min_presence - 1)
		)

		if stable_for_current_structure:
			poi_structure_unstable_started_at.erase(poi_name)
		else:
			if not poi_structure_unstable_started_at.has(poi_name):
				poi_structure_unstable_started_at[poi_name] = time_seconds
			var unstable_since: float = float(poi_structure_unstable_started_at.get(poi_name, time_seconds))
			if time_seconds - unstable_since >= poi_structure_loss_time:
				var previous_allegiance_id: String = str(poi_allegiance_id.get(poi_name, ""))
				if previous_allegiance_id != "":
					var interrupted_project_id: String = _interrupt_allegiance_project(previous_allegiance_id, time_seconds)
					if interrupted_project_id != "":
						events.append({
							"kind": "allegiance_project_interrupted",
							"poi": poi_name,
							"allegiance_id": previous_allegiance_id,
							"project_id": interrupted_project_id,
							"reason": "anchor_lost"
						})
					var doctrine_lost: String = _clear_allegiance_doctrine(previous_allegiance_id)
					faction_template_id_by_allegiance.erase(previous_allegiance_id)
					events.append({
						"kind": "allegiance_removed",
						"poi": poi_name,
						"allegiance_id": previous_allegiance_id,
						"faction": current_faction,
						"doctrine": doctrine_lost
					})
					poi_allegiance_id.erase(poi_name)
				events.append({
					"kind": "structure_lost",
					"poi": poi_name,
					"structure_state": current_state,
					"faction": current_faction
				})
				current_state = ""
				current_faction = ""
				poi_structure_state[poi_name] = ""
				poi_structure_faction[poi_name] = ""
				poi_structure_started_at.erase(poi_name)
				poi_structure_unstable_started_at.erase(poi_name)

	var structure_seconds: float = 0.0
	if current_state != "":
		var started_at: float = float(poi_structure_started_at.get(poi_name, time_seconds))
		structure_seconds = max(0.0, time_seconds - started_at)

	return {
		"state": current_state,
		"active": current_state != "",
		"faction": current_faction,
		"structure_seconds": structure_seconds,
		"events": events
	}


func _ensure_allegiance_for_poi(poi_name: String, faction: String) -> String:
	var current: String = str(poi_allegiance_id.get(poi_name, ""))
	if current != "":
		return current
	var next_id := "%s:%s" % [faction, poi_name]
	poi_allegiance_id[poi_name] = next_id
	return next_id


func _pick_doctrine_for_allegiance(
	faction: String,
	structure_state: String,
	dominant_champions: int
) -> String:
	if world_event_visual_id == "mana_surge" and dominant_champions > 0:
		return _pick_preferred_doctrine_for_faction(faction, "arcane")
	if structure_state == "human_outpost":
		if world_event_visual_id == "mana_surge":
			return _pick_preferred_doctrine_for_faction(faction, "arcane")
		return _pick_preferred_doctrine_for_faction(faction, "steadfast")
	if structure_state == "monster_lair":
		return _pick_preferred_doctrine_for_faction(faction, "warlike")
	if faction == "human":
		return _pick_preferred_doctrine_for_faction(faction, "steadfast")
	if faction == "monster":
		return _pick_preferred_doctrine_for_faction(faction, "warlike")
	return _pick_preferred_doctrine_for_faction(faction, "steadfast")


func _pick_preferred_doctrine_for_faction(faction: String, preferred: String) -> String:
	var doctrine_pool: Array[String] = _get_faction_doctrine_pool_for_kind(faction)
	if doctrine_pool.is_empty():
		if preferred in ALLEGIANCE_DOCTRINES:
			return preferred
		return "steadfast"
	if preferred in doctrine_pool:
		return preferred
	return str(doctrine_pool[0])


func _assign_doctrine_for_allegiance(
	allegiance_id: String,
	faction: String,
	structure_state: String,
	dominant_champions: int
) -> String:
	if allegiance_id == "":
		return ""
	var doctrine: String = _pick_doctrine_for_allegiance(faction, structure_state, dominant_champions)
	if not (doctrine in ALLEGIANCE_DOCTRINES):
		push_warning("WorldManager: ignored invalid doctrine '%s' for allegiance '%s'." % [doctrine, allegiance_id])
		allegiance_doctrine_by_id.erase(allegiance_id)
		doctrine_invalid_by_allegiance[allegiance_id] = doctrine
		return ""
	allegiance_doctrine_by_id[allegiance_id] = doctrine
	doctrine_invalid_by_allegiance.erase(allegiance_id)
	return doctrine


func _clear_allegiance_doctrine(allegiance_id: String) -> String:
	var doctrine: String = get_allegiance_doctrine(allegiance_id)
	if allegiance_id != "":
		allegiance_doctrine_by_id.erase(allegiance_id)
		doctrine_invalid_by_allegiance.erase(allegiance_id)
	return doctrine


func _pick_project_for_allegiance(
	allegiance_id: String,
	faction: String,
	home_poi: String,
	structure_state: String,
	doctrine: String
) -> String:
	var choice: Dictionary = _pick_project_choice_for_allegiance(
		allegiance_id,
		faction,
		home_poi,
		structure_state,
		doctrine
	)
	return str(choice.get("project_id", ""))


func _base_project_for_allegiance(
	allegiance_id: String,
	faction: String,
	structure_state: String
) -> String:
	var faction_template: Dictionary = get_allegiance_faction_template(allegiance_id)
	var project_bias: String = str(faction_template.get("project_bias", ""))
	if project_bias in ALLEGIANCE_PROJECT_TYPES:
		return project_bias

	if structure_state == "human_outpost":
		return "fortify"
	if structure_state == "monster_lair":
		return "warband_muster"
	if faction == "monster":
		return "warband_muster"
	if allegiance_id == "":
		return ""
	return "fortify"


func _pick_project_choice_for_allegiance(
	allegiance_id: String,
	faction: String,
	home_poi: String,
	structure_state: String,
	doctrine: String
) -> Dictionary:
	var doctrine_project_bias: Dictionary = get_allegiance_doctrine_project_bias(allegiance_id)
	var doctrine_source: String = str(doctrine_project_bias.get("source", "fallback"))
	var preferred_project: String = str(doctrine_project_bias.get("preferred_project", ""))
	var influence_strength: float = clampf(float(doctrine_project_bias.get("influence_strength", 0.0)), 0.0, 0.32)

	if bool(poi_raid_state.get("active", false)):
		if str(poi_raid_state.get("target_poi", "")) == home_poi:
			return {
				"project_id": "fortify",
				"base_project_id": "fortify",
				"doctrine_id": doctrine,
				"doctrine_source": doctrine_source,
				"doctrine_preferred_project": preferred_project,
				"doctrine_influence_strength": influence_strength,
				"doctrine_influenced": false
			}
		if str(poi_raid_state.get("source_poi", "")) == home_poi:
			return {
				"project_id": "warband_muster",
				"base_project_id": "warband_muster",
				"doctrine_id": doctrine,
				"doctrine_source": doctrine_source,
				"doctrine_preferred_project": preferred_project,
				"doctrine_influence_strength": influence_strength,
				"doctrine_influenced": false
			}

	if doctrine == "arcane" and world_event_visual_id == "mana_surge":
		return {
			"project_id": "ritual_focus",
			"base_project_id": "ritual_focus",
			"doctrine_id": doctrine,
			"doctrine_source": doctrine_source,
			"doctrine_preferred_project": "ritual_focus",
			"doctrine_influence_strength": influence_strength,
			"doctrine_influenced": true
		}

	if doctrine_source != "json":
		var legacy_project_id: String = ""
		if doctrine == "steadfast":
			legacy_project_id = "fortify"
		elif doctrine == "warlike":
			legacy_project_id = "warband_muster"
		elif doctrine == "arcane":
			legacy_project_id = "ritual_focus"
		if legacy_project_id in ALLEGIANCE_PROJECT_TYPES:
			return {
				"project_id": legacy_project_id,
				"base_project_id": legacy_project_id,
				"doctrine_id": doctrine,
				"doctrine_source": doctrine_source,
				"doctrine_preferred_project": preferred_project,
				"doctrine_influence_strength": 0.0,
				"doctrine_influenced": false
			}

	var base_project_id: String = _base_project_for_allegiance(allegiance_id, faction, structure_state)
	if not (base_project_id in ALLEGIANCE_PROJECT_TYPES):
		return {
			"project_id": base_project_id,
			"base_project_id": base_project_id,
			"doctrine_id": doctrine,
			"doctrine_source": doctrine_source,
			"doctrine_preferred_project": preferred_project,
			"doctrine_influence_strength": influence_strength,
			"doctrine_influenced": false
		}

	var selected_project: String = base_project_id
	var doctrine_influenced: bool = false
	if preferred_project in ALLEGIANCE_PROJECT_TYPES and preferred_project != base_project_id:
		if randf() <= influence_strength:
			selected_project = preferred_project
			doctrine_influenced = true

	return {
		"project_id": selected_project,
		"base_project_id": base_project_id,
		"doctrine_id": doctrine,
		"doctrine_source": doctrine_source,
		"doctrine_preferred_project": preferred_project,
		"doctrine_influence_strength": influence_strength,
		"doctrine_influenced": doctrine_influenced
	}


func _interrupt_allegiance_project(allegiance_id: String, time_seconds: float) -> String:
	var project_id: String = get_allegiance_project(allegiance_id)
	if allegiance_id != "":
		allegiance_project_runtime_by_id.erase(allegiance_id)
		allegiance_project_cooldown_until_by_id[allegiance_id] = time_seconds + allegiance_project_cooldown * 0.60
		allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
	return project_id


func _update_allegiance_projects_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
	var events: Array[Dictionary] = []
	var active_allegiances: Dictionary = {}

	for poi_name_variant in snapshot.keys():
		var poi_name: String = str(poi_name_variant)
		var details: Dictionary = snapshot.get(poi_name, {})
		var allegiance_id: String = str(details.get("allegiance_id", ""))
		if allegiance_id == "":
			continue
		if not bool(details.get("structure_active", false)):
			continue
		active_allegiances[allegiance_id] = {
			"home_poi": poi_name,
			"faction": str(details.get("dominant_faction", "")),
			"structure_state": str(details.get("structure_state", "")),
			"doctrine": get_allegiance_doctrine(allegiance_id)
		}

	var runtime_ids: Array = allegiance_project_runtime_by_id.keys()
	for allegiance_variant in runtime_ids:
		var allegiance_id: String = str(allegiance_variant)
		if active_allegiances.has(allegiance_id):
			continue
		var interrupted_project: String = _interrupt_allegiance_project(allegiance_id, time_seconds)
		if interrupted_project != "":
			events.append({
				"kind": "allegiance_project_interrupted",
				"poi": "",
				"allegiance_id": allegiance_id,
				"project_id": interrupted_project,
				"reason": "allegiance_lost"
			})

	var cleanup_attempt_ids: Array = allegiance_project_next_attempt_at_by_id.keys()
	for allegiance_variant in cleanup_attempt_ids:
		var allegiance_id: String = str(allegiance_variant)
		if not active_allegiances.has(allegiance_id):
			allegiance_project_next_attempt_at_by_id.erase(allegiance_id)

	var cleanup_cooldown_ids: Array = allegiance_project_cooldown_until_by_id.keys()
	for allegiance_variant in cleanup_cooldown_ids:
		var allegiance_id: String = str(allegiance_variant)
		if not active_allegiances.has(allegiance_id):
			allegiance_project_cooldown_until_by_id.erase(allegiance_id)

	for allegiance_variant in active_allegiances.keys():
		var allegiance_id: String = str(allegiance_variant)
		var context: Dictionary = active_allegiances.get(allegiance_id, {})
		var home_poi: String = str(context.get("home_poi", ""))
		var runtime: Dictionary = allegiance_project_runtime_by_id.get(allegiance_id, {})
		if not runtime.is_empty():
			var project_id: String = str(runtime.get("project_id", ""))
			var end_at: float = float(runtime.get("end_at", time_seconds))
			if project_id == "" or not (project_id in ALLEGIANCE_PROJECT_TYPES):
				allegiance_project_runtime_by_id.erase(allegiance_id)
				continue
			if time_seconds >= end_at:
				allegiance_project_runtime_by_id.erase(allegiance_id)
				allegiance_project_cooldown_until_by_id[allegiance_id] = time_seconds + allegiance_project_cooldown
				allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
				events.append({
					"kind": "allegiance_project_ended",
					"poi": home_poi,
					"allegiance_id": allegiance_id,
					"project_id": project_id
				})
			continue

		var cooldown_until: float = float(allegiance_project_cooldown_until_by_id.get(allegiance_id, 0.0))
		if time_seconds < cooldown_until:
			continue

		var next_attempt_at: float = float(allegiance_project_next_attempt_at_by_id.get(allegiance_id, 0.0))
		if time_seconds < next_attempt_at:
			continue

		allegiance_project_next_attempt_at_by_id[allegiance_id] = time_seconds + allegiance_project_check_interval
		if randf() > clampf(allegiance_project_start_chance, 0.05, 0.80):
			continue

		var project_choice: Dictionary = _pick_project_choice_for_allegiance(
			allegiance_id,
			str(context.get("faction", "")),
			home_poi,
			str(context.get("structure_state", "")),
			str(context.get("doctrine", ""))
		)
		var project_id: String = str(project_choice.get("project_id", ""))
		if not (project_id in ALLEGIANCE_PROJECT_TYPES):
			continue

		var duration: float = randf_range(
			min(allegiance_project_duration_min, allegiance_project_duration_max),
			max(allegiance_project_duration_min, allegiance_project_duration_max)
		)
		var end_at: float = time_seconds + duration
		allegiance_project_runtime_by_id[allegiance_id] = {
			"project_id": project_id,
			"home_poi": home_poi,
			"started_at": time_seconds,
			"end_at": end_at
		}
		events.append({
			"kind": "allegiance_project_started",
			"poi": home_poi,
			"allegiance_id": allegiance_id,
			"project_id": project_id,
			"duration": duration,
			"base_project_id": str(project_choice.get("base_project_id", project_id)),
			"doctrine_id": str(project_choice.get("doctrine_id", "")),
			"doctrine_source": str(project_choice.get("doctrine_source", "fallback")),
			"doctrine_project_bias": str(project_choice.get("doctrine_preferred_project", "")),
			"doctrine_project_bias_strength": float(project_choice.get("doctrine_influence_strength", 0.0)),
			"doctrine_project_influenced": bool(project_choice.get("doctrine_influenced", false))
		})

	return {
		"events": events
	}


func _try_start_vendetta(
	source_allegiance_id: String,
	target_allegiance_id: String,
	reason: String,
	time_seconds: float
) -> Dictionary:
	if source_allegiance_id == "" or target_allegiance_id == "":
		return {}
	if source_allegiance_id == target_allegiance_id:
		return {}
	if _is_vendetta_pair_suppressed(source_allegiance_id, target_allegiance_id):
		return {}
	if not _is_allegiance_anchor_active(source_allegiance_id):
		return {}
	if not _is_allegiance_anchor_active(target_allegiance_id):
		return {}

	var current: Dictionary = allegiance_vendetta_runtime_by_id.get(source_allegiance_id, {})
	if not current.is_empty():
		var current_target: String = str(current.get("target_allegiance_id", ""))
		if current_target == target_allegiance_id:
			var refreshed_end: float = max(
				float(current.get("end_at", time_seconds)),
				time_seconds + allegiance_vendetta_duration_min * 0.45
			)
			current["end_at"] = min(
				refreshed_end,
				time_seconds + max(allegiance_vendetta_duration_min, allegiance_vendetta_duration_max)
			)
			allegiance_vendetta_runtime_by_id[source_allegiance_id] = current
		return {}

	var cooldown_until: float = float(allegiance_vendetta_cooldown_until_by_id.get(source_allegiance_id, 0.0))
	if time_seconds < cooldown_until:
		return {}

	var vendetta_bias: Dictionary = get_allegiance_doctrine_vendetta_bias(source_allegiance_id)
	var vendetta_delta: float = clampf(float(vendetta_bias.get("vendetta_start_delta", 0.0)), -0.10, 0.10)
	var doctrine_source: String = str(vendetta_bias.get("source", "fallback"))
	var vendetta_start_chance: float = 1.0
	if doctrine_source == "json":
		vendetta_start_chance = clampf(0.95 + vendetta_delta, 0.82, 1.0)
	if randf() > vendetta_start_chance:
		return {}

	var duration: float = randf_range(
		min(allegiance_vendetta_duration_min, allegiance_vendetta_duration_max),
		max(allegiance_vendetta_duration_min, allegiance_vendetta_duration_max)
	)
	var doctrine_id: String = str(vendetta_bias.get("doctrine", ""))
	var doctrine_label: String = get_allegiance_doctrine_label(source_allegiance_id, doctrine_id)
	allegiance_vendetta_runtime_by_id[source_allegiance_id] = {
		"target_allegiance_id": target_allegiance_id,
		"reason": reason,
		"started_at": time_seconds,
		"end_at": time_seconds + duration
	}
	return {
		"kind": "vendetta_started",
		"source_allegiance_id": source_allegiance_id,
		"target_allegiance_id": target_allegiance_id,
		"reason": reason,
		"duration": duration,
		"doctrine_id": doctrine_id,
		"doctrine_label": doctrine_label,
		"doctrine_source": doctrine_source,
		"doctrine_vendetta_bias": vendetta_delta,
		"doctrine_vendetta_start_chance": vendetta_start_chance
	}


func _mending_pair_key(source_allegiance_id: String, target_allegiance_id: String) -> String:
	var first_id: String = source_allegiance_id
	var second_id: String = target_allegiance_id
	if first_id > second_id:
		var swapped: String = first_id
		first_id = second_id
		second_id = swapped
	return "%s|%s" % [first_id, second_id]


func _is_vendetta_pair_suppressed(source_allegiance_id: String, target_allegiance_id: String) -> bool:
	if source_allegiance_id == "" or target_allegiance_id == "":
		return false
	var pair_key: String = _mending_pair_key(source_allegiance_id, target_allegiance_id)
	return bool(vendetta_suppressed_pair_keys.get(pair_key, false))


func _get_alert_runtime_for_allegiance(allegiance_id: String, time_seconds: float = 0.0) -> Dictionary:
	if allegiance_id == "":
		return {}
	var runtime: Dictionary = alert_state_by_allegiance.get(allegiance_id, {})
	if runtime.is_empty():
		return {}
	var ends_at: float = float(runtime.get("ends_at", 0.0))
	if ends_at > 0.0 and time_seconds > 0.0 and time_seconds >= ends_at:
		return {}
	return runtime


func _is_allegiance_anchor_active(allegiance_id: String) -> bool:
	if allegiance_id == "":
		return false
	for poi_name_variant in poi_allegiance_id.keys():
		var poi_name: String = str(poi_name_variant)
		if str(poi_allegiance_id.get(poi_name, "")) != allegiance_id:
			continue
		if str(poi_structure_state.get(poi_name, "")) == "":
			continue
		return true
	return false


func _update_vendetta_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
	var events: Array[Dictionary] = []
	var active_allegiances: Dictionary = {}
	for poi_name_variant in snapshot.keys():
		var poi_name: String = str(poi_name_variant)
		var details: Dictionary = snapshot.get(poi_name, {})
		var allegiance_id: String = str(details.get("allegiance_id", ""))
		if allegiance_id == "":
			continue
		if not bool(details.get("structure_active", false)):
			continue
		active_allegiances[allegiance_id] = true

	var runtime_ids: Array = allegiance_vendetta_runtime_by_id.keys()
	for source_variant in runtime_ids:
		var source_allegiance_id: String = str(source_variant)
		var runtime: Dictionary = allegiance_vendetta_runtime_by_id.get(source_allegiance_id, {})
		var target_allegiance_id: String = str(runtime.get("target_allegiance_id", ""))
		var reason: String = str(runtime.get("reason", "vendetta"))
		if not active_allegiances.has(source_allegiance_id):
			allegiance_vendetta_runtime_by_id.erase(source_allegiance_id)
			continue
		if target_allegiance_id == "" or not active_allegiances.has(target_allegiance_id):
			allegiance_vendetta_runtime_by_id.erase(source_allegiance_id)
			allegiance_vendetta_cooldown_until_by_id[source_allegiance_id] = time_seconds + allegiance_vendetta_cooldown
			events.append({
				"kind": "vendetta_resolved",
				"source_allegiance_id": source_allegiance_id,
				"target_allegiance_id": target_allegiance_id,
				"reason": reason
			})
			continue
		var end_at: float = float(runtime.get("end_at", time_seconds))
		if time_seconds >= end_at:
			allegiance_vendetta_runtime_by_id.erase(source_allegiance_id)
			allegiance_vendetta_cooldown_until_by_id[source_allegiance_id] = time_seconds + allegiance_vendetta_cooldown
			events.append({
				"kind": "vendetta_expired",
				"source_allegiance_id": source_allegiance_id,
				"target_allegiance_id": target_allegiance_id,
				"reason": reason
			})

	var cooldown_ids: Array = allegiance_vendetta_cooldown_until_by_id.keys()
	for source_variant in cooldown_ids:
		var source_allegiance_id: String = str(source_variant)
		if active_allegiances.has(source_allegiance_id):
			continue
		allegiance_vendetta_cooldown_until_by_id.erase(source_allegiance_id)

	return {
		"events": events
	}


func _is_neutral_gate_kind(poi_kind: String) -> bool:
	return poi_kind == "rift_gate"


func _is_neutral_gate_poi(poi: Dictionary) -> bool:
	return _is_neutral_gate_kind(str(poi.get("kind", "")))


func _find_neutral_gate_poi_name() -> String:
	for poi in pois:
		if _is_neutral_gate_poi(poi):
			return str(poi.get("name", ""))
	return ""


func _can_open_neutral_gate(snapshot: Dictionary, gate_name: String) -> bool:
	if world_event_visual_id == "":
		return false

	var stable_anchor_found: bool = false
	for poi_name_variant in snapshot.keys():
		var poi_name: String = str(poi_name_variant)
		if poi_name == gate_name:
			continue
		var details: Dictionary = snapshot.get(poi_name, {})
		if not bool(details.get("structure_active", false)):
			continue
		var dominance_seconds: float = float(details.get("dominance_seconds", 0.0))
		if dominance_seconds < neutral_gate_min_dominance_seconds:
			continue
		stable_anchor_found = true
		break

	return stable_anchor_found


func _update_neutral_gate_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
	var gate_name: String = _find_neutral_gate_poi_name()
	var events: Array[Dictionary] = []

	if gate_name == "":
		neutral_gate_status = "dormant"
		neutral_gate_open_until = 0.0
		neutral_gate_cooldown_until = 0.0
		neutral_gate_breach_pending = false
		neutral_gate_bonus_breach_used = false
		return {
			"poi": "",
			"status": neutral_gate_status,
			"active": false,
			"remaining": 0.0,
			"cooldown": 0.0,
			"opened_total": neutral_gate_opened_total,
			"closed_total": neutral_gate_closed_total,
			"breaches_total": neutral_gate_breaches_total,
			"events": events
		}

	if neutral_gate_status == "open":
		if time_seconds >= neutral_gate_open_until:
			neutral_gate_status = "dormant"
			neutral_gate_open_until = 0.0
			neutral_gate_breach_pending = false
			neutral_gate_bonus_breach_used = false
			neutral_gate_closed_total += 1
			neutral_gate_cooldown_until = time_seconds + randf_range(neutral_gate_cooldown_min, neutral_gate_cooldown_max)
			events.append({
				"kind": "neutral_gate_closed",
				"poi": gate_name,
				"cooldown_seconds": max(0.0, neutral_gate_cooldown_until - time_seconds)
			})
	else:
		if neutral_gate_cooldown_until <= 0.0:
			neutral_gate_cooldown_until = time_seconds + randf_range(
				neutral_gate_cooldown_min * 0.55,
				neutral_gate_cooldown_max * 0.72
			)
		elif time_seconds >= neutral_gate_cooldown_until:
			if _can_open_neutral_gate(snapshot, gate_name):
				neutral_gate_status = "open"
				neutral_gate_open_until = time_seconds + neutral_gate_open_duration
				neutral_gate_opened_total += 1
				neutral_gate_breach_pending = true
				neutral_gate_bonus_breach_used = false
				events.append({
					"kind": "neutral_gate_opened",
					"poi": gate_name,
					"open_seconds": neutral_gate_open_duration,
					"world_event": world_event_visual_id
				})
			else:
				neutral_gate_cooldown_until = time_seconds + neutral_gate_retry_delay

	if neutral_gate_status == "open" and neutral_gate_breach_pending:
		neutral_gate_breach_pending = false
		neutral_gate_breaches_total += 1
		var gate_position: Vector3 = _get_poi_by_name(gate_name).get("position", Vector3.ZERO)
		events.append({
			"kind": "neutral_gate_breach",
			"poi": gate_name,
			"position": gate_position,
			"world_event": world_event_visual_id
		})

	var remaining: float = 0.0
	var cooldown: float = 0.0
	if neutral_gate_status == "open":
		remaining = max(0.0, neutral_gate_open_until - time_seconds)
	else:
		cooldown = max(0.0, neutral_gate_cooldown_until - time_seconds)

	return {
		"poi": gate_name,
		"status": neutral_gate_status,
		"active": neutral_gate_status == "open",
		"remaining": remaining,
		"cooldown": cooldown,
		"opened_total": neutral_gate_opened_total,
		"closed_total": neutral_gate_closed_total,
		"breaches_total": neutral_gate_breaches_total,
		"events": events
	}


func _update_raid_runtime(snapshot: Dictionary, time_seconds: float) -> Dictionary:
	var events: Array[Dictionary] = []
	var has_outpost: bool = _find_structure_poi(snapshot, "human_outpost") != ""
	var has_lair: bool = _find_structure_poi(snapshot, "monster_lair") != ""

	var raid_active: bool = bool(poi_raid_state.get("active", false))
	if raid_active:
		var source_poi: String = str(poi_raid_state.get("source_poi", ""))
		var target_poi: String = str(poi_raid_state.get("target_poi", ""))
		var attacker_faction: String = str(poi_raid_state.get("attacker_faction", ""))
		var attacker_allegiance_id: String = str(poi_raid_state.get("attacker_allegiance_id", ""))
		var defender_allegiance_id: String = str(poi_raid_state.get("defender_allegiance_id", ""))
		var started_at: float = float(poi_raid_state.get("started_at", time_seconds))

		var source_details: Dictionary = snapshot.get(source_poi, {})
		var target_details: Dictionary = snapshot.get(target_poi, {})
		var source_structure_ok: bool = bool(source_details.get("structure_active", false))
		var target_structure_ok: bool = bool(target_details.get("structure_active", false))

		if not source_structure_ok or not target_structure_ok:
			events.append(_end_raid("interrupted", time_seconds))
		else:
			var target_dominant_faction: String = str(target_details.get("dominant_faction", ""))
			var target_dom_seconds: float = float(target_details.get("dominance_seconds", 0.0))
			if target_dominant_faction == attacker_faction and target_dom_seconds >= poi_raid_success_hold:
				if defender_allegiance_id != "" and attacker_allegiance_id != "":
					var vendetta_event: Dictionary = _try_start_vendetta(
						defender_allegiance_id,
						attacker_allegiance_id,
						"raid_loss",
						time_seconds
					)
					if not vendetta_event.is_empty():
						events.append(vendetta_event)
				events.append(_end_raid("success", time_seconds))
			elif time_seconds - started_at >= poi_raid_duration:
				events.append(_end_raid("timeout", time_seconds))
	else:
		if time_seconds >= poi_raid_cooldown_until and has_outpost and has_lair:
			var next_attacker: String = "human"
			if poi_last_raid_attacker == "human":
				next_attacker = "monster"

			var source_poi_name: String = _find_structure_poi(snapshot, "human_outpost") if next_attacker == "human" else _find_structure_poi(snapshot, "monster_lair")
			var target_poi_name: String = _find_structure_poi(snapshot, "monster_lair") if next_attacker == "human" else _find_structure_poi(snapshot, "human_outpost")
			if source_poi_name != "" and target_poi_name != "":
				var attacker_allegiance_id: String = str(poi_allegiance_id.get(source_poi_name, ""))
				var defender_allegiance_id: String = str(poi_allegiance_id.get(target_poi_name, ""))
				poi_raid_state = {
					"active": true,
					"attacker_faction": next_attacker,
					"defender_faction": "monster" if next_attacker == "human" else "human",
					"source_poi": source_poi_name,
					"target_poi": target_poi_name,
					"attacker_allegiance_id": attacker_allegiance_id,
					"defender_allegiance_id": defender_allegiance_id,
					"started_at": time_seconds
				}
				poi_last_raid_attacker = next_attacker
				events.append({
					"kind": "raid_started",
					"attacker_faction": next_attacker,
					"defender_faction": str(poi_raid_state.get("defender_faction", "")),
					"source_poi": source_poi_name,
					"target_poi": target_poi_name,
					"attacker_allegiance_id": attacker_allegiance_id,
					"defender_allegiance_id": defender_allegiance_id
				})

	return {
		"state": poi_raid_state.duplicate(true),
		"events": events
	}


func _end_raid(outcome: String, time_seconds: float) -> Dictionary:
	var event := {
		"kind": "raid_ended",
		"outcome": outcome,
		"attacker_faction": str(poi_raid_state.get("attacker_faction", "")),
		"defender_faction": str(poi_raid_state.get("defender_faction", "")),
		"source_poi": str(poi_raid_state.get("source_poi", "")),
		"target_poi": str(poi_raid_state.get("target_poi", "")),
		"attacker_allegiance_id": str(poi_raid_state.get("attacker_allegiance_id", "")),
		"defender_allegiance_id": str(poi_raid_state.get("defender_allegiance_id", "")),
		"duration": max(0.0, time_seconds - float(poi_raid_state.get("started_at", time_seconds)))
	}
	poi_raid_state.clear()
	poi_raid_cooldown_until = time_seconds + poi_raid_cooldown
	return event


func _find_structure_poi(snapshot: Dictionary, structure_state: String) -> String:
	for poi_name_variant in snapshot.keys():
		var poi_name: String = str(poi_name_variant)
		var details: Dictionary = snapshot.get(poi_name, {})
		if str(details.get("structure_state", "")) == structure_state and bool(details.get("structure_active", false)):
			return poi_name
	return ""


func _get_raid_role_for_poi(poi_name: String) -> String:
	if not bool(poi_raid_state.get("active", false)):
		return "none"
	if str(poi_raid_state.get("source_poi", "")) == poi_name:
		return "source"
	if str(poi_raid_state.get("target_poi", "")) == poi_name:
		return "target"
	return "none"


func _structure_color(structure_state: String) -> Color:
	match structure_state:
		"human_outpost":
			return Color(0.52, 0.80, 1.0)
		"monster_lair":
			return Color(1.0, 0.52, 0.64)
		_:
			return Color(0.8, 0.8, 0.8)


func _get_status_color(status: String) -> Color:
	match status:
		"human_dominant":
			return Color(0.43, 0.76, 1.0)
		"monster_dominant":
			return Color(1.0, 0.45, 0.42)
		"contested":
			return Color(1.0, 0.86, 0.36)
		_:
			return Color(0.62, 0.62, 0.62)


func _set_mesh_color(mesh: MeshInstance3D, color: Color, emission_strength: float) -> void:
	var material := mesh.material_override as StandardMaterial3D
	if material == null:
		return
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color * emission_strength


func _apply_world_event_visual_bias(
	ring: MeshInstance3D,
	beacon: MeshInstance3D,
	status_color: Color,
	intensity: float,
	time_seconds: float
) -> void:
	match world_event_visual_id:
		"mana_surge":
			var surge_mix := 0.22 + 0.06 * sin(time_seconds * 5.0)
			_set_mesh_color(beacon, status_color.lerp(Color(0.74, 0.56, 1.0), surge_mix), intensity + 0.22)
		"monster_frenzy":
			var frenzy_mix := 0.24 + 0.05 * sin(time_seconds * 6.2)
			_set_mesh_color(ring, status_color.lerp(Color(1.0, 0.38, 0.30), frenzy_mix), intensity + 0.18)
		"sanctuary_calm":
			var calm_mix := 0.20 + 0.04 * sin(time_seconds * 3.4)
			_set_mesh_color(ring, status_color.lerp(Color(0.52, 0.82, 1.0), calm_mix), intensity + 0.10)
func get_poi_runtime_snapshot() -> Dictionary:
	return {}
