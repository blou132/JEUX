# Evolution MVP (Python)

## Presentation rapide
Ce projet est un simulateur evolutif inspire de Spore, centre sur une evolution emergente simple, lisible et testable.
Le scope actuel est un MVP enrichi: creatures autonomes, survie, reproduction, mutation, menace/fuite, traits comportementaux heritaires, proto-groupes, pression ecologique legere sur la nourriture, memoire locale courte, influence sociale locale minimale, biais individuels legers sur memoire/social, et variabilite individuelle de perception.

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
- Interpretation batch memoire (pour parametres memoire) avec comparatifs usage/effet.
- Interpretation batch sociale (pour parametres sociaux) avec comparatifs usage/part/effet.
- Interpretation batch des biais individuels (`memory_focus`, `social_sensitivity`) pour les parametres memoire/sociaux.
- Lecture comparative legere memoire vs social dans l'historique batch (effets observes + metriques comportementales).
- Synthese comparative automatique en batch (plus stable, meilleure generation, meilleure population, plus faible extinction).
- Historique leger des campagnes batch (archivage multi-experiences + lecture dediee).
- Memoire locale courte des zones utiles/dangereuses avec influence legere sur le deplacement.
- Indicateurs d'impact memoire (usage, part active, effet moyen distance) visibles en stats/syntheses.
- Influence sociale locale minimale (suivi social vers nourriture + renforcement local de fuite).
- Indicateurs sociaux visibles dans le debug (`social_log`, `social_tick`, part influencee, multiplicateur de fuite tick/moyen).
- Indicateurs d'impact des biais individuels (`memory_focus`, `social_sensitivity`): moyennes, dispersion et biais d'usage memoire/social visibles en stats/syntheses.
- Biais individuels legers (memory_focus, social_sensitivity) qui modulent l'usage memoire/social.
- Variabilite individuelle de perception (`food_perception`, `threat_perception`) heritable, mutante et visible dans stats/synthese/debug.
- Evaluation legere de l'impact perception: moyennes/dispersion + biais d'usage detection/consommation/fuite en stats/syntheses.
- Interpretation batch perception (`perception_batch`) pour comparer usage/dispersion/stabilite des configurations testees.
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

### Biais individuels memoire/social
- Traits legers ajoutes: `memory_focus` (sensibilite a la memoire locale) et `social_sensitivity` (sensibilite aux signaux sociaux proches).
- Effet volontairement limite:
  - `memory_focus` module la distance de rappel/evitement de memoire utile ou dangereuse.
  - `social_sensitivity` module la portee sociale, le suivi social et le boost social de fuite.
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs:
  - moyennes globales: `memoire_trait_moy`, `social_trait_moy`
  - composantes traits: `traits_comp_moy` (inclut `mem` et `soc`).

