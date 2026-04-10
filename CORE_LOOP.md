# CORE LOOP

## Objectif du systeme
Transformer la simulation evolutive en decisions repetables, lisibles et strategiques pour le joueur.

## Regles
1. Le loop suit 5 etapes fixes : observer, decider, simuler, analyser, reajuster.
2. Chaque cycle doit produire au moins un signal clair (gain, perte, adaptation, crise).
3. Les actions du joueur modifient des pressions, pas des resultats garantis.
4. Le cout d'une action doit etre visible avant validation (risque, delai, impact probable).
5. Chaque fin de cycle doit proposer des options strategiques pour le cycle suivant.

## Donnees d'entree
- Etat courant du monde (populations, ressources, climat, niches).
- Historique recent des cycles precedents.
- Actions choisies par le joueur.
- Parametres de difficulte et objectifs de partie.

## Donnees de sortie
- Nouvel etat du monde apres simulation.
- Rapport de cycle (survie, extinctions, bifurcations, stress ecologique).
- Opportunites et menaces pour la prochaine decision.
- Metriques de progression (diversite, stabilite, dominance, resilience).

## Interactions avec les autres systemes
- Consomme les decisions de `GAME_DESIGN.md` sur la clarte et la cadence.
- Declenche `AI_SYSTEM.md` pour comportements d'agents et evenements systemiques.
- Declenche `EVOLUTION_SYSTEM.md` pour herite, mutation et selection.

## Cas limites
- Extinction totale precoce de l'ecosysteme.
- Effet boule de neige irreversible apres une mauvaise decision.
- Trop peu de changement entre deux cycles (loop percu comme statique).
- Trop de volatilite rendant les actions du joueur non lisibles.

## Choses hors scope
- Animation/cinematique de presentation.
- Reglages visuels de l'interface.
- IA de dialogue narratif.
- Economie meta hors partie (battle pass, boutique, etc.).
