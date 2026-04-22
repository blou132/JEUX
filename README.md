# Sandbox Fantasy 3D Pivot

## Project status
This repository now contains two tracks:
- `game3d/`: active Godot 4 prototype for a WorldBox-like fantasy sandbox.
- `legacy_python/` (logical status): the current Python simulator remains in place as **legacy Python (frozen)** for reference, batch tooling, and historical experiments.

The priority is now visible gameplay in 3D, not new micro-traits in the old simulator.

## New target (3D gameplay core)
The active direction is a minimal but playable sandbox loop:
- autonomous adventurers (humans)
- human role differentiation (fighter / mage / scout)
- autonomous monsters
- lightweight autonomous progression (levels 1->3)
- simple points of interest (POI): camp + ruins
- simple AI FSM: `wander -> detect -> chase -> attack -> flee`
- deterministic melee combat (range + cooldown + damage)
- three simple spells: projectile bolt + short-range nova + control slow
- two additional monster archetypes: brute monster + ranged monster
- sandbox population regulation (minimal respawn)
- runtime observability (debug HUD + event log)

## What is implemented now in `game3d/`
- Godot project bootstrap: [project.godot](game3d/project.godot)
- Main scene: [MainSandbox.tscn](game3d/scenes/MainSandbox.tscn)
- Core loop and orchestration: [GameLoop.gd](game3d/scripts/core/GameLoop.gd)
- Flat world + spawn points + nav grid helpers: [WorldManager.gd](game3d/scripts/world/WorldManager.gd)
- Entities:
  - [Actor.gd](game3d/scripts/entities/Actor.gd)
  - [HumanAgent.gd](game3d/scripts/entities/HumanAgent.gd)
  - [MonsterAgent.gd](game3d/scripts/entities/MonsterAgent.gd)
  - [BruteMonster.gd](game3d/scripts/entities/BruteMonster.gd)
  - [RangedMonster.gd](game3d/scripts/entities/RangedMonster.gd)
- AI decision layer: [AgentAI.gd](game3d/scripts/ai/AgentAI.gd)
- Combat system: [CombatSystem.gd](game3d/scripts/combat/CombatSystem.gd)
- Magic system: [MagicSystem.gd](game3d/scripts/magic/MagicSystem.gd)
- Sandbox regulation: [SandboxSystems.gd](game3d/scripts/sandbox/SandboxSystems.gd)
- Autonomous progression signals:
  - XP triggers on hit/cast/kill + survival time
  - bounded levels (`L1-L3`) with small capped stat gains
  - level-up event log + lightweight visual ring on level-up
- Debug UI:
  - [DebugOverlay.gd](game3d/scripts/ui/DebugOverlay.gd)
  - [FreeCamera.gd](game3d/scripts/ui/FreeCamera.gd)

## How to run the 3D prototype
Prerequisite: Godot 4.x installed locally.

1. Open Godot and import `game3d/project.godot`.
2. Run the project (main scene is `MainSandbox.tscn`).

Camera controls:
- `W A S D`: move on the XZ plane
- `Q / E`: down / up
- `Shift`: speed boost
- Hold right mouse button + move mouse: look around

## What to observe in the running sandbox
The debug overlay shows:
- alive population split (humans / monsters)
- human role split (`fighter`, `mage`, `scout`)
- brute monster count
- ranged monster count
- average HP and energy
- progression visibility (`avg_level`, `level_ups`, level distribution `L1/L2/L3`, split humans/monsters)
- melee hits, magic hits, casts (bolt/control/nova), kills, deaths, flee events
- control readability (`control applies`, `slowed alive` total + split H/M)
- current AI state distribution (`wander`, `poi`, `detect`, `chase`, `attack`, `cast`, `cast_control`, `cast_nova`, `reposition`, `flee`)
- POI status readability (`calme`, `conteste`, `domine_humains`, `domine_monstres`) + activity level
- POI occupancy (`camp`, `ruins`) with clearer format and POI event counters
- recent gameplay events (engagements, hits, deaths, casts, POI arrivals, contestation, domination shifts)
- role-aware logs for human actions (labels include role tags)

Validation target for current MVP:
- repeated cycles of encounter -> chase/attack/cast -> death or flee -> respawn

## Legacy Python status
The existing Python modules are intentionally preserved and not expanded as the main direction:
- `simulation/`, `ai/`, `creatures/`, `genetics/`, `world/`, `ui/`, `debug_tools/`, `save/`, `player/`

You can still run the old simulator and analytics if needed, but this is now secondary.

## Tests
Current scaffold checks for the 3D pivot:
- [test_game3d_scaffold.py](tests/test_game3d_scaffold.py)
- [test_game3d_behavioral_logic.py](tests/test_game3d_behavioral_logic.py) (behavior contracts: IA, POI runtime, spawn mix)
- [test_game3d_progression_behavior.py](tests/test_game3d_progression_behavior.py) (progression contracts: thresholds, XP triggers, survival pacing, snapshot fields)

Run targeted tests:
```bash
py -m unittest tests.test_game3d_scaffold -v
py -m unittest tests.test_game3d_behavioral_logic -v
py -m unittest tests.test_game3d_progression_behavior -v
```

Run full existing suite if needed:
```bash
py -m unittest discover -s tests -v
```

## Roadmap (updated)
### Done
- Add Godot 4 project alongside existing Python codebase
- Build minimal 3D sandbox scene with free camera
- Add autonomous humans/monsters
- Add FSM AI + melee + two-spell magic (bolt + nova)
- Add minimal sandbox regulation and debug observability
- Add simple POI layer (camp/ruins) with light AI convergence
- Add POI runtime readability: visual occupation signals, domination indicator, entry pulse effect, POI state events
- Add brute monster archetype for profile diversity
- Add ranged monster archetype with distance-keeping behavior and bolt pressure
- Add utility/control spell (short slow) with dedicated logs and HUD counters
- Add behavioral test coverage for IA decisions, POI runtime shape, and monster spawn coherence
- Add human role MVP (fighter/mage/scout) with stat/behavior differences and HUD/log visibility
- Add lightweight autonomous progression MVP (XP hit/cast/kill/survival, capped levels, level-up observability)

### Next
- Tune role balance and combat pacing from play sessions (durability/readability pass)
- Add one additional monster archetype focused on utility/disruption

### Later
- Replace placeholder meshes/FX with stylized fantasy assets
- Add player sandbox interventions (spawn, buff/debuff, world events)
- Add richer world simulation layers (factions, settlements, quests)

## Scope guard
- No global refactor of the legacy Python simulator during 3D MVP buildout.
- No heavy ML/complex systems before the gameplay core is robust and playable.
- Keep the 3D prototype modular, observable, and iteration-friendly.
