from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def legacy_candidate_contract(
    *,
    is_champion: bool,
    is_special_arrival: bool,
    has_relic: bool,
    renown: float,
    notoriety: float,
    renown_trigger: float,
    notoriety_trigger: float,
) -> bool:
    if is_champion or is_special_arrival or has_relic:
        return True
    if renown >= renown_trigger:
        return True
    if notoriety >= notoriety_trigger:
        return True
    return False


def choose_successor_contract(
    *,
    victim_faction: str,
    victim_allegiance: str,
    candidates: list[dict],
    max_distance: float,
) -> int:
    valid = [
        candidate
        for candidate in candidates
        if candidate.get("faction", "") == victim_faction and float(candidate.get("distance", 999.0)) <= max_distance
    ]
    if not valid:
        return 0

    same_allegiance = [candidate for candidate in valid if victim_allegiance != "" and candidate.get("allegiance", "") == victim_allegiance]
    pool = same_allegiance if same_allegiance else valid

    best_id = 0
    best_score = float("-inf")
    for candidate in pool:
        score = 0.0
        score += (max_distance - float(candidate.get("distance", max_distance))) * 0.8
        score += float(candidate.get("renown", 0.0)) * 0.08
        score += float(candidate.get("notoriety", 0.0)) * 0.05
        if bool(candidate.get("can_lead", False)):
            score += 2.5
        if bool(candidate.get("is_champion", False)):
            score += 1.8
        if bool(candidate.get("is_special", False)):
            score += 1.4
        if score > best_score:
            best_score = score
            best_id = int(candidate.get("id", 0))
    return best_id


def transfer_contract(renown: float, notoriety: float) -> tuple[float, float]:
    renown_gain = max(1.0, min(6.0, renown * 0.12))
    notoriety_gain = max(0.6, min(5.0, notoriety * 0.10))
    return renown_gain, notoriety_gain


def can_choose_successor_contract(active_successors: int, max_active_successors: int) -> bool:
    return active_successors < max_active_successors


class TestGame3DLegacyBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    def test_trigger_conditions_cover_notable_and_skip_non_notable(self):
        self.assertTrue(
            legacy_candidate_contract(
                is_champion=True,
                is_special_arrival=False,
                has_relic=False,
                renown=10.0,
                notoriety=10.0,
                renown_trigger=52.0,
                notoriety_trigger=58.0,
            )
        )
        self.assertTrue(
            legacy_candidate_contract(
                is_champion=False,
                is_special_arrival=False,
                has_relic=False,
                renown=58.0,
                notoriety=12.0,
                renown_trigger=52.0,
                notoriety_trigger=58.0,
            )
        )
        self.assertFalse(
            legacy_candidate_contract(
                is_champion=False,
                is_special_arrival=False,
                has_relic=False,
                renown=24.0,
                notoriety=26.0,
                renown_trigger=52.0,
                notoriety_trigger=58.0,
            )
        )

    def test_successor_choice_is_bounded_and_prefers_same_allegiance(self):
        candidates = [
            {"id": 1, "faction": "human", "allegiance": "human:camp", "distance": 5.0, "renown": 20.0, "notoriety": 14.0, "can_lead": True, "is_champion": False, "is_special": False},
            {"id": 2, "faction": "human", "allegiance": "human:camp", "distance": 7.0, "renown": 33.0, "notoriety": 18.0, "can_lead": True, "is_champion": False, "is_special": False},
            {"id": 3, "faction": "human", "allegiance": "human:other", "distance": 3.0, "renown": 42.0, "notoriety": 20.0, "can_lead": True, "is_champion": True, "is_special": False},
            {"id": 4, "faction": "monster", "allegiance": "monster:ruins", "distance": 2.0, "renown": 70.0, "notoriety": 70.0, "can_lead": True, "is_champion": True, "is_special": False},
        ]
        picked = choose_successor_contract(
            victim_faction="human",
            victim_allegiance="human:camp",
            candidates=candidates,
            max_distance=11.5,
        )
        self.assertIn(picked, [1, 2])

    def test_legacy_transfer_values_are_lightweight(self):
        renown_gain, notoriety_gain = transfer_contract(82.0, 76.0)
        self.assertGreaterEqual(renown_gain, 1.0)
        self.assertLessEqual(renown_gain, 6.0)
        self.assertGreaterEqual(notoriety_gain, 0.6)
        self.assertLessEqual(notoriety_gain, 5.0)

    def test_successor_cap_contract_is_bounded(self):
        self.assertTrue(can_choose_successor_contract(active_successors=2, max_active_successors=4))
        self.assertFalse(can_choose_successor_contract(active_successors=4, max_active_successors=4))

    def test_hooks_exist_across_runtime_hud_and_docs(self):
        self.assertIn("LEGACY_TRIGGER_CHANCE", self.loop_content)
        self.assertIn("LEGACY_MAX_ACTIVE_SUCCESSORS", self.loop_content)
        self.assertIn("LEGACY_COOLDOWN", self.loop_content)
        self.assertIn("_try_trigger_legacy", self.loop_content)
        self.assertIn("_pick_legacy_successor", self.loop_content)
        self.assertIn("_update_legacy_runtime", self.loop_content)
        self.assertIn("_legacy_successor_runtime_by_actor.size() < LEGACY_MAX_ACTIVE_SUCCESSORS", self.loop_content)
        self.assertIn("Legacy Triggered", self.loop_content)
        self.assertIn("Successor Chosen", self.loop_content)
        self.assertIn("Legacy Faded", self.loop_content)
        self.assertIn("register_vendetta_incident", self.loop_content)
        self.assertIn("Relic INHERITED", self.loop_content)
        self.assertIn('"legacy_successor_labels"', self.loop_content)
        self.assertIn("Legacy:", self.overlay_content)
        self.assertIn("Legacy successors:", self.overlay_content)
        self.assertIn("legacy", self.readme_content)
        self.assertIn("succession", self.readme_content)
        self.assertIn("successor", self.readme_content)


if __name__ == "__main__":
    unittest.main()
