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


def alert_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    active_total: int,
    max_active: int,
    anchor_active: bool,
    allegiance_cooldown_left: float,
    signal_score: float,
    min_signal_score: float,
    trigger_roll: float,
    trigger_chance: float,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if active_total >= max_active:
        return global_cooldown_left, False
    if not anchor_active:
        return global_cooldown_left, False
    if allegiance_cooldown_left > 0.0:
        return global_cooldown_left, False
    if signal_score < min_signal_score:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def alert_end_contract(
    *,
    anchor_active: bool,
    now: float,
    ends_at: float,
) -> str:
    if not anchor_active:
        return "anchor_lost"
    if now >= ends_at:
        return "duration_complete"
    return "active"


def alert_effect_contract(
    *,
    alert_active: bool,
    defense_weight: float,
    defense_delta: float,
    offense_weight: float,
    offense_delta: float,
    expedition_start_chance: float,
    expedition_start_mult: float,
) -> dict:
    if not alert_active:
        return {
            "defense_weight": defense_weight,
            "offense_weight": offense_weight,
            "expedition_start_chance": expedition_start_chance,
        }

    return {
        "defense_weight": min(0.92, defense_weight + defense_delta),
        "offense_weight": max(0.24, offense_weight + offense_delta),
        "expedition_start_chance": max(0.06, expedition_start_chance * expedition_start_mult),
    }


