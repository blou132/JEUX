# Pivot Sandbox Fantasy 3D

## Etat du projet
Ce depot est maintenant organise en 4 zones claires :
- `game3d/` : prototype Godot 4 actif (jeu principal).
- `legacy_python/` : ancien simulateur Python conserve comme laboratoire/frozen.
- `shared_data/` : donnees JSON intermediaires partagees.
- `tools/` : scripts utilitaires (synchronisation/analyse).

Flux de donnees cible :
- Godot ne lit que `game3d/data/*.json`.
- Les donnees sources sont maintenues dans `shared_data/`.
- La copie vers Godot passe par `tools/sync_shared_to_godot.py` (pas d'import Python runtime dans Godot).
- Le chargement runtime Godot passe par `game3d/scripts/data/DataLoader.gd`.
- Les world events runtime peuvent etre pilotes par `game3d/data/events.json` (`mana_surge`, `monster_frenzy`, `sanctuary_calm`).
- Les templates de factions/allegiances peuvent etre pilotes par `game3d/data/factions.json` (`human_core`, `monster_core`).
- Les templates de doctrines peuvent etre pilotes par `game3d/data/doctrines.json` (`warlike`, `steadfast`, `arcane`).
- Les templates de relics peuvent etre pilotes par `game3d/data/relics.json` (`arcane_sigil`, `oath_standard`).
- Les templates de lieux/POI peuvent etre pilotes par `game3d/data/locations.json` (`camp`, `ruins`, `rift_gate`).

La priorite est le gameplay 3D observable, pas l'ajout de micro-traits dans l'ancien simulateur.

## Cible actuelle (coeur gameplay 3D)
La direction active est une boucle sandbox minimale mais jouable :
- aventuriers autonomes (humains)
- differenciation des roles humains (`fighter` / `mage` / `scout`)
- monstres autonomes
- progression autonome legere (`L1 -> L3`)
- couche champions emergente (promotions rares `hero/elite`)
- groupes de rally menes par champions (`rally/warband` MVP)
- points d'interet simples (POI) : camp + ruins + `rift_gate` neutre
- influence territoriale des POI (activation apres domination stable)
- structures persistantes des POI (`camp -> human_outpost`, `ruins -> monster_lair`)
- cycles de pression de raid entre structures (`outpost <-> lair`)
- couche allegiances/proto-factions legere (ancree aux structures)
- couche doctrines/ethos legere (biais comportementaux bornes)
- couche projets d'allegeance legere (impulsions d'objectifs temporaires)
- couche vendetta/grudge legere (memoire de conflit bornee)
- couche succession/legacy legere (continuite bornee apres chutes notables)
- couche memorial/scar legere (traces locales post-chute de courte duree)
- couche evenements mondiaux legere (une perturbation temporaire active, alias `world event`)
- couche special arrivals legere (arrivees rares invoquees)
- couche relics legere (artefacts rares portes)
- couche prime/cible marquee legere (pression de chasse notable et bornee)
- couche renown/notoriety legere (figures connues sous pression sociale bornee)
- couche reponses a `rift_gate` legere (reactions bornees autour d'une porte ouverte)
- couche crise d'allegeance legere (instabilite temporaire bornee)
- couche recovery pulse legere (rebond bornee apres choc)
- couche mending/reconciliation legere (fenetres locales de desescalade)
- couche oaths/sworn moments legere (engagements notables temporaires)
- couche echoes/aftershocks legere (resonances courtes apres evenements majeurs)
- couche pilgrimages/expeditions legere (intentions notables de voyage)
- couche watch/alert pulse legere (vigilance locale bornee)
- couche destiny pulls legere (aspirations heroiques temporaires)
- couche convergence/crossroads legere (chevauchements de signaux locaux)
- couche marked zones legere (`sanctified_zone` / `corrupted_zone`)
- couche sanctuaries/bastions legere (`sanctuary_site` / `dark_bastion`)
- couche taboos/cursed warnings legere (`forbidden_site` / `cursed_warning`)
- couche rivalry/duel legere (oppositions notables bornees)
- couche patronage/bond legere (attaches locales temporaires)
- couche splinter/breakaway legere (fractures locales bornees)
- IA FSM simple : `wander -> detect -> chase -> attack -> flee`
- combat de melee deterministe (portee + cooldown + degats)
- trois sorts simples : projectile bolt + nova courte portee + slow de controle
- deux archetypes monstres en plus : brute + ranged
- regulation de population sandbox (respawn minimal)
- observabilite runtime (debug HUD + event log)

## Ce qui est implemente maintenant dans `game3d/`
- Initialisation du projet Godot : [project.godot](game3d/project.godot)
- Scene principale : [MainSandbox.tscn](game3d/scenes/MainSandbox.tscn)
- Boucle coeur et orchestration : [GameLoop.gd](game3d/scripts/core/GameLoop.gd)
- Monde plat + points d'apparition + aides de grille de navigation : [WorldManager.gd](game3d/scripts/world/WorldManager.gd)
- Entites :
  - [Actor.gd](game3d/scripts/entities/Actor.gd)
  - [HumanAgent.gd](game3d/scripts/entities/HumanAgent.gd)
  - [MonsterAgent.gd](game3d/scripts/entities/MonsterAgent.gd)
  - [BruteMonster.gd](game3d/scripts/entities/BruteMonster.gd)
  - [RangedMonster.gd](game3d/scripts/entities/RangedMonster.gd)
- Couche de decision IA : [AgentAI.gd](game3d/scripts/ai/AgentAI.gd)
- Systeme de combat : [CombatSystem.gd](game3d/scripts/combat/CombatSystem.gd)
- Systeme de magie : [MagicSystem.gd](game3d/scripts/magic/MagicSystem.gd)
- Regulation sandbox : [SandboxSystems.gd](game3d/scripts/sandbox/SandboxSystems.gd)

### Couches gameplay MVP en place
- Influence POI : bonus local leger humain/monstre apres domination stable, effets bornes dans le rayon du POI.
- Structures POI : `camp` peut devenir `human_outpost`, `ruins` peut devenir `monster_lair`, persistance runtime et perte si domination casse.
- Raids : cycle source/cible borne, duree finie, cooldown simple, `Raid START/END` et marquage HUD.
- Allegiances : affiliation autour des structures, perte propre sur disparition d'ancre, biais de cohesion/rally/defense.
- Doctrines : `warlike` / `steadfast` / `arcane`, assignation locale sure, suppression propre sur perte d'ancre.
- Projets de faction : `fortify` / `warband_muster` / `ritual_focus`, un projet actif max, effets legers et bornes.
- Vendettas : une cible active max par allegiance, duree/cooldown bornes, fin `RESOLVED` ou `EXPIRED`.
- Succession/legacy : declenchement notable rare, transfer leger de renown/notoriety, heritage de relic possible.
- Memorial/scar : traces locales courtes apres chute notable, cap global petit, fade propre.
- Evenements mondiaux : un evenement global actif max (`mana_surge`, `monster_frenzy`, `sanctuary_calm`).
- Special arrivals : `summoned_hero` et `calamity_invader`, declenchements rares et bornes.
- Relics : `arcane_sigil` / `oath_standard`, un relic max par acteur, reset a la mort du porteur.
- Bounties : cible marquee rare avec `max 1 active`, orientation de chasse legere et recompense XP bornee.
- Renown/notoriety : scores `0..100`, gains notables, dissipation passive, biais IA leger.
- `rift_gate` neutre : cycle `dormant/open` borne, breche simple, pression locale legere.
- Reponses a `rift_gate` : `gate_seal` / `gate_exploit`, une reponse active max par faction, cooldown borne.
- Crise d'allegeance : etat temporaire borne, declenchements sur chocs, sortie `RESOLVED` ou `EXPIRED`.
- Recovery pulse : rebond temporaire borne apres stabilisation, interruption propre si nouveau choc.
- Mending : fenetre locale de desescalade entre allegiances opposees, interruption `Mending BROKEN` possible.
- Oaths : `oath_of_guarding` / `oath_of_vengeance` / `oath_of_seeking`, rarete/caps/cooldowns bornes.
- Echoes : `heroic_echo` / `dark_aftershock`, courte resonance locale, cap global petit.
- Expeditions : leaders notables, destinations bornees (`rift_gate`, zone marquee, memorial/scar), fin propre.
- Pulses d'alerte : vigilance locale bornee par allegiance (`Alert START/END`) avec bonus defensif leger et baisse offensive legere.
- Destiny pulls : `rift_call` / `relic_call` / `vendetta_call`, une destinee active max par acteur.
- Convergence : evenements locaux rares autour d'un `rift_gate` ouvert, effets legers et courte duree.
- Marked zones : `sanctified_zone` / `corrupted_zone`, cap petit, duree courte, fade propre.
- Sanctuaries/Bastions : `sanctuary_site` / `dark_bastion`, cap global petit, duree bornee, fade propre.
- Taboos : `forbidden_site` / `cursed_warning`, zones redoutees temporaires, cap global petit, fade propre.
- Rivalry/duel : rivalites rares entre figures notables, duel optionnel court, cycle propre.
- Bonds : liens temporaires notable->groupe, cohesion locale legere, rupture propre.
- Splinters : fractures locales temporaires dans une allegiance, pas de vraie nouvelle faction persistante.

### Observabilite
- Logs dedies pour toutes les couches majeures (`START/END` + transitions de statut).
- Logs dedies supplementaires pour sanctuaries/bastions (`Sanctuary RISE`, `Bastion RISE`, `Sanctuary/Bastion FADE`).
- Logs dedies supplementaires pour taboos (`Taboo RISE`, `Taboo FADE`).
- HUD debug avec compteurs actifs, compteurs historiques et labels courts de contexte.
- Tags legers runtime sur POI/allegiances/acteurs selon couche active.

Alias techniques conserves pour compatibilite runtime/tests : world event, mana surge, monster frenzy, sanctuary calm, special arrival, summoned hero, calamity invader, relic, arcane sigil, oath standard, bounty, marked target, hunt, renown, notoriety, rift gate, dungeon/gate, gate response, gate_seal, gate_exploit, allegiance crisis, recovery pulse, doctrine, ethos, project, fortify, warband, ritual, vendetta, grudge, legacy, succession, successor, memorial, scar, destiny, convergence, sanctified, corrupted, zone faded, sanctuary_site, dark_bastion, sanctuary rise, bastion rise, sanctuary/bastion fade, taboo, forbidden_site, cursed_warning, taboo rise, taboo fade, rivalry, duel, bond, patron, splinter, breakaway, mending, reconciliation, oath, sworn, echo, aftershock, expedition, pilgrimage, alert pulse, alert start, alert end, watch.

## Lancer le prototype 3D
Prerequis : Godot 4.x installe localement.

1. Ouvrir Godot puis importer `game3d/project.godot`.
2. Lancer le projet (scene principale `MainSandbox.tscn`).

Controles camera (AZERTY) :
- `Z Q S D` : deplacement sur le plan XZ
- `A / E` : bas / haut
- `Shift` : acceleration
- Maintenir clic droit + bouger la souris : orienter la camera

## Ce qu'il faut observer en runtime
Le debug overlay affiche notamment :
- population vivante (humains / monstres)
- repartition des roles humains (`fighter`, `mage`, `scout`)
- compteurs combat/magie/fuite/morts
- etats IA actifs
- etat POI, influence, structures, raids
- compteurs allegiances/doctrines/projets/vendettas
- compteurs legacy/memorials/relics/bounties
- compteurs `rift_gate`, reponses, crises, recovery, mending
- compteurs oaths/echoes/expeditions/alerts/destiny/convergence
- compteurs zones marquees/sanctuaries-bastions/taboos/rivalries/bonds/splinters
- evenementiel recent en logs

Cible de validation MVP :
- cycles repetes de rencontre -> poursuite/attaque/sort -> mort ou fuite -> respawn.

## Statut Legacy Python
Les modules Python existants sont conserves volontairement et ne sont pas etendus dans la direction principale. Ils sont regroupes sous `legacy_python/` :
- `legacy_python/simulation/`
- `legacy_python/ai/`
- `legacy_python/creatures/`
- `legacy_python/genetics/`
- `legacy_python/world/`
- `legacy_python/ui/`
- `legacy_python/debug_tools/`
- `legacy_python/save/`
- `legacy_python/player/`

Vous pouvez encore executer l'ancien simulateur et les scripts d'analyse si necessaire, mais ce n'est plus prioritaire.

## Donnees partagees et sync Godot
- Sources JSON : `shared_data/*.json`
- Cible Godot : `game3d/data/*.json`
- Profils creatures : `shared_data/creatures.json` -> `game3d/data/creatures.json`
- Export/validation profils : `tools/export_creature_profiles.py`
- World events : `shared_data/events.json` -> `game3d/data/events.json`
- Export/validation world events : `tools/export_world_events.py`
- Templates factions/allegiances : `shared_data/factions.json` -> `game3d/data/factions.json`
- Export/validation factions : `tools/export_faction_templates.py`
- Templates doctrines : `shared_data/doctrines.json` -> `game3d/data/doctrines.json`
- Export/validation doctrines : `tools/export_doctrine_templates.py`
- Templates relics : `shared_data/relics.json` -> `game3d/data/relics.json`
- Export/validation relics : `tools/export_relic_templates.py`
- Templates lieux/POI : `shared_data/locations.json` -> `game3d/data/locations.json`
- Export/validation lieux/POI : `tools/export_location_templates.py`
- Script de sync : `tools/sync_shared_to_godot.py`
- Chargeur Godot : `game3d/scripts/data/DataLoader.gd`

Passerelles runtime (ordre de chargement) :
- `creatures.json` : charge par `DataLoader.load_creature_profiles()` puis applique via `SandboxSystems`.
- `events.json` : charge par `DataLoader.load_world_events()` puis utilise pour la rotation des world events.
- `factions.json` : charge par `DataLoader.load_faction_templates()` puis injecte dans `WorldManager` (pools de doctrines + metadata template).
- `doctrines.json` : charge par `DataLoader.load_doctrine_templates()` puis injecte dans `WorldManager` (labels + biais doctrine raid/defense/rally/magic avec fallback).
- `relics.json` : charge par `DataLoader.load_relic_templates()` puis utilise par `GameLoop` (labels, eligibilite d'apparition, modificateurs relics avec fallback).
- `locations.json` : charge par `DataLoader.load_location_templates()` puis injecte dans `WorldManager` (labels/rayons/tags/upgrade target POI avec fallback).

## Doctrine data bridge
- Regeneration/validation :
  - `py tools/export_doctrine_templates.py --path shared_data/doctrines.json`
  - `py tools/export_doctrine_templates.py --path shared_data/doctrines.json --validate-only`
  - `py tools/sync_shared_to_godot.py` (copie vers `game3d/data/doctrines.json`)
- Biais doctrines (legers, sans refonte gameplay) :
  - `raid_bias` : pression offensive appliquee au poids de raid.
  - `defense_bias` : pression defensive appliquee au poids de defense.
  - `rally_bias` : impact sur regroupement rally.
  - `magic_bias` : ajuste les multiplicateurs magie (degats/cout).
  - `project bias` : preference legere sur le choix de projet (`warlike` -> `warband_muster`, `steadfast` -> `fortify`, `arcane` -> `ritual_focus`).
  - `vendetta bias` : delta leger sur la tendance de depart vendetta (warlike +, steadfast -, arcane neutre/leger en contexte magique).
- Runtime et fallback :
  - `GameLoop` charge via `DataLoader` puis injecte dans `WorldManager`.
  - Si `doctrines.json` manque/est invalide/incomplet, fallback historique conserve (`source=fallback`).
  - Le HUD/debug affiche `Doctrines: warlike=X steadfast=Y arcane=Z fallback=N`, doctrine dominante, sources (`json`/`fallback`) et biais moyens actifs.

## Narrative timeline
- La timeline narrative est **observation-only**: elle n'ajoute aucun effet gameplay.
- `GameLoop` conserve un historique compact des evenements majeurs recents (environ 20-30 entrees):
  - doctrines assignees,
  - projets d'allegeance (start/end/interrupted),
  - vendettas (start/resolved/expired),
  - changements d'allegeance/structures,
  - world events, relics, promotions champion, legacy successor, memorial/scar.
- Le HUD/debug expose:
  - `narrative_timeline_labels`,
  - `narrative_timeline_count`,
  - `last_major_event_label`.
- Cette timeline sert a lire les histoires emergentes de la simulation (dominance faction, doctrines dominantes, escalades et ruptures).

Commande :
```bash
py tools/export_creature_profiles.py --path shared_data/creatures.json
py tools/export_world_events.py --path shared_data/events.json
py tools/export_faction_templates.py --path shared_data/factions.json
py tools/export_doctrine_templates.py --path shared_data/doctrines.json
py tools/export_relic_templates.py --path shared_data/relics.json
py tools/export_location_templates.py --path shared_data/locations.json
py tools/sync_shared_to_godot.py
```

Validation seule :
```bash
py tools/export_creature_profiles.py --path shared_data/creatures.json --validate-only
py tools/export_world_events.py --path shared_data/events.json --validate-only
py tools/export_faction_templates.py --path shared_data/factions.json --validate-only
py tools/export_doctrine_templates.py --path shared_data/doctrines.json --validate-only
py tools/export_relic_templates.py --path shared_data/relics.json --validate-only
py tools/export_location_templates.py --path shared_data/locations.json --validate-only
```

## Tests
Verifications de scaffold actuelles pour le pivot 3D :
- [test_game3d_scaffold.py](tests/test_game3d_scaffold.py)
- [test_game3d_behavioral_logic.py](tests/test_game3d_behavioral_logic.py) (contrats comportementaux : IA, POI runtime/influence/structure/raid/allegeance, repartition d'apparition)
- [test_game3d_progression_behavior.py](tests/test_game3d_progression_behavior.py) (contrats progression : seuils, triggers XP, rythme de survie, champs snapshot)
- [test_game3d_world_events_behavior.py](tests/test_game3d_world_events_behavior.py) (contrats evenements mondiaux : cadence de declenchement, fin/reset, modificateurs bornes)
- [test_game3d_special_arrivals_behavior.py](tests/test_game3d_special_arrivals_behavior.py) (contrats arrivees speciales : conditions, verrous cooldown/cap, points d'integration bornes)
- [test_game3d_relics_behavior.py](tests/test_game3d_relics_behavior.py) (contrats relics : apparition bornee, gating porteur, cooldown/cap, reset de perte)
- [test_game3d_bounties_behavior.py](tests/test_game3d_bounties_behavior.py) (contrats bounties : priorite de selection cible, gates cooldown/cap, cycle clear/expire borne)
- [test_game3d_renown_behavior.py](tests/test_game3d_renown_behavior.py) (contrats renown/notoriety : gains bornes, seuils, biais comportemental leger, dissipation)
- [test_game3d_neutral_gate_behavior.py](tests/test_game3d_neutral_gate_behavior.py) (contrats gate neutre : cycle open/close borne, pulse de breche unique, points IA legers)
- [test_game3d_doctrines_behavior.py](tests/test_game3d_doctrines_behavior.py) (contrats doctrines : assignation bornee, deltas comportementaux legers, nettoyage sur perte d'allegeance)
- [test_game3d_faction_projects_behavior.py](tests/test_game3d_faction_projects_behavior.py) (contrats projets : lancement borne, un projet actif, fin/interruption propre, points d'effet legers)
- [test_game3d_vendetta_behavior.py](tests/test_game3d_vendetta_behavior.py) (contrats vendetta : creation bornee, une vendetta active par allegiance, cycle de fin propre)
- [test_game3d_legacy_behavior.py](tests/test_game3d_legacy_behavior.py) (contrats legacy : gating des declencheurs notables, choix de successeur borne, effets de transfert/heritage legers)
- [test_game3d_memorials_behavior.py](tests/test_game3d_memorials_behavior.py) (contrats memorial/scar : gating, cycle apparition/fade/cap borne, effets locaux legers)
- [test_game3d_gate_responses_behavior.py](tests/test_game3d_gate_responses_behavior.py) (contrats reponses gate : verrou gate-open, cycle start/end borne, effets gate/breche legers)
- [test_game3d_allegiance_crisis_behavior.py](tests/test_game3d_allegiance_crisis_behavior.py) (contrats crise : triggers bornes, un actif par allegiance, cycle resolve/expire propre)
- [test_game3d_recovery_behavior.py](tests/test_game3d_recovery_behavior.py) (contrats recovery pulse : declenchement/unicite borne, fin/interruption propre)
- [test_game3d_mending_behavior.py](tests/test_game3d_mending_behavior.py) (contrats mending : declenchement/unicite/cap bornes, cycle end/broken propre)
- [test_game3d_oaths_behavior.py](tests/test_game3d_oaths_behavior.py) (contrats oaths : declenchement notable/unicite/cap bornes, cycle end/fulfilled/broken propre)
- [test_game3d_echoes_behavior.py](tests/test_game3d_echoes_behavior.py) (contrats echoes : declenchement/cap/cooldown bornes, cycle fade/end propre)
- [test_game3d_expeditions_behavior.py](tests/test_game3d_expeditions_behavior.py) (contrats expeditions : declenchement notable/unicite/cap bornes, cycle arrived/interrupted/end propre)
- [test_game3d_alert_pulses_behavior.py](tests/test_game3d_alert_pulses_behavior.py) (contrats alert : declenchement/cap/cooldowns bornes, cycle start/end propre, biais defense/offense leger)
- [test_game3d_destiny_behavior.py](tests/test_game3d_destiny_behavior.py) (contrats destiny : verrou des declencheurs notables, unicite par acteur, cycle fulfilled/interrupted/timeout propre)
- [test_game3d_convergence_behavior.py](tests/test_game3d_convergence_behavior.py) (contrats convergence : rarete bornee, pas de start sans signaux suffisants, cycle end/interruption propre)
- [test_game3d_marked_zones_behavior.py](tests/test_game3d_marked_zones_behavior.py) (contrats marked zones : declenchement/classification/cap bornes, cycle fade propre)
- [test_game3d_sanctuary_bastions_behavior.py](tests/test_game3d_sanctuary_bastions_behavior.py) (contrats sanctuaries/bastions : declenchement/classification/cap/cooldown bornes, cycle fade propre, effets locaux legers)
- [test_game3d_taboos_behavior.py](tests/test_game3d_taboos_behavior.py) (contrats taboos : declenchement/classification/cap/cooldowns bornes, cycle fade propre, avoidance/pression locale legeres)
- [test_game3d_rivalry_behavior.py](tests/test_game3d_rivalry_behavior.py) (contrats rivalry/duel : declenchement/unicite bornes, cycle resolved/expired/end propre)
- [test_game3d_bonds_behavior.py](tests/test_game3d_bonds_behavior.py) (contrats bonds : declenchement/unicite/cap bornes, cycle end/broken propre)
- [test_game3d_splinters_behavior.py](tests/test_game3d_splinters_behavior.py) (contrats splinters : declenchement/unicite/cooldown bornes, cycle resolved/faded/end propre)
- [test_tools_creature_profiles_export.py](tests/test_tools_creature_profiles_export.py) (contrats export/validation des profils creatures JSON)
- [test_tools_world_events_export.py](tests/test_tools_world_events_export.py) (contrats export/validation des world events JSON)
- [test_tools_faction_templates_export.py](tests/test_tools_faction_templates_export.py) (contrats export/validation des templates factions/allegiances JSON)
- [test_tools_doctrine_templates_export.py](tests/test_tools_doctrine_templates_export.py) (contrats export/validation des templates doctrines JSON)
- [test_tools_relic_templates_export.py](tests/test_tools_relic_templates_export.py) (contrats export/validation des templates relics JSON)
- [test_tools_location_templates_export.py](tests/test_tools_location_templates_export.py) (contrats export/validation des templates de lieux/POI JSON)

Executer les tests cibles :
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
py -m unittest tests.test_game3d_mending_behavior -v
py -m unittest tests.test_game3d_oaths_behavior -v
py -m unittest tests.test_game3d_echoes_behavior -v
py -m unittest tests.test_game3d_expeditions_behavior -v
py -m unittest tests.test_game3d_alert_pulses_behavior -v
py -m unittest tests.test_game3d_destiny_behavior -v
py -m unittest tests.test_game3d_convergence_behavior -v
py -m unittest tests.test_game3d_marked_zones_behavior -v
py -m unittest tests.test_game3d_sanctuary_bastions_behavior -v
py -m unittest tests.test_game3d_taboos_behavior -v
py -m unittest tests.test_game3d_rivalry_behavior -v
py -m unittest tests.test_game3d_bonds_behavior -v
py -m unittest tests.test_game3d_splinters_behavior -v
```

Executer la suite complete si necessaire :
```bash
py -m unittest discover -s tests -v
```

## Roadmap (mise a jour)
### Fait
- Ajout du projet Godot 4 en parallele de la base Python existante.
- Construction de la scene sandbox 3D minimale avec camera libre.
- Ajout humains/monstres autonomes + IA FSM + combat melee + magie simple.
- Ajout de la regulation sandbox et de l'observabilite runtime.
- Ajout de toutes les couches MVP decrites ci-dessus, jusqu'a `alert`, `destiny`, `convergence`, `marked zones`, `sanctuaries/bastions`, `taboos`, `rivalry`, `bond` et `splinter`.

### Prochaines etapes
- Ajuster l'equilibrage role/combat a partir de sessions de jeu.
- Ajuster les timings/cooldowns/effets des couches POI, raids et allegiances pour eviter tout snowball.
- Ajuster la cadence des couches rares (evenements, arrivees, relics, bounties, gate, crises, recovery, mending, oaths, echoes, expeditions, alerts, destiny, convergence, zones, sanctuaries/bastions, taboos, rivalry, bonds, splinters).
- Conserver un prototype lisible, borne et observable sans systemes lourds.

### Plus tard
- Remplacer les meshes/FX placeholder par des assets fantasy stylises.
- Ajouter des interventions joueur sandbox (apparition, buff/debuff, evenements mondiaux).
- Ajouter des couches monde plus riches (factions, settlements, quests).

## Garde-fou de scope
- Pas de refactor global du simulateur legacy Python pendant le buildout MVP 3D.
- Pas de ML lourd/systemes complexes avant un coeur gameplay robuste et jouable.
- Garder le prototype 3D modulaire, observable et facile a iterer.
