# debug_tools

## Responsabilite
Fournir observation, profiling, tracing et outils de diagnostic pour comprendre la simulation et accelerer l'equilibrage.

## Dependances
- Peut lire `simulation`, `world`, `creatures`, `ai`, `genetics`, `player`, `save`, `ui`.

## Interfaces publiques
- `DebugTools.capture_tick_trace(tick_id)`
- `DebugTools.collect_metrics(scope_filter)`
- `DebugTools.run_invariant_checks(snapshot)`
- `DebugTools.export_diagnostics(format, range)`
- `DebugTools.register_overlay_channel(channel_id, provider)`

## Ce qu'il n'a pas le droit de faire
- Devenir un point de passage obligatoire pour la logique metier en production.
- Modifier silencieusement l'etat de simulation sans trace explicite.
- Ecrire des sauvegardes de jeu officielles.
- Ajouter des dependances cycliques structurelles entre modules.
