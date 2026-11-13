import pygame

from src.game import Game
from src.settings import HEIGHT, WIDTH


def main():
    pygame.init()
    Game(pygame.display.set_mode((WIDTH, HEIGHT)), pygame.time.Clock()).run()


if __name__ == "__main__":
    main()
