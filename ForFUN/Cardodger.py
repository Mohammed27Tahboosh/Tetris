
import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1100, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Police Drift Dodge")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 25, bold=True)
big_font = pygame.font.SysFont("arial", 65, bold=True)

WHITE = (240, 240, 240)
DARK = (24, 34, 40)
ROAD = (43, 54, 60)
YELLOW = (255, 196, 65)
RED = (245, 75, 80)
BLUE = (65, 140, 255)
GREEN = (85, 235, 175)

Vector = pygame.Vector2


def forward(angle):
    rad = math.radians(angle)
    return Vector(math.sin(rad), -math.cos(rad))


def draw_car(position, angle, police=False):
    car = pygame.Surface((36, 60), pygame.SRCALPHA)
    color = WHITE if police else YELLOW

    pygame.draw.rect(car, color, (5, 5, 26, 50), border_radius=6)
    pygame.draw.rect(car, (35, 55, 70), (9, 17, 18, 13))
    pygame.draw.rect(car, (25, 40, 55), (9, 39, 18, 8))

    for x in (1, 31):
        for y in (13, 40):
            pygame.draw.rect(car, (10, 10, 15), (x, y, 5, 10))

    if police:
        pygame.draw.rect(car, RED, (8, 28, 10, 7))
        pygame.draw.rect(car, BLUE, (18, 28, 10, 7))

    rotated = pygame.transform.rotate(car, -angle)
    rect = rotated.get_rect(center=position)
    screen.blit(rotated, rect)


class Car:
    def __init__(self, x, y, police=False):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.angle = 0
        self.police = police
        self.speed = 0

    def update_player(self, keys, dt):
        direction = forward(self.angle)

        gas = keys[pygame.K_w] or keys[pygame.K_UP]
        brake = keys[pygame.K_s] or keys[pygame.K_DOWN]
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        drifting = keys[pygame.K_SPACE]

        if gas:
            self.vel += direction * 520 * dt

        if brake:
            self.vel -= direction * 440 * dt

        self.vel *= 0.985

        if self.vel.length() > 400:
            self.vel.scale_to_length(400)

        self.speed = self.vel.length()

        turn_speed = min(self.speed / 150, 1)

        if left:
            self.angle -= 180 * turn_speed * dt

        if right:
            self.angle += 180 * turn_speed * dt

        sideways = Vector(-direction.y, direction.x)
        lateral_speed = self.vel.dot(sideways)

        grip = 1.8 if drifting else 7.0
        self.vel -= sideways * lateral_speed * min(grip * dt, 1)

        if drifting and self.speed > 100:
            if left:
                self.vel -= sideways * 140 * dt
            if right:
                self.vel += sideways * 140 * dt

        self.pos += self.vel * dt

    def update_police(self, player, dt, difficulty):
        target = player.pos + player.vel * 0.45
        difference = target - self.pos

        if difference.length_squared() < 1:
            return

        desired_angle = math.degrees(
            math.atan2(difference.x, -difference.y)
        )

        angle_difference = (
            desired_angle - self.angle + 180
        ) % 360 - 180

        turn_limit = 105 * dt
        angle_difference = max(
            -turn_limit, min(turn_limit, angle_difference)
        )

        self.angle += angle_difference

        direction = forward(self.angle)
        self.vel += direction * (230 + difficulty * 12) * dt

        self.vel *= 0.985

        max_speed = min(330, 220 + difficulty * 10)

        if self.vel.length() > max_speed:
            self.vel.scale_to_length(max_speed)

        self.pos += self.vel * dt


