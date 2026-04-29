# ai

## Responsabilite
Calculer les decisions des agents (creatures) et les evenements systemiques credibles a partir de l'etat courant du monde.

## Dependances
- `world` (lecture de contexte)
- `creatures` (etat des agents)
- `genetics` (traits herites utiles a la decision)
- `debug_tools` (telemetry optionnelle)

## Interfaces publiques
- `AiSystem.compute_agent_actions(world_state, creatures_state)`
- `AiSystem.compute_director_events(world_state, sim_metrics)`
- `AiSystem.explain_decisions(agent_id, tick_id)`
- `AiSystem.get_debug_metrics()`

## Ce qu'il n'a pas le droit de faire
- Modifier directement les genomes (delegue a `genetics`).
- Sauvegarder des donnees de jeu sur disque (delegue a `save`).
- Forcer des etats monde sans passer par `simulation`.
- Rendre des elements UI.
