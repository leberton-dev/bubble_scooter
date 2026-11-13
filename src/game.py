from collections import deque

import pygame

from src.grid import Cell, Grid
from src.hud import HUD
from src.projectile import Projectile
from src.settings import (
    BG_COLOR,
    COLORS,
    COLS,
    FPS,
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
from src.state import GameState


class Game:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.running: bool = True
        self.hud: HUD = HUD()
        self.sounds: Sounds = Sounds()
        self.reset()

    @property
    def can_shoot(self) -> bool:
        return self.projectile is None and not self.pop_queue

    def reset(self) -> None:
        self.grid: Grid = Grid.random(START_ROWS, ROWS, COLS, COLORS)
        self.shooter: Shooter = Shooter.spawn(self.grid.colors_present())
        self.projectile: Projectile | None = None
        self.miss_allowance: int = MISSES_PER_ROW
        self.misses_left: int = self.miss_allowance
        self.score: int = 0
        self.state: GameState = GameState.playing
        self.pop_queue: deque[Cell] = deque()
        self.pop_timer: float = 0
        self.mouse_pos: tuple[int, int] = (0, 0)

    def run(self) -> None:
        dt = 0
        while self.running:
            self.handle_events()
            self.update(dt)
            self.draw()
            dt = self.clock.tick(FPS) / 1000

        pygame.quit()

    def handle_events(self) -> None:
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state != GameState.playing:
                    self.reset()
                elif self.can_shoot:
                    self.projectile = self.shooter.shoot(self.grid.colors_present())
                    self.sounds.play("shoot")

    def update(self, dt: float) -> None:
        if self.state != GameState.playing:
            return

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

    def end_turn(self) -> None:
        if self.grid.is_empty():
            self.state = GameState.won
            self.sounds.play("win")
        elif self.grid.reached_bottom():
            self.state = GameState.lost
            self.sounds.play("lose")
        else:
            self.shooter.refresh_colors(self.grid.colors_present())

    def draw(self) -> None:
        self.screen.fill(BG_COLOR)
        self.grid.draw(self.screen)
        self.shooter.draw(self.screen)
        if self.projectile is not None:
            self.projectile.draw(self.screen)
        self.hud.draw(
            self.screen, self.score, self.state, self.grid.lose_y, self.misses_left
        )
        pygame.display.flip()
