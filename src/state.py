from enum import Enum, auto


class GameState(Enum):
    playing = auto()
    won = auto()
    lost = auto()
