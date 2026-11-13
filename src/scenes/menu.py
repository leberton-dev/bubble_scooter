from collections.abc import Callable

import pygame

from src.hud import FONT_SIZE, TEXT_COLOR
from src.scene import Scene
from src.settings import BG_COLOR, HEIGHT, WIDTH

BIG_FONT_SIZE: int = 80
SUBTITLE_OFFSET_Y: int = 60


class MenuScene:
    def __init__(self, new_game: Callable[[], Scene]) -> None:
        self.new_game: Callable[[], Scene] = new_game
        self.next_scene: Scene | None = None
        self.font: pygame.font.Font = pygame.font.Font(None, FONT_SIZE)
        self.big_font: pygame.font.Font = pygame.font.Font(None, BIG_FONT_SIZE)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            return
        self.next_scene = self.new_game()

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        title = self.big_font.render("BUBBLE SCOOTER", True, TEXT_COLOR)
        sub = self.font.render("Click to play", True, TEXT_COLOR)
        center = (WIDTH / 2, HEIGHT / 2)
        surface.blit(title, title.get_rect(center=center))
        surface.blit(
            sub, sub.get_rect(center=(center[0], center[1] + SUBTITLE_OFFSET_Y))
        )
