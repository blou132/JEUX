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


def crisis_spawn_contract(
    *,
    anchor_active: bool,
    already_active: bool,
    cooldown_left: float,
    start_base: float,
    shock_bonus: float,
    trigger_roll: float,
) -> bool:
    if not anchor_active:
        return False
    if already_active:
        return False
    if cooldown_left > 0.0:
        return False
    chance = max(0.14, min(0.82, start_base + shock_bonus))
    return trigger_roll <= chance


def crisis_end_contract(
    *,
    anchor_active: bool,
    now: float,
    ends_at: float,
    successor_ready: bool,
    calming_event: bool,
) -> str:
    if not anchor_active:
        return "expired_anchor_lost"
    if successor_ready or calming_event:
        return "resolved"
    if now >= ends_at:
        return "expired_time"
    return "active"


def crisis_effect_contract(
    *,
    crisis_active: bool,
    rally_bonus_active: bool,
    suppress_roll: float,
    suppress_chance: float,
    raid_weight: float,
    raid_mult: float,
) -> dict:
    if not crisis_active:
        return {
            "rally_bonus_active": rally_bonus_active,
            "raid_weight": raid_weight,
        }

    next_rally_bonus = rally_bonus_active and suppress_roll > suppress_chance
    next_raid_weight = max(0.28, raid_weight * raid_mult)
    return {
        "rally_bonus_active": next_rally_bonus,
        "raid_weight": next_raid_weight,
    }


class TestGame3DAllegianceCrisisBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.duration_min = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.cooldown = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.raid_mult = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_RAID_WEIGHT_MULT:\s*float\s*=\s*([0-9.]+)",
        )
        self.suppress_chance = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_RALLY_BONUS_SUPPRESS_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.base_chance = _extract_float(
            self.loop_content,
            r"ALLEGIANCE_CRISIS_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_crisis_constants_are_bounded(self):
        self.assertGreaterEqual(self.duration_min, 12.0)
        self.assertLessEqual(self.duration_min, 28.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 44.0)
        self.assertGreaterEqual(self.cooldown, 24.0)
        self.assertLessEqual(self.cooldown, 80.0)
        self.assertGreaterEqual(self.raid_mult, 0.65)
        self.assertLessEqual(self.raid_mult, 1.0)
        self.assertGreaterEqual(self.suppress_chance, 0.2)
        self.assertLessEqual(self.suppress_chance, 0.8)
        self.assertGreaterEqual(self.base_chance, 0.14)
        self.assertLessEqual(self.base_chance, 0.65)

    def test_crisis_trigger_is_bounded_and_unique(self):
        self.assertFalse(
            crisis_spawn_contract(
                anchor_active=False,
                already_active=False,
                cooldown_left=0.0,
                start_base=self.base_chance,
                shock_bonus=0.4,
                trigger_roll=0.0,
            )
        )
        self.assertFalse(
            crisis_spawn_contract(
                anchor_active=True,
                already_active=True,
                cooldown_left=0.0,
                start_base=self.base_chance,
                shock_bonus=0.4,
                trigger_roll=0.0,
            )
        )
        self.assertFalse(
            crisis_spawn_contract(
                anchor_active=True,
                already_active=False,
                cooldown_left=self.cooldown,
                start_base=self.base_chance,
                shock_bonus=0.4,
                trigger_roll=0.0,
            )
        )
        self.assertTrue(
            crisis_spawn_contract(
                anchor_active=True,
                already_active=False,
                cooldown_left=0.0,
                start_base=self.base_chance,
                shock_bonus=0.24,
                trigger_roll=0.20,
            )
        )

    def test_crisis_end_is_clean_with_resolved_or_expired(self):
        self.assertEqual(
            crisis_end_contract(
                anchor_active=True,
                now=12.0,
                ends_at=20.0,
                successor_ready=False,
                calming_event=False,
            ),
            "active",
        )
        self.assertEqual(
            crisis_end_contract(
                anchor_active=True,
                now=12.0,
                ends_at=20.0,
                successor_ready=True,
                calming_event=False,
            ),
            "resolved",
        )
        self.assertEqual(
            crisis_end_contract(
                anchor_active=True,
                now=12.0,
                ends_at=20.0,
                successor_ready=False,
                calming_event=True,
            ),
            "resolved",
        )
        self.assertEqual(
            crisis_end_contract(
                anchor_active=False,
                now=12.0,
                ends_at=20.0,
                successor_ready=False,
                calming_event=False,
            ),
            "expired_anchor_lost",
        )
        self.assertEqual(
            crisis_end_contract(
                anchor_active=True,
                now=21.0,
                ends_at=20.0,
                successor_ready=False,
                calming_event=False,
            ),
            "expired_time",
        )

    def test_crisis_effects_are_light_and_real(self):
        active = crisis_effect_contract(
            crisis_active=True,
            rally_bonus_active=True,
            suppress_roll=0.10,
            suppress_chance=self.suppress_chance,
            raid_weight=0.72,
            raid_mult=self.raid_mult,
        )
        self.assertFalse(active["rally_bonus_active"])
        self.assertLess(active["raid_weight"], 0.72)
        self.assertGreaterEqual(active["raid_weight"], 0.28)

        inactive = crisis_effect_contract(
            crisis_active=False,
            rally_bonus_active=True,
            suppress_roll=0.10,
            suppress_chance=self.suppress_chance,
            raid_weight=0.72,
            raid_mult=self.raid_mult,
        )
        self.assertTrue(inactive["rally_bonus_active"])
        self.assertEqual(inactive["raid_weight"], 0.72)

    def test_hooks_exist_across_runtime_world_hud_and_docs(self):
        self.assertIn("_setup_allegiance_crisis_state", self.loop_content)
        self.assertIn("_update_allegiance_crisis_runtime", self.loop_content)
        self.assertIn("_try_start_allegiance_crisis", self.loop_content)
        self.assertIn("Crisis START", self.loop_content)
        self.assertIn("Crisis END", self.loop_content)
        self.assertIn("Crisis RESOLVED", self.loop_content)
        self.assertIn("Crisis EXPIRED", self.loop_content)
        self.assertIn('"crisis_started_total"', self.loop_content)
        self.assertIn('"allegiance_crisis_labels"', self.loop_content)

        self.assertIn("set_allegiance_crisis_raid_modifiers", self.world_content)
        self.assertIn("get_allegiance_crisis_raid_multiplier", self.world_content)
        self.assertIn("allegiance_crisis_raid_mult_by_id", self.world_content)

        self.assertIn("Crisis:", self.overlay_content)
        self.assertIn("Crisis map:", self.overlay_content)
        self.assertIn("allegiance crisis", self.readme_content)


if __name__ == "__main__":
    unittest.main()
