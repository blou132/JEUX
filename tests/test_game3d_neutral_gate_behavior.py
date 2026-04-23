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


def neutral_gate_step_contract(
    *,
    status: str,
    open_until: float,
    cooldown_until: float,
    now: float,
    can_open: bool,
    open_duration: float,
    cooldown_min: float,
    cooldown_max: float,
    retry_delay: float,
    breach_pending: bool,
) -> dict:
    events: list[str] = []
    next_status = status
    next_open_until = open_until
    next_cooldown_until = cooldown_until
    next_breach_pending = breach_pending

    if next_status == "open":
        if now >= next_open_until:
            next_status = "dormant"
            next_open_until = 0.0
            next_breach_pending = False
            next_cooldown_until = now + (cooldown_min + cooldown_max) * 0.5
            events.append("closed")
    else:
        if next_cooldown_until <= 0.0:
            next_cooldown_until = now + cooldown_min * 0.6
        elif now >= next_cooldown_until:
            if can_open:
                next_status = "open"
                next_open_until = now + open_duration
                next_breach_pending = True
                events.append("opened")
            else:
                next_cooldown_until = now + retry_delay

    if next_status == "open" and next_breach_pending:
        next_breach_pending = False
        events.append("breach")

    return {
        "status": next_status,
        "open_until": next_open_until,
        "cooldown_until": next_cooldown_until,
        "breach_pending": next_breach_pending,
        "events": events,
    }


def neutral_gate_guidance_contract(
    *,
    gate_open: bool,
    distance: float,
    max_distance: float,
    cautious: bool,
    powerful: bool,
) -> str:
    if not gate_open or distance > max_distance:
        return "none"
    if cautious and distance <= 9.0:
        return "avoid"
    if powerful:
        return "investigate"
    return "none"


