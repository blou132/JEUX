import random
import unittest

from ai import HungerAI
from creatures import Creature, create_initial_population
from genetics import GeneticTraits
from simulation import HungerSimulation
from world import FoodField, FoodSpawnConfig, SimpleMap, SimpleWorld


class PredatorPreyFleeTests(unittest.TestCase):
    def test_creature_flees_when_threat_detected(self) -> None:
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
            traits=GeneticTraits(speed=1.2, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
        )

        sim.tick(dt=1.0)

        self.assertEqual(sim.last_intents["prey"].action, HungerAI.ACTION_FLEE)
        self.assertEqual(sim.flees_last_tick, 1)

    def test_creature_does_not_flee_without_threat(self) -> None:
        creature_a = Creature(
            creature_id="a",
            x=5.0,
            y=5.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        creature_b = Creature(
            creature_id="b",
            x=6.0,
            y=5.0,
            energy=90.0,
            traits=GeneticTraits(speed=0.9, metabolism=1.0, max_energy=90.0),
        )

        sim = HungerSimulation(
            creatures=[creature_a, creature_b],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
        )

        sim.tick(dt=1.0)

        self.assertNotEqual(sim.last_intents["a"].action, HungerAI.ACTION_FLEE)
        self.assertEqual(sim.last_intents["a"].action, HungerAI.ACTION_WANDER)

    def test_flee_moves_away_from_threat(self) -> None:
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
            traits=GeneticTraits(speed=1.2, metabolism=1.0, max_energy=140.0),
        )

        sim = HungerSimulation(
            creatures=[prey, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            reproduction_energy_threshold=200.0,
        )

        before_distance = prey.distance_to(predator.x, predator.y)
        sim.tick(dt=1.0)
        after_distance = prey.distance_to(predator.x, predator.y)

        self.assertEqual(sim.last_intents["prey"].action, HungerAI.ACTION_FLEE)
        self.assertGreater(after_distance, before_distance)
        self.assertLess(prey.x, 5.0)

    def test_flee_does_not_block_overall_reproduction_and_survival(self) -> None:
        rng = random.Random(42)
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
            ai_system=HungerAI(hunger_seek_threshold=0.6, threat_detection_range=5.0),
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

        for _ in range(200):
            world.tick()
            sim.tick(1.0)
            if sim.get_alive_count() == 0:
                break

        max_generation = max((c.generation for c in sim.creatures), default=0)

        self.assertGreater(sim.total_flees, 0)
        self.assertGreater(sim.total_births, 0)
        self.assertGreater(sim.get_alive_count(), 0)
        self.assertGreaterEqual(max_generation, 2)


if __name__ == "__main__":
    unittest.main()
