import pygame

def get_player_hitbox(player):
    # Centralized on body
    return pygame.Rect(player.x + 40, player.y + 40, 100, 120)

def get_enemy_hitbox(enemy):
    # Centralized on body
    return pygame.Rect(enemy.x + 30, enemy.y + 40, 100, 120)

def get_attack_hitbox(player):
    # Hitbox of player's attack (in front)
    if player.direction == 'right':
        return pygame.Rect(player.x + 110, player.y + 50, 80, 80)
    else:
        return pygame.Rect(player.x - 10, player.y + 50, 80, 80)
