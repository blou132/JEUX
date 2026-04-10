# VISION

## 1) Genre exact du jeu
**Simulation evolutive systemique en temps reel**, avec une couche de **strategie indirecte**.  
Le joueur n'incarne pas une creature unique : il pilote les pressions qui faconnent un ecosysteme.

## 2) Boucle de gameplay principale
1. **Observer** l'ecosysteme (especes, ressources, predation, climat, lignees).
2. **Decider** des interventions (modifier environnement, introduire contraintes/opportunites, selectionner des lignees).
3. **Lancer un cycle d'evolution** (plusieurs generations simulees).
4. **Analyser les resultats** (survie, diversification, comportements emergents, effondrements).
5. **Ajuster la strategie** pour viser un objectif long terme (stabilite, diversite, domination d'une lignee, etc.).

## 3) Role du joueur
- Definir la direction evolutive sans micro-controler les individus.
- Choisir quelles pressions ecologiques amplifier ou reduire.
- Arbitrer entre objectifs contradictoires : stabilite, innovation, rendement, resilience.
- Assumer les consequences a long terme de decisions locales.

## 4) Role de l'IA
- **IA comportementale des agents** : decisions locales (fuite, chasse, reproduction, migration, cooperation).
- **IA d'evolution** : mutation/recombinaison sous contraintes biologiques du jeu.
- **IA de direction systemique** : generer des evenements ecologiques credibles (secheresse, maladie, predateur invasif) pour maintenir la tension.
- **IA d'aide au joueur** : expliquer les causes d'un effondrement ou d'une emergence via une lecture claire des donnees.

## 5) Ce qui evolue reellement
- **Genome fonctionnel** : traits hereditaires qui impactent directement les stats et comportements.
- **Morphologie utilitaire** : modifications qui changent les capacites (mobilite, alimentation, defense, perception).
- **Comportements appris/transmis** (partiellement) : routines de chasse, trajectoires migratoires, priorites de reproduction.
- **Dynamique d'ecosysteme** : chaines trophiques, niches, cycles de ressources, co-evolution proie/predateur.

## 6) Ce qui differencie ce jeu de Spore
- Simulation **continue et systemique**, pas decoupee en mini-phases de progression.
- Le joueur agit surtout par **pression selective** plutot que par creation directe "a la main" de creatures.
- Priorite a la **co-evolution d'un ecosysteme entier**, pas a l'ascension lineaire d'une seule espece.
- Les consequences sont **persistantes et mesurables** (historique genetique, extinctions, bifurcations).
- Le fun vient de l'**emergence strategique** et de la lecture de systemes, plus que du "toy-like editing".

## 7) Contraintes techniques
- Simuler un grand nombre d'agents a cout stable (CPU/GPU) avec ticks deterministes.
- Modele genetique lisible, extensible et serialisable (sauvegardes robustes).
- Outils de debug/telemetry obligatoires pour comprendre les causes d'un comportement emergent.
- Pipeline de donnees modulaire (traits, especes, biomes, evenements) pour iterer sans casser les saves.
- UI de visualisation claire (filtres, graphes, timelines) pour rendre la complexite jouable.

## 8) Risques majeurs
- **Opacite systemique** : le joueur ne comprend pas pourquoi il gagne/perd.
- **Explosion de complexite** : simulation riche mais peu amusante faute d'objectifs clairs.
- **Cout performance** : l'echelle d'agents casse le framerate ou les temps de simulation.
- **Equilibrage fragile** : une strategie dominante tue la diversite.
- **Scope creep** : vouloir couvrir trop de couches (bio + social + civilisation) trop tot.
- **Comparaison frontale a Spore** : promesse percue comme "Spore 2" au lieu d'une proposition propre.
