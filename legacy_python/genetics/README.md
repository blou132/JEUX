# genetics

## Responsabilite
Definir le genome fonctionnel, appliquer mutation/recombinaison/heredite et produire les traits utilises par les autres systemes.

## Dependances
- `world` (pressions environnementales, lecture seule)

## Interfaces publiques
- `Genetics.create_initial_genome(species_template)`
- `Genetics.recombine(parent_a, parent_b, context)`
- `Genetics.mutate(genome, mutation_config, context)`
- `Genetics.express_traits(genome)`
- `Genetics.validate_viability(genome)`

## Ce qu'il n'a pas le droit de faire
- Decider des actions comportementales (delegue a `ai`).
- Piloter l'ordonnancement des ticks (delegue a `simulation`).
- Ecrire ou lire des sauvegardes directement.
- Faire du rendu ou de l'interaction joueur.
