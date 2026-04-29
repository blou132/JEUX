import math
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField, FoodSource


class MovementBehaviorTests(unittest.TestCase):
    def test_move_to_food_reduces_distance_to_target(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=20.0, max_energy=100.0)
        food = FoodField()
        food.add_food(FoodSource(food_id="f1", x=10.0, y=0.0, energy_value=50.0))

        sim = HungerSimulation(
            creatures=[creature],
            food_field=food,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=30.0),
            energy_drain_rate=0.0,
            movement_speed=2.0,
        )

        before = creature.distance_to(10.0, 0.0)
        sim.tick(dt=1.0)
        after = creature.distance_to(10.0, 0.0)

        self.assertEqual(sim.last_intents["c1"].action, "move_to_food")
        self.assertLess(after, before)

    def test_wander_moves_when_no_food_target(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=90.0, max_energy=100.0)

        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        sim.tick(dt=1.0)
        moved_distance = math.hypot(creature.x, creature.y)

        self.assertEqual(sim.last_intents["c1"].action, "wander")
        self.assertGreater(moved_distance, 0.0)

    def test_search_food_moves_faster_than_wander(self) -> None:
        hungry = Creature(creature_id="h", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        calm = Creature(creature_id="c", x=0.0, y=0.0, energy=90.0, max_energy=100.0)

        field = FoodField()
        # Exists but outside visibility to trigger search_food, not move_to_food.
        field.add_food(FoodSource(food_id="f_far", x=100.0, y=100.0, energy_value=30.0))

        sim_hungry = HungerSimulation(
            creatures=[hungry],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=5.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )
        sim_calm = HungerSimulation(
            creatures=[calm],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        sim_hungry.tick(dt=1.0)
        sim_calm.tick(dt=1.0)

        search_distance = math.hypot(hungry.x, hungry.y)
        wander_distance = math.hypot(calm.x, calm.y)

        self.assertEqual(sim_hungry.last_intents["h"].action, "search_food")
        self.assertEqual(sim_calm.last_intents["c"].action, "wander")
        self.assertGreater(search_distance, wander_distance)


if __name__ == "__main__":
    unittest.main()

