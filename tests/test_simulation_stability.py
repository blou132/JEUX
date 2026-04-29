import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import create_initial_population
from legacy_python.debug_tools import build_population_stats
from legacy_python.simulation import HungerSimulation
from legacy_python.world import FoodSpawnConfig, SimpleMap, SimpleWorld


class SimulationStabilityTests(unittest.TestCase):
    def _build_default_simulation(self, seed: int) -> tuple[SimpleWorld, HungerSimulation]:
        rng = random.Random(seed)
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
        return world, simulation

    def test_short_run_keeps_core_invariants(self) -> None:
        world, simulation = self._build_default_simulation(seed=42)

        for _ in range(200):
            world.tick()
            simulation.tick(1.0)
            stats = build_population_stats(simulation)

            # Core loop should keep coherent counts and non-negative resources.
            self.assertEqual(stats["population"], stats["alive"] + stats["dead"])
            self.assertGreaterEqual(stats["food_remaining"], 0.0)
            self.assertGreaterEqual(stats["avg_energy"], 0.0)

            if simulation.get_alive_count() == 0:
                break

    def test_multiple_seeds_do_not_show_systematic_early_extinction(self) -> None:
        survived_runs = 0
        reached_generation_3 = 0

        for seed in range(5):
            world, simulation = self._build_default_simulation(seed=seed)

            for _ in range(120):
                world.tick()
                simulation.tick(1.0)
                if simulation.get_alive_count() == 0:
                    break

            if simulation.get_alive_count() > 0:
                survived_runs += 1

            max_generation = max((c.generation for c in simulation.creatures), default=0)
            if max_generation >= 3:
                reached_generation_3 += 1

        # MVP should not collapse immediately for most deterministic seeds.
        self.assertGreaterEqual(survived_runs, 4)
        self.assertGreaterEqual(reached_generation_3, 3)


if __name__ == "__main__":
    unittest.main()

