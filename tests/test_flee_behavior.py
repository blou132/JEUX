import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import build_hunger_snapshot
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField, FoodSource


class FleeBehaviorTests(unittest.TestCase):
    def test_threat_detection_triggers_flee_with_target(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=70.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=40.0,
            traits=GeneticTraits(speed=1.3, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(10),
        )

        sim.tick(1.0)

        intent = sim.last_intents["prey"]
        self.assertEqual(intent.action, HungerAI.ACTION_FLEE)
        self.assertEqual(intent.target_creature_id, "predator")

    def test_flee_priority_over_food_and_reproduction(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=40.0,
            traits=GeneticTraits(speed=1.3, metabolism=1.0, max_energy=140.0),
        )

        food_field = FoodField()
        food_field.add_food(FoodSource(food_id="food_1", x=5.2, y=5.0, energy_value=100.0))

        ai_system = HungerAI(hunger_seek_threshold=0.6, food_detection_range=18.0, threat_detection_range=10.0)
        intent = ai_system.decide(
            creature=prey,
            food_field=food_field,
            can_reproduce=True,
            nearby_creatures=[prey, predator],
        )

        self.assertEqual(intent.action, HungerAI.ACTION_FLEE)

    def test_flee_movement_increases_distance_from_initial_threat_position(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=70.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=40.0,
            traits=GeneticTraits(speed=1.3, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(11),
        )

        predator_start_x = predator.x
        predator_start_y = predator.y
        before = prey.distance_to(predator_start_x, predator_start_y)

        sim.tick(1.0)

        after = prey.distance_to(predator_start_x, predator_start_y)

        self.assertEqual(sim.last_intents["prey"].action, HungerAI.ACTION_FLEE)
        self.assertGreater(after, before)

    def test_flee_stops_when_threat_disappears(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=70.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=40.0,
            traits=GeneticTraits(speed=1.3, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(12),
        )

        sim.tick(1.0)
        self.assertEqual(sim.last_intents["prey"].action, HungerAI.ACTION_FLEE)

        predator.energy = predator.max_energy
        sim.tick(1.0)

        self.assertNotEqual(sim.last_intents["prey"].action, HungerAI.ACTION_FLEE)

    def test_debug_snapshot_exposes_flee_reason_and_threat_distance(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=70.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=40.0,
            traits=GeneticTraits(speed=1.3, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(13),
        )

        sim.tick(1.0)
        snapshot = build_hunger_snapshot(sim)

        prey_row = next(row for row in snapshot["creatures"] if row["id"] == "prey")
        self.assertEqual(prey_row["intent"], HungerAI.ACTION_FLEE)
        self.assertEqual(prey_row["action_reason"], "threat_detected")
        self.assertEqual(prey_row["threat_target_id"], "predator")
        self.assertIsNotNone(prey_row["threat_distance"])
        self.assertGreater(prey_row["threat_distance"], 0.0)


if __name__ == "__main__":
    unittest.main()

