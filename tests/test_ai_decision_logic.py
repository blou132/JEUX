import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.world import FoodField, FoodSource


class AiDecisionLogicTests(unittest.TestCase):
    def test_hungry_and_food_near_moves_to_food(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, food_detection_range=5.0)
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=3.0, y=0.0, energy_value=20.0))

        intent = ai.decide(creature, field, can_reproduce=True)
        self.assertEqual(intent.action, "move_to_food")
        self.assertEqual(intent.target_food_id, "f1")

    def test_hungry_and_food_far_searches_food(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0)
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=10.0, y=0.0, energy_value=20.0))

        intent = ai.decide(creature, field, can_reproduce=True)
        self.assertEqual(intent.action, "search_food")

    def test_reproduction_when_not_hungry_and_conditions_met(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6)
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=90.0, max_energy=100.0)

        intent = ai.decide(creature, FoodField(), can_reproduce=True)
        self.assertEqual(intent.action, "reproduce")

    def test_wander_when_no_other_priority(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6)
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=90.0, max_energy=100.0)

        intent = ai.decide(creature, FoodField(), can_reproduce=False)
        self.assertEqual(intent.action, "wander")


if __name__ == "__main__":
    unittest.main()

