import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import (
    build_final_run_summary,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodField


class MemoryImpactMetricsTests(unittest.TestCase):
    def test_population_stats_include_memory_impact_metrics(self) -> None:
        c_food = Creature(creature_id="food", x=0.0, y=0.0, energy=10.0, max_energy=100.0)
        c_food.remember_food_zone(6.0, 0.0, ttl=8.0)

        c_danger = Creature(creature_id="danger", x=0.0, y=2.0, energy=80.0, max_energy=100.0)
        c_danger.remember_danger_zone(1.0, 2.0, ttl=8.0)

        simulation = HungerSimulation(
            creatures=[c_food, c_danger],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
        )

        simulation.tick(dt=1.0)
        stats = build_population_stats(simulation)

        self.assertEqual(int(stats["food_memory_guided_moves_last_tick"]), 1)
        self.assertEqual(int(stats["danger_memory_avoid_moves_last_tick"]), 1)
        self.assertAlmostEqual(float(stats["food_memory_usage_per_alive_tick"]), 0.5)
        self.assertAlmostEqual(float(stats["danger_memory_usage_per_alive_tick"]), 0.5)
        self.assertAlmostEqual(float(stats["food_memory_usage_per_tick_total"]), 1.0)
        self.assertAlmostEqual(float(stats["danger_memory_usage_per_tick_total"]), 1.0)
        self.assertGreater(float(stats["food_memory_effect_avg_distance_tick"]), 0.0)
        self.assertGreater(float(stats["danger_memory_effect_avg_distance_tick"]), 0.0)
        self.assertGreater(float(stats["food_memory_effect_avg_distance_total"]), 0.0)
        self.assertGreater(float(stats["danger_memory_effect_avg_distance_total"]), 0.0)

    def test_run_summaries_include_memory_impact(self) -> None:
        final_stats = {
            "total_food_memory_guided_moves": 9,
            "total_danger_memory_avoid_moves": 4,
            "food_memory_active_share": 0.35,
            "danger_memory_active_share": 0.20,
            "food_memory_effect_avg_distance_total": 1.25,
            "danger_memory_effect_avg_distance_total": 0.75,
            "food_memory_usage_per_tick_total": 0.45,
            "danger_memory_usage_per_tick_total": 0.15,
            "proto_groups_top": [{"signature": "gA", "share": 0.5}],
            "creatures_by_fertility_zone": {"rich": 4, "neutral": 3, "poor": 1},
            "avg_speed": 1.0,
            "avg_metabolism": 1.0,
            "avg_prudence": 1.0,
            "avg_dominance": 1.0,
            "avg_repro_drive": 1.0,
        }

        run_summary = build_final_run_summary(final_stats, create_proto_temporal_tracker())
        memory = run_summary.get("memory_impact")

        self.assertIsInstance(memory, dict)
        assert isinstance(memory, dict)
        self.assertEqual(int(memory["food_usage_total"]), 9)
        self.assertEqual(int(memory["danger_usage_total"]), 4)
        self.assertAlmostEqual(float(memory["food_active_share"]), 0.35)
        self.assertAlmostEqual(float(memory["danger_active_share"]), 0.20)
        self.assertAlmostEqual(float(memory["food_effect_avg_distance"]), 1.25)
        self.assertAlmostEqual(float(memory["danger_effect_avg_distance"]), 0.75)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 4,
                    "final_alive": 10,
                    "run_summary": run_summary,
                },
                {
                    "seed": 2,
                    "extinct": True,
                    "max_generation": 2,
                    "final_alive": 0,
                    "run_summary": {
                        "final_dominant_group_signature": "gB",
                        "avg_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "memory_impact": {
                            "food_usage_total": 3,
                            "danger_usage_total": 1,
                            "food_active_share": 0.10,
                            "danger_active_share": 0.05,
                            "food_effect_avg_distance": 0.5,
                            "danger_effect_avg_distance": 0.2,
                            "food_usage_per_tick": 0.2,
                            "danger_usage_per_tick": 0.1,
                        },
                    },
                },
            ]
        )

        avg_memory = multi_summary.get("avg_memory_impact")
        self.assertIsInstance(avg_memory, dict)
        assert isinstance(avg_memory, dict)
        self.assertAlmostEqual(float(avg_memory["food_usage_total"]), 6.0)
        self.assertAlmostEqual(float(avg_memory["danger_usage_total"]), 2.5)
        self.assertAlmostEqual(float(avg_memory["food_active_share"]), 0.225)
        self.assertAlmostEqual(float(avg_memory["danger_active_share"]), 0.125)


if __name__ == "__main__":
    unittest.main()

