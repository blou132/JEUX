import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField


class ReproductionMaturityTests(unittest.TestCase):
    def test_reproduction_requires_minimum_age(self) -> None:
        parent_a = Creature(
            creature_id="p1",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
            age=2.0,
        )
        parent_b = Creature(
            creature_id="p2",
            x=0.5,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
            age=2.0,
        )

        sim = HungerSimulation(
            creatures=[parent_a, parent_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=70.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            reproduction_min_age=5.0,
            mutation_variation=0.1,
        )

        sim.tick(dt=1.0)
        self.assertEqual(len(sim.creatures), 2)
        self.assertEqual(sim.total_births, 0)

    def test_reproduction_happens_after_min_age(self) -> None:
        parent_a = Creature(
            creature_id="p1",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
            age=5.0,
        )
        parent_b = Creature(
            creature_id="p2",
            x=0.5,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
            age=5.0,
        )

        sim = HungerSimulation(
            creatures=[parent_a, parent_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=70.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            reproduction_min_age=5.0,
            mutation_variation=0.1,
        )

        sim.tick(dt=1.0)
        self.assertEqual(len(sim.creatures), 3)
        self.assertEqual(sim.total_births, 1)


if __name__ == "__main__":
    unittest.main()

