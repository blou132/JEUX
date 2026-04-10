# EVOLUTION SYSTEM

## Objectif du systeme
Simuler une evolution heritable qui cree des adaptations utiles, des compromis et de la diversite observable a l'echelle des generations.

## Regles
1. Les traits heritables sont portes par un genome fonctionnel.
2. La mutation reste bornee par des plages viables definies par espece.
3. La selection depend de la survie et du succes reproductif en contexte.
4. Les compromis sont obligatoires (un gain sur un axe entraine un cout sur un autre).
5. Les changements evolutifs doivent etre mesurables sur timeline.

## Donnees d'entree
- Genomes parentaux et distribution des traits de population.
- Pressions du milieu (ressources, climat, predation, maladie).
- Parametres de mutation/recombinaison/speciation.
- Contraintes de viabilite biologique definies par design.

## Donnees de sortie
- Nouvelles generations avec genomes et traits mis a jour.
- Variations de frequences alleliques et distribution de phenotypes.
- Evenements macro (speciation locale, extinction, adaptation cle).
- Indicateurs de resilience et diversite genetique.

## Interactions avec les autres systemes
- Suit le cadre de progression et de lisibilite fixe dans `GAME_DESIGN.md`.
- Produit les changements utilises dans `CORE_LOOP.md` pour les bilans de cycle.
- Fournit a `AI_SYSTEM.md` des traits actualises qui influencent les comportements.

## Cas limites
- Derive genetique excessive sur population trop faible.
- Mutation cascade menant a effondrement brutal de viabilite.
- Stagnation evolutive dans un optimum local non fun.
- Explosion combinatoire des traits qui degrade performance et equilibrage.

## Choses hors scope
- Simulation biochimique molecule par molecule.
- Evolution culturelle/societale avancee type civilisation.
- Edition manuelle libre du genome par le joueur en temps reel.
- Validation scientifique exhaustive de toutes equations du modele.
