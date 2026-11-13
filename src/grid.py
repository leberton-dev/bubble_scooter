import random
from collections import deque
from collections.abc import Callable, Iterator
from math import sqrt
from typing import NamedTuple

import pygame

from src.bubble import Bubble
from src.projectile import Projectile
from src.settings import BUBBLE_RADIUS, COLORS, Color


class Cell(NamedTuple):
    row: int
    col: int


class Grid:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.board: list[list[Bubble | None]] = [[None] * cols for _ in range(rows)]
        self.first_row_shifted: bool = True

    @classmethod
    def random(
        cls, start_rows: int, rows: int, cols: int, colors: list[Color]
    ) -> "Grid":
        if start_rows > rows:
            raise ValueError("start_rows cannot be bigger than rows")
        grid = cls(rows, cols)
        for cell in grid.cells():
            if cell.row < start_rows:
                grid.place_cell(cell, random.choice(colors))
        return grid

    @property
    def lose_y(self) -> float:
        return self.grid_to_pixel(self.rows - 1, 0).y

    def is_shifted(self, row: int) -> bool:
        return (row % 2 == 1) != self.first_row_shifted

    def grid_to_pixel(self, row: int, col: int) -> pygame.Vector2:
        x = col * 2 * BUBBLE_RADIUS + BUBBLE_RADIUS
        if self.is_shifted(row):
            x += BUBBLE_RADIUS
        y = row * BUBBLE_RADIUS * sqrt(3) + BUBBLE_RADIUS
        return pygame.Vector2(x, y)

    def pixel_to_grid(self, x: float, y: float) -> Cell:
        row = round((y - BUBBLE_RADIUS) / (BUBBLE_RADIUS * sqrt(3)))
        row = min(self.rows - 1, max(0, row))
        if self.is_shifted(row):
            x -= BUBBLE_RADIUS
        col = round((x - BUBBLE_RADIUS) / (2 * BUBBLE_RADIUS))
        col = min(self.cols - 1, max(0, col))
        return Cell(row, col)

    def get_neighbors(self, row: int, col: int) -> list[Cell]:
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
        return [
            Cell(r, c)
            for r, c in candidates
            if 0 <= r < self.rows and 0 <= c < self.cols
        ]

    def collides(self, projectile: Projectile) -> bool:
        for cell, _ in self.bubbles():
            if (
                self.grid_to_pixel(cell.row, cell.col).distance_to(projectile.pos)
                < 2 * BUBBLE_RADIUS
            ):
                return True
        return False

    def place_cell(self, cell: Cell, color: Color) -> None:
        self.board[cell.row][cell.col] = Bubble(color)

    def remove_cell(self, cell: Cell) -> Bubble | None:
        b = self.bubble_at(cell)
        self.board[cell.row][cell.col] = None
        return b

    def nearest_free_cell(self, pos: pygame.Vector2) -> Cell:
        def distance_to_pos(cell: Cell) -> float:
            return self.grid_to_pixel(cell.row, cell.col).distance_to(pos)

        target = self.pixel_to_grid(pos.x, pos.y)
        if self.bubble_at(target) is None:
            return target

        neighbours = [
            cell
            for cell in self.get_neighbors(target.row, target.col)
            if self.bubble_at(cell) is None
        ]
        if neighbours:
            return min(neighbours, key=distance_to_pos)
        return min(self.empty_cells(), key=distance_to_pos)

    def _flood_fill(
        self, start: list[Cell], condition: Callable[[Cell], bool]
    ) -> list[Cell]:
        visited = set(start)
        visited_ordered = list(start)
        queue = deque(start)
        while queue:
            cell = queue.popleft()
            for c in self.get_neighbors(cell.row, cell.col):
                if c not in visited and condition(c):
                    visited.add(c)
                    visited_ordered.append(c)
                    queue.append(c)
        return visited_ordered

    def find_cluster(self, cell: Cell) -> list[Cell]:
        start_bubble = self.bubble_at(cell)
        if start_bubble is None:
            return []

        def bubble_is_start_color(cell: Cell) -> bool:
            b = self.bubble_at(cell)
            return b is not None and b.color == start_bubble.color

        return self._flood_fill([cell], bubble_is_start_color)

    def find_floating(self, ignore: set[Cell]) -> list[Cell]:
        def filled(cell: Cell) -> bool:
            return self.bubble_at(cell) is not None and cell not in ignore

        start: list[Cell] = []
        for c in range(self.cols):
            cell = Cell(0, c)
            if filled(cell):
                start.append(cell)

        flood = set(self._flood_fill(start, filled))
        return [
            cell
            for cell, _ in self.bubbles()
            if cell not in ignore and cell not in flood
        ]

    def colors_present(self) -> list[Color]:
        return list({b.color for _, b in self.bubbles()})

    def add_row(self) -> None:
        colors = self.colors_present() or COLORS

        self.first_row_shifted = not self.first_row_shifted
        self.board.pop()
        self.board.insert(0, [Bubble(random.choice(colors)) for _ in range(self.cols)])

    def add_rows(self, n: int) -> None:
        for _ in range(n):
            self.add_row()
            if self.reached_bottom():
                break

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
        for r in range(self.rows):
            for c in range(self.cols):
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
