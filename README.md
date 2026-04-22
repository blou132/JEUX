# Sandbox Fantasy 3D Pivot

## Project status
This repository now contains two tracks:
- `game3d/`: active Godot 4 prototype for a WorldBox-like fantasy sandbox.
- `legacy_python/` (logical status): the current Python simulator remains in place as **legacy Python (frozen)** for reference, batch tooling, and historical experiments.

The priority is now visible gameplay in 3D, not new micro-traits in the old simulator.

## New target (3D gameplay core)
The active direction is a minimal but playable sandbox loop:
- autonomous adventurers (humans)
- autonomous monsters
- simple points of interest (POI): camp + ruins
- simple AI FSM: `wander -> detect -> chase -> attack -> flee`
- deterministic melee combat (range + cooldown + damage)
- two simple spells: projectile bolt + short-range nova
- one additional monster archetype: brute monster
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
- AI decision layer: [AgentAI.gd](game3d/scripts/ai/AgentAI.gd)
- Combat system: [CombatSystem.gd](game3d/scripts/combat/CombatSystem.gd)
- Magic system: [MagicSystem.gd](game3d/scripts/magic/MagicSystem.gd)
- Sandbox regulation: [SandboxSystems.gd](game3d/scripts/sandbox/SandboxSystems.gd)
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
- brute monster count
- average HP and energy
- melee hits, magic hits, casts (bolt/nova), kills, deaths, flee events
- current AI state distribution (`wander`, `poi`, `detect`, `chase`, `attack`, `cast`, `cast_nova`, `flee`)
- POI occupancy (`camp`, `ruins`)
- recent gameplay events (engagements, hits, deaths, casts)

Validation target for current MVP:
- repeated cycles of encounter -> chase/attack/cast -> death or flee -> respawn

## Legacy Python status
The existing Python modules are intentionally preserved and not expanded as the main direction:
- `simulation/`, `ai/`, `creatures/`, `genetics/`, `world/`, `ui/`, `debug_tools/`, `save/`, `player/`

You can still run the old simulator and analytics if needed, but this is now secondary.

## Tests
Current scaffold checks for the 3D pivot:
- [test_game3d_scaffold.py](tests/test_game3d_scaffold.py)

Run targeted tests:
```bash
py -m unittest tests.test_game3d_scaffold -v
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
- Add brute monster archetype for profile diversity

### Next
- Improve POI behavior readability (per-POI event cues and clearer occupancy feedback)
- Add one extra spell archetype (control/utility) and one ranged monster archetype
- Tune combat/magic values from play sessions (durability/readability pass)

### Later
- Replace placeholder meshes/FX with stylized fantasy assets
- Add player sandbox interventions (spawn, buff/debuff, world events)
- Add richer world simulation layers (factions, settlements, quests)

## Scope guard
- No global refactor of the legacy Python simulator during 3D MVP buildout.
- No heavy ML/complex systems before the gameplay core is robust and playable.
- Keep the 3D prototype modular, observable, and iteration-friendly.
