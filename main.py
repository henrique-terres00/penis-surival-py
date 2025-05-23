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
from health_potion import HealthPotion
from mana_potion import ManaPotion
from milky_grenade import MilkyGrenade

from background import ParallaxBackground

BACKGROUND_DIR = os.path.join('assets', 'background', 'jungle')

def handle_events(game_state, restart_flag):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 'quit'
        game_state.handle_event(event)
    if restart_flag['restart']:
        return 'restart'
    return None


def update_game(player, spawner, enemies, kills, game_state, effects, potions, grenades):
    # Player input and update
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()
    
    # We no longer need to update the ultimate HUD here as it's now handled by the skill icons in the center top of the screen

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
            
            # Add the directional effect of the ultimate
            effects.add_ultimate_effect(player_position, ultimate_direction)
            
            # Add the central effect of master_cum
            effects.add_master_cum_effect()
            
            # Play the ultimate sound
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
            
            # Get the size of the last frame (frame 4) of the ultimate animation to use as range
            ultimate_range = 0
            if effects.ult_frames[ultimate_direction]:
                # The last frame (index 3) is the largest and defines the maximum range
                ultimate_range = effects.ult_frames[ultimate_direction][3].get_width()
                
            # If unable to get the size, use a default value
            if ultimate_range == 0:
                ultimate_range = 400  # Default value in case unable to get the frame size
                
            # Get the ultimate effect area from the effects list
            ultimate_effect_area = None
            for effect in effects.effects:
                if effect['type'] == 'ultimate_animated':
                    ultimate_effect_area = effect.get('effect_area')
                    break
            
            # If we couldn't find the effect area, create a default one based on the calculated range
            if not ultimate_effect_area:
                # Create a default effect area
                ultimate_effect_area = {
                    'direction': ultimate_direction,
                    'x_start': player_centerx if ultimate_direction == 'left' else player_centerx,
                    'x_end': player_centerx - ultimate_range if ultimate_direction == 'left' else player_centerx + ultimate_range,
                    'y_top': player_centery - 90,  # Approximate height of the player
                    'y_bottom': player_centery + 90
                }
                
            # Use the full effect area (horizontal and vertical) with proper hitbox collision
            for enemy in enemies:
                if enemy.state != 'dead':
                    # Ensure enemy has width and height attributes
                    enemy_width = getattr(enemy, 'width', 180)  # Default to ENEMY_SIZE[0]
                    enemy_height = getattr(enemy, 'height', 180)  # Default to ENEMY_SIZE[1]
                    
                    # Create a pygame.Rect for the enemy's hitbox
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy_width, enemy_height)
                    
                    # Check if the enemy is in the correct direction
                    enemy_centerx = enemy.x + (enemy_width // 2)
                    is_to_right = enemy_centerx > player_centerx
                    is_to_left = enemy_centerx < player_centerx
                    
                    # Only check collision if the enemy is in the correct direction
                    correct_direction = (ultimate_direction == 'right' and is_to_right) or \
                                       (ultimate_direction == 'left' and is_to_left)
                    
                    # Check for collision using pygame.Rect.colliderect
                    collision_detected = False
                    if correct_direction and 'hitbox_rect' in ultimate_effect_area:
                        # Use the hitbox_rect for collision detection
                        collision_detected = ultimate_effect_area['hitbox_rect'].colliderect(enemy_rect)
                        
                        # Debug information removed
                    
                    # Check if the enemy is within the effect area
                    if collision_detected:
                        # Ultimate deals significant damage
                        ultimate_dmg = 50  # Fatal damage for enemies within range
                        enemy.take_damage(ultimate_dmg)
                        enemies_hit += 1
                        
                        # We no longer add the milky effect for enemies killed by the ultimate
            
            # Print debug info about enemies hit
            # Ultimate hit enemies in the specified direction
            
            # Reset the flag so we don't apply damage again
            player.ultimate_damage_pending = False
    
    # We removed the second collision check for the Ultimate to simplify the code
    # The first check (when the Ultimate is activated) is already sufficient for the desired effect
    
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
                        # Heal the player with the same value as the critical damage
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
        
    # Check for dead enemies to drop items
    for enemy in enemies:
        if enemy.state == 'dead' and enemy.drop_type and not enemy.item_dropped:
            # Check drop chance
            if random.random() <= enemy.drop_chance:
                # Create the appropriate item at the enemy's position
                drop_x = enemy.x + 70  # Adjust position to the center of the enemy
                drop_y = enemy.y + 70
                
                if enemy.drop_type == 'health_potion':
                    item = HealthPotion(drop_x, drop_y)
                    potions.append(item)
                elif enemy.drop_type == 'mana_potion':
                    item = ManaPotion(drop_x, drop_y)
                    potions.append(item)
                    
            enemy.item_dropped = True
            
    # Handle Milky Grenade creation if player has thrown one
    if hasattr(player, 'grenade_thrown') and player.grenade_thrown:
        # Create a new grenade at the player's position
        x, y = player.grenade_position
        grenade = MilkyGrenade(x, y, player.grenade_direction)
        grenades.append(grenade)
        
        # Reset the flag
        player.grenade_thrown = False
    
    # Update grenades and check for explosions
    for grenade in grenades[:]:
        grenade.update()
        
        # If grenade is exploding, check for enemy damage
        if grenade.exploding:
            explosion_rect = grenade.get_explosion_rect()
            if explosion_rect:
                for enemy in enemies:
                    if enemy.state != 'dead':
                        # Ensure enemy has width and height attributes
                        enemy_width = getattr(enemy, 'width', 180)  # Default to ENEMY_SIZE[0]
                        enemy_height = getattr(enemy, 'height', 180)  # Default to ENEMY_SIZE[1]
                        
                        # Create a pygame.Rect for the enemy's hitbox
                        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy_width, enemy_height)
                        if explosion_rect.colliderect(enemy_rect):
                            # Calculate damage based on distance from explosion center
                            dx = (enemy.x + enemy_width/2) - (grenade.x)
                            dy = (enemy.y + enemy_height/2) - (grenade.y)
                            distance = (dx**2 + dy**2)**0.5
                            
                            # Maximum damage at center, decreasing with distance
                            max_damage = 40
                            min_damage = 10
                            damage_factor = max(0, 1 - distance / grenade.explosion_radius)
                            damage = int(min_damage + damage_factor * (max_damage - min_damage))
                            
                            enemy.take_damage(damage)
                            if enemy.hp <= 0:
                                kills[0] += 1
                                if enemy.__class__.__name__ == 'WolfEnemy':
                                    player.mana = min(player.max_mana, player.mana + 10)
                                elif enemy.__class__.__name__ == 'FatGirlEnemy':
                                    player.mana = min(player.max_mana, player.mana + 12)
        
        # Remove inactive grenades
        if not grenade.active:
            grenades.remove(grenade)
    
    # Update potions and other items
    for item in potions[:]:  # Use a copy of the list to be able to remove items during iteration
        item.update()
        
        # Check collision with the player
        player_hitbox = get_player_hitbox(player)
        if item.can_collect() and player_hitbox.colliderect(item.rect):
            # Player collects the item
            if isinstance(item, HealthPotion):
                # Health potion
                heal_amount = item.collect()
                player.hp = min(player.max_hp, player.hp + heal_amount)
                # Add "HEAL" text effect at the potion's position
                player.damage_popups.append([f"{heal_amount}", item.x, item.y - 30, 255, 0, "heal"])
            elif isinstance(item, ManaPotion):
                # Mana potion
                mana_amount = item.collect()
                player.mana = min(player.max_mana, player.mana + mana_amount)
                # Add "MANA" text effect at the potion's position
                player.damage_popups.append([f"{mana_amount}", item.x, item.y - 30, 255, 0, "mana"])
def draw_game(screen, player, enemies, background, effects, potions, grenades, elapsed_time, kills, hud):
    background.update()
    background.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    # Draw potions before the player so the player is on top
    for potion in potions:
        potion.draw(screen)
    
    # Draw grenades
    for grenade in grenades:
        grenade.draw(screen)
        
    player.draw(screen)
    hud.draw_hud(screen, player, int(elapsed_time), kills)
    # Draw visual effects on top of everything
    effects.draw(screen)
    
    # DEBUG: Draw the effect area of the ultimate (commented, only for debug)
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
    potions = []  # List to store health potions
    grenades = []  # List to store active grenades
    spawner = Spawner()
    game_state = GameState()
    effects = Effects()  # Initialize the visual effects manager
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
            # If returned to menu, reinitialize the game
            if game_state.state == GameState.MENU:
                player = Player()
                enemies = []
                potions = []  # Reset health potions
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
            update_game(player, spawner, enemies, kills, game_state, effects, potions, grenades)
            effects.update()  # Update the visual effects
            elapsed_time += 1/FPS if FPS else 1/60
            draw_game(screen, player, enemies, background, effects, potions, grenades, elapsed_time, kills[0], hud)
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
