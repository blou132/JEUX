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
- Mode multi-runs optionnel pour comparer automatiquement plusieurs seeds.
- Export optionnel des syntheses en JSON ou CSV.
- Outil CLI d'analyse des exports (JSON prioritaire, CSV support simple).
- Mode batch experimental optionnel pour comparer plusieurs valeurs d'un parametre.
- Synthese comparative automatique en batch (plus stable, meilleure generation, meilleure population, plus faible extinction).
- Historique leger des campagnes batch (archivage multi-experiences + lecture dediee).
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
- `debug_tools/`: calcul d'indicateurs, syntheses, export, analyse d'exports et historique batch.
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

### Mode multi-runs (comparaison seeds)
- Lance automatiquement N runs avec seeds deterministes.
- Reutilise la synthese finale de chaque run.
- Produit un resume agrege: taux d'extinction, generation max moyenne, population finale moyenne, traits moyens finaux, dominant final le plus frequent.
- Systeme purement observatoire (aucune mecanique gameplay ajoutee).

### Export optionnel (JSON / CSV)
- Export du resume final d'un run simple.
- Export du resume multi-runs avec agregats + details par run.
- Export du resume batch experimental (agregats par valeur + details de runs).
- Export de la synthese comparative batch (`comparative_summary`).
- Formats disponibles: `json` (structure complete) et `csv` (aplati lisible).
- Systeme purement observatoire (aucune mecanique gameplay ajoutee).

### Analyse d'exports (CLI)
- Lit un export existant (JSON obligatoire, CSV support simple).
- Affiche un resume lisible sans relancer la simulation.
- En multi-runs: runs, seeds, extinctions, generation max moyenne, population finale moyenne, traits finaux moyens.
- En run simple: seed, extinction, generation max, population finale et synthese finale.
- En batch: parametre teste, valeurs, runs par valeur, resumes agreges par valeur, et synthese comparative automatique.

### Mode batch experimental
- Fait varier un parametre numerique existant sur une liste de valeurs.
- Execute plusieurs runs par valeur (deterministes via seed + seed_step).
- Produit une synthese par valeur:
  - nombre de runs
  - taux d'extinction
  - generation max moyenne
  - population finale moyenne
  - traits finaux moyens (via resume multi-runs)
- Produit aussi une synthese comparative automatique:
  - plus stable (regle transparente: extinction_rate min, puis population moyenne max, puis generation moyenne max)
  - meilleure generation max moyenne
  - meilleure population finale moyenne
  - plus faible taux d'extinction
  - gestion explicite des egalites
- Aucun changement gameplay (mode purement observatoire).

### Historique batch (archive d'experiences)
- Possibilite d'enregistrer plusieurs campagnes batch dans un fichier JSON d'historique.
- Chaque entree contient au minimum:
  - identifiant (`id`)
  - date UTC d'enregistrement
  - parametre et valeurs testees
  - runs par valeur + seed de base
  - synthese comparative batch
- Lecture et resume rapide via un outil CLI dedie (`analyze_batch_history.py`).
- Systeme purement observatoire (aucune mecanique gameplay ajoutee).

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

Exemple multi-runs (comparaison de seeds):
```powershell
py main.py --runs 5 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple batch experimental:
```powershell
py main.py --batch-param energy_drain_rate --batch-values 1.0,1.2,1.4 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple batch + archivage historique:
```powershell
py main.py --batch-param energy_drain_rate --batch-values 1.0,1.2,1.4 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20 --batch-history-path outputs/batch_history.json --batch-id exp_001
```

Exemple export JSON (run simple):
```powershell
py main.py --seed 42 --steps 120 --log-interval 20 --export-path outputs/run_42.json --export-format json
```

Exemple export CSV (multi-runs):
```powershell
py main.py --runs 5 --seed 42 --seed-step 1 --steps 120 --log-interval 20 --export-path outputs/multi_42.csv --export-format csv
```

Exemple export JSON (batch):
```powershell
py main.py --batch-param energy_drain_rate --batch-values 1.0,1.2,1.4 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20 --export-path outputs/batch_energy_drain.json --export-format json
```

