extends RefCounted
class_name DataLoader

const CREATURES_PATH: String = "res://data/creatures.json"
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

var _profiles_by_id: Dictionary = {}
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
