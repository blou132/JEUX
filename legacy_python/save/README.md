# save

## Responsabilite
Serialiser, deserialiser et versionner l'etat de jeu pour garantir des sauvegardes robustes et compatibles.

## Dependances
- `world`
- `creatures`
- `genetics`
- `player`
- `simulation`

## Interfaces publiques
- `Save.create_snapshot(game_state, metadata)`
- `Save.write_slot(slot_id, snapshot)`
- `Save.read_slot(slot_id)`
- `Save.migrate_snapshot(snapshot, from_version, to_version)`
- `Save.validate_snapshot(snapshot)`

## Ce qu'il n'a pas le droit de faire
- Recalculer de la logique metier de simulation.
- Modifier le rendu UI.
- Injecter des commandes joueur.
- Cacher des erreurs de compatibilite de version sans signalement explicite.
