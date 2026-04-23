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
    faction: str = "monster"
    actor_id: int = 999
    position: tuple[float, float] = (0.0, 0.0)
    slowed: bool = False
    is_dead: bool = False

    def is_slowed(self) -> bool:
        return self.slowed


@dataclass
class ActorStub:
    actor_id: int = 1
    actor_kind: str = "adventurer"
    faction: str = "human"
    position: tuple[float, float] = (0.0, 0.0)
    is_dead: bool = False
    is_champion: bool = False
    state: str = "wander"
    target_actor: EnemyStub | None = None
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


def decide_action_contract(
    actor: ActorStub,
    world: WorldStub,
    random_roll: float,
    spell_roll: float = 0.0,
    all_actors: list[ActorStub] | None = None,
) -> dict:
    all_actors = all_actors or []
    rally = _build_rally_context_contract(actor, all_actors)
    rally_leader = rally["leader"]
    rally_bonus = rally["bonus_active"]
    rally_pressure_target = rally["pressure_target"]

    enemy = world.find_nearest_enemy(actor, all_actors, actor.vision_range)
    if enemy is None:
        if rally_leader is not None:
            if rally_pressure_target is not None:
                return _with_rally_contract(
                    {
                        "state": "rally",
                        "target": rally_pressure_target,
                        "target_position": rally_pressure_target.position,
                        "reason": "rally_pressure",
                    },
                    rally_leader,
                    rally_bonus,
                )
            if rally["distance"] > actor.attack_range * 1.05 and random_roll <= 0.66:
                return _with_rally_contract(
                    {
                        "state": "rally",
                        "target_position": rally_leader.position,
                        "reason": "rally_regroup",
                    },
                    rally_leader,
                    rally_bonus,
                )

        guidance = world.get_poi_guidance(actor.position, actor.faction)
        if guidance and random_roll <= 0.58:
            return _with_rally_contract(
                {
                    "state": "poi",
                    "target_position": guidance.get("target_position", actor.position),
                    "reason": f"poi_guidance:{guidance.get('name', 'poi')}",
                },
                rally_leader,
                rally_bonus,
            )
        return _with_rally_contract({"state": "wander", "reason": "no_enemy_visible"}, rally_leader, rally_bonus)

    if (
        rally_pressure_target is not None
        and rally_pressure_target is not enemy
        and math.dist(actor.position, rally_pressure_target.position) <= actor.vision_range * 1.08
        and random_roll <= 0.34
    ):
        enemy = rally_pressure_target

    distance = math.dist(actor.position, enemy.position)
    under_pressure = (
        actor.hp <= actor.max_hp * actor.flee_health_ratio
        or actor.energy <= actor.max_energy * 0.20
    )
    is_ranged = actor.actor_kind == "ranged_monster"
    preferred_min_distance = actor.attack_range * 1.85

    if is_ranged and distance < preferred_min_distance and not under_pressure:
        return _with_rally_contract(
            {"state": "reposition", "target": enemy, "reason": "ranged_keep_distance"},
            rally_leader,
            rally_bonus,
        )

    if under_pressure and distance <= actor.vision_range * 0.9:
        return _with_rally_contract(
            {"state": "flee", "target": enemy, "reason": "pressure_and_threat"},
            rally_leader,
            rally_bonus,
        )

    if (
        actor.can_cast_control()
        and distance <= actor.control_range
        and distance > actor.attack_range * 1.12
        and not enemy.is_slowed()
    ):
        if enemy.actor_kind in ["brute_monster", "ranged_monster"] or distance <= actor.control_range * 0.78:
            if spell_roll <= actor.control_usage_bias:
                return _with_rally_contract(
                    {"state": "cast_control", "target": enemy, "reason": "control_window"},
                    rally_leader,
                    rally_bonus,
                )

    if actor.can_cast_nova() and distance <= actor.nova_radius * 0.95:
        if spell_roll <= actor.nova_usage_bias:
            return _with_rally_contract(
                {"state": "cast_nova", "target": enemy, "reason": "nova_range"},
                rally_leader,
                rally_bonus,
            )

    if actor.can_cast_magic() and distance <= actor.magic_range and distance > actor.attack_range * 1.2:
        if spell_roll <= actor.magic_usage_bias:
            return _with_rally_contract(
                {"state": "cast", "target": enemy, "reason": "ranged_cast" if is_ranged else "magic_range"},
                rally_leader,
                rally_bonus,
            )

    if distance <= actor.attack_range:
        return _with_rally_contract(
            {"state": "attack", "target": enemy, "reason": "melee_range"},
            rally_leader,
            rally_bonus,
        )

    if distance > actor.vision_range * 0.55:
        if actor.actor_kind == "brute_monster":
            return _with_rally_contract(
                {"state": "chase", "target": enemy, "reason": "brute_commit"},
                rally_leader,
                rally_bonus,
            )
        if is_ranged and distance <= actor.magic_range * 1.08:
            return _with_rally_contract(
                {"state": "detect", "target": enemy, "reason": "ranged_hold_line"},
                rally_leader,
                rally_bonus,
            )
        return _with_rally_contract(
            {"state": "detect", "target": enemy, "reason": "enemy_detected_far"},
            rally_leader,
            rally_bonus,
        )

    if is_ranged and distance > actor.attack_range * 1.15 and actor.can_cast_magic():
        if spell_roll <= actor.magic_usage_bias:
            return _with_rally_contract(
                {"state": "cast", "target": enemy, "reason": "ranged_pressure_cast"},
                rally_leader,
                rally_bonus,
            )

    return _with_rally_contract(
        {
            "state": "chase",
            "target": enemy,
            "reason": "ranged_reposition_chase" if is_ranged else "enemy_detected_near",
        },
        rally_leader,
        rally_bonus,
    )


