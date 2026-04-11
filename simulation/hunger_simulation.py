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

        self.last_intents: Dict[str, CreatureIntent] = {}
        self._child_counter = 0

        self.births_last_tick = 0
        self.total_births = 0
        self.deaths_last_tick = 0
        self.total_deaths = 0
        self.flees_last_tick = 0
        self.total_flees = 0
        self.fleeing_creatures_last_tick: list[str] = []

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
        self.death_causes_last_tick = {
            self.DEATH_CAUSE_STARVATION: 0,
            self.DEATH_CAUSE_EXHAUSTION: 0,
            self.DEATH_CAUSE_UNKNOWN: 0,
        }

        dead_before = self.get_dead_count()
        alive_before_ids = {creature.creature_id for creature in self.creatures if creature.alive}

        # 1) Passive aging and energy loss.
        for creature in self.creatures:
            creature.grow_older(dt)
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

        # 3) Execute movement and feeding behavior.
        creatures_by_id = {creature.creature_id: creature for creature in self.creatures}

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
                else:
                    self._flee_from(creature, threat, dt)

                self.flees_last_tick += 1
                self.total_flees += 1
                self.fleeing_creatures_last_tick.append(creature.creature_id)
                continue

            if intent.action == "move_to_food" and intent.target_food_id is not None:
                target = self.food_field.get_food(intent.target_food_id)
                if target is None:
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
                continue

            if intent.action == "search_food":
                # Search mode: more active movement than idle wandering.
                self._wander(creature, dt, activity=1.0)
                continue

            if intent.action == "wander":
                self._wander(creature, dt, activity=0.5)

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

                parent_a.spend_energy(self.reproduction_cost)
                parent_b.spend_energy(self.reproduction_cost)

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
    def _flee_from(self, creature: Creature, threat: Creature, dt: float) -> None:
        flee_distance = self.movement_speed * creature.traits.speed * dt * 1.2
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