class TestGame3DAlertPulsesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"ALERT_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"ALERT_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.start_chance_base = _extract_float(
            self.loop_content,
            r"ALERT_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"ALERT_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.allegiance_cooldown = _extract_float(
            self.loop_content,
            r"ALERT_ALLEGIANCE_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"ALERT_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"ALERT_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"ALERT_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"ALERT_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.signal_radius = _extract_float(
            self.loop_content,
            r"ALERT_SIGNAL_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.signal_radius_gate = _extract_float(
            self.loop_content,
            r"ALERT_SIGNAL_RADIUS_GATE:\s*float\s*=\s*([0-9.]+)",
        )
        self.defense_delta = _extract_float(
            self.loop_content,
            r"ALERT_DEFENSE_WEIGHT_DELTA:\s*float\s*=\s*([0-9.]+)",
        )
        self.offense_delta = _extract_float(
            self.loop_content,
            r"ALERT_OFFENSE_WEIGHT_DELTA:\s*float\s*=\s*(-?[0-9.]+)",
        )
        self.expedition_mult = _extract_float(
            self.loop_content,
            r"ALERT_EXPEDITION_START_MULT:\s*float\s*=\s*([0-9.]+)",
        )

    def test_alert_constants_are_rare_short_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 140.0)
        self.assertLessEqual(self.start_delay, 360.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.start_chance_base, 0.08)
        self.assertLessEqual(self.start_chance_base, 0.45)
        self.assertGreaterEqual(self.global_cooldown, 4.0)
        self.assertLessEqual(self.global_cooldown, 24.0)
        self.assertGreaterEqual(self.allegiance_cooldown, 12.0)
        self.assertLessEqual(self.allegiance_cooldown, 64.0)
        self.assertGreaterEqual(self.duration_min, 5.0)
        self.assertLessEqual(self.duration_min, 16.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 24.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.signal_radius, 7.0)
        self.assertLessEqual(self.signal_radius, 18.0)
        self.assertGreaterEqual(self.signal_radius_gate, self.signal_radius)
        self.assertLessEqual(self.signal_radius_gate, 24.0)
        self.assertGreater(self.defense_delta, 0.02)
        self.assertLessEqual(self.defense_delta, 0.16)
        self.assertLess(self.offense_delta, 0.0)
        self.assertGreaterEqual(self.offense_delta, -0.16)
        self.assertGreaterEqual(self.expedition_mult, 0.55)
        self.assertLessEqual(self.expedition_mult, 0.95)

    def test_trigger_contract_enforces_cap_cooldowns_and_signals(self):
        _cooldown_left, started = alert_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            active_total=0,
            max_active=self.max_active,
            anchor_active=True,
            allegiance_cooldown_left=0.0,
            signal_score=1.4,
            min_signal_score=1.0,
            trigger_roll=0.10,
            trigger_chance=min(0.62, self.start_chance_base + 0.20),
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)

        _cooldown_left, started = alert_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            active_total=self.max_active,
            max_active=self.max_active,
            anchor_active=True,
            allegiance_cooldown_left=0.0,
            signal_score=1.4,
            min_signal_score=1.0,
            trigger_roll=0.10,
            trigger_chance=min(0.62, self.start_chance_base + 0.20),
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = alert_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            active_total=0,
            max_active=self.max_active,
            anchor_active=True,
            allegiance_cooldown_left=self.allegiance_cooldown,
            signal_score=1.4,
            min_signal_score=1.0,
            trigger_roll=0.10,
            trigger_chance=min(0.62, self.start_chance_base + 0.20),
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = alert_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            active_total=0,
            max_active=self.max_active,
            anchor_active=True,
            allegiance_cooldown_left=0.0,
            signal_score=0.6,
            min_signal_score=1.0,
            trigger_roll=0.10,
            trigger_chance=min(0.62, self.start_chance_base + 0.20),
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_end_contract_is_clean(self):
        self.assertEqual(
            alert_end_contract(anchor_active=True, now=8.0, ends_at=16.0),
            "active",
        )
        self.assertEqual(
            alert_end_contract(anchor_active=False, now=8.0, ends_at=16.0),
            "anchor_lost",
        )
        self.assertEqual(
            alert_end_contract(anchor_active=True, now=18.0, ends_at=16.0),
            "duration_complete",
        )

    def test_effects_are_light_and_real(self):
        active = alert_effect_contract(
            alert_active=True,
            defense_weight=0.66,
            defense_delta=self.defense_delta,
            offense_weight=0.72,
            offense_delta=self.offense_delta,
            expedition_start_chance=0.30,
            expedition_start_mult=self.expedition_mult,
        )
        self.assertGreater(active["defense_weight"], 0.66)
        self.assertLess(active["offense_weight"], 0.72)
        self.assertLess(active["expedition_start_chance"], 0.30)

        inactive = alert_effect_contract(
            alert_active=False,
            defense_weight=0.66,
            defense_delta=self.defense_delta,
            offense_weight=0.72,
            offense_delta=self.offense_delta,
            expedition_start_chance=0.30,
            expedition_start_mult=self.expedition_mult,
        )
        self.assertEqual(inactive["defense_weight"], 0.66)
        self.assertEqual(inactive["offense_weight"], 0.72)
        self.assertEqual(inactive["expedition_start_chance"], 0.30)

    def test_hooks_exist_across_runtime_world_ai_hud_and_docs(self):
        self.assertIn("_setup_alert_state", self.loop_content)
        self.assertIn("_update_alert_pulses", self.loop_content)
        self.assertIn("_build_alert_candidate", self.loop_content)
        self.assertIn("_collect_alert_signal_context", self.loop_content)
        self.assertIn("Alert START", self.loop_content)
        self.assertIn("Alert END", self.loop_content)
        self.assertIn('"alert_active_count"', self.loop_content)
        self.assertIn('"alert_started_total"', self.loop_content)
        self.assertIn('"alert_ended_total"', self.loop_content)

        self.assertIn("set_alert_state", self.world_content)
        self.assertIn("get_alert_guidance", self.world_content)
        self.assertIn("get_alert_defense_delta", self.world_content)
        self.assertIn("get_alert_offense_weight_delta", self.world_content)
        self.assertIn("get_alert_expedition_start_multiplier", self.world_content)

        self.assertIn("get_alert_guidance", self.ai_content)
        self.assertIn("alert:", self.ai_content)

        self.assertIn("Alerts:", self.overlay_content)
        self.assertIn("Alert labels:", self.overlay_content)
        self.assertIn("alert:", self.overlay_content)

        self.assertIn("alert pulse", self.readme_content)
        self.assertIn("alert start", self.readme_content)
        self.assertIn("alert end", self.readme_content)


if __name__ == "__main__":
    unittest.main()
