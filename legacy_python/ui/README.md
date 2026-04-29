# ui

## Responsabilite
Afficher l'etat du jeu, collecter les inputs utilisateur et presenter les retours de simulation et de debug de maniere lisible.

## Dependances
- `player` (intentions et etat joueur)
- `simulation` (snapshots et rapports de cycle)
- `debug_tools` (overlays et panels optionnels)

## Interfaces publiques
- `Ui.render_frame(view_model)`
- `Ui.bind_input(input_device_stream)`
- `Ui.show_cycle_report(cycle_report)`
- `Ui.show_alert(alert_payload)`
- `Ui.toggle_debug_overlay(flag)`

## Ce qu'il n'a pas le droit de faire
- Modifier directement la simulation metier sans passer par `player` ou `simulation`.
- Faire de la persistance directe sur disque.
- Contenir des regles d'equilibrage IA/genetique.
- Executer des traitements lourds de simulation dans le thread de rendu.
