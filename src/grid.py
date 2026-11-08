from collections import deque
from dataclasses import dataclass
from math import sqrt
import queue
import random

import pygame

from src.bubble import Bubble
from src.projectile import Projectile
from src.settings import BUBBLE_RADIUS, COLORS, COLS, ROWS, START_ROWS


@dataclass()
class Grid:
    board: list[list[Bubble | None]]
    first_row_shifted: bool

    def is_shifted(self, row: int) -> bool:
        return (row % 2 == 1) != self.first_row_shifted

    def grid_to_pixel(self, row: int, col: int) -> pygame.Vector2:
        x = col * 2 * BUBBLE_RADIUS + BUBBLE_RADIUS
        if self.is_shifted(row):
            x += BUBBLE_RADIUS
        y = row * BUBBLE_RADIUS * sqrt(3) + BUBBLE_RADIUS
        return pygame.Vector2(x, y)

    def pixel_to_grid(self, x: float, y: float) -> tuple[int, int]:
        row = round((y - BUBBLE_RADIUS) / (BUBBLE_RADIUS * sqrt(3)))
        row = min(ROWS - 1, max(0, row))
        if self.is_shifted(row):
            x -= BUBBLE_RADIUS
        col = round((x - BUBBLE_RADIUS) / (2 * BUBBLE_RADIUS))
        col = min(COLS - 1, max(0, col))
        return (row, col)

    def get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        if self.is_shifted(row):
            diag = (col, col + 1)
        else:
            diag = (col - 1, col)

        candidates = [
            (row, col - 1),
            (row, col + 1),
            (row - 1, diag[0]),
            (row - 1, diag[1]),
            (row + 1, diag[0]),
            (row + 1, diag[1]),
        ]
        return [(r, c) for r, c in candidates if 0 <= r < ROWS and 0 <= c < COLS]

    def collides(self, projectile: Projectile) -> bool:
        for line in self.board:
            for b in line:
                if (
                    b is not None
                    and b.pos.distance_to(projectile.pos) < 2 * BUBBLE_RADIUS
                ):
                    return True
        return False

    def snap(self, projectile: Projectile) -> tuple[int, int]:
        row, col = self.pixel_to_grid(projectile.pos.x, projectile.pos.y)

        if self.board[row][col] is not None:
            empty = [
                (r, c)
                for r in range(ROWS)
                for c in range(COLS)
                if self.board[r][c] is None
            ]
            row, col = min(
                empty,
                key=lambda rc: self.grid_to_pixel(rc[0], rc[1]).distance_to(
                    projectile.pos
                ),
            )

        self.board[row][col] = Bubble(
            projectile.color, row, col, self.grid_to_pixel(row, col), BUBBLE_RADIUS
        )
        return (row, col)

    def find_cluster(self, row: int, col: int) -> list[tuple[int, int]]:
        start = self.board[row][col]
        if start is None:
            return []

        visited: set[tuple[int, int]] = {(row, col)}
        order: list[tuple[int, int]] = [(row, col)]
        queue = deque([(row, col)])
        while queue:
            r, c = queue.popleft()
            for nr, nc in self.get_neighbors(r, c):
                b = self.board[nr][nc]
                if (nr, nc) not in visited and b is not None and b.color == start.color:
                    visited.add((nr, nc))
                    order.append((nr, nc))
                    queue.append((nr, nc))

        return order

    def remove(self, cells: set[tuple[int, int]]) -> None:
        for r, c in cells:
            self.board[r][c] = None

    def find_floating(self, ignore: set[tuple[int, int]]) -> list[tuple[int, int]]:
        def filled(r: int, c: int) -> bool:
            return self.board[r][c] is not None and (r, c) not in ignore

        attached: set[tuple[int, int]] = set()
        queue = deque()
        for c in range(COLS):
            if filled(0, c):
                attached.add((0, c))
                queue.append((0, c))

        while queue:
            r, c = queue.popleft()
            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in attached and filled(nr, nc):
                    attached.add((nr, nc))
                    queue.append((nr, nc))

        return [
            (r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if filled(r, c) and (r, c) not in attached
        ]

    def colors_present(self) -> list[tuple[int, int, int]]:
        return list({b.color for line in self.board for b in line if b is not None})

    def add_row(self) -> bool:
        if self.reached_bottom():
            return True

        colors = self.colors_present() or COLORS

        self.first_row_shifted = not self.first_row_shifted
        _ = self.board.pop()
        self.board.insert(0, [None] * COLS)

        for c in range(COLS):
            self.board[0][c] = Bubble(
                get_random_color(colors), 0, c, pygame.Vector2(), BUBBLE_RADIUS
            )

        for r, line in enumerate(self.board):
            for b in line:
                if b is not None:
                    b.row = r
                    b.pos = self.grid_to_pixel(r, b.col)

        return self.reached_bottom()

    def draw(self, surface: pygame.Surface) -> None:
        for line in self.board:
            for b in line:
                if b is not None:
                    b.draw(surface)

    def is_empty(self) -> bool:
        return all(b is None for line in self.board for b in line)

    def reached_bottom(self) -> bool:
        return any(b is not None for b in self.board[-1])


def get_random_color(colors: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return random.choice(colors)


def create_test_grid() -> Grid:
    board: list[list[Bubble | None]] = []
    for _ in range(ROWS):
        board.append([None] * COLS)

    grid = Grid(board, True)
    for row in range(START_ROWS):
        for col in range(COLS):
            b = Bubble(
                get_random_color(COLORS),
                row,
                col,
                grid.grid_to_pixel(row, col),
                BUBBLE_RADIUS,
            )
            grid.board[row][col] = b
    return grid
