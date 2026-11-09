import pygame

from src.state import GameState
from src.settings import HEIGHT, WIDTH


class HUD:
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        self.big_font: pygame.font.Font = pygame.font.Font(None, 80)

    def draw(self, surface: pygame.Surface, score: int, state: GameState) -> None:
        score_txt = self.font.render(f"Score : {score}", True, "white")
        _ = surface.blit(score_txt, (WIDTH - score_txt.get_width() - 20, HEIGHT - 50))

        if state == GameState.playing:
            return

        msg = "Won!" if state == GameState.won else "Lost..."
        title = self.big_font.render(msg, True, "white")
        sub = self.font.render("Click to play", True, "white")
        _ = surface.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2)))
        _ = surface.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60)))
