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


def splinter_candidate_contract(
    *,
    signals_ready: bool,
    has_active_for_allegiance: bool,
    cooldown_ready: bool,
    alive_total: int,
    min_population: int,
    active_total: int,
    max_active: int,
    member_count: int,
    min_members: int,
) -> bool:
    if not signals_ready:
        return False
    if has_active_for_allegiance:
        return False
    if not cooldown_ready:
        return False
    if alive_total < min_population:
        return False
    if active_total >= max_active:
        return False
    if member_count < min_members:
        return False
    return True


def splinter_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    eligible: bool,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if not eligible:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def splinter_end_contract(
    *,
    anchor_active: bool,
    member_count: int,
    min_members: int,
    pressure_active: bool,
    now: float,
    ends_at: float,
) -> str:
    if not anchor_active:
        return "faded"
    if member_count < min_members:
        return "faded"
    if now >= ends_at:
        return "faded" if pressure_active else "resolved"
    return "active"


def splinter_local_effect_contract(
    *,
    in_cluster: bool,
    rally_bonus_active: bool,
    suppress_roll: float,
    suppress_chance: float,
    engagement_score: float,
    engagement_boost: float,
    has_local_enemy: bool,
) -> tuple[bool, float]:
    next_bonus: bool = rally_bonus_active
    next_score: float = engagement_score
    if in_cluster and rally_bonus_active and suppress_roll <= suppress_chance:
        next_bonus = False
    if in_cluster and has_local_enemy:
        next_score += engagement_boost
    return next_bonus, next_score


