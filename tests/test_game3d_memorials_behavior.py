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


def should_spawn_memorial_scar_contract(
    *,
    legacy_triggered: bool,
    is_champion: bool,
    is_special_arrival: bool,
    had_relic: bool,
    renown: float,
    notoriety: float,
    renown_trigger: float,
    notoriety_trigger: float,
) -> bool:
    if legacy_triggered or is_champion or is_special_arrival or had_relic:
        return True
    if renown >= renown_trigger:
        return True
    if notoriety >= notoriety_trigger:
        return True
    return False


def classify_memorial_scar_type_contract(*, faction: str, special_arrival_id: str = "") -> str:
    if faction == "human":
        return "memorial_site"
    if special_arrival_id in {"calamity_invader", "rift_gate_breach"}:
        return "scar_site"
    if faction == "monster":
        return "scar_site"
    return "scar_site"


def apply_cap_contract(existing: list[dict], max_active: int, new_site: dict) -> list[dict]:
    runtime = [dict(item) for item in existing]
    while len(runtime) >= max_active:
        runtime.sort(key=lambda item: float(item.get("ends_at", 0.0)))
        runtime.pop(0)
    runtime.append(dict(new_site))
    return runtime


def pulse_contract(
    *,
    site_type: str,
    site_faction: str,
    radius: float,
    renown_pulse: float,
    notoriety_pulse: float,
    actors: list[dict],
) -> list[dict]:
    next_actors: list[dict] = []
    for actor in actors:
        row = dict(actor)
        distance = float(row.get("distance", 999.0))
        if distance <= radius:
            if site_type == "memorial_site" and row.get("faction", "") == site_faction:
                row["renown"] = float(row.get("renown", 0.0)) + renown_pulse
            elif site_type == "scar_site" and row.get("faction", "") != site_faction:
                row["notoriety"] = float(row.get("notoriety", 0.0)) + notoriety_pulse
        next_actors.append(row)
    return next_actors


