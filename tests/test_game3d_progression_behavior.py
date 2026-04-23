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


def _extract_float_list(content: str, pattern: str) -> list[float]:
    match = re.search(pattern, content)
    if not match:
        raise AssertionError(f"Pattern not found: {pattern}")
    raw = match.group(1)
    return [float(item.strip()) for item in raw.split(",")]


def apply_progression_contract(
    xp_awards: list[float],
    thresholds: list[float],
    max_level: int,
    start_level: int = 1,
    start_xp: float = 0.0,
) -> tuple[int, float]:
    level = start_level
    xp = start_xp
    for amount in xp_awards:
        xp += amount
        while level < max_level and xp >= thresholds[level]:
            level += 1
    return level, xp


def survival_xp_contract(duration: float, tick_dt: float, interval: float) -> int:
    timer = 0.0
    gains = 0
    steps = int(duration / tick_dt)
    for _ in range(steps):
        timer += tick_dt
        if timer < interval:
            continue
        timer -= interval
        gains += 1
    return gains


class TestGame3DProgressionBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")

        self.max_level = _extract_int(self.actor_content, r"max_level:\s*int\s*=\s*([0-9]+)")
        self.thresholds = _extract_float_list(
            self.actor_content,
            r"level_xp_thresholds:\s*Array\[float\]\s*=\s*\[([^\]]+)\]",
        )
        self.survival_interval = _extract_float(
            self.actor_content,
            r"survival_xp_interval:\s*float\s*=\s*([0-9.]+)",
        )
        self.xp_on_hit = _extract_float(self.loop_content, r"XP_ON_HIT:\s*float\s*=\s*([0-9.]+)")
        self.xp_on_cast = _extract_float(self.loop_content, r"XP_ON_CAST:\s*float\s*=\s*([0-9.]+)")
        self.xp_on_kill = _extract_float(self.loop_content, r"XP_ON_KILL:\s*float\s*=\s*([0-9.]+)")

    def test_thresholds_are_monotonic_and_usable(self):
        self.assertEqual(self.max_level, 3)
        self.assertEqual(len(self.thresholds), self.max_level)
        self.assertEqual(self.thresholds[0], 0.0)
        self.assertGreater(self.thresholds[1], self.thresholds[0])
        self.assertGreater(self.thresholds[2], self.thresholds[1])

    def test_progression_rewards_reach_level_two_then_cap(self):
        early_awards = [self.xp_on_cast] * 4 + [self.xp_on_hit] * 8
        level_after_early, xp_after_early = apply_progression_contract(
            early_awards,
            self.thresholds,
            self.max_level,
        )
        self.assertGreaterEqual(level_after_early, 2)

        level_after_chain, _ = apply_progression_contract(
            [self.xp_on_kill] * 20,
            self.thresholds,
            self.max_level,
            start_level=level_after_early,
            start_xp=xp_after_early,
        )
        self.assertEqual(level_after_chain, self.max_level)

    def test_survival_progress_contract_ticks_regularly(self):
        tick_dt = 1.0 / 8.0
        short_gains = survival_xp_contract(self.survival_interval * 0.9, tick_dt, self.survival_interval)
        long_gains = survival_xp_contract(self.survival_interval * 2.2, tick_dt, self.survival_interval)
        self.assertEqual(short_gains, 0)
        self.assertGreaterEqual(long_gains, 2)

    def test_runtime_snapshot_mentions_progression_fields(self):
        self.assertIn('"level_counts"', self.loop_content)
        self.assertIn('"human_level_counts"', self.loop_content)
        self.assertIn('"monster_level_counts"', self.loop_content)
        self.assertIn('"avg_level"', self.loop_content)
        self.assertIn('"level_ups_total"', self.loop_content)

    def test_runtime_snapshot_mentions_champion_fields(self):
        self.assertIn('"champion_alive_total"', self.loop_content)
        self.assertIn('"human_champions_alive"', self.loop_content)
        self.assertIn('"monster_champions_alive"', self.loop_content)
        self.assertIn('"champion_promotions_total"', self.loop_content)
        self.assertIn("promote_to_champion", self.actor_content)

    def test_progression_xp_constants_are_non_zero_and_bounded(self):
        self.assertGreater(self.xp_on_hit, 0.0)
        self.assertGreater(self.xp_on_cast, 0.0)
        self.assertGreater(self.xp_on_kill, self.xp_on_hit)
        self.assertLessEqual(self.xp_on_kill, 8.0)
        self.assertLessEqual(self.xp_on_hit, 3.0)
        self.assertLessEqual(self.xp_on_cast, 2.0)


if __name__ == "__main__":
    unittest.main()
