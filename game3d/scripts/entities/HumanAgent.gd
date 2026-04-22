extends Actor
class_name HumanAgent


func _init() -> void:
    actor_kind = "adventurer"
    faction = "human"
    _apply_base_human_profile()
    assign_role("fighter")

func assign_role(role: String) -> void:
    _apply_base_human_profile()
    human_role = role if role in ["fighter", "mage", "scout"] else "fighter"

    match human_role:
        "fighter":
            max_hp += 12.0
            speed -= 0.20
            melee_damage += 3.0
            melee_cooldown -= 0.08
            magic_damage -= 1.0
            magic_range -= 0.8
            magic_cooldown += 0.25
            magic_energy_cost += 1.0
            nova_damage += 1.0
            nova_energy_cost -= 1.0
            control_range -= 0.6
            control_duration -= 0.2
            control_slow_multiplier += 0.03
            magic_usage_bias = 0.36
            nova_usage_bias = 0.42
            control_usage_bias = 0.22
        "mage":
            max_hp -= 10.0
            speed -= 0.10
            melee_damage -= 2.0
            melee_cooldown += 0.12
            magic_damage += 2.0
            magic_range += 1.6
            magic_cooldown -= 0.35
            magic_energy_cost -= 1.0
            nova_damage += 2.0
            nova_radius += 0.3
            control_range += 1.2
            control_duration += 0.3
            control_slow_multiplier -= 0.05
            magic_usage_bias = 0.88
            nova_usage_bias = 0.70
            control_usage_bias = 0.56
        "scout":
            max_hp -= 4.0
            speed += 0.40
            melee_damage -= 1.0
            magic_damage -= 0.5
            magic_range += 0.6
            magic_cooldown -= 0.15
            control_range += 1.0
            control_duration += 0.1
            control_slow_multiplier -= 0.04
            control_energy_cost -= 1.0
            energy_drain_rate += 0.15
            magic_usage_bias = 0.50
            nova_usage_bias = 0.28
            control_usage_bias = 0.80

    max_hp = max(80.0, max_hp)
    max_energy = max(90.0, max_energy)
    hp = max_hp
    energy = max_energy


func _apply_base_human_profile() -> void:
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

    magic_usage_bias = 0.58
    nova_usage_bias = 0.44
    control_usage_bias = 0.38

    energy_drain_rate = 2.2
    exhaustion_damage_rate = 6.5
