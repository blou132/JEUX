# creatures

## Responsabilite
Representer les creatures (etat, besoins, cycle de vie, capacites) et appliquer les transitions d'etat individuelles.

## Dependances
- `genetics` (traits exprimes)
- `world` (terrain, ressources, contraintes locales)

## Interfaces publiques
- `Creatures.spawn(species_id, genome, spawn_context)`
- `Creatures.update_states(actions_batch, world_delta)`
- `Creatures.resolve_life_cycle(delta_time)`
- `Creatures.get_population_snapshot()`
- `Creatures.remove_dead_entities()`

## Ce qu'il n'a pas le droit de faire
- Evaluer la strategie globale IA (delegue a `ai`).
- Modifier directement la carte du monde (delegue a `world`).
- Prendre des decisions de sauvegarde (delegue a `save`).
- Afficher des widgets UI.
