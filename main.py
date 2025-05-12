import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player
from enemies import FatGirlEnemy, WolfEnemy
from spawner import Spawner
import random
from game_state import GameState
from hitboxes import get_player_hitbox, get_enemy_hitbox, get_attack_hitbox
from game_sounds import GameSounds
from effects import Effects

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


def update_game(player, spawner, enemies, kills, game_state, effects):
    # Player input and update
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()
    
    # Atualizar o HUD da ultimate com base no estado da mana e da ultimate
    is_ultimate_ready = player.mana >= player.max_mana and not player.ultimate_active
    
    # Adicionar ou atualizar o efeito do HUD da ultimate
    effects.add_ultimate_hud(is_ready=is_ultimate_ready)

    # Spawn enemies
    new_enemy = spawner.update(player_alive=(player.hp > 0))
    if new_enemy:
        enemies.append(new_enemy)

    # Handle Ultimate ability effects if active
    if player.ultimate_active:
        # Check if we need to create the ultimate visual effects
        if hasattr(player, 'ultimate_effect_created') and player.ultimate_effect_created:
            # Create the main ultimate visual effect in the direction the player was facing when activated
            player_centerx = player.x + 90
            player_top = player.y
            player_position = (player_centerx, player_top)
            
            # Use the stored direction from when the ultimate was activated
            ultimate_direction = player.ultimate_direction if hasattr(player, 'ultimate_direction') else player.direction
            
            # Adiciona o efeito direcional da ultimate
            effects.add_ultimate_effect(player_position, ultimate_direction)
            
            # Adiciona o efeito central do master_cum
            effects.add_master_cum_effect()
            
            # Reproduzir o som da ultimate
            GameSounds.play_ultimate_effect()
                
            player.ultimate_effect_created = False  # Reset the flag
            
        # Apply Ultimate damage to enemies in the correct direction (only once)
        if hasattr(player, 'ultimate_damage_pending') and player.ultimate_damage_pending:
            # Get the direction the player was facing when the ultimate was activated
            ultimate_direction = player.ultimate_direction if hasattr(player, 'ultimate_direction') else player.direction
            
            # Apply damage to enemies in that direction only
            player_centerx = player.x + 90
            player_centery = player.y + 90  # Centro vertical do jogador
            enemies_hit = 0
            
            # Obter o tamanho do último frame (frame 4) da animação da ultimate para usar como alcance
            ultimate_range = 0
            if effects.ult_frames[ultimate_direction]:
                # O último frame (índice 3) é o maior e define o alcance máximo
                ultimate_range = effects.ult_frames[ultimate_direction][3].get_width()
                
            # Se não conseguir obter o tamanho, use um valor padrão
            if ultimate_range == 0:
                ultimate_range = 400  # Valor padrão caso não consiga obter o tamanho do frame
                
            print(f"Ultimate range: {ultimate_range} pixels")
            
            for enemy in enemies:
                if enemy.state != 'dead':
                    # Calcular o centro do inimigo
                    enemy_centerx = enemy.x + (enemy.width // 2 if hasattr(enemy, 'width') else 90)
                    enemy_centery = enemy.y + (enemy.height // 2 if hasattr(enemy, 'height') else 90)
                    
                    # Verificar se o inimigo está na direção correta
                    is_to_right = enemy_centerx > player_centerx
                    is_to_left = enemy_centerx < player_centerx
                    
                    # Calcular a distância horizontal entre o jogador e o inimigo
                    horizontal_distance = abs(enemy_centerx - player_centerx)
                    
                    # Verificar se o inimigo está dentro do alcance e na direção correta
                    if ((ultimate_direction == 'right' and is_to_right) or 
                        (ultimate_direction == 'left' and is_to_left)) and \
                       horizontal_distance <= ultimate_range:
                        
                        # Ultimate deals significant damage
                        ultimate_dmg = 50  # Dano fatal para inimigos dentro do alcance
                        enemy.take_damage(ultimate_dmg)
                        enemies_hit += 1
                        
                        # Não adicionamos mais o efeito milky para inimigos mortos pela ultimate
            
            # Print debug info about enemies hit
            print(f"Ultimate hit {enemies_hit} enemies in the {ultimate_direction} direction")
            
            # Reset the flag so we don't apply damage again
            player.ultimate_damage_pending = False
    
    # Verificar se há efeitos de ultimate ativos e se inimigos entraram na área de efeito
    active_ultimate_effects = [effect for effect in effects.effects 
                              if effect['type'] == 'ultimate_animated' and 'effect_area' in effect]
    
    # Se há efeitos de ultimate ativos, verificar inimigos entrando na área
    for effect in active_ultimate_effects:
        effect_area = effect['effect_area']
        direction = effect_area['direction']
        enemies_hit = 0
        
        for enemy in enemies:
            if enemy.state != 'dead':
                # Calcular o centro do inimigo
                enemy_centerx = enemy.x + (enemy.width // 2 if hasattr(enemy, 'width') else 90)
                
                # Verificar se o inimigo está dentro da área de efeito
                is_in_effect_area = (enemy_centerx >= effect_area['x_start'] and 
                                    enemy_centerx <= effect_area['x_end'])
                
                if is_in_effect_area:
                    # Ultimate deals significant damage to enemies that enter the effect area
                    ultimate_dmg = 50  # Dano fatal
                    enemy.take_damage(ultimate_dmg)
                    enemies_hit += 1
                    
                    # Não adicionamos mais o efeito milky para inimigos mortos pela ultimate
        
        if enemies_hit > 0:
            print(f"Ultimate caught {enemies_hit} enemies entering the effect area!")
    
    # Enemy collisions - player is invulnerable during ultimate
    player_hitbox = get_player_hitbox(player)
    for enemy in enemies:
        enemy_hitbox = get_enemy_hitbox(enemy)
        enemy.update(player)
        if enemy.state != 'dead' and player_hitbox.colliderect(enemy_hitbox):
            if enemy.dmg_cooldown == 0 and not player.ultimate_active:  # No damage during ultimate
                dmg = random.randint(enemy.dmg_min, enemy.dmg_max)
                player.take_damage(dmg)
                enemy.dmg_cooldown = 30

    # Player attack
    min_dmg = 1
    max_dmg = 5
    if player.state == 'attack':
        if not hasattr(player, 'attack_hit_set'):
            player.attack_hit_set = set()
        attack_hitbox = get_attack_hitbox(player)
        for idx, enemy in enumerate(enemies):
            enemy_hitbox = get_enemy_hitbox(enemy)
            if enemy.state != 'dead' and (attack_hitbox.colliderect(enemy_hitbox) or player_hitbox.colliderect(enemy_hitbox)):
                if idx not in player.attack_hit_set:
                    dmg = random.randint(min_dmg, max_dmg)
                    if dmg == max_dmg:
                        GameSounds.play_milky_effect()
                        player_centerx = player.x + 90
                        player_top = player.y
                        player_position = (player_centerx, player_top)
                        effects.add_milky_effect(duration=60, player_position=player_position)
                        critical_dmg = dmg + random.randint(min_dmg, max_dmg)
                        # Cura o jogador com o mesmo valor do dano crítico
                        player.heal(critical_dmg)
                        dmg = critical_dmg
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


def draw_game(screen, background, player, enemies, hud, elapsed_time, kills, effects):
    background.update()
    background.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    player.draw(screen)
    hud.draw_hud(screen, player, int(elapsed_time), kills)
    # Desenha os efeitos visuais por cima de tudo
    effects.draw(screen)
    
    # DEBUG: Desenhar a área de efeito da ultimate (comentado, apenas para debug)
    # for effect in effects.effects:
    #     if effect['type'] == 'ultimate_animated' and 'effect_area' in effect:
    #         area = effect['effect_area']
    #         pygame.draw.rect(screen, (255, 0, 0, 128), 
    #                         (area['x_start'], area['y_center'] - 50, 
    #                          area['x_end'] - area['x_start'], 100), 2)


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
    effects = Effects()  # Inicializa o gerenciador de efeitos visuais
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
            update_game(player, spawner, enemies, kills, game_state, effects)
            effects.update()  # Atualiza os efeitos visuais
            elapsed_time += 1/FPS if FPS else 1/60
            draw_game(screen, background, player, enemies, hud, elapsed_time, kills[0], effects)
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
