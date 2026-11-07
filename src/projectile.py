from dataclasses import dataclass

import pygame

from src.settings import BUBBLE_RADIUS, WIDTH


@dataclass
class Projectile:
    pos: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]

    def update(self, dt: float) -> None:
        self.pos += self.velocity * dt

        if self.pos.x - BUBBLE_RADIUS < 0:
            self.pos.x = BUBBLE_RADIUS
            self.velocity.x = -self.velocity.x

        if self.pos.x + BUBBLE_RADIUS > WIDTH:
            self.pos.x = WIDTH - BUBBLE_RADIUS
            self.velocity.x = -self.velocity.x

    def hit_ceiling(self) -> bool:
        return self.pos.y - BUBBLE_RADIUS <= 0

    def draw(self, surface: pygame.Surface) -> None:
        _ = pygame.draw.circle(surface, self.color, self.pos, BUBBLE_RADIUS)
