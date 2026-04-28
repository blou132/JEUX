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


def bond_candidate_contract(
    *,
    notable: bool,
    actor_has_bond: bool,
    actor_cooldown_ready: bool,
    alive_total: int,
    min_population: int,
    active_total: int,
    max_active: int,
    allegiance_active_bonds: int,
    max_per_allegiance: int,
) -> bool:
    if not notable:
        return False
    if actor_has_bond or not actor_cooldown_ready:
        return False
    if alive_total < min_population:
        return False
    if active_total >= max_active:
        return False
    if allegiance_active_bonds >= max_per_allegiance:
        return False
    return True


def bond_spawn_step_contract(
    *,
    global_cooldown_left: float,
    delta: float,
    trigger_roll: float,
    trigger_chance: float,
    eligible: bool,
    global_cooldown_on_start: float,
) -> tuple[float, bool]:
    global_cooldown_left = max(0.0, global_cooldown_left - delta)
    if global_cooldown_left > 0.0:
        return global_cooldown_left, False
    if not eligible:
        return global_cooldown_left, False
    if trigger_roll > trigger_chance:
        return global_cooldown_left, False
    return global_cooldown_on_start, True


def bond_end_contract(
    *,
    patron_alive: bool,
    context_ok: bool,
    now: float,
    ends_at: float,
) -> str:
    if not patron_alive:
        return "broken"
    if not context_ok:
        return "broken"
    if now >= ends_at:
        return "ended"
    return "active"


def bond_local_effect_contract(
    *,
    in_radius: bool,
    follower_of_patron: bool,
    rally_bonus_active: bool,
    bonus_roll: float,
    bonus_chance: float,
    patron_renown: float,
    ally_renown: float,
    renown_pulse: float,
) -> tuple[bool, float, float]:
    next_bonus: bool = rally_bonus_active
    next_patron_renown: float = patron_renown
    next_ally_renown: float = ally_renown
    if in_radius and follower_of_patron and not rally_bonus_active and bonus_roll <= bonus_chance:
        next_bonus = True
    if in_radius:
        next_patron_renown += renown_pulse
        if follower_of_patron:
            next_ally_renown += renown_pulse * 0.72
    return next_bonus, next_patron_renown, next_ally_renown


