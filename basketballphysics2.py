import pygame
import math
import random
import sys

# ============================================================
# JACKSONVILLE
# 1P VS BOT / 2P LOCAL BASKETBALL
# Pure Pygame - no Pymunk, so no version-compatibility crashes
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1100, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jacksonville")
clock = pygame.time.Clock()

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------

BG = (13, 17, 25)
COURT = (184, 128, 76)
COURT_LIGHT = (205, 150, 91)
WHITE = (245, 245, 245)
BLACK = (20, 20, 24)
ORANGE = (235, 105, 35)
ORANGE_LIGHT = (255, 145, 55)
BLUE = (55, 145, 255)
BLUE_LIGHT = (100, 180, 255)
RED = (245, 70, 85)
RED_LIGHT = (255, 115, 125)
GRAY = (120, 130, 145)
DARK_GRAY = (35, 42, 55)
YELLOW = (255, 215, 80)

# ------------------------------------------------------------
# FONTS
# ------------------------------------------------------------

FONT_SMALL = pygame.font.SysFont("arial", 20, bold=True)
FONT = pygame.font.SysFont("arial", 28, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 52, bold=True)
FONT_HUGE = pygame.font.SysFont("arial", 82, bold=True)

# ------------------------------------------------------------
# COURT CONSTANTS
# ------------------------------------------------------------

FLOOR_Y = 625
PLAYER_RADIUS = 28
BALL_RADIUS = 15

BORDER_X_LEFT = 15
BORDER_X_RIGHT = WIDTH - 15

# --- MODIFIED: Lowered hoop to be 80% of the previous distance from the floor ---
HOOP_Y = 330             
HOOP_REACH = 50          # how far the rim sticks in from the border
HOOP_BAND_HEIGHT = 90    # height of the backboard strip on the wall

# Physics defined per-second and scaled by dt so it stays smooth
GRAVITY_BALL = 1500.0
GRAVITY_PLAYER = 1900.0
AIR_DRAG = 0.999
FLOOR_BOUNCE = 0.72
WALL_BOUNCE = 0.75
PLAYER_FRICTION_PER_SEC = 9.0
PLAYER_ACCEL = 2600.0
PLAYER_MAX_SPEED = 420.0
JUMP_VELOCITY = 700.0

# Aiming arrow
AIM_RADIUS = 60
AIM_MIN_ANGLE = 15
AIM_MAX_ANGLE = 165
AIM_STEP_DEGREES = 4
AIM_TICK_INTERVAL = 0.045
SHOT_SPEED = 600.0


# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def draw_text(text, font, color, x, y, center=True):
    surface = font.render(text, True, color)
    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)


def distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


