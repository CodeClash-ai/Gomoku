#!/usr/bin/env python3
"""
Gomoku Game Engine
A simple Python engine for running Gomoku games between player bots.
Usage: python engine.py /path/to/player1.py /path/to/player2.py -r NUM_ROUNDS
"""

import argparse
import importlib.util
import os
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


@dataclass
class GomokuGame:
    """Represents a Gomoku game state."""
    board_size: int = 15
    board: list = field(default_factory=list)
    current_player: str = "black"
    winner: str | None = None
    history: list = field(default_factory=list)

    def __post_init__(self):
        if not self.board:
            self.board = [[0] * self.board_size for _ in range(self.board_size)]

    def make_move(self, x: int, y: int) -> bool:
        """Make a move. Returns True if valid, False otherwise."""
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False
        if self.board[x][y] != 0:
            return False
        if self.winner is not None:
            return False

        stone = 1 if self.current_player == "black" else 2
        self.board[x][y] = stone
        self.history.append((self.current_player, x, y))

        if self._check_win(x, y, stone):
            self.winner = self.current_player
            return True

        # Switch player
        self.current_player = "white" if self.current_player == "black" else "black"
        return True

    def _check_win(self, x: int, y: int, stone: int) -> bool:
        """Check if the last move resulted in a win."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1

            # Count in positive direction
            nx, ny = x + dx, y + dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx][ny] == stone:
                count += 1
                nx += dx
                ny += dy

            # Count in negative direction
            nx, ny = x - dx, y - dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx][ny] == stone:
                count += 1
                nx -= dx
                ny -= dy

            if count == 5:
                return True

        return False

    def is_full(self) -> bool:
        """Check if the board is full."""
        for row in self.board:
            if 0 in row:
                return False
        return True

    def get_board_copy(self) -> list:
        """Return a deep copy of the board."""
        return [row[:] for row in self.board]


_module_counter = 0


def load_player_module(path: str) -> Callable:
    """Load a player module and return its get_move function."""
    global _module_counter
    _module_counter += 1
    module_name = f"player_module_{_module_counter}"

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, 'get_move'):
        raise ValueError(f"Player module {path} must define a get_move(board, color) function")

    return module.get_move


def run_game(player1_path: str, player2_path: str, board_size: int = 15) -> dict:
    """Run a single game between two players."""
    # Load player modules
    try:
        player1_move = load_player_module(player1_path)
    except Exception as e:
        return {"winner": "player2", "error": f"Failed to load player1: {e}"}

    try:
        player2_move = load_player_module(player2_path)
    except Exception as e:
        return {"winner": "player1", "error": f"Failed to load player2: {e}"}

    # Randomly assign colors
    if random.random() < 0.5:
        players = {"black": (player1_move, "player1"), "white": (player2_move, "player2")}
    else:
        players = {"black": (player2_move, "player2"), "white": (player1_move, "player1")}

    game = GomokuGame(board_size=board_size)

    max_moves = board_size * board_size
    move_count = 0

    while game.winner is None and move_count < max_moves:
        move_fn, player_name = players[game.current_player]

        try:
            board_copy = game.get_board_copy()
            move = move_fn(board_copy, game.current_player)

            if not isinstance(move, (list, tuple)) or len(move) != 2:
                # Invalid move format - other player wins
                other_color = "white" if game.current_player == "black" else "black"
                _, winner_name = players[other_color]
                return {"winner": winner_name, "error": f"{player_name} returned invalid move format: {move}", "players": players}

            x, y = int(move[0]), int(move[1])

            if not game.make_move(x, y):
                # Invalid move - other player wins
                other_color = "white" if game.current_player == "black" else "black"
                _, winner_name = players[other_color]
                return {"winner": winner_name, "error": f"{player_name} made invalid move: ({x}, {y})", "players": players}

            move_count += 1

        except Exception as e:
            # Error in player code - other player wins
            other_color = "white" if game.current_player == "black" else "black"
            _, winner_name = players[other_color]
            return {"winner": winner_name, "error": f"{player_name} raised exception: {e}", "players": players}

    if game.winner:
        _, winner_name = players[game.winner]
        return {"winner": winner_name, "history": game.history, "players": players}
    else:
        return {"winner": "draw", "history": game.history, "players": players}


def write_game_log(game_num: int, result: dict, players: dict, player1_path: str, player2_path: str, output_dir: str = "."):
    """Write a detailed log file for a single game."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_filename = os.path.join(output_dir, f"log-{timestamp}.log")
    
    with open(log_filename, 'w') as f:
        # Write header with player assignments
        f.write(f"=== Gomoku Game Log (Game #{game_num}) ===\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\nPlayer Assignments:\n")
        
        for color in ["black", "white"]:
            _, player_name = players[color]
            player_path = player1_path if player_name == "player1" else player2_path
            f.write(f"  {color.upper()}: {player_name} ({player_path})\n")
        
        f.write(f"\nResult: {result['winner']} wins\n")
        
        if "error" in result:
            f.write(f"Error: {result['error']}\n")
        
        # Write move history
        if "history" in result:
            f.write(f"\nMove History ({len(result['history'])} moves):\n")
            f.write("-" * 50 + "\n")
            for i, (color, x, y) in enumerate(result["history"], 1):
                f.write(f"Move {i:3d}: {color:5s} -> ({x:2d}, {y:2d})\n")
        
        f.write("\n" + "=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Gomoku Game Engine')
    parser.add_argument('player1', help='Path to player 1 code (main.py)')
    parser.add_argument('player2', help='Path to player 2 code (main.py)')
    parser.add_argument('-r', '--rounds', type=int, default=10, help='Number of rounds to play')
    parser.add_argument('-b', '--board-size', type=int, default=15, help='Board size')
    parser.add_argument('-o', '--output-dir', type=str, default=None, help='Output directory for log files')
    args = parser.parse_args()

    scores = {"player1": 0, "player2": 0, "draw": 0}

    print(f"Running {args.rounds} games between:")
    print(f"  Player 1: {args.player1}")
    print(f"  Player 2: {args.player2}")
    print()

    for i in range(args.rounds):
        result = run_game(args.player1, args.player2, args.board_size)
        winner = result["winner"]
        scores[winner] = scores.get(winner, 0) + 1
        
        # Write detailed log for this game
        if args.output_dir and "players" in result:
            write_game_log(i + 1, result, result["players"], args.player1, args.player2, args.output_dir)

        if "error" in result:
            print(f"Game {i+1}: {winner} wins (error: {result['error']})")
        else:
            print(f"Game {i+1}: {winner} wins")

    print()
    print("FINAL_RESULTS")
    p1_name = os.path.basename(os.path.dirname(args.player1))
    p2_name = os.path.basename(os.path.dirname(args.player2))

    print(f"Bot_1_main: {scores['player1']} rounds won ({p1_name})")
    print(f"Bot_2_main: {scores['player2']} rounds won ({p2_name})")
    print(f"Draws: {scores['draw']}")


if __name__ == '__main__':
    main()
