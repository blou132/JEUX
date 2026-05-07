# tools

## Responsabilite
Regrouper les scripts utilitaires d'analyse, de verification CI et d'export.

## Contenu principal
- `analyze_run_metrics_history.py`: resume et comparaison des run metrics.
- `collect_support_metrics_runtime.py`: collecte locale multi-runs Godot vers `outputs/ci/support_metrics_baseline.jsonl` ou `outputs/ci/support_metrics_current.jsonl`, avec mode diagnostic/probe runtime.
- `validate_support_metrics_runtime_files.py`: validation des fichiers runtime baseline/current avant comparaison (presence, JSONL lisible, lignes exploitables, warnings legacy).
- `run_support_metrics_runtime_pipeline.py`: pipeline local `collect -> validate -> compare -> decide` pour les metriques runtime support (rapports comparaison + decision heuristique).
- `decide_support_metrics_runtime_tuning.py`: protocole heuristique local de decision (`keep/revert/collect/investigate`) a partir du resume runtime baseline/current.
- `write_support_metrics_ci_summary.py`: generation rapports/summary CI support metrics.
- `simulate_support_metrics_ci.py`: simulation locale du chemin CI support metrics.
- `check_support_metrics_ci_fragments.py`: validation des fragments contractuels CI.
- `check_support_metrics_ci_health.py`: health check global de la chaine support metrics CI.

## Notes
- Outils de maintenance CI/debug uniquement; aucune modification directe du gameplay.
- Pour l'execution runtime avec Godot (checklist pratique v211), voir la section README: `Runtime Godot validation checklist for v211`.
- Pour diagnostiquer une collecte runtime sans nouvelles lignes exportees, voir la section README: `Diagnose runtime collection`.
- Pour verifier le handshake Godot runtime (probe), voir la section README: `Probe Godot runtime collection`.
- Pour tracer le chemin d'export runtime reel (latest/history), voir la section README: `Trace runtime export`.
- Pour forcer l'objectif runtime en debug/CI (ex: `rally_champion`), voir la section README: `Force runtime objective for support metrics`.
