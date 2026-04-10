# simulation

## Responsabilite
Piloter la boucle de simulation (ticks, ordonnancement des systemes, passage des etats) et garantir la coherence globale d'un cycle.

## Dependances
- `world`
- `creatures`
- `ai`
- `genetics`
- `player`
- `save`
- `debug_tools` (hooks optionnels)

## Interfaces publiques
- `SimulationEngine.start(config)`
- `SimulationEngine.step(delta_time)`
- `SimulationEngine.pause()`
- `SimulationEngine.resume()`
- `SimulationEngine.get_snapshot()`
- `SimulationEngine.apply_player_actions(actions_batch)`

## Ce qu'il n'a pas le droit de faire
- Afficher du rendu UI directement.
- Ecrire les sauvegardes directement sur disque sans passer par `save`.
- Encoder des regles metier propres a un module (ex: mutation genetique detaillee de `genetics`) au mauvais endroit.
- Contourner les interfaces publiques des autres modules.
