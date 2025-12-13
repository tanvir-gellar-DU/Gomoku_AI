from __future__ import annotations

import argparse
import tkinter as tk
from typing import Optional
import os

try:
    import pygame
    _PYGAME_AVAILABLE = True
except Exception:
    pygame = None
    _PYGAME_AVAILABLE = False

from .board import Board
from .engine import Engine


class GomokuGUI:
    def __init__(
        self,
        size: int = 15,
        cell: int = 48,
        max_depth: int = 3,
        time_limit: float = 2.0,
        simulate: bool = False,
        move_delay: int = 450,
    ):
        self.size = size
        self.board = Board(size=size)
        self.engine = Engine(max_depth=max_depth, time_limit=time_limit)
        self.current_player = 1  # 1 black, -1 white
        self.simulate = simulate
        self.move_delay = move_delay
        self.sim_after_id: Optional[str] = None
        self.end_popup: Optional[tk.Frame] = None
        self.game_started = False
        self.game_mode = "human_ai"  # human_ai | human_human | ai_ai(simulate)
        self.window = tk.Tk()
        self.window.title("Gomoku AI")
        self.window.configure(bg="#1f1f1f")
        self.window.attributes("-fullscreen", True)
        self.window.bind("<Escape>", self._exit_fullscreen)
        default_status = "Simulation: black vs white" if simulate else "Turn: Human"
        self.status = tk.StringVar(value=default_status)

        # sound support (optional)
        self._sounds = {}
        self._pygame = pygame if _PYGAME_AVAILABLE else None
        self._init_sounds()

        # Fit the board to the screen while keeping generous cell size
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        max_board_px = min(screen_w, screen_h) - 120
        self.cell = max(int(max_board_px / self.size), cell, 24)
        self.margin = self.cell // 2
        board_px = self.margin * 2 + (self.size - 1) * self.cell

        # Start and game frames
        self.start_frame = tk.Frame(self.window, bg="#1f1f1f")
        self.game_frame = tk.Frame(self.window, bg="#1f1f1f")

        # Game UI
        top_bar = tk.Frame(self.game_frame, bg="#1f1f1f")
        top_bar.pack(side="top", fill="x", pady=8)
        tk.Label(
            top_bar,
            text="Gomoku AI",
            fg="#ffcc66",
            bg="#1f1f1f",
            font=("Helvetica", 26, "bold"),
        ).pack(side="left", padx=16)
        tk.Button(top_bar, text="New Game", command=self.reset_game).pack(side="right", padx=8)
        tk.Button(top_bar, text="Quit", command=self._return_to_start).pack(side="right", padx=8)

        self.canvas = tk.Canvas(
            self.game_frame,
            width=board_px,
            height=board_px,
            bg="#f5d9a6",
            highlightthickness=0,
        )
        self.canvas.pack(expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        status_bar = tk.Frame(self.game_frame, bg="#1f1f1f")
        status_bar.pack(side="bottom", fill="x", pady=6)
        tk.Label(
            status_bar,
            textvariable=self.status,
            fg="white",
            bg="#1f1f1f",
            font=("Helvetica", 16, "bold"),
        ).pack()

        self._draw_grid()
        self._build_start_screen()
        self._show_start_screen()

    def _draw_grid(self):
        start = self.margin
        end = self.margin + (self.size - 1) * self.cell
        for i in range(self.size):
            pos = start + i * self.cell
            width = 3 if i % 5 == 0 else 2
            self.canvas.create_line(start, pos, end, pos, width=width, fill="#5e3e12")
            self.canvas.create_line(pos, start, pos, end, width=width, fill="#5e3e12")

        # Star points for standard 15x15 layout
        if self.size >= 11:
            points = [
                (3, 3),
                (3, self.size - 4),
                (self.size - 4, 3),
                (self.size - 4, self.size - 4),
                (self.size // 2, self.size // 2),
            ]
            for px, py in points:
                cx, cy = self._board_to_canvas((px, py))
                r = self.cell * 0.08
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#5e3e12", outline="")

    def _board_to_canvas(self, pos):
        x, y = pos
        return self.margin + y * self.cell, self.margin + x * self.cell

    def on_click(self, event):
        if self.simulate:
            return
        x = event.y // self.cell
        y = event.x // self.cell
        player = self.current_player
        color = "black" if player == 1 else "white"
        if self.game_mode == "human_ai" and player != 1:
            return
        if not self.board.place_move((x, y), player):
            self.status.set("Invalid move. Try again.")
            return
        self._draw_stone((x, y), color)
        # play move sound
        try:
            self._play_move_sound(player)
        except Exception:
            pass
        if self._check_end():
            return
        self.current_player *= -1
        if self.game_mode == "human_ai":
            self._update_turn_status()
            self.window.after(50, self._ai_move)
        else:
            self._update_turn_status()

    def _ai_move(self):
        move = self.engine.choose_move(self.board, -1)
        self.board.place_move(move, -1)
        self._draw_stone(move, "white")
        try:
            self._play_move_sound(-1)
        except Exception:
            pass
        if self._check_end():
            return
        self.current_player = 1
        self._update_turn_status()

    def _draw_stone(self, pos, color: str):
        cx, cy = self._board_to_canvas(pos)
        r = self.cell * 0.42
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")

    def _check_end(self) -> bool:
        win_line = self.board.get_winner_line()
        if win_line is not None:
            player, positions = win_line
            if self.game_mode == "human_ai":
                message = "You win!" if player == 1 else "AI wins!"
            else:
                message = "Black wins!" if player == 1 else "White wins!"
            self.status.set(message)
            self._draw_win_line(positions)
            # play end sound (win/lose)
            try:
                if self.game_mode == "human_ai":
                    # player == 1 means human won
                    if player == 1:
                        self._play_game_end_sound("win")
                    else:
                        self._play_game_end_sound("lose")
                else:
                    self._play_game_end_sound("win")
            except Exception:
                pass
            self._show_end_popup(message)
            return True
        if self.board.is_full():
            self.status.set("Draw!")
            try:
                self._play_game_end_sound("draw")
            except Exception:
                pass
            self._show_end_popup("Draw!")
            return True
        return False

    def _draw_win_line(self, positions):
        positions = sorted(positions)
        start = positions[0]
        end = positions[-1]
        sx, sy = self._board_to_canvas(start)
        ex, ey = self._board_to_canvas(end)
        offset = self.cell * 0.05
        self.canvas.create_line(
            sx,
            sy,
            ex,
            ey,
            width=self.cell * 0.15,
            fill="#d62828",
            capstyle=tk.ROUND,
        )

    def reset_game(self, schedule_sim: bool = True):
        self.board = Board(size=self.size)
        self.current_player = 1
        if self.simulate and self.game_mode == "ai_ai":
            self.status.set("Simulation: black vs white")
        else:
            self._update_turn_status()
        if self.sim_after_id is not None:
            self.window.after_cancel(self.sim_after_id)
            self.sim_after_id = None
        self._clear_end_popup()
        self.canvas.delete("all")
        self._draw_grid()
        if (
            schedule_sim
            and self.simulate
            and self.game_started
            and self.game_mode == "ai_ai"
        ):
            self._schedule_next_sim_move(initial=True)

    def _exit_fullscreen(self, *_):
        self.window.attributes("-fullscreen", False)

    def _schedule_next_sim_move(self, initial: bool = False):
        if self.sim_after_id is not None:
            self.window.after_cancel(self.sim_after_id)
        if initial:
            self.current_player = 1
            self.status.set("Simulation running (black to move)")
        self.sim_after_id = self.window.after(self.move_delay, self._sim_move)

    def _sim_move(self):
        if self._check_end():
            return
        player = self.current_player
        color = "black" if player == 1 else "white"
        move = self.engine.choose_move(self.board, player)
        placed = self.board.place_move(move, player)
        if not placed:
            self.status.set(f"Simulation stopped: no move for {color}")
            return
        self._draw_stone(move, color)
        try:
            self._play_move_sound(player)
        except Exception:
            pass
        if self._check_end():
            return
        self.current_player *= -1
        next_color = "black" if self.current_player == 1 else "white"
        self.status.set(f"Simulation running ({next_color} to move)")
        self._schedule_next_sim_move()

    def _build_start_screen(self):
        for widget in self.start_frame.winfo_children():
            widget.destroy()
        tk.Label(
            self.start_frame,
            text="Gomoku AI",
            fg="#ffd166",
            bg="#1f1f1f",
            font=("Helvetica", 48, "bold"),
            pady=40,
        ).pack()
        btn_frame = tk.Frame(self.start_frame, bg="#1f1f1f")
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="Human vs Human",
            width=14,
            height=2,
            command=lambda: self._start_game("human_human"),
        ).pack(side="left", padx=12)
        tk.Button(
            btn_frame,
            text="Human vs AI",
            width=14,
            height=2,
            command=lambda: self._start_game("human_ai"),
        ).pack(side="left", padx=12)
        tk.Button(btn_frame, text="Quit", width=14, height=2, command=self.window.destroy).pack(
            side="left", padx=12
        )

    def _show_start_screen(self):
        self.game_frame.pack_forget()
        self.start_frame.pack(expand=True)

    def _start_game(self, mode: str):
        self.start_frame.pack_forget()
        self.game_frame.pack(expand=True, fill="both")
        self.window.update_idletasks()  # render immediately for faster perceived transition
        self.game_started = True
        self.game_mode = mode
        self.simulate = mode == "ai_ai"
        self.reset_game(schedule_sim=True)

    def _clear_end_popup(self):
        if self.end_popup is not None:
            self.end_popup.destroy()
            self.end_popup = None

    def _update_turn_status(self):
        if self.simulate and self.game_mode == "ai_ai":
            next_color = "black" if self.current_player == 1 else "white"
            self.status.set(f"Simulation running ({next_color} to move)")
            return
        if self.game_mode == "human_ai":
            self.status.set("Turn: Human" if self.current_player == 1 else "Turn: AI")
        else:
            self.status.set("Turn: Black" if self.current_player == 1 else "Turn: White")

    def _show_end_popup(self, message: str):
        if self.end_popup is not None:
            return
        self.end_popup = tk.Frame(self.window, bg="#2b2b2b", bd=2, relief="ridge")
        self.end_popup.place(relx=0.5, y=self.margin // 2 + 20, anchor="n")
        tk.Label(
            self.end_popup,
            text=message,
            fg="white",
            bg="#2b2b2b",
            font=("Helvetica", 18, "bold"),
            padx=16,
            pady=8,
        ).pack(fill="x")
        btns = tk.Frame(self.end_popup, bg="#2b2b2b")
        btns.pack(fill="x", padx=12, pady=8)
        tk.Button(btns, text="Play Again", command=self.reset_game, width=12).pack(
            side="left", padx=6
        )
        tk.Button(btns, text="Quit", command=self._return_to_start, width=12).pack(
            side="right", padx=6
        )

    def _return_to_start(self):
        # Cancel any pending AI timers first
        if self.sim_after_id is not None:
            self.window.after_cancel(self.sim_after_id)
            self.sim_after_id = None

        # Instantly show the start screen for a snappier feel
        self.game_frame.pack_forget()
        self.start_frame.pack(expand=True)
        self.window.update_idletasks()

        # Reset state in the background after UI swap
        self.board = Board(size=self.size)
        self.current_player = 1
        self.simulate = False
        self.game_mode = "human_ai"
        self.game_started = False
        self._clear_end_popup()
        self.canvas.delete("all")
        self._draw_grid()
        self.status.set("Turn: Human")

    def run(self):
        self.window.mainloop()

    # Sound helpers
    def _init_sounds(self):
        """Initialize optional sounds. Looks for a `sounds/` folder next to this file
        with optional files: move.wav, win.wav, lose.wav, draw.wav. If pygame is not
        available or files are missing, fall back to tkinter bell.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "sounds")
        files = {
            "move": os.path.join(base_dir, "move.wav"),
            "win": os.path.join(base_dir, "win.wav"),
            "lose": os.path.join(base_dir, "lose.wav"),
            "draw": os.path.join(base_dir, "draw.wav"),
        }
        if self._pygame:
            try:
                if not self._pygame.mixer.get_init():
                    self._pygame.mixer.init()
            except Exception:
                # mixer init failed -> disable pygame usage
                self._pygame = None
        for k, path in files.items():
            if os.path.exists(path) and self._pygame:
                try:
                    self._sounds[k] = self._pygame.mixer.Sound(path)
                except Exception:
                    # skip loading this sound
                    pass

    def _play_sound(self, key: str):
        """Play a loaded sound by key or fall back to a short bell if unavailable."""
        snd = self._sounds.get(key)
        if snd and self._pygame:
            try:
                snd.play()
                return
            except Exception:
                pass
        # final fallback: a short system bell
        try:
            self.window.bell()
        except Exception:
            pass

    def _play_move_sound(self, player: int):
        # optionally play different move tones for black/white in future; use same for now
        self._play_sound("move")

    def _play_game_end_sound(self, result: str):
        # result should be one of: "win", "lose", "draw"
        if result == "win":
            self._play_sound("win")
        elif result == "lose":
            self._play_sound("lose")
        else:
            self._play_sound("draw")


def main():
    parser = argparse.ArgumentParser(description="Play Gomoku with a simple Tkinter GUI.")
    parser.add_argument("--size", type=int, default=15, help="Board size (default 15)")
    parser.add_argument("--cell", type=int, default=48, help="Cell size in pixels")
    parser.add_argument("--depth", type=int, default=3, help="Max search depth")
    parser.add_argument("--time", type=float, default=2.0, help="Time limit per AI move (seconds)")
    parser.add_argument("--simulate", action="store_true", help="Run AI vs AI simulator mode")
    parser.add_argument(
        "--delay",
        type=int,
        default=450,
        help="Delay between simulator moves in ms (only with --simulate)",
    )
    args = parser.parse_args()

    gui = GomokuGUI(
        size=args.size,
        cell=args.cell,
        max_depth=args.depth,
        time_limit=args.time,
        simulate=args.simulate,
        move_delay=args.delay,
    )
    gui.run()


if __name__ == "__main__":
    main()

