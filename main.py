import pygame
import random
import copy
import time

pygame.init()

pygame.mixer.init()

pygame.mixer.music.load("theme.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

SCREEN_WIDTH = 475
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
PLAY_AREA_WIDTH = 10 * BLOCK_SIZE

BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
UI_BG_COLOR = (50, 50, 50)

COLORS = [
    (0, 255, 255),  # Cyan (I)
    (255, 255, 0),  # Yellow (O)
    (255, 127, 0),  # Orange (L)
    (0, 0, 255),    # Blue (J)
    (0, 255, 0),    # Green (S)
    (255, 0, 0),    # Red (Z)
    (128, 0, 128)   # Purple (T)
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 0], [1, 1, 1]]   # T
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

grid = [[0 for _ in range(PLAY_AREA_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

score = 0

def draw_grid():
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x]:
                pygame.draw.rect(screen, COLORS[grid[y][x] - 1], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, UI_BG_COLOR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_ui_background():
    pygame.draw.rect(screen, UI_BG_COLOR, (PLAY_AREA_WIDTH, 0, SCREEN_WIDTH - PLAY_AREA_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(screen, WHITE, (PLAY_AREA_WIDTH, 0), (PLAY_AREA_WIDTH, SCREEN_HEIGHT), 2)

def new_tetromino():
    shape = random.choice(SHAPES)
    color = random.randint(1, len(COLORS))
    return {
        "shape": shape,
        "color": color,
        "x": PLAY_AREA_WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2,
        "y": 0
    }
    
def draw_next_tetromino(next_tetromino):
    font = pygame.font.Font(None, 36)
    next_text = font.render("Next:", True, WHITE)
    screen.blit(next_text, (PLAY_AREA_WIDTH + 20, 10))

    for y, row in enumerate(next_tetromino["shape"]):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    screen,
                    COLORS[next_tetromino["color"] - 1],
                    (PLAY_AREA_WIDTH + 20 + x * BLOCK_SIZE, 50 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )
                
def draw_held_tetromino(held_tetromino):
    font = pygame.font.Font(None, 36)
    hold_text = font.render("Hold:", True, WHITE)
    screen.blit(hold_text, (PLAY_AREA_WIDTH + 20, 250))

    if held_tetromino:
        for y, row in enumerate(held_tetromino["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        COLORS[held_tetromino["color"] - 1],
                        (PLAY_AREA_WIDTH + 20 + x * BLOCK_SIZE, 290 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

def draw_controls_legend():
    font = pygame.font.Font(None, 24)
    controls = [
        "Controls:",
        "Arrow Keys: Move",
        "UP: Rotate",
        "DOWN: Soft Drop",
        "SPACE: Hard Drop",
        "SHIFT: Hold"
    ]
    for i, text in enumerate(controls):
        control_text = font.render(text, True, WHITE)
        screen.blit(control_text, (PLAY_AREA_WIDTH + 20, 400 + i * 20))

def can_move(tetromino, dx, dy):
    for y, row in enumerate(tetromino["shape"]):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetromino["x"] + x + dx
                new_y = tetromino["y"] + y + dy

                if new_x < 0 or new_x >= len(grid[0]) or new_y >= len(grid) or (new_y >= 0 and grid[new_y][new_x]):
                    return False
    return True

def place_tetromino(tetromino):
    for y, row in enumerate(tetromino["shape"]):
        for x, cell in enumerate(row):
            if cell:
                grid[tetromino["y"] + y][tetromino["x"] + x] = tetromino["color"]

def clear_lines_with_effect():
    global grid, score
    lines_to_clear = [i for i, row in enumerate(grid) if all(row)]

    if lines_to_clear:
        for _ in range(3):
            for line in lines_to_clear:
                for x in range(len(grid[line])):
                    pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, line * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.display.flip()
            time.sleep(0.1)
            draw_grid()
            pygame.display.flip()
            time.sleep(0.05)

        for line in lines_to_clear:
            del grid[line]
            grid.insert(0, [0 for _ in range(PLAY_AREA_WIDTH // BLOCK_SIZE)])

        if len(lines_to_clear) == 1:
            score += 100
        elif len(lines_to_clear) == 2:
            score += 200
        elif len(lines_to_clear) == 3:
            score += 300
        elif len(lines_to_clear) == 4:
            score += 400

def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (PLAY_AREA_WIDTH + 20, 150))

def rotate_tetromino(tetromino):
    rotated_shape = list(zip(*tetromino["shape"][::-1]))
    new_tetromino = copy.deepcopy(tetromino)
    new_tetromino["shape"] = rotated_shape
    if can_move(new_tetromino, 0, 0):
        return new_tetromino
    return tetromino

def calculate_level_and_speed(score):
    level = score // 1000 + 1
    fall_speed = max(25, 125 - (level - 1) * 25)
    return level, fall_speed

def draw_level(level):
    font = pygame.font.Font(None, 36)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (PLAY_AREA_WIDTH + 20, 200))

def draw_ghost_tetromino(tetromino):
    ghost_tetromino = tetromino.copy()
    while can_move(ghost_tetromino, 0, 1):
        ghost_tetromino["y"] += 1

    for y, row in enumerate(ghost_tetromino["shape"]):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    screen,
                    COLORS[ghost_tetromino["color"] - 1],
                    ((ghost_tetromino["x"] + x) * BLOCK_SIZE, (ghost_tetromino["y"] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

def hard_drop(tetromino):
    while can_move(tetromino, 0, 1):
        tetromino["y"] += 1
    return tetromino

def show_game_over_screen(level, score):
    screen.fill(BG_COLOR)

    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    game_over_text = font_large.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))

    level_text = font_small.render(f"Level: {level}", True, WHITE)
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 200))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))

    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 420, 200, 50)

    pygame.draw.rect(screen, (0, 200, 0), restart_button)
    pygame.draw.rect(screen, (200, 0, 0), quit_button)

    restart_text = font_small.render("Restart", True, WHITE)
    quit_text = font_small.render("Quit", True, WHITE)
    screen.blit(restart_text, (restart_button.x + restart_button.width // 2 - restart_text.get_width() // 2, restart_button.y + 10))
    screen.blit(quit_text, (quit_button.x + quit_button.width // 2 - quit_text.get_width() // 2, quit_button.y + 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

def main():
    global score, grid
    while True:
        score = 0
        grid = [[0 for _ in range(PLAY_AREA_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        tetromino = new_tetromino()
        next_tetromino = new_tetromino()
        held_tetromino = None
        can_hold = True
        fall_time = 0
        move_time = 0
        move_delay = 10
        level, fall_speed = calculate_level_and_speed(score)

        keys_pressed = {"left": False, "right": False, "down": False}
        tetromino_placed = False

        running = True
        while running:
            screen.fill(BG_COLOR)
            draw_ui_background()
            draw_grid()
            draw_score()
            draw_level(level)
            draw_next_tetromino(next_tetromino)
            draw_held_tetromino(held_tetromino)
            draw_controls_legend()
            draw_ghost_tetromino(tetromino)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        keys_pressed["left"] = True
                    if event.key == pygame.K_RIGHT:
                        keys_pressed["right"] = True
                    if event.key == pygame.K_DOWN:
                        keys_pressed["down"] = True
                    if event.key == pygame.K_UP:
                        tetromino = rotate_tetromino(tetromino)
                    if event.key == pygame.K_SPACE:
                        tetromino = hard_drop(tetromino)
                        tetromino_placed = True
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        if can_hold:
                            if held_tetromino:
                                tetromino, held_tetromino = held_tetromino, tetromino
                                tetromino["x"] = PLAY_AREA_WIDTH // BLOCK_SIZE // 2 - len(tetromino["shape"][0]) // 2
                                tetromino["y"] = 0
                            else:
                                held_tetromino = tetromino
                                tetromino = next_tetromino
                                next_tetromino = new_tetromino()
                            can_hold = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        keys_pressed["left"] = False
                    if event.key == pygame.K_RIGHT:
                        keys_pressed["right"] = False
                    if event.key == pygame.K_DOWN:
                        keys_pressed["down"] = False

            move_time += clock.get_rawtime()
            if move_time >= move_delay:
                move_time = 0
                if keys_pressed["left"] and can_move(tetromino, -1, 0):
                    tetromino["x"] -= 1
                if keys_pressed["right"] and can_move(tetromino, 1, 0):
                    tetromino["x"] += 1

            if keys_pressed["down"] and can_move(tetromino, 0, 1):
                tetromino["y"] += 1

            fall_time += clock.get_rawtime()
            if fall_time >= fall_speed:
                fall_time = 0
                if can_move(tetromino, 0, 1):
                    tetromino["y"] += 1
                else:
                    tetromino_placed = True

            if tetromino_placed:
                place_tetromino(tetromino)
                clear_lines_with_effect()
                level, fall_speed = calculate_level_and_speed(score)
                tetromino = next_tetromino
                next_tetromino = new_tetromino()
                can_hold = True
                if not can_move(tetromino, 0, 0):
                    running = False
                tetromino_placed = False

            for y, row in enumerate(tetromino["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, COLORS[tetromino["color"] - 1], ((tetromino["x"] + x) * BLOCK_SIZE, (tetromino["y"] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

            pygame.display.flip()
            clock.tick(30)

        choice = show_game_over_screen(level, score)
        if choice == "restart":
            continue
        else:
            break

if __name__ == "__main__":
    main()