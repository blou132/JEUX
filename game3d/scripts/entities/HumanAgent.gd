extends Actor
class_name HumanAgent


func _init() -> void:
    actor_kind = "adventurer"
    faction = "human"

    max_hp = 126.0
    hp = max_hp

    max_energy = 118.0
    energy = max_energy

    speed = 5.0
    vision_range = 20.0
    attack_range = 2.0
    flee_health_ratio = 0.27

    melee_damage = 14.0
    melee_cooldown = 1.12

    magic_enabled = true
    magic_damage = 12.0
    magic_range = 13.0
    magic_cooldown = 3.4
    magic_energy_cost = 14.0
    nova_enabled = true
    nova_damage = 18.0
    nova_radius = 3.5
    nova_energy_cost = 22.0

    energy_drain_rate = 2.2
    exhaustion_damage_rate = 6.5
