import random
import unittest

from ai import HungerAI
from creatures import create_initial_population
from simulation import HungerSimulation
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


class GenerationDepthMvpTests(unittest.TestCase):
    def test_default_mvp_parameters_reach_generation_10(self) -> None:
        rng = random.Random(42)
        world_map = SimpleMap(60.0, 40.0)
        world = SimpleWorld(
            world_map=world_map,
            spawn_config=FoodSpawnConfig(initial_food_count=50, min_food_count=30),
            random_source=rng,
        )
        creatures = create_initial_population(20, world_map, rng)

        simulation = HungerSimulation(
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

        for _ in range(400):
            world.tick()
            simulation.tick(1.0)
            if simulation.get_alive_count() == 0:
                break

        max_generation = max((c.generation for c in simulation.creatures), default=0)
        self.assertGreaterEqual(max_generation, 10)


if __name__ == "__main__":
    unittest.main()