### Variabilite individuelle de perception
- Traits legers ajoutes: `food_perception` et `threat_perception`.
- Effet volontairement limite:
  - `food_perception` ajuste legerement la portee de detection de nourriture.
  - `threat_perception` ajuste legerement la portee de detection de menace.
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*` via `traits_comp_moy` (`fp`, `tp`) et `traits_disp` (`fp_sigma`, `tp_sigma`)
  - `Run Summary` et `Multi-Run Summary` via `traits_moy` / `traits_finaux_moy` (`fp`, `tp`).

### Evaluation legere de l'impact perception
- Indicateurs exposes en stats/synthese:
  - moyenne et dispersion de `food_perception` et `threat_perception`
  - usage reel detection nourriture (`food_detection_*`) et consommation (`food_consumption_*`)
  - usage reel detection menace/fuite (`threat_detection_*`)
  - biais simples: moyenne des utilisateurs - moyenne population (`food_perception_detection_usage_bias_*`, `food_perception_consumption_usage_bias_*`, `threat_perception_flee_usage_bias_*`)
- Visibilite:
  - `dynamique_*`: `perception_log`, `perception_tick`, `perception_freq_tick`, `perception_bias_tick`
  - `Run Summary` / `Multi-Run Summary`: bloc `traits_impact` / `traits_impact_moy` (inclut `fp_mu`, `tp_mu`, biais perception)

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
- Pour les batchs sur parametres memoire (`food_memory_duration`, `danger_memory_duration`, `food_memory_recall_distance`, `danger_memory_avoid_distance`):
  - plus forte utilisation memoire utile
  - plus forte utilisation memoire dangereuse
  - plus grand effet moyen memoire utile
  - plus grand effet moyen memoire dangereuse
  - signalement explicite si donnees insuffisantes
- Pour les batchs sur parametres sociaux (`social_influence_distance`, `social_follow_strength`, `social_flee_boost_per_neighbor`, `social_flee_boost_max`):
  - plus forte frequence de suivi social
  - plus forte frequence de boost de fuite social
  - plus grande part de creatures influencees
  - plus grand effet moyen du multiplicateur de fuite social
  - signalement explicite si donnees insuffisantes
- Pour les batchs sur parametres memoire/sociaux, la synthese inclut aussi `traits_batch` (si donnees presentes):
  - plus fort biais moyen d'usage memoire (`(bias_food + bias_danger) / 2`)
  - plus fort biais moyen d'usage social (`(bias_suivi + bias_fuite) / 2`)
  - plus forte dispersion utile des biais individuels (`(std_mem + std_soc) / 2`)
  - configuration la plus stable (regle batch standard)
  - signalement explicite des cas ambigus ou insuffisants
- Quand les metriques existent, la synthese inclut aussi `perception_batch`:
  - configuration qui maximise l'usage reel de `food_perception` (proxy: `(bias_detection + bias_consommation) / 2`)
  - configuration qui maximise l'usage reel de `threat_perception` (proxy: `bias_fuite`)
  - configuration avec la plus forte dispersion perception utile (`(std_food_perception + std_threat_perception) / 2`)
  - configuration la plus stable (regle batch standard)
  - signalement explicite des cas ambigus ou insuffisants
- Aucun changement gameplay (mode purement observatoire).

### Memoire locale courte (zones utiles/dangereuses)
- Chaque creature conserve une memoire courte de derniere zone utile (nourriture consommee).
- Chaque creature conserve une memoire courte de derniere zone dangereuse (menace lors d'une fuite).
- Influence legere du comportement: en recherche de nourriture, retour vers zone utile proche; en errance, evitement bref d'une zone dangereuse proche.
- Systeme purement local, sans pathfinding ni apprentissage complexe.
- Indicateurs associes: frequence d'usage memoire utile/dangereuse, part de creatures avec memoire active, effet moyen de rapprochement/eloignement par tick et cumule.


### Influence sociale locale minimale
- Une creature peut suivre legerement un congenere proche qui se deplace vers une zone de nourriture visible.
- Une fuite locale peut etre renforcee si d'autres creatures proches fuient au meme tick.
- Systeme volontairement leger et local (pas de groupe complexe, pas de hierarchie, pas de pathfinding social).
- Indicateurs associes: `social_follow_moves_last_tick`, `social_flee_boosted_last_tick`, `social_influenced_creatures_last_tick`, `social_influenced_share_last_tick`, `avg_social_flee_multiplier_last_tick`, `social_flee_multiplier_avg_total`, plus les blocs `social_log` et `social_tick` dans `dynamique_*`.

### Evaluation legere de l'impact social
- Mesures d'impact exposees en stats/synthese: frequence du suivi social, frequence du boost de fuite social, part de creatures influencees, effet moyen du multiplicateur de fuite social (tick + moyenne run).
- Ces indicateurs sont visibles dans:
  - la ligne `dynamique_*` des logs (`social_log`, `social_tick`, `part_infl`, `mult_fuite`, `mult_fuite_moy`)
  - la `Run Summary` (`social:`)
  - la `Multi-Run Summary` (`social_moy:`)
- Neutralisation simple via CLI (sans refactor): mettre les parametres sociaux a 0 (par exemple `--social-influence-distance 0`).
### Evaluation legere de l'impact des biais individuels
- Mesures exposees en stats/synthese: moyenne et dispersion de `memory_focus`/`social_sensitivity`, plus biais d'usage observables.
- Biais d'usage calcules simplement (sans statistique lourde):
  - `memory_focus` vs usages reels memoire utile/dangereuse
  - `social_sensitivity` vs usages reels suivi social/boost de fuite
- En batch memoire/social, un bloc `traits_batch` compare automatiquement:
  - la configuration qui maximise le biais d'usage memoire
  - la configuration qui maximise le biais d'usage social
  - la configuration avec la plus forte dispersion de traits utile
  - la configuration la plus stable (reprise de la regle batch existante)
  - avec signalement explicite si donnees insuffisantes
- Ces indicateurs sont visibles dans:
  - la ligne `dynamique_*` (`traits_disp`, `traits_bias_tick`)
  - la `Run Summary` (`traits_impact:`)
  - la `Multi-Run Summary` (`traits_impact_moy:`), utile pour comparer plusieurs runs/batchs.


### Historique batch (archive d'experiences)
- Possibilite d'enregistrer plusieurs campagnes batch dans un fichier JSON d'historique.
- Chaque entree contient au minimum:
  - identifiant (`id`)
  - date UTC d'enregistrement
  - parametre et valeurs testees
  - runs par valeur + seed de base
  - synthese comparative batch
- Lecture et resume rapide via un outil CLI dedie (`analyze_batch_history.py`).
- Synthese comparative globale de l'historique: campagnes archivees, parametres testes, campagne la plus stable, meilleure generation max moyenne, meilleure population finale moyenne, plus faible extinction.
- Lecture agregee par parametre teste: campagnes concernees + valeurs les plus frequemment associees a stabilite / generation max / population finale (ambiguite ou insuffisance explicites).
- Lecture comparative memoire vs social: deltas moyens observes (stabilite/gen/pop) + metriques comportementales propres a chaque mecanique, avec signalement explicite si donnees insuffisantes/non comparables.
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
Exemple comparaison memoire active vs neutralisee (run simple):
```powershell
py main.py --seed 42 --steps 120 --log-interval 20 --food-memory-duration 0 --danger-memory-duration 0
```
Exemple comparaison influence sociale active vs neutralisee (run simple):
```powershell
py main.py --seed 42 --steps 120 --log-interval 20 --social-influence-distance 0 --social-follow-strength 0 --social-flee-boost-per-neighbor 0 --social-flee-boost-max 0
```

Exemple batch social (variation d'un parametre social):
```powershell
py main.py --batch-param social_follow_strength --batch-values 0,0.35,0.7 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple comparaison memoire via batch (meme seed de base):
```powershell
py main.py --batch-param food_memory_duration --batch-values 0,8 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture des biais individuels en batch (`traits_batch`):
```powershell
py main.py --batch-param social_follow_strength --batch-values 0,0.35,0.7 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture comparative perception en batch (`perception_batch`):
```powershell
py main.py --batch-param energy_drain_rate --batch-values 0.9,1.1,1.3 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
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
- `--food-memory-duration`, `--danger-memory-duration`
- `--food-memory-recall-distance`, `--danger-memory-avoid-distance`
- `--social-influence-distance`, `--social-follow-strength`, `--social-flee-boost-per-neighbor`, `--social-flee-boost-max`

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
Il inclut une synthese comparative globale de l'historique avec:
- nombre de campagnes archivees
- liste des parametres testes
- campagne la plus stable
- campagne avec meilleure generation max moyenne
- campagne avec meilleure population finale moyenne
- campagne avec plus faible taux d'extinction
- vue agregee par parametre teste (campagnes, valeur dominante stabilite/gen/pop).
- lecture comparative memoire vs social (deltas stabilite/gen/pop + lecture comportementale propre a chaque mecanique).
- signalement explicite des cas ambigus ou insuffisants.

## Exemple de sortie batch comparative
```text
--- Batch Comparative Summary ---
batch_comparatif:
plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
meilleure_gen_max_moy: energy_drain_rate=1.0 (gen_max_moy=2.50)
meilleure_pop_finale_moy: energy_drain_rate=1.0 (pop_finale_moy=42.50)
plus_faible_taux_extinction: egalite[energy_drain_rate=1.0,1.5] (taux_ext=0.00)
memoire_batch:
usage_memoire_utile_max: food_memory_duration=8.0 (usage_moy=4.30)
usage_memoire_dangereuse_max: food_memory_duration=8.0 (usage_moy=2.10)
effet_memoire_utile_max: food_memory_duration=8.0 (effet_moy=1.15)
effet_memoire_dangereuse_max: food_memory_duration=8.0 (effet_moy=0.72)
social_batch:
usage_suivi_social_max: social_follow_strength=0.7 (usage_moy=0.31)
usage_boost_fuite_social_max: social_follow_strength=0.35 (usage_moy=0.21)
part_creatures_influencees_max: social_follow_strength=0.7 (part_moy=0.28)
effet_multiplicateur_fuite_max: social_follow_strength=0.7 (multiplicateur_moy=1.18)
traits_batch:
bias_usage_memoire_max: social_follow_strength=0.35 (bias_moy=+0.06)
bias_usage_social_max: social_follow_strength=0.7 (bias_moy=+0.07)
dispersion_traits_max: social_follow_strength=0.7 (disp_moy=0.12)
configuration_plus_stable: social_follow_strength=0.35 (taux_ext=0.00, pop_finale_moy=43.00, gen_max_moy=2.90)
perception_batch:
usage_food_perception_max: energy_drain_rate=1.0 (bias_usage_moy=+0.06)
usage_threat_perception_max: energy_drain_rate=1.2 (bias_usage_moy=+0.08)
dispersion_perception_max: energy_drain_rate=1.0 (disp_moy=0.11)
configuration_plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
```

## Exemple de sortie historique batch comparative
```text
--- Batch History Comparative Summary ---
historique_batch_comparatif:
campagnes_archivees=3
parametres_testes=energy_drain_rate,reproduction_cost
campagne_plus_stable=exp_002 (taux_ext=0.00, pop_finale_moy=45.50, gen_max_moy=3.20)
campagne_meilleure_gen_max_moy=exp_003 (gen_max_moy=3.60)
campagne_meilleure_pop_finale_moy=exp_002 (pop_finale_moy=45.50)
campagne_plus_faible_taux_extinction=egalite[exp_001,exp_002] (taux_ext=0.00)
```

## Exemple de sortie historique par parametre
```text
--- Batch History Parameter Impact ---
historique_batch_parametres:
parametres=2
parametre=energy_drain_rate campagnes=3
  valeur_plus_frequente_stabilite=1.0 (freq=2/3)
  valeur_plus_frequente_gen_max=1.2 (freq=2/3)
  valeur_plus_frequente_pop_finale=1.0 (freq=2/3)
