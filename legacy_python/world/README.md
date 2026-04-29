# world

## Responsabilite
Maintenir l'etat du monde (biomes, ressources, climat, topologie, evenements environnementaux) et fournir un contexte fiable a la simulation.

## Dependances
- Aucune dependance gameplay obligatoire.

## Interfaces publiques
- `World.initialize(world_seed, world_config)`
- `World.step_environment(delta_time)`
- `World.apply_event(event_payload)`
- `World.query_region(region_id)`
- `World.get_global_state()`

## Ce qu'il n'a pas le droit de faire
- Executer la logique de decision IA.
- Gerer la saisie joueur ou les interactions UI.
- Geler/relancer la simulation globale (delegue a `simulation`).
- Serialiser lui-meme les sauvegardes sur disque.
