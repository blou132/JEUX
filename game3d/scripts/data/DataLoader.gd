extends RefCounted
class_name DataLoader

const CREATURES_PATH: String = "res://data/creatures.json"
const EVENTS_PATH: String = "res://data/events.json"
const FACTIONS_PATH: String = "res://data/factions.json"
const REQUIRED_PROFILE_FIELDS: Array[String] = [
	"id",
	"kind",
	"hp",
	"speed",
	"melee_damage",
	"magic_damage",
	"magic_range",
	"role",
	"tags",
]
const REQUIRED_WORLD_EVENT_FIELDS: Array[String] = [
	"id",
	"label",
	"duration",
	"cooldown_min",
	"cooldown_max",
	"modifiers",
	"tags",
]
const REQUIRED_FACTION_TEMPLATE_FIELDS: Array[String] = [
	"id",
	"label",
	"kind",
	"default_doctrine_pool",
	"tags",
]
const VALID_FACTION_TEMPLATE_KINDS: Array[String] = ["human", "monster"]
const VALID_FACTION_DOCTRINES: Array[String] = ["warlike", "steadfast", "arcane"]
const VALID_FACTION_PROJECT_BIASES: Array[String] = ["fortify", "warband_muster", "ritual_focus"]

var _profiles_by_id: Dictionary = {}
var _world_events_by_id: Dictionary = {}
var _faction_templates_by_id: Dictionary = {}
var _last_error: String = ""


func load_creature_profiles(path: String = CREATURES_PATH) -> bool:
	_profiles_by_id.clear()
	_last_error = ""

	if not FileAccess.file_exists(path):
		return _set_error("missing file: %s" % path)

	var raw_text: String = FileAccess.get_file_as_string(path)
	var parser := JSON.new()
	var parse_result: int = parser.parse(raw_text)
	if parse_result != OK:
		return _set_error("invalid JSON (%s) at line %d" % [parser.get_error_message(), parser.get_error_line()])

	if typeof(parser.data) != TYPE_DICTIONARY:
		return _set_error("root payload must be an object")
	var payload: Dictionary = parser.data

	var profiles_variant: Variant = payload.get("profiles", [])
	if typeof(profiles_variant) != TYPE_ARRAY:
		return _set_error("payload.profiles must be an array")

	var profiles: Array = profiles_variant
	var ignored_profiles: int = 0
	for profile_variant in profiles:
		if typeof(profile_variant) != TYPE_DICTIONARY:
			ignored_profiles += 1
			push_warning("DataLoader: ignored non-object creature profile entry.")
			continue

		var profile: Dictionary = profile_variant
		var validation_error: String = _validate_profile(profile)
		if validation_error != "":
			ignored_profiles += 1
			push_warning("DataLoader: ignored profile (%s)." % validation_error)
			continue

		var profile_id: String = str(profile.get("id", ""))
		_profiles_by_id[profile_id] = profile.duplicate(true)

	if _profiles_by_id.is_empty():
		return _set_error("no valid creature profiles found")

	if ignored_profiles > 0:
		print("DataLoader: loaded %d creature profiles, ignored %d invalid entries." % [_profiles_by_id.size(), ignored_profiles])
	else:
		print("DataLoader: loaded %d creature profiles." % _profiles_by_id.size())
	return true


func get_creature_profiles() -> Dictionary:
	return _profiles_by_id.duplicate(true)


func get_creature_profile(profile_id: String) -> Dictionary:
	if not _profiles_by_id.has(profile_id):
		return {}
	return Dictionary(_profiles_by_id[profile_id]).duplicate(true)


func load_world_events(path: String = EVENTS_PATH) -> bool:
	_world_events_by_id.clear()
	_last_error = ""

	if not FileAccess.file_exists(path):
		return _set_error("missing file: %s" % path)

	var raw_text: String = FileAccess.get_file_as_string(path)
	var parser := JSON.new()
	var parse_result: int = parser.parse(raw_text)
	if parse_result != OK:
		return _set_error("invalid JSON (%s) at line %d" % [parser.get_error_message(), parser.get_error_line()])

	if typeof(parser.data) != TYPE_DICTIONARY:
		return _set_error("root payload must be an object")
	var payload: Dictionary = parser.data

	var events_variant: Variant = payload.get("events", [])
	if typeof(events_variant) != TYPE_ARRAY:
		return _set_error("payload.events must be an array")

	var events: Array = events_variant
	var ignored_events: int = 0
	for event_variant in events:
		if typeof(event_variant) != TYPE_DICTIONARY:
			ignored_events += 1
			push_warning("DataLoader: ignored non-object world event entry.")
			continue

		var event_data: Dictionary = event_variant
		var validation_error: String = _validate_world_event(event_data)
		if validation_error != "":
			ignored_events += 1
			push_warning("DataLoader: ignored world event (%s)." % validation_error)
			continue

		var event_id: String = str(event_data.get("id", ""))
		_world_events_by_id[event_id] = event_data.duplicate(true)

	if _world_events_by_id.is_empty():
		return _set_error("no valid world events found")

	if ignored_events > 0:
		print("DataLoader: loaded %d world events, ignored %d invalid entries." % [_world_events_by_id.size(), ignored_events])
	else:
		print("DataLoader: loaded %d world events." % _world_events_by_id.size())
	return true


