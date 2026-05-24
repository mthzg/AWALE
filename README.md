# Awalé

Projet Python orienté objet pour le jeu Awalé

Ce projet implémente les règles du jeu Awalé ainsi que plusieurs types de joueurs :

- joueur humain ;
- bot aléatoire ;
- bot glouton ;
- MinMax ;
- MCTS.

## architecture

awale/
├── core.py          # Classe Awale : règles du jeu, plateau, scores, coups licites
├── players.py       # Joueurs : Human, StupidBot, GreedyTactic, MinMax, Sommet, MCTS
├── gui.py           # Interface graphique Tkinter
├── match.py         # Lancement et déroulement d'une partie
├── tournament.py    # Statistiques d'affrontement entre joueurs

docs/
└── documentation.md # Documentation technique du projet

main.py             # Interface en ligne de commande
README.md           # Présentation du projet et commandes d'utilisation


## Joueurs disponibles

human = Joueur humain : sélection d'une case à la souris ou au clavier =                              
random = Bot aléatoire : choisit un coup légal au hasard
greedy = Bot glouton : choisit le meilleur coup immédiat selon la position actuelle
minmax-score = IA MinMax avec heuristique basée principalement sur le score
minmax-mobility = IA MinMax avec heuristique basée sur la mobilité et les coups disponibles
mcts = IA Monte Carlo Tree Search avec simulations aléatoires

# Lancer une partie avec interface graphique

Pour lancer une partie avec l'interface graphique, il faut ajouter l'option --gui.

Le joueur P0 correspond à la rangée du bas.

Le joueur P1 correspond à la rangée du haut.

## Humain contre bot aléatoire

py main.py play --p0 human --p1 random --gui

# Faire jouer les IA entre elles avec interface graphique

## Random contre Greedy

py main.py play --p0 random --p1 greedy --gui

# Lancer une partie sans interface graphique

Pour lancer une partie en console, il suffit d'enlever l'option --gui.

## Humain contre bot aléatoire

py main.py play --p0 random --p1 greedy


# Comment jouer avec l'interface graphique

Après avoir lancé une commande avec --gui, une fenêtre Tkinter s'ouvre.

Le plateau contient deux rangées :

- la rangée du bas correspond au joueur P0 ;
- la rangée du haut correspond au joueur P1.

Pour jouer :

1. attendre que ce soit le tour du joueur humain ;
2. cliquer sur une case de son côté du plateau ;
3. le bot joue automatiquement après le coup humain ;
4. continuer jusqu'à la fin de la partie ;
5. consulter le score affiché en bas de la fenêtre.

Si une case est vide ou si le coup est interdit, le clic est ignoré.

# Lancer les statistiques de tournoi

Le mode tournoi permet de faire jouer automatiquement plusieurs parties entre les différents joueurs.

## Test avec 10 parties

py main.py tournament --games 10

