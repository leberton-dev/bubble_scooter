from enum import auto, Enum

class GameState(Enum):
    playing = auto()
    won = auto()
    lost = auto()
