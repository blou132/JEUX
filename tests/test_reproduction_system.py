import unittest

from ai import HungerAI
from creatures import Creature
from genetics import GeneticTraits
from simulation import HungerSimulation
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        # Always returns the max mutation to make variation deterministic in tests.
        return b


class ReproductionSystemTests(unittest.TestCase):
    def test_child_inherits_parent_traits(self) -> None:
        parent_a = Creature(
            creature_id="p1",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.2, metabolism=0.9, max_energy=120.0),
        )
        parent_b = Creature(
            creature_id="p2",
            x=0.5,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=0.8, metabolism=1.1, max_energy=80.0),
        )

        sim = HungerSimulation(
            creatures=[parent_a, parent_b],
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=70.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            mutation_variation=0.1,
            random_source=FixedRandom(),
        )

        sim.tick(dt=1.0)

        self.assertEqual(len(sim.creatures), 3)
        child = sim.creatures[-1]
        self.assertEqual(child.parent_ids, ("p1", "p2"))
        self.assertEqual(child.generation, 1)

        avg_speed = (1.2 + 0.8) / 2.0
        avg_metabolism = (0.9 + 1.1) / 2.0
        avg_max_energy = (120.0 + 80.0) / 2.0

        self.assertAlmostEqual(child.traits.speed, avg_speed * 1.1)
        self.assertAlmostEqual(child.traits.metabolism, avg_metabolism * 1.1)
        self.assertAlmostEqual(child.traits.max_energy, avg_max_energy * 1.1)

    def test_variation_observable_between_generations(self) -> None:
        parent_a = Creature(
            creature_id="p1",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        parent_b = Creature(
            creature_id="p2",
            x=0.4,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[parent_a, parent_b],
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=70.0,
            reproduction_cost=10.0,
            reproduction_distance=1.0,
            mutation_variation=0.15,
            random_source=FixedRandom(),
        )

        sim.tick(dt=1.0)
        child = sim.creatures[-1]

        self.assertNotEqual(child.traits.speed, parent_a.traits.speed)
        self.assertNotEqual(child.traits.metabolism, parent_a.traits.metabolism)
        self.assertNotEqual(child.traits.max_energy, parent_a.traits.max_energy)


if __name__ == "__main__":
    unittest.main()
