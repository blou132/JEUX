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


def destiny_candidate_contract(
    *,
    is_champion: bool,
    is_special_arrival: bool,
    has_relic: bool,
    is_successor: bool,
    renown: float,
    renown_trigger: float,
    bounty_marked: bool,
) -> bool:
    if bounty_marked:
        return False
    if is_champion or is_special_arrival or has_relic or is_successor:
        return True
    return renown >= renown_trigger


def destiny_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    alive_total: int,
    min_population: int,
    active_total: int,
    max_active: int,
    actor_has_active_pull: bool,
    actor_cooldown_ready: bool,
    has_option: bool,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if alive_total < min_population:
        return global_cooldown_left, False
    if active_total >= max_active:
        return global_cooldown_left, False
    if actor_has_active_pull or not actor_cooldown_ready:
        return global_cooldown_left, False
    if not has_option:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def destiny_end_step_contract(
    *,
    objective_valid: bool,
    near_time: float,
    delta: float,
    fulfill_hold: float,
    now: float,
    ends_at: float,
) -> tuple[float, str]:
    if not objective_valid:
        return max(0.0, near_time - delta), "interrupted"
    near_time += delta
    if near_time >= fulfill_hold:
        return near_time, "fulfilled"
    if now >= ends_at:
        return near_time, "timeout"
    return near_time, "active"


