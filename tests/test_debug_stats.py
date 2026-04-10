import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_population_stats
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
                traits=GeneticTraits(speed=1.2, metabolism=0.9, max_energy=100.0),
                age=5.0,
            ),
            Creature(
                creature_id="c2",
                x=1.0,
                y=0.0,
                energy=20.0,
                traits=GeneticTraits(speed=0.8, metabolism=1.1, max_energy=100.0),
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
        self.assertIn("total_deaths", stats)
        self.assertIn("total_births", stats)
        self.assertIn("avg_speed", stats)
        self.assertIn("avg_metabolism", stats)


if __name__ == "__main__":
    unittest.main()
