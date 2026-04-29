# player

## Responsabilite
Transformer les intentions du joueur en commandes valides pour la simulation, et porter l'etat joueur (objectifs, progression, preferences).

## Dependances
- `simulation` (envoi de commandes)
- `save` (profil et progression persistante)

## Interfaces publiques
- `Player.submit_command(command_payload)`
- `Player.validate_command(command_payload, sim_snapshot)`
- `Player.get_player_state(player_id)`
- `Player.apply_progression(delta_progress)`
- `Player.set_objective(objective_id)`

## Ce qu'il n'a pas le droit de faire
- Modifier directement les structures internes de `world`, `creatures`, `genetics` ou `ai`.
- Rendre l'interface visuelle.
- Court-circuiter les regles de simulation pour appliquer un effet instantane non valide.
- Ecrire directement des fichiers de sauvegarde.
