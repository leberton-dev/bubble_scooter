from dataclasses import dataclass
import pygame

from src.settings import BUBBLE_RADIUS


@dataclass
class Bubble:
    color: tuple[int, int, int]

    def draw(self, surface: pygame.Surface, pos: pygame.Vector2) -> None:
        _ = pygame.draw.circle(surface, self.color, pos, BUBBLE_RADIUS)
