import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_generation_distribution, build_population_stats
from genetics import GeneticTraits
from simulation import HungerSimulation
from world import FoodField


class DebugStatsTests(unittest.TestCase):
    def test_population_stats_include_required_fields(self) -> None:
        creatures = [
            Creature(
                creature_id="c1",
                x=0.0,
                y=0.0,
                energy=50.0,
                traits=GeneticTraits(
                    speed=1.2,
                    metabolism=0.9,
                    max_energy=100.0,
                    prudence=1.1,
                    dominance=0.9,
                    repro_drive=1.2,
                ),
                age=5.0,
            ),
            Creature(
                creature_id="c2",
                x=1.0,
                y=0.0,
                energy=20.0,
                traits=GeneticTraits(
                    speed=0.8,
                    metabolism=1.1,
                    max_energy=100.0,
                    prudence=0.9,
                    dominance=1.1,
                    repro_drive=0.8,
                ),
                age=3.0,
            ),
        ]
        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)

        self.assertEqual(stats["population"], 2)
        self.assertIn("food_remaining", stats)
        self.assertIn("avg_energy", stats)
        self.assertIn("avg_age", stats)
        self.assertIn("avg_generation", stats)
        self.assertIn("total_deaths", stats)
        self.assertIn("total_births", stats)
        self.assertIn("avg_speed", stats)
        self.assertIn("avg_metabolism", stats)
        self.assertIn("avg_prudence", stats)
        self.assertIn("avg_dominance", stats)
        self.assertIn("avg_repro_drive", stats)
        self.assertIn("death_causes_last_tick", stats)
        self.assertIn("death_causes_total", stats)
        self.assertIn("flees_last_tick", stats)
        self.assertIn("total_flees", stats)
        self.assertIn("fleeing_creatures_last_tick", stats)
        self.assertIn("avg_flee_threat_distance_last_tick", stats)
        self.assertIn("creatures_with_food_memory", stats)
        self.assertIn("creatures_with_danger_memory", stats)
        self.assertIn("food_memory_guided_moves_last_tick", stats)
        self.assertIn("total_food_memory_guided_moves", stats)
        self.assertIn("danger_memory_avoid_moves_last_tick", stats)
        self.assertIn("total_danger_memory_avoid_moves", stats)
        self.assertIn("creatures_by_fertility_zone", stats)
        self.assertIn("dominant_proto_group_by_fertility_zone", stats)
        self.assertIn("proto_group_temporal_trends", stats)
        self.assertIn("proto_group_temporal_summary", stats)

    def test_generation_distribution_matches_population_counts(self) -> None:
        creatures = [
            Creature(creature_id="g0_a", x=0.0, y=0.0, energy=80.0, generation=0),
            Creature(creature_id="g0_b", x=1.0, y=0.0, energy=70.0, generation=0),
            Creature(creature_id="g1", x=2.0, y=0.0, energy=60.0, generation=1),
            Creature(creature_id="g2", x=3.0, y=0.0, energy=50.0, generation=2),
        ]
        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        distribution = build_generation_distribution(sim)

        self.assertEqual(sum(distribution.values()), stats["population"])
        self.assertEqual(distribution, {0: 2, 1: 1, 2: 1})
        self.assertAlmostEqual(float(stats["avg_generation"]), 0.75)


if __name__ == "__main__":
    unittest.main()

