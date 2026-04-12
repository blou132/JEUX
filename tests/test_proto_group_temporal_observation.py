import random
import unittest

from ai import HungerAI
from creatures import Creature, create_initial_population
from debug_tools import build_population_stats
from genetics import GeneticTraits
from simulation import HungerSimulation
from ui import format_proto_group_temporal
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


class ProtoGroupTemporalObservationTests(unittest.TestCase):
    def _create_group_creatures(
        self,
        count: int,
        traits: GeneticTraits,
        x: float,
        y: float,
        prefix: str,
    ) -> list[Creature]:
        creatures: list[Creature] = []
        for idx in range(count):
            creatures.append(
                Creature(
                    creature_id=f"{prefix}_{idx}",
                    x=x,
                    y=y,
                    energy=70.0,
                    traits=traits,
                )
            )
        return creatures

    def test_temporal_trends_detect_new_up_down_and_stable(self) -> None:
        traits_a = GeneticTraits(
            speed=1.0,
            metabolism=1.0,
            max_energy=100.0,
            prudence=1.0,
            dominance=1.0,
            repro_drive=1.0,
        )
        traits_b = GeneticTraits(
            speed=1.4,
            metabolism=1.1,
            max_energy=105.0,
            prudence=1.1,
            dominance=0.9,
            repro_drive=1.1,
        )
        traits_c = GeneticTraits(
            speed=0.6,
            metabolism=0.9,
            max_energy=95.0,
            prudence=0.8,
            dominance=1.2,
            repro_drive=0.9,
        )
        traits_d = GeneticTraits(
            speed=1.8,
            metabolism=1.3,
            max_energy=110.0,
            prudence=1.2,
            dominance=0.7,
            repro_drive=1.2,
        )

        snapshot_1_creatures = []
        snapshot_1_creatures.extend(self._create_group_creatures(5, traits_a, 1.0, 1.0, "a"))
        snapshot_1_creatures.extend(self._create_group_creatures(3, traits_b, 2.0, 2.0, "b"))
        snapshot_1_creatures.extend(self._create_group_creatures(2, traits_c, 3.0, 3.0, "c"))

        simulation_1 = HungerSimulation(
            creatures=snapshot_1_creatures,
            food_field=SimpleWorld(SimpleMap(10.0, 10.0), FoodSpawnConfig(0, 0)).food_field,
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )
        stats_1 = build_population_stats(simulation_1)

        snapshot_2_creatures = []
        snapshot_2_creatures.extend(self._create_group_creatures(6, traits_a, 1.0, 1.0, "a2"))
        snapshot_2_creatures.extend(self._create_group_creatures(3, traits_b, 2.0, 2.0, "b2"))
        snapshot_2_creatures.extend(self._create_group_creatures(1, traits_d, 4.0, 4.0, "d2"))

        simulation_2 = HungerSimulation(
            creatures=snapshot_2_creatures,
            food_field=SimpleWorld(SimpleMap(10.0, 10.0), FoodSpawnConfig(0, 0)).food_field,
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )
        stats_2 = build_population_stats(simulation_2, previous_stats=stats_1)

        trends = stats_2["proto_group_temporal_trends"]
        self.assertIsInstance(trends, list)
        self.assertGreaterEqual(len(trends), 4)

        def find_status(current_share: float, previous_share: float) -> str:
            for trend in trends:
                if not isinstance(trend, dict):
                    continue
                if (
                    abs(float(trend.get("current_share", 0.0)) - current_share) < 1e-9
                    and abs(float(trend.get("previous_share", 0.0)) - previous_share) < 1e-9
                ):
                    return str(trend.get("status", ""))
            return ""

        self.assertEqual(find_status(0.6, 0.5), "en_hausse")
        self.assertEqual(find_status(0.3, 0.3), "stable")
        self.assertEqual(find_status(0.1, 0.0), "nouveau")
        self.assertEqual(find_status(0.0, 0.2), "en_baisse")

        summary = stats_2["proto_group_temporal_summary"]
        self.assertEqual(int(summary["en_hausse"]), 1)
        self.assertEqual(int(summary["stable"]), 1)
        self.assertEqual(int(summary["nouveau"]), 1)
        self.assertEqual(int(summary["en_baisse"]), 1)

    def test_temporal_trends_are_stable_for_same_inputs(self) -> None:
        creatures = [
            Creature(creature_id="c1", x=0.0, y=0.0, energy=70.0),
            Creature(creature_id="c2", x=0.0, y=0.0, energy=70.0),
            Creature(
                creature_id="c3",
                x=0.0,
                y=0.0,
                energy=70.0,
                traits=GeneticTraits(speed=1.4, metabolism=1.1, max_energy=100.0),
            ),
        ]
        simulation = HungerSimulation(
            creatures=creatures,
            food_field=SimpleWorld(SimpleMap(10.0, 10.0), FoodSpawnConfig(0, 0)).food_field,
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        first = build_population_stats(simulation)
        second_a = build_population_stats(simulation, previous_stats=first)
        second_b = build_population_stats(simulation, previous_stats=first)

        self.assertEqual(second_a["proto_group_temporal_trends"], second_b["proto_group_temporal_trends"])
        self.assertEqual(second_a["proto_group_temporal_summary"], second_b["proto_group_temporal_summary"])

    def test_temporal_trends_are_visible_in_debug_text(self) -> None:
        stats = {
            "proto_group_temporal_trends": [
                {
                    "signature": "s5m7p4d4r4",
                    "status": "en_hausse",
                    "current_share": 0.32,
                    "previous_share": 0.25,
                    "delta_share": 0.07,
                },
                {
                    "signature": "s5m6p4d4r4",
                    "status": "stable",
                    "current_share": 0.30,
                    "previous_share": 0.31,
                    "delta_share": -0.01,
                },
            ],
            "proto_group_temporal_summary": {
                "stable": 1,
                "en_hausse": 1,
                "en_baisse": 0,
                "nouveau": 0,
            },
        }

        text = format_proto_group_temporal(stats)
        self.assertIn("proto_tendance:", text)
        self.assertIn("hausse", text)
        self.assertIn("stable", text)

    def test_short_run_stable_with_temporal_observation(self) -> None:
        rng = random.Random(89)
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

        previous_stats = None
        for _ in range(60):
            world.tick()
            simulation.tick(1.0)
            stats = build_population_stats(simulation, world=world, previous_stats=previous_stats)

            self.assertIn("proto_group_temporal_trends", stats)
            self.assertIn("proto_group_temporal_summary", stats)

            previous_stats = stats
            if simulation.get_alive_count() == 0:
                break


if __name__ == "__main__":
    unittest.main()
