import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature, create_initial_population
from legacy_python.debug_tools import build_population_stats
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_proto_groups_by_fertility_zone
from legacy_python.world import FoodField, FoodSpawnConfig, SimpleMap, SimpleWorld


class ProtoGroupEcologyObservationTests(unittest.TestCase):
    def _find_zone_point(self, world: SimpleWorld, zone_name: str) -> tuple[float, float]:
        for y_index in range(1, 40):
            y = world.map.height * (y_index / 40.0)
            for x_index in range(1, 40):
                x = world.map.width * (x_index / 40.0)
                if world.get_fertility_zone(x, y) == zone_name:
                    return x, y
        raise AssertionError(f"zone not found: {zone_name}")

    def test_zone_distribution_and_zone_dominants_are_present(self) -> None:
        world = SimpleWorld(
            world_map=SimpleMap(60.0, 40.0),
            spawn_config=FoodSpawnConfig(initial_food_count=0, min_food_count=0),
            random_source=random.Random(11),
        )

        rich_x, rich_y = self._find_zone_point(world, "rich")
        poor_x, poor_y = self._find_zone_point(world, "poor")

        group_a = GeneticTraits(
            speed=1.0,
            metabolism=1.0,
            max_energy=100.0,
            prudence=1.0,
            dominance=1.0,
            repro_drive=1.0,
        )
        group_b = GeneticTraits(
            speed=1.4,
            metabolism=1.2,
            max_energy=110.0,
            prudence=1.3,
            dominance=0.7,
            repro_drive=1.2,
        )

        creatures = [
            Creature("rich_a1", rich_x, rich_y, 60.0, traits=group_a),
            Creature("rich_a2", rich_x, rich_y, 60.0, traits=group_a),
            Creature("rich_b1", rich_x, rich_y, 60.0, traits=group_b),
            Creature("poor_b1", poor_x, poor_y, 60.0, traits=group_b),
            Creature("poor_b2", poor_x, poor_y, 60.0, traits=group_b),
        ]

        simulation = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(simulation, world=world)

        zone_counts = stats["creatures_by_fertility_zone"]
        self.assertEqual(zone_counts, {"rich": 3, "neutral": 0, "poor": 2})
        self.assertEqual(sum(zone_counts.values()), simulation.get_alive_count())

        dominants = stats["dominant_proto_group_by_fertility_zone"]
        self.assertIsNotNone(dominants["rich"])
        self.assertIsNone(dominants["neutral"])
        self.assertIsNotNone(dominants["poor"])
        self.assertEqual(int(dominants["rich"]["count"]), 2)
        self.assertEqual(int(dominants["poor"]["count"]), 2)
        self.assertNotEqual(dominants["rich"]["signature"], dominants["poor"]["signature"])

    def test_zone_observation_stats_are_stable(self) -> None:
        world = SimpleWorld(
            world_map=SimpleMap(60.0, 40.0),
            spawn_config=FoodSpawnConfig(initial_food_count=0, min_food_count=0),
            random_source=random.Random(22),
        )
        rich_x, rich_y = self._find_zone_point(world, "rich")

        creatures = [
            Creature("a", rich_x, rich_y, 50.0),
            Creature("b", rich_x, rich_y, 50.0),
        ]
        simulation = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats_a = build_population_stats(simulation, world=world)
        stats_b = build_population_stats(simulation, world=world)

        self.assertEqual(
            stats_a["creatures_by_fertility_zone"],
            stats_b["creatures_by_fertility_zone"],
        )
        self.assertEqual(
            stats_a["dominant_proto_group_by_fertility_zone"],
            stats_b["dominant_proto_group_by_fertility_zone"],
        )

    def test_zone_observation_is_visible_in_debug_text(self) -> None:
        stats = {
            "creatures_by_fertility_zone": {"rich": 4, "neutral": 3, "poor": 1},
            "dominant_proto_group_by_fertility_zone": {
                "rich": {"signature": "s5m7p4d4r4", "count": 3, "share": 0.75},
                "neutral": {"signature": "s6m8p5d3r5", "count": 2, "share": 0.67},
                "poor": None,
            },
        }

        text = format_proto_groups_by_fertility_zone(stats)

        self.assertIn("proto_zones_creatures:", text)
        self.assertIn("riches=4", text)
        self.assertIn("neutres=3", text)
        self.assertIn("pauvres=1", text)
        self.assertIn("dominants:", text)

    def test_short_run_remains_stable_with_zone_observation(self) -> None:
        rng = random.Random(33)
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

        for _ in range(60):
            world.tick()
            simulation.tick(1.0)
            stats = build_population_stats(simulation, world=world)

            zone_counts = stats["creatures_by_fertility_zone"]
            self.assertEqual(
                int(zone_counts["rich"]) + int(zone_counts["neutral"]) + int(zone_counts["poor"]),
                simulation.get_alive_count(),
            )

            if simulation.get_alive_count() == 0:
                break


if __name__ == "__main__":
    unittest.main()



