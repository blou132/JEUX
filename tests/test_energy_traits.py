import random
import unittest

from legacy_python.ai import HungerAI
from legacy_python.creatures import Creature
from legacy_python.debug_tools import (
    build_final_run_summary,
    build_hunger_snapshot,
    build_multi_run_summary,
    build_population_stats,
    create_proto_temporal_tracker,
)
from legacy_python.genetics import GeneticTraits, inherit_traits
from legacy_python.simulation import HungerSimulation
from legacy_python.ui import format_final_run_summary, format_multi_run_summary
from legacy_python.world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class EnergyTraitsTests(unittest.TestCase):
    def test_energy_efficiency_lightly_modulates_passive_drain(self) -> None:
        high_eff = Creature(
            creature_id="high_eff",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(metabolism=1.0, energy_efficiency=1.1, max_energy=100.0),
        )
        low_eff = Creature(
            creature_id="low_eff",
            x=1.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(metabolism=1.0, energy_efficiency=0.9, max_energy=100.0),
        )

        sim = HungerSimulation(
            creatures=[high_eff, low_eff],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(901),
        )

        sim.tick(dt=1.0)

        self.assertAlmostEqual(high_eff.energy, 100.0 - (10.0 * 0.975), places=4)
        self.assertAlmostEqual(low_eff.energy, 100.0 - (10.0 * 1.025), places=4)
        self.assertGreater(high_eff.energy, low_eff.energy)

    def test_exhaustion_resistance_lightly_modulates_reproduction_cost(self) -> None:
        high_a = Creature(
            creature_id="ha",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=1.1),
        )
        high_b = Creature(
            creature_id="hb",
            x=0.5,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=1.1),
        )

        low_a = Creature(
            creature_id="la",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=0.9),
        )
        low_b = Creature(
            creature_id="lb",
            x=0.5,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(max_energy=10.0, exhaustion_resistance=0.9),
        )

        sim_high = HungerSimulation(
            creatures=[high_a, high_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=10.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            random_source=random.Random(902),
        )
        sim_low = HungerSimulation(
            creatures=[low_a, low_b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=10.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            random_source=random.Random(903),
        )

        sim_high.tick(dt=1.0)
        sim_low.tick(dt=1.0)

        self.assertEqual(sim_high.total_births, 1)
        self.assertTrue(high_a.alive)
        self.assertTrue(high_b.alive)

        self.assertEqual(sim_low.total_births, 1)
        self.assertFalse(low_a.alive)
        self.assertFalse(low_b.alive)
        self.assertEqual(int(sim_low.death_causes_last_tick[HungerSimulation.DEATH_CAUSE_EXHAUSTION]), 2)

    def test_energy_traits_are_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(energy_efficiency=1.1, exhaustion_resistance=1.2)
        parent_b = GeneticTraits(energy_efficiency=0.9, exhaustion_resistance=0.8)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.energy_efficiency, 1.1)
        self.assertAlmostEqual(child.exhaustion_resistance, 1.1)

    def test_energy_traits_are_visible_in_stats_and_snapshot(self) -> None:
        creatures = [
            Creature(
                creature_id="c1",
                x=0.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(energy_efficiency=1.1, exhaustion_resistance=1.2),
            ),
            Creature(
                creature_id="c2",
                x=1.0,
                y=0.0,
                energy=80.0,
                traits=GeneticTraits(energy_efficiency=0.9, exhaustion_resistance=0.8),
            ),
        ]

        sim = HungerSimulation(
            creatures=creatures,
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_energy_efficiency", stats)
        self.assertIn("avg_exhaustion_resistance", stats)
        self.assertIn("std_energy_efficiency", stats)
        self.assertIn("std_exhaustion_resistance", stats)
        self.assertIn("avg_effective_energy_drain_multiplier", stats)
        self.assertIn("avg_reproduction_cost_multiplier", stats)
        self.assertAlmostEqual(float(stats["avg_energy_efficiency"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_exhaustion_resistance"]), 1.0)
        self.assertGreater(float(stats["std_energy_efficiency"]), 0.0)
        self.assertGreater(float(stats["std_exhaustion_resistance"]), 0.0)

        row = snapshot["creatures"][0]
        traits = row["traits"]
        self.assertIn("energy_efficiency", traits)
        self.assertIn("exhaustion_resistance", traits)

    def test_energy_impact_metrics_are_observed_in_stats_and_summaries(self) -> None:
        a = Creature(
            creature_id="a",
            x=0.0,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=1.1,
                exhaustion_resistance=1.1,
                max_energy=100.0,
            ),
        )
        b = Creature(
            creature_id="b",
            x=0.5,
            y=0.0,
            energy=100.0,
            traits=GeneticTraits(
                metabolism=1.0,
                energy_efficiency=0.9,
                exhaustion_resistance=0.9,
                max_energy=100.0,
            ),
        )

        sim = HungerSimulation(
            creatures=[a, b],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6),
            energy_drain_rate=10.0,
            reproduction_energy_threshold=80.0,
            reproduction_cost=10.0,
            reproduction_distance=2.0,
            random_source=random.Random(904),
        )
        sim.tick(dt=1.0)

        stats = build_population_stats(sim)
        self.assertEqual(int(stats["energy_drain_events_last_tick"]), 2)
        self.assertEqual(int(stats["total_energy_drain_events"]), 2)
        self.assertEqual(int(stats["reproduction_cost_events_last_tick"]), 2)
        self.assertEqual(int(stats["total_reproduction_cost_events"]), 2)
        self.assertAlmostEqual(float(stats["avg_energy_drain_multiplier_observed_last_tick"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_reproduction_cost_multiplier_observed_last_tick"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_energy_drain_amount_last_tick"]), 10.0)
        self.assertAlmostEqual(float(stats["avg_reproduction_cost_amount_last_tick"]), 10.0)
        self.assertAlmostEqual(
            float(stats["energy_efficiency_drain_usage_bias_tick"]),
            float(stats["energy_efficiency_drain_users_avg_tick"]) - float(stats["avg_energy_efficiency"]),
        )
        self.assertAlmostEqual(
            float(stats["exhaustion_resistance_reproduction_usage_bias_tick"]),
            float(stats["exhaustion_resistance_reproduction_users_avg_tick"])
            - float(stats["avg_exhaustion_resistance"]),
        )

        tracker = create_proto_temporal_tracker()
        run_summary = build_final_run_summary(stats, tracker)
        trait_impact = run_summary.get("trait_impact")
        self.assertIsInstance(trait_impact, dict)
        assert isinstance(trait_impact, dict)
        self.assertIn("energy_efficiency_drain_bias", trait_impact)
        self.assertIn("exhaustion_resistance_reproduction_bias", trait_impact)
        self.assertIn("energy_drain_multiplier_observed", trait_impact)
        self.assertIn("reproduction_cost_multiplier_observed", trait_impact)
        self.assertIn("energy_drain_amount_observed", trait_impact)
        self.assertIn("reproduction_cost_amount_observed", trait_impact)
        run_text = format_final_run_summary(run_summary)
        self.assertIn("energy_obs:", run_text)
        self.assertIn("bias_ee_drain=", run_text)
        self.assertIn("bias_er_repro=", run_text)

        multi_summary = build_multi_run_summary(
            [
                {
                    "seed": 1,
                    "extinct": False,
                    "max_generation": 2,
                    "final_alive": sim.get_alive_count(),
                    "run_summary": run_summary,
                }
            ]
        )
        avg_trait_impact = multi_summary.get("avg_trait_impact")
        self.assertIsInstance(avg_trait_impact, dict)
        assert isinstance(avg_trait_impact, dict)
        self.assertIn("energy_efficiency_drain_bias", avg_trait_impact)
        self.assertIn("exhaustion_resistance_reproduction_bias", avg_trait_impact)
        self.assertIn("energy_drain_multiplier_observed", avg_trait_impact)
        self.assertIn("reproduction_cost_multiplier_observed", avg_trait_impact)
        multi_text = format_multi_run_summary(multi_summary)
        self.assertIn("energy_obs_moy:", multi_text)
        self.assertIn("bias_ee_drain=", multi_text)
        self.assertIn("bias_er_repro=", multi_text)


if __name__ == "__main__":
    unittest.main()


