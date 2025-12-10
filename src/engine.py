from __future__ import annotations

import math
from typing import Optional, Tuple

from .board import Board, Position
from .search import SearchResult, iterative_deepening


class Engine:
    def __init__(self, max_depth: int = 4, time_limit: float = 2.0):
        self.max_depth = max_depth
        self.time_limit = time_limit

    def choose_move(self, board: Board, player: int) -> Position:
        result: SearchResult = iterative_deepening(
            board, player, max_depth=self.max_depth, time_limit=self.time_limit
        )
        if result.move is None:
            # Fallback: first available
            moves = board.generate_moves()
            if not moves:
                raise RuntimeError("No moves available")
            return moves[0]
        return result.move

    def set_limits(self, max_depth: Optional[int] = None, time_limit: Optional[float] = None):
        if max_depth is not None:
            self.max_depth = max_depth
        if time_limit is not None:
            self.time_limit = time_limit

