import pygame
import serial
import random
import time
import math

# =========================================================
# ARDUINO
# =========================================================

ARDUINO_PORT = "COM6"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.01)
    time.sleep(2)
    print("Arduino connected!")
except Exception as e:
    arduino = None
    print("Arduino not connected:", e)

# =========================================================
# PYGAME SETUP
# =========================================================

pygame.init()

WIDTH = 900
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turbo Bike 3D - Arduino Edition")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 26)
small_font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 55, bold=True)

# =========================================================
# COLORS
# =========================================================

SKY = (80, 165, 220)
GRASS = (45, 145, 70)
ROAD = (55, 55, 60)
ROAD_EDGE = (210, 210, 210)
WHITE = (245, 245, 245)
YELLOW = (255, 210, 0)
RED = (230, 45, 45)
BLUE = (30, 130, 255)
BLACK = (15, 15, 15)
GREEN = (40, 220, 80)
ORANGE = (255, 125, 20)

# =========================================================
# ROAD / PERSPECTIVE
# =========================================================

HORIZON_Y = 120

ROAD_TOP_LEFT = 365
ROAD_TOP_RIGHT = 535

ROAD_BOTTOM_LEFT = 100
ROAD_BOTTOM_RIGHT = 800

LANES = 3

# =========================================================
# GAME VARIABLES
# =========================================================

lane = 1

bike_y = 500

speed = 70
normal_speed = 70
max_speed = 180
brake_speed = 35

score = 0
lap = 1
health = 100

road_offset = 0

obstacles = []

spawn_timer = 0
spawn_delay = 85

game_over = False

last_left = False
last_right = False

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def road_width_at_y(y):

    ratio = (y - HORIZON_Y) / (HEIGHT - HORIZON_Y)
    ratio = max(0, min(1, ratio))

    left = ROAD_TOP_LEFT + (ROAD_BOTTOM_LEFT - ROAD_TOP_LEFT) * ratio
    right = ROAD_TOP_RIGHT + (ROAD_BOTTOM_RIGHT - ROAD_TOP_RIGHT) * ratio

    return left, right


def lane_center(lane_number, y):

    left, right = road_width_at_y(y)

    width = right - left

    lane_width = width / LANES

    return left + lane_width * lane_number + lane_width / 2


def draw_background():

    # Sky
    screen.fill(SKY)

    # Grass
    pygame.draw.rect(
        screen,
        GRASS,
        (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y)
    )

    # Road
    pygame.draw.polygon(
        screen,
        ROAD,
        [
            (ROAD_TOP_LEFT, HORIZON_Y),
            (ROAD_TOP_RIGHT, HORIZON_Y),
            (ROAD_BOTTOM_RIGHT, HEIGHT),
            (ROAD_BOTTOM_LEFT, HEIGHT)
        ]
    )

    # Road edges
    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (ROAD_TOP_LEFT, HORIZON_Y),
        (ROAD_BOTTOM_LEFT, HEIGHT),
        6
    )

    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (ROAD_TOP_RIGHT, HORIZON_Y),
        (ROAD_BOTTOM_RIGHT, HEIGHT),
        6
    )


def draw_lane_lines():

    global road_offset

    road_offset += speed / 35

    if road_offset > 65:
        road_offset = 0

    for y in range(HORIZON_Y, HEIGHT, 65):

        yy = y + road_offset

        if yy > HEIGHT:
            continue

        ratio = (yy - HORIZON_Y) / (HEIGHT - HORIZON_Y)

        line_length = int(8 + ratio * 30)

        for lane_line in [1, 2]:

            left, right = road_width_at_y(yy)

            x = left + ((right - left) / LANES) * lane_line

            pygame.draw.line(
                screen,
                WHITE,
                (int(x), int(yy)),
                (int(x), int(yy + line_length)),
                max(1, int(1 + ratio * 4))
            )


def draw_bike(x, y):

    # rear wheel
    pygame.draw.ellipse(
        screen,
        BLACK,
        (x - 14, y + 47, 28, 55)
    )

    # front wheel
    pygame.draw.ellipse(
        screen,
        BLACK,
        (x - 11, y - 10, 22, 45)
    )

    # bike body
    pygame.draw.polygon(
        screen,
        BLUE,
        [
            (x, y + 15),
            (x - 23, y + 55),
            (x - 10, y + 78),
            (x + 10, y + 78),
            (x + 23, y + 55)
        ]
    )

    # rider body
    pygame.draw.rect(
        screen,
        BLACK,
        (x - 12, y + 15, 24, 40),
        border_radius=8
    )

    # helmet
    pygame.draw.circle(
        screen,
        RED,
        (int(x), int(y + 5)),
        16
    )

    # visor
    pygame.draw.rect(
        screen,
        (30, 30, 30),
        (x - 11, y, 22, 8),
        border_radius=4
    )

    # tail light
    pygame.draw.circle(
        screen,
        RED,
        (int(x), int(y + 72)),
        5
    )


def draw_enemy(obstacle):

    y = obstacle["y"]

    ratio = (y - HORIZON_Y) / (HEIGHT - HORIZON_Y)
    ratio = max(0.1, min(1, ratio))

    x = lane_center(obstacle["lane"], y)

    width = int(20 + ratio * 45)
    height = int(35 + ratio * 85)

    obstacle["rect"] = pygame.Rect(
        int(x - width / 2),
        int(y),
        width,
        height
    )

    pygame.draw.rect(
        screen,
        obstacle["color"],
        obstacle["rect"],
        border_radius=max(3, int(ratio * 10))
    )

    # windshield
    pygame.draw.rect(
        screen,
        BLACK,
        (
            int(x - width * 0.32),
            int(y + height * 0.12),
            int(width * 0.64),
            int(height * 0.20)
        ),
        border_radius=4
    )

    # rear window
    pygame.draw.rect(
        screen,
        BLACK,
        (
            int(x - width * 0.32),
            int(y + height * 0.60),
            int(width * 0.64),
            int(height * 0.18)
        ),
        border_radius=4
    )


