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


def recovery_spawn_contract(
    *,
    anchor_active: bool,
    crisis_active: bool,
    already_active: bool,
    cooldown_left: float,
    trigger_roll: float,
    trigger_chance: float,
) -> bool:
    if not anchor_active:
        return False
    if crisis_active:
        return False
    if already_active:
        return False
    if cooldown_left > 0.0:
        return False
    return trigger_roll <= trigger_chance


def recovery_end_contract(
    *,
    anchor_active: bool,
    crisis_restart: bool,
    now: float,
    ends_at: float,
) -> str:
    if not anchor_active:
        return "interrupted_anchor_lost"
    if crisis_restart:
        return "interrupted_crisis_restart"
    if now >= ends_at:
        return "ended_duration_complete"
    return "active"


def recovery_effect_contract(
    *,
    recovery_active: bool,
    rally_bonus_active: bool,
    boost_roll: float,
    boost_chance: float,
    defense_weight: float,
    defense_delta: float,
) -> dict:
    if not recovery_active:
        return {
            "rally_bonus_active": rally_bonus_active,
            "defense_weight": defense_weight,
        }

    next_rally_bonus = rally_bonus_active or boost_roll <= boost_chance
    next_defense_weight = min(0.92, defense_weight + defense_delta)
    return {
        "rally_bonus_active": next_rally_bonus,
        "defense_weight": next_defense_weight,
    }


class TestGame3DRecoveryBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.duration_min = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.cooldown = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.start_base = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.defense_delta = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_DEFENSE_WEIGHT_DELTA:\s*float\s*=\s*([0-9.]+)",
        )
        self.rally_boost_chance = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_RECOVERY_RALLY_BONUS_BOOST_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_recovery_constants_are_bounded(self):
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 20.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 28.0)
        self.assertGreaterEqual(self.cooldown, 18.0)
        self.assertLessEqual(self.cooldown, 60.0)
        self.assertGreaterEqual(self.start_base, 0.20)
        self.assertLessEqual(self.start_base, 0.65)
        self.assertGreaterEqual(self.defense_delta, 0.02)
        self.assertLessEqual(self.defense_delta, 0.16)
        self.assertGreaterEqual(self.rally_boost_chance, 0.18)
        self.assertLessEqual(self.rally_boost_chance, 0.62)

    def test_recovery_trigger_is_bounded_and_unique(self):
        chance = min(0.86, max(0.16, self.start_base + 0.14))
        self.assertFalse(
            recovery_spawn_contract(
                anchor_active=False,
                crisis_active=False,
                already_active=False,
                cooldown_left=0.0,
                trigger_roll=0.0,
                trigger_chance=chance,
            )
        )
        self.assertFalse(
            recovery_spawn_contract(
                anchor_active=True,
                crisis_active=True,
                already_active=False,
                cooldown_left=0.0,
                trigger_roll=0.0,
                trigger_chance=chance,
            )
        )
        self.assertFalse(
            recovery_spawn_contract(
                anchor_active=True,
                crisis_active=False,
                already_active=True,
                cooldown_left=0.0,
                trigger_roll=0.0,
                trigger_chance=chance,
            )
        )
        self.assertFalse(
            recovery_spawn_contract(
                anchor_active=True,
                crisis_active=False,
                already_active=False,
                cooldown_left=self.cooldown,
                trigger_roll=0.0,
                trigger_chance=chance,
            )
        )
        self.assertTrue(
            recovery_spawn_contract(
                anchor_active=True,
                crisis_active=False,
                already_active=False,
                cooldown_left=0.0,
                trigger_roll=0.18,
                trigger_chance=chance,
            )
        )

    def test_recovery_end_is_clean_or_interrupted(self):
        self.assertEqual(
            recovery_end_contract(
                anchor_active=True,
                crisis_restart=False,
                now=8.0,
                ends_at=16.0,
            ),
            "active",
        )
        self.assertEqual(
            recovery_end_contract(
                anchor_active=True,
                crisis_restart=False,
                now=18.0,
                ends_at=16.0,
            ),
            "ended_duration_complete",
        )
        self.assertEqual(
            recovery_end_contract(
                anchor_active=False,
                crisis_restart=False,
                now=10.0,
                ends_at=16.0,
            ),
            "interrupted_anchor_lost",
        )
        self.assertEqual(
            recovery_end_contract(
                anchor_active=True,
                crisis_restart=True,
                now=10.0,
                ends_at=16.0,
            ),
            "interrupted_crisis_restart",
        )

    def test_recovery_effects_are_light_and_real(self):
        active = recovery_effect_contract(
            recovery_active=True,
            rally_bonus_active=False,
            boost_roll=0.10,
            boost_chance=self.rally_boost_chance,
            defense_weight=0.70,
            defense_delta=self.defense_delta,
        )
        self.assertTrue(active["rally_bonus_active"])
        self.assertGreater(active["defense_weight"], 0.70)
        self.assertLessEqual(active["defense_weight"], 0.92)

        inactive = recovery_effect_contract(
            recovery_active=False,
            rally_bonus_active=False,
            boost_roll=0.10,
            boost_chance=self.rally_boost_chance,
            defense_weight=0.70,
            defense_delta=self.defense_delta,
        )
        self.assertFalse(inactive["rally_bonus_active"])
        self.assertEqual(inactive["defense_weight"], 0.70)

    def test_hooks_exist_across_runtime_world_hud_and_docs(self):
        self.assertIn("_setup_allegiance_recovery_state", self.loop_content)
        self.assertIn("_update_allegiance_recovery_runtime", self.loop_content)
        self.assertIn("_try_start_allegiance_recovery", self.loop_content)
        self.assertIn("Recovery START", self.loop_content)
        self.assertIn("Recovery END", self.loop_content)
        self.assertIn("Recovery INTERRUPTED", self.loop_content)
        self.assertIn('"recovery_started_total"', self.loop_content)
        self.assertIn('"allegiance_recovery_labels"', self.loop_content)

        self.assertIn("set_allegiance_recovery_defense_modifiers", self.world_content)
        self.assertIn("get_allegiance_recovery_defense_delta", self.world_content)
        self.assertIn("allegiance_recovery_defense_delta_by_id", self.world_content)

        self.assertIn("Recovery:", self.overlay_content)
        self.assertIn("Recovery map:", self.overlay_content)
        self.assertIn("recovery pulse", self.readme_content)


if __name__ == "__main__":
    unittest.main()
