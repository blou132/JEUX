# Evolution MVP (Python)

## Presentation rapide
Ce projet est un simulateur evolutif inspire de Spore, centre sur une evolution emergente simple, lisible et testable.
Le scope actuel est un MVP enrichi: creatures autonomes, survie, reproduction, mutation, menace/fuite, traits comportementaux heritaires, proto-groupes, pression ecologique legere sur la nourriture, memoire locale courte, influence sociale locale minimale, biais individuels legers sur memoire/social, variabilite individuelle de perception, biais individuel leger de prise de risque, variabilite individuelle legere de persistance comportementale, biais individuel leger d'exploration spatiale, biais individuel leger de preference de densite locale, et variabilite individuelle legere de longevite/vieillissement.

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
- Biais individuel leger de prise de risque (`risk_taking`) heritable, mutante et visible en stats/synthese/debug.
- Variabilite individuelle legere de persistance comportementale (`behavior_persistence`) heritable, mutante et visible en stats/synthese/debug.
- Variabilite individuelle legere d'exploration spatiale (`exploration_bias`) heritable, mutante et visible en stats/synthese/debug.
- Variabilite individuelle legere de preference de densite locale (`density_preference`) heritable, mutante et visible en stats/synthese/debug.
- Variabilite individuelle legere de longevite/vieillissement (`longevity_factor`) heritable, mutante et visible en stats/synthese/debug.
- Evaluation legere de l'impact `density_preference` (moyenne/dispersion, frequences `seek`/`avoid`, biais d'usage et effet local) visible en stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact `exploration_bias` (moyenne/dispersion, frequences `explore`/`settle`, biais d'usage separes, effet distance a l'ancre) visible en stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact `behavior_persistence` (moyenne/dispersion, frequence d'inertie, biais d'usage, oscillations `search_food`<->`wander`) visible en stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact `risk_taking` (moyenne/dispersion, biais de fuite et signal borderline) visible en stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact perception: moyennes/dispersion + biais d'usage detection/consommation/fuite en stats/syntheses.
- Interpretation batch perception (`perception_batch`) pour comparer usage/dispersion/stabilite des configurations testees.
- Interpretation batch energie (`energie_batch`) pour comparer effet drain/cout repro, dispersion energetique et stabilite.
- Interpretation batch `behavior_persistence` (`behavior_persistence_batch`) pour comparer switchs evites, taux de switch et taux de blocage utile.
- Interpretation batch `exploration_bias` (`exploration_bias_batch`) pour comparer usages `explore`/`settle`/`guided` et stabilite.
- Interpretation batch `density_preference` (`density_preference_batch`) pour comparer usages `seek`/`avoid`, part `avoid` et stabilite.
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

### Biais individuel de prise de risque
- Trait leger ajoute: `risk_taking`.
- Effet volontairement limite:
  - ajuste legerement la sensibilite a une menace borderline (priorite fuite conservee).
  - plus `risk_taking` est eleve, moins la creature fuit les menaces limite.
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*`: `traits_comp_moy` (`rk`), `traits_disp` (`rk_sigma`) et `perception_bias_tick` (`rk_fuite`).
  - `Run Summary` / `Multi-Run Summary`: `traits_moy` / `traits_finaux_moy` (`rk`) et `traits_impact` / `traits_impact_moy` (`rk_mu`, `rk_sigma`, `bias_rk_fuite`).
  - indicateurs borderline lies au risque: `borderline_threat_encounters`, `borderline_threat_flees`, `borderline_threat_flee_rate`, `risk_taking_borderline_encounter_mean`, `risk_taking_borderline_flee_mean`, `risk_taking_borderline_flee_bias`.

### Variabilite individuelle de persistance comportementale
- Trait leger ajoute: `behavior_persistence`.
- Effet volontairement limite:
  - ajoute une legere inertie entre intentions compatibles (`search_food` <-> `wander`) autour du seuil de faim.
  - ne prend pas le dessus sur les priorites fortes (fuite, mort, reproduction, cible nourriture visible).
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*`: `inertie_tick`, `inertie_log`, `traits_comp_moy` (`bp`), `traits_disp` (`bp_sigma`) et `traits_bias_tick` (`bp_inertie`).
  - `dynamique_*`: `oscill_tick` / `oscill_log` pour observer les bascules reelles vs bascules evitees entre `search_food` et `wander`.
  - `Run Summary` / `Multi-Run Summary`: `traits_impact` / `traits_impact_moy` (`bp_mu`, `bp_sigma`, `bias_bp_inertie`, `inertie_total`/`inertie_total_moy`, `osc_bp`/`osc_bp_moy`).

