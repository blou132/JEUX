import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_hunger_snapshot, build_population_stats
from genetics import GeneticTraits, inherit_traits
from simulation import HungerSimulation
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class DensityPreferenceTraitTests(unittest.TestCase):
    def _run_single_creature(self, density_preference: float, seed: int) -> tuple[HungerSimulation, float, float]:
        subject = Creature(
            creature_id="subject",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(density_preference=density_preference, max_energy=100.0),
        )
        n1 = Creature(
            creature_id="n1",
            x=3.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        n2 = Creature(
            creature_id="n2",
            x=3.0,
            y=1.0,
            energy=80.0,
            traits=GeneticTraits(max_energy=100.0),
        )
        center_x = (n1.x + n2.x) / 2.0
        center_y = (n1.y + n2.y) / 2.0

        sim = HungerSimulation(
            creatures=[subject, n1, n2],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(seed),
        )

        before = subject.distance_to(center_x, center_y)
        sim.tick(dt=1.0)
        after = subject.distance_to(center_x, center_y)
        return sim, before, after

    def test_density_preference_influences_wander_by_local_density(self) -> None:
        sim_seek, before_seek, after_seek = self._run_single_creature(1.3, seed=77)
        sim_avoid, before_avoid, after_avoid = self._run_single_creature(0.7, seed=77)

        self.assertEqual(sim_seek.last_intents["subject"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_avoid.last_intents["subject"].action, HungerAI.ACTION_WANDER)

        self.assertEqual(sim_seek.density_preference_guided_moves_last_tick, 1)
        self.assertEqual(sim_seek.density_preference_seek_moves_last_tick, 1)
        self.assertEqual(sim_avoid.density_preference_guided_moves_last_tick, 1)
        self.assertEqual(sim_avoid.density_preference_avoid_moves_last_tick, 1)

        self.assertLess(after_seek, before_seek)
        self.assertGreater(after_avoid, before_avoid)

    def test_density_preference_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(density_preference=0.9)
        parent_b = GeneticTraits(density_preference=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.density_preference, 1.1)

    def test_density_preference_is_visible_in_stats_and_snapshot(self) -> None:
        creatures = [
            Creature(
                creature_id="high",
                x=0.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(density_preference=1.2, max_energy=100.0),
            ),
            Creature(
                creature_id="low",
                x=0.5,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(density_preference=0.8, max_energy=100.0),
            ),
            Creature(
                creature_id="n1",
                x=2.8,
                y=0.4,
                energy=80.0,
                traits=GeneticTraits(max_energy=100.0),
            ),
            Creature(
                creature_id="n2",
                x=2.8,
                y=-0.4,
                energy=80.0,
                traits=GeneticTraits(max_energy=100.0),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(123),
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_density_preference", stats)
        self.assertIn("std_density_preference", stats)
        self.assertIn("density_preference_guided_moves_last_tick", stats)
        self.assertIn("density_preference_seek_moves_last_tick", stats)
        self.assertIn("density_preference_avoid_moves_last_tick", stats)
        self.assertIn("density_preference_seek_usage_bias_tick", stats)
        self.assertIn("density_preference_seek_usage_per_tick_total", stats)
        self.assertIn("density_preference_avoid_usage_per_tick_total", stats)
        self.assertIn("density_preference_avoid_share_last_tick", stats)
        self.assertIn("avg_density_preference_neighbor_count_last_tick", stats)
        self.assertIn("avg_density_preference_center_distance_delta_last_tick", stats)

        self.assertGreater(float(stats["std_density_preference"]), 0.0)
        self.assertGreater(int(stats["density_preference_guided_moves_last_tick"]), 0)
        self.assertGreater(int(stats["density_preference_seek_moves_last_tick"]), 0)
        self.assertGreater(int(stats["density_preference_avoid_moves_last_tick"]), 0)
        self.assertGreaterEqual(float(stats["density_preference_avoid_share_last_tick"]), 0.0)
        self.assertLessEqual(float(stats["density_preference_avoid_share_last_tick"]), 1.0)

        row = snapshot["creatures"][0]
        self.assertIn("density_preference", row["traits"])


if __name__ == "__main__":
    unittest.main()