def _with_rally_contract(base_decision: dict, rally_leader: ActorStub | None, rally_bonus: bool) -> dict:
    decision = dict(base_decision)
    if rally_leader is not None and not rally_leader.is_dead:
        decision["rally_leader"] = rally_leader
        decision["rally_bonus"] = rally_bonus
    return decision


def _build_rally_context_contract(actor: ActorStub, all_actors: list[ActorStub]) -> dict:
    if actor.is_champion:
        return {"leader": None, "distance": math.inf, "bonus_active": False, "pressure_target": None}

    max_distance = min(actor.vision_range * 0.72, 14.0)
    leader = _find_nearby_allied_champion_contract(actor, all_actors, max_distance)
    if leader is None:
        return {"leader": None, "distance": math.inf, "bonus_active": False, "pressure_target": None}

    distance = math.dist(actor.position, leader.position)
    pressure_target = None
    if (
        leader.target_actor is not None
        and not leader.target_actor.is_dead
        and leader.state in {"detect", "chase", "attack", "cast", "cast_control", "cast_nova", "reposition"}
    ):
        pressure_target = leader.target_actor

    return {
        "leader": leader,
        "distance": distance,
        "bonus_active": distance <= 3.6,
        "pressure_target": pressure_target,
    }


def _find_nearby_allied_champion_contract(actor: ActorStub, all_actors: list[ActorStub], max_distance: float) -> ActorStub | None:
    closest = None
    best_dist = max_distance
    for other in all_actors:
        if other is actor:
            continue
        if other.is_dead or not other.is_champion:
            continue
        if other.faction != actor.faction:
            continue
        dist = math.dist(actor.position, other.position)
        if dist <= best_dist:
            closest = other
            best_dist = dist
    return closest


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


def poi_influence_step_contract(
    previous_status: str,
    previous_active: bool,
    previous_dominant: str,
    dominant_started_at: float,
    current_status: str,
    now: float,
    poi_kind: str,
    activation_time: float = 8.0,
) -> dict:
    dominant = ""
    if current_status == "human_dominant":
        dominant = "human"
    elif current_status == "monster_dominant":
        dominant = "monster"

    if dominant == "":
        dominance_seconds = 0.0
        dominant_started_at = now
    elif dominant != previous_dominant:
        dominance_seconds = 0.0
        dominant_started_at = now
    else:
        dominance_seconds = max(0.0, now - dominant_started_at)

    influence_kind = ""
    if dominance_seconds >= activation_time:
        if poi_kind == "camp" and dominant == "human":
            influence_kind = "human_camp_influence"
        elif poi_kind == "ruins" and dominant == "monster":
            influence_kind = "monster_ruins_influence"

    active = influence_kind != ""
    events: list[str] = []
    if previous_status != "" and previous_status != current_status:
        if current_status == "contested":
            events.append("contest_started")
        elif current_status in ["human_dominant", "monster_dominant"]:
            events.append("domination_changed")
    if previous_active != active:
        events.append("influence_activated" if active else "influence_deactivated")

    return {
        "dominant": dominant,
        "dominance_seconds": dominance_seconds,
        "active": active,
        "influence_kind": influence_kind,
        "dominant_started_at": dominant_started_at,
        "events": events,
    }


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


def champion_promotion_contract(
    *,
    is_champion: bool,
    level: int,
    kills: int,
    age_seconds: float,
    progress_xp: float,
    alive_total: int,
    champions_alive: int,
    min_level: int = 3,
    min_kills: int = 2,
    min_age_seconds: float = 26.0,
    min_progress_xp: float = 42.0,
    max_ratio: float = 0.16,
    min_population: int = 8,
) -> bool:
    if is_champion:
        return False
    if level < min_level or kills < min_kills:
        return False
    if age_seconds < min_age_seconds or progress_xp < min_progress_xp:
        return False
    if alive_total < min_population:
        return False
    champion_cap = max(1, int(math.floor(alive_total * max_ratio)))
    return champions_alive < champion_cap


