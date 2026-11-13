from enum import Enum, auto
from typing import Literal

import pygame

from src.settings import HEIGHT, WIDTH

FONT_SIZE: int = 36
SMALL_FONT_SIZE: int = 24
BIG_FONT_SIZE: int = 80

TEXT_COLOR: str = "white"


Anchor = Literal[
    "center",
    "topleft",
    "topright",
    "bottomleft",
    "bottomright",
    "midtop",
    "midbottom",
    "midleft",
    "midright",
]


class TextSize(Enum):
    small = auto()
    normal = auto()
    big = auto()


class TextRenderer:
    LINE_SPACING: int = 60

    def __init__(self) -> None:
        self.fonts: dict[TextSize, pygame.font.Font] = {
            TextSize.small: pygame.font.Font(None, SMALL_FONT_SIZE),
            TextSize.normal: pygame.font.Font(None, FONT_SIZE),
            TextSize.big: pygame.font.Font(None, BIG_FONT_SIZE),
        }

    @staticmethod
    def screen_center(offset_y: float) -> tuple[float, float]:
        return (WIDTH / 2, HEIGHT / 2 + offset_y)

    def draw_centered(
        self,
        surface: pygame.Surface,
        text: str,
        size: TextSize = TextSize.normal,
        *,
        offset_y: float = 0,
    ) -> None:
        txt = self._get_text(text, size)
        surface.blit(txt, txt.get_rect(center=self.screen_center(offset_y)))

    def draw_at(
        self,
        surface: pygame.Surface,
        text: str,
        pos: tuple[float, float],
        size: TextSize = TextSize.normal,
        *,
        anchor: Anchor = "center",
    ) -> None:
        txt = self._get_text(text, size)
        surface.blit(txt, txt.get_rect(**{anchor: pos}))

    def _get_text(self, text: str, size: TextSize) -> pygame.Surface:
        return self.fonts[size].render(text, True, TEXT_COLOR)
