# RELEASE PLAN

## Regle de cadrage
Le projet est decoupe en 4 buckets stricts: `MVP`, `v0.2`, `v0.3`, `long terme`.
Le `MVP` doit etre jouable en **une seule phase** sans dependre d'une feature des versions suivantes.

## MVP (1 phase jouable)
Objectif: lancer une simulation simple, observer plusieurs generations, voir de vraies differences dues aux mutations.

Contenu `MVP` (non negociable):
- Carte simple (1 biome, taille fixe, pas de streaming).
- Ressources de nourriture (spawn + respawn simple).
- Creatures autonomes (boucle decision locale).
- Faim / energie / mort.
- Deplacement.
- Fuite / chasse.
- Reproduction.
- Mutations simples.
- Statistiques de generations.
- Interface de debug minimale.

Definition de "phase jouable" du MVP:
- Le joueur lance une partie et demarre la simulation.
- Les creatures survivent, chassent/fuient, se reproduisent et meurent sans intervention manuelle continue.
- Au moins 10 generations peuvent etre simulees.
- Les stats montrent une evolution mesurable (population, age moyen, traits moyens).

## v0.2
Objectif: stabiliser et enrichir l'ecosysteme sans exploser la complexite.

Contenu `v0.2`:
- Plusieurs types de nourriture (valeurs nutritives differentes).
- 2 a 3 archetypes de creatures (ex: herbivore, opportuniste, predateur).
- Cycles environnementaux simples (jour/nuit ou saison legere).
- Evenements systemiques de base (secheresse courte, maladie locale).
- Sauvegarde/chargement en slots.
- UI joueur minimale hors debug (pause, vitesse x1/x2/x4, resume cycle).
- Telemetry de debug plus lisible (timeline courte + filtres par espece).

## v0.3
Objectif: ajouter de la profondeur strategique et de la lisibilite causale.

Contenu `v0.3`:
- Co-evolution plus marquee proie/predateur.
- Traits genetiques multi-axes avec compromis explicites.
- Debut de speciation (separation de lignees sous conditions).
- Outils d'influence joueur (pressions selectives controlees).
- Rapport causal post-cycle (pourquoi une lignee monte ou s'effondre).
- Objectifs de partie (stabilite, diversite, dominance).
- Equilibrage avance anti-strategie dominante.

## Long terme
Objectif: etendre l'echelle et la richesse sans perdre la lisibilite.

Contenu `long terme`:
- Monde multi-biomes large echelle.
- Migration inter-zones et niches complexes.
- Comportements appris/transmis plus sophistiques.
- Morphologie utilitaire visible et impactante.
- Directeur systemique avance avec arcs d'evenements.
- Outils de replay/analyse complets.
- Scenarios de campagne et meta-progression.

## Classement "tout le reste" par module
`simulation`
- MVP: boucle tick stable + vitesse normale.
- v0.2: controle de vitesse + pause fiable + stabilisation perf.
- v0.3: pipelines d'evenements plus riches.
- long terme: optimisation large echelle / parallelisation avancee.

`ai`
- MVP: deplacement, fuite, chasse, reproduction basique.
- v0.2: archetypes comportementaux + evenements simples.
- v0.3: explication causale + adaptation plus fine.
- long terme: comportements appris complexes.

`genetics`
- MVP: mutation simple sur quelques traits numeriques.
- v0.2: contraintes de viabilite mieux bornees.
- v0.3: compromis multi-traits + debut speciation.
- long terme: modele genetique etendu et plus expressif.

`creatures`
- MVP: cycle de vie minimal (naissance, survie, mort).
- v0.2: roles ecologiques differencies.
- v0.3: interactions sociales simples.
- long terme: comportements collectifs avances.

`world`
- MVP: carte unique + ressources nourriture.
- v0.2: cycles environnementaux et evenements locaux.
- v0.3: variations regionales influencant l'evolution.
- long terme: monde multi-biomes et dynamique profonde.

`player`
- MVP: lancer/pause/restart + observation.
- v0.2: controle de vitesse + options de session.
- v0.3: outils de pression selective.
- long terme: meta-progression et scenarios.

`ui`
- MVP: overlay debug minimal (stats, compteurs, graph simple).
- v0.2: HUD joueur de base.
- v0.3: panneaux explicatifs causaux.
- long terme: visualisations avancees + replay.

`save`
- MVP: hors scope.
- v0.2: sauvegarde/chargement version 1.
- v0.3: migration de format et robustesse.
- long terme: compatibilite longue duree et compression avancee.

`debug_tools`
- MVP: compteurs de base + logs essentiels.
- v0.2: filtres et timeline courte.
- v0.3: checks d'invariants et rapports automatiques.
- long terme: observabilite complete orientee equilibrage.
