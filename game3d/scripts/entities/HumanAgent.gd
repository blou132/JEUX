extends Actor
class_name HumanAgent


func _init() -> void:
    actor_kind = "adventurer"
    faction = "human"

    max_hp = 132.0
    hp = max_hp

    max_energy = 122.0
    energy = max_energy

    speed = 4.9
    vision_range = 20.0
    attack_range = 2.0
    flee_health_ratio = 0.27

    melee_damage = 13.0
    melee_cooldown = 1.18

    magic_enabled = true
    magic_damage = 11.0
    magic_range = 13.0
    magic_cooldown = 3.6
    magic_energy_cost = 15.0
    nova_enabled = true
    nova_damage = 17.0
    nova_radius = 3.5
    nova_energy_cost = 24.0
    control_enabled = true
    control_range = 11.0
    control_duration = 1.9
    control_slow_multiplier = 0.66
    control_energy_cost = 12.0

    energy_drain_rate = 2.2
    exhaustion_damage_rate = 6.5
