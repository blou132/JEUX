import random
import unittest

from ai import HungerAI
from creatures import create_initial_population
from debug_tools import (
    build_final_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
    update_proto_temporal_tracker,
)
from simulation import HungerSimulation
from ui import format_final_run_summary
from world import FoodSpawnConfig, SimpleMap, SimpleWorld


class RunFinalSummaryTests(unittest.TestCase):
    def test_summary_fields_are_present_and_coherent(self) -> None:
        tracker = create_proto_temporal_tracker()

        update_proto_temporal_tracker(
            tracker,
            {
                "proto_group_temporal_trends": [
                    {"signature": "gA", "status": "nouveau"},
                    {"signature": "gB", "status": "nouveau"},
                ]
            },
        )
        update_proto_temporal_tracker(
            tracker,
            {
                "proto_group_temporal_trends": [
                    {"signature": "gA", "status": "stable"},
                    {"signature": "gB", "status": "en_baisse"},
                    {"signature": "gC", "status": "en_hausse"},
                ]
            },
        )
        update_proto_temporal_tracker(
            tracker,
            {
                "proto_group_temporal_trends": [
                    {"signature": "gA", "status": "stable"},
                    {"signature": "gC", "status": "en_hausse"},
                ]
            },
        )

        final_stats = {
            "proto_groups_top": [{"signature": "gA", "share": 0.42}],
            "creatures_by_fertility_zone": {"rich": 10, "neutral": 7, "poor": 3},
            "avg_speed": 1.02,
            "avg_metabolism": 0.97,
            "avg_prudence": 1.01,
            "avg_dominance": 1.08,
            "avg_repro_drive": 0.95,
        }

        summary = build_final_run_summary(final_stats, tracker)

        self.assertEqual(summary["final_dominant_group_signature"], "gA")
        self.assertAlmostEqual(float(summary["final_dominant_group_share"]), 0.42)
        self.assertEqual(summary["most_stable_group_signature"], "gA")
        self.assertEqual(int(summary["most_stable_group_count"]), 2)
        self.assertEqual(summary["most_rising_group_signature"], "gC")
        self.assertEqual(int(summary["most_rising_group_count"]), 2)
        self.assertEqual(summary["final_zone_distribution"], {"rich": 10, "neutral": 7, "poor": 3})
        self.assertEqual(int(summary["observed_logs"]), 3)

        avg_traits = summary["avg_traits"]
        self.assertAlmostEqual(float(avg_traits["speed"]), 1.02)
        self.assertAlmostEqual(float(avg_traits["metabolism"]), 0.97)
        self.assertAlmostEqual(float(avg_traits["prudence"]), 1.01)
        self.assertAlmostEqual(float(avg_traits["dominance"]), 1.08)
        self.assertAlmostEqual(float(avg_traits["repro_drive"]), 0.95)

    def test_final_summary_format_is_readable(self) -> None:
        summary = {
            "final_dominant_group_signature": "gA",
            "final_dominant_group_share": 0.42,
            "most_stable_group_signature": "gA",
            "most_stable_group_count": 3,
            "most_rising_group_signature": "gC",
            "most_rising_group_count": 2,
            "final_zone_distribution": {"rich": 11, "neutral": 8, "poor": 1},
            "avg_traits": {
                "speed": 1.01,
                "metabolism": 0.98,
                "prudence": 1.02,
                "dominance": 1.05,
                "repro_drive": 0.96,
            },
            "observed_logs": 5,
        }

        text = format_final_run_summary(summary)

        self.assertIn("synthese_run:", text)
        self.assertIn("dominant_final=gA", text)
        self.assertIn("plus_stable=gA", text)
        self.assertIn("plus_hausse=gC", text)
        self.assertIn("zones_finales:", text)
        self.assertIn("traits_moy:", text)

    def test_short_run_stays_stable_with_final_summary(self) -> None:
        rng = random.Random(123)
        world_map = SimpleMap(width=60.0, height=40.0)
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

        tracker = create_proto_temporal_tracker()
        previous_stats = None

        for tick in range(1, 61):
            world.tick()
            simulation.tick(1.0)
            if tick == 1 or tick % 10 == 0:
                stats = build_population_stats(
                    simulation,
                    world=world,
                    previous_stats=previous_stats,
                )
                update_proto_temporal_tracker(tracker, stats)
                previous_stats = stats
            if simulation.get_alive_count() == 0:
                break

        final_stats = build_population_stats(
            simulation,
            world=world,
            previous_stats=previous_stats,
        )
        summary = build_final_run_summary(final_stats, tracker)

        required_fields = {
            "final_dominant_group_signature",
            "final_dominant_group_share",
            "most_stable_group_signature",
            "most_stable_group_count",
            "most_rising_group_signature",
            "most_rising_group_count",
            "final_zone_distribution",
            "avg_traits",
            "observed_logs",
        }
        self.assertTrue(required_fields.issubset(set(summary.keys())))


if __name__ == "__main__":
    unittest.main()
