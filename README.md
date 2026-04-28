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
- simple points of interest (POI): camp + ruins + neutral rift gate
- POI territorial influence (activation after stable domination)
- POI persistent structures (camp -> outpost, ruins -> lair)
- POI raid pressure cycles (outpost <-> lair)
- lightweight allegiance/proto-faction layer (structure-anchored)
- lightweight allegiance doctrine/ethos layer (bounded behavior bias)
- lightweight allegiance projects layer (temporary objective pulses)
- lightweight allegiance vendetta/grudge layer (bounded conflict memory)
- lightweight succession/legacy layer (bounded continuity after notable falls)
- lightweight memorial/scar layer (short-lived local post-fall traces)
- lightweight global world events layer (single active temporary perturbation)
- lightweight special arrivals layer (rare summoned champions)
- lightweight relics layer (rare carrier-bound artifacts)
- lightweight bounty / marked-target layer (rare notable hunt pressure)
- lightweight renown/notoriety layer (known figures with bounded social pressure)
- lightweight rift gate responses layer (bounded allegiance reactions around open gate)
- lightweight allegiance crisis layer (bounded temporary instability after major shocks)
- lightweight recovery pulse layer (bounded post-shock allegiance rebound)
- lightweight destiny pulls layer (rare temporary heroic aspirations toward local world stakes)
- lightweight crossroads/convergence events layer (rare short local signal overlap moments)
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
- Allegiance doctrines / ethos layer (MVP):
  - each active allegiance anchor can hold exactly one lightweight doctrine: `warlike`, `steadfast`, or `arcane`
  - doctrine is assigned at anchor creation using safe local context (structure type + current world-event/champion signal)
  - doctrine disappears automatically with allegiance/anchor loss (no global memory system)
  - bounded effect layer only: small deltas on raid pressure, home defense bias, rally regroup/pressure behavior, and (for `arcane`) light magic efficiency
  - observability: dedicated `Doctrine assigned` logs, doctrine labels per active allegiance, and HUD counters/map per doctrine
- Allegiance projects / faction projects layer (MVP):
  - each active allegiance can run at most one temporary project at a time, with a bounded cooldown between projects
  - project launch is autonomous and context-safe (home role in active raid, doctrine bias, current world event), with no economy/tech tree
  - compact project set: `fortify`, `warband_muster`, `ritual_focus`
  - bounded effects only:
    - `fortify`: small home-defense boost + slight raid pressure reduction
    - `warband_muster`: small raid pressure boost + slight rally regroup boost
    - `ritual_focus`: slight magic efficiency boost (damage up, energy cost down)
  - lifecycle is explicit and safe: `Project START` -> `Project END`, with `Project INTERRUPTED` on anchor/allegiance loss
  - observability: HUD project counters/map and project label in allegiance/POI labels
- Allegiance vendettas / grudges layer (MVP):
  - each active allegiance can hold at most one vendetta target at a time (`source -> target`) with bounded duration and cooldown
  - trigger signals reuse existing conflict events: mainly raid losses, plus notable bounty-kill incidents when safe
  - lifecycle is bounded: `Vendetta START` then `Vendetta RESOLVED` (target gone) or `Vendetta EXPIRED` (time), both producing `Vendetta END`
  - bounded behavior bias only: small raid-priority increase versus vendetta target allegiance and slight bounty pressure bias toward that target allegiance
  - integration stays light and readable with doctrine/projects by additive small deltas (no diplomacy matrix)
  - observability: vendetta counters + source/target map in HUD, plus vendetta tags in allegiance labels
- Succession / legacy layer (MVP):
  - only notable fallen figures can trigger legacy continuity (champion, special arrival, relic carrier, or very high renown/notoriety)
  - trigger is rare and bounded (cooldown + chance + small active successor cap)
  - lightweight successor flow: a nearby allied successor can be chosen, receiving a small renown/notoriety transfer
  - if the fallen figure carried a relic and successor is eligible, relic inheritance can happen directly (`Relic INHERITED`)
  - vendetta integration stays light: a notable legacy fall can seed a vendetta impulse against the killer allegiance when context exists
  - observability: `Legacy Triggered` / `Successor Chosen` / `Legacy Faded` logs, HUD counters, and short active successor list
