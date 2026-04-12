# Evolution MVP (Python)

## Presentation rapide
Ce projet est un simulateur evolutif inspire de Spore, centre sur une evolution emergente simple, lisible et testable.
Le scope actuel est un MVP enrichi: creatures autonomes, survie, reproduction, mutation, menace/fuite, traits comportementaux heritaires, proto-groupes et pression ecologique legere sur la nourriture.

## Objectif du simulateur
Observer comment des regles minimales (faim, energie, nourriture, fuite, reproduction, mutation) produisent des dynamiques de population et des tendances de traits sur plusieurs generations.

## Etat actuel du projet
- Boucle de simulation stable en ticks.
- Carte simple 2D + nourriture avec respawn.
- Systeme faim / energie / mort operationnel.
- Decision IA MVP (fuir, chercher nourriture, se deplacer vers cible, reproduire, errer).
- Reproduction simple avec heredite + mutation legere.
- Traits comportementaux heritaires (prudence, dominance, repro_drive).
- Proto-groupes (regroupements approximatifs par traits).
- Pression ecologique legere: distribution spatiale heterogene de nourriture (zones plus riches/pauvres).
- Observation proto-groupes x fertilite de zone (repartition et dominants par zone).
- Observation temporelle des proto-groupes (stable / en_hausse / en_baisse / nouveau entre logs).
- Synthese finale de run orientee comparaison de seeds.
- Debug texte lisible avec indicateurs causaux.
- Suite de tests `unittest` couvrant les mecanismes MVP.

## Architecture (modules)
- `simulation/`: boucle de tick, application des intents, naissances/deces.
- `ai/`: logique de decision (faim, fuite, reproduction, errance).
- `genetics/`: heredite et mutation des traits.
- `creatures/`: entites creature + traits + usine de population initiale.
- `world/`: carte, ressources nourriture, fertilite spatiale.
- `player/`: configuration de run.
- `ui/`: formatage des logs texte.
- `debug_tools/`: calcul d'indicateurs et distributions.
- `save/`: reserve pour plus tard (non active dans le MVP courant).

## Fonctionnalites validees

### Survie: faim / energie / mort
- L'energie diminue avec le temps.
- Une creature affamee cherche de la nourriture.
- Energie a 0 => mort.

### Reproduction + mutation
- Reproduction simple quand conditions minimales sont remplies (energie, distance, age).
- Enfant herite de traits parentaux avec variation aleatoire legere.
- Progression de generations observable dans les stats.

### Menace / fuite
- Detection de menace proche selon un critere de puissance relatif.
- Priorite de fuite dans la decision.
- Mouvement de fuite a l'oppose de la menace.
- Compteurs de fuites visibles dans le debug.

### Traits comportementaux heritaires
- Traits utilises dans la decision: `prudence`, `dominance`, `repro_drive`.
- Ces traits influencent legerement les priorites d'action.
- Heredite + mutation appliquees sur ces traits.

### Proto-groupes
- Regroupement approximatif de sous-populations selon plusieurs traits.
- Affichage du nombre de groupes, groupe dominant, top groupes et moyennes de traits.

### Fertilite spatiale (pression ecologique legere)
- La carte contient des zones de fertilite differentes (deterministes).
- Le spawn/respawn de nourriture est influence par la fertilite (zones riches/pauvres).
- Indicateurs de zones nourriture exposes dans le debug.

### Observation proto-groupes x fertilite
- Repartition des creatures par zones `rich` / `neutral` / `poor`.
- Proto-groupe dominant observe dans chaque type de zone.
- Systeme purement observatoire (aucune nouvelle regle gameplay ajoutee).

### Observation temporelle des proto-groupes
- Comparaison legere des proto-groupes dominants entre deux logs consecutifs.
- Etiquettes simples: `stable`, `en_hausse`, `en_baisse`, `nouveau`.
- Suivi purement observatoire (aucune modification de decision gameplay).

### Synthese finale de run
- Groupe dominant final + part finale.
- Groupe le plus stable observe sur le run.
- Groupe le plus souvent en hausse observe sur le run.
- Repartition finale par zones de fertilite.
- Rappel des moyennes de traits principales.
- Resume lisible pour comparer rapidement plusieurs seeds.

