# GAME DESIGN

## Objectif du systeme
Definir le cadre global du jeu pour garder une direction claire entre fun, lisibilite et profondeur systemique.

## Regles
1. Toute feature doit servir la boucle principale : observer, intervenir, simuler, analyser, ajuster.
2. Le joueur agit par pressions selectives, pas par controle direct des individus.
3. Les consequences doivent etre persistantes et explicables.
4. La complexite ajoutee doit rester lisible via UI et telemetry.
5. Le scope priorise l'ecosysteme evolutif avant toute couche civilisationnelle.

## Donnees d'entree
- Vision produit (`VISION.md`).
- Plan de release (`RELEASE_PLAN.md`).
- Retours de playtest (frictions, moments fun, incomprehensions).
- Contraintes techniques (performance, outils, budget de production).
- Objectifs business et perimetre de release.

## Donnees de sortie
- Priorites de production (features must-have, should-have, later).
- Regles de design transverses (clarte, progression, difficulte).
- Backlog ordonne par valeur joueur et risque.
- Criteres d'acceptation gameplay pour validation interne.

## Interactions avec les autres systemes
- Aligne `CORE_LOOP.md` sur les objectifs de jeu et les criteres de fun.
- Definis les bornes de comportement de `AI_SYSTEM.md` (credibilite, lisibilite, difficulte).
- Fixe les objectifs de progression de `EVOLUTION_SYSTEM.md` (diversite, adaptation, resilience).

## Cas limites
- Une feature techniquement brillante mais sans impact sur le fun.
- Conflit entre realisme de simulation et comprehension joueur.
- Systeme emergent tres riche mais impossible a lire sans outil de debug.
- Pression de production qui pousse a du scope creep.

## Choses hors scope
- Implementation de bas niveau (algorithmes exacts, architecture moteur).
- Details narratifs complets (lore, script, dialogues).
- Contenu final de toutes especes/biomes.
- Plan marketing et communication externe.
