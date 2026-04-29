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


def mending_start_contract(
    *,
    source_ok: bool,
    target_ok: bool,
    same_allegiance: bool,
    global_cooldown_left: float,
    source_cooldown_left: float,
    target_cooldown_left: float,
    active_for_source: bool,
    active_for_target: bool,
    active_total: int,
    max_active: int,
    trigger_roll: float,
    trigger_chance: float,
) -> bool:
    if not source_ok or not target_ok:
        return False
    if same_allegiance:
        return False
    if global_cooldown_left > 0.0:
        return False
    if source_cooldown_left > 0.0 or target_cooldown_left > 0.0:
        return False
    if active_for_source or active_for_target:
        return False
    if active_total >= max_active:
        return False
    return trigger_roll <= trigger_chance


def mending_end_contract(
    *,
    source_anchor_active: bool,
    target_anchor_active: bool,
    escalation: bool,
    now: float,
    ends_at: float,
) -> str:
    if not source_anchor_active or not target_anchor_active:
        return "broken_anchor_lost"
    if escalation:
        return "broken_escalation"
    if now >= ends_at:
        return "ended_duration_complete"
    return "active"


def mending_effect_contract(
    *,
    active: bool,
    pair_match: bool,
    raid_weight: float,
    bounty_weight: float,
    raid_delta: float,
    bounty_delta: float,
) -> dict[str, float | bool]:
    if not active or not pair_match:
        return {
            "vendetta_blocked": False,
            "raid_weight": raid_weight,
            "bounty_weight": bounty_weight,
        }

    return {
        "vendetta_blocked": True,
        "raid_weight": max(0.28, raid_weight + raid_delta),
        "bounty_weight": max(0.26, bounty_weight + bounty_delta),
    }