# ============================================================
# BALL
# ============================================================

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH / 2
        self.y = 360
        self.vx = random.choice([-60, 60])
        self.vy = -60
        self.held_by = None
        self.scored = False
        self.score_timer = 0
        self.trail = []

    def update(self, dt):
        if self.held_by is not None:
            player = self.held_by
            direction = 1 if player.facing_right else -1
            self.x = player.x + direction * 34
            self.y = player.y - 8
            self.vx = 0
            self.vy = 0
            self.trail.clear()
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vy += GRAVITY_BALL * dt
        self.vx *= AIR_DRAG

        if self.y + BALL_RADIUS >= FLOOR_Y:
            self.y = FLOOR_Y - BALL_RADIUS
            if abs(self.vy) > 60:
                self.vy *= -FLOOR_BOUNCE
                self.vx *= 0.82
            else:
                self.vy = 0

        if self.x - BALL_RADIUS <= BORDER_X_LEFT:
            self.x = BORDER_X_LEFT + BALL_RADIUS
            self.vx *= -WALL_BOUNCE

        if self.x + BALL_RADIUS >= BORDER_X_RIGHT:
            self.x = BORDER_X_RIGHT - BALL_RADIUS
            self.vx *= -WALL_BOUNCE

        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

    def launch(self, vx, vy):
        self.held_by = None
        self.vx = vx
        self.vy = vy

    def draw(self):
        for i, (tx, ty) in enumerate(self.trail):
            r = int(BALL_RADIUS * (0.3 + 0.08 * i))
            trail_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*ORANGE, 30 + i * 10), (r, r), r)
            screen.blit(trail_surf, (tx - r, ty - r))

        x = int(self.x)
        y = int(self.y)

        shadow_width = clamp(38 - int(abs(FLOOR_Y - self.y) * 0.04), 8, 38)
        pygame.draw.ellipse(screen, (65, 45, 30),
                             (x - shadow_width, FLOOR_Y - 5, shadow_width * 2, 8))

        pygame.draw.circle(screen, ORANGE, (x, y), BALL_RADIUS)
        pygame.draw.circle(screen, BLACK, (x, y), BALL_RADIUS, 2)
        pygame.draw.arc(screen, BLACK, (x - BALL_RADIUS, y - BALL_RADIUS,
                         BALL_RADIUS * 2, BALL_RADIUS * 2), -1.1, 1.1, 2)
        pygame.draw.arc(screen, BLACK, (x - BALL_RADIUS, y - BALL_RADIUS,
                         BALL_RADIUS * 2, BALL_RADIUS * 2), 2.0, 4.2, 2)
        pygame.draw.line(screen, BLACK, (x - BALL_RADIUS + 3, y), (x + BALL_RADIUS - 3, y), 2)


# ============================================================
# PLAYER
# ============================================================

