import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_hunger_snapshot, build_population_stats
from genetics import GeneticTraits
from simulation import HungerSimulation
from world import FoodField, FoodSource


class IndividualBehaviorBiasTests(unittest.TestCase):
    def test_memory_focus_lightly_modulates_food_memory_usage(self) -> None:
        high_focus = Creature(
            creature_id="high_focus",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(memory_focus=1.3, social_sensitivity=1.0),
        )
        high_focus.remember_food_zone(6.0, 0.0, ttl=8.0)

        low_focus = Creature(
            creature_id="low_focus",
            x=0.0,
            y=0.0,
            energy=10.0,
            traits=GeneticTraits(memory_focus=0.7, social_sensitivity=1.0),
        )
        low_focus.remember_food_zone(6.0, 0.0, ttl=8.0)

        sim_high = HungerSimulation(
            creatures=[high_focus],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            food_memory_recall_distance=5.0,
            random_source=random.Random(101),
        )
        sim_low = HungerSimulation(
            creatures=[low_focus],
            food_field=FoodField(),
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=2.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            food_memory_recall_distance=5.0,
            random_source=random.Random(102),
        )

        sim_high.tick(dt=1.0)
        sim_low.tick(dt=1.0)

        self.assertEqual(sim_high.last_intents["high_focus"].action, HungerAI.ACTION_SEARCH_FOOD)
        self.assertEqual(sim_low.last_intents["low_focus"].action, HungerAI.ACTION_SEARCH_FOOD)
        self.assertEqual(sim_high.food_memory_guided_moves_last_tick, 1)
        self.assertEqual(sim_low.food_memory_guided_moves_last_tick, 0)

    def test_social_sensitivity_lightly_modulates_social_follow(self) -> None:
        leader_high = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=1.0),
        )
        follower_high = Creature(
            creature_id="follower",
            x=0.0,
            y=3.3,
            energy=90.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=1.2),
        )

        leader_low = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=1.0),
        )
        follower_low = Creature(
            creature_id="follower",
            x=0.0,
            y=3.3,
            energy=90.0,
            traits=GeneticTraits(memory_focus=1.0, social_sensitivity=0.8),
        )

        field_high = FoodField()
        field_high.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))
        field_low = FoodField()
        field_low.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))

        sim_high = HungerSimulation(
            creatures=[leader_high, follower_high],
            food_field=field_high,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=3.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(201),
        )
        sim_low = HungerSimulation(
            creatures=[leader_low, follower_low],
            food_field=field_low,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=3.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(202),
        )

        sim_high.tick(dt=1.0)
        sim_low.tick(dt=1.0)

        self.assertEqual(sim_high.last_intents["leader"].action, HungerAI.ACTION_MOVE_TO_FOOD)
        self.assertEqual(sim_high.last_intents["follower"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_low.last_intents["leader"].action, HungerAI.ACTION_MOVE_TO_FOOD)
        self.assertEqual(sim_low.last_intents["follower"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim_high.social_follow_moves_last_tick, 1)
        self.assertEqual(sim_low.social_follow_moves_last_tick, 0)

    def test_bias_traits_are_visible_in_stats_and_snapshot(self) -> None:
        c1 = Creature(
            creature_id="c1",
            x=0.0,
            y=0.0,
            energy=80.0,
            traits=GeneticTraits(memory_focus=1.2, social_sensitivity=0.9),
        )
        c2 = Creature(
            creature_id="c2",
            x=1.0,
            y=0.0,
            energy=70.0,
            traits=GeneticTraits(memory_focus=0.8, social_sensitivity=1.1),
        )

        sim = HungerSimulation(
            creatures=[c1, c2],
            food_field=FoodField(),
            ai_system=HungerAI(),
            energy_drain_rate=0.0,
        )

        stats = build_population_stats(sim)
        snapshot = build_hunger_snapshot(sim)

        self.assertIn("avg_memory_focus", stats)
        self.assertIn("avg_social_sensitivity", stats)
        self.assertAlmostEqual(float(stats["avg_memory_focus"]), 1.0)
        self.assertAlmostEqual(float(stats["avg_social_sensitivity"]), 1.0)

        row = snapshot["creatures"][0]
        traits = row["traits"]
        self.assertIn("memory_focus", traits)
        self.assertIn("social_sensitivity", traits)


if __name__ == "__main__":
    unittest.main()
