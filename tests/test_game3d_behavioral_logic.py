from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


@dataclass
class EnemyStub:
    actor_kind: str = "monster"
    position: tuple[float, float] = (0.0, 0.0)
    slowed: bool = False

    def is_slowed(self) -> bool:
        return self.slowed


@dataclass
class ActorStub:
    actor_kind: str = "adventurer"
    faction: str = "human"
    position: tuple[float, float] = (0.0, 0.0)
    vision_range: float = 20.0
    attack_range: float = 2.0
    magic_range: float = 13.0
    control_range: float = 11.0
    nova_radius: float = 3.5
    hp: float = 120.0
    max_hp: float = 130.0
    flee_health_ratio: float = 0.27
    energy: float = 100.0
    max_energy: float = 120.0
    can_magic: bool = True
    can_nova: bool = False
    can_control: bool = False
    magic_usage_bias: float = 1.0
    nova_usage_bias: float = 1.0
    control_usage_bias: float = 1.0

    def can_cast_magic(self) -> bool:
        return self.can_magic

    def can_cast_nova(self) -> bool:
        return self.can_nova

    def can_cast_control(self) -> bool:
        return self.can_control


class WorldStub:
    def __init__(self, enemy: EnemyStub | None, poi_guidance: dict | None = None):
        self.enemy = enemy
        self.poi_guidance = poi_guidance or {}

    def find_nearest_enemy(self, _source, _all, _max_distance):
        return self.enemy

    def get_poi_guidance(self, _position, _faction):
        return self.poi_guidance


def decide_action_contract(actor: ActorStub, world: WorldStub, random_roll: float, spell_roll: float = 0.0) -> dict:
    enemy = world.find_nearest_enemy(actor, [], actor.vision_range)
    if enemy is None:
        guidance = world.get_poi_guidance(actor.position, actor.faction)
        if guidance and random_roll <= 0.58:
            return {
                "state": "poi",
                "target_position": guidance.get("target_position", actor.position),
                "reason": f"poi_guidance:{guidance.get('name', 'poi')}",
            }
        return {"state": "wander", "reason": "no_enemy_visible"}

    distance = math.dist(actor.position, enemy.position)
    under_pressure = (
        actor.hp <= actor.max_hp * actor.flee_health_ratio
        or actor.energy <= actor.max_energy * 0.20
    )
    is_ranged = actor.actor_kind == "ranged_monster"
    preferred_min_distance = actor.attack_range * 1.85

    if is_ranged and distance < preferred_min_distance and not under_pressure:
        return {"state": "reposition", "target": enemy, "reason": "ranged_keep_distance"}

    if under_pressure and distance <= actor.vision_range * 0.9:
        return {"state": "flee", "target": enemy, "reason": "pressure_and_threat"}

    if (
        actor.can_cast_control()
        and distance <= actor.control_range
        and distance > actor.attack_range * 1.12
        and not enemy.is_slowed()
    ):
        if enemy.actor_kind in ["brute_monster", "ranged_monster"] or distance <= actor.control_range * 0.78:
            if spell_roll <= actor.control_usage_bias:
                return {"state": "cast_control", "target": enemy, "reason": "control_window"}

    if actor.can_cast_nova() and distance <= actor.nova_radius * 0.95:
        if spell_roll <= actor.nova_usage_bias:
            return {"state": "cast_nova", "target": enemy, "reason": "nova_range"}

    if actor.can_cast_magic() and distance <= actor.magic_range and distance > actor.attack_range * 1.2:
        if spell_roll <= actor.magic_usage_bias:
            return {"state": "cast", "target": enemy, "reason": "ranged_cast" if is_ranged else "magic_range"}

    if distance <= actor.attack_range:
        return {"state": "attack", "target": enemy, "reason": "melee_range"}

    if distance > actor.vision_range * 0.55:
        if actor.actor_kind == "brute_monster":
            return {"state": "chase", "target": enemy, "reason": "brute_commit"}
        if is_ranged and distance <= actor.magic_range * 1.08:
            return {"state": "detect", "target": enemy, "reason": "ranged_hold_line"}
        return {"state": "detect", "target": enemy, "reason": "enemy_detected_far"}

    if is_ranged and distance > actor.attack_range * 1.15 and actor.can_cast_magic():
        if spell_roll <= actor.magic_usage_bias:
            return {"state": "cast", "target": enemy, "reason": "ranged_pressure_cast"}

    return {
        "state": "chase",
        "target": enemy,
        "reason": "ranged_reposition_chase" if is_ranged else "enemy_detected_near",
    }


def poi_runtime_contract(occupancy: dict, previous_status: dict | None = None) -> dict:
    previous_status = previous_status or {}
    snapshot = {}
    events = []
    next_status = dict(previous_status)

    for poi_name, values in occupancy.items():
        h = int(values.get("human", 0))
        m = int(values.get("monster", 0))
        total = h + m
        if h == 0 and m == 0:
            status = "calm"
        elif h > 0 and m > 0:
            status = "contested"
        elif h > 0:
            status = "human_dominant"
        else:
            status = "monster_dominant"

        if total <= 1:
            activity = "low"
        elif total <= 4:
            activity = "medium"
        else:
            activity = "high"

        snapshot[poi_name] = {
            "human": h,
            "monster": m,
            "total": total,
            "status": status,
            "activity": activity,
        }

        prev = previous_status.get(poi_name, "")
        if prev and prev != status:
            if status == "contested":
                events.append({"kind": "contest_started", "poi": poi_name, "from": prev, "to": status})
            elif status in ["human_dominant", "monster_dominant"]:
                events.append({"kind": "domination_changed", "poi": poi_name, "from": prev, "to": status})
            elif prev == "contested" and status == "calm":
                events.append({"kind": "contest_resolved", "poi": poi_name, "from": prev, "to": status})

        next_status[poi_name] = status

    return {"snapshot": snapshot, "events": events, "next_status": next_status}


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def spawn_kind_contract(roll: float, brute_ratio: float, ranged_ratio: float) -> str:
    brute = clamp01(brute_ratio)
    ranged = max(0.0, min(ranged_ratio, 1.0 - brute))
    if roll < brute:
        return "brute_monster"
    if roll < brute + ranged:
        return "ranged_monster"
    return "monster"


