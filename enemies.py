import os
import random
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

ENEMY_SIZE = (180, 180)


def load_enemy_frames(enemy_name, left_count, right_count, dead_name):
    enemy_dir = os.path.join('assets', 'enemies')
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
        self.damage_popups.append([str(dmg), bar_x, bar_y, 255, 0])
        if self.hp <= 0 and self.state != 'dead':
            self.state = 'dead'
            self.anim_index = 0
            self.dead_timer = 0
            self.fade_alpha = 255

    def draw(self, surface):
        from hud import draw_health_bar, draw_damage_popups
        # Fade out if dead
        if self.state == 'dead' and hasattr(self, 'fade_alpha'):
            dead_img = self.frames['dead'].copy()
            dead_img.set_alpha(self.fade_alpha)
            surface.blit(dead_img, (self.x, self.y))
        elif self.state == 'dead':
            surface.blit(self.frames['dead'], (self.x, self.y))
        else:
            frames = self.frames[self.direction]
            img = frames[self.anim_index % len(frames)]
            surface.blit(img, (self.x, self.y))
        # Health bar
        if self.state != 'dead':
            draw_health_bar(surface, self.x+30, self.y-10, 100, 14, self.hp, self.max_hp)
        # Damage popups
        draw_damage_popups(surface, self.damage_popups)

class FatGirlEnemy(Enemy):
    def __init__(self, x, y, direction, speed=3, dmg_min=3, dmg_max=11):
        frames = load_enemy_frames('fat_girl', 3, 3, 'dead_fat_girl')
        super().__init__(x, y, direction, frames, max_hp=10, speed=speed)
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max

class WolfEnemy(Enemy):
    def __init__(self, x, y, direction, speed=6, dmg_min=1, dmg_max=7):
        frames = load_enemy_frames('wolf', 4, 4, 'dead_wolf')
        super().__init__(x, y, direction, frames, max_hp=5, speed=speed)
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max