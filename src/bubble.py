from dataclasses import dataclass
import pygame


@dataclass
class Bubble:
    color: tuple[int, int, int]
    row: int
    col: int
    pos: pygame.Vector2
    radius: float

    def draw(self, surface: pygame.Surface) -> None:
        _ = pygame.draw.circle(surface, self.color, self.pos, self.radius)
