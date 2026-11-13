from typing import cast

import pygame

from src.settings import Color
from src.text_renderer import TextRenderer


class Button:
    WIDTH: int = 150
    HEIGHT: int = 50
    BORDER_RADIUS: int = 12
    COLOR: Color = (46, 160, 90)
    HCOLOR: Color = (70, 200, 120)

    def __init__(
        self, label: str, center: tuple[int, int], text_renderer: TextRenderer
    ) -> None:
        self.label: str = label
        self.rect: pygame.Rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.center = center
        self.text_renderer: TextRenderer = text_renderer
        self.hovered: bool = False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        pos = cast(tuple[int, int], event.pos)
        return self.rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface) -> None:
        color = self.HCOLOR if self.hovered else self.COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=self.BORDER_RADIUS)
        self.text_renderer.draw_at(
            surface, self.label, self.rect.center, anchor="center"
        )