### Variabilite individuelle d'exploration spatiale
- Trait leger ajoute: `exploration_bias`.
- Effet volontairement limite:
  - `exploration_bias > 1.0`: tendance legere a s'eloigner d'une zone favorable recente (exploration).
  - `exploration_bias < 1.0`: tendance legere a rester proche d'une zone favorable recente (fidelite locale).
- L'effet est applique uniquement en errance/recherche sans cible directe, pour ne pas casser les priorites existantes (fuite, mort, reproduction, cible nourriture visible).
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*`: `traits_comp_moy` (`ex`), `traits_disp` (`ex_sigma`), `traits_bias_tick` (`ex_guide`, `ex_explore`, `ex_settle`), `exploration_tick`/`exploration_log`.
  - `Run Summary` / `Multi-Run Summary`: `traits_moy` / `traits_finaux_moy` (`ex`) et `traits_impact` / `traits_impact_moy` (`ex_mu`, `ex_sigma`, `bias_explore`, `exploration:*` avec `ex_mu`/`st_mu` et biais associes).

### Variabilite individuelle de preference de densite locale
- Trait leger ajoute: `density_preference`.
- Effet volontairement limite:
  - `density_preference > 1.0`: tendance legere a se rapprocher d'un centre local de congeneres (`seek`).
  - `density_preference < 1.0`: tendance legere a s'eloigner d'une zone localement dense (`avoid`).
- L'effet est applique uniquement en errance/recherche sans cible directe, pour ne pas casser les priorites existantes (fuite, mort, reproduction, cible nourriture visible).
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*`: `traits_comp_moy` (`dp`), `traits_disp` (`dp_sigma`), `traits_bias_tick` (`dp_guide`, `dp_seek`, `dp_avoid`), `densite_tick`/`densite_log`.
  - `Run Summary` / `Multi-Run Summary`: `traits_moy` / `traits_finaux_moy` (`dp`) et `traits_impact` / `traits_impact_moy` (`dp_mu`, `dp_sigma`, `densite:*` avec `part_seek`, `seek_mu`, `avoid_mu`, `dens_voisins`, `delta_centre`).

### Evaluation legere de l'impact density_preference
- Indicateurs exposes en stats/synthese:
  - moyenne et dispersion de `density_preference`
  - frequences d'usage `seek` / `avoid` (`density_preference_seek_usage_per_tick_total`, `density_preference_avoid_usage_per_tick_total`)
  - parts d'usage `seek` / `avoid` (`density_preference_seek_share_*`, `density_preference_avoid_share_*`)
  - biais d'usage du trait (`density_preference_seek_usage_bias_*`, `density_preference_avoid_usage_bias_*`)
  - effet local observable (`avg_density_preference_neighbor_count_*`, `avg_density_preference_center_distance_delta_*`)
- Visibilite:
  - `dynamique_*`: bloc `densite_tick` / `densite_log`
  - `Run Summary` / `Multi-Run Summary`: bloc `densite:` / `densite_moy:` avec `part_avoid`, `freq_seek`, `freq_avoid`

### Evaluation legere de l'impact perception
- Indicateurs exposes en stats/synthese:
  - moyenne et dispersion de `food_perception` et `threat_perception`
  - usage reel detection nourriture (`food_detection_*`) et consommation (`food_consumption_*`)
  - usage reel detection menace/fuite (`threat_detection_*`)
  - biais simples: moyenne des utilisateurs - moyenne population (`food_perception_detection_usage_bias_*`, `food_perception_consumption_usage_bias_*`, `threat_perception_flee_usage_bias_*`)
