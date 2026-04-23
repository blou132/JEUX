from __future__ import annotations

from pathlib import Path
import math
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def apply_notability_gain_contract(value: float, amount: float, cap: float = 100.0) -> float:
    if amount <= 0.0:
        return max(0.0, min(cap, value))
    return max(0.0, min(cap, value + amount))


def notability_tier_contract(value: float, thresholds: list[float]) -> int:
    tier = 0
    for threshold in thresholds:
        if value >= threshold:
            tier += 1
    return tier


def decay_notability_contract(
    *,
    renown: float,
    notoriety: float,
    delta: float,
    renown_decay_per_sec: float = 0.16,
    notoriety_decay_per_sec: float = 0.14,
    is_champion: bool = False,
    is_special_arrival: bool = False,
    has_relic: bool = False,
    bounty_marked: bool = False,
) -> tuple[float, float]:
    damping = 1.0
    if is_champion:
        damping *= 0.72
    if is_special_arrival:
        damping *= 0.68
    if has_relic:
        damping *= 0.74
    if bounty_marked:
        damping *= 0.58

    next_renown = max(0.0, renown - renown_decay_per_sec * damping * max(0.0, delta))
    next_notoriety = max(0.0, notoriety - notoriety_decay_per_sec * damping * max(0.0, delta))
    return next_renown, next_notoriety


def pick_rally_leader_contract(
    *,
    actor_faction: str,
    actor_allegiance_id: str,
    actor_position: tuple[float, float],
    candidates: list[dict],
    max_distance: float,
) -> dict | None:
    best_champion = None
    best_champion_dist = max_distance
    for cand in candidates:
        if cand.get("faction") != actor_faction:
            continue
        if bool(cand.get("is_dead", False)):
            continue
        if not bool(cand.get("is_champion", False)):
            continue
        if actor_allegiance_id and cand.get("allegiance_id") and cand.get("allegiance_id") != actor_allegiance_id:
            continue
        dist = math.dist(actor_position, cand.get("position", (0.0, 0.0)))
        if dist <= best_champion_dist:
            best_champion = cand
            best_champion_dist = dist
    if best_champion is not None:
        return best_champion

    best_renown = None
    best_renown_dist = max_distance * 0.94
    for cand in candidates:
        if cand.get("faction") != actor_faction:
            continue
        if bool(cand.get("is_dead", False)):
            continue
        if bool(cand.get("is_champion", False)):
            continue
        if actor_allegiance_id and cand.get("allegiance_id") and cand.get("allegiance_id") != actor_allegiance_id:
            continue
        can_lead = bool(cand.get("is_special_arrival", False)) or bool(cand.get("has_relic", False)) or float(cand.get("renown", 0.0)) >= 28.0
        if not can_lead:
            continue
        dist = math.dist(actor_position, cand.get("position", (0.0, 0.0)))
        if dist <= best_renown_dist:
            best_renown = cand
            best_renown_dist = dist
    return best_renown


def should_avoid_notorious_enemy_contract(
    *,
    actor_is_champion: bool,
    actor_kind: str,
    actor_has_relic: bool,
    actor_is_special_arrival: bool,
    actor_hp: float,
    actor_max_hp: float,
    actor_energy: float,
    actor_max_energy: float,
    vision_range: float,
    distance: float,
    enemy_notoriety: float,
) -> bool:
    if enemy_notoriety < 56.0:
        return False
    if actor_is_champion or actor_kind == "brute_monster" or actor_has_relic or actor_is_special_arrival:
        return False
    if distance > vision_range * 0.70:
        return False
    return actor_hp <= actor_max_hp * 0.82 or actor_energy <= actor_max_energy * 0.55