class TestGame3DSplintersBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"SPLINTER_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"SPLINTER_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"SPLINTER_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"SPLINTER_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.allegiance_cooldown = _extract_float(
            self.loop_content,
            r"SPLINTER_ALLEGIANCE_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"SPLINTER_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"SPLINTER_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"SPLINTER_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"SPLINTER_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.min_members = _extract_int(
            self.loop_content,
            r"SPLINTER_MIN_MEMBERS:\s*int\s*=\s*([0-9]+)",
        )
        self.max_members = _extract_int(
            self.loop_content,
            r"SPLINTER_MAX_MEMBERS:\s*int\s*=\s*([0-9]+)",
        )
        self.member_radius = _extract_float(
            self.loop_content,
            r"SPLINTER_MEMBER_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.rally_suppress = _extract_float(
            self.loop_content,
            r"SPLINTER_RALLY_SUPPRESS_CHANCE_PER_SEC:\s*float\s*=\s*([0-9.]+)",
        )
        self.leader_drift = _extract_float(
            self.loop_content,
            r"SPLINTER_LEADER_DRIFT_CHANCE_PER_SEC:\s*float\s*=\s*([0-9.]+)",
        )
        self.engagement_boost = _extract_float(
            self.loop_content,
            r"SPLINTER_RIVALRY_ENGAGEMENT_BOOST:\s*float\s*=\s*([0-9.]+)",
        )

    def test_splinter_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 70.0)
        self.assertLessEqual(self.start_delay, 260.0)
        self.assertGreaterEqual(self.check_interval, 1.6)
        self.assertLessEqual(self.check_interval, 8.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.30)
        self.assertGreaterEqual(self.global_cooldown, 16.0)
        self.assertLessEqual(self.global_cooldown, 120.0)
        self.assertGreaterEqual(self.allegiance_cooldown, 30.0)
        self.assertLessEqual(self.allegiance_cooldown, 150.0)
        self.assertGreaterEqual(self.duration_min, 10.0)
        self.assertLessEqual(self.duration_min, 40.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 45.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 2)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 22)
        self.assertGreaterEqual(self.min_members, 2)
        self.assertLessEqual(self.min_members, 4)
        self.assertGreaterEqual(self.max_members, self.min_members)
        self.assertLessEqual(self.max_members, 8)
        self.assertGreater(self.member_radius, 4.0)
        self.assertLessEqual(self.member_radius, 14.0)
        self.assertGreater(self.rally_suppress, 0.0)
        self.assertLessEqual(self.rally_suppress, 0.35)
        self.assertGreater(self.leader_drift, 0.0)
        self.assertLessEqual(self.leader_drift, 0.25)
        self.assertGreater(self.engagement_boost, 0.0)
        self.assertLessEqual(self.engagement_boost, 0.30)

    def test_trigger_contract_is_bounded_and_unique_per_allegiance(self):
        self.assertTrue(
            splinter_candidate_contract(
                signals_ready=True,
                has_active_for_allegiance=False,
                cooldown_ready=True,
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                member_count=self.min_members + 1,
                min_members=self.min_members,
            )
        )
        self.assertFalse(
            splinter_candidate_contract(
                signals_ready=True,
                has_active_for_allegiance=True,
                cooldown_ready=True,
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                member_count=self.min_members + 1,
                min_members=self.min_members,
            )
        )
        self.assertFalse(
            splinter_candidate_contract(
                signals_ready=False,
                has_active_for_allegiance=False,
                cooldown_ready=True,
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                member_count=self.min_members + 1,
                min_members=self.min_members,
            )
        )

        cooldown_left, started = splinter_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            eligible=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

    def test_non_trigger_when_signals_are_insufficient(self):
        _cooldown_left, started = splinter_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            eligible=False,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_end_resolution_and_fade_are_clean(self):
        self.assertEqual(
            splinter_end_contract(
                anchor_active=True,
                member_count=self.min_members,
                min_members=self.min_members,
                pressure_active=False,
                now=6.0,
                ends_at=18.0,
            ),
            "active",
        )
        self.assertEqual(
            splinter_end_contract(
                anchor_active=True,
                member_count=self.min_members,
                min_members=self.min_members,
                pressure_active=False,
                now=22.0,
                ends_at=18.0,
            ),
            "resolved",
        )
        self.assertEqual(
            splinter_end_contract(
                anchor_active=True,
                member_count=self.min_members,
                min_members=self.min_members,
                pressure_active=True,
                now=22.0,
                ends_at=18.0,
            ),
            "faded",
        )
        self.assertEqual(
            splinter_end_contract(
                anchor_active=False,
                member_count=self.min_members,
                min_members=self.min_members,
                pressure_active=True,
                now=8.0,
                ends_at=18.0,
            ),
            "faded",
        )

    def test_local_bias_is_light_but_real(self):
        boosted = splinter_local_effect_contract(
            in_cluster=True,
            rally_bonus_active=True,
            suppress_roll=0.0,
            suppress_chance=self.rally_suppress,
            engagement_score=1.0,
            engagement_boost=self.engagement_boost,
            has_local_enemy=True,
        )
        self.assertFalse(boosted[0])
        self.assertGreater(boosted[1], 1.0)

        neutral = splinter_local_effect_contract(
            in_cluster=False,
            rally_bonus_active=True,
            suppress_roll=0.0,
            suppress_chance=self.rally_suppress,
            engagement_score=1.0,
            engagement_boost=self.engagement_boost,
            has_local_enemy=True,
        )
        self.assertTrue(neutral[0])
        self.assertEqual(neutral[1], 1.0)

    def test_hooks_exist_across_runtime_hud_actor_and_docs(self):
        self.assertIn("_setup_splinter_state", self.loop_content)
        self.assertIn("_update_splinters", self.loop_content)
        self.assertIn("_build_splinter_candidate", self.loop_content)
        self.assertIn("_start_splinter", self.loop_content)
        self.assertIn("_end_splinter", self.loop_content)
        self.assertIn("Splinter START", self.loop_content)
        self.assertIn("Splinter END", self.loop_content)
        self.assertIn("Splinter RESOLVED", self.loop_content)
        self.assertIn("Splinter FADED", self.loop_content)
        self.assertIn('"splinter_active_total"', self.loop_content)
        self.assertIn('"splinter_active_labels"', self.loop_content)

        self.assertIn("splinter_active", self.actor_content)
        self.assertIn("set_splinter_state", self.actor_content)
        self.assertIn("splinter_tag", self.actor_content)

        self.assertIn("Splinters:", self.overlay_content)
        self.assertIn("Splinter groups:", self.overlay_content)

        self.assertIn("splinter", self.readme_content)
        self.assertIn("breakaway", self.readme_content)


if __name__ == "__main__":
    unittest.main()
