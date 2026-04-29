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


def expedition_start_contract(
    *,
    actor_notable: bool,
    has_active_expedition: bool,
    global_cooldown_left: float,
    actor_cooldown_left: float,
    active_total: int,
    max_active: int,
    trigger_roll: float,
    trigger_chance: float,
) -> bool:
    if not actor_notable:
        return False
    if has_active_expedition:
        return False
    if global_cooldown_left > 0.0:
        return False
    if actor_cooldown_left > 0.0:
        return False
    if active_total >= max_active:
        return False
    return trigger_roll <= trigger_chance


def expedition_end_contract(
    *,
    leader_alive: bool,
    destination_alive: bool,
    near_hold: float,
    arrival_hold: float,
    now: float,
    ends_at: float,
) -> str:
    if not leader_alive:
        return "interrupted_leader_unavailable"
    if not destination_alive:
        return "interrupted_destination_lost"
    if near_hold >= arrival_hold:
        return "arrived_destination_reached"
    if now >= ends_at:
        return "ended_duration_complete"
    return "active"


def expedition_guidance_contract(*, has_enemy: bool, roll: float, weight: float) -> str:
    weight = max(0.20, min(0.80, weight))
    if has_enemy:
        return "normal_enemy"
    if roll <= weight:
        return "poi"
    return "wander"


class TestGame3DExpeditionsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"EXPEDITION_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"EXPEDITION_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"EXPEDITION_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.actor_cooldown = _extract_float(
            self.loop_content,
            r"EXPEDITION_ACTOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"EXPEDITION_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"EXPEDITION_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"EXPEDITION_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"EXPEDITION_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.start_base = _extract_float(
            self.loop_content,
            r"EXPEDITION_START_CHANCE_BASE:\s*float\s*=\s*([0-9.]+)",
        )
        self.arrival_radius = _extract_float(
            self.loop_content,
            r"EXPEDITION_ARRIVAL_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.arrival_hold = _extract_float(
            self.loop_content,
            r"EXPEDITION_ARRIVAL_HOLD:\s*float\s*=\s*([0-9.]+)",
        )
        self.renown_arrival = _extract_float(
            self.loop_content,
            r"EXPEDITION_RENOWN_ON_ARRIVAL:\s*float\s*=\s*([0-9.]+)",
        )

    def test_expedition_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 140.0)
        self.assertLessEqual(self.start_delay, 360.0)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.global_cooldown, 8.0)
        self.assertLessEqual(self.global_cooldown, 46.0)
        self.assertGreaterEqual(self.actor_cooldown, 28.0)
        self.assertLessEqual(self.actor_cooldown, 150.0)
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 24.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 30.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 4)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreaterEqual(self.start_base, 0.08)
        self.assertLessEqual(self.start_base, 0.35)
        self.assertGreater(self.arrival_radius, 2.0)
        self.assertLessEqual(self.arrival_radius, 8.0)
        self.assertGreater(self.arrival_hold, 0.5)
        self.assertLessEqual(self.arrival_hold, 3.0)
        self.assertGreater(self.renown_arrival, 0.0)
        self.assertLessEqual(self.renown_arrival, 0.40)

    def test_start_contract_enforces_uniqueness_and_cap(self):
        self.assertFalse(
            expedition_start_contract(
                actor_notable=False,
                has_active_expedition=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            expedition_start_contract(
                actor_notable=True,
                has_active_expedition=True,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertFalse(
            expedition_start_contract(
                actor_notable=True,
                has_active_expedition=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=self.max_active,
                max_active=self.max_active,
                trigger_roll=0.0,
                trigger_chance=self.start_base,
            )
        )
        self.assertTrue(
            expedition_start_contract(
                actor_notable=True,
                has_active_expedition=False,
                global_cooldown_left=0.0,
                actor_cooldown_left=0.0,
                active_total=0,
                max_active=self.max_active,
                trigger_roll=0.12,
                trigger_chance=min(0.62, self.start_base + 0.12),
            )
        )

    def test_end_contract_supports_arrived_interrupted_and_end(self):
        self.assertEqual(
            expedition_end_contract(
                leader_alive=False,
                destination_alive=True,
                near_hold=0.0,
                arrival_hold=self.arrival_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "interrupted_leader_unavailable",
        )
        self.assertEqual(
            expedition_end_contract(
                leader_alive=True,
                destination_alive=False,
                near_hold=0.0,
                arrival_hold=self.arrival_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "interrupted_destination_lost",
        )
        self.assertEqual(
            expedition_end_contract(
                leader_alive=True,
                destination_alive=True,
                near_hold=self.arrival_hold,
                arrival_hold=self.arrival_hold,
                now=8.0,
                ends_at=20.0,
            ),
            "arrived_destination_reached",
        )
        self.assertEqual(
            expedition_end_contract(
                leader_alive=True,
                destination_alive=True,
                near_hold=0.0,
                arrival_hold=self.arrival_hold,
                now=24.0,
                ends_at=20.0,
            ),
            "ended_duration_complete",
        )

    def test_guidance_bias_is_light_and_local(self):
        self.assertEqual(
            expedition_guidance_contract(has_enemy=False, roll=0.10, weight=0.56),
            "poi",
        )
        self.assertEqual(
            expedition_guidance_contract(has_enemy=False, roll=0.88, weight=0.56),
            "wander",
        )
        self.assertEqual(
            expedition_guidance_contract(has_enemy=True, roll=0.10, weight=0.56),
            "normal_enemy",
        )

    def test_hooks_exist_across_runtime_ai_actor_hud_and_docs(self):
        self.assertIn("_setup_expedition_state", self.loop_content)
        self.assertIn("_update_expeditions", self.loop_content)
        self.assertIn("_try_start_expedition", self.loop_content)
        self.assertIn("_resolve_expedition_target", self.loop_content)
        self.assertIn("_arrive_expedition", self.loop_content)
        self.assertIn("_interrupt_expedition", self.loop_content)
        self.assertIn("Expedition START", self.loop_content)
        self.assertIn("Expedition ARRIVED", self.loop_content)
        self.assertIn("Expedition END", self.loop_content)
        self.assertIn("Expedition INTERRUPTED", self.loop_content)
        self.assertIn('"expedition_active_count"', self.loop_content)
        self.assertIn('"expedition_active_labels"', self.loop_content)
        self.assertIn('"expedition_started_total"', self.loop_content)

        self.assertIn("destiny_active", self.loop_content)
        self.assertIn("oath_active", self.loop_content)
        self.assertIn("legacy_successor", self.loop_content)
        self.assertIn("bond_anchor", self.loop_content)
        self.assertIn("mending_window", self.loop_content)
        self.assertIn("recovery_local", self.loop_content)
        self.assertIn("echo_near", self.loop_content)

        self.assertIn("get_expedition_guidance", self.ai_content)
        self.assertIn("expedition:", self.ai_content)

        self.assertIn("set_expedition_state", self.actor_content)
        self.assertIn("get_expedition_guidance", self.actor_content)
        self.assertIn("expedition_tag", self.actor_content)

        self.assertIn("Expeditions:", self.overlay_content)
        self.assertIn("Expedition labels:", self.overlay_content)

        self.assertIn("expedition", self.readme_content)
        self.assertIn("pilgrimage", self.readme_content)


if __name__ == "__main__":
    unittest.main()