parametre=reproduction_cost campagnes=1
  valeur_plus_frequente_stabilite=ambigu[5.0,6.0] (freq=1/1)
  valeur_plus_frequente_gen_max=ambigu[5.0,6.0] (freq=1/1)
  valeur_plus_frequente_pop_finale=ambigu[5.0,6.0] (freq=1/1)
```

## Exemple de sortie historique memoire vs social
```text
--- Batch History Memory vs Social ---
historique_batch_memoire_vs_social:
campagnes_memoire=2 campagnes_sociales=2
delta_moy_stabilite_taux_ext: memoire=0.33 social=0.13
delta_moy_gen_max: memoire=1.50 social=3.50
delta_moy_pop_finale: memoire=6.50 social=11.00
lecture_stabilite=memory
lecture_gen_max=social
lecture_pop_finale=social
comportement_memoire: usage_utile_max_moy=3.50 usage_dangereuse_max_moy=2.25 effet_utile_max_moy=1.10 effet_dangereuse_max_moy=0.85
comportement_social: suivi_max_moy=0.60 boost_fuite_max_moy=0.23 part_influencee_max_moy=0.29 multiplicateur_fuite_max_moy=1.18
note=les metriques comportementales memoire/social sont affichees separement (unites differentes, comparaison directe non stricte)
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
py -m unittest tests.test_social_influence_behavior
py -m unittest tests.test_social_impact_metrics
py -m unittest tests.test_trait_impact_metrics
py -m unittest tests.test_individual_behavior_bias
py -m unittest tests.test_perception_traits
py -m unittest tests.test_perception_impact_metrics
```

## Lire les logs debug (indicateurs utiles)
Chaque bloc de log periodique contient:
- ligne principale: `population`, `vivants/morts`, `nourriture`, `energie_moy`, `age_moy`, `gen_moy`, naissances/deces, moyennes de traits (`prudence`, `dominance`, `repro_drive`, `memory_focus`, `social_sensitivity`).
- `generations:` distribution par generation (`g0`, `g1`, ...).
- `proto_groupes:` nombre de groupes, part du dominant, top groupes et traits moyens.
- `proto_tendance:` tendance temporelle des proto-groupes (`stable`, `hausse`, `baisse`, `nouveau`) entre logs.
- `proto_zones_creatures:` repartition des creatures par zones fertiles et proto-groupe dominant par zone.
- `causes_deces:` faim / epuisement / autre (tick et total).
- `dynamique_*:` croissance/declin/stagnation, pression nourriture, etat energie.
- `memoire_*:` creatures avec memoire active (utile/dangereuse), frequence d'usage, et effet moyen distance (tick/log).
- `social_*:` influence sociale locale (suivi social vers nourriture, renforcement de fuite, part influencee, multiplicateur de fuite tick/moyen).
- `traits_disp` / `traits_bias_tick` dans `dynamique_*`: dispersion des traits `memory_focus`/`social_sensitivity` et biais d'usage observables sur le tick.
- `traits_comp_moy` / `traits_disp` dans `dynamique_*`: inclut aussi `fp`/`tp` (moyennes `food_perception`/`threat_perception`) et `fp_sigma`/`tp_sigma`.
- `perception_*` dans `dynamique_*`: usages reels perception (`perception_log`, `perception_tick`, `perception_freq_tick`) et biais tick (`perception_bias_tick`).
- `zones_nourriture:` `riches`, `neutres`, `pauvres`, `fert_moy`.

En fin de run:
- bloc `--- Run Summary ---` avec dominant final, stabilite/hausse observees, zones finales, traits moyens, impact memoire cumule, impact social (`social:`) et impact des biais individuels (`traits_impact:`).
- le bloc `traits_impact:` inclut aussi les mesures perception (`fp_mu`, `fp_sigma`, `tp_mu`, `tp_sigma`, `bias_fp_det`, `bias_fp_eat`, `bias_tp_fuite`).

En mode multi-runs:
- bloc `--- Multi-Run Summary ---` avec: nombre de runs, seeds, taux d'extinction, generation max moyenne, population finale moyenne, traits moyens finaux, dominant final le plus frequent, impact memoire moyen, impact social moyen (`social_moy:`) et impact moyen des biais individuels (`traits_impact_moy:`).
- le bloc `traits_impact_moy:` inclut aussi les mesures perception agregees (`fp_mu`, `fp_sigma`, `tp_mu`, `tp_sigma`, biais perception).

En mode batch:
- bloc `=== Batch Experimental Mode ===` puis un resume par valeur testee.
- bloc `--- Batch Summary ---` avec agregats comparables entre valeurs.
- bloc `--- Batch Comparative Summary ---` avec interpretation automatique des meilleures valeurs.
- si le parametre batch est un parametre memoire, le bloc inclut aussi les comparatifs memoire (`memoire_batch`).
- si le parametre batch est un parametre social, le bloc inclut aussi les comparatifs sociaux (`social_batch`).
- si le parametre batch est memoire ou social et que les metriques existent, le bloc inclut aussi `traits_batch`.

En mode historique batch:
- ligne `batch_history: <chemin> id=<batch_id>` quand une campagne est archivee.

En mode export:
- ligne `export: <chemin> (<format>)` en fin d'execution.
- le contenu exporte reprend les memes syntheses que la console (run simple, multi-runs, batch).

Avec les outils d'analyse:
- `py analyze_export.py <fichier>` affiche une synthese concise basee sur l'export.
- `py analyze_batch_history.py <fichier_historique>` affiche un resume des campagnes batch archivees, une synthese comparative globale, une vue agregee par parametre teste (avec ambiguite/insuffisance explicites) et une lecture memoire vs social.
- pour observer la memoire locale en run: suivre `memoire_active`, `memoire_part`, `memoire_tick`, `memoire_freq_tick`, `memoire_effet_tick` et `memoire_log` dans la ligne `dynamique_*`.
- pour comparer memoire active vs neutralisee: relancer avec `--food-memory-duration 0 --danger-memory-duration 0` puis comparer `memoire:*` et la synthese finale.
- pour comparer influence sociale active vs neutralisee: relancer avec `--social-influence-distance 0 --social-follow-strength 0 --social-flee-boost-per-neighbor 0 --social-flee-boost-max 0` puis comparer `social_*` et les blocs `social:`/`social_moy:`.
- pour un batch social, verifier dans `Batch Comparative Summary` le bloc `social_batch` (usage suivi, usage boost fuite, part influencee, effet multiplicateur).

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
- Interpretation batch memoire (usage/effet utiles et dangereux) pour les parametres memoire.
- Interpretation batch sociale (suivi/fuite/part influencee/effet multiplicateur) pour les parametres sociaux.
- Interpretation batch des biais individuels (`traits_batch`) pour les parametres memoire/sociaux.
- Historique batch leger (archivage multi-campagnes + outil de lecture).
- Synthese comparative globale de l'historique batch (stable/gen/pop/extinction).
- Lecture agregee de l'impact des parametres testes dans l'historique batch.
- Lecture comparative memoire vs social dans l'historique batch (deltas stabilite/gen/pop + lecture comportementale dediee).
- Memoire locale courte (zone utile/dangereuse) visible dans les stats/debug et testee.
- Evaluation legere de l'impact memoire (usage/frequence/part active/effet distance) dans stats, synthese run, multi-runs, export et analyse.
- Influence sociale locale minimale observable dans les stats/debug (suivi social + fuite renforcee).
- Evaluation legere de l'impact social (frequences, part influencee, multiplicateur de fuite tick/moyen) dans stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact des biais individuels (`memory_focus`, `social_sensitivity`): moyenne/dispersion + biais d'usage memoire/social en stats, synthese run, multi-runs, export et analyse.
- Biais individuels legers sur memoire/social (memory_focus, social_sensitivity) heritables, mutables, visibles en stats/debug et testes.
- Variabilite individuelle de perception (`food_perception`, `threat_perception`) heritable et mutante, avec effet leger sur detection nourriture/menace et visibilite en stats/synthese/debug.
- Evaluation legere de l'impact perception (moyenne/dispersion + biais detection/consommation/fuite) visible en stats, synthese run, multi-runs, export et analyse.
- Interpretation batch perception (`perception_batch`) pour comparer usage perception, dispersion et stabilite des configurations testees.

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