func get_world_events() -> Dictionary:
	return _world_events_by_id.duplicate(true)


func get_world_event(event_id: String) -> Dictionary:
	if not _world_events_by_id.has(event_id):
		return {}
	return Dictionary(_world_events_by_id[event_id]).duplicate(true)


func load_faction_templates(path: String = FACTIONS_PATH) -> bool:
	_faction_templates_by_id.clear()
	_last_error = ""

	if not FileAccess.file_exists(path):
		return _set_error("missing file: %s" % path)

	var raw_text: String = FileAccess.get_file_as_string(path)
	var parser := JSON.new()
	var parse_result: int = parser.parse(raw_text)
	if parse_result != OK:
		return _set_error("invalid JSON (%s) at line %d" % [parser.get_error_message(), parser.get_error_line()])

	if typeof(parser.data) != TYPE_DICTIONARY:
		return _set_error("root payload must be an object")
	var payload: Dictionary = parser.data

	var factions_variant: Variant = payload.get("factions", [])
	if typeof(factions_variant) != TYPE_ARRAY:
		return _set_error("payload.factions must be an array")

	var faction_templates: Array = factions_variant
	var ignored_templates: int = 0
	for template_variant in faction_templates:
		if typeof(template_variant) != TYPE_DICTIONARY:
			ignored_templates += 1
			push_warning("DataLoader: ignored non-object faction template entry.")
			continue

		var template_data: Dictionary = template_variant
		var validation_error: String = _validate_faction_template(template_data)
		if validation_error != "":
			ignored_templates += 1
			push_warning("DataLoader: ignored faction template (%s)." % validation_error)
			continue

		var template_id: String = str(template_data.get("id", ""))
		if _faction_templates_by_id.has(template_id):
			ignored_templates += 1
			push_warning("DataLoader: ignored duplicate faction template id '%s'." % template_id)
			continue

		_faction_templates_by_id[template_id] = template_data.duplicate(true)

	if _faction_templates_by_id.is_empty():
		return _set_error("no valid faction templates found")

	if ignored_templates > 0:
		print(
			"DataLoader: loaded %d faction templates, ignored %d invalid entries."
			% [_faction_templates_by_id.size(), ignored_templates]
		)
	else:
		print("DataLoader: loaded %d faction templates." % _faction_templates_by_id.size())
	return true


func get_faction_templates() -> Dictionary:
	return _faction_templates_by_id.duplicate(true)


func get_faction_template(template_id: String) -> Dictionary:
	if not _faction_templates_by_id.has(template_id):
		return {}
	return Dictionary(_faction_templates_by_id[template_id]).duplicate(true)


func get_last_error() -> String:
	return _last_error


func _set_error(message: String) -> bool:
	_last_error = message
	push_warning("DataLoader: %s" % message)
	return false


func _validate_profile(profile: Dictionary) -> String:
	for field in REQUIRED_PROFILE_FIELDS:
		if not profile.has(field):
			return "missing field '%s'" % field

	var profile_id: String = str(profile.get("id", ""))
	if profile_id == "":
		return "empty profile id"

	if typeof(profile.get("kind", "")) != TYPE_STRING:
		return "%s.kind must be a string" % profile_id
	if typeof(profile.get("role", "")) != TYPE_STRING:
		return "%s.role must be a string" % profile_id

	var tags_variant: Variant = profile.get("tags", [])
	if typeof(tags_variant) != TYPE_ARRAY:
		return "%s.tags must be an array" % profile_id
	var tags: Array = tags_variant
	for tag in tags:
		if typeof(tag) != TYPE_STRING:
			return "%s.tags entries must be strings" % profile_id

	for numeric_field in ["hp", "speed", "melee_damage", "magic_damage", "magic_range"]:
		var numeric_value: Variant = profile.get(numeric_field, null)
		if typeof(numeric_value) != TYPE_INT and typeof(numeric_value) != TYPE_FLOAT:
			return "%s.%s must be numeric" % [profile_id, numeric_field]
		var as_float: float = float(numeric_value)
		if numeric_field in ["hp", "speed"] and as_float <= 0.0:
			return "%s.%s must be > 0" % [profile_id, numeric_field]
		if numeric_field in ["melee_damage", "magic_damage", "magic_range"] and as_float < 0.0:
			return "%s.%s must be >= 0" % [profile_id, numeric_field]

	return ""


