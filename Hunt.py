import pygame
import sys
import random
from menu import *
from character import *
from chaos import *

#window resize function
def menu_resize(screen) :
    screen.resolution = pygame.display.get_window_size()
    screen.bg = pygame.transform.scale(screen.img, screen.resolution)

pygame.init()


# Window setup
screen_width = 800
screen_height = 600
window = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("HUNT")

clock = pygame.time.Clock()

# Game setup
menu = Menu(pygame.display.get_window_size(), "main_menu.png")
menu.active = True
game = False
game_over = Menu((screen_width, screen_height), "game_over.png")
game_menu = Menu((screen_width, screen_height), "game_menu.png")
control = Menu((screen_width, screen_height), "controls.png")


# Player
rust = player_operated("mcFrames")

# Enemy list
enemies = []
def spawn_enemy():
    x = random.randint(100, screen_width - 100)
    y = random.randint(100, screen_height - 100)
    enemies.append(Enemy(x, y, "orc_01", rust.x, rust.y))

for _ in range(3):
    spawn_enemy()

respawn_timer = 0
respawn_delay = 3000  # ms

def check_movement():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RSHIFT] and keys[pygame.K_w]:
        return "run_back"
    elif keys[pygame.K_RSHIFT] and keys[pygame.K_s]:
        return "run_front"
    elif keys[pygame.K_RSHIFT] and keys[pygame.K_a]:
        return "run_left"
    elif keys[pygame.K_RSHIFT] and keys[pygame.K_d]:
        return "run_right"
    elif keys[pygame.K_w]:
        return "walk_back"
    elif keys[pygame.K_s]:
        return "walk_front"
    elif keys[pygame.K_a]:
        return "walk_left"
    elif keys[pygame.K_d]:
        return "walk_right"
    else:
        return "idle_front"

running = True
while running:
    window.fill((30, 30, 30))
    dt = clock.tick(60)
    respawn_timer += dt

    #   Events  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.VIDEORESIZE :
            menu_resize(menu)
            menu_resize(game_over)
            menu_resize(game_menu)
            menu_resize(control)
            screen_width, screen_height = pygame.display.get_window_size()

    mov = check_movement()
    keys = pygame.key.get_pressed()
    attacking = keys[pygame.K_o]

    #   MENU SCREEN  
    if menu.active:
        if keys[pygame.K_RETURN]:
            game = True
            menu.active = False
            rust.dead = False
            rust.health = 40
        if keys[pygame.K_g] :
            menu.active = False
            control.active = True
        menu.render(window)

    # controls menu
    if control.active :
        control.render(window)
        if keys[pygame.K_m] :
            menu.active = True
            control.active = False

    # Game over screen
    if rust.dead :
        game_over.render(window)
        if keys[pygame.K_q] :
            game = True
            game_over.active = False
            rust.dead = False
            rust.health = 40
        elif keys[pygame.K_m] :
            game_over.active = False
            menu.active = True
            rust.dead = False

    # in game menu
    if game_menu.active :
        game_menu.render(window)

        if keys[pygame.K_r] :
            game = True
            game_menu.active = False
        elif keys[pygame.K_m] :
            game_menu.active = False
            menu.active = True
    

    #GAME SCREEN
    if game:
        if keys[pygame.K_k]:
            game = False
            game_menu.active = True
        window.fill((30, 30, 30))

        #Update player
        rust.update(dt, mov, screen_width, screen_height, attacking)

        #Update enemies
        for enemy in enemies:
            enemy.update(dt, rust.x, rust.y, screen_width, screen_height)

        #Player attacks enemies 
        if rust.attack_rect and not rust.attack_applied:
            for enemy in enemies:
                if not enemy.dead and rust.attack_rect.colliderect(enemy.hitbox_rect):
                    enemy.take_damage()
                    rust.attack_applied = True
                    break

        #Enemies attack player
        for enemy in enemies:
            if enemy.hitbox_rect.colliderect(rust.rect) and not enemy.dead and not rust.dead:
                enemy.try_hit_player(rust)

        #Remove dead enemies after death timer
        enemies = [e for e in enemies if not (e.dead and e.death_timer >= 1200)]

        #   Respawn new enemies  
        if respawn_timer >= respawn_delay and len(enemies) < 4:
            spawn_enemy()
            respawn_timer = 0

        #   Rendering  
        for enemy in enemies:
            enemy.render(window)
            enemy.draw_health(window, screen_width)

        rust.render(window)
        rust.draw_health(window)

        #   Logs  
        font = pygame.font.SysFont(None, 22)
        logs = rust.get_logs()
        for i, msg in enumerate(logs[-5:]):
            text = font.render(msg, True, (255, 255, 0))
            window.blit(text, (20, 60 + i * 20))

        #   Game over  
        if rust.dead:
            font_big = pygame.font.SysFont(None, 72)
            over = font_big.render("GAME OVER", True, (255, 0, 0))
            window.blit(over, (screen_width // 2 - 200, screen_height // 2 - 50))
            game = False
            game_over.active = True

    pygame.display.update()

pygame.quit()
sys.exit()