Parametres CLI principaux:
- `--steps`, `--dt`, `--log-interval`, `--seed`
- `--runs`, `--seed-step`
- `--batch-param`, `--batch-values`, `--batch-runs`
- `--batch-history-path`, `--batch-id`
- `--export-path`, `--export-format`
- `--map-width`, `--map-height`
- `--creatures`, `--initial-food`, `--min-food`
- `--energy-drain-rate`, `--movement-speed`, `--eat-rate`, `--hunger-threshold`
- `--reproduction-threshold`, `--reproduction-cost`, `--reproduction-distance`, `--reproduction-min-age`
- `--mutation-variation`

## Outil d'analyse d'exports
Commande de base:
```powershell
py analyze_export.py <chemin_export>
```

Exemple analyse JSON multi-runs:
```powershell
py analyze_export.py outputs/multi_42.json
```

Exemple analyse JSON batch:
```powershell
py analyze_export.py outputs/batch_energy_drain.json
```

Exemple analyse CSV en forcant le format:
```powershell
py analyze_export.py outputs/multi_42.csv --format csv
```

Le script affiche un resume texte exploitable sans dependre des logs complets du run.

## Outil d'analyse de l'historique batch
Commande de base:
```powershell
py analyze_batch_history.py outputs/batch_history.json
```

Limiter le nombre d'entrees affichees:
```powershell
py analyze_batch_history.py outputs/batch_history.json --max 10
```

Ce script permet de relire rapidement plusieurs campagnes batch archivees.

## Exemple de sortie batch comparative
```text
--- Batch Comparative Summary ---
batch_comparatif:
plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
meilleure_gen_max_moy: energy_drain_rate=1.0 (gen_max_moy=2.50)
meilleure_pop_finale_moy: energy_drain_rate=1.0 (pop_finale_moy=42.50)
plus_faible_taux_extinction: egalite[energy_drain_rate=1.0,1.5] (taux_ext=0.00)
```

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
py -m unittest tests.test_multi_run_mode
py -m unittest tests.test_export_results
py -m unittest tests.test_export_analysis
py -m unittest tests.test_batch_experiment_mode
py -m unittest tests.test_batch_comparative_summary
py -m unittest tests.test_batch_history
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

En mode multi-runs:
- bloc `--- Multi-Run Summary ---` avec: nombre de runs, seeds, taux d'extinction, generation max moyenne, population finale moyenne, traits moyens finaux, dominant final le plus frequent.

En mode batch:
- bloc `=== Batch Experimental Mode ===` puis un resume par valeur testee.
- bloc `--- Batch Summary ---` avec agregats comparables entre valeurs.
- bloc `--- Batch Comparative Summary ---` avec interpretation automatique des meilleures valeurs.

En mode historique batch:
- ligne `batch_history: <chemin> id=<batch_id>` quand une campagne est archivee.

En mode export:
- ligne `export: <chemin> (<format>)` en fin d'execution.
- le contenu exporte reprend les memes syntheses que la console (run simple, multi-runs, batch).

Avec les outils d'analyse:
- `py analyze_export.py <fichier>` affiche une synthese concise basee sur l'export.
- `py analyze_batch_history.py <fichier_historique>` affiche un resume des campagnes batch archivees.

Lecture rapide conseillee:
1. verifier `alive` + `total_births/total_deaths` pour la dynamique globale,
2. verifier `pression_nourriture` + `zones_nourriture` pour la contrainte environnementale,
3. verifier `proto_groupes` + `proto_tendance` + `proto_zones_creatures` pour les tendances evolutives locales,
4. verifier `Run Summary` pour comparer rapidement plusieurs seeds,
5. en mode multi-runs, verifier `Multi-Run Summary` pour comparer plusieurs seeds,
6. en mode batch, comparer les lignes du `Batch Summary` puis valider `Batch Comparative Summary`,
7. en mode historique, suivre les campagnes via `analyze_batch_history.py`,
8. si export actif, utiliser le fichier JSON/CSV puis `analyze_export.py` pour exploitation hors console.

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
- Mode multi-runs optionnel avec resume agrege compare-seeds.
- Export optionnel JSON/CSV des syntheses run et multi-runs.
- Outil CLI d'analyse des exports pour resume hors console.
- Mode batch experimental pour comparer l'effet de valeurs de parametres existants.
- Interpretation automatique legere des resultats batch (comparative summary).
- Historique batch leger (archivage multi-campagnes + outil de lecture).

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
