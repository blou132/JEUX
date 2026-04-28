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


def classify_marked_zone_contract(
    *,
    source_type: str,
    heroic_count: int,
    corrupted_count: int,
    gate_pressure: bool,
) -> str:
    if source_type == "memorial_site" and heroic_count > 0:
        return "sanctified_zone"
    if source_type == "scar_site" and (corrupted_count > 0 or gate_pressure):
        return "corrupted_zone"
    return ""


def marked_zone_spawn_step_contract(
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


def marked_zone_fade_contract(
    *,
    source_active: bool,
    now: float,
    ends_at: float,
) -> str:
    if not source_active:
        return "faded_source_lost"
    if now >= ends_at:
        return "faded_duration"
    return "active"


def marked_zone_local_effect_contract(
    *,
    zone_type: str,
    actor_faction: str,
    in_zone: bool,
    energy: float,
    energy_pulse: float,
    renown: float,
    renown_pulse: float,
    notoriety: float,
    notoriety_pulse: float,
) -> tuple[float, float, float]:
    if not in_zone:
        return energy, renown, notoriety
    if zone_type == "sanctified_zone" and actor_faction == "human":
        return energy + energy_pulse, renown + renown_pulse, notoriety
    if zone_type == "corrupted_zone":
        if actor_faction == "human":
            return energy - energy_pulse, renown, notoriety
        if actor_faction == "monster":
            return energy, renown, notoriety + notoriety_pulse
    return energy, renown, notoriety


class TestGame3DMarkedZonesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"MARKED_ZONE_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"MARKED_ZONE_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"MARKED_ZONE_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.sanctified_energy_pulse = _extract_float(
            self.loop_content,
            r"SANCTIFIED_ZONE_ENERGY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.sanctified_renown_pulse = _extract_float(
            self.loop_content,
            r"SANCTIFIED_ZONE_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.corrupted_energy_drain = _extract_float(
            self.loop_content,
            r"CORRUPTED_ZONE_ENERGY_DRAIN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.corrupted_notoriety_pulse = _extract_float(
            self.loop_content,
            r"CORRUPTED_ZONE_NOTORIETY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )

    def test_marked_zone_constants_are_rare_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 40.0)
        self.assertLessEqual(self.start_delay, 180.0)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.35)
        self.assertGreaterEqual(self.global_cooldown, 20.0)
        self.assertLessEqual(self.global_cooldown, 90.0)
        self.assertGreaterEqual(self.duration_min, 10.0)
        self.assertLessEqual(self.duration_min, 36.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 44.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.radius, 3.0)
        self.assertLessEqual(self.radius, 14.0)
        self.assertGreater(self.sanctified_energy_pulse, 0.0)
        self.assertLessEqual(self.sanctified_energy_pulse, 0.5)
        self.assertGreater(self.sanctified_renown_pulse, 0.0)
        self.assertLessEqual(self.sanctified_renown_pulse, 0.15)
        self.assertGreater(self.corrupted_energy_drain, 0.0)
        self.assertLessEqual(self.corrupted_energy_drain, 0.5)
        self.assertGreater(self.corrupted_notoriety_pulse, 0.0)
        self.assertLessEqual(self.corrupted_notoriety_pulse, 0.18)

    def test_classification_uses_safe_existing_signals(self):
        self.assertEqual(
            classify_marked_zone_contract(
                source_type="memorial_site",
                heroic_count=1,
                corrupted_count=0,
                gate_pressure=False,
            ),
            "sanctified_zone",
        )
        self.assertEqual(
            classify_marked_zone_contract(
                source_type="scar_site",
                heroic_count=0,
                corrupted_count=1,
                gate_pressure=False,
            ),
            "corrupted_zone",
        )
        self.assertEqual(
            classify_marked_zone_contract(
                source_type="scar_site",
                heroic_count=0,
                corrupted_count=0,
                gate_pressure=True,
            ),
            "corrupted_zone",
        )
        self.assertEqual(
            classify_marked_zone_contract(
                source_type="memorial_site",
                heroic_count=0,
                corrupted_count=0,
                gate_pressure=False,
            ),
            "",
        )

    def test_spawn_step_enforces_cap_and_rarity(self):
        cooldown_left, started = marked_zone_spawn_step_contract(
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

        _cooldown_left, started = marked_zone_spawn_step_contract(
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

        _cooldown_left, started = marked_zone_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=False,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_fade_contract_is_clean(self):
        self.assertEqual(
            marked_zone_fade_contract(source_active=True, now=12.0, ends_at=20.0),
            "active",
        )
        self.assertEqual(
            marked_zone_fade_contract(source_active=True, now=21.0, ends_at=20.0),
            "faded_duration",
        )
        self.assertEqual(
            marked_zone_fade_contract(source_active=False, now=12.0, ends_at=20.0),
            "faded_source_lost",
        )

    def test_local_effects_are_light_and_real(self):
        s_in = marked_zone_local_effect_contract(
            zone_type="sanctified_zone",
            actor_faction="human",
            in_zone=True,
            energy=10.0,
            energy_pulse=self.sanctified_energy_pulse,
            renown=8.0,
            renown_pulse=self.sanctified_renown_pulse,
            notoriety=4.0,
            notoriety_pulse=self.corrupted_notoriety_pulse,
        )
        self.assertGreater(s_in[0], 10.0)
        self.assertGreater(s_in[1], 8.0)

        c_in_human = marked_zone_local_effect_contract(
            zone_type="corrupted_zone",
            actor_faction="human",
            in_zone=True,
            energy=10.0,
            energy_pulse=self.corrupted_energy_drain,
            renown=8.0,
            renown_pulse=self.sanctified_renown_pulse,
            notoriety=4.0,
            notoriety_pulse=self.corrupted_notoriety_pulse,
        )
        self.assertLess(c_in_human[0], 10.0)

        c_in_monster = marked_zone_local_effect_contract(
            zone_type="corrupted_zone",
            actor_faction="monster",
            in_zone=True,
            energy=10.0,
            energy_pulse=self.corrupted_energy_drain,
            renown=8.0,
            renown_pulse=self.sanctified_renown_pulse,
            notoriety=4.0,
            notoriety_pulse=self.corrupted_notoriety_pulse,
        )
        self.assertGreater(c_in_monster[2], 4.0)

    def test_hooks_exist_across_runtime_hud_and_docs(self):
        self.assertIn("_setup_marked_zone_state", self.loop_content)
        self.assertIn("_update_marked_zones", self.loop_content)
        self.assertIn("_build_marked_zone_candidate", self.loop_content)
        self.assertIn("_apply_marked_zone_pulse", self.loop_content)
        self.assertIn("Zone SANCTIFIED", self.loop_content)
        self.assertIn("Zone CORRUPTED", self.loop_content)
        self.assertIn("Zone FADED", self.loop_content)
        self.assertIn('"marked_zone_active_total"', self.loop_content)
        self.assertIn('"marked_zone_active_labels"', self.loop_content)

        self.assertIn("Marked zones:", self.overlay_content)
        self.assertIn("Marked zone labels:", self.overlay_content)
        self.assertIn("sanctified", self.readme_content)
        self.assertIn("corrupted", self.readme_content)
        self.assertIn("zone faded", self.readme_content)


if __name__ == "__main__":
    unittest.main()
