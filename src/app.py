import pygame

from src.match import Match
from src.settings import FPS, HEIGHT, WIDTH
from src.sound import Sounds


class App:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.sounds: Sounds = Sounds()
        self.match: Match = Match(self.sounds)
        self.running: bool = True

    def run(self) -> None:
        dt = 0.0
        while self.running:
            for event in pygame.event.get():
                self._handle_event(event)
            self.match.update(dt)
            self.match.draw(self.screen)
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000
        pygame.quit()

    def _handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.match.is_over:
            self.match = Match(self.sounds)
            return
        self.match.handle_event(event)