- Memorial/scar layer (MVP):
  - only notable falls can spawn a local short-lived site (`memorial_site` or `scar_site`) at death location
  - trigger reuses existing notable markers (champion, special arrival, relic carrier, high renown/notoriety, legacy-triggered falls)
  - bounded runtime: finite duration + small global active cap + clean fade-out (`Memorial/Scar BORN` / `Memorial/Scar FADED`)
  - bounded local effects only:
    - `memorial_site`: tiny local renown pulse for nearby allied units
    - `scar_site`: tiny local notoriety pulse for nearby opposing units
  - light integration: renown/notoriety pulses can indirectly feed local rally, legacy continuity readability, and bounty pressure
  - observability: dedicated HUD counters + short active site labels (`M:` / `S:`)
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
- Bounties / marked targets layer (MVP):
  - rare autonomous marks with bounded cooldown/cap (`max 1 active`) and structure/allegiance anchors
  - target profiles reuse existing notable enemies with safe priority: relic carrier > special arrival > champion
  - lightweight integration: emitter-side hunt guidance (`hunt` state) nudges allied convergence toward marked target zone
  - clear bounded reward: on target fall, nearby emitter allies receive a small XP pulse
  - observability: dedicated `Bounty START/CLEARED/EXPIRED` logs, HUD active status + source/target + counters, light marker signal on target
- Renown / notoriety layer (MVP):
  - each actor now carries bounded `renown` (admiration) and `notoriety` (threat) scores (`0..100`)
  - score gains reuse existing notable runtime signals (kill, level-up, champion promotion, special arrival, relic acquisition, active bounty mark)
  - light passive dissipation reduces long-term snowball while preserving notable spikes
  - AI integration stays lightweight: nearby allies can rally around non-champion renowned figures; weak units may avoid very notorious enemies; high-notoriety enemies are slightly easier bounty targets
  - observability: dedicated `Renown Rising` / `Notoriety Rising` threshold logs, HUD split counters, and top notable figures lists
- Neutral dungeon/gate layer (MVP):
  - a unique neutral POI `rift_gate` can cycle between `dormant` and `open` runtime states with bounded duration/cooldown
  - autonomous trigger stays rare and safe: active world event + stable anchored domination + gate cooldown/retry guards
  - bounded local pressure: nearby cautious units can avoid an open gate while stronger/notable units can investigate it
  - bounded breach effect: each open cycle can spawn one lightweight `rift_gate_breach` special invader near the gate
  - light integration: breach events can slightly accelerate bounty checks and feed renown/notoriety stories without heavy snowball
  - observability: dedicated `Dungeon/Gate OPEN` / `Dungeon/Gate CLOSED` / `Dungeon/Gate BREACH` logs, HUD gate status/timer/counters, and distinct gate pulse visual
- Rift gate responses layer (MVP):
  - two bounded allegiance responses can react to an open gate:
    - `gate_seal` (human, defensive arcane response)
    - `gate_exploit` (monster, hostile opportunistic response)
  - hard gates for clarity/safety: gate must be open, active allegiance anchor required, one active response max per faction, per-faction cooldown
  - lightweight criteria reuse existing runtime context (allegiance doctrine/project, anchor proximity to gate, nearby notable presence)
  - lightweight effects only:
    - `gate_seal`: shortens current gate open remaining time a little
    - `gate_exploit`: slightly extends open remaining time and can request at most one bonus breach per open cycle
  - lightweight IA integration through existing `get_neutral_gate_guidance` path: active response gives a small temporary pull boost to concerned faction near gate
  - clean lifecycle: `START` -> `SUCCESS`/`INTERRUPTED` -> `END`; interruption on gate close or anchor loss
