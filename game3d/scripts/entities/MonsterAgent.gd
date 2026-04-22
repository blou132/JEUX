extends Actor
class_name MonsterAgent


func _init() -> void:
    actor_kind = "monster"
    faction = "monster"

    max_hp = 142.0
    hp = max_hp

    max_energy = 100.0
    energy = max_energy

    speed = 4.4
    vision_range = 18.0
    attack_range = 2.0
    flee_health_ratio = 0.18

    melee_damage = 16.0
    melee_cooldown = 1.32

    magic_enabled = false
    magic_damage = 0.0
    magic_range = 0.0
    magic_cooldown = 0.0
    magic_energy_cost = 0.0

    energy_drain_rate = 2.0
    exhaustion_damage_rate = 6.0
