import os
import random
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

ENEMY_SIZE = (180, 180)


def load_enemy_frames(enemy_name, left_count, right_count, dead_name, subfolder=None):
    # Base directory for enemies
    enemy_dir = os.path.join('assets', 'enemies')
    
    # If a subfolder is specified, add it to the path
    if subfolder:
        enemy_dir = os.path.join(enemy_dir, subfolder)
    
    frames = {
        'left': [],
        'right': [],
        'dead': None
    }
    
    for i in range(1, left_count + 1):
        path = os.path.join(enemy_dir, f'{enemy_name}_left_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, ENEMY_SIZE)
        frames['left'].append(img)
    
    for i in range(1, right_count + 1):
        path = os.path.join(enemy_dir, f'{enemy_name}_right_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, ENEMY_SIZE)
        frames['right'].append(img)
    
    dead_path = os.path.join(enemy_dir, dead_name + '.png')
    frames['dead'] = pygame.image.load(dead_path).convert_alpha()
    frames['dead'] = pygame.transform.scale(frames['dead'], ENEMY_SIZE)
    
    return frames

# --- Enemy base class: logic, damage, drawing, and death ---
class Enemy:
    def __init__(self, x, y, direction, frames, max_hp, speed):
        self.dmg_cooldown = 0  # Cooldown to apply damage to player
        self.damage_popups = []  # (damage, x, y, alpha, timer)
        self.x = x
        self.y = y
        self.direction = direction  # 'left' or 'right'
        self.frames = frames
        self.state = 'walk'  # 'walk' or 'dead'
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.13
        self.hp = max_hp
        self.max_hp = max_hp
        self.speed = speed
        self.rect = pygame.Rect(self.x + 30, self.y + 40, 100, 120)
        self.dead_timer = 0
        # Sistema de drops genérico
        self.drop_type = None  # Tipo de item que o inimigo dropa (None, 'health_potion', 'mana_potion', etc)
        self.drop_chance = 1.0  # Chance de dropar o item (1.0 = 100%)
        self.item_dropped = False  # Indica se já dropou o item

    def update(self, player):
        from hud import update_damage_popups
        update_damage_popups(self.damage_popups)
        if self.state == 'dead':
            self.dead_timer += 1
            if self.dead_timer > 60:
                if hasattr(self, 'fade_alpha'):
                    self.fade_alpha = max(0, self.fade_alpha - 10)
                else:
                    self.fade_alpha = 255
            return
        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_index = (self.anim_index + 1) % len(self.frames[self.direction])
            self.anim_timer = 0
        # Movement: pursue player, but stop at a minimum distance
        stop_distance = 60
        if abs((self.x + ENEMY_SIZE[0]//2) - (player.x + 90)) > stop_distance:
            if self.x < player.x:
                self.x += self.speed
                self.direction = 'right'
            elif self.x > player.x:
                self.x -= self.speed
                self.direction = 'left'
        self.rect.topleft = (self.x, self.y)
        # Damage cooldown
        if self.dmg_cooldown > 0:
            self.dmg_cooldown -= 1

    def take_damage(self, dmg):
        self.hp -= dmg
        # Damage popup
        # Centralized above the health bar
        bar_x = self.x + ENEMY_SIZE[0] // 2
        bar_y = self.y - 25
        self.damage_popups.append([str(dmg), bar_x, bar_y, 255, 0, "damage"])
        if self.hp <= 0 and self.state != 'dead':
            self.state = 'dead'
            self.anim_index = 0
            self.dead_timer = 0
            self.fade_alpha = 255

    def draw(self, screen):
        # Draws the enemy on the screen.
        
        if self.state == 'dead':
            if self.frames['dead']:
                dead_img = self.frames['dead']
                if hasattr(self, 'fade_alpha'):
                    # Create a copy of the image with adjusted alpha
                    dead_img = dead_img.copy()
                    alpha_img = pygame.Surface(dead_img.get_size(), pygame.SRCALPHA)
                    alpha_img.fill((255, 255, 255, self.fade_alpha))
                    dead_img.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(dead_img, (self.x, self.y))
        else:
            current_frame = self.frames[self.direction][self.anim_index]
            screen.blit(current_frame, (self.x, self.y))
        # Health bar
        if self.state != 'dead':
            from hud import draw_health_bar
            draw_health_bar(screen, self.x+30, self.y-10, 100, 14, self.hp, self.max_hp)
        # Damage popups
        from hud import draw_damage_popups
        draw_damage_popups(screen, self.damage_popups)

class FatGirlEnemy(Enemy):
    def __init__(self, x, y, direction, speed=3, dmg_min=3, dmg_max=11):
        # Use the 'fat_girl' subfolder for this enemy type
        frames = load_enemy_frames('fat_girl', 3, 3, 'dead_fat_girl', subfolder='fat_girl')
        super().__init__(x, y, direction, frames, max_hp=10, speed=speed)
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max

class WolfEnemy(Enemy):
    def __init__(self, x, y, direction, speed=6, dmg_min=1, dmg_max=7):
        # Use the 'wolf' subfolder for this enemy type
        frames = load_enemy_frames('wolf', 4, 4, 'dead_wolf', subfolder='wolf')
        super().__init__(x, y, direction, frames, max_hp=5, speed=speed)
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max

class BirdEnemy(Enemy):
    def __init__(self, bird_name, x, y, direction, speed=7, dmg_min=2, dmg_max=6, subfolder=None):
        # Load frames using the load_enemy_frames function with optional subfolder
        frames = load_enemy_frames(bird_name, 4, 4, f'dead_{bird_name}', subfolder)
        
        super().__init__(x, y, direction, frames, max_hp=5, speed=speed)
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max
        self.base_y = y
        self.osc_time = 0

    def update(self, player):
        from hud import update_damage_popups
        update_damage_popups(self.damage_popups)
        if self.state == 'dead':
            # Animate fall
            if not hasattr(self, 'fall_vy'):
                self.fall_vy = 0
            self.fall_vy += 1.2  # gravity
            self.y += self.fall_vy
            self.rect.topleft = (self.x, self.y)
            self.dead_timer += 1
            if hasattr(self, 'fade_alpha'):
                self.fade_alpha = max(0, self.fade_alpha - 10)
            return
        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_index = (self.anim_index + 1) % len(self.frames[self.direction])
            self.anim_timer = 0
        # Horizontal movement
        if self.direction == 'right':
            self.x += self.speed
        else:
            self.x -= self.speed
        # Vertical movement
        import math
        self.osc_time += 0.10
        self.y = self.base_y + math.sin(self.osc_time) * 40  # Oscillation
        self.rect.topleft = (self.x, self.y)
        if self.dmg_cooldown > 0:
            self.dmg_cooldown -= 1

class BlueBirdEnemy(BirdEnemy):
    def __init__(self, x, y, direction, speed=7, dmg_min=2, dmg_max=6):
        # Use the 'blue_bird' subfolder for this enemy type
        super().__init__('blue_bird', x, y, direction, speed, dmg_min, dmg_max, subfolder='blue_bird')
        self.drop_type = 'mana_potion'  # Blue birds drop mana potions when they die
        self.drop_chance = 1.0  # 100% chance to drop

class RedBirdEnemy(BirdEnemy):
    def __init__(self, x, y, direction, speed=7, dmg_min=2, dmg_max=6):
        # Use the 'red_bird' subfolder for this enemy type
        super().__init__('red_bird', x, y, direction, speed, dmg_min, dmg_max, subfolder='red_bird')
        self.drop_type = 'health_potion'  # Red birds drop health potions when they die