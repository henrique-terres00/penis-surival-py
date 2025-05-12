import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player
from enemies import FatGirlEnemy, WolfEnemy
from spawner import Spawner
import random
from game_state import GameState
from hitboxes import get_player_hitbox, get_enemy_hitbox, get_attack_hitbox

from background import ParallaxBackground

BACKGROUND_DIR = os.path.join('assets', 'background')

def handle_events(game_state, restart_flag):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 'quit'
        game_state.handle_event(event)
    if restart_flag['restart']:
        return 'restart'
    return None


def update_game(player, spawner, enemies, kills, game_state):
    # Player input and update
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()

    # Spawn enemies
    new_enemy = spawner.update(player_alive=(player.hp > 0))
    if new_enemy:
        enemies.append(new_enemy)

    # Enemy collisions
    player_hitbox = get_player_hitbox(player)
    for enemy in enemies:
        enemy_hitbox = get_enemy_hitbox(enemy)
        enemy.update(player)
        if enemy.state != 'dead' and player_hitbox.colliderect(enemy_hitbox):
            if enemy.dmg_cooldown == 0:
                dmg = random.randint(enemy.dmg_min, enemy.dmg_max)
                player.take_damage(dmg)
                enemy.dmg_cooldown = 30

    # Player attack
    if player.state == 'attack':
        if not hasattr(player, 'attack_hit_set'):
            player.attack_hit_set = set()
        attack_hitbox = get_attack_hitbox(player)
        for idx, enemy in enumerate(enemies):
            enemy_hitbox = get_enemy_hitbox(enemy)
            if enemy.state != 'dead' and (attack_hitbox.colliderect(enemy_hitbox) or player_hitbox.colliderect(enemy_hitbox)):
                if idx not in player.attack_hit_set:
                    dmg = random.randint(1, 5)
                    enemy.take_damage(dmg)
                    player.attack_hit_set.add(idx)
                    if enemy.hp <= 0:
                        kills[0] += 1
                        if enemy.__class__.__name__ == 'WolfEnemy':
                            player.mana = min(player.max_mana, player.mana + 10)
                        elif enemy.__class__.__name__ == 'FatGirlEnemy':
                            player.mana = min(player.max_mana, player.mana + 12)
    else:
        player.attack_hit_set = set()


def draw_game(screen, background, player, enemies, hud, elapsed_time, kills):
    background.update()
    background.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    player.draw(screen)
    hud.draw_hud(screen, player, int(elapsed_time), kills)


def main(start_playing=False):
    import hud
    from game_sounds import GameSounds
    pygame.init()
    GameSounds.play_soundtrack()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Penis Survival')
    clock = pygame.time.Clock()

    background = ParallaxBackground(BACKGROUND_DIR)
    player = Player()
    enemies = []
    spawner = Spawner()
    game_state = GameState()
    if start_playing:
        game_state.set_state(GameState.PLAYING)
    restart_flag = {'restart': False}
    def restart():
        restart_flag['restart'] = True
    game_state.set_restart_callback(restart)
    font = pygame.font.SysFont(None, 60)
    kills = [0]
    elapsed_time = 0
    running = True

    while running:
        # --- EVENTS AND STATE ---
        result = handle_events(game_state, restart_flag)
        if result == 'quit':
            game_state.fade_out(screen, background)
            return 'quit'
        if result == 'restart':
            return 'restart'

        game_state.update(player)

        # --- MENU/PAUSE/GAME OVER ---
        if not game_state.is_playing():
            # Se voltou ao menu, reinicialize o jogo
            if game_state.state == GameState.MENU:
                player = Player()
                enemies = []
                spawner = Spawner()
                kills = [0]
                elapsed_time = 0
            leave_game = game_state.draw(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, background)
            pygame.display.flip()
            if game_state.state == 'leave_game' or leave_game:
                game_state.fade_out(screen, background)
                return 'quit'
            clock.tick(FPS)
            continue

        # --- MAIN GAMEPLAY ---
        if game_state.state == GameState.PLAYING:
            update_game(player, spawner, enemies, kills, game_state)
            elapsed_time += 1/FPS if FPS else 1/60
            draw_game(screen, background, player, enemies, hud, elapsed_time, kills[0])
            # Save kills/time for game over
            if player.hp <= 0 and game_state.state != 'game_over':
                game_state.last_kills = kills[0]
                game_state.last_time = int(elapsed_time)
        else:
            # Draw menu, settings, pause, game over, etc
            game_state.draw(screen, pygame.font.SysFont(None, 60), SCREEN_WIDTH, SCREEN_HEIGHT, background)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return None

if __name__ == '__main__':
    start_playing = False
    while True:
        result = main(start_playing=start_playing)
        if result == 'restart':
            start_playing = True
            continue
        elif result == 'menu':
            start_playing = False
            continue
        elif result == 'quit':
            break
        else:
            break
