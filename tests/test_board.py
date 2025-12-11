import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.board import Board  # noqa: E402
from src.engine import Engine  # noqa: E402
from src.evaluation import evaluate  # noqa: E402


def test_win_detection_row():
    b = Board(size=10)
    for y in range(5):
        assert b.place_move((0, y), 1)
    assert b.get_winner() == 1


def test_evaluation_prefers_winning():
    b = Board(size=10)
    for y in range(4):
        b.place_move((0, y), 1)
    score_before = evaluate(b, 1)
    b.place_move((0, 4), 1)
    score_after = evaluate(b, 1)
    assert score_after > score_before


def test_engine_returns_move():
    b = Board(size=10)
    engine = Engine(max_depth=2, time_limit=1.0)
    move = engine.choose_move(b, 1)
    assert move is not None
    assert b.in_bounds(move)

