import pygame

from src.save_file import SaveFile
from src.scene import Scene
from src.scenes.menu import MenuScene
from src.scenes.play import PlayScene
from src.settings import FPS, HEIGHT, WIDTH
from src.sound import Sounds


class App:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.sounds: Sounds = Sounds()
        self.save_file: SaveFile = SaveFile(SaveFile.data_dir() / "save.json")
        self.scene: Scene = MenuScene(
            lambda: PlayScene(self.sounds, self.save_file), self.save_file
        )
        self.running: bool = True

    def run(self) -> None:
        dt = 0.0
        while self.running:
            for event in pygame.event.get():
                self._handle_event(event)
            self.scene.update(dt)
            if self.scene.next_scene is not None:
                self.scene = self.scene.next_scene
            self.scene.draw(self.screen)
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000
        pygame.quit()

    def _handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        self.scene.handle_event(event)