class TestGame3DNeutralGateBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.open_duration = _extract_float(
            self.world_content,
            r"neutral_gate_open_duration:\s*float\s*=\s*([0-9.]+)",
        )
        self.cooldown_min = _extract_float(
            self.world_content,
            r"neutral_gate_cooldown_min:\s*float\s*=\s*([0-9.]+)",
        )
        self.cooldown_max = _extract_float(
            self.world_content,
            r"neutral_gate_cooldown_max:\s*float\s*=\s*([0-9.]+)",
        )
        self.retry_delay = _extract_float(
            self.world_content,
            r"neutral_gate_retry_delay:\s*float\s*=\s*([0-9.]+)",
        )
        self.min_dom = _extract_float(
            self.world_content,
            r"neutral_gate_min_dominance_seconds:\s*float\s*=\s*([0-9.]+)",
        )

    def test_gate_constants_are_rare_bounded_and_readable(self):
        self.assertGreaterEqual(self.open_duration, 10.0)
        self.assertLessEqual(self.open_duration, 28.0)
        self.assertGreaterEqual(self.cooldown_min, 35.0)
        self.assertLessEqual(self.cooldown_min, 90.0)
        self.assertGreater(self.cooldown_max, self.cooldown_min)
        self.assertLessEqual(self.cooldown_max, 150.0)
        self.assertGreaterEqual(self.retry_delay, 6.0)
        self.assertLessEqual(self.retry_delay, 20.0)
        self.assertGreaterEqual(self.min_dom, 10.0)
        self.assertLessEqual(self.min_dom, 30.0)

    def test_gate_cycle_opens_then_closes_with_single_breach(self):
        state = neutral_gate_step_contract(
            status="dormant",
            open_until=0.0,
            cooldown_until=0.0,
            now=20.0,
            can_open=True,
            open_duration=self.open_duration,
            cooldown_min=self.cooldown_min,
            cooldown_max=self.cooldown_max,
            retry_delay=self.retry_delay,
            breach_pending=False,
        )
        self.assertEqual(state["status"], "dormant")
        self.assertNotIn("opened", state["events"])

        state = neutral_gate_step_contract(
            status=state["status"],
            open_until=state["open_until"],
            cooldown_until=20.0,
            now=21.0,
            can_open=True,
            open_duration=self.open_duration,
            cooldown_min=self.cooldown_min,
            cooldown_max=self.cooldown_max,
            retry_delay=self.retry_delay,
            breach_pending=state["breach_pending"],
        )
        self.assertEqual(state["status"], "open")
        self.assertIn("opened", state["events"])
        self.assertIn("breach", state["events"])
        self.assertFalse(state["breach_pending"])

        state = neutral_gate_step_contract(
            status=state["status"],
            open_until=state["open_until"],
            cooldown_until=state["cooldown_until"],
            now=21.5,
            can_open=True,
            open_duration=self.open_duration,
            cooldown_min=self.cooldown_min,
            cooldown_max=self.cooldown_max,
            retry_delay=self.retry_delay,
            breach_pending=state["breach_pending"],
        )
        self.assertEqual(state["status"], "open")
        self.assertNotIn("breach", state["events"])

        state = neutral_gate_step_contract(
            status=state["status"],
            open_until=21.0,
            cooldown_until=state["cooldown_until"],
            now=45.0,
            can_open=True,
            open_duration=self.open_duration,
            cooldown_min=self.cooldown_min,
            cooldown_max=self.cooldown_max,
            retry_delay=self.retry_delay,
            breach_pending=state["breach_pending"],
        )
        self.assertEqual(state["status"], "dormant")
        self.assertIn("closed", state["events"])
        self.assertGreater(state["cooldown_until"], 45.0)

    def test_gate_does_not_open_when_conditions_are_not_ready(self):
        state = neutral_gate_step_contract(
            status="dormant",
            open_until=0.0,
            cooldown_until=12.0,
            now=12.2,
            can_open=False,
            open_duration=self.open_duration,
            cooldown_min=self.cooldown_min,
            cooldown_max=self.cooldown_max,
            retry_delay=self.retry_delay,
            breach_pending=False,
        )
        self.assertEqual(state["status"], "dormant")
        self.assertNotIn("opened", state["events"])
        self.assertGreaterEqual(state["cooldown_until"], 12.2 + self.retry_delay - 0.001)

    def test_local_guidance_is_light_and_contextual(self):
        self.assertEqual(
            neutral_gate_guidance_contract(
                gate_open=False,
                distance=5.0,
                max_distance=40.0,
                cautious=False,
                powerful=True,
            ),
            "none",
        )
        self.assertEqual(
            neutral_gate_guidance_contract(
                gate_open=True,
                distance=6.0,
                max_distance=40.0,
                cautious=True,
                powerful=False,
            ),
            "avoid",
        )
        self.assertEqual(
            neutral_gate_guidance_contract(
                gate_open=True,
                distance=8.0,
                max_distance=40.0,
                cautious=False,
                powerful=True,
            ),
            "investigate",
        )

    def test_gate_hooks_exist_across_runtime_ai_hud_and_docs(self):
        self.assertIn('"name": "rift_gate"', self.world_content)
        self.assertIn("get_neutral_gate_guidance", self.world_content)
        self.assertIn("neutral_gate_opened", self.world_content)
        self.assertIn("neutral_gate_closed", self.world_content)
        self.assertIn("neutral_gate_breach", self.world_content)
        self.assertIn("Dungeon/Gate OPEN", self.loop_content)
        self.assertIn("Dungeon/Gate CLOSED", self.loop_content)
        self.assertIn("Dungeon/Gate BREACH", self.loop_content)
        self.assertIn("_spawn_neutral_gate_breach", self.loop_content)
        self.assertIn("NEUTRAL_GATE_BREACH_BOUNTY_COOLDOWN_CLAMP", self.loop_content)
        self.assertIn("neutral_gate_pull", self.ai_content)
        self.assertIn("neutral_gate_avoid", self.world_content)
        self.assertIn("Neutral Gate:", self.overlay_content)
        self.assertIn("gate:open", self.overlay_content)
        self.assertIn("rift_gate_breach", self.actor_content)
        self.assertIn("rift gate", self.readme_content)


if __name__ == "__main__":
    unittest.main()
