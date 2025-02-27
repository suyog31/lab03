import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Rocket Launch ")

DAY_COLOR = (135, 206, 250)
SUN_COLOR = (255, 255, 0)
SPACE_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
RED = (255, 69, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
GRASS_GREEN = (34, 139, 34)
SOIL_BROWN = (139, 69, 19)

rocket_x = WIDTH // 2 - 50
rocket_y = HEIGHT - 220
velocity = 0
acceleration = 0
thrust = -0.015
gravity = 0.05
max_velocity = -3
is_flying = False
boost_active = False

particles = []

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(200)]

sun_position = (WIDTH // 2, HEIGHT // 3)

paused = False
game_state = "START"

GROUND_HEIGHT = 100

max_fuel = 100
fuel = max_fuel
fuel_consumption_rate = 3
fuel_recovery_rate = 0.05

asteroids = []
asteroid_speed = 2
spawn_rate = 25
asteroid_timer = 0

def spawn_asteroid():
    asteroid_x = random.randint(100, WIDTH - 100)
    asteroid_y = -20
    size = random.randint(20, 50)
    asteroids.append([asteroid_x, asteroid_y, size])

def draw_fuel_bar():
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, 200 * (fuel / max_fuel), 20))

def check_collision(rocket_rect, asteroid):
    asteroid_rect = pygame.Rect(asteroid[0] - asteroid[2], asteroid[1] - asteroid[2], asteroid[2] * 2, asteroid[2] * 2)
    return rocket_rect.colliderect(asteroid_rect)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "START" or game_state == "YOU_WIN" or game_state == "YOU_LOST":
                    rocket_y = HEIGHT - 220
                    velocity = 0
                    fuel = max_fuel
                    asteroids.clear()
                    game_state = "PLAYING"
                    is_flying = True
                elif game_state == "PLAYING":
                    game_state = "START"

            if event.key == pygame.K_p:
                paused = not paused

    if not paused:
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and rocket_x > 0:
                rocket_x -= 5
            if keys[pygame.K_RIGHT] and rocket_x < WIDTH - 80:
                rocket_x += 5
            if keys[pygame.K_UP]:
                boost_active = True
            else:
                boost_active = False

            if rocket_y < HEIGHT // 2:
                sky_color = SPACE_COLOR
            else:
                sky_color = (
                    max(0, min(255, DAY_COLOR[0] - abs(int(rocket_y // 5)))),
                    max(0, min(255, DAY_COLOR[1] - abs(int(rocket_y // 5)))),
                    max(0, min(255, DAY_COLOR[2] - abs(int(rocket_y // 5)))) )

            screen.fill(sky_color)

            if rocket_y >= HEIGHT // 2:
                sun_alpha = max(0, 255 - abs(int(rocket_y // 5)))
                sun_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(sun_surface, (*SUN_COLOR, sun_alpha), (50, 50), 50)
                screen.blit(sun_surface, (sun_position[0] - 50, sun_position[1] - 50))

            if rocket_y < HEIGHT // 2:
                for star in stars:
                    pygame.draw.circle(screen, WHITE, star, 2)

            if rocket_y >= HEIGHT // 2:
                pygame.draw.rect(screen, SOIL_BROWN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
                for i in range(0, WIDTH, 20):
                    pygame.draw.rect(screen, GRASS_GREEN, (i, HEIGHT - GROUND_HEIGHT, 20, 20))

            if is_flying:
                if boost_active and fuel > 0:
                    fuel -= fuel_consumption_rate
                elif not boost_active and fuel < max_fuel:
                    fuel += fuel_recovery_rate

                if fuel <= 0:
                    game_state = "YOU_LOST"

                if boost_active:
                    acceleration = thrust * 2
                else:
                    acceleration = thrust

                velocity += acceleration
                velocity = max(velocity, max_velocity)
                rocket_y += velocity
                acceleration += gravity

                for _ in range(3):
                    particles.append([rocket_x + 50, rocket_y + 200, random.randint(2, 5)])

                rocket_body_rect = pygame.Rect(rocket_x + 30, rocket_y + 50, 40, 100)
                rocket_tip = [(rocket_x + 50, rocket_y), (rocket_x + 70, rocket_y + 50), (rocket_x + 30, rocket_y + 50)]
                fin_left = pygame.Rect(rocket_x + 20, rocket_y + 120, 20, 30)
                fin_right = pygame.Rect(rocket_x + 60, rocket_y + 120, 20, 30)

                pygame.draw.polygon(screen, RED, rocket_tip)
                pygame.draw.rect(screen, GRAY, rocket_body_rect)
                pygame.draw.rect(screen, DARK_GRAY, fin_left)
                pygame.draw.rect(screen, DARK_GRAY, fin_right)

                for particle in particles:
                    particle[1] += 2
                    pygame.draw.circle(screen, ORANGE, (particle[0], particle[1]), particle[2])
                    particle[2] -= 0.1

                particles = [p for p in particles if p[2] > 0]

                if rocket_y <= -100:
                    game_state = "YOU_WIN"

            asteroid_timer += 1
            if asteroid_timer >= spawn_rate:
                spawn_asteroid()
                asteroid_timer = 0

            for asteroid in asteroids:
                asteroid[1] += asteroid_speed
                pygame.draw.circle(screen, (139, 69, 19), (asteroid[0], asteroid[1]), asteroid[2])

                rocket_rect = pygame.Rect(rocket_x + 30, rocket_y + 50, 40, 100)
                if check_collision(rocket_rect, asteroid):
                    game_state = "YOU_LOST"
                    break

            asteroids = [a for a in asteroids if a[1] < HEIGHT]

            draw_fuel_bar()

        elif game_state == "YOU_WIN":
            font = pygame.font.Font(None, 36)
            win_text = font.render("YOU WIN! Press Space to Restart", True, WHITE)
            screen.blit(win_text, (WIDTH // 4, HEIGHT // 2))

        elif game_state == "YOU_LOST":
            font = pygame.font.Font(None, 36)
            lose_text = font.render("YOU LOST! Press Space to Restart", True, WHITE)
            screen.blit(lose_text, (WIDTH // 4, HEIGHT // 2))

        if paused:
            font = pygame.font.Font(None, 36)
            pause_text = font.render("PAUSED - Press P to resume", True, WHITE)
            screen.blit(pause_text, (WIDTH // 4, HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()



