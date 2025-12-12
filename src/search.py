from __future__ import annotations

import math
import time
from typing import List, Optional, Tuple

from .board import Board, Position
from .evaluation import evaluate


class SearchResult:
    def __init__(self, move: Optional[Position], value: int, depth: int):
        self.move = move
        self.value = value
        self.depth = depth


def minimax(
    board: Board,
    depth: int,
    alpha: int,
    beta: int,
    maximizing: bool,
    player: int,
    start_time: float,
    time_limit: float,
) -> Tuple[int, Optional[Position]]:
    """
    Depth-limited minimax search with alpha-beta pruning.
    Returns (score, best_move).
    """
    winner = board.get_winner()
    if winner is not None:
        return (math.inf if winner == player else -math.inf, None)

    if depth == 0 or board.is_full() or time.time() - start_time >= time_limit:
        return evaluate(board, player), None

    best_move: Optional[Position] = None
    moves = _order_moves(board, player if maximizing else -player)

    if maximizing:
        value = -math.inf
        for move in moves:
            if not board.place_move(move, player):
                continue
            score, _ = minimax(board, depth - 1, alpha, beta, False, player, start_time, time_limit)
            board.undo_move()
            if score > value:
                value = score
                best_move = move
            alpha = max(alpha, value)
            if beta <= alpha or time.time() - start_time >= time_limit:
                break
        return value, best_move
    else:
        value = math.inf
        opp = -player
        for move in moves:
            if not board.place_move(move, opp):
                continue
            score, _ = minimax(board, depth - 1, alpha, beta, True, player, start_time, time_limit)
            board.undo_move()
            if score < value:
                value = score
                best_move = move
            beta = min(beta, value)
            if beta <= alpha or time.time() - start_time >= time_limit:
                break
        return value, best_move


def iterative_deepening(
    board: Board, player: int, max_depth: int = 4, time_limit: float = 2.0
) -> SearchResult:
    """
    Iterative deepening wrapper that keeps the best result found within time.
    """
    start = time.time()
    best = SearchResult(move=None, value=-math.inf, depth=0)
    for depth in range(1, max_depth + 1):
        remaining = time_limit - (time.time() - start)
        if remaining <= 0:
            break
        value, move = minimax(
            board, depth, -math.inf, math.inf, True, player, start, time_limit
        )
        if move is not None:
            best = SearchResult(move=move, value=value, depth=depth)
        # Early exit on winning line
        if value == math.inf:
            break
    return best


def _order_moves(board: Board, player: int) -> List[Position]:
    """
    Order moves by a shallow heuristic to improve pruning.
    """
    candidates = board.generate_moves(radius=2)
    scored = []
    for move in candidates:
        if board.place_move(move, player):
            score = evaluate(board, player)
            board.undo_move()
            scored.append((score, move))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [m for _, m in scored]

