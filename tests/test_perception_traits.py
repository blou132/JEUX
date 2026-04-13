import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_hunger_snapshot, build_population_stats
from genetics import GeneticTraits, inherit_traits
from simulation import HungerSimulation
from world import FoodField, FoodSource


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class PerceptionTraitsTests(unittest.TestCase):
    def test_food_perception_lightly_changes_food_detection(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, food_detection_range=5.0, threat_detection_range=0.0)
        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=5.5, y=0.0, energy_value=20.0))

        high = Creature(
            creature_id="high_food_perception",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(food_perception=1.2),
        )
        low = Creature(
            creature_id="low_food_perception",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(food_perception=0.8),
        )

        high_intent = ai.decide(high, field, can_reproduce=False, nearby_creatures=[high])
        low_intent = ai.decide(low, field, can_reproduce=False, nearby_creatures=[low])

        self.assertEqual(high_intent.action, HungerAI.ACTION_MOVE_TO_FOOD)
        self.assertEqual(low_intent.action, HungerAI.ACTION_SEARCH_FOOD)

    def test_threat_perception_lightly_changes_threat_detection(self) -> None:
        ai = HungerAI(threat_detection_range=5.0, threat_strength_ratio=1.1)

        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.3, max_energy=120.0),
        )
        high = Creature(
            creature_id="high_threat_perception",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(threat_perception=1.3),
        )
        low = Creature(
            creature_id="low_threat_perception",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(threat_perception=0.7),
        )

        high_intent = ai.decide(high, FoodField(), can_reproduce=False, nearby_creatures=[high, predator])
        low_intent = ai.decide(low, FoodField(), can_reproduce=False, nearby_creatures=[low, predator])

        self.assertEqual(high_intent.action, HungerAI.ACTION_FLEE)
        self.assertNotEqual(low_intent.action, HungerAI.ACTION_FLEE)

    def test_perception_traits_are_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(food_perception=1.2, threat_perception=0.9)
        parent_b = GeneticTraits(food_perception=0.8, threat_perception=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.food_perception, 1.1)
        self.assertAlmostEqual(child.threat_perception, 1.1)

    def test_perception_traits_are_visible_in_stats_and_snapshot(self) -> None:
        creatures = [
            Creature(
                creature_id="c1",
                x=1.0,
                y=1.0,
                energy=80.0,
                traits=GeneticTraits(food_perception=1.2, threat_perception=0.8),
            ),
            Creature(
                creature_id="c2",
                x=2.0,
                y=2.0,
                energy=80.0,
                traits=GeneticTraits(food_perception=0.8, threat_perception=1.2),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(food_detection_range=10.0, threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(77),
        )
        sim.tick(1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_food_perception", stats)
        self.assertIn("avg_threat_perception", stats)
        self.assertIn("std_food_perception", stats)
        self.assertIn("std_threat_perception", stats)
        self.assertAlmostEqual(float(stats["avg_food_perception"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_threat_perception"]), 1.0)
        self.assertGreater(float(stats["std_food_perception"]), 0.0)
        self.assertGreater(float(stats["std_threat_perception"]), 0.0)

        row = snapshot["creatures"][0]
        traits = row["traits"]
        self.assertIn("food_perception", traits)
        self.assertIn("threat_perception", traits)


if __name__ == "__main__":
    unittest.main()