def draw_background(camera):
    screen.fill(DARK)

    grid = 400
    road_width = 180

    for x in range(-2, 5):
        world_x = int(camera.x // grid + x) * grid
        sx = world_x - camera.x + WIDTH / 2

        pygame.draw.rect(
            screen, ROAD,
            (sx - road_width / 2, 0, road_width, HEIGHT)
        )

        for y in range(0, HEIGHT, 45):
            pygame.draw.line(
                screen, (90, 100, 105),
                (sx, y), (sx, y + 20), 2
            )

    for y in range(-2, 5):
        world_y = int(camera.y // grid + y) * grid
        sy = world_y - camera.y + HEIGHT / 2

        pygame.draw.rect(
            screen, ROAD,
            (0, sy - road_width / 2, WIDTH, road_width)
        )

        for x in range(0, WIDTH, 45):
            pygame.draw.line(
                screen, (90, 100, 105),
                (x, sy), (x + 20, sy), 2
            )


def spawn_police(player):
    angle = random.uniform(0, math.pi * 2)
    distance = random.randint(500, 700)

    x = player.pos.x + math.cos(angle) * distance
    y = player.pos.y + math.sin(angle) * distance

    cop = Car(x, y, True)
    cop.angle = random.randint(0, 360)
    return cop


def reset_game():
    return {
        "player": Car(0, 0),
        "police": [],
        "time": 0,
        "spawn_timer": 0,
        "wrecked": 0,
        "game_over": False
    }


game = reset_game()
best_score = 0
running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.033)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game["game_over"]:
                game = reset_game()

    keys = pygame.key.get_pressed()

    player = game["player"]
    police = game["police"]

    if not game["game_over"]:
        game["time"] += dt
        game["spawn_timer"] += dt

        difficulty = int(game["time"] / 12)
        player.update_player(keys, dt)

        max_police = min(15, 3 + difficulty)
        spawn_delay = max(0.8, 3 - difficulty * 0.15)

        if (
            game["spawn_timer"] >= spawn_delay
            and len(police) < max_police
        ):
            police.append(spawn_police(player))
            game["spawn_timer"] = 0

        for cop in police:
            cop.update_police(player, dt, difficulty)

            if cop.pos.distance_to(player.pos) < 28:
                game["game_over"] = True
                best_score = max(best_score, game["time"])

        # Police can collide with one another
        crashed = set()

        for i in range(len(police)):
            for j in range(i + 1, len(police)):
                if i in crashed or j in crashed:
                    continue

                a = police[i]
                b = police[j]

                if a.pos.distance_to(b.pos) < 28:
                    impact = (a.vel - b.vel).length()

                    if impact > 100:
                        crashed.add(i)
                        crashed.add(j)

        if crashed:
            police[:] = [
                cop for i, cop in enumerate(police)
                if i not in crashed
            ]

            game["wrecked"] += len(crashed)

        # Remove police too far away
        police[:] = [
            cop for cop in police
            if cop.pos.distance_to(player.pos) < 1400
        ]

    camera = player.pos
    draw_background(camera)

    for cop in police:
        screen_pos = (
            cop.pos - camera + Vector(WIDTH / 2, HEIGHT / 2)
        )
        draw_car(screen_pos, cop.angle, True)

    draw_car((WIDTH / 2, HEIGHT / 2), player.angle)

    pygame.draw.rect(screen, (12, 20, 27), (0, 0, WIDTH, 75))

    title = font.render("POLICE DRIFT DODGE", True, GREEN)
    score = font.render(
        f"Survived: {game['time']:.1f}s", True, WHITE
    )
    wrecks = font.render(
        f"Cops Wrecked: {game['wrecked']}", True, YELLOW
    )

    screen.blit(title, (20, 22))
    screen.blit(score, (375, 22))
    screen.blit(wrecks, (700, 22))

    if game["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        busted = big_font.render("BUSTED!", True, RED)
        final = font.render(
            f"Survived {game['time']:.1f} seconds", True, WHITE
        )
        best = font.render(
            f"Best: {best_score:.1f} seconds", True, YELLOW
        )
        restart = font.render(
            "Press R to restart", True, GREEN
        )

        screen.blit(
            busted, busted.get_rect(center=(WIDTH / 2, 265))
        )
        screen.blit(
            final, final.get_rect(center=(WIDTH / 2, 355))
        )
        screen.blit(
            best, best.get_rect(center=(WIDTH / 2, 395))
        )
        screen.blit(
            restart, restart.get_rect(center=(WIDTH / 2, 465))
        )

    pygame.display.flip()

pygame.quit()
