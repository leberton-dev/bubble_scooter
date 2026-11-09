from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from math import sqrt
import random
from typing import NamedTuple

import pygame

from src.bubble import Bubble
from src.projectile import Projectile
from src.settings import BUBBLE_RADIUS, COLORS, COLS, ROWS, START_ROWS


class Cell(NamedTuple):
    row: int
    col: int


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
        for cell, _ in self.bubbles():
            if self.grid_to_pixel(cell.row, cell.col).distance_to(projectile.pos) < 2 * BUBBLE_RADIUS:
                return True
        return False

    def snap(self, projectile: Projectile) -> Cell:
        row, col = self.pixel_to_grid(projectile.pos.x, projectile.pos.y)

        if self.board[row][col] is not None:
            row, col = min(
                self.empty_cells(),
                key=lambda cell: self.grid_to_pixel(cell.row, cell.col).distance_to(projectile.pos),
            )

        self.board[row][col] = Bubble(projectile.color)
        return Cell(row, col)

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

        return [cell for cell, _ in self.bubbles() if cell not in ignore and cell not in attached]

    def colors_present(self) -> list[tuple[int, int, int]]:
        return list({b.color for _, b in self.bubbles()})

    def add_row(self) -> None:
        colors = self.colors_present() or COLORS

        self.first_row_shifted = not self.first_row_shifted
        _ = self.board.pop()
        self.board.insert(0, [Bubble(get_random_color(colors)) for _ in range(COLS)])

    def draw(self, surface: pygame.Surface) -> None:
        for cell, bubble in self.bubbles():
            bubble.draw(surface, self.grid_to_pixel(cell.row, cell.col))

    def is_empty(self) -> bool:
        return next(self.bubbles(), None) is None

    def reached_bottom(self) -> bool:
        return any(b is not None for b in self.board[-1])

    def bubble_at(self, cell: Cell) -> Bubble | None:
        return self.board[cell.row][cell.col]

    def cells(self) -> Iterator[Cell]:
        for r in range(ROWS):
            for c in range(COLS):
                yield Cell(r, c)

    def bubbles(self) -> Iterator[tuple[Cell, Bubble]]:
        for cell in self.cells():
            b = self.bubble_at(cell)
            if b is not None:
                yield (cell, b)

    def empty_cells(self) -> Iterator[Cell]:
        for cell in self.cells():
            if self.bubble_at(cell) is None:
                yield cell


def get_random_color(colors: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return random.choice(colors)


def create_test_grid() -> Grid:
    board: list[list[Bubble | None]] = []
    for _ in range(ROWS):
        board.append([None] * COLS)

    grid = Grid(board, True)
    for cell in grid.cells():
        if cell.row < START_ROWS:
            grid.board[cell.row][cell.col] = Bubble(get_random_color(COLORS))

    return grid
