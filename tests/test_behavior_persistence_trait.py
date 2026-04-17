import random
import unittest

from ai import CreatureIntent, HungerAI
from creatures import Creature
from debug_tools import build_hunger_snapshot, build_population_stats
from genetics import GeneticTraits, inherit_traits
from simulation import HungerSimulation
from world import FoodField


class FixedRandom:
    def uniform(self, a: float, b: float) -> float:
        return b


class BehaviorPersistenceTraitTests(unittest.TestCase):
    def test_behavior_persistence_lightly_modulates_intent_switch_near_threshold(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0)

        high_persistence = Creature(
            creature_id="high_persistence",
            x=0.0,
            y=0.0,
            energy=42.0,  # hunger=0.58
            traits=GeneticTraits(max_energy=100.0, behavior_persistence=1.3),
        )
        low_persistence = Creature(
            creature_id="low_persistence",
            x=1.0,
            y=0.0,
            energy=42.0,  # hunger=0.58
            traits=GeneticTraits(max_energy=100.0, behavior_persistence=0.8),
        )
        previous = CreatureIntent(action=HungerAI.ACTION_SEARCH_FOOD)

        high_intent = ai.decide(
            high_persistence,
            FoodField(),
            can_reproduce=False,
            nearby_creatures=[high_persistence],
            previous_intent=previous,
        )
        low_intent = ai.decide(
            low_persistence,
            FoodField(),
            can_reproduce=False,
            nearby_creatures=[low_persistence],
            previous_intent=previous,
        )

        self.assertEqual(high_intent.action, HungerAI.ACTION_SEARCH_FOOD)
        self.assertTrue(high_intent.persisted_from_previous)
        self.assertEqual(low_intent.action, HungerAI.ACTION_WANDER)
        self.assertFalse(low_intent.persisted_from_previous)

    def test_behavior_persistence_does_not_override_threat_flee_priority(self) -> None:
        ai = HungerAI(hunger_seek_threshold=0.6, threat_detection_range=10.0, threat_strength_ratio=1.15)

        creature = Creature(
            creature_id="runner",
            x=0.0,
            y=0.0,
            energy=42.0,
            traits=GeneticTraits(max_energy=100.0, behavior_persistence=1.3),
        )
        predator = Creature(
            creature_id="predator",
            x=3.0,
            y=0.0,
            energy=20.0,  # hungry enough to be threatening
            traits=GeneticTraits(speed=1.2, max_energy=120.0),
        )
        previous = CreatureIntent(action=HungerAI.ACTION_WANDER)

        intent = ai.decide(
            creature,
            FoodField(),
            can_reproduce=False,
            nearby_creatures=[creature, predator],
            previous_intent=previous,
        )

        self.assertEqual(intent.action, HungerAI.ACTION_FLEE)
        self.assertFalse(intent.persisted_from_previous)

    def test_behavior_persistence_is_inherited_with_light_mutation(self) -> None:
        parent_a = GeneticTraits(behavior_persistence=0.9)
        parent_b = GeneticTraits(behavior_persistence=1.1)

        child = inherit_traits(parent_a, parent_b, mutation_variation=0.1, rng=FixedRandom())

        self.assertAlmostEqual(child.behavior_persistence, 1.1)

    def test_behavior_persistence_is_visible_in_stats_and_snapshot(self) -> None:
        high_persistence = Creature(
            creature_id="high_persistence",
            x=0.0,
            y=0.0,
            energy=42.0,  # hunger=0.58
            traits=GeneticTraits(max_energy=100.0, behavior_persistence=1.3),
        )
        low_persistence = Creature(
            creature_id="low_persistence",
            x=1.0,
            y=0.0,
            energy=42.0,  # hunger=0.58
            traits=GeneticTraits(max_energy=100.0, behavior_persistence=0.8),
        )

        sim = HungerSimulation(
            creatures=[high_persistence, low_persistence],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=0.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(321),
        )
        sim.last_intents = {
            "high_persistence": CreatureIntent(action=HungerAI.ACTION_SEARCH_FOOD),
            "low_persistence": CreatureIntent(action=HungerAI.ACTION_SEARCH_FOOD),
        }

        sim.tick(1.0)

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_behavior_persistence", stats)
        self.assertIn("std_behavior_persistence", stats)
        self.assertIn("persistence_holds_last_tick", stats)
        self.assertIn("behavior_persistence_hold_users_avg_tick", stats)
        self.assertIn("behavior_persistence_hold_usage_bias_tick", stats)

        self.assertGreater(float(stats["std_behavior_persistence"]), 0.0)
        self.assertGreaterEqual(int(stats["persistence_holds_last_tick"]), 1)
        self.assertGreater(
            float(stats["behavior_persistence_hold_users_avg_tick"]),
            float(stats["avg_behavior_persistence"]),
        )
        self.assertGreater(float(stats["behavior_persistence_hold_usage_bias_tick"]), 0.0)

        by_id = {str(row["id"]): row for row in snapshot["creatures"]}
        high_row = by_id["high_persistence"]
        self.assertIn("behavior_persistence", high_row["traits"])
        self.assertTrue(bool(high_row["persisted_from_previous"]))
        self.assertEqual(str(high_row["action_reason"]), "intent_inertia")


if __name__ == "__main__":
    unittest.main()
