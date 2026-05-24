# Mini-projet Awalé

Projet py orienté objet pour le jeu Awalé / Oware Abapa.

## Contenu

- `awale/core.py` : classe `Awale`, règles du jeu, plateau, scores, coups licites.
- `awale/players.py` : `Human`, `StupidBot`, `GreedyTactic`, `MinMax`, `Sommet`, `MCTS`.
- `awale/gui.py` : interface graphique Tkinter simple.
- `awale/match.py` : lancement d'une partie.
- `awale/tournament.py` : statistiques d'affrontement.
- `main.py` : interface en ligne de commande.
- `docs/documentation.md` : documentation technique demandée.

## Lancer une partie

human            # Joueur humain : sélection d'une case à la souris ou au clavier
random           # Bot aléatoire : choisit un coup légal au hasard
py main.py play --p0 human --p1 greedy --gui

greedy           # Bot glouton : choisit le meilleur coup immédiat selon la position actuelle
py main.py play --p0 human --p1 greedy --gui

minmax-score     # IA MinMax avec heuristique basée principalement sur le score
py main.py play --p0 human --p1 minmax-score --gui

minmax-mobility  # IA MinMax avec heuristique basée sur la mobilité et les coups disponibles
py main.py play --p0 human --p1 minmax-mobility --gui

mcts             # IA Monte Carlo Tree Search avec simulations aléatoires
py main.py play --p0 human --p1 mcts --gui

## Lancer les statistiques

```bash
py main.py tournament --games 100
```

## Tests rapides

```bash
py -m pytest
```