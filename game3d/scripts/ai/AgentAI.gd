extends RefCounted
class_name AgentAI


func decide_action(actor: Actor, world: WorldManager, all_actors: Array) -> Dictionary:
    var rally_context: Dictionary = _build_rally_context(actor, all_actors)
    var rally_leader: Actor = rally_context.get("leader", null)
    var rally_bonus: bool = bool(rally_context.get("bonus_active", false))
    var rally_pressure_target: Actor = rally_context.get("pressure_target", null)
    var enemy: Actor = world.find_nearest_enemy(actor, all_actors, actor.vision_range)
    if enemy == null:
        if rally_leader != null:
            if rally_pressure_target != null:
                return _with_rally(
                    {
                        "state": "rally",
                        "target": rally_pressure_target,
                        "target_position": rally_pressure_target.global_position,
                        "reason": "rally_pressure"
                    },
                    rally_leader,
                    rally_bonus
                )

            var rally_distance: float = float(rally_context.get("distance", INF))
            if rally_distance > actor.attack_range * 1.05 and randf() <= 0.66:
                return _with_rally(
                    {
                        "state": "rally",
                        "target_position": rally_leader.global_position,
                        "reason": "rally_regroup"
                    },
                    rally_leader,
                    rally_bonus
                )

        var defense_guidance: Dictionary = world.get_allegiance_defense_guidance(
            actor.global_position,
            actor.faction,
            actor.home_poi
        )
        if not defense_guidance.is_empty():
            var defense_weight: float = float(defense_guidance.get("weight", 0.62))
            if randf() <= clampf(defense_weight, 0.22, 0.90):
                return _with_rally(
                    {
                        "state": "poi",
                        "target_position": defense_guidance.get("target_position", actor.global_position),
                        "reason": str(defense_guidance.get("reason", "allegiance_defend_home"))
                    },
                    rally_leader,
                    rally_bonus
                )

        var raid_guidance: Dictionary = world.get_raid_guidance(
            actor.global_position,
            actor.faction,
            actor.allegiance_id,
            actor.home_poi
        )
        if not raid_guidance.is_empty():
            var raid_weight: float = float(raid_guidance.get("weight", 0.65))
            if randf() <= clampf(raid_weight, 0.25, 0.90):
                return _with_rally(
                    {
                        "state": "raid",
                        "target_position": raid_guidance.get("target_position", actor.global_position),
                        "reason": str(raid_guidance.get("reason", "raid_pressure"))
                    },
                    rally_leader,
                    rally_bonus
                )

        var poi_guidance: Dictionary = world.get_poi_guidance(actor.global_position, actor.faction)
        if not poi_guidance.is_empty() and randf() <= 0.58:
            return _with_rally(
                {
                    "state": "poi",
                    "target_position": poi_guidance.get("target_position", actor.global_position),
                    "reason": "poi_guidance:%s" % str(poi_guidance.get("name", "poi"))
                },
                rally_leader,
                rally_bonus
            )
        return _with_rally(
            {
                "state": "wander",
                "reason": "no_enemy_visible"
            },
            rally_leader,
            rally_bonus
        )

    if rally_pressure_target != null and rally_pressure_target != enemy:
        var pressure_distance: float = actor.global_position.distance_to(rally_pressure_target.global_position)
        if pressure_distance <= actor.vision_range * 1.08 and randf() <= 0.34:
            enemy = rally_pressure_target

    var distance: float = actor.global_position.distance_to(enemy.global_position)
    var under_pressure: bool = _is_under_pressure(actor)
    var is_ranged: bool = actor.actor_kind == "ranged_monster"
    var preferred_min_distance: float = actor.attack_range * 1.85

    if is_ranged and distance < preferred_min_distance and not under_pressure:
        return _with_rally(
            {
                "state": "reposition",
                "target": enemy,
                "reason": "ranged_keep_distance"
            },
            rally_leader,
            rally_bonus
        )

    if under_pressure and distance <= actor.vision_range * 0.9:
        return _with_rally(
            {
                "state": "flee",
                "target": enemy,
                "reason": "pressure_and_threat"
            },
            rally_leader,
            rally_bonus
        )

    if actor.can_cast_control() and distance <= actor.control_range and distance > actor.attack_range * 1.12 and not enemy.is_slowed():
        if enemy.actor_kind in ["brute_monster", "ranged_monster"] or distance <= actor.control_range * 0.78:
            if randf() <= actor.control_usage_bias:
                return _with_rally(
                    {
                        "state": "cast_control",
                        "target": enemy,
                        "reason": "control_window"
                    },
                    rally_leader,
                    rally_bonus
                )

    if actor.can_cast_nova() and distance <= actor.nova_radius * 0.95:
        if randf() <= actor.nova_usage_bias:
            return _with_rally(
                {
                    "state": "cast_nova",
                    "target": enemy,
                    "reason": "nova_range"
                },
                rally_leader,
                rally_bonus
            )

    if actor.can_cast_magic() and distance <= actor.magic_range and distance > actor.attack_range * 1.2:
        if randf() <= actor.magic_usage_bias:
            return _with_rally(
                {
                    "state": "cast",
                    "target": enemy,
                    "reason": "magic_range" if not is_ranged else "ranged_cast"
                },
                rally_leader,
                rally_bonus
            )

    if distance <= actor.attack_range:
        return _with_rally(
            {
                "state": "attack",
                "target": enemy,
                "reason": "melee_range"
            },
            rally_leader,
            rally_bonus
        )

    if distance > actor.vision_range * 0.55:
        if actor.actor_kind == "brute_monster":
            return _with_rally(
                {
                    "state": "chase",
                    "target": enemy,
                    "reason": "brute_commit"
                },
                rally_leader,
                rally_bonus
            )
        if is_ranged and distance <= actor.magic_range * 1.08:
            return _with_rally(
                {
                    "state": "detect",
                    "target": enemy,
                    "reason": "ranged_hold_line"
                },
                rally_leader,
                rally_bonus
            )
        return _with_rally(
            {
                "state": "detect",
                "target": enemy,
                "reason": "enemy_detected_far"
            },
            rally_leader,
            rally_bonus
        )

    if is_ranged and distance > actor.attack_range * 1.15 and actor.can_cast_magic():
        if randf() <= actor.magic_usage_bias:
            return _with_rally(
                {
                    "state": "cast",
                    "target": enemy,
                    "reason": "ranged_pressure_cast"
                },
                rally_leader,
                rally_bonus
            )

    return _with_rally(
        {
            "state": "chase",
            "target": enemy,
            "reason": "enemy_detected_near" if not is_ranged else "ranged_reposition_chase"
        },
        rally_leader,
        rally_bonus
    )


