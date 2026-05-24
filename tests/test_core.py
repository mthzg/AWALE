from awale import Awale, GreedyTactic, MinMax, StupidBot, play_game


def test_initial_state():
    game = Awale()
    assert game.board() == [4] * 12
    assert game.scores() == (0, 0)
    assert game.legal_moves() == [0, 1, 2, 3, 4, 5]


def test_play_changes_turn():
    game = Awale()
    game.play(0)
    assert game.current_player() == 1
    assert sum(game.board()) + sum(game.scores()) == 48


def test_bot_game_finishes():
    winner, scores, _ = play_game(StupidBot(), GreedyTactic(), max_turns=300)
    assert winner in (-1, 0, 1)
    assert 0 <= sum(scores) <= 48


def test_minmax_returns_legal_move():
    game = Awale()
    bot = MinMax(depth=2, heuristic="score")
    assert bot.choose_move(game) in game.legal_moves()
