extends Actor
class_name RangedMonster


func _init() -> void:
    actor_kind = "ranged_monster"
    faction = "monster"

    max_hp = 114.0
    hp = max_hp

    max_energy = 122.0
    energy = max_energy

    speed = 4.8
    vision_range = 21.0
    attack_range = 1.6
    flee_health_ratio = 0.26

    melee_damage = 8.0
    melee_cooldown = 1.35

    magic_enabled = true
    magic_damage = 10.0
    magic_range = 16.0
    magic_cooldown = 3.0
    magic_energy_cost = 12.0
    magic_usage_bias = 0.92

    nova_enabled = false
    nova_damage = 0.0
    nova_radius = 0.0
    nova_energy_cost = 0.0

    energy_drain_rate = 2.3
    exhaustion_damage_rate = 6.4