- Allegiance crisis layer (MVP):
  - one bounded temporary `crisis` state max per allegiance, with per-allegiance cooldown and short duration
  - trigger signals reuse existing shocks: notable allegiance figure fall, heavy vendetta starts, central bounty pressure, and impactful project interruptions
  - lightweight effects only:
    - rally cohesion dip: rally bonus around the crisis allegiance is reduced intermittently
    - raid pressure dip: allegiance raid guidance weight is slightly reduced while crisis is active
  - clean exits:
    - `EXPIRED` on timeout or anchor loss
    - `RESOLVED` if a successor stabilizes the allegiance (or via favorable event pulse)
  - observability: dedicated `Crisis START/END/RESOLVED/EXPIRED` logs and HUD crisis counters/map
- Recovery pulse layer (MVP):
  - one bounded temporary `recovery` pulse max per allegiance, with per-allegiance cooldown and short duration
  - trigger signals reuse existing stabilization moments: crisis resolution, successful succession, vendetta end, raid endured, and rapid anchor re-stabilization after structure loss
  - lightweight effects only:
    - rally cohesion uplift: crisis-affected allegiance followers can briefly regain rally bonus more often
    - local defense uplift: home defense guidance weight gets a small temporary boost for recovering allegiance
  - interruption is explicit and safe: pulse ends early if anchor falls again (or if crisis restarts)
  - observability: dedicated `Recovery START/END/INTERRUPTED` logs and HUD recovery counters/map
- Destiny pulls layer (MVP):
  - no quest system: only rare short-lived pull states for notable/promising actors, with one active destiny max per actor
  - candidate signals reuse existing notability markers (champion, special arrival, relic carrier, active successor, very high renown), with simple cooldown gates
  - bounded pull types only: `rift_call` (toward open `rift_gate`), `relic_call` (toward active relic carrier), `vendetta_call` (toward active vendetta anchor)
  - lightweight gameplay effect: slight directional convergence via existing `poi/hunt` guidance + tiny local energy sustain near objective
  - clean runtime lifecycle: `Destiny START` -> `Destiny FULFILLED`/`Destiny INTERRUPTED` -> `Destiny END` (or timeout end)
  - observability: HUD counters + active pull labels (`type:actor->target`) and a lightweight actor fate tag
