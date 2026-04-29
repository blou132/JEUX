import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature, create_initial_population
from legacy_python.debug_tools import build_hunger_snapshot
from legacy_python.genetics import GeneticTraits, inherit_traits
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField, FoodSpawnConfig, SimpleMap, SimpleWorld


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class BehaviorTraitsTests(unittest.TestCase):
    def test_prudence_and_dominance_influence_flee_decision(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=120.0),
        )

        cautious = Creature(
            creature_id="cautious",
            x=5.0,
            y=5.0,
            energy=80.0,
            traits=GeneticTraits(
                speed=1.0,
                metabolism=1.0,
                max_energy=100.0,
                prudence=1.6,
                dominance=0.6,
                repro_drive=1.0,
            ),
        )
        bold = Creature(
            creature_id="bold",
            x=5.0,
            y=5.0,
            energy=80.0,
            traits=GeneticTraits(
                speed=1.0,
                metabolism=1.0,
                max_energy=100.0,
                prudence=0.6,
                dominance=1.6,
                repro_drive=1.0,
            ),
        )

        ai = HungerAI(threat_detection_range=10.0, threat_strength_ratio=1.15)

        cautious_intent = ai.decide(cautious, FoodField(), can_reproduce=False, nearby_creatures=[cautious, predator])
        bold_intent = ai.decide(bold, FoodField(), can_reproduce=False, nearby_creatures=[bold, predator])

        self.assertEqual(cautious_intent.action, HungerAI.ACTION_FLEE)
        self.assertNotEqual(bold_intent.action, HungerAI.ACTION_FLEE)

    def test_repro_drive_influences_reproduction_priority(self) -> None:
        low_drive = Creature(
            creature_id="low",
            x=0.0,
            y=0.0,
            energy=44.0,
            traits=GeneticTraits(
                speed=1.0,
                metabolism=1.0,
                max_energy=100.0,
                prudence=1.0,
                dominance=1.0,
                repro_drive=0.6,
            ),
        )
        high_drive = Creature(
            creature_id="high",
            x=0.0,
            y=0.0,
            energy=44.0,
            traits=GeneticTraits(
                speed=1.0,
                metabolism=1.0,
                max_energy=100.0,
                prudence=1.0,
                dominance=1.0,
                repro_drive=1.6,
            ),
        )

        ai = HungerAI(hunger_seek_threshold=0.6)
        low_intent = ai.decide(low_drive, FoodField(), can_reproduce=True, nearby_creatures=[low_drive])
        high_intent = ai.decide(high_drive, FoodField(), can_reproduce=True, nearby_creatures=[high_drive])

        self.assertEqual(low_intent.action, HungerAI.ACTION_WANDER)
        self.assertEqual(high_intent.action, HungerAI.ACTION_REPRODUCE)

    def test_behavior_traits_are_inherited_with_mutation(self) -> None:
        parent_a = GeneticTraits(prudence=1.2, dominance=0.8, repro_drive=1.1)
        parent_b = GeneticTraits(prudence=0.8, dominance=1.2, repro_drive=0.9)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.prudence, ((1.2 + 0.8) / 2.0) * 1.1)
        self.assertAlmostEqual(child.dominance, ((0.8 + 1.2) / 2.0) * 1.1)
        self.assertAlmostEqual(child.repro_drive, ((1.1 + 0.9) / 2.0) * 1.1)

    def test_debug_exposes_behavior_traits_and_effects(self) -> None:
        prey = Creature(
            creature_id="prey",
            x=5.0,
            y=5.0,
            energy=70.0,
            traits=GeneticTraits(
                speed=1.0,
                metabolism=1.0,
                max_energy=100.0,
                prudence=1.4,
                dominance=0.7,
                repro_drive=1.2,
            ),
        )
        predator = Creature(
            creature_id="predator",
            x=6.0,
            y=5.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=120.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(31),
        )
        sim.tick(1.0)

        snapshot = build_hunger_snapshot(sim)
        prey_row = next(row for row in snapshot["creatures"] if row["id"] == "prey")

        self.assertEqual(prey_row["intent"], HungerAI.ACTION_FLEE)
        self.assertEqual(prey_row["action_reason"], "threat_detected")
        self.assertIn("prudence", prey_row["traits"])
        self.assertIn("dominance", prey_row["traits"])
        self.assertIn("repro_drive", prey_row["traits"])

    def test_short_simulation_remains_stable_with_behavior_traits(self) -> None:
        rng = random.Random(123)
        world_map = SimpleMap(60.0, 40.0)
        world = SimpleWorld(
            world_map=world_map,
            spawn_config=FoodSpawnConfig(initial_food_count=50, min_food_count=30),
            random_source=rng,
        )
        creatures = create_initial_population(20, world_map, rng)

        sim = HungerSimulation(
            creatures=creatures,
            food_field=world.food_field,
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=1.2,
            movement_speed=1.0,
            eat_rate=26.0,
            reproduction_energy_threshold=58.0,
            reproduction_cost=12.0,
            reproduction_distance=15.0,
            mutation_variation=0.1,
            random_source=rng,
            world_map=world_map,
        )

        for _ in range(120):
            world.tick()
            sim.tick(1.0)
            if sim.get_alive_count() == 0:
                break

        self.assertGreaterEqual(sim.get_total_count(), sim.get_alive_count())
        self.assertGreaterEqual(sim.total_births, 0)


if __name__ == "__main__":
    unittest.main()



