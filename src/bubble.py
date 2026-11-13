from dataclasses import dataclass

import pygame

from src.settings import BUBBLE_RADIUS, Color


@dataclass
class Bubble:
    color: Color

    def draw(self, surface: pygame.Surface, pos: pygame.Vector2) -> None:
        pygame.draw.circle(surface, self.color, pos, BUBBLE_RADIUS)
