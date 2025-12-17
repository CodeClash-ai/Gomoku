# Gomoku Game Engine for CodeClash

This repository contains the game engine and bot examples for the **Gomoku** arena in [CodeClash](https://github.com/CodeClash-ai/CodeClash).

## Overview

Gomoku (Five in a Row) is a 2-player strategy board game:
- 15×15 board
- Black plays first
- Win by connecting 5 stones in a row (horizontally, vertically, or diagonally)

## Repository Structure

```
Gomoku/
├── engine.py           # Game engine - runs games between bots
├── main.py             # Starter bot implementation (edit this!)
└── README.md
```

## Quick Start

1. Edit `main.py` to implement your bot logic
2. Test locally:
   ```bash
   python engine.py main.py main.py -r 10
   ```
3. Submit to CodeClash!

## Bot Interface

Your bot must implement one function in `main.py`:

### `get_move(board, color) -> tuple[int, int]`

Choose where to place your stone.

**Parameters:**
- `board`: 2D list representing the board state
  - `0` = empty
  - `1` = black stone
  - `2` = white stone
- `color`: Your color - `"black"` or `"white"`

**Returns:** `(row, col)` tuple for your move (0-indexed)

## Starter Bot

The included `main.py` is a functional bot with basic strategy:

1. **Win**: Complete 5 in a row if possible
2. **Block**: Stop opponent from winning
3. **Evaluate**: Score positions based on line potential
4. **Center**: Prefer central positions

```python
def get_move(board, color):
    # 1. Check for winning move
    # 2. Block opponent's winning move
    # 3. Find best strategic move (open threes, etc.)
    # 4. Fallback to center or random
    ...
```

## Running Games Locally

Use `engine.py` to test your bot:

```bash
# Run 10 games between two agents
python engine.py agent1.py agent2.py -r 10

# With options
python engine.py agent1.py agent2.py -r 100 -b 15
```

**Options:**
- `-r, --rounds`: Number of games to play (default: 10)
- `-b, --board-size`: Board size (default: 15)

## Game Rules

- Black always plays first
- Players alternate placing one stone per turn
- First player to get **exactly 5** stones in a row wins
- Overlines (6 or more in a row) do **not** count as a win
- If the board fills up with no winner, it's a draw
- Invalid moves (out of bounds, occupied position) forfeit the game

## Strategy Tips

- Control the center early
- Look for winning moves (5 in a row)
- Block opponent's threats (4 in a row)
- Create double threats (two ways to win)

## License

MIT License - See CodeClash repository for details.
