#!/usr/bin/env python3
"""
Gomoku Starter Bot
A functional bot with basic strategy for CodeClash.
"""

import random


def get_move(board: list, color: str) -> tuple:
    """
    Get the best move for the current board state.

    Strategy:
    1. Win if possible (complete 5 in a row)
    2. Block opponent's winning move
    3. Extend own lines / block opponent's threats
    4. Prefer center and positions near existing stones
    """
    board_size = len(board)
    my_stone = 1 if color == "black" else 2
    opp_stone = 2 if color == "black" else 1

    # 1. Check for winning move
    win_move = find_winning_move(board, my_stone, board_size)
    if win_move:
        return win_move

    # 2. Block opponent's winning move
    block_move = find_winning_move(board, opp_stone, board_size)
    if block_move:
        return block_move

    # 3. Find best strategic move
    best_move = find_best_move(board, my_stone, opp_stone, board_size)
    if best_move:
        return best_move

    # 4. Fallback: center or random
    center = board_size // 2
    if board[center][center] == 0:
        return (center, center)

    empty = [(x, y) for x in range(board_size) for y in range(board_size) if board[x][y] == 0]
    return random.choice(empty) if empty else (0, 0)


def find_winning_move(board: list, stone: int, board_size: int) -> tuple | None:
    """Find a move that creates exactly 5 in a row."""
    for x in range(board_size):
        for y in range(board_size):
            if board[x][y] == 0:
                if is_winning_move(board, x, y, stone, board_size):
                    return (x, y)
    return None


def is_winning_move(board: list, x: int, y: int, stone: int, board_size: int) -> bool:
    """Check if placing stone at (x,y) creates exactly 5 in a row."""
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dx, dy in directions:
        count = 1

        # Count in positive direction
        nx, ny = x + dx, y + dy
        while 0 <= nx < board_size and 0 <= ny < board_size and board[nx][ny] == stone:
            count += 1
            nx += dx
            ny += dy

        # Count in negative direction
        nx, ny = x - dx, y - dy
        while 0 <= nx < board_size and 0 <= ny < board_size and board[nx][ny] == stone:
            count += 1
            nx -= dx
            ny -= dy

        if count == 5:
            return True

    return False


def find_best_move(board: list, my_stone: int, opp_stone: int, board_size: int) -> tuple | None:
    """Find the best strategic move based on position scoring."""
    best_score = -1
    best_moves = []

    for x in range(board_size):
        for y in range(board_size):
            if board[x][y] == 0:
                # Only consider positions near existing stones
                if not has_neighbor(board, x, y, board_size):
                    continue

                score = evaluate_position(board, x, y, my_stone, opp_stone, board_size)

                if score > best_score:
                    best_score = score
                    best_moves = [(x, y)]
                elif score == best_score:
                    best_moves.append((x, y))

    return random.choice(best_moves) if best_moves else None


def has_neighbor(board: list, x: int, y: int, board_size: int) -> bool:
    """Check if position has any neighboring stones."""
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                if board[nx][ny] != 0:
                    return True
    return False


def evaluate_position(board: list, x: int, y: int, my_stone: int, opp_stone: int, board_size: int) -> int:
    """Score a position based on strategic value."""
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    # Prefer center
    center = board_size // 2
    distance = abs(x - center) + abs(y - center)
    score += max(0, 10 - distance)

    for dx, dy in directions:
        my_count, opp_count, open_ends = count_line(board, x, y, dx, dy, my_stone, opp_stone, board_size)

        # Score based on line potential
        if my_count >= 4:
            score += 10000  # Almost winning
        elif my_count == 3 and open_ends == 2:
            score += 1000   # Open three
        elif my_count == 3:
            score += 100    # Closed three
        elif my_count == 2 and open_ends == 2:
            score += 50     # Open two
        elif my_count == 2:
            score += 10

        # Defensive scoring
        if opp_count >= 4:
            score += 5000   # Must block
        elif opp_count == 3 and open_ends == 2:
            score += 500    # Block open three
        elif opp_count == 3:
            score += 50
        elif opp_count == 2 and open_ends == 2:
            score += 25

    return score


def count_line(board: list, x: int, y: int, dx: int, dy: int, my_stone: int, opp_stone: int, board_size: int) -> tuple:
    """Count stones in a line and check if ends are open."""
    my_count = 0
    opp_count = 0
    open_ends = 0

    # Check positive direction
    nx, ny = x + dx, y + dy
    while 0 <= nx < board_size and 0 <= ny < board_size:
        if board[nx][ny] == my_stone:
            my_count += 1
        elif board[nx][ny] == opp_stone:
            opp_count += 1
            break
        else:
            open_ends += 1
            break
        nx += dx
        ny += dy

    # Check negative direction
    nx, ny = x - dx, y - dy
    while 0 <= nx < board_size and 0 <= ny < board_size:
        if board[nx][ny] == my_stone:
            my_count += 1
        elif board[nx][ny] == opp_stone:
            opp_count += 1
            break
        else:
            open_ends += 1
            break
        nx -= dx
        ny -= dy

    return (my_count, opp_count, open_ends)