- Crossroads / convergence events layer (MVP):
  - rare short-lived local `convergence` events triggered only when strong existing signals overlap around an open `rift_gate`
  - safe trigger set kept narrow: local destiny presence + (local relic carrier or local notable figure), with hard gate-open, active-cap, and global cooldown bounds
  - lightweight local effects only: tiny local renown/notoriety pulses and slight temporary AI pull toward the convergence zone
  - clean lifecycle: `Convergence START` -> `Convergence END`, with `Convergence INTERRUPTED` if gate closes or local signals collapse
  - observability: dedicated HUD counters + active convergence labels and a distinct short-lived world signal ring/beacon
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
- renown/notoriety visibility (`avg`, split notable figures, rising threshold counters)
- top notable figure labels (`renown` and `notoriety` leaders)
- rally visibility (`leaders`, `followers`, split humans/monsters, near-leader bonus followers)
- melee hits, magic hits, casts (bolt/control/nova), kills, deaths, flee events
- control readability (`control applies`, `slowed alive` total + split H/M)
- current AI state distribution (`wander`, `poi`, `raid`, `rally`, `detect`, `chase`, `attack`, `cast`, `cast_control`, `cast_nova`, `reposition`, `flee`)
- POI status readability (`calme`, `conteste`, `domine_humains`, `domine_monstres`) + activity level
- POI occupancy (`camp`, `ruins`, `rift_gate`) with dominance duration, influence status, structure status (`outpost`/`lair`), and gate state
- POI influence counters (`active`, activation/deactivation events, regen ticks, XP ticks)
- POI structure counters (`active`, created/lost, extra regen ticks from structures)
- raid counters (`active`, starts/ends, success/interrupted/timeout)
- neutral gate counters (`status`, `remaining/cooldown`, `opens`, `closes`, `breaches`)
- gate response counters (`human active`, `monster active`, `starts`, `ends`, `success`, `interrupted`)
- allegiance crisis counters (`active`, `start/end/resolved/expired`) + crisis map per allegiance
- recovery pulse counters (`active`, `start/end/interrupted`) + recovery map per allegiance
- destiny pull counters (`active`, `start/end/fulfilled/interrupted`) + active pull labels
- convergence counters (`active`, `start/end/interrupted`) + active zone labels
- allegiance counters (`active`, affiliated/unassigned, creation/removal/assignment/loss)
- doctrine counters (`warlike`, `steadfast`, `arcane`) + doctrine map per active allegiance
- project counters (`fortify`, `warband_muster`, `ritual_focus`) + active project map per allegiance
- vendetta counters (`active`, `start/end/resolved/expired`) + active vendetta map (`source->target`)
- legacy counters (`triggered`, `successors`, `relic_inherited`, `faded`) + active successor list
- memorial/scar counters (`active`, `memorial`, `scar`, `born`, `faded`) + active site list
- world event counters (`active`, remaining/next timer, starts/ends)
- special arrival counters (`active`, split H/M, total arrivals, fallen)
- relic counters (`active`, split H/M, appear/acquired/lost)
- relic carriers (`relic -> carrier` labels)
- bounty counters (`active`, source, marked target, starts/cleared/expired)
- recent gameplay events (engagements, hits, deaths, casts, POI arrivals, contestation, domination shifts)
- POI influence events (`ON`/`OFF`) when control stays stable long enough or is lost
- POI structure events (`UP`/`DOWN`) when persistent structures are created or destroyed
- raid events (`START`/`END`) for autonomous pressure cycles between structures
- allegiance events (`UP`/`DOWN` + unit assignment/loss) to track emerging proto-factions
- world event logs (`START`/`END`) for temporary global perturbations
- special arrival logs (`START`/`FALLEN`) for rare exceptional units
- relic logs (`APPEAR`/`ACQUIRED`/`LOST`) for rare artifact stories
- bounty logs (`START`/`CLEARED`/`EXPIRED`) for marked hunt stories
- notability logs (`Renown Rising`/`Notoriety Rising`) for emerging known figures
- doctrine logs (`Doctrine assigned`) for proto-faction identity emergence
- project logs (`Project START` / `Project END` / `Project INTERRUPTED`) for temporary faction objectives
- vendetta logs (`Vendetta START` / `Vendetta END` / `Vendetta RESOLVED` / `Vendetta EXPIRED`) for conflict memory
- legacy logs (`Legacy Triggered` / `Successor Chosen` / `Legacy Faded`) for post-fall continuity
- memorial/scar logs (`Memorial/Scar BORN` / `Memorial/Scar FADED`) for post-fall local traces
- neutral gate logs (`OPEN`/`CLOSED`/`BREACH`) for third-pressure spikes
- gate response logs (`Gate Response START` / `SUCCESS` / `INTERRUPTED` / `END`) for bounded faction reaction around gate
- crisis logs (`Crisis START` / `Crisis RESOLVED` / `Crisis EXPIRED` / `Crisis END`) for temporary proto-faction instability
- recovery logs (`Recovery START` / `Recovery INTERRUPTED` / `Recovery END`) for temporary post-shock rebound windows
- destiny logs (`Destiny START` / `Destiny FULFILLED` / `Destiny INTERRUPTED` / `Destiny END`) for bounded heroic convergence moments
- convergence logs (`Convergence START` / `Convergence INTERRUPTED` / `Convergence END`) for short local crossroads moments
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
- [test_game3d_bounties_behavior.py](tests/test_game3d_bounties_behavior.py) (bounty contracts: target selection priority, cooldown/cap gates, bounded clear/expire flow)
- [test_game3d_renown_behavior.py](tests/test_game3d_renown_behavior.py) (renown/notoriety contracts: bounded gain, threshold tiers, light behavior bias, dissipation)
- [test_game3d_neutral_gate_behavior.py](tests/test_game3d_neutral_gate_behavior.py) (neutral gate contracts: bounded open/close cycle, single breach pulse, light AI pressure hooks)
- [test_game3d_doctrines_behavior.py](tests/test_game3d_doctrines_behavior.py) (doctrine contracts: bounded assignment, lightweight behavior deltas, cleanup on allegiance loss)
- [test_game3d_faction_projects_behavior.py](tests/test_game3d_faction_projects_behavior.py) (faction project contracts: bounded launch, single active project, clean end/interruption, lightweight effect hooks)
- [test_game3d_vendetta_behavior.py](tests/test_game3d_vendetta_behavior.py) (vendetta contracts: bounded creation, one active vendetta per allegiance, clean resolved/expired lifecycle, lightweight raid+bounty bias)
- [test_game3d_legacy_behavior.py](tests/test_game3d_legacy_behavior.py) (legacy contracts: notable trigger gating, bounded successor choice, lightweight transfer/inheritance effects)
- [test_game3d_memorials_behavior.py](tests/test_game3d_memorials_behavior.py) (memorial/scar contracts: notable trigger gating, bounded spawn/fade/cap lifecycle, lightweight local renown/notoriety effects)
- [test_game3d_gate_responses_behavior.py](tests/test_game3d_gate_responses_behavior.py) (rift response contracts: gate-open gating, bounded start/end lifecycle, lightweight gate duration/breach effects)
- [test_game3d_allegiance_crisis_behavior.py](tests/test_game3d_allegiance_crisis_behavior.py) (allegiance crisis contracts: bounded triggers, one-active-per-allegiance, clean resolve/expire lifecycle, lightweight rally/raid bias)
- [test_game3d_recovery_behavior.py](tests/test_game3d_recovery_behavior.py) (recovery pulse contracts: bounded trigger/uniqueness, clean end/interruption, lightweight rally/defense uplift)
- [test_game3d_destiny_behavior.py](tests/test_game3d_destiny_behavior.py) (destiny contracts: notable trigger gating, one-active-per-actor uniqueness, clean fulfilled/interrupted/timeout lifecycle, light guidance bias)
- [test_game3d_convergence_behavior.py](tests/test_game3d_convergence_behavior.py) (convergence contracts: bounded trigger rarity, no-start on insufficient local signals, clean end/interruption lifecycle, light local effects)

