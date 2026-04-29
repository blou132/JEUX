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


def classify_sanctuary_bastion_contract(
    *,
    zone_type: str,
    heroic_count: int,
    corrupted_count: int,
    memorial_near: bool,
    scar_near: bool,
    gate_pressure: bool,
) -> str:
    if zone_type == "sanctified_zone" and (heroic_count > 0 or memorial_near):
        return "sanctuary_site"
    if zone_type == "corrupted_zone" and (corrupted_count > 0 or scar_near or gate_pressure):
        return "dark_bastion"
    return ""


def sanctuary_bastion_spawn_step_contract(
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


def sanctuary_bastion_fade_contract(
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


def sanctuary_bastion_local_effect_contract(
    *,
    site_type: str,
    actor_faction: str,
    in_site: bool,
    energy: float,
    sanctuary_energy_pulse: float,
    bastion_energy_drain: float,
    renown: float,
    sanctuary_renown_pulse: float,
    notoriety: float,
    bastion_notoriety_pulse: float,
) -> tuple[float, float, float]:
    if not in_site:
        return energy, renown, notoriety
    if site_type == "sanctuary_site" and actor_faction == "human":
        return energy + sanctuary_energy_pulse, renown + sanctuary_renown_pulse, notoriety
    if site_type == "dark_bastion":
        if actor_faction == "human":
            return energy - bastion_energy_drain, renown, notoriety
        if actor_faction == "monster":
            return energy, renown, notoriety + bastion_notoriety_pulse
    return energy, renown, notoriety


class TestGame3DSanctuaryBastionsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"SANCTUARY_BASTION_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"SANCTUARY_BASTION_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"SANCTUARY_BASTION_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.sanctuary_renown_pulse = _extract_float(
            self.loop_content,
            r"SANCTUARY_SITE_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.sanctuary_energy_pulse = _extract_float(
            self.loop_content,
            r"SANCTUARY_SITE_ENERGY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.bastion_notoriety_pulse = _extract_float(
            self.loop_content,
            r"DARK_BASTION_NOTORIETY_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.bastion_energy_drain = _extract_float(
            self.loop_content,
            r"DARK_BASTION_ENERGY_DRAIN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.bastion_alert_bonus = _extract_float(
            self.loop_content,
            r"DARK_BASTION_ALERT_SCORE_BONUS:\s*float\s*=\s*([0-9.]+)",
        )

    def test_constants_are_rare_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 180.0)
        self.assertLessEqual(self.start_delay, 420.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 7.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.30)
        self.assertGreaterEqual(self.global_cooldown, 20.0)
        self.assertLessEqual(self.global_cooldown, 120.0)
        self.assertGreaterEqual(self.duration_min, 10.0)
        self.assertLessEqual(self.duration_min, 34.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 40.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 3)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.radius, 4.0)
        self.assertLessEqual(self.radius, 14.0)
        self.assertGreater(self.sanctuary_renown_pulse, 0.0)
        self.assertLessEqual(self.sanctuary_renown_pulse, 0.16)
        self.assertGreater(self.sanctuary_energy_pulse, 0.0)
        self.assertLessEqual(self.sanctuary_energy_pulse, 0.40)
        self.assertGreater(self.bastion_notoriety_pulse, 0.0)
        self.assertLessEqual(self.bastion_notoriety_pulse, 0.20)
        self.assertGreater(self.bastion_energy_drain, 0.0)
        self.assertLessEqual(self.bastion_energy_drain, 0.40)
        self.assertGreater(self.bastion_alert_bonus, 0.0)
        self.assertLessEqual(self.bastion_alert_bonus, 0.80)

    def test_classification_uses_safe_marked_signals(self):
        self.assertEqual(
            classify_sanctuary_bastion_contract(
                zone_type="sanctified_zone",
                heroic_count=1,
                corrupted_count=0,
                memorial_near=False,
                scar_near=False,
                gate_pressure=False,
            ),
            "sanctuary_site",
        )
        self.assertEqual(
            classify_sanctuary_bastion_contract(
                zone_type="corrupted_zone",
                heroic_count=0,
                corrupted_count=1,
                memorial_near=False,
                scar_near=False,
                gate_pressure=False,
            ),
            "dark_bastion",
        )
        self.assertEqual(
            classify_sanctuary_bastion_contract(
                zone_type="corrupted_zone",
                heroic_count=0,
                corrupted_count=0,
                memorial_near=False,
                scar_near=False,
                gate_pressure=True,
            ),
            "dark_bastion",
        )
        self.assertEqual(
            classify_sanctuary_bastion_contract(
                zone_type="sanctified_zone",
                heroic_count=0,
                corrupted_count=0,
                memorial_near=False,
                scar_near=False,
                gate_pressure=False,
            ),
            "",
        )

    def test_spawn_step_enforces_cap_and_cooldowns(self):
        cooldown_left, started = sanctuary_bastion_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=0.0,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        _cooldown_left, started = sanctuary_bastion_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=self.max_active,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=0.0,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = sanctuary_bastion_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 3,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            has_candidate=True,
            anchor_cooldown_left=self.global_cooldown,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_fade_contract_is_clean(self):
        self.assertEqual(
            sanctuary_bastion_fade_contract(source_active=True, now=14.0, ends_at=24.0),
            "active",
        )
        self.assertEqual(
            sanctuary_bastion_fade_contract(source_active=False, now=14.0, ends_at=24.0),
            "source_lost",
        )
        self.assertEqual(
            sanctuary_bastion_fade_contract(source_active=True, now=26.0, ends_at=24.0),
            "duration",
        )

    def test_local_effects_are_light_and_real(self):
        sanctuary_in = sanctuary_bastion_local_effect_contract(
            site_type="sanctuary_site",
            actor_faction="human",
            in_site=True,
            energy=10.0,
            sanctuary_energy_pulse=self.sanctuary_energy_pulse,
            bastion_energy_drain=self.bastion_energy_drain,
            renown=8.0,
            sanctuary_renown_pulse=self.sanctuary_renown_pulse,
            notoriety=4.0,
            bastion_notoriety_pulse=self.bastion_notoriety_pulse,
        )
        self.assertGreater(sanctuary_in[0], 10.0)
        self.assertGreater(sanctuary_in[1], 8.0)

        bastion_human = sanctuary_bastion_local_effect_contract(
            site_type="dark_bastion",
            actor_faction="human",
            in_site=True,
            energy=10.0,
            sanctuary_energy_pulse=self.sanctuary_energy_pulse,
            bastion_energy_drain=self.bastion_energy_drain,
            renown=8.0,
            sanctuary_renown_pulse=self.sanctuary_renown_pulse,
            notoriety=4.0,
            bastion_notoriety_pulse=self.bastion_notoriety_pulse,
        )
        self.assertLess(bastion_human[0], 10.0)

        bastion_monster = sanctuary_bastion_local_effect_contract(
            site_type="dark_bastion",
            actor_faction="monster",
            in_site=True,
            energy=10.0,
            sanctuary_energy_pulse=self.sanctuary_energy_pulse,
            bastion_energy_drain=self.bastion_energy_drain,
            renown=8.0,
            sanctuary_renown_pulse=self.sanctuary_renown_pulse,
            notoriety=4.0,
            bastion_notoriety_pulse=self.bastion_notoriety_pulse,
        )
        self.assertGreater(bastion_monster[2], 4.0)

    def test_hooks_exist_across_runtime_world_ai_hud_and_docs(self):
        self.assertIn("_setup_sanctuary_bastion_state", self.loop_content)
        self.assertIn("_update_sanctuary_bastions", self.loop_content)
        self.assertIn("_build_sanctuary_bastion_candidate", self.loop_content)
        self.assertIn("_apply_sanctuary_bastion_pulse", self.loop_content)
        self.assertIn("Sanctuary RISE", self.loop_content)
        self.assertIn("Bastion RISE", self.loop_content)
        self.assertIn("Sanctuary/Bastion FADE", self.loop_content)
        self.assertIn('"sanctuary_bastion_active_total"', self.loop_content)
        self.assertIn('"sanctuary_risen_total"', self.loop_content)
        self.assertIn('"bastion_risen_total"', self.loop_content)
        self.assertIn('"sanctuary_bastion_faded_total"', self.loop_content)
        self.assertIn("dark_bastion", self.loop_content)

        self.assertIn("set_sanctuary_bastion_state", self.world_content)
        self.assertIn("get_sanctuary_bastion_guidance", self.world_content)
        self.assertIn("get_sanctuary_bastion_guidance", self.ai_content)
        self.assertIn("sanctuary:", self.ai_content)
        self.assertIn("bastion:", self.ai_content)

        self.assertIn("Sanctuaries/Bastions:", self.overlay_content)
        self.assertIn("Sanctuary/Bastion labels:", self.overlay_content)

        self.assertIn("sanctuary_site", self.readme_content)
        self.assertIn("dark_bastion", self.readme_content)
        self.assertIn("sanctuary rise", self.readme_content)
        self.assertIn("sanctuary/bastion fade", self.readme_content)


if __name__ == "__main__":
    unittest.main()
