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
- emergent champion layer (rare `hero/elite` promotions)
- lightweight champion-led rally groups (`rally/warband` MVP)
- simple points of interest (POI): camp + ruins
- POI territorial influence (activation after stable domination)
- POI persistent structures (camp -> outpost, ruins -> lair)
- POI raid pressure cycles (outpost <-> lair)
- lightweight allegiance/proto-faction layer (structure-anchored)
- lightweight global world events layer (single active temporary perturbation)
- lightweight special arrivals layer (rare summoned champions)
- lightweight relics layer (rare carrier-bound artifacts)
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
- POI influence layer (MVP):
  - `camp` gives a light local boost to humans when human-dominated long enough
  - `ruins` gives a light local boost to monsters when monster-dominated long enough
  - effects are bounded and local to POI radius (energy regen + slow periodic XP)
- POI structure layer (MVP):
  - `camp` can evolve to `human_outpost` after sufficiently stable human control
  - `ruins` can evolve to `monster_lair` after sufficiently stable monster control
  - structures are runtime-persistent but can be lost if control stays broken long enough
  - bounded gameplay effect: active structures add a small local regen bonus on top of POI influence
  - observability: dedicated logs (`POI structure UP/DOWN`), structure status in HUD/POI snapshot, light `StructureHalo` visual
- Raid pressure layer (MVP):
  - when both `human_outpost` and `monster_lair` are active, temporary raids can start between structures
  - each raid has a source/target POI, finite duration, and simple cooldown
  - raid pressure lightly increases allied convergence toward the enemy structure (`raid` guidance state)
  - raid ends cleanly on success/timeout/interruption (structure loss or control break)
  - observability: `Raid START` / `Raid END` logs, raid status in HUD, and raid source/target POI markers
- Allegiance / proto-faction layer (MVP):
  - each active structure anchor can emit a lightweight allegiance id (`human:camp`, `monster:ruins`)
  - nearby units can be assigned to a matching allegiance and keep it while the anchor remains active
  - allegiance is lost automatically if the anchor disappears
  - bounded behavior effect: same-allegiance cohesion for champion rally and home-defense bias under raid pressure
  - observability: `Allegiance UP/DOWN/assign/lost` logs, allegiance counters in HUD, and allegiance id per POI snapshot
- World events layer (MVP):
  - one temporary world event at a time, autonomous trigger with bounded cooldown/duration
  - `mana_surge` (Mana Surge): light global magic boost (magic damage up, magic energy cost down)
  - `monster_frenzy` (Monster Frenzy): light monster pressure boost (monster melee/speed up, monster raid pressure up)
  - `sanctuary_calm` (Sanctuary Calm): light human stabilization (human passive energy regen, raid pressure reduced)
  - observability: dedicated `World Event START/END` logs, HUD active event + remaining time + start/end counters, subtle POI tint shift
- Special arrivals layer (MVP):
  - rare autonomous arrivals gated by existing world state (active structure, stable dominance, matching world event, cooldown, active cap)
  - human variant: `summoned_hero` (Summoned Hero), tied to `sanctuary_calm` + `human_outpost`
  - monster variant: `calamity_invader` (Calamity Invader), tied to `monster_frenzy` + `monster_lair`
  - each arrival uses existing actors with a lightweight special origin tag, bounded bonus package, champion initialization, and optional allegiance anchor
  - observability: dedicated `Special Arrival START/FALLEN` logs, HUD active split (humans/monsters), and total/fallen counters
- Relics / artifacts layer (MVP):
  - rare autonomous artifact appearances with bounded cooldown/cap and structure + world-event + dominance gates
  - carrier model only (no inventory): one relic max per actor, relic active while carrier is alive
  - `arcane_sigil`: light personal magic boost (damage up, magic cost down)
  - `oath_standard`: light leadership/survival boost (melee up, extra rally cohesion, small energy sustain)
  - acquisition is restricted to nearby champion/special-arrival profiles around stable anchors
  - loss behavior is safe and simple: relic is reset on carrier death (no persistent drop chain)
  - observability: dedicated `Relic APPEAR/ACQUIRED/LOST` logs, HUD active split and carrier labels
- Champion layer (MVP):
  - rare promotion based on notable performance (level, kills, survival, XP)
  - bounded bonus package (small combat/survival boost with light role/archetype flavor)
  - clear observability: tags in logs, promotion events, champion counters in HUD