Run targeted tests:
```bash
py -m unittest tests.test_game3d_scaffold -v
py -m unittest tests.test_game3d_behavioral_logic -v
py -m unittest tests.test_game3d_progression_behavior -v
py -m unittest tests.test_game3d_world_events_behavior -v
py -m unittest tests.test_game3d_special_arrivals_behavior -v
py -m unittest tests.test_game3d_relics_behavior -v
py -m unittest tests.test_game3d_bounties_behavior -v
py -m unittest tests.test_game3d_renown_behavior -v
py -m unittest tests.test_game3d_neutral_gate_behavior -v
py -m unittest tests.test_game3d_doctrines_behavior -v
py -m unittest tests.test_game3d_faction_projects_behavior -v
py -m unittest tests.test_game3d_vendetta_behavior -v
py -m unittest tests.test_game3d_legacy_behavior -v
py -m unittest tests.test_game3d_memorials_behavior -v
py -m unittest tests.test_game3d_gate_responses_behavior -v
py -m unittest tests.test_game3d_allegiance_crisis_behavior -v
py -m unittest tests.test_game3d_recovery_behavior -v
py -m unittest tests.test_game3d_destiny_behavior -v
py -m unittest tests.test_game3d_convergence_behavior -v
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
- Add rare bounty/marked-target MVP with bounded hunt pressure, notable target selection, and lightweight clear reward
- Add lightweight renown/notoriety MVP with bounded per-actor fame/threat, threshold logs, and small AI behavior bias
- Add neutral `rift_gate` POI MVP with rare autonomous open/close cycle, single breach pulse, and lightweight local pressure
- Add lightweight allegiance doctrines/ethos MVP with bounded identity bias (`warlike`/`steadfast`/`arcane`) and runtime observability
- Add lightweight faction projects MVP (`fortify`/`warband_muster`/`ritual_focus`) with one-active-project cap, cooldown, and bounded temporary behavior bias
- Add lightweight vendetta/grudge MVP with one-active-target cap, bounded duration/cooldown, and small raid+bounty bias
- Add lightweight succession/legacy MVP with rare notable-fall triggers, bounded successor inheritance, and runtime continuity observability
- Add lightweight memorial/scar MVP with notable-fall local traces, bounded duration/cap, and small local renown/notoriety pulses
- Add lightweight `rift_gate` response MVP (`gate_seal` / `gate_exploit`) with one-active-per-faction cap, cooldown, and bounded gate/breach effects
- Add lightweight allegiance crisis MVP with one-active-per-allegiance cap, cooldown, bounded rally/raid penalties, and clean resolve/expire lifecycle
- Add lightweight recovery pulse MVP with one-active-per-allegiance cap, cooldown, bounded rally/defense uplift, and clean interruption on renewed shocks
- Add lightweight destiny pull MVP (`rift_call` / `relic_call` / `vendetta_call`) with one-active-per-actor cap, short duration/cooldown, clean fulfilled/interrupted lifecycle, and bounded guidance bias
- Add lightweight crossroads/convergence events MVP (rare local overlap near open `rift_gate`) with one-active cap, short duration/cooldown, clean interrupted/end lifecycle, and bounded local pull/notability pulses

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
- Tune bounty rarity/weight/reward values to keep hunts memorable without overriding baseline raid/rally behavior
- Tune renown/notoriety gain/decay thresholds so notable figures stay readable without persistent global snowball
- Tune neutral gate cadence/open duration and breach strength to keep third-pressure stories visible but bounded
- Tune doctrine assignment heuristics and small bias deltas so group identity stays readable without overriding baseline simulation
- Tune faction project cadence/duration/modifier strength so temporary objectives remain visible without overriding baseline raid/rally dynamics
- Tune vendetta trigger rates/duration/bias so conflict memory stays readable without creating permanent hostility loops
- Tune legacy trigger rarity/successor duration/transfer values so continuity stories stay readable without creating new snowball loops
- Tune memorial/scar duration/cap/pulse values so post-fall traces stay visible and local without introducing snowball
- Tune gate response trigger chance/cooldown/duration and gate duration deltas so reactions stay visible without destabilizing gate cadence
- Tune crisis trigger chance/cooldown/duration and rally/raid penalty strength so instability stays readable without suppressing normal faction loops
- Tune recovery pulse trigger chance/cooldown/duration and uplift strength so rebounds stay readable without creating new snowball loops
- Tune destiny trigger rarity/duration/cooldown and pull weights so heroic convergence stays readable without overriding baseline raid/rally/gate behavior
- Tune convergence trigger rarity/cooldown/duration and local pulse/pull weights so crossroads moments stay visible without overriding baseline destiny/raid/gate flows

### Later
- Replace placeholder meshes/FX with stylized fantasy assets
- Add player sandbox interventions (spawn, buff/debuff, world events)
- Add richer world simulation layers (factions, settlements, quests)

## Scope guard
- No global refactor of the legacy Python simulator during 3D MVP buildout.
- No heavy ML/complex systems before the gameplay core is robust and playable.
- Keep the 3D prototype modular, observable, and iteration-friendly.
