import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

pygame.init()

from src.bubble import Bubble
from src.grid import Grid
from src.settings import BUBBLE_RADIUS, COLORS, COLS, ROWS


def make_empty_grid() -> Grid:
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    return Grid(board, first_row_shifted=True)


def test_add_row_returns_false_when_bottom_not_reached():
    grid = make_empty_grid()
    reached = grid.add_row()
    assert reached is False
    assert not grid.reached_bottom()
    assert any(b is not None for b in grid.board[0])


def test_add_row_returns_true_when_bubble_reaches_bottom():
    grid = make_empty_grid()
    # Place a bubble at row ROWS - 2
    bubble = Bubble(COLORS[0], ROWS - 2, 0, grid.grid_to_pixel(ROWS - 2, 0), BUBBLE_RADIUS)
    grid.board[ROWS - 2][0] = bubble

    reached = grid.add_row()
    assert reached is True
    assert grid.reached_bottom()
    assert grid.board[ROWS - 1][0] is not None
    assert grid.board[ROWS - 1][0].row == ROWS - 1


def test_add_row_does_not_drop_bubble_when_already_at_bottom():
    grid = make_empty_grid()
    # Place a bubble already at bottom row
    bubble = Bubble(COLORS[0], ROWS - 1, 0, grid.grid_to_pixel(ROWS - 1, 0), BUBBLE_RADIUS)
    grid.board[ROWS - 1][0] = bubble

    reached = grid.add_row()
    assert reached is True
    # Bubble must not have disappeared!
    assert grid.board[ROWS - 1][0] is bubble
    assert grid.reached_bottom()
