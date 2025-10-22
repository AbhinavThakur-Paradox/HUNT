import pygame
from loading import *

class player_operated(object):
    def __init__(self, folder):
        self.folder = folder
        self.animations = load(self.folder, 128, 128)
        self.frame_count = 0
        self.time = 0
        self.state = "idle_front"

        # Position & rect
        self.x = 300
        self.y = 300
        self.speed = 250
        self.rect = pygame.Rect(self.x , self.y , 50, 50)
        self.rect.topleft = (self.x, self.y)

        # Combat
        self.attack_cooldown = 0
        self.attack_duration = 250
        self.attack_timer = 0
        self.attack_rect = None
        self.attack_applied = False

        # Stats
        self.health = 40
        self.dead = False
        self.logs = []

# Movement & Animation

    def update(self, dt, mov, screen_width, screen_height, attacking):
        if self.dead:
            # Directional death animation
            if "left" in self.state:
                self.state = "death_left"
            elif "right" in self.state:
                self.state = "death_right"
            elif "back" in self.state:
                self.state = "death_back"
            else:
                self.state = "death_front"
            frames = self.animations[self.state]
            if self.frame_count < len(frames) - 1:
                frame_duration = 1000 / len(frames)
                self.time += dt
                if self.time >= frame_duration:
                    self.time = 0
                    self.frame_count += 1
            return

        vel = self.speed * (dt / 1000)

        if "run" in mov:
            vel *= 1.5
        if mov == "walk_back" or mov == "run_back":
            self.y -= vel
        elif mov == "walk_front" or mov == "run_front":
            self.y += vel
        elif mov == "walk_left" or mov == "run_left":
            self.x -= vel
        elif mov == "walk_right" or mov == "run_right":
            self.x += vel

        self.x = max(0, min(screen_width - 128, self.x))
        self.y = max(0, min(screen_height - 128, self.y))

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if attacking and self.attack_cooldown <= 0:
            self.start_attack()

        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_rect = None
                self.attack_applied = False

        # Setting animation state
        if self.attack_timer > 0:
            if "left" in self.state:
                self.state = "attack_left"
            elif "right" in self.state:
                self.state = "attack_right"
            elif "back" in self.state:
                self.state = "attack_back"
            else:
                self.state = "attack_front"
        else:
            self.state = mov if mov in self.animations else "idle_front"

        frames = self.animations[self.state]
        frame_duration = 1000 / len(frames)
        self.time += dt
        if self.time >= frame_duration:
            self.time = 0
            self.frame_count = (self.frame_count + 1) % len(frames)

        self.rect.topleft = (self.x, self.y)

    # Combat
    def start_attack(self):
        self.attack_timer = self.attack_duration
        self.attack_cooldown = 600
        self.attack_applied = False

        if "left" in self.state:
            self.attack_rect = pygame.Rect(self.x - 50, self.y + 40, 50, 50)
        elif "right" in self.state:
            self.attack_rect = pygame.Rect(self.x + 100, self.y + 40, 50, 50)
        elif "back" in self.state:
            self.attack_rect = pygame.Rect(self.x + 30, self.y - 40, 50, 50)
        else:
            self.attack_rect = pygame.Rect(self.x + 30, self.y + 100, 50, 50)

        self.logs.append("Rust attacks!")

    def take_damage(self):
        self.health -= 1
        self.logs.append(f"Rust hit! HP = {self.health}")
        if self.health <= 0:
            self.dead = True
            self.state = "death_front"
            self.logs.append("Rust has fallen!")


    # Rendering

    def render(self, window):
        frames = self.animations[self.state]
        if self.frame_count >= len(frames):
            self.frame_count = 0
        window.blit(frames[self.frame_count], (self.x, self.y))
        if self.attack_rect:
            pygame.draw.rect(window, (255, 0, 0), self.attack_rect, 1)

    def draw_health(self, window):
        bar_width = 100
        bar_height = 10
        x, y = 20, 20
        ratio = max(0, self.health / 5)
        pygame.draw.rect(window, (80, 80, 80), (x, y, bar_width, bar_height))
        pygame.draw.rect(window, (255, 0, 0), (x, y, bar_width * ratio, bar_height))

    def get_logs(self):
        return self.logs[-10:]


class Enemy(object):
    def __init__(self, x, y, folder, targetx, targety):
        self.x = x
        self.y = y
        self.folder = folder
        self.animations = load(folder, 128, 128)
        self.frame_count = 0
        self.time = 0
        self.state = "idle_front"
        self.rect = self.animations[self.state][0].get_rect(topleft=(self.x, self.y))

        # hitbox
        self.hitbox_rect = pygame.Rect(self.x , self.y , 50, 50)

        self.targetx = targetx
        self.targety = targety
        self.vel = 2.2
        self.dead = False
        self.health = 3
        self.death_timer = 0
        self.attack_cooldown = 0

        self.aggro_range = 250

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.dead = True 

    def try_hit_player(self, player):
        if self.attack_cooldown <= 0:
            player.take_damage()
            self.attack_cooldown = 1000

    def update(self, dt, x, y, screen_width, screen_height):
        if self.dead:
            self.death_timer += dt
            return

        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        dx = x - self.x
        dy = y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # follow player only if within  range
        if distance < self.aggro_range:
            if distance != 0:
                self.x += (dx / distance) * self.vel
                self.y += (dy / distance) * self.vel

            # update animation based on direction
            if abs(dx) > abs(dy):
                self.state = "walk_right" if dx > 0 else "walk_left"
            else:
                self.state = "walk_front" if dy > 0 else "walk_back"
        else:
            self.state = "idle_front"

        self.x = max(0, min(screen_width - 128, self.x))
        self.y = max(0, min(screen_height - 128, self.y))

        self.rect.topleft = (self.x , self.y - 20)
        self.hitbox_rect = pygame.Rect(self.x , self.y , 50, 50)

        # Animate
        frames = self.animations[self.state]
        frame_duration = 1000 / len(frames)
        self.time += dt
        if self.time >= frame_duration:
            self.time = 0
            self.frame_count = (self.frame_count + 1) % len(frames)

    def render(self, window):
        frames = self.animations[self.state]
        if self.frame_count >= len(frames):
            self.frame_count = 0
        window.blit(frames[self.frame_count], (self.x, self.y))

    def draw_health(self, window, screen_width):
        bar_width = 50
        bar_height = 5
        x = self.x + 40
        y = self.y - 10
        ratio = max(0, self.health / 3)
        pygame.draw.rect(window, (80, 80, 80), (x, y, bar_width, bar_height))
        pygame.draw.rect(window, (255, 0, 0), (x, y, bar_width * ratio, bar_height))
