from pathlib import Path
import pygame

SOUND_DIR = Path(__file__).parent.parent / "assets" / "sounds"

class Sounds:
    def __init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        if pygame.mixer.get_init() is None:
            return

        for name in ("shoot", "pop", "row", "win", "loose"):
            path = SOUND_DIR / f"{name}.wav"
            if path.exists():
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(0.5)

    def play(self, name: str) -> None:
        if name in self.sounds:
            _ = self.sounds[name].play()

