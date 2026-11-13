from __future__ import annotations

from typing import Protocol

import pygame


class Scene(Protocol):
    next_scene: Scene | None

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self, surface: pygame.Surface) -> None: ...
