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


def rivalry_candidate_contract(
    *,
    notable_a: bool,
    notable_b: bool,
    same_faction: bool,
    has_active_a: bool,
    has_active_b: bool,
    cooldown_ready_a: bool,
    cooldown_ready_b: bool,
    engagement_score: float,
    min_score: float,
) -> bool:
    if not notable_a or not notable_b:
        return False
    if same_faction:
        return False
    if has_active_a or has_active_b:
        return False
    if not cooldown_ready_a or not cooldown_ready_b:
        return False
    return engagement_score >= min_score


def rivalry_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    alive_total: int,
    min_population: int,
    active_total: int,
    max_active: int,
    has_candidate: bool,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if alive_total < min_population:
        return global_cooldown_left, False
    if active_total >= max_active:
        return global_cooldown_left, False
    if not has_candidate:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def duel_start_contract(
    *,
    duel_active: bool,
    close_hold: float,
    hold_threshold: float,
    roll: float,
    start_chance: float,
) -> bool:
    if duel_active:
        return False
    if close_hold < hold_threshold:
        return False
    return roll <= start_chance


def rivalry_end_contract(
    *,
    victim_has_rivalry: bool,
    killer_is_rival: bool,
    actor_missing: bool,
    timeout: bool,
) -> str:
    if not victim_has_rivalry:
        return "none"
    if killer_is_rival:
        return "resolved"
    if actor_missing:
        return "ended_actor_unavailable"
    if timeout:
        return "expired"
    return "ended"


def rivalry_focus_contract(
    *,
    default_enemy_id: int,
    rival_id: int,
    rival_visible: bool,
    roll: float,
    focus_weight: float,
) -> int:
    if rival_id == 0 or not rival_visible:
        return default_enemy_id
    if roll <= focus_weight:
        return rival_id
    return default_enemy_id


