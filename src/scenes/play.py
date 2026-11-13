from collections import deque

import pygame

from src.grid import Cell, Grid
from src.hud import HUD
from src.projectile import Projectile
from src.save_file import SaveFile
from src.scene import Scene
from src.scenes.game_over import GameOverScene
from src.settings import (
    BG_COLOR,
    COLORS,
    COLS,
    MIN_CLUSTER_SIZE,
    MISSES_PER_ROW,
    POINTS_PER_DROP,
    POINTS_PER_POP,
    POP_DELAY,
    ROWS,
    ROWS_PER_ADD,
    START_ROWS,
)
from src.shooter import Shooter
from src.sound import Sounds


class PlayScene:
    def __init__(self, sounds: Sounds, save_file: SaveFile) -> None:
        self.next_scene: Scene | None = None
        self.sounds: Sounds = sounds
        self.save_file: SaveFile = save_file
        self.hud: HUD = HUD()
        self.grid: Grid = Grid.random(START_ROWS, ROWS, COLS, COLORS)
        self.shooter: Shooter = Shooter.spawn(self.grid.colors_present())
        self.projectile: Projectile | None = None
        self.miss_allowance: int = MISSES_PER_ROW
        self.misses_left: int = self.miss_allowance
        self.score: int = 0
        self.pop_queue: deque[Cell] = deque()
        self.pop_timer: float = 0
        self.mouse_pos: tuple[int, int] = (0, 0)

    @property
    def can_shoot(self) -> bool:
        return self.projectile is None and not self.pop_queue

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.can_shoot:
            self.projectile = self.shooter.shoot(self.grid.colors_present())
            self.sounds.play("shoot")

    def update(self, dt: float) -> None:
        self.mouse_pos = pygame.mouse.get_pos()
        self.shooter.aim(pygame.Vector2(*self.mouse_pos))

        if self.pop_queue:
            self.update_pops(dt)
            return

        if self.projectile is None:
            return

        self.projectile.update(dt)
        if not (self.projectile.hit_ceiling() or self.grid.collides(self.projectile)):
            return

        cell = self.grid.nearest_free_cell(self.projectile.pos)
        self.grid.place_cell(cell, self.projectile.color)
        self.projectile = None
        self.resolve_shot(cell)

    def update_pops(self, dt: float) -> None:
        self.pop_timer -= dt
        while self.pop_timer <= 0 and self.pop_queue:
            cell = self.pop_queue.popleft()
            if self.grid.remove_cell(cell) is not None:
                self.sounds.play("pop")
            self.pop_timer += POP_DELAY

        if not self.pop_queue:
            self.end_turn()

    def _on_match(self, cluster: list[Cell]) -> None:
        floating = self.grid.find_floating(set(cluster))
        self.score += len(cluster) * POINTS_PER_POP + len(floating) * POINTS_PER_DROP
        self.pop_queue = deque(cluster + floating)
        self.pop_timer = 0

    def _shrink_miss_allowance(self) -> None:
        self.miss_allowance -= 1
        if self.miss_allowance == 1:
            self.miss_allowance = MISSES_PER_ROW

    def _on_miss(self) -> None:
        self.misses_left -= 1
        if self.misses_left == 0:
            self.grid.add_rows(ROWS_PER_ADD)
            self.sounds.play("row")
            self._shrink_miss_allowance()
            self.misses_left = self.miss_allowance
        self.end_turn()

    def resolve_shot(self, cell: Cell) -> None:
        cluster = self.grid.find_cluster(cell)
        if len(cluster) >= MIN_CLUSTER_SIZE:
            self._on_match(cluster)
        else:
            self._on_miss()

    def _game_over(self, won: bool) -> None:
        best = self.save_file.load()
        if self.score > best:
            self.save_file.save(self.score)
        self.next_scene = GameOverScene(won, self.score, lambda: PlayScene(self.sounds, self.save_file))

    def end_turn(self) -> None:
        if self.grid.is_empty():
            self._game_over(True)
            self.sounds.play("win")
        elif self.grid.reached_bottom():
            self._game_over(False)
            self.sounds.play("lose")
        else:
            self.shooter.refresh_colors(self.grid.colors_present())

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self.grid.draw(surface)
        self.shooter.draw(surface)
        if self.projectile is not None:
            self.projectile.draw(surface)
        self.hud.draw(surface, self.score, self.grid.lose_y, self.misses_left)
