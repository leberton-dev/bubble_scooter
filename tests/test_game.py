import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

pygame.init()

from src.bubble import Bubble
from src.game import Game
from src.settings import BUBBLE_RADIUS, COLORS, COLS, ROWS


def test_game_over_when_bubble_reaches_bottom_on_add_row():
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    game = Game(screen, clock)

    # Empty out grid board
    game.grid.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    # Put a bubble at ROWS - 2
    b = Bubble(COLORS[0], ROWS - 2, 0, game.grid.grid_to_pixel(ROWS - 2, 0), BUBBLE_RADIUS)
    game.grid.board[ROWS - 2][0] = b

    # Set misses_left to 1 so next miss triggers add_row
    game.misses_left = 1

    # Simulate miss by directly calling resolve_shot on empty cell without matching
    # or simulate resolve_shot with no cluster
    game.resolve_shot(0, 0)

    # Game should be lost because bubble was pushed to bottom row, and NOT dropped!
    assert game.state == "lost"
    assert game.grid.reached_bottom()
    assert game.grid.board[ROWS - 1][0] is not None
