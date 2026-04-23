from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def _extract_float(content: str, pattern: str) -> float:
    match = re.search(pattern, content)
    if not match:
        raise AssertionError(f"Pattern not found: {pattern}")
    return float(match.group(1))


def _extract_int(content: str, pattern: str) -> int:
    match = re.search(pattern, content)
    if not match:
        raise AssertionError(f"Pattern not found: {pattern}")
    return int(match.group(1))


def _target_priority(candidate: dict) -> int:
    if bool(candidate.get("has_relic", False)):
        return 3
    if bool(candidate.get("is_special_arrival", False)):
        return 2
    if bool(candidate.get("is_champion", False)):
        return 1
    return 0


def pick_bounty_target_contract(candidates: list[dict]) -> dict | None:
    best: dict | None = None
    best_priority = 0
    best_distance = 10e9
    for candidate in candidates:
        priority = _target_priority(candidate)
        if priority <= 0:
            continue
        distance = float(candidate.get("distance", 10e9))
        if priority > best_priority or (priority == best_priority and distance < best_distance):
            best = candidate
            best_priority = priority
            best_distance = distance
    return best


def bounty_spawn_step_contract(
    *,
    cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    active_total: int,
    max_active: int,
    has_source: bool,
    has_target: bool,
    cooldown_on_start: float,
) -> tuple[float, bool]:
    cooldown_left = max(0.0, cooldown_left - delta)
    if cooldown_left > 0.0:
        return cooldown_left, False
    if active_total >= max_active:
        return cooldown_left, False
    if not has_source or not has_target:
        return cooldown_left, False
    if trigger_roll > trigger_chance:
        return cooldown_left, False
    return cooldown_on_start, True


def bounty_active_step_contract(*, remaining: float, delta: float, target_alive: bool) -> tuple[float, str]:
    remaining = max(0.0, remaining - delta)
    if not target_alive:
        return remaining, "target_lost"
    if remaining <= 0.0:
        return remaining, "timeout"
    return remaining, "active"


class TestGame3DBountiesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")

        self.cooldown = _extract_float(self.loop_content, r"BOUNTY_COOLDOWN:\s*float\s*=\s*([0-9.]+)")
        self.check_interval = _extract_float(self.loop_content, r"BOUNTY_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)")
        self.trigger_chance = _extract_float(self.loop_content, r"BOUNTY_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)")
        self.max_active = _extract_int(self.loop_content, r"BOUNTY_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)")
        self.duration = _extract_float(self.loop_content, r"BOUNTY_DURATION:\s*float\s*=\s*([0-9.]+)")
        self.clear_xp = _extract_float(self.loop_content, r"BOUNTY_CLEAR_XP:\s*float\s*=\s*([0-9.]+)")

    def test_bounty_constants_are_rare_and_bounded(self):
        self.assertGreaterEqual(self.cooldown, 60.0)
        self.assertLessEqual(self.cooldown, 150.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.15)
        self.assertLessEqual(self.trigger_chance, 0.40)
        self.assertLessEqual(self.max_active, 2)
        self.assertGreaterEqual(self.duration, 15.0)
        self.assertLessEqual(self.duration, 40.0)
        self.assertGreater(self.clear_xp, 0.0)
        self.assertLessEqual(self.clear_xp, 2.5)

    def test_target_selection_prioritizes_relic_special_champion(self):
        candidates = [
            {"id": "champion", "is_champion": True, "is_special_arrival": False, "has_relic": False, "distance": 4.0},
            {"id": "special", "is_champion": True, "is_special_arrival": True, "has_relic": False, "distance": 6.0},
            {"id": "relic", "is_champion": True, "is_special_arrival": True, "has_relic": True, "distance": 12.0},
        ]
        picked = pick_bounty_target_contract(candidates)
        self.assertIsNotNone(picked)
        self.assertEqual(picked["id"], "relic")

        tied = [
            {"id": "relic_far", "has_relic": True, "distance": 10.0},
            {"id": "relic_near", "has_relic": True, "distance": 3.0},
        ]
        picked = pick_bounty_target_contract(tied)
        self.assertEqual(picked["id"], "relic_near")

    def test_spawn_step_respects_cooldown_cap_and_trigger(self):
        cooldown_left, started = bounty_spawn_step_contract(
            cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=0,
            max_active=self.max_active,
            has_source=True,
            has_target=True,
            cooldown_on_start=self.cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        cooldown_left, started = bounty_spawn_step_contract(
            cooldown_left=cooldown_left,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=0,
            max_active=self.max_active,
            has_source=True,
            has_target=True,
            cooldown_on_start=self.cooldown,
        )
        self.assertFalse(started)

        cooldown_left, started = bounty_spawn_step_contract(
            cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=self.max_active,
            max_active=self.max_active,
            has_source=True,
            has_target=True,
            cooldown_on_start=self.cooldown,
        )
        self.assertFalse(started)

    def test_active_step_ends_on_timeout_or_target_loss(self):
        remaining, status = bounty_active_step_contract(remaining=self.duration, delta=1.0, target_alive=True)
        self.assertEqual(status, "active")
        self.assertGreater(remaining, 0.0)

        remaining, status = bounty_active_step_contract(remaining=0.3, delta=1.0, target_alive=True)
        self.assertEqual(status, "timeout")

        _remaining, status = bounty_active_step_contract(remaining=self.duration, delta=1.0, target_alive=False)
        self.assertEqual(status, "target_lost")

    def test_bounty_hooks_exist_in_core_layers(self):
        self.assertIn("_update_bounty_system", self.loop_content)
        self.assertIn("_pick_bounty_target", self.loop_content)
        self.assertIn("Bounty START", self.loop_content)
        self.assertIn("Bounty CLEARED", self.loop_content)
        self.assertIn("Bounty EXPIRED", self.loop_content)
        self.assertIn("set_bounty_state", self.world_content)
        self.assertIn("get_bounty_guidance", self.world_content)
        self.assertIn("get_bounty_guidance", self.ai_content)
        self.assertIn('"state": "hunt"', self.ai_content)
        self.assertIn("set_bounty_marked", self.actor_content)
        self.assertIn("bounty_tag", self.actor_content)
        self.assertIn("Bounty:", self.overlay_content)


if __name__ == "__main__":
    unittest.main()
