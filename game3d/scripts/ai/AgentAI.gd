extends RefCounted
class_name AgentAI


func decide_action(actor: Actor, world: WorldManager, all_actors: Array) -> Dictionary:
    var enemy: Actor = world.find_nearest_enemy(actor, all_actors, actor.vision_range)
    if enemy == null:
        var poi_guidance: Dictionary = world.get_poi_guidance(actor.global_position, actor.faction)
        if not poi_guidance.is_empty() and randf() <= 0.58:
            return {
                "state": "poi",
                "target_position": poi_guidance.get("target_position", actor.global_position),
                "reason": "poi_guidance:%s" % str(poi_guidance.get("name", "poi"))
            }
        return {
            "state": "wander",
            "reason": "no_enemy_visible"
        }

    var distance: float = actor.global_position.distance_to(enemy.global_position)
    var under_pressure: bool = _is_under_pressure(actor)
    var is_ranged: bool = actor.actor_kind == "ranged_monster"
    var preferred_min_distance: float = actor.attack_range * 1.85

    if is_ranged and distance < preferred_min_distance and not under_pressure:
        return {
            "state": "reposition",
            "target": enemy,
            "reason": "ranged_keep_distance"
        }

    if under_pressure and distance <= actor.vision_range * 0.9:
        return {
            "state": "flee",
            "target": enemy,
            "reason": "pressure_and_threat"
        }

    if actor.can_cast_control() and distance <= actor.control_range and distance > actor.attack_range * 1.12 and not enemy.is_slowed():
        if enemy.actor_kind in ["brute_monster", "ranged_monster"] or distance <= actor.control_range * 0.78:
            return {
                "state": "cast_control",
                "target": enemy,
                "reason": "control_window"
            }

    if actor.can_cast_nova() and distance <= actor.nova_radius * 0.95:
        return {
            "state": "cast_nova",
            "target": enemy,
            "reason": "nova_range"
        }

    if actor.can_cast_magic() and distance <= actor.magic_range and distance > actor.attack_range * 1.2:
        return {
            "state": "cast",
            "target": enemy,
            "reason": "magic_range" if not is_ranged else "ranged_cast"
        }

    if distance <= actor.attack_range:
        return {
            "state": "attack",
            "target": enemy,
            "reason": "melee_range"
        }

    if distance > actor.vision_range * 0.55:
        if actor.actor_kind == "brute_monster":
            return {
                "state": "chase",
                "target": enemy,
                "reason": "brute_commit"
            }
        if is_ranged and distance <= actor.magic_range * 1.08:
            return {
                "state": "detect",
                "target": enemy,
                "reason": "ranged_hold_line"
            }
        return {
            "state": "detect",
            "target": enemy,
            "reason": "enemy_detected_far"
        }

    if is_ranged and distance > actor.attack_range * 1.15 and actor.can_cast_magic():
        return {
            "state": "cast",
            "target": enemy,
            "reason": "ranged_pressure_cast"
        }

    return {
        "state": "chase",
        "target": enemy,
        "reason": "enemy_detected_near" if not is_ranged else "ranged_reposition_chase"
    }


func _is_under_pressure(actor: Actor) -> bool:
    return actor.hp <= actor.max_hp * actor.flee_health_ratio or actor.energy <= actor.max_energy * 0.20
