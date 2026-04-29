extends RefCounted
class_name AgentAI


func decide_action(actor: Actor, world: WorldManager, all_actors: Array) -> Dictionary:
    var rally_context: Dictionary = _build_rally_context(actor, all_actors)
    var rally_leader: Actor = rally_context.get("leader", null)
    var rally_bonus: bool = bool(rally_context.get("bonus_active", false))
    var rally_pressure_target: Actor = rally_context.get("pressure_target", null)
    var rally_leader_kind: String = str(rally_context.get("leader_kind", "champion"))
    var oath_guidance: Dictionary = actor.get_oath_guidance()
    var doctrine_modifiers: Dictionary = world.get_allegiance_doctrine_modifiers(actor.allegiance_id)
    var project_modifiers: Dictionary = world.get_allegiance_project_modifiers(actor.allegiance_id)
    var rally_regroup_chance: float = float(rally_context.get("regroup_chance", 0.66))
    rally_regroup_chance = clampf(
        rally_regroup_chance
        + float(doctrine_modifiers.get("rally_regroup_delta", 0.0))
        + float(project_modifiers.get("rally_regroup_delta", 0.0)),
        0.34,
        0.86
    )
    var rally_pressure_chance: float = clampf(
        0.34
        + float(doctrine_modifiers.get("rally_pressure_delta", 0.0))
        + float(project_modifiers.get("rally_pressure_delta", 0.0)),
        0.20,
        0.55
    )
    var enemy: Actor = world.find_nearest_enemy(actor, all_actors, actor.vision_range)
    if enemy == null:
        if rally_leader != null:
            if rally_pressure_target != null:
                return _with_rally(
                    {
                        "state": "rally",
                        "target": rally_pressure_target,
                        "target_position": rally_pressure_target.global_position,
                        "reason": "rally_renown_pressure" if rally_leader_kind == "renown" else "rally_pressure"
                    },
                    rally_leader,
                    rally_bonus
                )

            var rally_distance: float = float(rally_context.get("distance", INF))
            if rally_distance > actor.attack_range * 1.05 and randf() <= rally_regroup_chance:
                return _with_rally(
                    {
                        "state": "rally",
                        "target_position": rally_leader.global_position,
                        "reason": "rally_renown_regroup" if rally_leader_kind == "renown" else "rally_regroup"
                    },
                    rally_leader,
                    rally_bonus
                )

        if not oath_guidance.is_empty():
            var oath_type: String = str(oath_guidance.get("type", ""))
            var oath_weight: float = clampf(float(oath_guidance.get("weight", 0.56)), 0.20, 0.86)
            if oath_type in ["oath_of_guarding", "oath_of_seeking"] and randf() <= oath_weight:
                var oath_state: String = "poi" if oath_type == "oath_of_guarding" else "hunt"
                var oath_reason: String = "oath:guarding" if oath_type == "oath_of_guarding" else "oath:seeking"
                return _with_rally(
                    {
                        "state": oath_state,
                        "target_position": oath_guidance.get("target_position", actor.global_position),
                        "reason": oath_reason
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

        var bounty_guidance: Dictionary = world.get_bounty_guidance(
            actor.global_position,
            actor.faction,
            actor.allegiance_id,
            actor.home_poi
        )
        if not bounty_guidance.is_empty():
            var bounty_weight: float = float(bounty_guidance.get("weight", 0.58))
            if randf() <= clampf(bounty_weight, 0.24, 0.90):
                return _with_rally(
                    {
                        "state": "hunt",
                        "target_position": bounty_guidance.get("target_position", actor.global_position),
                        "reason": str(bounty_guidance.get("reason", "bounty_hunt"))
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

        var neutral_gate_guidance: Dictionary = world.get_neutral_gate_guidance(actor)
        if not neutral_gate_guidance.is_empty():
            var gate_weight: float = float(neutral_gate_guidance.get("weight", 0.48))
            if randf() <= clampf(gate_weight, 0.22, 0.78):
                return _with_rally(
                    {
                        "state": "poi",
                        "target_position": neutral_gate_guidance.get("target_position", actor.global_position),
                        "reason": str(neutral_gate_guidance.get("reason", "neutral_gate_pull"))
                    },
                    rally_leader,
                    rally_bonus
                )

        var destiny_guidance: Dictionary = actor.get_destiny_guidance()
        if not destiny_guidance.is_empty():
            var destiny_weight: float = float(destiny_guidance.get("weight", 0.56))
            if randf() <= clampf(destiny_weight, 0.22, 0.84):
                var destiny_type: String = str(destiny_guidance.get("type", ""))
                var destiny_state: String = "hunt" if destiny_type in ["relic_call", "vendetta_call"] else "poi"
                return _with_rally(
                    {
                        "state": destiny_state,
                        "target_position": destiny_guidance.get("target_position", actor.global_position),
                        "reason": "destiny:%s" % destiny_type
                    },
                    rally_leader,
                    rally_bonus
                )

        var convergence_guidance: Dictionary = world.get_convergence_guidance(actor)
        if not convergence_guidance.is_empty():
            var convergence_weight: float = float(convergence_guidance.get("weight", 0.42))
            if randf() <= clampf(convergence_weight, 0.18, 0.82):
                return _with_rally(
                    {
                        "state": "poi",
                        "target_position": convergence_guidance.get("target_position", actor.global_position),
                        "reason": str(convergence_guidance.get("reason", "convergence_pull"))
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

    var rivalry_guidance: Dictionary = actor.get_rivalry_guidance()
    if not rivalry_guidance.is_empty():
        var rival_target: Actor = _find_actor_by_id_in_list(
            int(rivalry_guidance.get("target_actor_id", 0)),
            all_actors
        )
        if rival_target != null and not rival_target.is_dead and actor.is_enemy(rival_target):
            var rival_distance: float = actor.global_position.distance_to(rival_target.global_position)
            if rival_distance <= actor.vision_range * 1.12:
                var rival_weight: float = float(rivalry_guidance.get("weight", 0.48))
                if randf() <= clampf(rival_weight, 0.24, 0.88):
                    enemy = rival_target

    if not oath_guidance.is_empty() and str(oath_guidance.get("type", "")) == "oath_of_vengeance":
        var oath_target: Actor = _find_actor_by_id_in_list(
            int(oath_guidance.get("target_actor_id", 0)),
            all_actors
        )
        if oath_target != null and not oath_target.is_dead and actor.is_enemy(oath_target):
            var oath_distance: float = actor.global_position.distance_to(oath_target.global_position)
            var oath_weight: float = clampf(float(oath_guidance.get("weight", 0.56)), 0.22, 0.86)
            if oath_distance <= actor.vision_range * 1.15 and randf() <= oath_weight:
                enemy = oath_target

    if rally_pressure_target != null and rally_pressure_target != enemy:
        var pressure_distance: float = actor.global_position.distance_to(rally_pressure_target.global_position)
        if pressure_distance <= actor.vision_range * 1.08 and randf() <= rally_pressure_chance:
            enemy = rally_pressure_target

    var notoriety_focus_target: Actor = _find_notoriety_focus_enemy(actor, all_actors, actor.vision_range * 1.05)
    if notoriety_focus_target != null and notoriety_focus_target != enemy:
        if _can_prefer_notoriety_target(actor) and randf() <= 0.22:
            enemy = notoriety_focus_target

    var distance: float = actor.global_position.distance_to(enemy.global_position)
    var under_pressure: bool = _is_under_pressure(actor)
    var is_ranged: bool = actor.actor_kind == "ranged_monster"
    var preferred_min_distance: float = actor.attack_range * 1.85

    if _should_avoid_notorious_enemy(actor, enemy, distance) and randf() <= 0.26:
        return _with_rally(
            {
                "state": "flee",
                "target": enemy,
                "reason": "notoriety_avoid"
            },
            rally_leader,
            rally_bonus
        )

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
    if actor.can_lead_rally():
        return {
            "leader": null,
            "distance": INF,
            "bonus_active": false,
            "pressure_target": null,
            "leader_kind": "",
            "regroup_chance": 0.0
        }

    var max_distance := min(actor.vision_range * 0.72, 14.0)
    var leader: Actor = _find_nearby_allied_champion(actor, all_actors, max_distance)
    var leader_kind: String = "champion"
    if leader == null:
        leader = _find_nearby_allied_renown_figure(actor, all_actors, max_distance * 0.94)
        leader_kind = "renown"
    if leader == null:
        return {
            "leader": null,
            "distance": INF,
            "bonus_active": false,
            "pressure_target": null,
            "leader_kind": "",
            "regroup_chance": 0.0
        }

    var distance := actor.global_position.distance_to(leader.global_position)
    var pressure_target: Actor = null
    if leader.target_actor != null and not leader.target_actor.is_dead and _is_engagement_state(leader.state):
        pressure_target = leader.target_actor

    var bonus_distance: float = 3.6 if leader_kind == "champion" else 3.0
    var regroup_chance: float = 0.66 if leader_kind == "champion" else 0.52
    return {
        "leader": leader,
        "distance": distance,
        "bonus_active": distance <= bonus_distance,
        "pressure_target": pressure_target,
        "leader_kind": leader_kind,
        "regroup_chance": regroup_chance
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


func _find_nearby_allied_renown_figure(actor: Actor, all_actors: Array, max_distance: float) -> Actor:
    var closest: Actor = null
    var closest_dist_sq: float = max_distance * max_distance
    for other in all_actors:
        if other == null or other == actor or other.is_dead:
            continue
        if other.faction != actor.faction:
            continue
        if not other.can_lead_rally() or other.is_champion:
            continue
        if actor.allegiance_id != "" and other.allegiance_id != "" and other.allegiance_id != actor.allegiance_id:
            continue

        var dist_sq := actor.global_position.distance_squared_to(other.global_position)
        if dist_sq <= closest_dist_sq:
            closest = other
            closest_dist_sq = dist_sq
    return closest


func _find_notoriety_focus_enemy(actor: Actor, all_actors: Array, max_distance: float) -> Actor:
    var selected: Actor = null
    var best_notoriety: float = 0.0
    var best_dist_sq: float = max_distance * max_distance
    for other in all_actors:
        if other == null or other == actor or other.is_dead:
            continue
        if not actor.is_enemy(other):
            continue
        if other.notoriety < 38.0:
            continue

        var dist_sq := actor.global_position.distance_squared_to(other.global_position)
        if dist_sq > max_distance * max_distance:
            continue
        if other.notoriety > best_notoriety or (is_equal_approx(other.notoriety, best_notoriety) and dist_sq < best_dist_sq):
            selected = other
            best_notoriety = other.notoriety
            best_dist_sq = dist_sq
    return selected


func _can_prefer_notoriety_target(actor: Actor) -> bool:
    if actor == null:
        return false
    if actor.is_champion or actor.actor_kind == "brute_monster":
        return true
    return actor.has_relic() or actor.is_special_arrival()


func _should_avoid_notorious_enemy(actor: Actor, enemy: Actor, distance: float) -> bool:
    if actor == null or enemy == null:
        return false
    if enemy.notoriety < 56.0:
        return false
    if actor.is_champion or actor.actor_kind == "brute_monster" or actor.has_relic() or actor.is_special_arrival():
        return false
    if distance > actor.vision_range * 0.70:
        return false
    return actor.hp <= actor.max_hp * 0.82 or actor.energy <= actor.max_energy * 0.55


func _is_engagement_state(state: String) -> bool:
    return state in ["detect", "chase", "attack", "cast", "cast_control", "cast_nova", "reposition"]


func _find_actor_by_id_in_list(actor_id: int, all_actors: Array) -> Actor:
    if actor_id == 0:
        return null
    for other in all_actors:
        if other == null:
            continue
        if other.actor_id == actor_id:
            return other
    return null
