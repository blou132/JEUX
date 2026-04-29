import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import build_hunger_snapshot, build_population_stats
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField, FoodSource


class LocalMemoryBehaviorTests(unittest.TestCase):
    def test_food_memory_is_recorded_when_food_is_eaten(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=0.5, y=0.0, energy_value=20.0))

        sim = HungerSimulation(
            creatures=[creature],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        sim.tick(dt=1.0)

        self.assertTrue(creature.has_food_memory)
        self.assertIsNotNone(creature.last_food_zone)
        assert creature.last_food_zone is not None
        self.assertAlmostEqual(creature.last_food_zone[0], 0.5, places=3)
        self.assertAlmostEqual(creature.last_food_zone[1], 0.0, places=3)
        self.assertGreater(creature.food_memory_ttl, 0.0)

    def test_search_food_uses_nearby_food_memory(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        creature.remember_food_zone(6.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=3.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        before = creature.distance_to(6.0, 0.0)
        sim.tick(dt=1.0)
        after = creature.distance_to(6.0, 0.0)

        self.assertEqual(sim.last_intents["c1"].action, HungerAI.ACTION_SEARCH_FOOD)
        self.assertLess(after, before)
        self.assertEqual(sim.food_memory_guided_moves_last_tick, 1)
        self.assertEqual(sim.total_food_memory_guided_moves, 1)

    def test_wander_avoids_nearby_danger_memory(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=90.0, max_energy=100.0)
        creature.remember_danger_zone(1.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        before = creature.distance_to(1.0, 0.0)
        sim.tick(dt=1.0)
        after = creature.distance_to(1.0, 0.0)

        self.assertEqual(sim.last_intents["c1"].action, HungerAI.ACTION_WANDER)
        self.assertGreater(after, before)
        self.assertEqual(sim.danger_memory_avoid_moves_last_tick, 1)
        self.assertEqual(sim.total_danger_memory_avoid_moves, 1)

    def test_memory_can_be_neutralized_with_zero_duration(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        field = FoodField()
        field.add_food(FoodSource(food_id="f1", x=0.5, y=0.0, energy_value=30.0))

        sim = HungerSimulation(
            creatures=[creature],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            food_memory_duration=0.0,
            danger_memory_duration=0.0,
        )

        sim.tick(dt=1.0)
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        self.assertFalse(creature.has_food_memory)
        self.assertFalse(creature.has_danger_memory)
        self.assertEqual(sim.total_food_memory_guided_moves, 0)
        self.assertEqual(sim.total_danger_memory_avoid_moves, 0)
        self.assertAlmostEqual(float(stats["food_memory_usage_per_tick_total"]), 0.0)
        self.assertAlmostEqual(float(stats["danger_memory_usage_per_tick_total"]), 0.0)

    def test_debug_exposes_memory_counters_and_fields(self) -> None:
        creature = Creature(creature_id="c1", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        creature.remember_food_zone(4.0, 0.0, ttl=8.0)

        sim = HungerSimulation(
            creatures=[creature],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        sim.tick(dt=1.0)
        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("creatures_with_food_memory", stats)
        self.assertIn("food_memory_guided_moves_last_tick", stats)
        self.assertIn("danger_memory_avoid_moves_last_tick", stats)
        self.assertGreaterEqual(int(stats["creatures_with_food_memory"]), 1)

        row = snapshot["creatures"][0]
        self.assertIn("has_food_memory", row)
        self.assertIn("food_memory_zone", row)
        self.assertIn("food_memory_ttl", row)


if __name__ == "__main__":
    unittest.main()

