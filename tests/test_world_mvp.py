import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodSource, FoodSpawnConfig, SimpleMap, SimpleWorld


class WorldMvpTests(unittest.TestCase):
    def test_world_respawns_food_to_minimum(self) -> None:
        world = SimpleWorld(
            world_map=SimpleMap(width=10.0, height=10.0),
            spawn_config=FoodSpawnConfig(initial_food_count=2, min_food_count=5),
        )

        self.assertEqual(world.food_field.get_food_count(), 2)
        world.tick()
        self.assertEqual(world.food_field.get_food_count(), 5)

    def test_map_clamps_creature_position(self) -> None:
        world_map = SimpleMap(width=2.0, height=2.0)
        world = SimpleWorld(
            world_map=world_map,
            spawn_config=FoodSpawnConfig(initial_food_count=0, min_food_count=0),
        )
        world.food_field.add_food(FoodSource(food_id="out", x=5.0, y=5.0, energy_value=50.0))

        creature = Creature(creature_id="c1", x=1.9, y=1.9, energy=10.0)
        sim = HungerSimulation(
            creatures=[creature],
            food_field=world.food_field,
            ai_system=HungerAI(hunger_seek_threshold=0.0),
            energy_drain_rate=0.0,
            movement_speed=10.0,
            world_map=world_map,
        )

        sim.tick(dt=1.0)
        self.assertGreaterEqual(creature.x, 0.0)
        self.assertLessEqual(creature.x, world_map.width)
        self.assertGreaterEqual(creature.y, 0.0)
        self.assertLessEqual(creature.y, world_map.height)


if __name__ == "__main__":
    unittest.main()