class TestGame3DBehavioralLogic(unittest.TestCase):
    def test_ai_decides_rally_when_nearby_champion_exists(self):
        actor = ActorStub(actor_id=1, faction="human", position=(0.0, 0.0), attack_range=2.0)
        champion = ActorStub(
            actor_id=2,
            faction="human",
            position=(7.0, 0.0),
            is_champion=True,
            state="wander",
        )
        world = WorldStub(enemy=None, poi_guidance={})
        decision = decide_action_contract(actor, world, random_roll=0.20, all_actors=[actor, champion])
        self.assertEqual(decision["state"], "rally")
        self.assertEqual(decision["reason"], "rally_regroup")
        self.assertEqual(decision["rally_leader"].actor_id, 2)

    def test_ai_decides_rally_pressure_when_leader_is_engaged(self):
        actor = ActorStub(actor_id=10, faction="monster", position=(1.0, 0.0), attack_range=1.8)
        target = EnemyStub(actor_kind="adventurer", faction="human", actor_id=70, position=(9.0, 0.0))
        champion = ActorStub(
            actor_id=11,
            actor_kind="brute_monster",
            faction="monster",
            position=(3.0, 0.0),
            is_champion=True,
            state="chase",
            target_actor=target,
        )
        world = WorldStub(enemy=None, poi_guidance={})
        decision = decide_action_contract(actor, world, random_roll=0.90, all_actors=[actor, champion])
        self.assertEqual(decision["state"], "rally")
        self.assertEqual(decision["reason"], "rally_pressure")
        self.assertIs(decision["target"], target)

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

    def test_poi_influence_activates_after_stable_domination(self):
        step_1 = poi_influence_step_contract(
            previous_status="",
            previous_active=False,
            previous_dominant="",
            dominant_started_at=0.0,
            current_status="human_dominant",
            now=1.0,
            poi_kind="camp",
            activation_time=8.0,
        )
        self.assertFalse(step_1["active"])

        step_2 = poi_influence_step_contract(
            previous_status="human_dominant",
            previous_active=False,
            previous_dominant=step_1["dominant"],
            dominant_started_at=step_1["dominant_started_at"],
            current_status="human_dominant",
            now=10.5,
            poi_kind="camp",
            activation_time=8.0,
        )
        self.assertTrue(step_2["active"])
        self.assertEqual(step_2["influence_kind"], "human_camp_influence")
        self.assertIn("influence_activated", step_2["events"])

    def test_poi_influence_deactivates_when_contested(self):
        step = poi_influence_step_contract(
            previous_status="human_dominant",
            previous_active=True,
            previous_dominant="human",
            dominant_started_at=0.0,
            current_status="contested",
            now=12.0,
            poi_kind="camp",
            activation_time=8.0,
        )
        self.assertFalse(step["active"])
        self.assertIn("influence_deactivated", step["events"])
        self.assertIn("contest_started", step["events"])

    def test_camp_does_not_activate_monster_influence(self):
        step = poi_influence_step_contract(
            previous_status="monster_dominant",
            previous_active=False,
            previous_dominant="monster",
            dominant_started_at=0.0,
            current_status="monster_dominant",
            now=15.0,
            poi_kind="camp",
            activation_time=8.0,
        )
        self.assertFalse(step["active"])
        self.assertEqual(step["influence_kind"], "")

    def test_ruins_activates_monster_influence(self):
        step = poi_influence_step_contract(
            previous_status="monster_dominant",
            previous_active=False,
            previous_dominant="monster",
            dominant_started_at=0.0,
            current_status="monster_dominant",
            now=11.0,
            poi_kind="ruins",
            activation_time=8.0,
        )
        self.assertTrue(step["active"])
        self.assertEqual(step["influence_kind"], "monster_ruins_influence")

    def test_champion_promotion_requires_notable_actor_profile(self):
        self.assertFalse(
            champion_promotion_contract(
                is_champion=False,
                level=2,
                kills=3,
                age_seconds=60.0,
                progress_xp=70.0,
                alive_total=20,
                champions_alive=1,
            )
        )
        self.assertFalse(
            champion_promotion_contract(
                is_champion=False,
                level=3,
                kills=1,
                age_seconds=60.0,
                progress_xp=70.0,
                alive_total=20,
                champions_alive=1,
            )
        )
        self.assertTrue(
            champion_promotion_contract(
                is_champion=False,
                level=3,
                kills=3,
                age_seconds=42.0,
                progress_xp=56.0,
                alive_total=20,
                champions_alive=1,
            )
        )

    def test_champion_promotion_respects_population_cap(self):
        # For alive_total=20 and max_ratio=0.16, cap = floor(3.2) => 3.
        self.assertTrue(
            champion_promotion_contract(
                is_champion=False,
                level=3,
                kills=4,
                age_seconds=50.0,
                progress_xp=80.0,
                alive_total=20,
                champions_alive=2,
            )
        )
        self.assertFalse(
            champion_promotion_contract(
                is_champion=False,
                level=3,
                kills=4,
                age_seconds=50.0,
                progress_xp=80.0,
                alive_total=20,
                champions_alive=3,
            )
        )

    def test_champion_promotion_blocked_when_population_too_low(self):
        self.assertFalse(
            champion_promotion_contract(
                is_champion=False,
                level=3,
                kills=3,
                age_seconds=35.0,
                progress_xp=50.0,
                alive_total=6,
                champions_alive=0,
            )
        )


if __name__ == "__main__":
    unittest.main()