class TestGame3DRivalryBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"RIVALRY_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"RIVALRY_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"RIVALRY_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"RIVALRY_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.actor_cooldown = _extract_float(
            self.loop_content,
            r"RIVALRY_ACTOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"RIVALRY_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"RIVALRY_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"RIVALRY_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"RIVALRY_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.min_engagement_score = _extract_float(
            self.loop_content,
            r"RIVALRY_MIN_ENGAGEMENT_SCORE:\s*float\s*=\s*([0-9.]+)",
        )
        self.base_focus = _extract_float(
            self.loop_content,
            r"RIVALRY_BASE_FOCUS_WEIGHT:\s*float\s*=\s*([0-9.]+)",
        )
        self.duel_focus = _extract_float(
            self.loop_content,
            r"RIVALRY_DUEL_FOCUS_WEIGHT:\s*float\s*=\s*([0-9.]+)",
        )
        self.duel_range = _extract_float(
            self.loop_content,
            r"RIVALRY_DUEL_RANGE:\s*float\s*=\s*([0-9.]+)",
        )
        self.duel_hold = _extract_float(
            self.loop_content,
            r"RIVALRY_DUEL_HOLD:\s*float\s*=\s*([0-9.]+)",
        )
        self.duel_start_chance = _extract_float(
            self.loop_content,
            r"RIVALRY_DUEL_START_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_rivalry_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 50.0)
        self.assertLessEqual(self.start_delay, 220.0)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 7.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.30)
        self.assertGreaterEqual(self.global_cooldown, 10.0)
        self.assertLessEqual(self.global_cooldown, 90.0)
        self.assertGreaterEqual(self.actor_cooldown, 20.0)
        self.assertLessEqual(self.actor_cooldown, 120.0)
        self.assertGreaterEqual(self.duration_min, 10.0)
        self.assertLessEqual(self.duration_min, 45.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 55.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreaterEqual(self.min_engagement_score, 1.5)
        self.assertLessEqual(self.min_engagement_score, 4.0)
        self.assertGreater(self.base_focus, 0.0)
        self.assertLessEqual(self.base_focus, 0.75)
        self.assertGreaterEqual(self.duel_focus, self.base_focus)
        self.assertLessEqual(self.duel_focus, 0.90)
        self.assertGreater(self.duel_range, 2.0)
        self.assertLessEqual(self.duel_range, 10.0)
        self.assertGreater(self.duel_hold, 0.3)
        self.assertLessEqual(self.duel_hold, 2.0)
        self.assertGreaterEqual(self.duel_start_chance, 0.20)
        self.assertLessEqual(self.duel_start_chance, 0.70)

    def test_trigger_is_bounded_and_one_rivalry_per_actor(self):
        self.assertTrue(
            rivalry_candidate_contract(
                notable_a=True,
                notable_b=True,
                same_faction=False,
                has_active_a=False,
                has_active_b=False,
                cooldown_ready_a=True,
                cooldown_ready_b=True,
                engagement_score=self.min_engagement_score + 0.2,
                min_score=self.min_engagement_score,
            )
        )
        self.assertFalse(
            rivalry_candidate_contract(
                notable_a=True,
                notable_b=True,
                same_faction=False,
                has_active_a=True,
                has_active_b=False,
                cooldown_ready_a=True,
                cooldown_ready_b=True,
                engagement_score=self.min_engagement_score + 0.2,
                min_score=self.min_engagement_score,
            )
        )

        cooldown_left, started = rivalry_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        _cooldown_left, started = rivalry_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=self.max_active,
            max_active=self.max_active,
            has_candidate=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_duel_window_is_short_and_optional(self):
        self.assertTrue(
            duel_start_contract(
                duel_active=False,
                close_hold=self.duel_hold,
                hold_threshold=self.duel_hold,
                roll=0.0,
                start_chance=self.duel_start_chance,
            )
        )
        self.assertFalse(
            duel_start_contract(
                duel_active=False,
                close_hold=self.duel_hold * 0.5,
                hold_threshold=self.duel_hold,
                roll=0.0,
                start_chance=self.duel_start_chance,
            )
        )

    def test_resolution_and_end_contracts_are_clean(self):
        self.assertEqual(
            rivalry_end_contract(
                victim_has_rivalry=True,
                killer_is_rival=True,
                actor_missing=False,
                timeout=False,
            ),
            "resolved",
        )
        self.assertEqual(
            rivalry_end_contract(
                victim_has_rivalry=True,
                killer_is_rival=False,
                actor_missing=False,
                timeout=True,
            ),
            "expired",
        )
        self.assertEqual(
            rivalry_end_contract(
                victim_has_rivalry=True,
                killer_is_rival=False,
                actor_missing=True,
                timeout=False,
            ),
            "ended_actor_unavailable",
        )

    def test_focus_bias_is_light_but_real(self):
        self.assertEqual(
            rivalry_focus_contract(
                default_enemy_id=7,
                rival_id=42,
                rival_visible=True,
                roll=0.0,
                focus_weight=self.base_focus,
            ),
            42,
        )
        self.assertEqual(
            rivalry_focus_contract(
                default_enemy_id=7,
                rival_id=42,
                rival_visible=False,
                roll=0.0,
                focus_weight=self.base_focus,
            ),
            7,
        )

    def test_hooks_exist_across_runtime_ai_actor_hud_and_docs(self):
        self.assertIn("_setup_rivalry_state", self.loop_content)
        self.assertIn("_update_rivalries", self.loop_content)
        self.assertIn("_record_rivalry_engagement", self.loop_content)
        self.assertIn("_handle_rivalry_death", self.loop_content)
        self.assertIn("Rivalry START", self.loop_content)
        self.assertIn("Duel START", self.loop_content)
        self.assertIn("Rivalry RESOLVED", self.loop_content)
        self.assertIn("Rivalry END", self.loop_content)
        self.assertIn('"rivalry_active_total"', self.loop_content)
        self.assertIn('"duel_active_total"', self.loop_content)
        self.assertIn('"rivalry_active_labels"', self.loop_content)

        self.assertIn("get_rivalry_guidance", self.ai_content)
        self.assertIn("rival_target", self.ai_content)
        self.assertIn("set_rivalry_state", self.actor_content)
        self.assertIn("rivalry_tag", self.actor_content)
        self.assertIn("Rivalries:", self.overlay_content)
        self.assertIn("Rival pairs:", self.overlay_content)

        self.assertIn("rivalry", self.readme_content)
        self.assertIn("duel", self.readme_content)


if __name__ == "__main__":
    unittest.main()
