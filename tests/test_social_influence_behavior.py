import random
import unittest

from ai import HungerAI
from creatures import Creature
from debug_tools import build_population_stats
from genetics import GeneticTraits
from simulation import HungerSimulation
from ui import format_population_dynamics
from world import FoodField, FoodSource


class SocialInfluenceBehaviorTests(unittest.TestCase):
    def test_social_follow_guides_nearby_wanderer_towards_food(self) -> None:
        leader = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        follower = Creature(
            creature_id="follower",
            x=0.0,
            y=1.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))

        sim = HungerSimulation(
            creatures=[leader, follower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=4.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(11),
        )

        before_distance = follower.distance_to(12.0, 0.0)
        sim.tick(dt=1.0)
        after_distance = follower.distance_to(12.0, 0.0)

        self.assertEqual(sim.last_intents["leader"].action, HungerAI.ACTION_MOVE_TO_FOOD)
        self.assertEqual(sim.last_intents["follower"].action, HungerAI.ACTION_WANDER)
        self.assertEqual(sim.social_follow_moves_last_tick, 1)
        self.assertGreater(sim.total_social_follow_moves, 0)
        self.assertLess(after_distance, before_distance)

    def test_social_flee_boost_increases_escape_distance(self) -> None:
        predator = Creature(
            creature_id="predator",
            x=24.0,
            y=20.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.4, metabolism=1.0, max_energy=200.0),
        )

        prey_a_with_boost = Creature(
            creature_id="prey_a",
            x=20.0,
            y=20.0,
            energy=80.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        prey_b_with_boost = Creature(
            creature_id="prey_b",
            x=20.0,
            y=21.0,
            energy=80.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )

        sim_with_boost = HungerSimulation(
            creatures=[prey_a_with_boost, prey_b_with_boost, predator],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=3.0,
            social_flee_boost_per_neighbor=0.25,
            social_flee_boost_max=0.5,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(21),
        )

        boost_start = (prey_a_with_boost.x, prey_a_with_boost.y)
        sim_with_boost.tick(dt=1.0)
        boosted_distance = prey_a_with_boost.distance_to(boost_start[0], boost_start[1])

        prey_a_without_boost = Creature(
            creature_id="prey_a",
            x=20.0,
            y=20.0,
            energy=80.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        predator_without_boost = Creature(
            creature_id="predator",
            x=24.0,
            y=20.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.4, metabolism=1.0, max_energy=200.0),
        )

        sim_without_boost = HungerSimulation(
            creatures=[prey_a_without_boost, predator_without_boost],
            food_field=FoodField(),
            ai_system=HungerAI(threat_detection_range=10.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=3.0,
            social_flee_boost_per_neighbor=0.25,
            social_flee_boost_max=0.5,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(22),
        )

        base_start = (prey_a_without_boost.x, prey_a_without_boost.y)
        sim_without_boost.tick(dt=1.0)
        base_distance = prey_a_without_boost.distance_to(base_start[0], base_start[1])

        self.assertEqual(sim_with_boost.last_intents["prey_a"].action, HungerAI.ACTION_FLEE)
        self.assertEqual(sim_without_boost.last_intents["prey_a"].action, HungerAI.ACTION_FLEE)
        self.assertGreater(boosted_distance, base_distance)
        self.assertGreater(sim_with_boost.social_flee_boosted_last_tick, 0)
        self.assertEqual(sim_without_boost.social_flee_boosted_last_tick, 0)

    def test_social_influence_metrics_are_visible_in_stats_and_debug_text(self) -> None:
        leader = Creature(
            creature_id="leader",
            x=0.0,
            y=0.0,
            energy=20.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )
        follower = Creature(
            creature_id="follower",
            x=0.0,
            y=1.0,
            energy=90.0,
            traits=GeneticTraits(speed=1.0, metabolism=1.0, max_energy=100.0),
        )

        field = FoodField()
        field.add_food(FoodSource(food_id="food", x=12.0, y=0.0, energy_value=40.0))

        sim = HungerSimulation(
            creatures=[leader, follower],
            food_field=field,
            ai_system=HungerAI(hunger_seek_threshold=0.6, food_detection_range=20.0, threat_detection_range=0.0),
            energy_drain_rate=0.0,
            movement_speed=1.0,
            social_influence_distance=4.0,
            social_follow_strength=0.8,
            reproduction_energy_threshold=200.0,
            random_source=random.Random(31),
        )

        previous_stats = build_population_stats(sim)
        sim.tick(dt=1.0)
        current_stats = build_population_stats(sim, previous_stats=previous_stats)
        debug_line = format_population_dynamics(current_stats, previous_stats=previous_stats)

        self.assertGreaterEqual(int(current_stats["social_follow_moves_last_tick"]), 1)
        self.assertIn("social_follow_usage_per_alive_tick", current_stats)
        self.assertIn("social_flee_boost_usage_per_alive_tick", current_stats)
        self.assertIn("social_log:suivi=", debug_line)
        self.assertIn("social_tick:suivi=", debug_line)
        self.assertIn("mult_fuite=", debug_line)


if __name__ == "__main__":
    unittest.main()

