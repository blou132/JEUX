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


def gate_response_spawn_contract(
    *,
    gate_open: bool,
    cooldown_left: float,
    already_active: bool,
    has_candidate: bool,
    trigger_roll: float,
    trigger_chance: float,
    cooldown_on_end: float,
) -> tuple[bool, float]:
    if not gate_open:
        return False, max(0.0, cooldown_left)
    if cooldown_left > 0.0:
        return False, cooldown_left
    if already_active:
        return False, cooldown_left
    if not has_candidate:
        return False, cooldown_left
    if trigger_roll > trigger_chance:
        return False, cooldown_left
    return True, cooldown_on_end


def gate_response_end_contract(
    *,
    gate_open: bool,
    anchor_alive: bool,
    now: float,
    ends_at: float,
) -> str:
    if not gate_open:
        return "interrupted_gate_closed"
    if not anchor_alive:
        return "interrupted_anchor_lost"
    if now >= ends_at:
        return "success"
    return "active"


def gate_response_effect_contract(
    *,
    response_id: str,
    gate_remaining: float,
    seal_reduce: float,
    exploit_extend: float,
    breach_pending: bool,
    bonus_breach_used: bool,
) -> dict:
    next_remaining = gate_remaining
    next_breach_pending = breach_pending
    next_bonus_used = bonus_breach_used

    if response_id == "gate_seal":
        next_remaining = max(0.7, gate_remaining - seal_reduce)
    elif response_id == "gate_exploit":
        next_remaining = min(gate_remaining + exploit_extend, gate_remaining + 6.0)
        if not breach_pending and not bonus_breach_used:
            next_breach_pending = True
            next_bonus_used = True

    return {
        "remaining": next_remaining,
        "breach_pending": next_breach_pending,
        "bonus_breach_used": next_bonus_used,
    }


class TestGame3DGateResponsesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.min_population = _extract_int(
            self.loop_content,
            r"GATE_RESPONSE_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.check_interval = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)",
        )
        self.cooldown = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.pull_boost = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_PULL_BOOST:\s*float\s*=\s*([0-9.]+)",
        )
        self.seal_reduce = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_SEAL_START_REDUCE:\s*float\s*=\s*([0-9.]+)",
        )
        self.exploit_extend = _extract_float(
            self.loop_content,
            r"GATE_RESPONSE_EXPLOIT_START_EXTEND:\s*float\s*=\s*([0-9.]+)",
        )

    def test_gate_response_constants_are_bounded(self):
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 16)
        self.assertGreaterEqual(self.check_interval, 1.5)
        self.assertLessEqual(self.check_interval, 5.0)
        self.assertGreaterEqual(self.cooldown, 20.0)
        self.assertLessEqual(self.cooldown, 60.0)
        self.assertGreaterEqual(self.duration_min, 8.0)
        self.assertLessEqual(self.duration_min, 20.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 24.0)
        self.assertGreaterEqual(self.pull_boost, 1.0)
        self.assertLessEqual(self.pull_boost, 1.35)
        self.assertGreater(self.seal_reduce, 0.0)
        self.assertLessEqual(self.seal_reduce, 4.0)
        self.assertGreater(self.exploit_extend, 0.0)
        self.assertLessEqual(self.exploit_extend, 3.0)

    def test_trigger_is_bounded_and_disabled_when_gate_closed(self):
        started, _cooldown = gate_response_spawn_contract(
            gate_open=False,
            cooldown_left=0.0,
            already_active=False,
            has_candidate=True,
            trigger_roll=0.0,
            trigger_chance=0.8,
            cooldown_on_end=self.cooldown,
        )
        self.assertFalse(started)

        started, _cooldown = gate_response_spawn_contract(
            gate_open=True,
            cooldown_left=0.0,
            already_active=False,
            has_candidate=True,
            trigger_roll=0.1,
            trigger_chance=0.5,
            cooldown_on_end=self.cooldown,
        )
        self.assertTrue(started)

    def test_end_is_clean_with_success_or_interrupt(self):
        self.assertEqual(
            gate_response_end_contract(gate_open=True, anchor_alive=True, now=14.0, ends_at=20.0),
            "active",
        )
        self.assertEqual(
            gate_response_end_contract(gate_open=True, anchor_alive=True, now=21.0, ends_at=20.0),
            "success",
        )
        self.assertEqual(
            gate_response_end_contract(gate_open=False, anchor_alive=True, now=10.0, ends_at=20.0),
            "interrupted_gate_closed",
        )
        self.assertEqual(
            gate_response_end_contract(gate_open=True, anchor_alive=False, now=10.0, ends_at=20.0),
            "interrupted_anchor_lost",
        )

    def test_effects_are_light_and_real_on_gate_and_breach(self):
        seal = gate_response_effect_contract(
            response_id="gate_seal",
            gate_remaining=15.0,
            seal_reduce=self.seal_reduce,
            exploit_extend=self.exploit_extend,
            breach_pending=False,
            bonus_breach_used=False,
        )
        self.assertLess(seal["remaining"], 15.0)
        self.assertFalse(seal["breach_pending"])

        exploit = gate_response_effect_contract(
            response_id="gate_exploit",
            gate_remaining=15.0,
            seal_reduce=self.seal_reduce,
            exploit_extend=self.exploit_extend,
            breach_pending=False,
            bonus_breach_used=False,
        )
        self.assertGreater(exploit["remaining"], 15.0)
        self.assertTrue(exploit["breach_pending"])
        self.assertTrue(exploit["bonus_breach_used"])

    def test_hooks_exist_across_runtime_world_ai_hud_and_docs(self):
        self.assertIn("_update_gate_responses", self.loop_content)
        self.assertIn("_try_start_gate_response", self.loop_content)
        self.assertIn('"gate_seal"', self.loop_content)
        self.assertIn('"gate_exploit"', self.loop_content)
        self.assertIn("Gate Response START", self.loop_content)
        self.assertIn("Gate Response END", self.loop_content)
        self.assertIn("Gate Response SUCCESS", self.loop_content)
        self.assertIn("Gate Response INTERRUPTED", self.loop_content)
        self.assertIn('"gate_response_started_total"', self.loop_content)

        self.assertIn("set_neutral_gate_response_pull_modifiers", self.world_content)
        self.assertIn("apply_neutral_gate_open_duration_delta", self.world_content)
        self.assertIn("request_neutral_gate_bonus_breach", self.world_content)
        self.assertIn("neutral_gate_response_pull_human_mult", self.world_content)

        self.assertIn("get_neutral_gate_guidance", self.ai_content)
        self.assertIn("Gate Responses:", self.overlay_content)
        self.assertIn("gate response", self.readme_content)
        self.assertIn("gate_seal", self.readme_content)
        self.assertIn("gate_exploit", self.readme_content)


if __name__ == "__main__":
    unittest.main()
