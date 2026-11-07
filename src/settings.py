WIDTH: int = 640
HEIGHT: int = 800
FPS: int = 60

BUBBLE_RADIUS: int = 20
ROWS: int = 16
COLS: int = (WIDTH - BUBBLE_RADIUS) // (2 * BUBBLE_RADIUS)
START_ROWS: int = 6
COLORS: list[tuple[int, int, int]] = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]

BG_COLOR: tuple[int, int, int] = (20, 20, 30)

PROJECTILE_SPEED: int = 800

MISSES_PER_ROW: int = 5
ROWS_PER_ADD: int = 2