func _validate_world_event(event_data: Dictionary) -> String:
	for field in REQUIRED_WORLD_EVENT_FIELDS:
		if not event_data.has(field):
			return "missing field '%s'" % field

	var event_id: String = str(event_data.get("id", ""))
	if event_id == "":
		return "empty event id"

	var label: String = str(event_data.get("label", "")).strip_edges()
	if label == "":
		return "%s.label must be a non-empty string" % event_id

	for numeric_field in ["duration", "cooldown_min", "cooldown_max"]:
		var numeric_value: Variant = event_data.get(numeric_field, null)
		if typeof(numeric_value) != TYPE_INT and typeof(numeric_value) != TYPE_FLOAT:
			return "%s.%s must be numeric" % [event_id, numeric_field]
		var as_float: float = float(numeric_value)
		if numeric_field == "duration" and as_float <= 0.0:
			return "%s.duration must be > 0" % event_id
		if numeric_field in ["cooldown_min", "cooldown_max"] and as_float < 0.0:
			return "%s.%s must be >= 0" % [event_id, numeric_field]

	if float(event_data.get("cooldown_max", 0.0)) < float(event_data.get("cooldown_min", 0.0)):
		return "%s.cooldown_max must be >= cooldown_min" % event_id

	var modifiers_variant: Variant = event_data.get("modifiers", {})
	if typeof(modifiers_variant) != TYPE_DICTIONARY:
		return "%s.modifiers must be an object" % event_id
	var modifiers: Dictionary = modifiers_variant
	if modifiers.is_empty():
		return "%s.modifiers must not be empty" % event_id
	for key in modifiers.keys():
		var value: Variant = modifiers[key]
		if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
			return "%s.modifiers.%s must be numeric" % [event_id, str(key)]

	var tags_variant: Variant = event_data.get("tags", [])
	if typeof(tags_variant) != TYPE_ARRAY:
		return "%s.tags must be an array" % event_id
	var tags: Array = tags_variant
	for tag in tags:
		if typeof(tag) != TYPE_STRING:
			return "%s.tags entries must be strings" % event_id

	return ""


func _validate_faction_template(template_data: Dictionary) -> String:
	for field in REQUIRED_FACTION_TEMPLATE_FIELDS:
		if not template_data.has(field):
			return "missing field '%s'" % field

	var template_id: String = str(template_data.get("id", ""))
	if template_id == "":
		return "empty template id"

	var label: String = str(template_data.get("label", "")).strip_edges()
	if label == "":
		return "%s.label must be a non-empty string" % template_id

	var kind: String = str(template_data.get("kind", ""))
	if not (kind in VALID_FACTION_TEMPLATE_KINDS):
		return "%s.kind must be one of %s" % [template_id, str(VALID_FACTION_TEMPLATE_KINDS)]

	var doctrine_pool_variant: Variant = template_data.get("default_doctrine_pool", [])
	if typeof(doctrine_pool_variant) != TYPE_ARRAY:
		return "%s.default_doctrine_pool must be an array" % template_id
	var doctrine_pool: Array = doctrine_pool_variant
	if doctrine_pool.is_empty():
		return "%s.default_doctrine_pool must not be empty" % template_id
	for doctrine in doctrine_pool:
		if typeof(doctrine) != TYPE_STRING:
			return "%s.default_doctrine_pool entries must be strings" % template_id
		if not (str(doctrine) in VALID_FACTION_DOCTRINES):
			return "%s.default_doctrine_pool contains invalid doctrine '%s'" % [template_id, str(doctrine)]

	if template_data.has("project_bias"):
		var project_bias_value: Variant = template_data.get("project_bias", "")
		if typeof(project_bias_value) != TYPE_STRING:
			return "%s.project_bias must be a string" % template_id
		var project_bias: String = str(project_bias_value).strip_edges()
		if project_bias != "" and not (project_bias in VALID_FACTION_PROJECT_BIASES):
			return "%s.project_bias must be one of %s" % [template_id, str(VALID_FACTION_PROJECT_BIASES)]

	for numeric_field in ["raid_bias", "defense_bias", "rally_bias"]:
		if not template_data.has(numeric_field):
			continue
		var numeric_value: Variant = template_data.get(numeric_field, null)
		if typeof(numeric_value) != TYPE_INT and typeof(numeric_value) != TYPE_FLOAT:
			return "%s.%s must be numeric" % [template_id, numeric_field]
		var as_float: float = float(numeric_value)
		if as_float < -0.25 or as_float > 0.25:
			return "%s.%s must be between -0.25 and 0.25" % [template_id, numeric_field]

	var tags_variant: Variant = template_data.get("tags", [])
	if typeof(tags_variant) != TYPE_ARRAY:
		return "%s.tags must be an array" % template_id
	var tags: Array = tags_variant
	for tag in tags:
		if typeof(tag) != TYPE_STRING:
			return "%s.tags entries must be strings" % template_id
		if str(tag).strip_edges() == "":
			return "%s.tags entries must be non-empty strings" % template_id

	return ""
