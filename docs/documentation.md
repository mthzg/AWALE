# Documentation technique — Mini-projet Awalé

## 1. Objectif

Le projet implémente en Python le jeu Awalé dans sa variante Abapa. L'architecture est volontairement simple et séparée en modules courts. L'approche est orientée objet et les données internes du jeu sont encapsulées dans la classe `Awale`.

Les bonus ne sont pas inclus.

## 2. Architecture

```text
awale_project/
├── awale/
│   ├── core.py          # Règles et état du jeu
│   ├── players.py       # Joueurs humains et IA
│   ├── gui.py           # Interface graphique Tkinter
│   ├── match.py         # Boucle de partie
│   └── tournament.py    # Statistiques d'affrontement
├── main.py              # Point d'entrée CLI
├── tests/               # Tests simples
└── docs/documentation.md
```

Cette organisation garde un lien clair entre les responsabilités : règles, joueurs, affichage, orchestration et concours.

## 3. Structure de données

Le plateau est mémorisé dans une liste privée de 12 entiers :

- joueur 0 : cases `0` à `5` ;
- joueur 1 : cases `6` à `11` ;
- chaque case contient le nombre de graines présentes ;
- les scores capturés sont stockés dans une liste privée de deux entiers.

Attributs principaux de `Awale` :

- `__board` : état des 12 cases ;
- `__scores` : graines capturées par chaque joueur ;
- `__current_player` : joueur dont c'est le tour ;
- `__history` : historique pour pouvoir annuler un coup ;
- `__finished` : état de fin de partie.

Les accesseurs `board()` et `scores()` retournent des copies ou des tuples. Le code extérieur ne peut donc pas modifier directement l'état interne.

## 4. Classe `Awale`

Rôle : fournir toutes les méthodes nécessaires au déroulement d'une partie.

Méthodes principales :

- `legal_moves(player=None)` : retourne les coups licites ;
- `play(pit)` : joue un coup, sème les graines, applique les captures et change le joueur courant ;
- `copy()` : copie indépendante de l'état, utilisée par les IA ;
- `seeds_on_side(player)` : nombre de graines sur le côté d'un joueur ;
- `winner()` et `winner_by_score()` : détermination du vainqueur ;
- `finished()` : indique si la partie est terminée ;
- `pretty()` : affichage textuel utile au débogage.

### Règles implémentées

- Semis case par case dans le sens des index croissants, modulo 12.
- La case de départ est sautée si un tour complet est effectué.
- Capture sur le camp adverse si la dernière graine tombe dans une case contenant 2 ou 3 graines.
- Capture rétrograde des cases adverses contiguës contenant 2 ou 3 graines.
- Règle de famine : si l'adversaire n'a plus de graines, le joueur doit le nourrir lorsqu'un coup le permet.
- Une capture qui viderait complètement le camp adverse est annulée.
- Si un joueur ne peut plus jouer et ne peut plus être nourri, les graines restantes sont collectées et la partie se termine.

## 5. Joueurs

Toutes les classes de joueurs contiennent une instance de `Awale` via l'attribut protégé `_awale`, conformément à la contrainte du sujet. La méthode commune est `choose_move(game)`.

### `Human`

Le joueur humain utilise la GUI Tkinter. Les coups licites sont affichés comme boutons actifs ; les cases interdites sont désactivées.

### `StupidBot`

Choisit aléatoirement un coup parmi les coups licites. Il sert de joueur de référence faible.

### `GreedyTactic`

Tactique différente de MinMax et MCTS. Elle n'anticipe pas plusieurs coups. Pour chaque coup licite, elle simule uniquement le coup présent et choisit :

1. le plus grand gain immédiat ;
2. en cas d'égalité, la position gardant le plus de graines sur son propre camp ;
3. en dernier recours, un départage aléatoire.

Cette tactique est gloutonne et locale.

## 6. Classe `MinMax`

`MinMax` applique l'algorithme MinMax avec élagage alpha/bêta.

Paramètres :

- `depth` : profondeur maximale ;
- `heuristic` : nom de l'heuristique, `score` ou `mobility`.

Fonctionnement :

1. chaque coup licite est simulé dans une copie de `Awale` ;
2. l'arbre est exploré jusqu'à la profondeur fixée ou une fin de partie ;
3. alpha/bêta coupe les branches inutiles ;
4. le coup de meilleure valeur est choisi.

### Heuristique 1 : `score`

Objectif principal : maximiser l'écart de score capturé.

Formule simplifiée :

```text
5 * (score_joueur - score_adversaire)
+ 0.2 * (graines_camp_joueur - graines_camp_adversaire)
```

Cette heuristique favorise fortement les captures.

### Heuristique 2 : `mobility`

Objectif principal : conserver de bons choix de coups et éviter les positions bloquées.

Formule simplifiée :

```text
2 * écart_score
+ 1.5 * (nombre_coups_joueur - nombre_coups_adversaire)
+ 0.3 * écart_graines_sur_plateau
```

Elle est réellement différente de la première car elle valorise la mobilité, pas seulement les graines capturées.

## 7. Classe `Sommet`

`Sommet` modélise récursivement un nœud de l'arborescence de jeu pour MCTS.

Attributs :

- `_awale` : copie de l'état du jeu ;
- `__parent` : sommet parent ;
- `__move` : coup menant à ce sommet ;
- `__children` : fils déjà développés ;
- `__untried_moves` : coups non encore explorés ;
- `__visits` : nombre de visites ;
- `__wins` : score cumulé des simulations.

Méthodes principales :

- `expand()` : crée un enfant ;
- `best_child()` : sélection UCT ;
- `update()` : mise à jour statistique.

## 8. Classe `MCTS`

MCTS utilise quatre étapes :

1. sélection d'un sommet avec UCT ;
2. expansion d'un coup non encore essayé ;
3. simulation aléatoire jusqu'à la fin de partie ;
4. rétropropagation du résultat.

La politique de jeu pendant les simulations est aléatoire, comme demandé. La température UCT et le nombre d'itérations sont paramétrables.

## 9. Interface graphique

Le module `gui.py` utilise Tkinter, qui est autorisé par le sujet. La GUI reste volontairement simple :

- deux rangées de six boutons pour les cases ;
- affichage du joueur courant ;
- affichage des scores ;
- activation uniquement des coups licites.

## 10. Concours et statistiques

Le module `tournament.py` fournit :

- `run_duel(factory_a, factory_b, games)` ;
- `default_tournament(games_per_duel)`.

Les duels inclus couvrent notamment :

- `MinMax(score)` contre `StupidBot` ;
- `StupidBot` contre `GreedyTactic` ;
- `MCTS` contre `MinMax(mobility)` ;
- `GreedyTactic` contre `MinMax(score)`.

Les parties alternent le joueur qui commence, afin d'étudier l'influence du premier joueur.

## 11. Commandes utiles

Lancer une partie :

```bash
python main.py play --p0 human --p1 minmax-score
```

Lancer 100 parties par duel :

```bash
python main.py tournament --games 100
```

Tester rapidement :

```bash
python -m pytest
```