- Visibilite:
  - `dynamique_*`: `perception_log`, `perception_tick`, `perception_freq_tick`, `perception_bias_tick`
  - `Run Summary` / `Multi-Run Summary`: bloc `traits_impact` / `traits_impact_moy` (inclut `fp_mu`, `tp_mu`, biais perception)

### Variabilite individuelle d'endurance / cout energetique
- Traits legers ajoutes: `energy_efficiency` et `exhaustion_resistance`.
- Effet volontairement limite:
  - `energy_efficiency` module legerement la depense energetique passive (drain).
  - `exhaustion_resistance` module legerement le cout energetique de reproduction.
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - ligne principale: `efficacite_energie_moy`, `resistance_epuisement_moy`
  - `dynamique_*`: `traits_comp_moy` (`ee`, `er`), `traits_disp` (`ee_sigma`, `er_sigma`), `energie_traits_effets` (`drain_mult`, `repro_mult`, `drain_obs_mult`, `repro_obs_mult`, `drain_obs`, `repro_obs`) et `traits_bias_tick` (`ee_drain`, `er_repro`)
  - `Run Summary` / `Multi-Run Summary`: `traits_moy` / `traits_finaux_moy` (`ee`, `er`) et `traits_impact` / `traits_impact_moy` (`ee_mu`, `ee_sigma`, `er_mu`, `er_sigma`, `energy_obs`, biais `ee`/`er`)