class Player:
    def __init__(self, x, color, controls, name, is_bot=False):
        self.x = x
        self.y = FLOOR_Y - PLAYER_RADIUS
        self.vx = 0.0
        self.vy = 0.0
        self.color = color
        self.name = name
        self.controls = controls
        self.is_bot = is_bot

        self.facing_right = True
        self.on_ground = True
        self.has_ball = False
        self.shoot_cooldown = 0.0

        # Aiming arrow state
        self.aim_angle = 90.0
        self.aim_dir = 1

    def reset(self, x):
        self.x = x
        self.y = FLOOR_Y - PLAYER_RADIUS
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.has_ball = False
        self.shoot_cooldown = 0.0
        self.aim_angle = 90.0
        self.aim_dir = 1

    def jump(self):
        if self.on_ground:
            self.vy = -JUMP_VELOCITY
            self.on_ground = False

    def move(self, direction, dt):
        if direction != 0:
            self.vx += direction * PLAYER_ACCEL * dt
            self.facing_right = direction > 0

    def update_physics(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vy += GRAVITY_PLAYER * dt

        friction_factor = math.exp(-PLAYER_FRICTION_PER_SEC * dt)
        self.vx *= friction_factor

        if self.y >= FLOOR_Y - PLAYER_RADIUS:
            self.y = FLOOR_Y - PLAYER_RADIUS
            self.vy = 0
            self.on_ground = True

        self.x = clamp(self.x, 35 + PLAYER_RADIUS, WIDTH - 35 - PLAYER_RADIUS)

        if abs(self.vx) > PLAYER_MAX_SPEED:
            self.vx = math.copysign(PLAYER_MAX_SPEED, self.vx)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def update_aim(self, dt, tick_accumulator):
        tick_accumulator += dt
        while tick_accumulator >= AIM_TICK_INTERVAL:
            tick_accumulator -= AIM_TICK_INTERVAL
            self.aim_angle += self.aim_dir * AIM_STEP_DEGREES
            if self.aim_angle >= AIM_MAX_ANGLE:
                self.aim_angle = AIM_MAX_ANGLE
                self.aim_dir = -1
            elif self.aim_angle <= AIM_MIN_ANGLE:
                self.aim_angle = AIM_MIN_ANGLE
                self.aim_dir = 1
        return tick_accumulator

    def aim_vector(self):
        rad = math.radians(self.aim_angle)
        return math.cos(rad), -math.sin(rad)

    def draw(self):
        x = int(self.x)
        y = int(self.y)

        pygame.draw.ellipse(screen, (70, 45, 25), (x - 27, FLOOR_Y - 7, 54, 10))
        pygame.draw.circle(screen, self.color, (x, y), PLAYER_RADIUS)
        pygame.draw.circle(screen, WHITE, (x, y), PLAYER_RADIUS, 2)
        pygame.draw.circle(screen, (238, 190, 145), (x, y - 35), 15)
        pygame.draw.arc(screen, BLACK, (x - 15, y - 49, 30, 22), math.pi, math.pi * 2, 5)

        eye_x = x + (5 if self.facing_right else -5)
        pygame.draw.circle(screen, BLACK, (eye_x, y - 37), 2)

        draw_text("1" if self.name == "BLUE" else "2", FONT_SMALL, WHITE, x, y + 5)

    def draw_aim(self):
        if not self.has_ball:
            return

        center = (self.x, self.y - 15)

        # Dashed guide arc so the sweep range is visible
        guide_rect = pygame.Rect(
            center[0] - AIM_RADIUS, center[1] - AIM_RADIUS,
            AIM_RADIUS * 2, AIM_RADIUS * 2
        )
        pygame.draw.arc(
            screen, (255, 255, 255, 60), guide_rect,
            math.radians(AIM_MIN_ANGLE), math.radians(AIM_MAX_ANGLE), 2
        )

        dx, dy = self.aim_vector()
        tip = (center[0] + dx * AIM_RADIUS, center[1] + dy * AIM_RADIUS)

        pygame.draw.line(screen, YELLOW, center, tip, 4)

        # Arrowhead
        angle = math.atan2(-dy, dx)
        head_len = 12
        left = (
            tip[0] - head_len * math.cos(angle - math.pi / 7),
            tip[1] + head_len * math.sin(angle - math.pi / 7)
        )
        right = (
            tip[0] - head_len * math.cos(angle + math.pi / 7),
            tip[1] + head_len * math.sin(angle + math.pi / 7)
        )
        pygame.draw.polygon(screen, YELLOW, [tip, left, right])


# ============================================================
# HOOP (flush against the border, not a floating structure)
# ============================================================

class Hoop:
    def __init__(self, border_x, direction):
        # direction: +1 for the hoop on the left wall (rim points right)
        #            -1 for the hoop on the right wall (rim points left)
        self.border_x = border_x
        self.y = HOOP_Y
        self.direction = direction
        self.rim_inner = border_x + direction * HOOP_REACH

    def score_check(self, ball, previous_y):
        # Score when the ball actually passes downward through the rim
        # opening. Account for the ball radius so a realistic swish still counts.
        if previous_y < self.y <= ball.y and ball.vy > 0:
            left = min(self.border_x, self.rim_inner)
            right = max(self.border_x, self.rim_inner)

            # --- MODIFIED: Ensure the center of the ball actually falls within the rim ---
            # Added a slight margin (BALL_RADIUS/3) to feel fair, but strict enough to stop ghost goals
            margin = BALL_RADIUS / 3 
            if left - margin <= ball.x <= right + margin:
                return True
        return False

    def draw(self):
        # Backboard strip flush against the wall
        band_rect = pygame.Rect(
            self.border_x - (6 if self.direction > 0 else 0),
            self.y - HOOP_BAND_HEIGHT // 2,
            6,
            HOOP_BAND_HEIGHT
        )
        pygame.draw.rect(screen, WHITE, band_rect)

        # Rim sticking a short distance in from the border
        rim_start = (self.border_x, self.y)
        rim_end = (self.rim_inner, self.y)
        pygame.draw.line(screen, ORANGE_LIGHT, rim_start, rim_end, 7)
        pygame.draw.circle(screen, ORANGE_LIGHT, (int(self.rim_inner), int(self.y)), 5)

        # Simple net
        bottom_y = self.y + 34
        mid_x = (self.border_x + self.rim_inner) / 2
        pygame.draw.line(screen, WHITE, rim_start, (mid_x, bottom_y), 2)
        pygame.draw.line(screen, WHITE, rim_end, (mid_x, bottom_y), 2)
        pygame.draw.line(screen, WHITE, rim_start, rim_end, 1)


# ============================================================
# COURT DRAWING
# ============================================================

def draw_court():
    screen.fill(BG)

    pygame.draw.rect(screen, COURT, (0, 80, WIDTH, FLOOR_Y - 80))

    for x in range(0, WIDTH, 80):
        pygame.draw.line(screen, COURT_LIGHT, (x, 80), (x, FLOOR_Y), 2)

    pygame.draw.rect(screen, DARK_GRAY, (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))

    pygame.draw.rect(screen, WHITE, (BORDER_X_LEFT, 95, WIDTH - 30, FLOOR_Y - 95), 4)

    pygame.draw.line(screen, WHITE, (WIDTH // 2, 95), (WIDTH // 2, FLOOR_Y), 3)
    pygame.draw.circle(screen, WHITE, (WIDTH // 2, 380), 65, 3)

    pygame.draw.line(screen, COURT_LIGHT, (0, FLOOR_Y - 1), (WIDTH, FLOOR_Y - 1), 4)


# ============================================================
# GAMEPLAY HELPERS
# ============================================================

def handle_ball_pickup(player, ball):
    if ball.held_by is not None:
        return
    d = distance(player.x, player.y, ball.x, ball.y)
    if d < PLAYER_RADIUS + BALL_RADIUS + 18:
        if ball.y > player.y - 65:
            ball.held_by = player
            player.has_ball = True


def shoot_player(player, ball):
    if ball.held_by != player:
        return
    if player.shoot_cooldown > 0:
        return

    dx, dy = player.aim_vector()
    ball.x = player.x + dx * 45
    ball.y = (player.y - 15) + dy * 45
    ball.launch(dx * SHOT_SPEED, dy * SHOT_SPEED)

    player.has_ball = False
    player.shoot_cooldown = 0.4


def update_bot(bot, ball, target_hoop, dt):
    target_x = ball.x

    if ball.held_by == bot:
        # Bot's ideal aim is toward its own hoop (up-and-left since bot
        # defends/attacks the left hoop). Wait until the ticking arrow
        # swings near that band, then fire - same mechanic the player uses.
        ideal_low, ideal_high = 105, 150
        close_enough = abs(bot.x - target_hoop.rim_inner) < 260

        if close_enough and ideal_low <= bot.aim_angle <= ideal_high:
            if random.random() < 0.12:
                shoot_player(bot, ball)

        # Position itself at a reasonable shooting distance
        desired_x = target_hoop.border_x + 220
        if bot.x > desired_x + 15:
            bot.move(-1, dt)
        elif bot.x < desired_x - 15:
            bot.move(1, dt)

    elif ball.held_by is not None:
        target_x = ball.held_by.x
        if target_x > bot.x + 15:
            bot.move(1, dt)
        elif target_x < bot.x - 15:
            bot.move(-1, dt)
    else:
        if target_x > bot.x + 15:
            bot.move(1, dt)
        elif target_x < bot.x - 15:
            bot.move(-1, dt)

    if (ball.y < bot.y - 35 and abs(ball.x - bot.x) < 90
            and bot.on_ground and random.random() < 0.055 * 60 * dt):
        bot.jump()

    if (ball.held_by is not None and ball.held_by != bot
            and abs(ball.x - bot.x) < 100 and bot.on_ground
            and random.random() < 0.025 * 60 * dt):
        bot.jump()


def draw_score(score_blue, score_red):
    pygame.draw.rect(screen, BG, (0, 0, WIDTH, 80))

    draw_text(f"BLUE  {score_blue}", FONT_BIG, BLUE_LIGHT, 250, 40)
    draw_text(f"{score_red}  RED", FONT_BIG, RED_LIGHT, WIDTH - 250, 40)

    draw_text("FIRST TO 11", FONT_SMALL, GRAY, WIDTH // 2, 25)
    draw_text("JACKSONVILLE", FONT, WHITE, WIDTH // 2, 52)


# ============================================================
# MENU
# ============================================================

def menu():
    while True:
        screen.fill(BG)

        pygame.draw.circle(screen, (25, 32, 44), (100, 100), 170)
        pygame.draw.circle(screen, (25, 32, 44), (WIDTH - 100, HEIGHT - 100), 200)

        pygame.draw.circle(screen, ORANGE, (WIDTH // 2, 130), 50)
        pygame.draw.circle(screen, BLACK, (WIDTH // 2, 130), 50, 3)
        pygame.draw.line(screen, BLACK, (WIDTH // 2 - 45, 130), (WIDTH // 2 + 45, 130), 3)

        draw_text("JACKSONVILLE", FONT_HUGE, WHITE, WIDTH // 2, 260)

        pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 230, 390, 460, 65), border_radius=14)
        pygame.draw.rect(screen, RED, (WIDTH // 2 - 230, 480, 460, 65), border_radius=14)

        draw_text("1  •  PLAY VS BOT", FONT, WHITE, WIDTH // 2, 422)
        draw_text("2  •  TWO PLAYER", FONT, WHITE, WIDTH // 2, 512)

        draw_text("BLUE: A/D MOVE, W JUMP, S SHOOT", FONT_SMALL, GRAY, WIDTH // 2, 610)
        draw_text("RED: ARROWS MOVE/JUMP, DOWN ARROW SHOOT", FONT_SMALL, GRAY, WIDTH // 2, 640)
        draw_text("Time your shot with the ticking arrow above your head", FONT_SMALL, GRAY, WIDTH // 2, 668)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "1P"
                if event.key == pygame.K_2:
                    return "2P"

        clock.tick(FPS)


# ============================================================
# WIN SCREEN
# ============================================================

def win_screen(winner):
    timer = 0.0

    while timer < 8.0:
        screen.fill(BG)

        draw_text(winner, FONT_HUGE, BLUE_LIGHT if winner == "BLUE" else RED_LIGHT,
                  WIDTH // 2, 220)
        draw_text("WINS!", FONT_HUGE, WHITE, WIDTH // 2, 310)
        draw_text("First to 11", FONT, GRAY, WIDTH // 2, 390)
        draw_text("Press ENTER to play again", FONT, WHITE, WIDTH // 2, 490)
        draw_text("Press ESC for menu", FONT_SMALL, GRAY, WIDTH // 2, 535)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "RESTART"
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

        dt = clock.tick(FPS) / 1000.0
        timer += dt

    return "MENU"


# ============================================================
# GAME
# ============================================================

def game(mode):
    blue_controls = {
        "left": pygame.K_a, "right": pygame.K_d,
        "jump": pygame.K_w, "shoot": pygame.K_s
    }
    red_controls = {
        "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
        "jump": pygame.K_UP, "shoot": pygame.K_DOWN
    }

    blue = Player(280, BLUE, blue_controls, "BLUE")
    red = Player(WIDTH - 280, RED, red_controls, "RED", is_bot=(mode == "1P"))

    left_hoop = Hoop(BORDER_X_LEFT, 1)
    right_hoop = Hoop(BORDER_X_RIGHT, -1)

    ball = Ball()

    score_blue = 0
    score_red = 0

    goal_message = ""
    goal_timer = 0.0

    blue_tick_acc = 0.0
    red_tick_acc = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 1 / 30)

        # ------------------------------------------------
        # EVENTS
        # ------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

                if event.key == blue.controls["jump"]:
                    blue.jump()
                if event.key == blue.controls["shoot"]:
                    shoot_player(blue, ball)

                if not red.is_bot:
                    if event.key == red.controls["jump"]:
                        red.jump()
                    if event.key == red.controls["shoot"]:
                        shoot_player(red, ball)

        # ------------------------------------------------
        # KEYBOARD (held keys)
        # ------------------------------------------------
        keys = pygame.key.get_pressed()

        blue_direction = 0
        if keys[blue.controls["left"]]:
            blue_direction -= 1
        if keys[blue.controls["right"]]:
            blue_direction += 1
        blue.move(blue_direction, dt)

        if not red.is_bot:
            red_direction = 0
            if keys[red.controls["left"]]:
                red_direction -= 1
            if keys[red.controls["right"]]:
                red_direction += 1
            red.move(red_direction, dt)
        else:
            update_bot(red, ball, left_hoop, dt)

        # ------------------------------------------------
        # AIM ARROW TICKING (only while holding the ball)
        # ------------------------------------------------
        if ball.held_by == blue:
            blue_tick_acc = blue.update_aim(dt, blue_tick_acc)
        if ball.held_by == red:
            red_tick_acc = red.update_aim(dt, red_tick_acc)

        # ------------------------------------------------
        # PHYSICS
        # ------------------------------------------------
        blue.update_physics(dt)
        red.update_physics(dt)

        previous_ball_y = ball.y
        ball.update(dt)

        # ------------------------------------------------
        # PLAYER / PLAYER COLLISION
        # ------------------------------------------------
        d = distance(blue.x, blue.y, red.x, red.y)
        if d < PLAYER_RADIUS * 2:
            if d == 0:
                d = 1
            push = (PLAYER_RADIUS * 2 - d) / 2
            if blue.x < red.x:
                blue.x -= push
                red.x += push
            else:
                blue.x += push
                red.x -= push

        handle_ball_pickup(blue, ball)
        handle_ball_pickup(red, ball)

        if ball.held_by is None:
            for player in (blue, red):
                d = distance(player.x, player.y - 10, ball.x, ball.y)
                if d < PLAYER_RADIUS + BALL_RADIUS + 8:
                    direction = 1 if ball.x > player.x else -1
                    ball.vx += direction * 110
                    if ball.y < player.y:
                        ball.vy -= 90

        # ------------------------------------------------
        # SCORING (every basket is worth 1 point)
        # ------------------------------------------------
        if ball.held_by is None and not ball.scored:
            if left_hoop.score_check(ball, previous_ball_y):
                ball.scored = True
                score_red += 1
                goal_message = "RED +1"
                goal_timer = 1.3

            elif right_hoop.score_check(ball, previous_ball_y):
                ball.scored = True
                score_blue += 1
                goal_message = "BLUE +1"
                goal_timer = 1.3

        if ball.scored:
            ball.score_timer += dt
            if ball.score_timer > 0.5:
                ball.reset()
                blue.reset(280)
                red.reset(WIDTH - 280)
                blue_tick_acc = 0.0
                red_tick_acc = 0.0

        # ------------------------------------------------
        # WIN CONDITION
        # ------------------------------------------------
        if score_blue >= 11:
            result = win_screen("BLUE")
            return "RESTART" if result == "RESTART" else "MENU"

        if score_red >= 11:
            result = win_screen("RED")
            return "RESTART" if result == "RESTART" else "MENU"

        if goal_timer > 0:
            goal_timer -= dt

        # ------------------------------------------------
        # DRAW
        # ------------------------------------------------
        draw_court()
        left_hoop.draw()
        right_hoop.draw()

        blue.draw_aim()
        red.draw_aim()

        blue.draw()
        red.draw()
        ball.draw()
        draw_score(score_blue, score_red)

        if ball.held_by is not None:
            draw_text(f"{ball.held_by.name} HAS BALL", FONT_SMALL, WHITE, WIDTH // 2, 610)

        if goal_timer > 0:
            alpha = clamp(int(goal_timer * 220), 0, 255)
            goal_surface = FONT_BIG.render(goal_message, True, YELLOW)
            goal_surface.set_alpha(alpha)
            screen.blit(goal_surface, (WIDTH // 2 - goal_surface.get_width() // 2, 125))

        pygame.display.flip()


# ============================================================
# MAIN
# ============================================================

def main():
    while True:
        mode = menu()
        while True:
            result = game(mode)
            if result == "RESTART":
                continue
            break


if __name__ == "__main__":
    main()