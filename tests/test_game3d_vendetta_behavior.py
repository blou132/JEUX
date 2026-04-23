from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def can_start_vendetta_contract(
    *,
    active_target: str,
    cooldown_until: float,
    now: float,
    source_active: bool,
    target_active: bool,
) -> bool:
    if active_target != "":
        return False
    if not source_active or not target_active:
        return False
    if now < cooldown_until:
        return False
    return True


def vendetta_lifecycle_contract(
    *,
    source_active: bool,
    target_active: bool,
    now: float,
    end_at: float,
) -> str:
    if not source_active:
        return "dropped"
    if not target_active:
        return "resolved"
    if now >= end_at:
        return "expired"
    return "active"


def vendetta_modifier_contract(target_match: bool) -> dict[str, float]:
    if not target_match:
        return {"raid_delta": 0.0, "bounty_delta": 0.0}
    return {"raid_delta": 0.10, "bounty_delta": 0.12}


class TestGame3DVendettaBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    def test_vendetta_constants_are_bounded(self):
        min_match = re.search(r"allegiance_vendetta_duration_min:\s*float\s*=\s*([0-9.]+)", self.world_content)
        max_match = re.search(r"allegiance_vendetta_duration_max:\s*float\s*=\s*([0-9.]+)", self.world_content)
        cooldown_match = re.search(r"allegiance_vendetta_cooldown:\s*float\s*=\s*([0-9.]+)", self.world_content)
        self.assertIsNotNone(min_match)
        self.assertIsNotNone(max_match)
        self.assertIsNotNone(cooldown_match)
        duration_min = float(min_match.group(1))
        duration_max = float(max_match.group(1))
        cooldown = float(cooldown_match.group(1))
        self.assertGreaterEqual(duration_min, 10.0)
        self.assertLessEqual(duration_min, 40.0)
        self.assertGreater(duration_max, duration_min)
        self.assertLessEqual(duration_max, 70.0)
        self.assertGreaterEqual(cooldown, 10.0)
        self.assertLessEqual(cooldown, 50.0)

    def test_creation_contract_enforces_uniqueness_and_cooldown(self):
        self.assertFalse(
            can_start_vendetta_contract(
                active_target="monster:ruins",
                cooldown_until=0.0,
                now=24.0,
                source_active=True,
                target_active=True,
            )
        )
        self.assertFalse(
            can_start_vendetta_contract(
                active_target="",
                cooldown_until=30.0,
                now=24.0,
                source_active=True,
                target_active=True,
            )
        )
        self.assertTrue(
            can_start_vendetta_contract(
                active_target="",
                cooldown_until=22.0,
                now=24.0,
                source_active=True,
                target_active=True,
            )
        )

    def test_lifecycle_contract_resolves_or_expires_cleanly(self):
        self.assertEqual(
            vendetta_lifecycle_contract(
                source_active=True,
                target_active=False,
                now=30.0,
                end_at=45.0,
            ),
            "resolved",
        )
        self.assertEqual(
            vendetta_lifecycle_contract(
                source_active=True,
                target_active=True,
                now=46.0,
                end_at=45.0,
            ),
            "expired",
        )

    def test_modifiers_are_lightweight(self):
        inactive = vendetta_modifier_contract(False)
        self.assertEqual(inactive["raid_delta"], 0.0)
        self.assertEqual(inactive["bounty_delta"], 0.0)
        active = vendetta_modifier_contract(True)
        self.assertGreaterEqual(active["raid_delta"], 0.0)
        self.assertLessEqual(active["raid_delta"], 0.15)
        self.assertGreaterEqual(active["bounty_delta"], 0.0)
        self.assertLessEqual(active["bounty_delta"], 0.15)

    def test_hooks_exist_across_runtime_bounty_hud_and_docs(self):
        self.assertIn("get_allegiance_vendetta_target", self.world_content)
        self.assertIn("get_allegiance_vendetta_modifiers", self.world_content)
        self.assertIn("register_vendetta_incident", self.world_content)
        self.assertIn("_update_vendetta_runtime", self.world_content)
        self.assertIn("vendetta_started", self.world_content)
        self.assertIn("vendetta_resolved", self.world_content)
        self.assertIn("vendetta_expired", self.world_content)
        self.assertIn("target_allegiance_id", self.world_content)
        self.assertIn("_handle_vendetta_transition", self.loop_content)
        self.assertIn("Vendetta START", self.loop_content)
        self.assertIn("Vendetta END", self.loop_content)
        self.assertIn("Vendetta RESOLVED", self.loop_content)
        self.assertIn("Vendetta EXPIRED", self.loop_content)
        self.assertIn("bounty_target_allegiance_id", self.loop_content)
        self.assertIn("Vendettas:", self.overlay_content)
        self.assertIn("Vendetta map:", self.overlay_content)
        self.assertIn("vendetta", self.readme_content)
        self.assertIn("grudge", self.readme_content)


if __name__ == "__main__":
    unittest.main()
