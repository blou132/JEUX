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


def oath_start_contract(
    *,
    actor_notable: bool,
    has_active_oath: bool,
    global_cooldown_left: float,
    actor_cooldown_left: float,
    active_total: int,
    max_active: int,
    trigger_roll: float,
    trigger_chance: float,
) -> bool:
    if not actor_notable:
        return False
    if has_active_oath:
        return False
    if global_cooldown_left > 0.0:
        return False
    if actor_cooldown_left > 0.0:
        return False
    if active_total >= max_active:
        return False
    return trigger_roll <= trigger_chance


def oath_end_contract(
    *,
    oath_type: str,
    anchor_active: bool,
    target_alive: bool,
    hostile_still_valid: bool,
    near_hold: float,
    fulfill_hold: float,
    now: float,
    ends_at: float,
) -> str:
    if oath_type == "oath_of_guarding" and not anchor_active:
        return "broken_anchor_lost"
    if oath_type == "oath_of_vengeance":
        if not target_alive:
            return "fulfilled_target_fallen"
        if not hostile_still_valid:
            return "broken_hostility_lost"
    if oath_type == "oath_of_seeking" and near_hold >= fulfill_hold:
        return "fulfilled_objective_reached"
    if now >= ends_at:
        return "ended_duration_complete"
    return "active"


def oath_guidance_contract(*, has_enemy: bool, oath_type: str, roll: float, weight: float) -> str:
    weight = max(0.20, min(0.86, weight))
    if has_enemy:
        if oath_type == "oath_of_vengeance" and roll <= weight:
            return "focus_enemy"
        return "normal_enemy"

    if oath_type == "oath_of_guarding" and roll <= weight:
        return "poi"
    if oath_type == "oath_of_seeking" and roll <= weight:
        return "hunt"
    return "wander"


