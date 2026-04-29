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


def echo_start_contract(
    *,
    alive_total: int,
    min_population: int,
    global_cooldown_left: float,
    active_total: int,
    max_active: int,
    trigger_roll: float,
    trigger_chance: float,
) -> bool:
    if alive_total < min_population:
        return False
    if global_cooldown_left > 0.0:
        return False
    if active_total >= max_active:
        return False
    return trigger_roll <= trigger_chance


def echo_end_contract(*, now: float, ends_at: float) -> str:
    if now >= ends_at:
        return "faded_duration"
    return "active"


def echo_effect_contract(
    *,
    echo_type: str,
    in_radius: bool,
    renown: float,
    notoriety: float,
    renown_pulse: float,
    notoriety_pulse: float,
) -> dict[str, float]:
    if not in_radius:
        return {
            "renown": renown,
            "notoriety": notoriety,
        }

    if echo_type == "heroic_echo":
        return {
            "renown": renown + renown_pulse,
            "notoriety": notoriety,
        }
    if echo_type == "dark_aftershock":
        return {
            "renown": renown,
            "notoriety": notoriety + notoriety_pulse,
        }
    return {
        "renown": renown,
        "notoriety": notoriety,
    }


class TestGame3DEchoesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"ECHO_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"ECHO_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"ECHO_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"ECHO_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"ECHO_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"ECHO_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.start_base = _extract_float(
            self.loop_content,
            r"ECHO_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"ECHO_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.pulse_interval = _extract_float(
            self.loop_content,
            r"ECHO_PULSE_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.renown_pulse = _extract_float(
            self.loop_content,
            r"ECHO_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.notoriety_pulse = _extract_float(
            self.loop_content,
            r"ECHO_NOTORIETY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_echo_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 120.0)
        self.assertLessEqual(self.start_delay, 340.0)
        self.assertGreaterEqual(self.global_cooldown, 8.0)
        self.assertLessEqual(self.global_cooldown, 44.0)
        self.assertGreaterEqual(self.duration_min, 6.0)
        self.assertLessEqual(self.duration_min, 20.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 24.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreaterEqual(self.start_base, 0.10)
        self.assertLessEqual(self.start_base, 0.44)
        self.assertGreaterEqual(self.radius, 4.0)
        self.assertLessEqual(self.radius, 12.5)
        self.assertGreaterEqual(self.pulse_interval, 1.5)
        self.assertLessEqual(self.pulse_interval, 4.8)
        self.assertGreater(self.renown_pulse, 0.0)
        self.assertLessEqual(self.renown_pulse, 0.20)
        self.assertGreater(self.notoriety_pulse, 0.0)
        self.assertLessEqual(self.notoriety_pulse, 0.20)

    def test_start_contract_enforces_cap_cooldown_and_rarity(self):
        self.assertFalse(
            echo_start_contract(
                alive_total=self.min_population - 1,
                min_population=self.min_population,
                global_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            echo_start_contract(
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                global_cooldown_left=self.global_cooldown,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            echo_start_contract(
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                global_cooldown_left=0.0,
                active_total=self.max_active,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertTrue(
            echo_start_contract(
                alive_total=self.min_population + 2,
                min_population=self.min_population,
                global_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.08,
                trigger_chance=min(0.82, self.start_base + 0.10),
            )
        )

    def test_end_contract_is_clean(self):
        self.assertEqual(echo_end_contract(now=8.0, ends_at=12.0), "active")
        self.assertEqual(echo_end_contract(now=12.0, ends_at=12.0), "faded_duration")

    def test_effect_is_local_light_and_real(self):
        heroic = echo_effect_contract(
            echo_type="heroic_echo",
            in_radius=True,
            renown=40.0,
            notoriety=18.0,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
        )
        self.assertGreater(heroic["renown"], 40.0)
        self.assertEqual(heroic["notoriety"], 18.0)

        dark = echo_effect_contract(
            echo_type="dark_aftershock",
            in_radius=True,
            renown=40.0,
            notoriety=18.0,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
        )
        self.assertEqual(dark["renown"], 40.0)
        self.assertGreater(dark["notoriety"], 18.0)

        outside = echo_effect_contract(
            echo_type="heroic_echo",
            in_radius=False,
            renown=40.0,
            notoriety=18.0,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
        )
        self.assertEqual(outside["renown"], 40.0)
        self.assertEqual(outside["notoriety"], 18.0)

    def test_hooks_exist_across_runtime_hud_and_docs(self):
        self.assertIn("_setup_echo_state", self.loop_content)
        self.assertIn("_update_echo_runtime", self.loop_content)
        self.assertIn("_try_start_echo(", self.loop_content)
        self.assertIn("_fade_echo", self.loop_content)
        self.assertIn("_apply_echo_pulse", self.loop_content)
        self.assertIn("Echo START", self.loop_content)
        self.assertIn("Echo END", self.loop_content)
        self.assertIn("Echo FADED", self.loop_content)
        self.assertIn('"echo_active_count"', self.loop_content)
        self.assertIn('"echo_active_labels"', self.loop_content)

        self.assertIn("convergence_end", self.loop_content)
        self.assertIn("rivalry_resolved", self.loop_content)
        self.assertIn("notable_fall", self.loop_content)
        self.assertIn("rift_gate_breach", self.loop_content)
        self.assertIn("crisis_resolved", self.loop_content)
        self.assertIn("oath_fulfilled:", self.loop_content)

        self.assertIn("Echoes:", self.overlay_content)
        self.assertIn("Echo labels:", self.overlay_content)

        self.assertIn("echo", self.readme_content)
        self.assertIn("aftershock", self.readme_content)


if __name__ == "__main__":
    unittest.main()
