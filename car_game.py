import pygame
import serial
import random
import time

# -----------------------------
# ARDUINO SETTINGS
# -----------------------------
ARDUINO_PORT = "COM6"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.01)
    time.sleep(2)
    print("Arduino connected!")
except:
    arduino = None
    print("Arduino not connected - keyboard mode active")

# -----------------------------
# PYGAME SETUP
# -----------------------------
pygame.init()

WIDTH = 600
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arduino Highway Dodge")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
ROAD = (55, 55, 55)
GREEN = (40, 150, 60)
BLUE = (30, 130, 255)
RED = (230, 50, 50)
YELLOW = (255, 220, 0)

font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 55, bold=True)

# -----------------------------
# ROAD
# -----------------------------
road_left = 100
road_right = 500

lanes = [150, 275, 400]

# -----------------------------
# PLAYER
# -----------------------------
player_lane = 1

player_width = 60
player_height = 110

player_x = lanes[player_lane]
player_y = 590

# -----------------------------
# GAME VARIABLES
# -----------------------------
enemy_cars = []

enemy_speed = 7
normal_speed = 7
boost_speed = 12

score = 0
spawn_timer = 0
spawn_delay = 65

road_offset = 0

game_over = False


# -----------------------------
# DRAW PLAYER CAR
# -----------------------------
def draw_player_car(x, y):

    pygame.draw.rect(
        screen,
        BLUE,
        (x, y, player_width, player_height),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (x + 10, y + 15, 40, 25),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (x + 10, y + 70, 40, 25),
        border_radius=5
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (x + 12, y + 5),
        5
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (x + 48, y + 5),
        5
    )


# -----------------------------
# DRAW ENEMY
# -----------------------------
def draw_enemy(car):

    pygame.draw.rect(
        screen,
        RED,
        (car["x"], car["y"], 60, 110),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (car["x"] + 10, car["y"] + 15, 40, 25),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (car["x"] + 10, car["y"] + 70, 40, 25),
        border_radius=5
    )


# -----------------------------
# SPAWN CAR
# -----------------------------
def spawn_enemy():

    lane = random.randint(0, 2)

    enemy_cars.append({
        "x": lanes[lane],
        "y": -120
    })


# -----------------------------
# RESET
# -----------------------------
def reset_game():

    global player_lane
    global player_x
    global enemy_cars
    global enemy_speed
    global score
    global spawn_timer
    global game_over

    player_lane = 1
    player_x = lanes[player_lane]

    enemy_cars = []

    enemy_speed = normal_speed

    score = 0

    spawn_timer = 0

    game_over = False


# -----------------------------
# MAIN LOOP
# -----------------------------
running = True

while running:

    boosting = False

    # -------------------------
    # EVENTS
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                if player_lane > 0:
                    player_lane -= 1

            if event.key == pygame.K_RIGHT:
                if player_lane < 2:
                    player_lane += 1

            if event.key == pygame.K_r and game_over:
                reset_game()

    # -------------------------
    # KEYBOARD BOOST
    # -------------------------
    keys = pygame.key.get_pressed()

    if keys[pygame.K_DOWN]:
        boosting = True

    # -------------------------
    # ARDUINO INPUT
    # -------------------------
    if arduino:

        while arduino.in_waiting:

            try:
                command = arduino.readline().decode().strip()

                if command == "LEFT" and not game_over:

                    if player_lane > 0:
                        player_lane -= 1

                elif command == "RIGHT" and not game_over:

                    if player_lane < 2:
                        player_lane += 1

                elif command == "BRAKE" and not game_over:

                    # third button becomes BOOST
                    boosting = True

            except:
                pass

    # -------------------------
    # PLAYER MOVEMENT
    # -------------------------
    target_x = lanes[player_lane]

    player_x += (target_x - player_x) * 0.25

    # -------------------------
    # SPEED
    # -------------------------
    if boosting:
        current_speed = boost_speed
    else:
        current_speed = enemy_speed

    # -------------------------
    # SPAWN ENEMIES
    # -------------------------
    if not game_over:

        spawn_timer += 1

        if spawn_timer >= spawn_delay:

            spawn_enemy()

            spawn_timer = 0

    # -------------------------
    # MOVE ENEMIES
    # -------------------------
    if not game_over:

        for car in enemy_cars[:]:

            car["y"] += current_speed

            if car["y"] > HEIGHT:

                enemy_cars.remove(car)

                score += 1

                if score % 5 == 0:
                    enemy_speed += 0.5

    # -------------------------
    # COLLISION
    # -------------------------
    player_rect = pygame.Rect(
        int(player_x),
        player_y,
        player_width,
        player_height
    )

    for car in enemy_cars:

        enemy_rect = pygame.Rect(
            car["x"],
            car["y"],
            60,
            110
        )

        if player_rect.colliderect(enemy_rect):

            game_over = True

    # -------------------------
    # DRAW
    # -------------------------
    screen.fill(GREEN)

    pygame.draw.rect(
        screen,
        ROAD,
        (road_left, 0, road_right - road_left, HEIGHT)
    )

    pygame.draw.line(
        screen,
        WHITE,
        (road_left, 0),
        (road_left, HEIGHT),
        5
    )

    pygame.draw.line(
        screen,
        WHITE,
        (road_right, 0),
        (road_right, HEIGHT),
        5
    )

    # Moving lane lines
    road_offset += current_speed

    if road_offset > 80:
        road_offset = 0

    for y in range(-80, HEIGHT, 80):

        yy = y + road_offset

        pygame.draw.rect(
            screen,
            WHITE,
            (230, yy, 8, 45)
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (355, yy, 8, 45)
        )

    # Enemies
    for car in enemy_cars:
        draw_enemy(car)

    # Player
    draw_player_car(
        int(player_x),
        player_y
    )

    # Score
    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(score_text, (20, 20))

    speed_text = font.render(
        f"Speed: {int(current_speed * 10)}",
        True,
        WHITE
    )

    screen.blit(speed_text, (420, 20))

    # -------------------------
    # GAME OVER
    # -------------------------
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 170))

        screen.blit(overlay, (0, 0))

        text = big_font.render(
            "CRASH!",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                280
            )
        )

        final_score = font.render(
            f"Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2 - final_score.get_width() // 2,
                350
            )
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                405
            )
        )

    pygame.display.update()

    clock.tick(60)


if arduino:
    arduino.close()

pygame.quit()