func _is_under_pressure(actor: Actor) -> bool:
    return actor.hp <= actor.max_hp * actor.flee_health_ratio or actor.energy <= actor.max_energy * 0.20


func _with_rally(base_decision: Dictionary, rally_leader: Actor, rally_bonus: bool) -> Dictionary:
    var decision := base_decision.duplicate()
    if rally_leader != null and not rally_leader.is_dead:
        decision["rally_leader"] = rally_leader
        decision["rally_bonus"] = rally_bonus
    return decision


func _build_rally_context(actor: Actor, all_actors: Array) -> Dictionary:
    if actor.is_champion:
        return {
            "leader": null,
            "distance": INF,
            "bonus_active": false,
            "pressure_target": null
        }

    var max_distance := min(actor.vision_range * 0.72, 14.0)
    var leader: Actor = _find_nearby_allied_champion(actor, all_actors, max_distance)
    if leader == null:
        return {
            "leader": null,
            "distance": INF,
            "bonus_active": false,
            "pressure_target": null
        }

    var distance := actor.global_position.distance_to(leader.global_position)
    var pressure_target: Actor = null
    if leader.target_actor != null and not leader.target_actor.is_dead and _is_engagement_state(leader.state):
        pressure_target = leader.target_actor

    return {
        "leader": leader,
        "distance": distance,
        "bonus_active": distance <= 3.6,
        "pressure_target": pressure_target
    }


func _find_nearby_allied_champion(actor: Actor, all_actors: Array, max_distance: float) -> Actor:
    var closest: Actor = null
    var closest_dist_sq: float = max_distance * max_distance
    for other in all_actors:
        if other == null or other == actor or other.is_dead:
            continue
        if other.faction != actor.faction or not other.is_champion:
            continue
        if actor.allegiance_id != "" and other.allegiance_id != "" and other.allegiance_id != actor.allegiance_id:
            continue

        var dist_sq := actor.global_position.distance_squared_to(other.global_position)
        if dist_sq <= closest_dist_sq:
            closest = other
            closest_dist_sq = dist_sq
    return closest


func _is_engagement_state(state: String) -> bool:
    return state in ["detect", "chase", "attack", "cast", "cast_control", "cast_nova", "reposition"]
