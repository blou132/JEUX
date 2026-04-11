import random
import unittest

from ai import HungerAI
from creatures import create_initial_population
from simulation import HungerSimulation
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


class FoodDistributionPressureTests(unittest.TestCase):
    def test_food_distribution_is_non_uniform_and_stable(self) -> None:
        rng = random.Random(123)
        world = SimpleWorld(
            world_map=SimpleMap(width=60.0, height=40.0),
            spawn_config=FoodSpawnConfig(
                initial_food_count=0,
                min_food_count=0,
                spawn_candidate_count=5,
            ),
            random_source=rng,
        )

        world.seed_food(400)
        zone_stats = world.get_food_zone_stats()

        self.assertEqual(zone_stats["total"], 400)
        self.assertGreater(zone_stats["rich"], zone_stats["poor"])
        self.assertGreater(float(zone_stats["avg_fertility"]), 1.0)

    def test_distribution_is_reproducible_for_same_seed(self) -> None:
        config = FoodSpawnConfig(initial_food_count=120, min_food_count=30)

        world_a = SimpleWorld(
            world_map=SimpleMap(width=60.0, height=40.0),
            spawn_config=config,
            random_source=random.Random(99),
        )
        world_b = SimpleWorld(
            world_map=SimpleMap(width=60.0, height=40.0),
            spawn_config=config,
            random_source=random.Random(99),
        )

        snapshot_a = [
            (round(source.x, 4), round(source.y, 4), round(source.energy_value, 4))
            for source in world_a.food_field.iter_sources()
        ]
        snapshot_b = [
            (round(source.x, 4), round(source.y, 4), round(source.energy_value, 4))
            for source in world_b.food_field.iter_sources()
        ]

        self.assertEqual(snapshot_a, snapshot_b)
        self.assertEqual(world_a.get_food_zone_stats(), world_b.get_food_zone_stats())

    def test_distribution_works_with_existing_simulation_loop(self) -> None:
        rng = random.Random(7)
        world_map = SimpleMap(width=60.0, height=40.0)
        world = SimpleWorld(
            world_map=world_map,
            spawn_config=FoodSpawnConfig(initial_food_count=50, min_food_count=30),
            random_source=rng,
        )
        creatures = create_initial_population(count=20, world_map=world_map, random_source=rng)
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

        for _ in range(80):
            world.tick()
            simulation.tick(1.0)
            if simulation.get_alive_count() == 0:
                break

        self.assertEqual(simulation.get_total_count(), simulation.get_alive_count() + simulation.get_dead_count())
        self.assertGreaterEqual(world.food_field.get_food_count(), 0)


if __name__ == "__main__":
    unittest.main()