class TestGame3DMemorialsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.max_active = _extract_int(self.loop_content, r"MEMORIAL_SCAR_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)")
        self.duration_min = _extract_float(self.loop_content, r"MEMORIAL_SCAR_DURATION_MIN:\s*float\s*=\s*([0-9.]+)")
        self.duration_max = _extract_float(self.loop_content, r"MEMORIAL_SCAR_DURATION_MAX:\s*float\s*=\s*([0-9.]+)")
        self.radius = _extract_float(self.loop_content, r"MEMORIAL_SCAR_RADIUS:\s*float\s*=\s*([0-9.]+)")
        self.pulse_interval = _extract_float(self.loop_content, r"MEMORIAL_SCAR_PULSE_INTERVAL:\s*float\s*=\s*([0-9.]+)")
        self.renown_pulse = _extract_float(self.loop_content, r"MEMORIAL_SITE_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)")
        self.notoriety_pulse = _extract_float(self.loop_content, r"SCAR_SITE_NOTORIETY_PULSE:\s*float\s*=\s*([0-9.]+)")
        self.renown_trigger = _extract_float(self.loop_content, r"MEMORIAL_SCAR_RENOWN_TRIGGER:\s*float\s*=\s*([0-9.]+)")
        self.notoriety_trigger = _extract_float(self.loop_content, r"MEMORIAL_SCAR_NOTORIETY_TRIGGER:\s*float\s*=\s*([0-9.]+)")

    def test_memorial_scar_constants_are_bounded(self):
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 6)
        self.assertGreaterEqual(self.duration_min, 12.0)
        self.assertLessEqual(self.duration_min, 40.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 60.0)
        self.assertGreaterEqual(self.radius, 5.0)
        self.assertLessEqual(self.radius, 12.0)
        self.assertGreaterEqual(self.pulse_interval, 2.0)
        self.assertLessEqual(self.pulse_interval, 6.0)
        self.assertGreater(self.renown_pulse, 0.0)
        self.assertLessEqual(self.renown_pulse, 0.6)
        self.assertGreater(self.notoriety_pulse, 0.0)
        self.assertLessEqual(self.notoriety_pulse, 0.8)

    def test_trigger_is_notable_only(self):
        self.assertTrue(
            should_spawn_memorial_scar_contract(
                legacy_triggered=False,
                is_champion=True,
                is_special_arrival=False,
                had_relic=False,
                renown=4.0,
                notoriety=4.0,
                renown_trigger=self.renown_trigger,
                notoriety_trigger=self.notoriety_trigger,
            )
        )
        self.assertTrue(
            should_spawn_memorial_scar_contract(
                legacy_triggered=False,
                is_champion=False,
                is_special_arrival=False,
                had_relic=False,
                renown=self.renown_trigger + 1.0,
                notoriety=12.0,
                renown_trigger=self.renown_trigger,
                notoriety_trigger=self.notoriety_trigger,
            )
        )
        self.assertFalse(
            should_spawn_memorial_scar_contract(
                legacy_triggered=False,
                is_champion=False,
                is_special_arrival=False,
                had_relic=False,
                renown=self.renown_trigger - 20.0,
                notoriety=self.notoriety_trigger - 20.0,
                renown_trigger=self.renown_trigger,
                notoriety_trigger=self.notoriety_trigger,
            )
        )

    def test_type_selection_is_human_memorial_vs_monster_scar(self):
        self.assertEqual(
            classify_memorial_scar_type_contract(faction="human", special_arrival_id="summoned_hero"),
            "memorial_site",
        )
        self.assertEqual(
            classify_memorial_scar_type_contract(faction="monster", special_arrival_id="calamity_invader"),
            "scar_site",
        )

    def test_cap_and_fade_contract_stays_bounded(self):
        existing = [
            {"id": "a", "ends_at": 10.0},
            {"id": "b", "ends_at": 20.0},
            {"id": "c", "ends_at": 30.0},
        ]
        runtime = apply_cap_contract(existing, max_active=3, new_site={"id": "new", "ends_at": 40.0})
        ids = {str(item["id"]) for item in runtime}
        self.assertEqual(len(runtime), 3)
        self.assertNotIn("a", ids)
        self.assertIn("new", ids)

    def test_local_pulses_affect_only_nearby_relevant_factions(self):
        actors = [
            {"id": "ally_near", "faction": "human", "distance": 3.0, "renown": 5.0, "notoriety": 4.0},
            {"id": "ally_far", "faction": "human", "distance": 12.0, "renown": 5.0, "notoriety": 4.0},
            {"id": "enemy_near", "faction": "monster", "distance": 3.0, "renown": 5.0, "notoriety": 4.0},
        ]
        memorial_result = pulse_contract(
            site_type="memorial_site",
            site_faction="human",
            radius=self.radius,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
            actors=actors,
        )
        by_id = {str(row["id"]): row for row in memorial_result}
        self.assertGreater(by_id["ally_near"]["renown"], 5.0)
        self.assertEqual(by_id["ally_far"]["renown"], 5.0)
        self.assertEqual(by_id["enemy_near"]["renown"], 5.0)

        scar_result = pulse_contract(
            site_type="scar_site",
            site_faction="monster",
            radius=self.radius,
            renown_pulse=self.renown_pulse,
            notoriety_pulse=self.notoriety_pulse,
            actors=actors,
        )
        by_id = {str(row["id"]): row for row in scar_result}
        self.assertGreater(by_id["ally_near"]["notoriety"], 4.0)
        self.assertEqual(by_id["enemy_near"]["notoriety"], 4.0)

    def test_hooks_exist_across_runtime_hud_and_docs(self):
        self.assertIn("_try_spawn_memorial_scar_site", self.loop_content)
        self.assertIn("_update_memorial_scar_runtime", self.loop_content)
        self.assertIn("_apply_memorial_scar_pulse", self.loop_content)
        self.assertIn("Memorial/Scar BORN", self.loop_content)
        self.assertIn("Memorial/Scar FADED", self.loop_content)
        self.assertIn('"memorial_scar_active_total"', self.loop_content)
        self.assertIn('"memorial_scar_labels"', self.loop_content)
        self.assertIn("Memorial/Scar:", self.overlay_content)
        self.assertIn("Memorial/Scar sites:", self.overlay_content)
        self.assertIn("memorial", self.readme_content)
        self.assertIn("scar", self.readme_content)


if __name__ == "__main__":
    unittest.main()
