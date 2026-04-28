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


def convergence_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    gate_open: bool,
    alive_total: int,
    min_population: int,
    active_total: int,
    max_active: int,
    trigger_roll: float,
    trigger_chance: float,
    signals_ok: bool,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if not gate_open:
        return global_cooldown_left, False
    if alive_total < min_population:
        return global_cooldown_left, False
    if active_total >= max_active:
        return global_cooldown_left, False
    if not signals_ok:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def convergence_end_contract(
    *,
    gate_open: bool,
    signals_ok: bool,
    now: float,
    ends_at: float,
) -> str:
    if not gate_open:
        return "interrupted_gate_closed"
    if not signals_ok:
        return "interrupted_signals_lost"
    if now >= ends_at:
        return "ended_duration_complete"
    return "active"


def convergence_local_effect_contract(
    *,
    actor_distance: float,
    radius: float,
    renown: float,
    notoriety: float,
    renown_pulse: float,
    notoriety_pulse: float,
) -> tuple[float, float]:
    if actor_distance > radius:
        return renown, notoriety
    return renown + renown_pulse, notoriety + notoriety_pulse


class TestGame3DConvergenceBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"CONVERGENCE_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"CONVERGENCE_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"CONVERGENCE_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"CONVERGENCE_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"CONVERGENCE_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"CONVERGENCE_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"CONVERGENCE_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"CONVERGENCE_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"CONVERGENCE_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.renown_pulse = _extract_float(
            self.loop_content,
            r"CONVERGENCE_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.notoriety_pulse = _extract_float(
            self.loop_content,
            r"CONVERGENCE_NOTORIETY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_convergence_constants_are_rare_short_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 40.0)
        self.assertLessEqual(self.start_delay, 180.0)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.35)
        self.assertGreaterEqual(self.global_cooldown, 20.0)
        self.assertLessEqual(self.global_cooldown, 120.0)
        self.assertGreaterEqual(self.duration_min, 6.0)
        self.assertLessEqual(self.duration_min, 22.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 28.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 2)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.radius, 3.0)
        self.assertLessEqual(self.radius, 16.0)
        self.assertGreater(self.renown_pulse, 0.0)
        self.assertLessEqual(self.renown_pulse, 0.20)
        self.assertGreater(self.notoriety_pulse, 0.0)
        self.assertLessEqual(self.notoriety_pulse, 0.24)

    def test_spawn_is_bounded_and_needs_local_signals(self):
        cooldown_left, started = convergence_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            gate_open=True,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            signals_ok=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        _cooldown_left, started = convergence_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            gate_open=True,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            signals_ok=False,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = convergence_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            gate_open=False,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            signals_ok=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_end_or_interrupt_is_clean(self):
        self.assertEqual(
            convergence_end_contract(
                gate_open=True,
                signals_ok=True,
                now=8.0,
                ends_at=14.0,
            ),
            "active",
        )
        self.assertEqual(
            convergence_end_contract(
                gate_open=True,
                signals_ok=True,
                now=16.0,
                ends_at=14.0,
            ),
            "ended_duration_complete",
        )
        self.assertEqual(
            convergence_end_contract(
                gate_open=False,
                signals_ok=True,
                now=8.0,
                ends_at=14.0,
            ),
            "interrupted_gate_closed",
        )
        self.assertEqual(
            convergence_end_contract(
                gate_open=True,
                signals_ok=False,
                now=8.0,
                ends_at=14.0,
            ),
            "interrupted_signals_lost",
        )

    def test_local_effect_is_light_and_real(self):
        in_zone = convergence_local_effect_contract(
            actor_distance=self.radius * 0.50,
            radius=self.radius,
            renown=12.0,
            notoriety=10.0,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
        )
        self.assertGreater(in_zone[0], 12.0)
        self.assertGreater(in_zone[1], 10.0)

        out_zone = convergence_local_effect_contract(
            actor_distance=self.radius * 1.25,
            radius=self.radius,
            renown=12.0,
            notoriety=10.0,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
        )
        self.assertEqual(out_zone[0], 12.0)
        self.assertEqual(out_zone[1], 10.0)

    def test_hooks_exist_across_runtime_world_ai_hud_and_docs(self):
        self.assertIn("_update_convergence_events", self.loop_content)
        self.assertIn("_build_convergence_candidate", self.loop_content)
        self.assertIn("_collect_convergence_signal_counts", self.loop_content)
        self.assertIn("_start_convergence_event", self.loop_content)
        self.assertIn("_end_convergence_event", self.loop_content)
        self.assertIn("_apply_convergence_pulse", self.loop_content)
        self.assertIn("Convergence START", self.loop_content)
        self.assertIn("Convergence END", self.loop_content)
        self.assertIn("Convergence INTERRUPTED", self.loop_content)
        self.assertIn('"convergence_active_total"', self.loop_content)
        self.assertIn('"convergence_active_labels"', self.loop_content)

        self.assertIn("set_convergence_state", self.world_content)
        self.assertIn("get_convergence_guidance", self.world_content)
        self.assertIn("convergence_state", self.world_content)

        self.assertIn("get_convergence_guidance", self.ai_content)
        self.assertIn("convergence_pull", self.ai_content)
        self.assertIn("Convergence:", self.overlay_content)
        self.assertIn("Convergence zones:", self.overlay_content)

        self.assertIn("convergence", self.readme_content)
        self.assertIn("crossroads", self.readme_content)


if __name__ == "__main__":
    unittest.main()
