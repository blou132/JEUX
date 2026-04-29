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


def classify_taboo_contract(
    *,
    source_kind: str,
    scar_near: bool,
    duel_near: bool,
    gate_breach_near: bool,
) -> str:
    if source_kind == "sanctuary_site" and (scar_near or duel_near):
        return "forbidden_site"
    if source_kind in ["dark_bastion", "corrupted_zone"] and (scar_near or duel_near or gate_breach_near):
        return "cursed_warning"
    return ""


def taboo_spawn_step_contract(
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
    anchor_cooldown_left: float,
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
    if anchor_cooldown_left > 0.0:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def taboo_fade_contract(
    *,
    source_active: bool,
    now: float,
    ends_at: float,
) -> str:
    if not source_active:
        return "source_lost"
    if now >= ends_at:
        return "duration"
    return "active"


def taboo_avoidance_contract(
    *,
    taboo_type: str,
    actor_faction: str,
    prudent_profile: bool,
    distance: float,
    radius: float,
) -> bool:
    if distance > radius * 1.9:
        return False
    if taboo_type == "forbidden_site":
        return actor_faction == "human" or prudent_profile
    if taboo_type == "cursed_warning":
        return actor_faction == "human" or prudent_profile
    return False


def taboo_alert_effect_contract(
    *,
    taboo_near: bool,
    taboo_type: str,
    base_score: float,
    taboo_alert_bonus: float,
) -> float:
    if not taboo_near:
        return base_score
    if taboo_type == "forbidden_site":
        return base_score + taboo_alert_bonus * 0.72
    if taboo_type == "cursed_warning":
        return base_score + taboo_alert_bonus
    return base_score


class TestGame3DTaboosBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"TABOO_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"TABOO_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"TABOO_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"TABOO_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"TABOO_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"TABOO_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"TABOO_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"TABOO_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"TABOO_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.anchor_cooldown = _extract_float(
            self.loop_content,
            r"TABOO_ANCHOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.alert_bonus = _extract_float(
            self.loop_content,
            r"TABOO_ALERT_SCORE_BONUS:\s*float\s*=\s*([0-9.]+)",
        )

    def test_taboo_constants_are_rare_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 220.0)
        self.assertLessEqual(self.start_delay, 520.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 8.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.26)
        self.assertGreaterEqual(self.global_cooldown, 20.0)
        self.assertLessEqual(self.global_cooldown, 96.0)
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 30.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 36.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.radius, 4.0)
        self.assertLessEqual(self.radius, 14.0)
        self.assertGreaterEqual(self.anchor_cooldown, 24.0)
        self.assertLessEqual(self.anchor_cooldown, 120.0)
        self.assertGreater(self.alert_bonus, 0.0)
        self.assertLessEqual(self.alert_bonus, 0.42)

    def test_classification_uses_safe_existing_signals(self):
        self.assertEqual(
            classify_taboo_contract(
                source_kind="sanctuary_site",
                scar_near=True,
                duel_near=False,
                gate_breach_near=False,
            ),
            "forbidden_site",
        )
        self.assertEqual(
            classify_taboo_contract(
                source_kind="dark_bastion",
                scar_near=False,
                duel_near=True,
                gate_breach_near=False,
            ),
            "cursed_warning",
        )
        self.assertEqual(
            classify_taboo_contract(
                source_kind="corrupted_zone",
                scar_near=False,
                duel_near=False,
                gate_breach_near=True,
            ),
            "cursed_warning",
        )
        self.assertEqual(
            classify_taboo_contract(
                source_kind="sanctuary_site",
                scar_near=False,
                duel_near=False,
                gate_breach_near=False,
            ),
            "",
        )

    def test_spawn_contract_enforces_cap_and_cooldowns(self):
        cooldown_left, started = taboo_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=0.0,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        _cooldown_left, started = taboo_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=self.max_active,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=0.0,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = taboo_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=self.anchor_cooldown,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_fade_contract_is_clean(self):
        self.assertEqual(
            taboo_fade_contract(source_active=True, now=12.0, ends_at=20.0),
            "active",
        )
        self.assertEqual(
            taboo_fade_contract(source_active=False, now=12.0, ends_at=20.0),
            "source_lost",
        )
        self.assertEqual(
            taboo_fade_contract(source_active=True, now=22.0, ends_at=20.0),
            "duration",
        )

    def test_local_effects_are_light_and_real(self):
        self.assertTrue(
            taboo_avoidance_contract(
                taboo_type="forbidden_site",
                actor_faction="human",
                prudent_profile=True,
                distance=6.0,
                radius=self.radius,
            )
        )
        self.assertTrue(
            taboo_avoidance_contract(
                taboo_type="cursed_warning",
                actor_faction="monster",
                prudent_profile=True,
                distance=6.0,
                radius=self.radius,
            )
        )
        self.assertFalse(
            taboo_avoidance_contract(
                taboo_type="forbidden_site",
                actor_faction="monster",
                prudent_profile=False,
                distance=6.0,
                radius=self.radius,
            )
        )

        boosted = taboo_alert_effect_contract(
            taboo_near=True,
            taboo_type="cursed_warning",
            base_score=1.0,
            taboo_alert_bonus=self.alert_bonus,
        )
        self.assertGreater(boosted, 1.0)
        calm = taboo_alert_effect_contract(
            taboo_near=False,
            taboo_type="cursed_warning",
            base_score=1.0,
            taboo_alert_bonus=self.alert_bonus,
        )
        self.assertEqual(calm, 1.0)

    def test_hooks_exist_across_runtime_world_ai_hud_and_docs(self):
        self.assertIn("_setup_taboo_state", self.loop_content)
        self.assertIn("_update_taboos", self.loop_content)
        self.assertIn("_build_taboo_candidate", self.loop_content)
        self.assertIn("Taboo RISE", self.loop_content)
        self.assertIn("Taboo FADE", self.loop_content)
        self.assertIn('"taboo_active_total"', self.loop_content)
        self.assertIn('"taboo_risen_total"', self.loop_content)
        self.assertIn('"taboo_faded_total"', self.loop_content)

        self.assertIn("set_taboo_state", self.world_content)
        self.assertIn("get_taboo_avoidance_guidance", self.world_content)

        self.assertIn("get_taboo_avoidance_guidance", self.ai_content)
        self.assertIn("taboo:", self.ai_content)

        self.assertIn("Taboos:", self.overlay_content)
        self.assertIn("Taboo labels:", self.overlay_content)

        self.assertIn("taboo", self.readme_content)
        self.assertIn("forbidden_site", self.readme_content)
        self.assertIn("cursed_warning", self.readme_content)
        self.assertIn("taboo rise", self.readme_content)
        self.assertIn("taboo fade", self.readme_content)


if __name__ == "__main__":
    unittest.main()
