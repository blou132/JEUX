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


class EnergyTraitsTests(unittest.TestCase):
    def test_energy_efficiency_lightly_modulates_passive_drain(self) -> None:
        high_eff = Creature(
            creature_id="high_eff",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(metabolism=1.0, energy_efficiency=1.1, max_energy=100.0),
        )
        low_eff = Creature(
            creature_id="low_eff",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(metabolism=1.0, energy_efficiency=0.9, max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[high_eff, low_eff],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(901),
        )

        sim.tick(dt=1.0)

        self.assertAlmostEqual(high_eff.energy, 100.0 - (10.0 * 0.975), places=4)
        self.assertAlmostEqual(low_eff.energy, 100.0 - (10.0 * 1.025), places=4)
        self.assertGreater(high_eff.energy, low_eff.energy)

    def test_exhaustion_resistance_lightly_modulates_reproduction_cost(self) -> None:
        high_a = Creature(
            creature_id="ha",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=1.1),
        )
        high_b = Creature(
            creature_id="hb",
            x=0.5,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=1.1),
        )

        low_a = Creature(
            creature_id="la",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=0.9),
        )
        low_b = Creature(
            creature_id="lb",
            x=0.5,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=0.9),
        )

        sim_high = HungerSimulation(
            creatures=[high_a, high_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=10.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            random_source=random.Random(902),
        )
        sim_low = HungerSimulation(
            creatures=[low_a, low_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=10.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            random_source=random.Random(903),
        )

        sim_high.tick(dt=1.0)
        sim_low.tick(dt=1.0)

        self.assertEqual(sim_high.total_births, 1)
        self.assertTrue(high_a.alive)
        self.assertTrue(high_b.alive)

        self.assertEqual(sim_low.total_births, 1)
        self.assertFalse(low_a.alive)
        self.assertFalse(low_b.alive)
        self.assertEqual(int(sim_low.death_causes_last_tick[HungerSimulation.DEATH_CAUSE_EXHAUSTION]), 2)

    def test_energy_traits_are_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(energy_efficiency=1.1, exhaustion_resistance=1.2)
        parent_b = GeneticTraits(energy_efficiency=0.9, exhaustion_resistance=0.8)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.energy_efficiency, 1.1)
        self.assertAlmostEqual(child.exhaustion_resistance, 1.1)

    def test_energy_traits_are_visible_in_stats_and_snapshot(self) -> None:
        creatures = [
            Creature(
                creature_id="c1",
                x=0.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(energy_efficiency=1.1, exhaustion_resistance=1.2),
            ),
            Creature(
                creature_id="c2",
                x=1.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(energy_efficiency=0.9, exhaustion_resistance=0.8),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_energy_efficiency", stats)
        self.assertIn("avg_exhaustion_resistance", stats)
        self.assertIn("std_energy_efficiency", stats)
        self.assertIn("std_exhaustion_resistance", stats)
        self.assertIn("avg_effective_energy_drain_multiplier", stats)
        self.assertIn("avg_reproduction_cost_multiplier", stats)
        self.assertAlmostEqual(float(stats["avg_energy_efficiency"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_exhaustion_resistance"]), 1.0)
        self.assertGreater(float(stats["std_energy_efficiency"]), 0.0)
        self.assertGreater(float(stats["std_exhaustion_resistance"]), 0.0)

        row = snapshot["creatures"][0]
        traits = row["traits"]
        self.assertIn("energy_efficiency", traits)
        self.assertIn("exhaustion_resistance", traits)


if __name__ == "__main__":
    unittest.main()

