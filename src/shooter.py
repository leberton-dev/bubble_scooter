from dataclasses import dataclass
from math import atan2, cos, pi, sin

import pygame

from src.grid import get_random_color
from src.projectile import Projectile
from src.settings import BUBBLE_RADIUS, PROJECTILE_SPEED, SHOOTER_Y, WIDTH

MIN_ANGLE: float = 0.17
MAX_ANGLE: float = pi - 0.17
START_ANGLE: float = pi / 2
AIM_LENGTH: int = 100
AIM_WIDTH: int = 3
AIM_COLOR: str = "white"
NEXT_PREVIEW_MARGIN: int = 10


@dataclass
class Shooter:
    current_color: tuple[int, int, int]
    next_color: tuple[int, int, int]
    pos: pygame.Vector2
    angle: float

    @classmethod
    def spawn(cls, colors: list[tuple[int, int, int]]) -> "Shooter":
        return cls(get_random_color(colors), get_random_color(colors), pygame.Vector2(WIDTH / 2, SHOOTER_Y), START_ANGLE)

    def aim(self, mouse_pos: tuple[int, int]) -> None:
        dx = mouse_pos[0] - self.pos.x
        dy = mouse_pos[1] - self.pos.y
        angle = atan2(-dy, dx)

        if angle < 0:
            angle = MAX_ANGLE if dx < 0 else MIN_ANGLE
        self.angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    def draw(self, surface: pygame.Surface) -> None:
        _ = pygame.draw.circle(surface, self.current_color, self.pos, BUBBLE_RADIUS)
        end_x = self.pos.x + cos(self.angle) * AIM_LENGTH
        end_y = self.pos.y - sin(self.angle) * AIM_LENGTH
        _ = pygame.draw.line(surface, AIM_COLOR, self.pos, (end_x, end_y), AIM_WIDTH)

        preview_pos = (WIDTH - BUBBLE_RADIUS - NEXT_PREVIEW_MARGIN, self.pos.y)
        _ = pygame.draw.circle(surface, self.next_color, preview_pos, BUBBLE_RADIUS)

    def shoot(self, colors: list[tuple[int, int, int]]) -> Projectile:
        direction = pygame.Vector2(cos(self.angle), -sin(self.angle))
        proj = Projectile(
            self.pos.copy(), direction * PROJECTILE_SPEED, self.current_color
        )
        self.current_color = self.next_color
        self.next_color = get_random_color(colors)
        return proj

    def refresh_colors(self, colors: list[tuple[int, int, int]]) -> None:
        if not colors:
            return
        if self.current_color not in colors:
            self.current_color = get_random_color(colors)
        if self.next_color not in colors:
            self.next_color = get_random_color(colors)
