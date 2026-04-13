import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_hunger_snapshot, build_population_stats
from genetics import GeneticTraits, inherit_traits
from simulation import HungerSimulation
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class RiskTakingTraitTests(unittest.TestCase):
    def test_risk_taking_lightly_modulates_borderline_threat_sensitivity(self) -> None:
        ai = HungerAI(threat_detection_range=10.0, threat_strength_ratio=1.15)

        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.15, max_energy=100.0),
        )
        cautious = Creature(
            creature_id="cautious",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=0.7),
        )
        bold = Creature(
            creature_id="bold",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=1.3),
        )

        cautious_intent = ai.decide(
            cautious,
            FoodField(),
            can_reproduce=False,
            nearby_creatures=[cautious, predator],
        )
        bold_intent = ai.decide(
            bold,
            FoodField(),
            can_reproduce=False,
            nearby_creatures=[bold, predator],
        )

        self.assertEqual(cautious_intent.action, HungerAI.ACTION_FLEE)
        self.assertNotEqual(bold_intent.action, HungerAI.ACTION_FLEE)

    def test_risk_taking_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(risk_taking=0.9)
        parent_b = GeneticTraits(risk_taking=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.risk_taking, 1.1)

    def test_risk_taking_is_visible_in_stats_and_snapshot(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.15, max_energy=100.0, risk_taking=1.0),
        )
        cautious = Creature(
            creature_id="cautious",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=0.7),
        )
        bold = Creature(
            creature_id="bold",
            x=0.0,
            y=0.0,
            energy=90.0,
            traits=GeneticTraits(risk_taking=1.3),
        )

        sim = HungerSimulation(
            creatures=[cautious, bold, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0, threat_strength_ratio=1.15),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(900),
        )

        sim.tick(1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_risk_taking", stats)
        self.assertIn("std_risk_taking", stats)
        self.assertIn("risk_taking_flee_users_avg_tick", stats)
        self.assertIn("risk_taking_flee_usage_bias_tick", stats)

        self.assertGreater(float(stats["std_risk_taking"]), 0.0)
        self.assertLess(
            float(stats["risk_taking_flee_users_avg_tick"]),
            float(stats["avg_risk_taking"]),
        )
        self.assertLess(float(stats["risk_taking_flee_usage_bias_tick"]), 0.0)

        first_creature_traits = snapshot["creatures"][0]["traits"]
        self.assertIn("risk_taking", first_creature_traits)


if __name__ == "__main__":
    unittest.main()
