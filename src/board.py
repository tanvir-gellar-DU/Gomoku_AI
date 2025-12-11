from __future__ import annotations

from typing import List, Optional, Tuple

Position = Tuple[int, int]


class Board:
    """
    Immutable-ish board representation with helper methods for move legality
    and win detection. Stones are stored as integers:
    - 1 for black, -1 for white, 0 for empty.
    """

    def __init__(self, size: int = 15):
        self.size = size
        self.grid: List[List[int]] = [[0 for _ in range(size)] for _ in range(size)]
        self.moves: List[Position] = []

    def clone(self) -> "Board":
        new_board = Board(self.size)
        new_board.grid = [row[:] for row in self.grid]
        new_board.moves = self.moves[:]
        return new_board

    def in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size

    def is_empty(self, pos: Position) -> bool:
        x, y = pos
        return self.grid[x][y] == 0

    def place_move(self, pos: Position, player: int) -> bool:
        if not self.in_bounds(pos) or not self.is_empty(pos):
            return False
        x, y = pos
        self.grid[x][y] = player
        self.moves.append(pos)
        return True

    def undo_move(self) -> None:
        if not self.moves:
            return
        x, y = self.moves.pop()
        self.grid[x][y] = 0

    def last_move(self) -> Optional[Position]:
        return self.moves[-1] if self.moves else None

    def is_full(self) -> bool:
        return all(cell != 0 for row in self.grid for cell in row)

    def get_winner(self) -> Optional[int]:
        result = self.get_winner_line()
        return result[0] if result else None

    def get_winner_line(self) -> Optional[Tuple[int, List[Position]]]:
        """
        Returns (player, positions) for the winning sequence if present,
        otherwise None.
        """
        if not self.moves:
            return None
        x, y = self.moves[-1]
        player = self.grid[x][y]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            line = [(x, y)]
            line = self._collect_dir(x, y, dx, dy, player, line)
            line = self._collect_dir(x, y, -dx, -dy, player, line)
            if len(line) >= 5:
                # Sort line from start to end for consistency
                line.sort()
                return player, line
        return None

    def _count_dir(self, x: int, y: int, dx: int, dy: int, player: int) -> int:
        count = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == player:
            count += 1
            nx += dx
            ny += dy
        return count

    def _collect_dir(
        self, x: int, y: int, dx: int, dy: int, player: int, acc: List[Position]
    ) -> List[Position]:
        nx, ny = x + dx, y + dy
        while 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == player:
            acc.append((nx, ny))
            nx += dx
            ny += dy
        return acc

    def generate_moves(self, radius: int = 2) -> List[Position]:
        """
        Generate candidate moves near existing stones to reduce branching.
        """
        if not self.moves:
            mid = self.size // 2
            return [(mid, mid)]

        xs = [x for x, _ in self.moves]
        ys = [y for _, y in self.moves]
        min_x, max_x = max(min(xs) - radius, 0), min(max(xs) + radius, self.size - 1)
        min_y, max_y = max(min(ys) - radius, 0), min(max(ys) + radius, self.size - 1)

        candidates = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if self.grid[x][y] != 0:
                    continue
                if self._has_neighbor((x, y), radius):
                    candidates.append((x, y))
        return candidates

    def _has_neighbor(self, pos: Position, radius: int) -> bool:
        px, py = pos
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = px + dx, py + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] != 0:
                    return True
        return False

    def __str__(self) -> str:
        header = "   " + " ".join(f"{i:2}" for i in range(self.size))
        rows = []
        for i, row in enumerate(self.grid):
            symbols = []
            for cell in row:
                if cell == 1:
                    symbols.append("X ")
                elif cell == -1:
                    symbols.append("O ")
                else:
                    symbols.append(". ")
            rows.append(f"{i:2} " + "".join(symbols))
        return "\n".join([header] + rows)

