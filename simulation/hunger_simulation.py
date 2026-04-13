from __future__ import annotations

import random
from math import cos, pi, sin
from typing import Dict, Iterable, Set

from ai import CreatureIntent, HungerAI
from creatures import Creature
from genetics import inherit_traits
from world import FoodField, SimpleMap


class HungerSimulation:
    DEATH_CAUSE_STARVATION = "starvation"
    DEATH_CAUSE_EXHAUSTION = "exhaustion"
    DEATH_CAUSE_UNKNOWN = "unknown"

    def __init__(
        self,
        creatures: Iterable[Creature],
        food_field: FoodField,
        ai_system: HungerAI,
        energy_drain_rate: float = 1.0,
        movement_speed: float = 1.0,
        eat_rate: float = 20.0,
        reproduction_energy_threshold: float = 70.0,
        reproduction_cost: float = 20.0,
        reproduction_distance: float = 1.5,
        reproduction_min_age: float = 0.0,
        mutation_variation: float = 0.1,
        random_source: random.Random | None = None,
        world_map: SimpleMap | None = None,
        food_memory_duration: float = 8.0,
        danger_memory_duration: float = 6.0,
        food_memory_recall_distance: float = 8.0,
        danger_memory_avoid_distance: float = 5.0,
        social_influence_distance: float = 6.0,
        social_follow_strength: float = 0.35,
        social_flee_boost_per_neighbor: float = 0.15,
        social_flee_boost_max: float = 0.45,
    ) -> None:
        if (
            energy_drain_rate < 0
            or movement_speed < 0
            or eat_rate < 0
            or reproduction_energy_threshold < 0
            or reproduction_cost < 0
            or reproduction_distance < 0
            or reproduction_min_age < 0
            or mutation_variation < 0
            or food_memory_duration < 0
            or danger_memory_duration < 0
            or food_memory_recall_distance < 0
            or danger_memory_avoid_distance < 0
            or social_influence_distance < 0
            or social_follow_strength < 0
            or social_flee_boost_per_neighbor < 0
            or social_flee_boost_max < 0
        ):
            raise ValueError("rates must be >= 0")

        self.creatures = list(creatures)
        self.food_field = food_field
        self.ai_system = ai_system
        self.energy_drain_rate = energy_drain_rate
        self.movement_speed = movement_speed
        self.eat_rate = eat_rate
        self.reproduction_energy_threshold = reproduction_energy_threshold
        self.reproduction_cost = reproduction_cost
        self.reproduction_distance = reproduction_distance
        self.reproduction_min_age = reproduction_min_age
        self.mutation_variation = mutation_variation
        self.random_source = random_source or random.Random()
        self.world_map = world_map

        self.food_memory_duration = food_memory_duration
        self.danger_memory_duration = danger_memory_duration
        self.food_memory_recall_distance = food_memory_recall_distance
        self.danger_memory_avoid_distance = danger_memory_avoid_distance
        self.social_influence_distance = social_influence_distance
        self.social_follow_strength = social_follow_strength
        self.social_flee_boost_per_neighbor = social_flee_boost_per_neighbor
        self.social_flee_boost_max = social_flee_boost_max

        self.last_intents: Dict[str, CreatureIntent] = {}
        self._child_counter = 0

        self.births_last_tick = 0
        self.total_births = 0
        self.deaths_last_tick = 0
        self.total_deaths = 0
        self.flees_last_tick = 0
        self.total_flees = 0
        self.fleeing_creatures_last_tick: list[str] = []
        self.flee_threat_distance_last_tick: Dict[str, float] = {}
        self.avg_flee_threat_distance_last_tick = 0.0
        self.food_detection_moves_last_tick = 0
        self.total_food_detection_moves = 0
        self.food_perception_sum_detection_last_tick = 0.0
        self.total_food_perception_sum_detection = 0.0
        self.food_consumptions_last_tick = 0
        self.total_food_consumptions = 0
        self.food_perception_sum_consumption_last_tick = 0.0
        self.total_food_perception_sum_consumption = 0.0
        self.threat_detection_flee_last_tick = 0
        self.total_threat_detection_flee = 0
        self.threat_perception_sum_flee_last_tick = 0.0
        self.total_threat_perception_sum_flee = 0.0

        self.food_memory_guided_moves_last_tick = 0
        self.total_food_memory_guided_moves = 0
        self.danger_memory_avoid_moves_last_tick = 0
        self.total_danger_memory_avoid_moves = 0
        self.memory_focus_sum_food_memory_last_tick = 0.0
        self.total_memory_focus_sum_food_memory = 0.0
        self.memory_focus_sum_danger_memory_last_tick = 0.0
        self.total_memory_focus_sum_danger_memory = 0.0
        self.food_memory_distance_gain_last_tick = 0.0
        self.total_food_memory_distance_gain = 0.0
        self.avg_food_memory_distance_gain_last_tick = 0.0
        self.danger_memory_distance_gain_last_tick = 0.0
        self.total_danger_memory_distance_gain = 0.0
        self.avg_danger_memory_distance_gain_last_tick = 0.0
        self.tick_count = 0
        self.social_follow_moves_last_tick = 0
        self.total_social_follow_moves = 0
        self.social_flee_boosted_last_tick = 0
        self.total_social_flee_boosted = 0
        self.social_flee_multiplier_sum_last_tick = 0.0
        self.avg_social_flee_multiplier_last_tick = 1.0
        self.social_influenced_creatures_last_tick = 0
        self.total_social_influenced_creatures = 0
        self.total_social_flee_multiplier_sum = 0.0
        self.social_sensitivity_sum_follow_last_tick = 0.0
        self.total_social_sensitivity_sum_follow = 0.0
        self.social_sensitivity_sum_flee_boost_last_tick = 0.0
        self.total_social_sensitivity_sum_flee_boost = 0.0

        self.energy_drain_events_last_tick = 0
        self.total_energy_drain_events = 0
        self.energy_drain_amount_last_tick = 0.0
        self.total_energy_drain_amount = 0.0
        self.energy_drain_multiplier_sum_last_tick = 0.0
        self.total_energy_drain_multiplier_sum = 0.0
        self.energy_efficiency_sum_drain_last_tick = 0.0
        self.total_energy_efficiency_sum_drain = 0.0
        self.reproduction_cost_events_last_tick = 0
        self.total_reproduction_cost_events = 0
        self.reproduction_cost_amount_last_tick = 0.0
        self.total_reproduction_cost_amount = 0.0
        self.reproduction_cost_multiplier_sum_last_tick = 0.0
        self.total_reproduction_cost_multiplier_sum = 0.0
        self.exhaustion_resistance_sum_reproduction_last_tick = 0.0
        self.total_exhaustion_resistance_sum_reproduction = 0.0

        self.death_causes_last_tick: Dict[str, int] = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }
        self.total_death_causes: Dict[str, int] = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }

    def tick(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")

        self.births_last_tick = 0
        self.deaths_last_tick = 0
        self.flees_last_tick = 0
        self.fleeing_creatures_last_tick = []
        self.flee_threat_distance_last_tick = {}
        self.avg_flee_threat_distance_last_tick = 0.0
        self.food_detection_moves_last_tick = 0
        self.food_perception_sum_detection_last_tick = 0.0
        self.food_consumptions_last_tick = 0
        self.food_perception_sum_consumption_last_tick = 0.0
        self.threat_detection_flee_last_tick = 0
        self.threat_perception_sum_flee_last_tick = 0.0
        self.food_memory_guided_moves_last_tick = 0
        self.danger_memory_avoid_moves_last_tick = 0
        self.memory_focus_sum_food_memory_last_tick = 0.0
        self.memory_focus_sum_danger_memory_last_tick = 0.0
        self.food_memory_distance_gain_last_tick = 0.0
        self.avg_food_memory_distance_gain_last_tick = 0.0
        self.danger_memory_distance_gain_last_tick = 0.0
        self.avg_danger_memory_distance_gain_last_tick = 0.0
        self.social_follow_moves_last_tick = 0
        self.social_sensitivity_sum_follow_last_tick = 0.0
        self.social_flee_boosted_last_tick = 0
        self.social_sensitivity_sum_flee_boost_last_tick = 0.0
        self.social_flee_multiplier_sum_last_tick = 0.0
        self.avg_social_flee_multiplier_last_tick = 1.0
        self.social_influenced_creatures_last_tick = 0
        self.energy_drain_events_last_tick = 0
        self.energy_drain_amount_last_tick = 0.0
        self.energy_drain_multiplier_sum_last_tick = 0.0
        self.energy_efficiency_sum_drain_last_tick = 0.0
        self.reproduction_cost_events_last_tick = 0
        self.reproduction_cost_amount_last_tick = 0.0
        self.reproduction_cost_multiplier_sum_last_tick = 0.0
        self.exhaustion_resistance_sum_reproduction_last_tick = 0.0
        self.death_causes_last_tick = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }

        dead_before = self.get_dead_count()
        alive_before_ids = {creature.creature_id for creature in self.creatures if creature.alive}

        # 1) Passive aging, memory decay and energy loss.
        for creature in self.creatures:
            creature.grow_older(dt)
            creature.decay_memory(dt)
            if creature.alive:
                drain_multiplier = self._compute_energy_efficiency_drain_multiplier(creature)
                effective_drain = self.energy_drain_rate * creature.traits.metabolism * drain_multiplier
                self.energy_drain_events_last_tick += 1
                self.total_energy_drain_events += 1
                self.energy_drain_amount_last_tick += effective_drain * dt
                self.total_energy_drain_amount += effective_drain * dt
                self.energy_drain_multiplier_sum_last_tick += drain_multiplier
                self.total_energy_drain_multiplier_sum += drain_multiplier
                self.energy_efficiency_sum_drain_last_tick += creature.traits.energy_efficiency
                self.total_energy_efficiency_sum_drain += creature.traits.energy_efficiency
            creature.drain_energy(dt=dt, drain_rate=self.energy_drain_rate)

        starvation_deaths = sum(
            1
            for creature in self.creatures
            if creature.creature_id in alive_before_ids and not creature.alive
        )
        self.death_causes_last_tick[self.DEATH_CAUSE_STARVATION] = starvation_deaths

        # 2) Decide behavior for each creature.
        reproduction_candidates = self._build_reproduction_candidates()
        intents: Dict[str, CreatureIntent] = {}
        for creature in self.creatures:
            intents[creature.creature_id] = self.ai_system.decide(
                creature,
                self.food_field,
                can_reproduce=(creature.creature_id in reproduction_candidates),
                nearby_creatures=self.creatures,
            )
        self.last_intents = intents

        for creature in self.creatures:
            if not creature.alive:
                continue
            intent = intents[creature.creature_id]
            if intent.action == HungerAI.ACTION_MOVE_TO_FOOD and intent.target_food_id is not None:
                self.food_detection_moves_last_tick += 1
                self.total_food_detection_moves += 1
                self.food_perception_sum_detection_last_tick += creature.traits.food_perception
                self.total_food_perception_sum_detection += creature.traits.food_perception
            if intent.action == HungerAI.ACTION_FLEE:
                self.threat_detection_flee_last_tick += 1
                self.total_threat_detection_flee += 1
                self.threat_perception_sum_flee_last_tick += creature.traits.threat_perception
                self.total_threat_perception_sum_flee += creature.traits.threat_perception

        # 3) Execute movement and feeding behavior.
        creatures_by_id = {creature.creature_id: creature for creature in self.creatures}
        social_influenced_ids: set[str] = set()

        for creature in self.creatures:
            if not creature.alive:
                continue

            intent = intents[creature.creature_id]
            # THREAT/FLEE: execute flee intent before normal food/wander actions.
            if intent.action == HungerAI.ACTION_FLEE:
                threat = None
                if intent.target_creature_id is not None:
                    threat = creatures_by_id.get(intent.target_creature_id)

                if threat is None or not threat.alive:
                    self._wander(creature, dt, activity=1.0)
                    continue

                threat_distance = creature.distance_to(threat.x, threat.y)
                flee_boost_multiplier = self._social_flee_boost_multiplier(
                    creature,
                    intents,
                    creatures_by_id,
                )
                self._flee_from(creature, threat, dt, boost_multiplier=flee_boost_multiplier)
                if flee_boost_multiplier > 1.0:
                    self.social_flee_boosted_last_tick += 1
                    self.total_social_flee_boosted += 1
                    self.social_flee_multiplier_sum_last_tick += flee_boost_multiplier
                    self.total_social_flee_multiplier_sum += flee_boost_multiplier
                    self.social_sensitivity_sum_flee_boost_last_tick += creature.traits.social_sensitivity
                    self.total_social_sensitivity_sum_flee_boost += creature.traits.social_sensitivity
                    social_influenced_ids.add(creature.creature_id)
                creature.remember_danger_zone(threat.x, threat.y, ttl=self.danger_memory_duration)

                self.flees_last_tick += 1
                self.total_flees += 1
                self.fleeing_creatures_last_tick.append(creature.creature_id)
                self.flee_threat_distance_last_tick[creature.creature_id] = threat_distance
                continue

            if intent.action == "move_to_food" and intent.target_food_id is not None:
                target = self.food_field.get_food(intent.target_food_id)
                if target is None:
                    if not self._move_using_memory(creature, dt, search_mode=True):
                        self._wander(creature, dt, activity=1.0)
                    continue

                reached = creature.move_towards(
                    target_x=target.x,
                    target_y=target.y,
                    max_distance=self.movement_speed * creature.traits.speed * dt,
                )
                self._clamp_creature_position(creature)
                if reached:
                    eaten = self.food_field.consume(target.food_id, self.eat_rate * dt)
                    creature.add_energy(eaten)
                    if eaten > 0.0:
                        self.food_consumptions_last_tick += 1
                        self.total_food_consumptions += 1
                        self.food_perception_sum_consumption_last_tick += creature.traits.food_perception
                        self.total_food_perception_sum_consumption += creature.traits.food_perception
                        creature.remember_food_zone(target.x, target.y, ttl=self.food_memory_duration)
                continue

            if intent.action == "search_food":
                if not self._move_using_memory(creature, dt, search_mode=True):
                    if self._move_using_social_follow(creature, dt, intents, creatures_by_id):
                        social_influenced_ids.add(creature.creature_id)
                    else:
                        # Search mode: more active movement than idle wandering.
                        self._wander(creature, dt, activity=1.0)
                continue

            if intent.action == "wander":
                if not self._move_using_memory(creature, dt, search_mode=False):
                    if self._move_using_social_follow(creature, dt, intents, creatures_by_id):
                        social_influenced_ids.add(creature.creature_id)
                    else:
                        self._wander(creature, dt, activity=0.5)

        self.social_influenced_creatures_last_tick = len(social_influenced_ids)
        self.total_social_influenced_creatures += self.social_influenced_creatures_last_tick

        if self.flee_threat_distance_last_tick:
            self.avg_flee_threat_distance_last_tick = (
                sum(self.flee_threat_distance_last_tick.values())
                / len(self.flee_threat_distance_last_tick)
            )
        else:
            self.avg_flee_threat_distance_last_tick = 0.0

        if self.food_memory_guided_moves_last_tick > 0:
            self.avg_food_memory_distance_gain_last_tick = (
                self.food_memory_distance_gain_last_tick / self.food_memory_guided_moves_last_tick
            )
        else:
            self.avg_food_memory_distance_gain_last_tick = 0.0

        if self.danger_memory_avoid_moves_last_tick > 0:
            self.avg_danger_memory_distance_gain_last_tick = (
                self.danger_memory_distance_gain_last_tick / self.danger_memory_avoid_moves_last_tick
            )
        else:
            self.avg_danger_memory_distance_gain_last_tick = 0.0

        if self.social_flee_boosted_last_tick > 0:
            self.avg_social_flee_multiplier_last_tick = (
                self.social_flee_multiplier_sum_last_tick / self.social_flee_boosted_last_tick
            )
        else:
            self.avg_social_flee_multiplier_last_tick = 1.0

        # 4) Reproduction with simple inheritance + mutation.
        exhaustion_deaths = self._process_reproduction(intents)
        self.death_causes_last_tick[self.DEATH_CAUSE_EXHAUSTION] = exhaustion_deaths

        dead_after = self.get_dead_count()
        self.deaths_last_tick = max(0, dead_after - dead_before)
        self.total_deaths += self.deaths_last_tick

        known_deaths = (
            self.death_causes_last_tick[self.DEATH_CAUSE_STARVATION]
            + self.death_causes_last_tick[self.DEATH_CAUSE_EXHAUSTION]
        )
        self.death_causes_last_tick[self.DEATH_CAUSE_UNKNOWN] = max(0, self.deaths_last_tick - known_deaths)

        for cause, value in self.death_causes_last_tick.items():
            self.total_death_causes[cause] += value

        self.tick_count += 1

    def _is_reproduction_eligible(self, creature: Creature) -> bool:
        return (
            creature.alive
            and creature.age >= self.reproduction_min_age
            and creature.energy >= self.reproduction_energy_threshold
        )

    def _build_reproduction_candidates(self) -> Set[str]:
        eligible = [c for c in self.creatures if self._is_reproduction_eligible(c)]
        candidates: Set[str] = set()

        for idx, parent_a in enumerate(eligible):
            for parent_b in eligible[idx + 1 :]:
                if parent_a.distance_to(parent_b.x, parent_b.y) <= self.reproduction_distance:
                    candidates.add(parent_a.creature_id)
                    candidates.add(parent_b.creature_id)

        return candidates

    def _process_reproduction(self, intents: Dict[str, CreatureIntent]) -> int:
        newborns: list[Creature] = []
        used_ids: set[str] = set()
        exhaustion_deaths = 0

        candidates = [
            c
            for c in self.creatures
            if self._is_reproduction_eligible(c) and intents[c.creature_id].action == "reproduce"
        ]

        for idx, parent_a in enumerate(candidates):
            if parent_a.creature_id in used_ids:
                continue

            for parent_b in candidates[idx + 1 :]:
                if parent_b.creature_id in used_ids:
                    continue
                if parent_a.distance_to(parent_b.x, parent_b.y) > self.reproduction_distance:
                    continue

                child_traits = inherit_traits(
                    parent_a.traits,
                    parent_b.traits,
                    mutation_variation=self.mutation_variation,
                    rng=self.random_source,
                )

                child_x = (parent_a.x + parent_b.x) / 2.0
                child_y = (parent_a.y + parent_b.y) / 2.0
                if self.world_map is not None:
                    child_x, child_y = self.world_map.clamp(child_x, child_y)

                child = Creature(
                    creature_id=f"child_{self._child_counter}",
                    x=child_x,
                    y=child_y,
                    energy=child_traits.max_energy * 0.5,
                    traits=child_traits,
                    generation=max(parent_a.generation, parent_b.generation) + 1,
                    parent_ids=(parent_a.creature_id, parent_b.creature_id),
                )
                self._child_counter += 1
                newborns.append(child)

                parent_a_alive_before = parent_a.alive
                parent_b_alive_before = parent_b.alive

                parent_a_resistance_multiplier = self._compute_exhaustion_resistance_reproduction_multiplier(
                    parent_a
                )
                parent_b_resistance_multiplier = self._compute_exhaustion_resistance_reproduction_multiplier(
                    parent_b
                )
                parent_a_cost = self.reproduction_cost * parent_a_resistance_multiplier
                parent_b_cost = self.reproduction_cost * parent_b_resistance_multiplier

                parent_a.spend_energy(parent_a_cost)
                parent_b.spend_energy(parent_b_cost)
                self.reproduction_cost_events_last_tick += 2
                self.total_reproduction_cost_events += 2
                self.reproduction_cost_amount_last_tick += parent_a_cost + parent_b_cost
                self.total_reproduction_cost_amount += parent_a_cost + parent_b_cost
                self.reproduction_cost_multiplier_sum_last_tick += (
                    parent_a_resistance_multiplier + parent_b_resistance_multiplier
                )
                self.total_reproduction_cost_multiplier_sum += (
                    parent_a_resistance_multiplier + parent_b_resistance_multiplier
                )
                self.exhaustion_resistance_sum_reproduction_last_tick += (
                    parent_a.traits.exhaustion_resistance + parent_b.traits.exhaustion_resistance
                )
                self.total_exhaustion_resistance_sum_reproduction += (
                    parent_a.traits.exhaustion_resistance + parent_b.traits.exhaustion_resistance
                )

                if parent_a_alive_before and not parent_a.alive:
                    exhaustion_deaths += 1
                if parent_b_alive_before and not parent_b.alive:
                    exhaustion_deaths += 1

                used_ids.add(parent_a.creature_id)
                used_ids.add(parent_b.creature_id)
                break

        if newborns:
            self.creatures.extend(newborns)
            self.births_last_tick = len(newborns)
            self.total_births += len(newborns)

        return exhaustion_deaths

    def _move_using_memory(self, creature: Creature, dt: float, search_mode: bool) -> bool:
        if self._avoid_danger_memory(creature, dt):
            return True

        if search_mode:
            return self._move_towards_food_memory(creature, dt, activity=1.0)

        return False

    def _move_towards_food_memory(self, creature: Creature, dt: float, activity: float) -> bool:
        if not creature.has_food_memory:
            return False

        effective_recall_distance = self.food_memory_recall_distance * creature.traits.memory_focus
        if effective_recall_distance <= 0.0:
            return False

        assert creature.last_food_zone is not None
        target_x, target_y = creature.last_food_zone
        distance_to_memory = creature.distance_to(target_x, target_y)
        if distance_to_memory > effective_recall_distance:
            return False

        step_distance = self.movement_speed * activity * creature.traits.speed * dt
        if step_distance <= 0.0:
            return False

        before_distance = distance_to_memory
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=step_distance)
        self._clamp_creature_position(creature)
        after_distance = creature.distance_to(target_x, target_y)
        distance_gain = max(0.0, before_distance - after_distance)

        self.food_memory_guided_moves_last_tick += 1
        self.total_food_memory_guided_moves += 1
        self.memory_focus_sum_food_memory_last_tick += creature.traits.memory_focus
        self.total_memory_focus_sum_food_memory += creature.traits.memory_focus
        self.food_memory_distance_gain_last_tick += distance_gain
        self.total_food_memory_distance_gain += distance_gain
        return True

    def _avoid_danger_memory(self, creature: Creature, dt: float) -> bool:
        if not creature.has_danger_memory:
            return False

        effective_avoid_distance = self.danger_memory_avoid_distance * creature.traits.memory_focus
        if effective_avoid_distance <= 0.0:
            return False

        assert creature.last_danger_zone is not None
        danger_x, danger_y = creature.last_danger_zone
        distance_to_danger = creature.distance_to(danger_x, danger_y)
        if distance_to_danger > effective_avoid_distance:
            return False

        step_distance = self.movement_speed * creature.traits.speed * dt
        if step_distance <= 0.0:
            return False

        before_distance = distance_to_danger
        dx = creature.x - danger_x
        dy = creature.y - danger_y
        if dx == 0.0 and dy == 0.0:
            self._wander(creature, dt, activity=1.0)
        else:
            target_x = creature.x + dx
            target_y = creature.y + dy
            creature.move_towards(target_x=target_x, target_y=target_y, max_distance=step_distance)
            self._clamp_creature_position(creature)
        after_distance = creature.distance_to(danger_x, danger_y)
        distance_gain = max(0.0, after_distance - before_distance)

        self.danger_memory_avoid_moves_last_tick += 1
        self.total_danger_memory_avoid_moves += 1
        self.memory_focus_sum_danger_memory_last_tick += creature.traits.memory_focus
        self.total_memory_focus_sum_danger_memory += creature.traits.memory_focus
        self.danger_memory_distance_gain_last_tick += distance_gain
        self.total_danger_memory_distance_gain += distance_gain
        return True

    def _move_using_social_follow(
        self,
        creature: Creature,
        dt: float,
        intents: Dict[str, CreatureIntent],
        creatures_by_id: Dict[str, Creature],
    ) -> bool:
        effective_social_distance = self.social_influence_distance * creature.traits.social_sensitivity
        effective_follow_strength = self.social_follow_strength * creature.traits.social_sensitivity

        if effective_social_distance <= 0.0 or effective_follow_strength <= 0.0:
            return False

        nearest_target: tuple[float, float] | None = None
        nearest_distance = float("inf")

        for other_id, other_intent in intents.items():
            if other_id == creature.creature_id:
                continue

            other = creatures_by_id.get(other_id)
            if other is None or not other.alive:
                continue

            if other_intent.action != HungerAI.ACTION_MOVE_TO_FOOD or other_intent.target_food_id is None:
                continue

            distance_to_other = creature.distance_to(other.x, other.y)
            if distance_to_other > effective_social_distance:
                continue

            food = self.food_field.get_food(other_intent.target_food_id)
            if food is None:
                continue

            if distance_to_other < nearest_distance:
                nearest_distance = distance_to_other
                nearest_target = (food.x, food.y)

        if nearest_target is None:
            return False

        step_distance = self.movement_speed * creature.traits.speed * dt * effective_follow_strength
        if step_distance <= 0.0:
            return False

        creature.move_towards(
            target_x=nearest_target[0],
            target_y=nearest_target[1],
            max_distance=step_distance,
        )
        self._clamp_creature_position(creature)
        self.social_follow_moves_last_tick += 1
        self.total_social_follow_moves += 1
        self.social_sensitivity_sum_follow_last_tick += creature.traits.social_sensitivity
        self.total_social_sensitivity_sum_follow += creature.traits.social_sensitivity
        return True

    def _social_flee_boost_multiplier(
        self,
        creature: Creature,
        intents: Dict[str, CreatureIntent],
        creatures_by_id: Dict[str, Creature],
    ) -> float:
        effective_social_distance = self.social_influence_distance * creature.traits.social_sensitivity
        effective_boost_per_neighbor = self.social_flee_boost_per_neighbor * creature.traits.social_sensitivity
        effective_boost_max = self.social_flee_boost_max * creature.traits.social_sensitivity

        if effective_social_distance <= 0.0 or effective_boost_per_neighbor <= 0.0:
            return 1.0

        nearby_fleeing = 0
        for other_id, other_intent in intents.items():
            if other_id == creature.creature_id:
                continue

            if other_intent.action != HungerAI.ACTION_FLEE:
                continue

            other = creatures_by_id.get(other_id)
            if other is None or not other.alive:
                continue

            if creature.distance_to(other.x, other.y) <= effective_social_distance:
                nearby_fleeing += 1

        if nearby_fleeing <= 0:
            return 1.0

        boost = min(effective_boost_max, nearby_fleeing * effective_boost_per_neighbor)
        return 1.0 + boost

    def _wander(self, creature: Creature, dt: float, activity: float = 0.5) -> None:
        if activity < 0:
            raise ValueError("activity must be >= 0")

        distance = self.movement_speed * activity * creature.traits.speed * dt
        if distance <= 0:
            return

        angle = self.random_source.uniform(0.0, 2.0 * pi)
        target_x = creature.x + cos(angle) * distance
        target_y = creature.y + sin(angle) * distance
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=distance)
        self._clamp_creature_position(creature)

    # THREAT/FLEE: move in the opposite direction of the threat (no pathfinding).
    def _flee_from(
        self,
        creature: Creature,
        threat: Creature,
        dt: float,
        boost_multiplier: float = 1.0,
    ) -> None:
        flee_distance = self.movement_speed * creature.traits.speed * dt * 1.2 * max(1.0, boost_multiplier)
        if flee_distance <= 0:
            return

        dx = creature.x - threat.x
        dy = creature.y - threat.y

        if dx == 0.0 and dy == 0.0:
            self._wander(creature, dt, activity=1.2)
            return

        target_x = creature.x + dx
        target_y = creature.y + dy
        creature.move_towards(target_x=target_x, target_y=target_y, max_distance=flee_distance)
        self._clamp_creature_position(creature)

    def _clamp_creature_position(self, creature: Creature) -> None:
        if self.world_map is not None:
            creature.x, creature.y = self.world_map.clamp(creature.x, creature.y)

    def get_alive_count(self) -> int:
        return sum(1 for creature in self.creatures if creature.alive)

    def get_dead_count(self) -> int:
        return sum(1 for creature in self.creatures if not creature.alive)

    def get_total_count(self) -> int:
        return len(self.creatures)

    @staticmethod
    def _compute_energy_efficiency_drain_multiplier(creature: Creature) -> float:
        return max(0.1, 1.0 - (0.25 * (creature.traits.energy_efficiency - 1.0)))

    @staticmethod
    def _compute_exhaustion_resistance_reproduction_multiplier(creature: Creature) -> float:
        return max(0.1, 1.0 - (0.3 * (creature.traits.exhaustion_resistance - 1.0)))




