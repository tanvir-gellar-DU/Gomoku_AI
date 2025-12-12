from __future__ import annotations

from typing import List

from .board import Board

PATTERN_SCORES = {
    "11111": 100000,
    "011110": 10000,  # open four
    "211110": 5000,
    "111102": 5000,
    "10111": 5000,
    "11011": 5000,
    "11101": 5000,
    "011100": 1000,
    "001110": 1000,
    "011010": 1000,
    "010110": 1000,
    "001112": 200,
    "010112": 200,
    "011012": 200,
    "211100": 200,
    "211010": 200,
    "210110": 200,
    "00110": 50,
    "01100": 50,
    "01010": 50,
    "010010": 50,
}


def evaluate(board: Board, player: int) -> int:
    """
    Heuristic evaluation for the current board state from the perspective of `player`.
    Positive scores favor `player`, negative scores favor the opponent.
    """
    opponent = -player
    player_score = _evaluate_player(board, player)
    opp_score = _evaluate_player(board, opponent)
    return player_score - int(0.9 * opp_score)


def _evaluate_player(board: Board, player: int) -> int:
    total = 0
    lines = _extract_lines(board)
    for line in lines:
        encoded = _encode_line(line, player)
        total += _score_encoded_line(encoded)
    return total


def _encode_line(line: List[int], player: int) -> str:
    # Encode: current player -> 1, opponent -> 2, empty -> 0
    return "".join("1" if cell == player else "2" if cell == -player else "0" for cell in line)


def _score_encoded_line(encoded: str) -> int:
    score = 0
    for pattern, value in PATTERN_SCORES.items():
        idx = encoded.find(pattern)
        while idx != -1:
            score += value
            idx = encoded.find(pattern, idx + 1)
    return score


def _extract_lines(board: Board) -> List[List[int]]:
    lines: List[List[int]] = []
    size = board.size
    g = board.grid

    # Rows and columns
    for i in range(size):
        lines.append(g[i][:])
        lines.append([g[x][i] for x in range(size)])

    # Diagonals (top-left to bottom-right)
    for d in range(-size + 1, size):
        diag = [g[i][i - d] for i in range(max(d, 0), min(size + d, size))]
        if len(diag) >= 5:
            lines.append(diag)

    # Anti-diagonals (top-right to bottom-left)
    for d in range(0, 2 * size - 1):
        anti = []
        for x in range(size):
            y = d - x
            if 0 <= y < size:
                anti.append(g[x][y])
        if len(anti) >= 5:
            lines.append(anti)

    return lines