def spawn_obstacle():

    color = random.choice([
        RED,
        ORANGE,
        (180, 60, 230),
        (240, 240, 240)
    ])

    obstacles.append({
        "lane": random.randint(0, 2),
        "y": HORIZON_Y + 15,
        "color": color,
        "rect": pygame.Rect(0, 0, 1, 1)
    })


def reset_game():

    global lane
    global speed
    global normal_speed
    global score
    global lap
    global health
    global obstacles
    global spawn_timer
    global game_over

    lane = 1

    speed = 70
    normal_speed = 70

    score = 0
    lap = 1
    health = 100

    obstacles = []

    spawn_timer = 0

    game_over = False


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    braking = False

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                lane = max(0, lane - 1)

            if event.key == pygame.K_RIGHT:
                lane = min(2, lane + 1)

            if event.key == pygame.K_r and game_over:
                reset_game()

    # -----------------------------------------------------
    # KEYBOARD BRAKE
    # -----------------------------------------------------

    keys = pygame.key.get_pressed()

    if keys[pygame.K_DOWN]:
        braking = True

    # -----------------------------------------------------
    # ARDUINO INPUT
    # -----------------------------------------------------

    if arduino:

        while arduino.in_waiting:

            try:

                command = arduino.readline().decode().strip()

                if command == "LEFT" and not game_over:
                    lane = max(0, lane - 1)

                elif command == "RIGHT" and not game_over:
                    lane = min(2, lane + 1)

                elif command == "BRAKE" and not game_over:
                    braking = True

            except:
                pass

    # -----------------------------------------------------
    # SPEED
    # -----------------------------------------------------

    if not game_over:

        if braking:

            speed -= 6

            if speed < brake_speed:
                speed = brake_speed

        else:

            speed += 0.18

            if speed > max_speed:
                speed = max_speed

    # -----------------------------------------------------
    # OBSTACLE GENERATION
    # -----------------------------------------------------

    if not game_over:

        spawn_timer += 1

        current_delay = max(
            35,
            spawn_delay - int(speed / 8)
        )

        if spawn_timer >= current_delay:

            spawn_obstacle()

            spawn_timer = 0

    # -----------------------------------------------------
    # OBSTACLE MOVEMENT
    # -----------------------------------------------------

    if not game_over:

        movement = speed / 38

        for obstacle in obstacles[:]:

            obstacle["y"] += movement

            if obstacle["y"] > HEIGHT + 120:

                obstacles.remove(obstacle)

                score += 10

                if score % 200 == 0:
                    lap += 1

    # -----------------------------------------------------
    # BIKE POSITION
    # -----------------------------------------------------

    bike_x = lane_center(lane, bike_y)

    bike_rect = pygame.Rect(
        int(bike_x - 20),
        bike_y + 5,
        40,
        85
    )

    # -----------------------------------------------------
    # COLLISION
    # -----------------------------------------------------

    for obstacle in obstacles[:]:

        if bike_rect.colliderect(obstacle["rect"]):

            health -= 25

            obstacles.remove(obstacle)

            speed = max(40, speed - 40)

            if health <= 0:

                health = 0
                game_over = True

    # =====================================================
    # DRAW
    # =====================================================

    draw_background()

    draw_lane_lines()

    # distant mountains
    pygame.draw.polygon(
        screen,
        (100, 120, 135),
        [
            (0, HORIZON_Y),
            (150, 40),
            (280, HORIZON_Y)
        ]
    )

    pygame.draw.polygon(
        screen,
        (90, 110, 125),
        [
            (600, HORIZON_Y),
            (760, 45),
            (900, HORIZON_Y)
        ]
    )

    # obstacles
    for obstacle in obstacles:
        draw_enemy(obstacle)

    # bike
    draw_bike(
        int(bike_x),
        bike_y
    )

    # =====================================================
    # HUD
    # =====================================================

    hud = pygame.Surface(
        (WIDTH, 80),
        pygame.SRCALPHA
    )

    hud.fill((0, 0, 0, 145))

    screen.blit(hud, (0, 0))

    speed_text = font.render(
        f"SPEED  {int(speed)} km/h",
        True,
        WHITE
    )

    score_text = font.render(
        f"SCORE  {score}",
        True,
        WHITE
    )

    lap_text = font.render(
        f"LAP  {lap}",
        True,
        WHITE
    )

    health_text = font.render(
        f"HEALTH",
        True,
        WHITE
    )

    screen.blit(speed_text, (30, 25))
    screen.blit(score_text, (280, 25))
    screen.blit(lap_text, (500, 25))
    screen.blit(health_text, (640, 25))

    # health bar
    pygame.draw.rect(
        screen,
        RED,
        (740, 31, 120, 18)
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (740, 31, int(120 * health / 100), 18)
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (740, 31, 120, 18),
        2
    )

    # =====================================================
    # GAME OVER
    # =====================================================

    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(overlay, (0, 0))

        text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                240
            )
        )

        text2 = font.render(
            f"Score: {score}   Lap: {lap}",
            True,
            WHITE
        )

        screen.blit(
            text2,
            (
                WIDTH // 2 - text2.get_width() // 2,
                320
            )
        )

        restart = font.render(
            "Press R to restart",
            True,
            WHITE
        )

        screen.blit(
            restart,
            (
                WIDTH // 2 - restart.get_width() // 2,
                370
            )
        )

    pygame.display.flip()

    clock.tick(60)

# =========================================================
# CLEANUP
# =========================================================

if arduino:
    arduino.close()

pygame.quit()