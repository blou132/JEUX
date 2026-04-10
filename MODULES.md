# MODULES

## Arborescence cible
```text
big jeux/
  simulation/
    README.md
  ai/
    README.md
  genetics/
    README.md
  creatures/
    README.md
  world/
    README.md
  player/
    README.md
  ui/
    README.md
  save/
    README.md
  debug_tools/
    README.md
```

## Regles de dependances (vue macro)
- `simulation` depend de: `world`, `creatures`, `ai`, `genetics`, `player`, `save`, `debug_tools`.
- `ai` depend de: `world`, `creatures`, `genetics`, `debug_tools` (optionnel).
- `genetics` depend de: `world` (contexte environnemental, lecture seule).
- `creatures` depend de: `genetics`, `world`.
- `world` ne depend d'aucun module gameplay.
- `player` depend de: `simulation` (commandes), `save` (profil et progression).
- `ui` depend de: `player`, `simulation`, `debug_tools` (overlay).
- `save` depend de: `world`, `creatures`, `genetics`, `player`, `simulation` (etat global).
- `debug_tools` peut lire tous les modules, mais ne doit pas imposer de logique metier.

## Regles transverses
1. Les modules echangent via interfaces publiques documentees.
2. Aucun acces direct disque hors module `save`, sauf logs techniques controles.
3. `ui` et `debug_tools` ne modifient pas la simulation metier sans passer par `player` ou `simulation`.
4. Aucune boucle de dependance cyclique n'est autorisee.