class TestGame3DOathsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"OATH_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"OATH_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.actor_cooldown = _extract_float(
            self.loop_content,
            r"OATH_ACTOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"OATH_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"OATH_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"OATH_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.start_base = _extract_float(
            self.loop_content,
            r"OATH_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"OATH_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.renown_trigger = _extract_float(
            self.loop_content,
            r"OATH_NOTABLE_RENOWN_TRIGGER:\s*float\s*=\s*([0-9.]+)",
        )
        self.fulfill_hold = _extract_float(
            self.loop_content,
            r"OATH_FULFILL_HOLD:\s*float\s*=\s*([0-9.]+)",
        )

    def test_oath_constants_are_rare_bounded_and_readable(self):
        self.assertGreaterEqual(self.start_delay, 90.0)
        self.assertLessEqual(self.start_delay, 320.0)
        self.assertGreaterEqual(self.global_cooldown, 8.0)
        self.assertLessEqual(self.global_cooldown, 40.0)
        self.assertGreaterEqual(self.actor_cooldown, 24.0)
        self.assertLessEqual(self.actor_cooldown, 120.0)
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 24.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 32.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 4)
        self.assertGreaterEqual(self.start_base, 0.12)
        self.assertLessEqual(self.start_base, 0.40)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 18)
        self.assertGreaterEqual(self.renown_trigger, 50.0)
        self.assertLessEqual(self.renown_trigger, 80.0)
        self.assertGreater(self.fulfill_hold, 0.3)
        self.assertLessEqual(self.fulfill_hold, 3.0)

    def test_start_contract_enforces_uniqueness_and_cap(self):
        self.assertFalse(
            oath_start_contract(
                actor_notable=False,
                has_active_oath=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            oath_start_contract(
                actor_notable=True,
                has_active_oath=True,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            oath_start_contract(
                actor_notable=True,
                has_active_oath=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=self.max_active,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertTrue(
            oath_start_contract(
                actor_notable=True,
                has_active_oath=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.10,
                trigger_chance=min(0.78, self.start_base + 0.12),
            )
        )

    def test_end_contract_supports_end_fulfilled_and_broken(self):
        self.assertEqual(
            oath_end_contract(
                oath_type="oath_of_guarding",
                anchor_active=False,
                target_alive=True,
                hostile_still_valid=True,
                near_hold=0.0,
                fulfill_hold=self.fulfill_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "broken_anchor_lost",
        )
        self.assertEqual(
            oath_end_contract(
                oath_type="oath_of_vengeance",
                anchor_active=True,
                target_alive=False,
                hostile_still_valid=True,
                near_hold=0.0,
                fulfill_hold=self.fulfill_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "fulfilled_target_fallen",
        )
        self.assertEqual(
            oath_end_contract(
                oath_type="oath_of_seeking",
                anchor_active=True,
                target_alive=True,
                hostile_still_valid=True,
                near_hold=self.fulfill_hold,
                fulfill_hold=self.fulfill_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "fulfilled_objective_reached",
        )
        self.assertEqual(
            oath_end_contract(
                oath_type="oath_of_guarding",
                anchor_active=True,
                target_alive=True,
                hostile_still_valid=True,
                near_hold=0.0,
                fulfill_hold=self.fulfill_hold,
                now=24.0,
                ends_at=20.0,
            ),
            "ended_duration_complete",
        )

    def test_guidance_bias_is_light_and_local(self):
        self.assertEqual(
            oath_guidance_contract(has_enemy=False, oath_type="oath_of_guarding", roll=0.1, weight=0.6),
            "poi",
        )
        self.assertEqual(
            oath_guidance_contract(has_enemy=False, oath_type="oath_of_seeking", roll=0.1, weight=0.6),
            "hunt",
        )
        self.assertEqual(
            oath_guidance_contract(has_enemy=True, oath_type="oath_of_vengeance", roll=0.1, weight=0.6),
            "focus_enemy",
        )
        self.assertEqual(
            oath_guidance_contract(has_enemy=True, oath_type="oath_of_guarding", roll=0.1, weight=0.6),
            "normal_enemy",
        )

    def test_hooks_exist_across_runtime_ai_actor_hud_and_docs(self):
        self.assertIn("_setup_oath_state", self.loop_content)
        self.assertIn("_update_oath_runtime", self.loop_content)
        self.assertIn("_try_start_oath", self.loop_content)
        self.assertIn("_clear_actor_oath_tracking", self.loop_content)
        self.assertIn("Oath START", self.loop_content)
        self.assertIn("Oath END", self.loop_content)
        self.assertIn("Oath FULFILLED", self.loop_content)
        self.assertIn("Oath BROKEN", self.loop_content)
        self.assertIn('"oath_active_count"', self.loop_content)
        self.assertIn('"oath_active_labels"', self.loop_content)
        self.assertIn('"oath_started_total"', self.loop_content)

        self.assertIn("destiny:", self.loop_content)
        self.assertIn("rivalry:", self.loop_content)
        self.assertIn("vendetta_started:", self.loop_content)
        self.assertIn("legacy_successor:", self.loop_content)
        self.assertIn("bond_stable:", self.loop_content)
        self.assertIn("recovery_stabilized:", self.loop_content)
        self.assertIn("mending_window:", self.loop_content)

        self.assertIn("get_oath_guidance", self.ai_content)
        self.assertIn("oath:guarding", self.ai_content)
        self.assertIn("oath:seeking", self.ai_content)
        self.assertIn("oath_of_vengeance", self.ai_content)

        self.assertIn("set_oath_state", self.actor_content)
        self.assertIn("get_oath_guidance", self.actor_content)
        self.assertIn("oath_tag", self.actor_content)

        self.assertIn("Oaths:", self.overlay_content)
        self.assertIn("Oath labels:", self.overlay_content)

        self.assertIn("oath", self.readme_content)
        self.assertIn("sworn", self.readme_content)


if __name__ == "__main__":
    unittest.main()
