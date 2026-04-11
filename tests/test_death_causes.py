import unittest

from ai import HungerAI
from creatures import Creature
from simulation import HungerSimulation
from world import FoodField


class DeathCauseAggregationTests(unittest.TestCase):
    def test_starvation_death_is_counted(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=1.0, max_energy=10.0)
        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=2.0,
            reproduction_energy_threshold=50.0,
            reproduction_cost=10.0,
        )

        sim.tick(dt=1.0)

        self.assertEqual(sim.deaths_last_tick, 1)
        self.assertEqual(sim.death_causes_last_tick["starvation"], 1)
        self.assertEqual(sim.death_causes_last_tick["exhaustion"], 0)
        self.assertEqual(sim.death_causes_last_tick["unknown"], 0)
        self.assertEqual(sim.total_death_causes["starvation"], 1)

    def test_reproduction_exhaustion_death_is_counted(self) -> None:
        parent_a = Creature(creature_id="p1", x=0.0, y=0.0, energy=10.0, max_energy=10.0)
        parent_b = Creature(creature_id="p2", x=0.5, y=0.0, energy=10.0, max_energy=10.0)

        sim = HungerSimulation(
            creatures=[parent_a, parent_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=10.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            mutation_variation=0.1,
        )

        sim.tick(dt=1.0)

        self.assertEqual(sim.births_last_tick, 1)
        self.assertEqual(sim.deaths_last_tick, 2)
        self.assertEqual(sim.death_causes_last_tick["starvation"], 0)
        self.assertEqual(sim.death_causes_last_tick["exhaustion"], 2)
        self.assertEqual(sim.death_causes_last_tick["unknown"], 0)
        self.assertEqual(sim.total_death_causes["exhaustion"], 2)


if __name__ == "__main__":
    unittest.main()
