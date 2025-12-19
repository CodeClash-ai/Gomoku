#!/usr/bin/env python3
"""
Gomoku Starter Bot
A simple bot with basic strategy for CodeClash.
"""

import random


def get_move(board: list, color: str) -> tuple:
    """
    Get a move for the current board state.

    Strategy:
    1. Win if possible (complete 5 in a row)
    2. Block opponent's winning move
    3. Play near existing stones
    4. Fallback to center or random
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

    # 3. Play near existing stones (simple approach)
    neighbors = get_neighbor_moves(board, board_size)
    if neighbors:
        return random.choice(neighbors)

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


def get_neighbor_moves(board: list, board_size: int) -> list:
    """Get all empty positions adjacent to existing stones."""
    neighbors = []
    for x in range(board_size):
        for y in range(board_size):
            if board[x][y] == 0 and has_neighbor(board, x, y, board_size):
                neighbors.append((x, y))
    return neighbors


def has_neighbor(board: list, x: int, y: int, board_size: int) -> bool:
    """Check if position has any neighboring stones (distance 1 only)."""
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                if board[nx][ny] != 0:
                    return True
    return False
