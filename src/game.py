from collections import deque
from math import pi
import pygame

from src.grid import Cell, Grid, get_random_color
from src.hud import HUD
from src.projectile import Projectile
from src.settings import BUBBLE_RADIUS, COLORS, COLS, FPS, BG_COLOR, MISSES_PER_ROW, POP_DELAY, ROWS, ROWS_PER_ADD, START_ROWS, WIDTH, HEIGHT
from src.shooter import Shooter
from src.sound import Sounds


class Game:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.running: bool = True
        self.hud: HUD = HUD()
        self.sounds: Sounds = Sounds()
        self.reset()

    def reset(self) -> None:
        self.grid: Grid = Grid.random(START_ROWS, ROWS, COLS, COLORS)
        colors = self.grid.colors_present()
        self.shooter: Shooter = Shooter(
            get_random_color(colors),
            get_random_color(colors),
            pygame.Vector2(WIDTH / 2, HEIGHT - 100),
            pi / 2,
        )
        self.projectile: Projectile | None = None
        self.max_misses: int = MISSES_PER_ROW
        self.misses_left: int = self.max_misses
        self.score: int = 0
        self.state: str = "playing"
        self.pop_queue: deque[Cell] = deque()
        self.pop_timer: float = 0

    def run(self) -> None:
        dt = 0
        while self.running:
            self.handle_events()
            self.update(dt)
            self.draw()
            dt = self.clock.tick(FPS) / 1000

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state != "playing":
                    self.reset()
                elif self.projectile is None and not self.pop_queue:
                    self.projectile = self.shooter.shoot(self.grid.colors_present())
                    self.sounds.play("shoot")

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return

        self.shooter.aim(pygame.mouse.get_pos())

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

    def resolve_shot(self, cell: Cell) -> None:
        cluster = self.grid.find_cluster(cell)
        if len(cluster) >= 3:
            floating = self.grid.find_floating(set(cluster))
            self.score += len(cluster) * 10 + len(floating) * 20
            self.pop_queue = deque(cluster + floating)
            self.pop_timer = 0
            return

        self.misses_left -= 1
        if self.misses_left == 0:
            for _ in range(ROWS_PER_ADD):
                self.grid.add_row()
                if self.grid.reached_bottom():
                    break
            self.sounds.play("row")
            self.max_misses -= 1
            if self.max_misses == 1:
                self.max_misses = MISSES_PER_ROW
            self.misses_left = self.max_misses
        self.end_turn()

    def end_turn(self) -> None:
        if self.grid.is_empty():
            self.state = "won"
            self.sounds.play("win")
        elif self.grid.reached_bottom():
            self.state = "lost"
            self.sounds.play("lose")
        else:
            self.shooter.refresh_colors(self.grid.colors_present())

    def draw(self) -> None:
        _ = self.screen.fill(BG_COLOR)
        self.grid.draw(self.screen)
        self.shooter.draw(self.screen)
        if self.projectile is not None:
            self.projectile.draw(self.screen)

        lose_y = self.grid.grid_to_pixel(ROWS -1, 0).y
        _ = pygame.draw.line(self.screen, (200, 50, 50), (0, lose_y), (WIDTH, lose_y), 2)

        for i in range(self.misses_left):
            pos = (30 + i * 25, self.shooter.pos.y)
            _ = pygame.draw.circle(
                self.screen, (150, 150, 150), pos, BUBBLE_RADIUS // 2
            )

        _ = pygame.draw.circle(self.screen, self.shooter.next_color, (WIDTH - BUBBLE_RADIUS - 10, self.shooter.pos.y), BUBBLE_RADIUS)
        self.hud.draw(self.screen, self.score, self.state)
        pygame.display.flip()
