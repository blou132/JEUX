extends Actor
class_name HumanAgent


func _init() -> void:
    actor_kind = "adventurer"
    faction = "human"

    max_hp = 110.0
    hp = max_hp

    max_energy = 110.0
    energy = max_energy

    speed = 5.2
    vision_range = 20.0
    attack_range = 2.1
    flee_health_ratio = 0.27

    melee_damage = 16.0
    melee_cooldown = 1.0

    magic_enabled = true
    magic_damage = 14.0
    magic_range = 14.0
    magic_cooldown = 3.2
    magic_energy_cost = 12.0

    energy_drain_rate = 2.6
    exhaustion_damage_rate = 7.0