class TestGame3DBondsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.start_delay = _extract_float(
            self.loop_content,
            r"BOND_START_DELAY:\s*float\s*=\s*([0-9.]+)",
        )
        self.global_cooldown = _extract_float(
            self.loop_content,
            r"BOND_GLOBAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.actor_cooldown = _extract_float(
            self.loop_content,
            r"BOND_ACTOR_COOLDOWN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_min = _extract_float(
            self.loop_content,
            r"BOND_DURATION_MIN:\s*float\s*=\s*([0-9.]+)",
        )
        self.duration_max = _extract_float(
            self.loop_content,
            r"BOND_DURATION_MAX:\s*float\s*=\s*([0-9.]+)",
        )
        self.max_active = _extract_int(
            self.loop_content,
            r"BOND_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)",
        )
        self.max_per_allegiance = _extract_int(
            self.loop_content,
            r"BOND_MAX_PER_ALLEGIANCE:\s*int\s*=\s*([0-9]+)",
        )
        self.min_population = _extract_int(
            self.loop_content,
            r"BOND_MIN_POPULATION:\s*int\s*=\s*([0-9]+)",
        )
        self.radius = _extract_float(
            self.loop_content,
            r"BOND_RADIUS:\s*float\s*=\s*([0-9.]+)",
        )
        self.renown_pulse = _extract_float(
            self.loop_content,
            r"BOND_SHARED_RENOWN_PULSE:\s*float\s*=\s*([0-9.]+)",
        )
        self.rally_bonus_chance = _extract_float(
            self.loop_content,
            r"BOND_RALLY_BONUS_CHANCE_PER_SEC:\s*float\s*=\s*([0-9.]+)",
        )

    def test_bond_constants_are_rare_bounded_and_light(self):
        self.assertGreaterEqual(self.start_delay, 40.0)
        self.assertLessEqual(self.start_delay, 240.0)
        self.assertGreaterEqual(self.global_cooldown, 10.0)
        self.assertLessEqual(self.global_cooldown, 120.0)
        self.assertGreaterEqual(self.actor_cooldown, 20.0)
        self.assertLessEqual(self.actor_cooldown, 140.0)
        self.assertGreaterEqual(self.duration_min, 10.0)
        self.assertLessEqual(self.duration_min, 40.0)
        self.assertGreaterEqual(self.duration_max, self.duration_min)
        self.assertLessEqual(self.duration_max, 48.0)
        self.assertGreaterEqual(self.max_active, 1)
        self.assertLessEqual(self.max_active, 4)
        self.assertGreaterEqual(self.max_per_allegiance, 1)
        self.assertLessEqual(self.max_per_allegiance, 2)
        self.assertGreaterEqual(self.min_population, 8)
        self.assertLessEqual(self.min_population, 20)
        self.assertGreater(self.radius, 3.0)
        self.assertLessEqual(self.radius, 14.0)
        self.assertGreater(self.renown_pulse, 0.0)
        self.assertLessEqual(self.renown_pulse, 0.16)
        self.assertGreater(self.rally_bonus_chance, 0.0)
        self.assertLessEqual(self.rally_bonus_chance, 0.40)

    def test_trigger_contract_enforces_uniqueness_and_caps(self):
        self.assertTrue(
            bond_candidate_contract(
                notable=True,
                actor_has_bond=False,
                actor_cooldown_ready=True,
                alive_total=self.min_population + 3,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                allegiance_active_bonds=0,
                max_per_allegiance=self.max_per_allegiance,
            )
        )
        self.assertFalse(
            bond_candidate_contract(
                notable=True,
                actor_has_bond=True,
                actor_cooldown_ready=True,
                alive_total=self.min_population + 3,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                allegiance_active_bonds=0,
                max_per_allegiance=self.max_per_allegiance,
            )
        )
        self.assertFalse(
            bond_candidate_contract(
                notable=True,
                actor_has_bond=False,
                actor_cooldown_ready=True,
                alive_total=self.min_population + 3,
                min_population=self.min_population,
                active_total=0,
                max_active=self.max_active,
                allegiance_active_bonds=self.max_per_allegiance,
                max_per_allegiance=self.max_per_allegiance,
            )
        )

        cooldown_left, started = bond_spawn_step_contract(
            global_cooldown_left=0.0,
            delta=1.0,
            trigger_roll=0.0,
            trigger_chance=0.30,
            eligible=True,
            global_cooldown_on_start=self.global_cooldown,
        )
        self.assertTrue(started)
        self.assertGreater(cooldown_left, 0.0)

    def test_end_and_break_contracts_are_clean(self):
        self.assertEqual(
            bond_end_contract(
                patron_alive=True,
                context_ok=True,
                now=8.0,
                ends_at=20.0,
            ),
            "active",
        )
        self.assertEqual(
            bond_end_contract(
                patron_alive=True,
                context_ok=True,
                now=22.0,
                ends_at=20.0,
            ),
            "ended",
        )
        self.assertEqual(
            bond_end_contract(
                patron_alive=False,
                context_ok=True,
                now=8.0,
                ends_at=20.0,
            ),
            "broken",
        )

    def test_local_effect_is_light_but_real(self):
        boosted = bond_local_effect_contract(
            in_radius=True,
            follower_of_patron=True,
            rally_bonus_active=False,
            bonus_roll=0.0,
            bonus_chance=self.rally_bonus_chance,
            patron_renown=10.0,
            ally_renown=6.0,
            renown_pulse=self.renown_pulse,
        )
        self.assertTrue(boosted[0])
        self.assertGreater(boosted[1], 10.0)
        self.assertGreater(boosted[2], 6.0)

        out = bond_local_effect_contract(
            in_radius=False,
            follower_of_patron=True,
            rally_bonus_active=False,
            bonus_roll=0.0,
            bonus_chance=self.rally_bonus_chance,
            patron_renown=10.0,
            ally_renown=6.0,
            renown_pulse=self.renown_pulse,
        )
        self.assertFalse(out[0])
        self.assertEqual(out[1], 10.0)
        self.assertEqual(out[2], 6.0)

    def test_hooks_exist_across_runtime_hud_actor_and_docs(self):
        self.assertIn("_setup_bond_state", self.loop_content)
        self.assertIn("_update_bonds", self.loop_content)
        self.assertIn("_try_start_bond", self.loop_content)
        self.assertIn("_break_bond", self.loop_content)
        self.assertIn("_end_bond", self.loop_content)
        self.assertIn("_try_start_bond_from_legacy", self.loop_content)
        self.assertIn("_try_start_bond_from_recovery", self.loop_content)
        self.assertIn("_try_start_bond_from_rally", self.loop_content)
        self.assertIn("Bond START", self.loop_content)
        self.assertIn("Bond END", self.loop_content)
        self.assertIn("Bond BROKEN", self.loop_content)
        self.assertIn('"bond_active_total"', self.loop_content)
        self.assertIn('"bond_active_labels"', self.loop_content)

        self.assertIn("bond_patron_active", self.actor_content)
        self.assertIn("set_bond_state", self.actor_content)
        self.assertIn("bond_tag", self.actor_content)

        self.assertIn("Bonds:", self.overlay_content)
        self.assertIn("Bond links:", self.overlay_content)

        self.assertIn("bond", self.readme_content)
        self.assertIn("patron", self.readme_content)


if __name__ == "__main__":
    unittest.main()
