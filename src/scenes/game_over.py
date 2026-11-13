from collections.abc import Callable

import pygame

from src.scene import Scene
from src.settings import BG_COLOR
from src.text_renderer import TextRenderer, TextSize


class GameOverScene:
    def __init__(self, won: bool, score: int, new_game: Callable[[], Scene]) -> None:
        self.next_scene: Scene | None = None
        self.won: bool = won
        self.score: int = score
        self.new_game: Callable[[], Scene] = new_game
        self.text_renderer: TextRenderer = TextRenderer()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        self.next_scene = self.new_game()

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        msg = "You won!" if self.won else "You lost..."
        self.text_renderer.draw_centered(surface, msg, TextSize.big)
        self.text_renderer.draw_centered(
            surface, f"Score: {self.score}", offset_y=TextRenderer.LINE_SPACING
        )
        self.text_renderer.draw_centered(
            surface, "Click to play", offset_y=TextRenderer.LINE_SPACING * 2
        )