def pick_human_role_contract(roll: float, fighter_ratio: float, mage_ratio: float, scout_ratio: float) -> str:
    fighter = clamp01(fighter_ratio)
    mage = max(0.0, min(mage_ratio, 1.0 - fighter))
    scout = max(0.0, min(scout_ratio, 1.0 - fighter - mage))
    remainder = max(0.0, 1.0 - (fighter + mage + scout))
    fighter += remainder
    if roll < fighter:
        return "fighter"
    if roll < fighter + mage:
        return "mage"
    return "scout"


class TestGame3DBehavioralLogic(unittest.TestCase):
    def test_ai_decides_poi_when_no_enemy_and_guidance(self):
        actor = ActorStub()
        world = WorldStub(enemy=None, poi_guidance={"name": "camp", "target_position": (4.0, -3.0)})
        decision = decide_action_contract(actor, world, random_roll=0.30)
        self.assertEqual(decision["state"], "poi")
        self.assertIn("poi_guidance", decision["reason"])

    def test_ai_decides_cast_nova_in_valid_range(self):
        actor = ActorStub(can_nova=True, can_magic=False, can_control=False, nova_radius=4.0, nova_usage_bias=0.9)
        enemy = EnemyStub(position=(3.0, 0.0))
        world = WorldStub(enemy=enemy)
        decision = decide_action_contract(actor, world, random_roll=0.99, spell_roll=0.2)
        self.assertEqual(decision["state"], "cast_nova")

    def test_ai_decides_reposition_for_ranged_when_too_close(self):
        actor = ActorStub(actor_kind="ranged_monster", attack_range=1.6, can_magic=True, can_control=False, magic_usage_bias=0.9)
        enemy = EnemyStub(position=(2.2, 0.0))
        world = WorldStub(enemy=enemy)
        decision = decide_action_contract(actor, world, random_roll=0.99, spell_roll=0.2)
        self.assertEqual(decision["state"], "reposition")
        self.assertEqual(decision["reason"], "ranged_keep_distance")

    def test_ai_decides_cast_control_when_window_is_good(self):
        actor = ActorStub(
            can_control=True,
            can_nova=False,
            can_magic=False,
            attack_range=2.0,
            control_range=11.0,
            control_usage_bias=0.9,
        )
        enemy = EnemyStub(actor_kind="brute_monster", position=(6.5, 0.0), slowed=False)
        world = WorldStub(enemy=enemy)
        decision = decide_action_contract(actor, world, random_roll=0.99, spell_roll=0.2)
        self.assertEqual(decision["state"], "cast_control")
        self.assertEqual(decision["reason"], "control_window")

    def test_poi_runtime_snapshot_and_transition_structure(self):
        prev = {"camp": "human_dominant"}
        runtime = poi_runtime_contract(
            {"camp": {"human": 2, "monster": 2}, "ruins": {"human": 0, "monster": 0}},
            previous_status=prev,
        )
        camp = runtime["snapshot"]["camp"]
        ruins = runtime["snapshot"]["ruins"]

        self.assertEqual(camp["status"], "contested")
        self.assertEqual(camp["activity"], "medium")
        self.assertEqual(camp["total"], 4)
        self.assertEqual(ruins["status"], "calm")
        self.assertIn("kind", runtime["events"][0])
        self.assertEqual(runtime["events"][0]["kind"], "contest_started")

    def test_spawn_contract_covers_standard_brute_ranged(self):
        content = (GAME3D / "scripts" / "sandbox" / "SandboxSystems.gd").read_text(encoding="utf-8")
        brute_ratio = float(re.search(r"brute_spawn_ratio: float = ([0-9.]+)", content).group(1))
        ranged_ratio = float(re.search(r"ranged_spawn_ratio: float = ([0-9.]+)", content).group(1))

        kinds = {
            spawn_kind_contract(0.00, brute_ratio, ranged_ratio),
            spawn_kind_contract(min(0.999, brute_ratio + 0.01), brute_ratio, ranged_ratio),
            spawn_kind_contract(0.999, brute_ratio, ranged_ratio),
        }

        self.assertIn("brute_monster", kinds)
        self.assertIn("ranged_monster", kinds)
        self.assertIn("monster", kinds)
        self.assertLessEqual(brute_ratio + ranged_ratio, 1.0)

    def test_human_role_pick_contract_covers_three_roles(self):
        content = (GAME3D / "scripts" / "sandbox" / "SandboxSystems.gd").read_text(encoding="utf-8")
        fighter = float(re.search(r"fighter_role_ratio: float = ([0-9.]+)", content).group(1))
        mage = float(re.search(r"mage_role_ratio: float = ([0-9.]+)", content).group(1))
        scout = float(re.search(r"scout_role_ratio: float = ([0-9.]+)", content).group(1))

        roles = {
            pick_human_role_contract(0.00, fighter, mage, scout),
            pick_human_role_contract(min(0.999, fighter + 0.01), fighter, mage, scout),
            pick_human_role_contract(0.999, fighter, mage, scout),
        }
        self.assertIn("fighter", roles)
        self.assertIn("mage", roles)
        self.assertIn("scout", roles)


if __name__ == "__main__":
    unittest.main()
