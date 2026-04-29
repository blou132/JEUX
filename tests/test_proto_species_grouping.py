import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature, create_initial_population
from legacy_python.debug_tools import build_population_stats
from legacy_python.genetics import GeneticTraits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_proto_groups
from legacy_python.world import FoodField, FoodSpawnConfig, SimpleMap, SimpleWorld


class ProtoSpeciesGroupingTests(unittest.TestCase):
    def test_grouping_is_stable_and_size_ordered(self) -> None:
        creatures = [
            Creature(
                creature_id="a1",
                x=0.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(
                    speed=1.00,
                    metabolism=1.00,
                    max_energy=100.0,
                    prudence=1.00,
                    dominance=1.00,
                    repro_drive=1.00,
                ),
            ),
            Creature(
                creature_id="a2",
                x=1.0,
                y=0.0,
                energy=78.0,
                traits=GeneticTraits(
                    speed=1.02,
                    metabolism=1.00,
                    max_energy=100.0,
                    prudence=1.00,
                    dominance=1.00,
                    repro_drive=1.00,
                ),
            ),
            Creature(
                creature_id="a3",
                x=2.0,
                y=0.0,
                energy=76.0,
                traits=GeneticTraits(
                    speed=0.98,
                    metabolism=1.00,
                    max_energy=100.0,
                    prudence=1.00,
                    dominance=1.00,
                    repro_drive=1.00,
                ),
            ),
            Creature(
                creature_id="b1",
                x=3.0,
                y=0.0,
                energy=75.0,
                traits=GeneticTraits(
                    speed=1.42,
                    metabolism=1.18,
                    max_energy=120.0,
                    prudence=1.45,
                    dominance=0.60,
                    repro_drive=1.35,
                ),
            ),
            Creature(
                creature_id="b2",
                x=4.0,
                y=0.0,
                energy=74.0,
                traits=GeneticTraits(
                    speed=1.39,
                    metabolism=1.19,
                    max_energy=120.0,
                    prudence=1.41,
                    dominance=0.62,
                    repro_drive=1.31,
                ),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats_a = build_population_stats(sim)
        stats_b = build_population_stats(sim)

        self.assertEqual(stats_a["proto_group_count"], 2)
        self.assertEqual(stats_a["proto_groups_top"][0]["size"], 3)
        self.assertEqual(stats_a["proto_groups_top"][1]["size"], 2)
        self.assertEqual(stats_a["proto_groups_top"], stats_b["proto_groups_top"])

    def test_groups_are_visible_in_debug_format(self) -> None:
        creatures = [
            Creature(creature_id="c1", x=0.0, y=0.0, energy=80.0),
            Creature(creature_id="c2", x=1.0, y=0.0, energy=78.0),
            Creature(
                creature_id="c3",
                x=2.0,
                y=0.0,
                energy=76.0,
                traits=GeneticTraits(speed=1.4, metabolism=1.2, max_energy=110.0),
            ),
        ]
        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        text = format_proto_groups(stats, max_groups=3)

        self.assertIn("proto_groupes:", text)
        self.assertIn("dominant_part:", text)
        self.assertIn("(n=", text)

    def test_simulation_remains_stable_with_grouping_stats(self) -> None:
        rng = random.Random(77)
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

        for _ in range(80):
            world.tick()
            sim.tick(1.0)
            if sim.get_alive_count() == 0:
                break

        stats = build_population_stats(sim)
        self.assertGreaterEqual(stats["proto_group_count"], 0)
        self.assertIn("proto_groups_top", stats)


if __name__ == "__main__":
    unittest.main()


