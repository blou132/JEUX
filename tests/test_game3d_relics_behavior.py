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


def collect_relic_candidates_contract(
    *,
    world_event_id: str,
    has_human_anchor: bool,
    has_monster_anchor: bool,
    active_relic_ids: set[str],
) -> list[str]:
    candidates: list[str] = []
    if world_event_id == "mana_surge" and has_human_anchor and "arcane_sigil" not in active_relic_ids:
        candidates.append("arcane_sigil")
    if world_event_id == "monster_frenzy" and has_monster_anchor and "oath_standard" not in active_relic_ids:
        candidates.append("oath_standard")
    return candidates


def relic_spawn_step_contract(
    *,
    cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    active_total: int,
    max_active: int,
    has_candidate: bool,
    cooldown_on_spawn: float,
) -> tuple[float, bool]:
    cooldown_left = max(0.0, cooldown_left - delta)
    if cooldown_left > 0.0:
        return cooldown_left, False
    if active_total >= max_active:
        return cooldown_left, False
    if not has_candidate:
        return cooldown_left, False
    if trigger_roll > trigger_chance:
        return cooldown_left, False
    return cooldown_on_spawn, True


def relic_loss_step_contract(cooldown_left: float, relic_cooldown: float) -> float:
    return max(cooldown_left, relic_cooldown * 0.34)


class TestGame3DRelicsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")

        self.cooldown = _extract_float(self.loop_content, r"RELIC_COOLDOWN:\s*float\s*=\s*([0-9.]+)")
        self.check_interval = _extract_float(self.loop_content, r"RELIC_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)")
        self.trigger_chance = _extract_float(self.loop_content, r"RELIC_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)")
        self.min_dominance = _extract_float(self.loop_content, r"RELIC_MIN_DOMINANCE_SECONDS:\s*float\s*=\s*([0-9.]+)")
        self.max_active = _extract_int(self.loop_content, r"RELIC_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)")

    def test_relic_constants_are_bounded_and_rare(self):
        self.assertGreaterEqual(self.cooldown, 60.0)
        self.assertLessEqual(self.cooldown, 140.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.20)
        self.assertLessEqual(self.trigger_chance, 0.40)
        self.assertGreaterEqual(self.min_dominance, 12.0)
        self.assertLessEqual(self.min_dominance, 30.0)
        self.assertLessEqual(self.max_active, 2)

    def test_candidate_selection_is_event_and_anchor_gated(self):
        human_candidates = collect_relic_candidates_contract(
            world_event_id="mana_surge",
            has_human_anchor=True,
            has_monster_anchor=False,
            active_relic_ids=set(),
        )
        self.assertIn("arcane_sigil", human_candidates)

        monster_candidates = collect_relic_candidates_contract(
            world_event_id="monster_frenzy",
            has_human_anchor=False,
            has_monster_anchor=True,
            active_relic_ids=set(),
        )
        self.assertIn("oath_standard", monster_candidates)

        blocked_candidates = collect_relic_candidates_contract(
            world_event_id="sanctuary_calm",
            has_human_anchor=True,
            has_monster_anchor=True,
            active_relic_ids=set(),
        )
        self.assertEqual(blocked_candidates, [])

    def test_spawn_step_respects_cooldown_cap_and_chance(self):
        cooldown_after_spawn, spawned = relic_spawn_step_contract(
            cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            cooldown_on_spawn=self.cooldown,
        )
        self.assertTrue(spawned)
        self.assertGreater(cooldown_after_spawn, 0.0)

        cooldown_after_block, spawned = relic_spawn_step_contract(
            cooldown_left=cooldown_after_spawn,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            cooldown_on_spawn=self.cooldown,
        )
        self.assertFalse(spawned)
        self.assertGreater(cooldown_after_block, 0.0)

        cooldown_after_cap, spawned = relic_spawn_step_contract(
            cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            active_total=self.max_active,
            max_active=self.max_active,
            has_candidate=True,
            cooldown_on_spawn=self.cooldown,
        )
        self.assertFalse(spawned)
        self.assertEqual(cooldown_after_cap, 0.0)

    def test_loss_step_applies_safe_reset_and_hooks_exist(self):
        reset_cd = relic_loss_step_contract(0.0, self.cooldown)
        self.assertGreater(reset_cd, 0.0)
        self.assertLess(reset_cd, self.cooldown)

        self.assertIn("Relic APPEAR", self.loop_content)
        self.assertIn("Relic ACQUIRED", self.loop_content)
        self.assertIn("Relic LOST", self.loop_content)
        self.assertIn("_update_relic_system", self.loop_content)
        self.assertIn("_collect_relic_candidates", self.loop_content)
        self.assertIn("_find_relic_anchor", self.loop_content)
        self.assertIn("set_relic", self.actor_content)
        self.assertIn("has_relic", self.actor_content)
        self.assertIn("clear_relic", self.actor_content)
        self.assertIn("Relics:", self.overlay_content)
        self.assertIn("Relic carriers:", self.overlay_content)


if __name__ == "__main__":
    unittest.main()
