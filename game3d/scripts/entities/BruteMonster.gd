extends Actor
class_name BruteMonster


func _init() -> void:
    actor_kind = "brute_monster"
    faction = "monster"

    max_hp = 190.0
    hp = max_hp

    max_energy = 110.0
    energy = max_energy

    speed = 3.8
    vision_range = 17.0
    attack_range = 2.3
    flee_health_ratio = 0.10

    melee_damage = 24.0
    melee_cooldown = 1.45

    magic_enabled = false
    nova_enabled = false

    energy_drain_rate = 1.9
    exhaustion_damage_rate = 6.5