class TestGame3DMendingBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"MENDING_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"MENDING_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.allegiance_cooldown = _extract_float(
            self.loop_content,
            r"MENDING_ALLEGIANCE_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"MENDING_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"MENDING_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"MENDING_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.start_base = _extract_float(
            self.loop_content,
            r"MENDING_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.raid_delta = _extract_float(
            self.loop_content,
            r"MENDING_RAID_WEIGHT_DELTA:\s*float\s*=\s*(-?[0-9.]+)",
        )
        self.bounty_delta = _extract_float(
            self.loop_content,
            r"MENDING_BOUNTY_WEIGHT_DELTA:\s*float\s*=\s*(-?[0-9.]+)",
        )

    def test_mending_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 90.0)
        self.assertLessEqual(self.start_delay, 260.0)
        self.assertGreaterEqual(self.global_cooldown, 18.0)
        self.assertLessEqual(self.global_cooldown, 90.0)
        self.assertGreaterEqual(self.allegiance_cooldown, 24.0)
        self.assertLessEqual(self.allegiance_cooldown, 120.0)
        self.assertGreaterEqual(self.duration_min, 6.0)
        self.assertLessEqual(self.duration_min, 24.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 36.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.start_base, 0.12)
        self.assertLessEqual(self.start_base, 0.55)
        self.assertLess(self.raid_delta, 0.0)
        self.assertGreaterEqual(self.raid_delta, -0.12)
        self.assertLess(self.bounty_delta, 0.0)
        self.assertGreaterEqual(self.bounty_delta, -0.14)

    def test_trigger_contract_is_unique_and_capped(self):
        self.assertFalse(
            mending_start_contract(
                source_ok=True,
                target_ok=True,
                same_allegiance=True,
                global_cooldown_left=0.0,
                source_cooldown_left=0.0,
                target_cooldown_left=0.0,
                active_for_source=False,
                active_for_target=False,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            mending_start_contract(
                source_ok=True,
                target_ok=True,
                same_allegiance=False,
                global_cooldown_left=self.global_cooldown,
                source_cooldown_left=0.0,
                target_cooldown_left=0.0,
                active_for_source=False,
                active_for_target=False,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            mending_start_contract(
                source_ok=True,
                target_ok=True,
                same_allegiance=False,
                global_cooldown_left=0.0,
                source_cooldown_left=0.0,
                target_cooldown_left=0.0,
                active_for_source=True,
                active_for_target=False,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            mending_start_contract(
                source_ok=True,
                target_ok=True,
                same_allegiance=False,
                global_cooldown_left=0.0,
                source_cooldown_left=0.0,
                target_cooldown_left=0.0,
                active_for_source=False,
                active_for_target=False,
                active_total=self.max_active,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertTrue(
            mending_start_contract(
                source_ok=True,
                target_ok=True,
                same_allegiance=False,
                global_cooldown_left=0.0,
                source_cooldown_left=0.0,
                target_cooldown_left=0.0,
                active_for_source=False,
                active_for_target=False,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.12,
                trigger_chance=min(0.72, self.start_base + 0.20),
            )
        )

    def test_end_and_break_contracts_are_clean(self):
        self.assertEqual(
            mending_end_contract(
                source_anchor_active=True,
                target_anchor_active=True,
                escalation=False,
                now=12.0,
                ends_at=18.0,
            ),
            "active",
        )
        self.assertEqual(
            mending_end_contract(
                source_anchor_active=True,
                target_anchor_active=True,
                escalation=True,
                now=12.0,
                ends_at=18.0,
            ),
            "broken_escalation",
        )
        self.assertEqual(
            mending_end_contract(
                source_anchor_active=False,
                target_anchor_active=True,
                escalation=False,
                now=12.0,
                ends_at=18.0,
            ),
            "broken_anchor_lost",
        )
        self.assertEqual(
            mending_end_contract(
                source_anchor_active=True,
                target_anchor_active=True,
                escalation=False,
                now=19.0,
                ends_at=18.0,
            ),
            "ended_duration_complete",
        )

    def test_effects_are_light_real_and_local(self):
        active = mending_effect_contract(
            active=True,
            pair_match=True,
            raid_weight=0.70,
            bounty_weight=0.62,
            raid_delta=self.raid_delta,
            bounty_delta=self.bounty_delta,
        )
        self.assertTrue(active["vendetta_blocked"])
        self.assertLess(active["raid_weight"], 0.70)
        self.assertLess(active["bounty_weight"], 0.62)

        inactive = mending_effect_contract(
            active=False,
            pair_match=True,
            raid_weight=0.70,
            bounty_weight=0.62,
            raid_delta=self.raid_delta,
            bounty_delta=self.bounty_delta,
        )
        self.assertFalse(inactive["vendetta_blocked"])
        self.assertEqual(inactive["raid_weight"], 0.70)
        self.assertEqual(inactive["bounty_weight"], 0.62)

    def test_hooks_exist_across_runtime_world_hud_and_docs(self):
        self.assertIn("_setup_mending_state", self.loop_content)
        self.assertIn("_update_mending_runtime", self.loop_content)
        self.assertIn("_try_start_mending_arc", self.loop_content)
        self.assertIn("Mending START", self.loop_content)
        self.assertIn("Mending END", self.loop_content)
        self.assertIn("Mending BROKEN", self.loop_content)
        self.assertIn('"mending_active_count"', self.loop_content)
        self.assertIn('"mending_active_labels"', self.loop_content)

        self.assertIn("set_mending_state", self.world_content)
        self.assertIn("get_allegiance_mending_modifiers", self.world_content)
        self.assertIn("vendetta_suppressed_pair_keys", self.world_content)
        self.assertIn("_is_vendetta_pair_suppressed", self.world_content)

        self.assertIn("Mending:", self.overlay_content)
        self.assertIn("Mending arcs:", self.overlay_content)
        self.assertIn("mending", self.readme_content)
        self.assertIn("reconciliation", self.readme_content)


if __name__ == "__main__":
    unittest.main()