class TestGame3DDestinyBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"DESTINY_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"DESTINY_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.trigger_chance = _extract_float(
            self.loop_content,
            r"DESTINY_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"DESTINY_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.actor_cooldown = _extract_float(
            self.loop_content,
            r"DESTINY_ACTOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"DESTINY_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"DESTINY_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"DESTINY_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"DESTINY_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.renown_trigger = _extract_float(
            self.loop_content,
            r"DESTINY_HIGH_RENOWN_TRIGGER:\s*float\s*=\s*([0-9.]+)",
        )
        self.fulfill_hold = _extract_float(
            self.loop_content,
            r"DESTINY_FULFILL_HOLD:\s*float\s*=\s*([0-9.]+)",
        )
        self.near_energy_bonus = _extract_float(
            self.loop_content,
            r"DESTINY_NEAR_ENERGY_BONUS_PER_SEC:\s*float\s*=\s*([0-9.]+)",
        )

    def test_destiny_constants_are_rare_and_bounded(self):
        self.assertGreaterEqual(self.start_delay, 30.0)
        self.assertLessEqual(self.start_delay, 120.0)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.08)
        self.assertLessEqual(self.trigger_chance, 0.30)
        self.assertGreaterEqual(self.global_cooldown, 8.0)
        self.assertLessEqual(self.global_cooldown, 30.0)
        self.assertGreaterEqual(self.actor_cooldown, 20.0)
        self.assertLessEqual(self.actor_cooldown, 90.0)
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 24.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 30.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 6)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreaterEqual(self.renown_trigger, 50.0)
        self.assertLessEqual(self.renown_trigger, 80.0)
        self.assertGreater(self.fulfill_hold, 0.2)
        self.assertLessEqual(self.fulfill_hold, 4.0)
        self.assertGreater(self.near_energy_bonus, 0.0)
        self.assertLessEqual(self.near_energy_bonus, 0.35)

    def test_candidate_gate_uses_notable_signals_and_skips_marked(self):
        self.assertTrue(
            destiny_candidate_contract(
                is_champion=True,
                is_special_arrival=False,
                has_relic=False,
                is_successor=False,
                renown=12.0,
                renown_trigger=self.renown_trigger,
                bounty_marked=False,
            )
        )
        self.assertTrue(
            destiny_candidate_contract(
                is_champion=False,
                is_special_arrival=False,
                has_relic=False,
                is_successor=False,
                renown=self.renown_trigger + 2.0,
                renown_trigger=self.renown_trigger,
                bounty_marked=False,
            )
        )
        self.assertFalse(
            destiny_candidate_contract(
                is_champion=False,
                is_special_arrival=False,
                has_relic=False,
                is_successor=False,
                renown=self.renown_trigger - 20.0,
                renown_trigger=self.renown_trigger,
                bounty_marked=False,
            )
        )
        self.assertFalse(
            destiny_candidate_contract(
                is_champion=True,
                is_special_arrival=False,
                has_relic=False,
                is_successor=False,
                renown=80.0,
                renown_trigger=self.renown_trigger,
                bounty_marked=True,
            )
        )

    def test_spawn_step_enforces_uniqueness_and_bounds(self):
        cooldown_left, started = destiny_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            actor_has_active_pull=False,
            actor_cooldown_ready=True,
            has_option=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

        _cooldown_left, started = destiny_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            actor_has_active_pull=True,
            actor_cooldown_ready=True,
            has_option=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = destiny_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=self.max_active,
            max_active=self.max_active,
            actor_has_active_pull=False,
            actor_cooldown_ready=True,
            has_option=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

        _cooldown_left, started = destiny_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=self.check_interval,
            trigger_roll=0.0,
            trigger_chance=self.trigger_chance,
            alive_total=self.min_population + 2,
            min_population=self.min_population,
            active_total=0,
            max_active=self.max_active,
            actor_has_active_pull=False,
            actor_cooldown_ready=False,
            has_option=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertFalse(started)

    def test_end_step_handles_fulfilled_interrupted_and_timeout(self):
        near_time, status = destiny_end_step_contract(
            objective_valid=True,
            near_time=0.0,
            delta=self.fulfill_hold,
            fulfill_hold=self.fulfill_hold,
            now=10.0,
            ends_at=30.0,
        )
        self.assertEqual(status, "fulfilled")
        self.assertGreaterEqual(near_time, self.fulfill_hold)

        near_time, status = destiny_end_step_contract(
            objective_valid=False,
            near_time=0.4,
            delta=0.2,
            fulfill_hold=self.fulfill_hold,
            now=10.0,
            ends_at=30.0,
        )
        self.assertEqual(status, "interrupted")
        self.assertGreaterEqual(near_time, 0.0)

        _near_time, status = destiny_end_step_contract(
            objective_valid=True,
            near_time=0.0,
            delta=0.2,
            fulfill_hold=self.fulfill_hold,
            now=31.0,
            ends_at=30.0,
        )
        self.assertEqual(status, "timeout")

    def test_hooks_exist_across_runtime_ai_actor_hud_and_docs(self):
        self.assertIn("_update_destiny_pulls", self.loop_content)
        self.assertIn("_collect_destiny_options", self.loop_content)
        self.assertIn("_end_destiny_pull", self.loop_content)
        self.assertIn("Destiny START", self.loop_content)
        self.assertIn("Destiny END", self.loop_content)
        self.assertIn("Destiny FULFILLED", self.loop_content)
        self.assertIn("Destiny INTERRUPTED", self.loop_content)
        self.assertIn('"destiny_active_total"', self.loop_content)
        self.assertIn('"destiny_active_labels"', self.loop_content)

        self.assertIn('"rift_call"', self.loop_content)
        self.assertIn('"relic_call"', self.loop_content)
        self.assertIn('"vendetta_call"', self.loop_content)

        self.assertIn("get_destiny_guidance", self.ai_content)
        self.assertIn("destiny:", self.ai_content)
        self.assertIn("set_destiny_pull", self.actor_content)
        self.assertIn("destiny_tag", self.actor_content)
        self.assertIn("Destiny:", self.overlay_content)
        self.assertIn("Destiny pulls:", self.overlay_content)

        self.assertIn("destiny", self.readme_content)
        self.assertIn("rift", self.readme_content)
        self.assertIn("vendetta", self.readme_content)
        self.assertIn("relic", self.readme_content)


if __name__ == "__main__":
    unittest.main()
