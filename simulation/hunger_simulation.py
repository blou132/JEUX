from __future__ import annotations

import random
from typing import Dict, Iterable

from ai import CreatureIntent, HungerAI
from creatures import Creature
from genetics import inherit_traits
from world import FoodField


class HungerSimulation:
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
        mutation_variation: float = 0.1,
        random_source: random.Random | None = None,
    ) -> None:
        if (
            energy_drain_rate < 0
            or movement_speed < 0
            or eat_rate < 0
            or reproduction_energy_threshold < 0
            or reproduction_cost < 0
            or reproduction_distance < 0
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
        self.mutation_variation = mutation_variation
        self.random_source = random_source or random.Random()
        self.last_intents: Dict[str, CreatureIntent] = {}
        self._child_counter = 0

    def tick(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt must be >= 0")

        # 1) Passive energy loss.
        for creature in self.creatures:
            creature.drain_energy(dt=dt, drain_rate=self.energy_drain_rate)

        # 2) Decide behavior for alive creatures.
        intents: Dict[str, CreatureIntent] = {}
        for creature in self.creatures:
            intents[creature.creature_id] = self.ai_system.decide(creature, self.food_field)
        self.last_intents = intents

        # 3) Execute simple seek-food behavior.
        for creature in self.creatures:
            intent = intents[creature.creature_id]
            if intent.action != "seek_food" or not creature.alive or intent.target_food_id is None:
                continue

            target = self.food_field.get_food(intent.target_food_id)
            if target is None:
                continue

            reached = creature.move_towards(
                target_x=target.x,
                target_y=target.y,
                max_distance=self.movement_speed * creature.traits.speed * dt,
            )
            if reached:
                eaten = self.food_field.consume(target.food_id, self.eat_rate * dt)
                creature.add_energy(eaten)

        # 4) Reproduction with simple inheritance + mutation.
        newborns: list[Creature] = []
        used_ids: set[str] = set()
        candidates = [
            c
            for c in self.creatures
            if c.alive and c.energy >= self.reproduction_energy_threshold and c.creature_id not in used_ids
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
                child = Creature(
                    creature_id=f"child_{self._child_counter}",
                    x=(parent_a.x + parent_b.x) / 2.0,
                    y=(parent_a.y + parent_b.y) / 2.0,
                    energy=child_traits.max_energy * 0.5,
                    traits=child_traits,
                    generation=max(parent_a.generation, parent_b.generation) + 1,
                    parent_ids=(parent_a.creature_id, parent_b.creature_id),
                )
                self._child_counter += 1
                newborns.append(child)

                parent_a.spend_energy(self.reproduction_cost)
                parent_b.spend_energy(self.reproduction_cost)
                used_ids.add(parent_a.creature_id)
                used_ids.add(parent_b.creature_id)
                break

        if newborns:
            self.creatures.extend(newborns)

    def get_alive_count(self) -> int:
        return sum(1 for creature in self.creatures if creature.alive)
