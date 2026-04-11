import unittest

from ai import HungerAI
from creatures import Creature
from simulation import HungerSimulation
from world import FoodField, FoodSource


class HungerSystemTests(unittest.TestCase):
    def test_energy_decreases_with_time(self) -> None:
        creature = Creature(creature_id="c1", x=0, y=0, energy=10, max_energy=10)
        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=2.0,
        )

        sim.tick(dt=1.5)
        self.assertAlmostEqual(creature.energy, 7.0)
        self.assertTrue(creature.alive)

    def test_hungry_creature_targets_food(self) -> None:
        creature = Creature(creature_id="c1", x=0, y=0, energy=20, max_energy=100)
        food = FoodField()
        food.add_food(FoodSource(food_id="f1", x=10, y=0, energy_value=30))
        sim = HungerSimulation(
            creatures=[creature],
            food_field=food,
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        sim.tick(dt=1.0)
        self.assertEqual(sim.last_intents["c1"].action, "move_to_food")

    def test_consuming_food_restores_energy_and_reduces_food(self) -> None:
        creature = Creature(creature_id="c1", x=0, y=0, energy=20, max_energy=100)
        food = FoodField()
        food.add_food(FoodSource(food_id="f1", x=0, y=0, energy_value=10))

        sim = HungerSimulation(
            creatures=[creature],
            food_field=food,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=5.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            eat_rate=10.0,
        )

        sim.tick(dt=1.0)
        self.assertGreater(creature.energy, 20.0)
        self.assertEqual(food.get_food_count(), 0)

    def test_creature_dies_at_zero_energy(self) -> None:
        creature = Creature(creature_id="c1", x=0, y=0, energy=1, max_energy=10)
        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=2.0,
        )

        sim.tick(dt=1.0)
        self.assertEqual(creature.energy, 0.0)
        self.assertFalse(creature.alive)
        self.assertEqual(sim.last_intents["c1"].action, "dead")


if __name__ == "__main__":
    unittest.main()
