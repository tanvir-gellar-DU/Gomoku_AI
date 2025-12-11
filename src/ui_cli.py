from __future__ import annotations

import argparse

from .board import Board
from .engine import Engine


def parse_move(inp: str, size: int):
    parts = inp.strip().split()
    if len(parts) != 2:
        raise ValueError("Enter move as: row col")
    x, y = int(parts[0]), int(parts[1])
    if not (0 <= x < size and 0 <= y < size):
        raise ValueError(f"Coordinates must be in range [0,{size-1}]")
    return x, y


def play_cli(size: int = 15, max_depth: int = 4, time_limit: float = 2.0):
    board = Board(size=size)
    engine = Engine(max_depth=max_depth, time_limit=time_limit)
    current_player = 1  # 1 = human (black), -1 = AI

    print("Gomoku CLI - you are X (black). Input as: row col")
    while True:
        print(board)
        winner = board.get_winner()
        if winner is not None:
            print("You win!" if winner == 1 else "AI wins!")
            break
        if board.is_full():
            print("Draw!")
            break

        if current_player == 1:
            try:
                move_input = input("Your move: ")
                move = parse_move(move_input, size)
                if not board.place_move(move, current_player):
                    print("Invalid move. Try again.")
                    continue
            except Exception as exc:  # noqa: BLE001
                print(f"Error: {exc}")
                continue
        else:
            print("AI thinking...")
            move = engine.choose_move(board, current_player)
            board.place_move(move, current_player)
            print(f"AI plays: {move[0]} {move[1]}")

        current_player *= -1


def main():
    parser = argparse.ArgumentParser(description="Play Gomoku against an AI.")
    parser.add_argument("--size", type=int, default=15, help="Board size (default 15)")
    parser.add_argument("--depth", type=int, default=4, help="Max search depth")
    parser.add_argument("--time", type=float, default=2.0, help="Time limit per move (seconds)")
    args = parser.parse_args()

    play_cli(size=args.size, max_depth=args.depth, time_limit=args.time)


if __name__ == "__main__":
    main()

