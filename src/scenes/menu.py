from collections.abc import Callable

import pygame

from src.save_file import SaveFile
from src.scene import Scene
from src.settings import BG_COLOR
from src.text_renderer import TextRenderer, TextSize


class MenuScene:
    def __init__(self, new_game: Callable[[], Scene], save_file: SaveFile) -> None:
        self.new_game: Callable[[], Scene] = new_game
        self.next_scene: Scene | None = None
        self.text_renderer: TextRenderer = TextRenderer()
        self.best_score: int = save_file.load()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            return
        self.next_scene = self.new_game()

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self.text_renderer.draw_centered(surface, "BUBBLE SCOOTER", TextSize.big)
        self.text_renderer.draw_centered(
            surface, "Click to play", offset_y=TextRenderer.LINE_SPACING
        )
        self.text_renderer.draw_centered(
            surface,
            f"Best score: {self.best_score}",
            offset_y=TextRenderer.LINE_SPACING * 2,
        )
