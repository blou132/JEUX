extends Node
class_name CombatSystem


func try_melee(attacker: Actor, target: Actor, game_loop: GameLoop) -> bool:
    if attacker == null or target == null:
        return false
    if attacker.is_dead or target.is_dead:
        return false
    if not attacker.is_enemy(target):
        return false
    if attacker.melee_cooldown_left > 0.0:
        return false

    var distance: float = attacker.global_position.distance_to(target.global_position)
    if distance > attacker.attack_range:
        return false

    attacker.melee_cooldown_left = attacker.melee_cooldown
    var damage: float = attacker.melee_damage * game_loop.get_melee_damage_multiplier(attacker)
    target.apply_damage(damage, attacker, "melee")

    game_loop.register_attack("melee", attacker, target, damage)
    if target.is_dead:
        game_loop.register_death(target, attacker, "melee")

    return true