class TestGame3DRenownBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    def test_gain_is_bounded_for_renown_and_notoriety(self):
        self.assertEqual(apply_notability_gain_contract(98.0, 10.0), 100.0)
        self.assertEqual(apply_notability_gain_contract(0.0, -5.0), 0.0)
        self.assertEqual(apply_notability_gain_contract(22.0, 3.0), 25.0)

    def test_threshold_tier_contract_is_stable(self):
        thresholds = [20.0, 45.0, 70.0]
        self.assertEqual(notability_tier_contract(19.9, thresholds), 0)
        self.assertEqual(notability_tier_contract(20.0, thresholds), 1)
        self.assertEqual(notability_tier_contract(45.0, thresholds), 2)
        self.assertEqual(notability_tier_contract(85.0, thresholds), 3)

    def test_decay_contract_is_light_and_non_negative(self):
        next_renown, next_notoriety = decay_notability_contract(
            renown=40.0,
            notoriety=35.0,
            delta=15.0,
            is_champion=False,
            is_special_arrival=False,
            has_relic=False,
            bounty_marked=False,
        )
        self.assertLess(next_renown, 40.0)
        self.assertLess(next_notoriety, 35.0)
        self.assertGreaterEqual(next_renown, 0.0)
        self.assertGreaterEqual(next_notoriety, 0.0)

        protected_renown, protected_notoriety = decay_notability_contract(
            renown=40.0,
            notoriety=35.0,
            delta=15.0,
            is_champion=True,
            has_relic=True,
        )
        self.assertGreater(protected_renown, next_renown)
        self.assertGreater(protected_notoriety, next_notoriety)

    def test_rally_prefers_champion_then_renown_figure(self):
        champion = {
            "faction": "human",
            "allegiance_id": "human:camp",
            "position": (6.0, 0.0),
            "is_champion": True,
            "renown": 20.0,
        }
        renown_leader = {
            "faction": "human",
            "allegiance_id": "human:camp",
            "position": (4.0, 0.0),
            "is_champion": False,
            "renown": 40.0,
        }
        leader = pick_rally_leader_contract(
            actor_faction="human",
            actor_allegiance_id="human:camp",
            actor_position=(0.0, 0.0),
            candidates=[renown_leader, champion],
            max_distance=14.0,
        )
        self.assertIs(leader, champion)

        leader = pick_rally_leader_contract(
            actor_faction="human",
            actor_allegiance_id="human:camp",
            actor_position=(0.0, 0.0),
            candidates=[renown_leader],
            max_distance=14.0,
        )
        self.assertIs(leader, renown_leader)

    def test_notoriety_can_trigger_avoid_bias_for_weaker_units(self):
        avoid = should_avoid_notorious_enemy_contract(
            actor_is_champion=False,
            actor_kind="adventurer",
            actor_has_relic=False,
            actor_is_special_arrival=False,
            actor_hp=98.0,
            actor_max_hp=130.0,
            actor_energy=62.0,
            actor_max_energy=120.0,
            vision_range=18.0,
            distance=8.0,
            enemy_notoriety=60.0,
        )
        self.assertTrue(avoid)

        avoid = should_avoid_notorious_enemy_contract(
            actor_is_champion=False,
            actor_kind="brute_monster",
            actor_has_relic=False,
            actor_is_special_arrival=False,
            actor_hp=98.0,
            actor_max_hp=130.0,
            actor_energy=62.0,
            actor_max_energy=120.0,
            vision_range=18.0,
            distance=8.0,
            enemy_notoriety=60.0,
        )
        self.assertFalse(avoid)

    def test_implementation_hooks_exist(self):
        self.assertIn("var renown: float", self.actor_content)
        self.assertIn("var notoriety: float", self.actor_content)
        self.assertIn("func add_renown", self.actor_content)
        self.assertIn("func add_notoriety", self.actor_content)
        self.assertIn("func decay_notability", self.actor_content)
        self.assertIn("func renown_tag", self.actor_content)
        self.assertIn("func notoriety_tag", self.actor_content)

        self.assertIn("rally_renown_regroup", self.ai_content)
        self.assertIn("notoriety_avoid", self.ai_content)
        self.assertIn("_find_nearby_allied_renown_figure", self.ai_content)
        self.assertIn("_find_notoriety_focus_enemy", self.ai_content)

        self.assertIn("NOTABILITY_LOG_THRESHOLDS", self.loop_content)
        self.assertIn("BOUNTY_NOTORIETY_PRIORITY_MIN", self.loop_content)
        self.assertIn("Renown Rising", self.loop_content)
        self.assertIn("Notoriety Rising", self.loop_content)
        self.assertIn('"avg_renown"', self.loop_content)
        self.assertIn('"avg_notoriety"', self.loop_content)
        self.assertIn('"top_renown_labels"', self.loop_content)
        self.assertIn('"top_notoriety_labels"', self.loop_content)

        self.assertIn("Renown:", self.overlay_content)
        self.assertIn("Notoriety:", self.overlay_content)
        self.assertIn("Top renown figures:", self.overlay_content)
        self.assertIn("Top notoriety figures:", self.overlay_content)

        self.assertIn("renown", self.readme_content)
        self.assertIn("notoriety", self.readme_content)


if __name__ == "__main__":
    unittest.main()