### Variabilite individuelle de longevite / vieillissement
- Trait leger ajoute: `longevity_factor`.
- Effet volontairement limite:
  - module legerement l'usure energetique liee a l'age (retarde ou accelere le surcout de drain avec l'age).
  - n'ajoute aucune nouvelle mecanique lourde (pas de systeme biologique complexe).
- Heredite simple + mutation legere via le pipeline genetique existant.
- Observation dans les logs/syntheses:
  - `dynamique_*`: `traits_comp_moy` (`lg`), `traits_disp` (`lg_sigma`) et `vieillissement_tick` (`act`, `freq`, `mult`, `lg_bias`).
  - `Run Summary` / `Multi-Run Summary`: `traits_moy` / `traits_finaux_moy` (`lg`) et `traits_impact` / `traits_impact_moy` (`lg_mu`, `lg_sigma`, `agewear_freq`, `agewear_mult`, `lg_age_bias`).

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
- Quand les metriques existent, la synthese inclut aussi `risque_batch`:
  - configuration qui maximise l'intensite d'usage observee du risque en fuite (proxy: `abs(bias_rk_fuite)`)
  - configuration qui maximise l'effet risque sur menaces borderline (proxy: `abs(rk_border_bias)`)
  - configuration avec la plus forte dispersion utile de `risk_taking` (`rk_sigma`)
  - configuration avec le plus haut taux de fuite en cas borderline (`rk_border_rate`)
  - signalement explicite si les cas borderline sont absents (interpretation limitee)
- Pour les batchs sur parametres energetiques (`energy_drain_rate`, `reproduction_cost`, `reproduction_threshold`, `reproduction_min_age`, `mutation_variation`), la synthese inclut aussi `energie_batch`:
  - configuration qui maximise l'effet observe sur le drain energetique (proxy: `abs(drain_mult_obs - 1)`)
  - configuration qui maximise l'effet observe sur le cout de reproduction (proxy: `abs(repro_mult_obs - 1)`)
  - configuration avec la plus forte dispersion energetique utile (`(std_ee + std_er) / 2`)
  - configuration la plus stable (regle batch standard)
  - signalement explicite des cas ambigus ou insuffisants
- Quand les metriques existent, la synthese inclut aussi `behavior_persistence_batch`:
  - configuration qui maximise les switchs evites (`search_wander_switches_prevented_total`)
  - configuration qui minimise le taux de switch (`behavior_persistence_oscillation_switch_rate`)
  - configuration qui maximise le taux de blocage utile (`behavior_persistence_oscillation_prevented_rate`)
  - configuration la plus stable (regle batch standard)
  - signalement explicite des cas ambigus ou insuffisants
- Quand les metriques existent, la synthese inclut aussi `exploration_bias_batch`:
  - configuration qui maximise l'usage `explore` (`exploration_bias_explore_share`)
  - configuration qui maximise l'usage `settle` (`1 - exploration_bias_explore_share`)
  - configuration qui maximise le guidage `guided` (`exploration_bias_guided_total`)
  - configuration la plus stable (regle batch standard)
  - signalement explicite des cas ambigus ou insuffisants
- Quand les metriques existent, la synthese inclut aussi `density_preference_batch`:
  - configuration qui maximise l'usage `seek` (`density_preference_seek_usage_per_tick`)
  - configuration qui maximise l'usage `avoid` (`density_preference_avoid_usage_per_tick`)
  - configuration qui maximise la part `avoid` (`density_preference_avoid_share`)
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

Exemple lecture comparative energie en batch (`energie_batch`):
```powershell
py main.py --batch-param energy_drain_rate --batch-values 0.9,1.0,1.2 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture comparative perception en batch (`perception_batch`):
```powershell
py main.py --batch-param energy_drain_rate --batch-values 0.9,1.1,1.3 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture comparative `behavior_persistence` en batch (`behavior_persistence_batch`):
```powershell
py main.py --batch-param mutation_variation --batch-values 0.05,0.1,0.2 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture comparative `exploration_bias` en batch (`exploration_bias_batch`):
```powershell
py main.py --batch-param mutation_variation --batch-values 0.05,0.1,0.2 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
```

Exemple lecture comparative `density_preference` en batch (`density_preference_batch`):
```powershell
py main.py --batch-param mutation_variation --batch-values 0.05,0.1,0.2 --batch-runs 3 --seed 42 --seed-step 1 --steps 120 --log-interval 20
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
energie_batch:
effet_drain_energie_max: energy_drain_rate=1.0 (effet_moy=0.05)
effet_cout_reproduction_max: energy_drain_rate=1.2 (effet_moy=0.08)
dispersion_energie_max: energy_drain_rate=1.2 (disp_moy=0.10)
configuration_plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
perception_batch:
usage_food_perception_max: energy_drain_rate=1.0 (bias_usage_moy=+0.06)
usage_threat_perception_max: energy_drain_rate=1.2 (bias_usage_moy=+0.08)
dispersion_perception_max: energy_drain_rate=1.0 (disp_moy=0.11)
configuration_plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
risque_batch:
usage_fuite_risque_max: energy_drain_rate=1.0 (impact_abs_moy=0.09)
effet_borderline_risque_max: energy_drain_rate=1.0 (impact_abs_moy=0.07)
dispersion_risque_max: energy_drain_rate=1.2 (rk_sigma_moy=0.12)
taux_fuite_borderline_max: energy_drain_rate=1.2 (taux_moy=0.61)
configuration_plus_stable: energy_drain_rate=1.0 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
behavior_persistence_batch:
switchs_evites_max: mutation_variation=0.1 (switchs_evites_moy=8.00)
taux_switch_min: mutation_variation=0.1 (taux_moy=0.350)
taux_blocage_utile_max: mutation_variation=0.1 (taux_moy=0.650)
configuration_plus_stable: mutation_variation=0.1 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
exploration_bias_batch:
usage_explore_max: mutation_variation=0.05 (part_explore_moy=0.750)
usage_settle_max: mutation_variation=0.2 (part_settle_moy=0.800)
usage_guided_max: mutation_variation=0.2 (guided_moy=11.00)
configuration_plus_stable: mutation_variation=0.1 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
density_preference_batch:
usage_seek_max: mutation_variation=0.05 (freq_seek_moy=0.310)
usage_avoid_max: mutation_variation=0.2 (freq_avoid_moy=0.280)
part_avoid_max: mutation_variation=0.2 (part_avoid_moy=0.640)
configuration_plus_stable: mutation_variation=0.1 (taux_ext=0.00, pop_finale_moy=42.50, gen_max_moy=2.50)
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
py -m unittest tests.test_energy_traits
py -m unittest tests.test_behavior_persistence_trait
py -m unittest tests.test_behavior_persistence_impact_metrics
py -m unittest tests.test_risk_taking_trait
py -m unittest tests.test_risk_taking_impact_metrics
py -m unittest tests.test_exploration_bias_trait
py -m unittest tests.test_longevity_trait
```

## Lire les logs debug (indicateurs utiles)
Chaque bloc de log periodique contient:
- ligne principale: `population`, `vivants/morts`, `nourriture`, `energie_moy`, `age_moy`, `gen_moy`, naissances/deces, moyennes de traits (`prudence`, `dominance`, `risk_taking`, `repro_drive`, `memory_focus`, `social_sensitivity`, `behavior_persistence`, `exploration_bias`, `density_preference`, `energy_efficiency`, `exhaustion_resistance`, `longevity_factor`).
- `generations:` distribution par generation (`g0`, `g1`, ...).
- `proto_groupes:` nombre de groupes, part du dominant, top groupes et traits moyens.
- `proto_tendance:` tendance temporelle des proto-groupes (`stable`, `hausse`, `baisse`, `nouveau`) entre logs.
- `proto_zones_creatures:` repartition des creatures par zones fertiles et proto-groupe dominant par zone.
- `causes_deces:` faim / epuisement / autre (tick et total).
- `dynamique_*:` croissance/declin/stagnation, pression nourriture, etat energie.
- `memoire_*:` creatures avec memoire active (utile/dangereuse), frequence d'usage, et effet moyen distance (tick/log).
- `social_*:` influence sociale locale (suivi social vers nourriture, renforcement de fuite, part influencee, multiplicateur de fuite tick/moyen).
- `traits_disp` / `traits_bias_tick` dans `dynamique_*`: dispersion des traits `memory_focus`/`social_sensitivity` et biais d'usage observables sur le tick.
- `traits_comp_moy` / `traits_disp` dans `dynamique_*`: inclut aussi `fp`/`tp` (moyennes `food_perception`/`threat_perception`) et `fp_sigma`/`tp_sigma`, `rk`/`rk_sigma` pour la prise de risque, `bp`/`bp_sigma` pour la persistance comportementale, `ex`/`ex_sigma` pour l'exploration spatiale, `dp`/`dp_sigma` pour la preference de densite locale, `ee`/`er` et `ee_sigma`/`er_sigma` pour l'endurance energetique, ainsi que `lg`/`lg_sigma` pour la longevite.
- `exploration_log` / `exploration_tick` dans `dynamique_*`: usage observe du biais d'exploration (`guides`, `explore`, `settle`, `part_explore`, `ex_mu`, `st_mu`, `ex_bias`, `st_bias`, `delta_ancre`).
- `densite_log` / `densite_tick` dans `dynamique_*`: usage observe de la preference de densite (`guides`, `seek`, `avoid`, `part_seek`, `part_avoid`, `freq_seek`, `freq_avoid`, `seek_mu`, `avoid_mu`, `dp_bias`, `seek_bias`, `avoid_bias`, `dens_voisins`, `delta_centre`).
- `inertie_log` / `inertie_tick` dans `dynamique_*`: usage observe de la persistance d'intention.
- `oscill_log` / `oscill_tick` dans `dynamique_*`: oscillations `search_food`<->`wander` (switch reels, switches evites par inertie, taux associes).
- `perception_*` dans `dynamique_*`: usages reels perception (`perception_log`, `perception_tick`, `perception_freq_tick`) et biais tick (`perception_bias_tick`, incluant `rk_fuite`).
- `energie_traits_effets` dans `dynamique_*`: multiplicateurs moyens de drain/cout (`drain_mult`, `repro_mult`) + effets observes (`drain_obs_mult`, `repro_obs_mult`, `drain_obs`, `repro_obs`), avec biais tick associes (`ee_drain`, `er_repro`).
- `vieillissement_tick` dans `dynamique_*`: usure age observee (`act`, `freq`, `mult`) et biais d'usage `longevity_factor` (`lg_bias`).
- `zones_nourriture:` `riches`, `neutres`, `pauvres`, `fert_moy`.

En fin de run:
- bloc `--- Run Summary ---` avec dominant final, stabilite/hausse observees, zones finales, traits moyens, impact memoire cumule, impact social (`social:`) et impact des biais individuels (`traits_impact:`).
- le bloc `traits_impact:` inclut aussi les mesures perception (`fp_mu`, `fp_sigma`, `tp_mu`, `tp_sigma`, `bias_fp_det`, `bias_fp_eat`, `bias_tp_fuite`), la prise de risque (`rk_mu`, `rk_sigma`, `bias_rk_fuite`), la persistance comportementale (`bp_mu`, `bp_sigma`, `bias_bp_inertie`, `inertie_total`), l'exploration spatiale (`ex_mu`, `ex_sigma`, `bias_explore`, `exploration:*`, plus `ex_mu`/`st_mu` et biais `ex`/`st`), la preference de densite locale (`dp_mu`, `dp_sigma`, `densite:*`, plus biais `dp`/`seek`/`avoid`), les mesures d'endurance (`ee_mu`, `ee_sigma`, `er_mu`, `er_sigma`, `energy_obs`, `bias_ee_drain`, `bias_er_repro`) et la longevite (`lg_mu`, `lg_sigma`, `agewear_freq`, `agewear_mult`, `lg_age_bias`).
- le bloc `traits_impact:` inclut aussi `osc_bp` pour la lecture d'oscillation `search_food`<->`wander` (`switch`, `bloc`, `events`, `taux_switch`, `taux_bloc`).

En mode multi-runs:
- bloc `--- Multi-Run Summary ---` avec: nombre de runs, seeds, taux d'extinction, generation max moyenne, population finale moyenne, traits moyens finaux, dominant final le plus frequent, impact memoire moyen, impact social moyen (`social_moy:`) et impact moyen des biais individuels (`traits_impact_moy:`).
- le bloc `traits_impact_moy:` inclut aussi les mesures perception agregees (`fp_mu`, `fp_sigma`, `tp_mu`, `tp_sigma`, biais perception), la prise de risque agregee (`rk_mu`, `rk_sigma`, `bias_rk_fuite`), la persistance comportementale agregee (`bp_mu`, `bp_sigma`, `bias_bp_inertie`, `inertie_total_moy`), l'exploration spatiale agregee (`ex_mu`, `ex_sigma`, `bias_explore`, `exploration_moy:*`, plus `ex_mu`/`st_mu` et biais `ex`/`st`), la preference de densite locale agregee (`dp_mu`, `dp_sigma`, `densite_moy:*`, plus biais `dp`/`seek`/`avoid`), les mesures d'endurance agregees (`ee_mu`, `ee_sigma`, `er_mu`, `er_sigma`, `energy_obs_moy`, biais `ee`/`er`) et la longevite agregee (`lg_mu`, `lg_sigma`, `agewear_freq`, `agewear_mult`, `lg_age_bias`).
- le bloc `traits_impact_moy:` inclut aussi `osc_bp_moy` pour la lecture moyenne des oscillations `search_food`<->`wander` (switch, blocage inertie, taux).

En mode batch:
- bloc `=== Batch Experimental Mode ===` puis un resume par valeur testee.
- bloc `--- Batch Summary ---` avec agregats comparables entre valeurs.
- bloc `--- Batch Comparative Summary ---` avec interpretation automatique des meilleures valeurs.
- si le parametre batch est un parametre memoire, le bloc inclut aussi les comparatifs memoire (`memoire_batch`).
- si le parametre batch est un parametre social, le bloc inclut aussi les comparatifs sociaux (`social_batch`).
- si le parametre batch est un parametre energetique, le bloc inclut aussi les comparatifs energie (`energie_batch`).
- si le parametre batch est memoire ou social et que les metriques existent, le bloc inclut aussi `traits_batch`.
- quand les metriques existent, le bloc inclut aussi `behavior_persistence_batch`.
- quand les metriques existent, le bloc inclut aussi `exploration_bias_batch`.
- quand les metriques existent, le bloc inclut aussi `density_preference_batch`.

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
- pour un batch energetique, verifier dans `Batch Comparative Summary` le bloc `energie_batch` (effet drain/cout repro, dispersion energetique, stabilite).
- pour l'impact `risk_taking`, verifier dans `Batch Comparative Summary` le bloc `risque_batch` (usage fuite, effet borderline, dispersion `rk`, taux borderline).
- pour l'impact `behavior_persistence`, verifier dans `Batch Comparative Summary` le bloc `behavior_persistence_batch` (switchs evites, taux de switch, taux de blocage utile).
- pour l'impact `density_preference`, verifier dans `Batch Comparative Summary` le bloc `density_preference_batch` (usage `seek`, usage `avoid`, part `avoid`, stabilite).

Lecture rapide conseillee:
1. verifier `alive` + `total_births/total_deaths` pour la dynamique globale,
2. verifier `pression_nourriture` + `zones_nourriture` pour la contrainte environnementale,
3. verifier `proto_groupes` + `proto_tendance` + `proto_zones_creatures` pour les tendances evolutives locales,
4. verifier `Run Summary` pour comparer rapidement plusieurs seeds,
5. en mode multi-runs, verifier `Multi-Run Summary` pour comparer plusieurs seeds,
6. en mode batch, comparer les lignes du `Batch Summary` puis valider `Batch Comparative Summary` (incluant `risque_batch` quand les metriques existent),
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
- Interpretation batch energie (`energie_batch`) pour les parametres energetiques (effet drain/cout reproduction, dispersion, stabilite).
- Interpretation batch `behavior_persistence` (`behavior_persistence_batch`) pour comparer switchs evites / taux de switch / taux de blocage utile et stabilite.
- Interpretation batch `exploration_bias` (`exploration_bias_batch`) pour comparer usage `explore`/`settle`/`guided` et stabilite.
- Interpretation batch `density_preference` (`density_preference_batch`) pour comparer usage `seek`/`avoid`, part `avoid` et stabilite.
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
- Biais individuel leger de prise de risque (`risk_taking`) heritable et mutante, avec effet leger sur la fuite face aux menaces borderline et visibilite en stats/synthese/debug.
- Variabilite individuelle legere de persistance comportementale (`behavior_persistence`) heritable et mutante, avec effet leger d'inertie entre intentions compatibles et visibilite en stats/synthese/debug.
- Variabilite individuelle legere d'exploration spatiale (`exploration_bias`) heritable et mutante, avec effet leger d'exploration/fidelite locale autour des zones favorables memorisees et visibilite en stats/synthese/debug.
- Variabilite individuelle legere de preference de densite locale (`density_preference`) heritable et mutante, avec effet leger `seek`/`avoid` selon densite locale et visibilite en stats/synthese/debug.
- Evaluation legere de l'impact `density_preference` (moyenne/dispersion, frequences `seek`/`avoid`, biais d'usage et effet local) visible en stats, synthese run, multi-runs, export et analyse.
- Evaluation legere de l'impact `behavior_persistence` (frequence inertie, biais d'usage et impact oscillation `search_food`<->`wander`) visible en stats/synthese/debug/export.
- Evaluation legere de l'impact perception (moyenne/dispersion + biais detection/consommation/fuite) visible en stats, synthese run, multi-runs, export et analyse.
- Interpretation batch perception (`perception_batch`) pour comparer usage perception, dispersion et stabilite des configurations testees.
- Evaluation legere de l'impact energetique (`energy_efficiency`, `exhaustion_resistance`): moyenne/dispersion + effet observe sur drain/cout reproduction + biais d'usage, visible en stats, synthese run, multi-runs, export et analyse.
- Variabilite individuelle legere de longevite/vieillissement (`longevity_factor`) heritable et mutante, avec effet leger sur l'usure d'age (drain age), et visibilite en stats/synthese/debug.

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


