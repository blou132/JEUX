# AI SYSTEM

## Objectif du systeme
Produire des comportements credibles, emergents et lisibles pour les agents, tout en gardant un jeu strategique et comprehensible.

## Regles
1. L'IA agent decide localement (survie, nourriture, reproduction, migration).
2. L'IA ne triche pas : elle agit avec les memes contraintes que la simulation.
3. Les priorites de decision sont pilotees par etat interne + pression environnementale.
4. L'IA systemique (directeur) injecte des evenements credibles, jamais arbitraires.
5. L'IA d'assistance explique les causes probables des resultats au joueur.

## Donnees d'entree
- Etat du monde par tick/cycle (ressources, menaces, climat, densites).
- Traits des especes (capacites, besoins, vulnerabilites).
- Historique local (succes echec de comportements recents).
- Parametres de design (difficulte, intensite d'evenements, lisibilite voulue).

## Donnees de sortie
- Actions agents (deplacement, chasse, fuite, reproduction, cooperation).
- Evenements systemiques (maladie, secheresse, espece invasive).
- Explications de causalite pour UI et post-cycle report.
- Logs telemetry pour debug, equilibrage et replay.

## Interactions avec les autres systemes
- Respecte les contraintes de clartes et objectifs fixes dans `GAME_DESIGN.md`.
- Alimente `CORE_LOOP.md` avec des consequences visibles cycle apres cycle.
- Utilise `EVOLUTION_SYSTEM.md` pour faire emerger des comportements relies aux traits herites.

## Cas limites
- Oscillation de comportement (agents qui alternent indecisement entre deux actions).
- Convergence vers une strategie dominante qui casse la diversite.
- Surreaction du directeur systemique qui cree un sentiment d'injustice.
- Cout CPU trop eleve lorsque la population depasse la cible.

## Choses hors scope
- IA conversationnelle libre type PNJ narratif.
- Vision par ordinateur externe ou donnees utilisateurs reelles.
- Apprentissage en ligne non borne en production.
- Automatisation complete des decisions du joueur.