- Rally / warband layer (MVP):
  - nearby allies can temporarily regroup around allied champions
  - champions in active engagement can pull nearby allies toward the same pressure target
  - bounded cohesion bonus near leader (slight energy drain reduction for followers)
  - runtime observability: group formed/dissolved events and leader/follower counters in HUD
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
- champion visibility (`alive`, split humans/monsters, promotions, champion kills)
- rally visibility (`leaders`, `followers`, split humans/monsters, near-leader bonus followers)
- melee hits, magic hits, casts (bolt/control/nova), kills, deaths, flee events
- control readability (`control applies`, `slowed alive` total + split H/M)
- current AI state distribution (`wander`, `poi`, `raid`, `rally`, `detect`, `chase`, `attack`, `cast`, `cast_control`, `cast_nova`, `reposition`, `flee`)
- POI status readability (`calme`, `conteste`, `domine_humains`, `domine_monstres`) + activity level
- POI occupancy (`camp`, `ruins`) with dominance duration, influence status, and structure status (`outpost`/`lair`)
- POI influence counters (`active`, activation/deactivation events, regen ticks, XP ticks)
- POI structure counters (`active`, created/lost, extra regen ticks from structures)
- raid counters (`active`, starts/ends, success/interrupted/timeout)
- allegiance counters (`active`, affiliated/unassigned, creation/removal/assignment/loss)
- world event counters (`active`, remaining/next timer, starts/ends)
- special arrival counters (`active`, split H/M, total arrivals, fallen)
- relic counters (`active`, split H/M, appear/acquired/lost)
- relic carriers (`relic -> carrier` labels)
- recent gameplay events (engagements, hits, deaths, casts, POI arrivals, contestation, domination shifts)
- POI influence events (`ON`/`OFF`) when control stays stable long enough or is lost
- POI structure events (`UP`/`DOWN`) when persistent structures are created or destroyed
- raid events (`START`/`END`) for autonomous pressure cycles between structures
- allegiance events (`UP`/`DOWN` + unit assignment/loss) to track emerging proto-factions
- world event logs (`START`/`END`) for temporary global perturbations
- special arrival logs (`START`/`FALLEN`) for rare exceptional units
- relic logs (`APPEAR`/`ACQUIRED`/`LOST`) for rare artifact stories
- champion events (`Champion promoted`, `Champion fallen`)
- rally events (`Rally formed`, `Rally dissolved`)
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
- [test_game3d_behavioral_logic.py](tests/test_game3d_behavioral_logic.py) (behavior contracts: IA, POI runtime/influence/structure/raid/allegiance, spawn mix)
- [test_game3d_progression_behavior.py](tests/test_game3d_progression_behavior.py) (progression contracts: thresholds, XP triggers, survival pacing, snapshot fields)
- [test_game3d_world_events_behavior.py](tests/test_game3d_world_events_behavior.py) (world event contracts: trigger cadence, end/reset, bounded modifiers)
- [test_game3d_special_arrivals_behavior.py](tests/test_game3d_special_arrivals_behavior.py) (special arrival contracts: trigger conditions, cooldown/cap gates, bounded integration hooks)
- [test_game3d_relics_behavior.py](tests/test_game3d_relics_behavior.py) (relic contracts: bounded appearance, carrier gating, cooldown/cap, loss reset)

Run targeted tests:
```bash
py -m unittest tests.test_game3d_scaffold -v
py -m unittest tests.test_game3d_behavioral_logic -v
py -m unittest tests.test_game3d_progression_behavior -v
py -m unittest tests.test_game3d_world_events_behavior -v
py -m unittest tests.test_game3d_special_arrivals_behavior -v
py -m unittest tests.test_game3d_relics_behavior -v
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
- Add POI territorial influence MVP (stable domination -> bounded local faction bonus + runtime logs/HUD counters)
- Add emergent champion MVP (rare hero/elite promotions with bounded bonuses and runtime visibility)
- Add champion-led rally/warband MVP (temporary local regrouping + bounded cohesion bonus + runtime counters/logs)
- Add POI persistent structures MVP (`human_outpost` / `monster_lair`) with bounded local bonus and destroy-on-instability behavior
- Add autonomous POI raid pressure MVP (temporary source->target raid guidance with cooldown and bounded conflict cycles)
- Add lightweight allegiance/proto-faction MVP anchored on structures, with unit affiliation stability and bounded behavior bias
- Add autonomous world events MVP (single active event, bounded temporary effects, dedicated observability)
- Add rare special arrivals MVP (`Summoned Hero` / `Calamity Invader`) with bounded spawn conditions, champion seeding, and runtime visibility
- Add rare relic/artifact MVP (`Arcane Sigil` / `Oath Standard`) with bounded carrier assignment and death-reset behavior

### Next
- Tune role balance and combat pacing from play sessions (durability/readability pass)
- Tune POI influence timing/strength to avoid snowball while keeping territorial readability
- Tune POI structure thresholds (activation/loss/presence) to keep structures visible but not snowballing
- Tune raid timing/cooldowns/success conditions for readable pressure cycles without permanent snowball
- Tune allegiance assignment radius and defense bias to improve group coherence without hard-locking unit behavior
- Tune champion rarity thresholds (promotion criteria/cap) from live runs
- Tune rally distances/probabilities to avoid over-clumping while keeping readable group behavior
- Tune world event cadence/duration/effect strength for high variety without persistent snowball
- Tune special arrival rarity gates (dominance threshold/cooldown/cap) for memorable spikes without destabilizing baseline simulation
- Tune relic appearance and effect strengths (cooldown/gates/bonuses) for memorable local stories without runaway scaling

### Later
- Replace placeholder meshes/FX with stylized fantasy assets
- Add player sandbox interventions (spawn, buff/debuff, world events)
- Add richer world simulation layers (factions, settlements, quests)

## Scope guard
- No global refactor of the legacy Python simulator during 3D MVP buildout.
- No heavy ML/complex systems before the gameplay core is robust and playable.
- Keep the 3D prototype modular, observable, and iteration-friendly.
