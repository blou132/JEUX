extends RefCounted
class_name AgentAI


func decide_action(actor: Actor, world: WorldManager, all_actors: Array) -> Dictionary:
    var enemy: Actor = world.find_nearest_enemy(actor, all_actors, actor.vision_range)
    if enemy == null:
        return {
            "state": "wander",
            "reason": "no_enemy_visible"
        }

    var distance: float = actor.global_position.distance_to(enemy.global_position)
    var under_pressure: bool = _is_under_pressure(actor)

    if under_pressure and distance <= actor.vision_range * 0.9:
        return {
            "state": "flee",
            "target": enemy,
            "reason": "pressure_and_threat"
        }

    if actor.can_cast_magic() and distance <= actor.magic_range and distance > actor.attack_range * 1.2:
        return {
            "state": "cast",
            "target": enemy,
            "reason": "magic_range"
        }

    if distance <= actor.attack_range:
        return {
            "state": "attack",
            "target": enemy,
            "reason": "melee_range"
        }

    if distance > actor.vision_range * 0.55:
        return {
            "state": "detect",
            "target": enemy,
            "reason": "enemy_detected_far"
        }

    return {
        "state": "chase",
        "target": enemy,
        "reason": "enemy_detected_near"
    }


func _is_under_pressure(actor: Actor) -> bool:
    return actor.hp <= actor.max_hp * actor.flee_health_ratio or actor.energy <= actor.max_energy * 0.20
