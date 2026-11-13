import pygame

from src.settings import BUBBLE_RADIUS, HEIGHT, SHOOTER_Y, WIDTH, Color
from src.text_renderer import TextRenderer

SCORE_MARGIN_X: int = 20
SCORE_MARGIN_BOTTOM: int = 50

LOSE_LINE_COLOR: Color = (200, 50, 50)
LOSE_LINE_WIDTH: int = 2

MISS_DOT_COLOR: Color = (150, 150, 150)
MISS_DOT_RADIUS: int = BUBBLE_RADIUS // 2
MISS_DOT_START_X: int = 30
MISS_DOT_SPACING: int = 25


class HUD:
    def __init__(self) -> None:
        self.text_renderer: TextRenderer = TextRenderer()

    def draw(
        self,
        surface: pygame.Surface,
        score: int,
        lose_y: float,
        misses_left: int,
    ) -> None:
        self._draw_lose_line(surface, lose_y)
        self._draw_misses(surface, misses_left)
        self._draw_score(surface, score)

    def _draw_lose_line(self, surface: pygame.Surface, lose_y: float) -> None:
        pygame.draw.line(
            surface, LOSE_LINE_COLOR, (0, lose_y), (WIDTH, lose_y), LOSE_LINE_WIDTH
        )

    def _draw_misses(self, surface: pygame.Surface, misses_left: int) -> None:
        for i in range(misses_left):
            pos = (MISS_DOT_START_X + i * MISS_DOT_SPACING, SHOOTER_Y)
            pygame.draw.circle(surface, MISS_DOT_COLOR, pos, BUBBLE_RADIUS // 2)

    def _draw_score(self, surface: pygame.Surface, score: int) -> None:
        self.text_renderer.draw_at(
            surface,
            f"Score : {score}",
            (WIDTH - SCORE_MARGIN_X, HEIGHT - SCORE_MARGIN_BOTTOM),
            anchor="topright",
        )