## Lancer la simulation
Prerequis:
- Python 3.x
- Aucune dependance externe (stdlib uniquement)

Commandes Windows (PowerShell):
```powershell
py main.py
```

Exemple utile (run court, seed fixe):
```powershell
py main.py --steps 120 --log-interval 20 --seed 42
```

Parametres CLI principaux:
- `--steps`, `--dt`, `--log-interval`, `--seed`
- `--map-width`, `--map-height`
- `--creatures`, `--initial-food`, `--min-food`
- `--energy-drain-rate`, `--movement-speed`, `--eat-rate`, `--hunger-threshold`
- `--reproduction-threshold`, `--reproduction-cost`, `--reproduction-distance`, `--reproduction-min-age`
- `--mutation-variation`

## Lancer les tests
Tous les tests:
```powershell
py -m unittest discover -s tests -p "test_*.py"
```

Exemples cibles:
```powershell
py -m unittest tests.test_hunger_system
py -m unittest tests.test_flee_behavior
py -m unittest tests.test_food_distribution_pressure
py -m unittest tests.test_proto_group_ecology_observation
py -m unittest tests.test_proto_group_temporal_observation
py -m unittest tests.test_run_final_summary
```

## Lire les logs debug (indicateurs utiles)
Chaque bloc de log periodique contient:
- ligne principale: `population`, `vivants/morts`, `nourriture`, `energie_moy`, `age_moy`, `gen_moy`, naissances/deces, moyennes de traits.
- `generations:` distribution par generation (`g0`, `g1`, ...).
- `proto_groupes:` nombre de groupes, part du dominant, top groupes et traits moyens.
- `proto_tendance:` tendance temporelle des proto-groupes (`stable`, `hausse`, `baisse`, `nouveau`) entre logs.
- `proto_zones_creatures:` repartition des creatures par zones fertiles et proto-groupe dominant par zone.
- `causes_deces:` faim / epuisement / autre (tick et total).
- `dynamique_*:` croissance/declin/stagnation, pression nourriture, etat energie.
- `zones_nourriture:` `riches`, `neutres`, `pauvres`, `fert_moy`.

En fin de run:
- bloc `--- Run Summary ---` avec dominant final, stabilite/hausse observees, zones finales et traits moyens.

Lecture rapide conseillee:
1. verifier `alive` + `total_births/total_deaths` pour la dynamique globale,
2. verifier `pression_nourriture` + `zones_nourriture` pour la contrainte environnementale,
3. verifier `proto_groupes` + `proto_tendance` + `proto_zones_creatures` pour les tendances evolutives locales,
4. verifier `Run Summary` pour comparer rapidement plusieurs seeds.

## Roadmap actuelle

### Termine
- MVP jouable: boucle, faim/energie/mort, nourriture, deplacement, reproduction, mutation.
- Debug/stats lisibles (population, generations, causes de deces, traits).
- Menace/fuite minimale testee.
- Traits comportementaux heritaires testes.
- Proto-groupes visibles en debug.
- Pression ecologique legere sur la nourriture (heterogene, stable, testable).
- Observation proto-groupes x fertilite (repartition + dominants par zone).
- Observation temporelle des proto-groupes (stable/hausse/baisse/nouveau).
- Synthese finale de run orientee comparaison de seeds.

### En cours / prochain ajout
- Consolidation continue de l'equilibrage (sans nouvelles grosses mecaniques).
- Validation comportementale multi-seeds pour confirmer robustesse des tendances.
- Renforcement cible des tests d'invariants long run (sans sur-architecture).

### Plus tard
- Systeme espece/lignee plus explicite (toujours leger).
- Environnement plus riche (sans basculer vers des biomes complexes trop tot).
- Eventuelle couche UI plus visuelle (apres stabilisation complete du core).
- Save/load quand le gameplay coeur sera suffisamment fige.

## Notes de scope
- Pas de combat complexe.
- Pas de systeme de degats detaille.
- Pas de machine learning.
- Pas de refactor global dans la phase actuelle.
