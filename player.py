import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def load_player_frames():
    player_dir = os.path.join('assets', 'player')
    actions = {
        'walk_right': [],
        'walk_left': [],
        'jump': [],
        'attack_right': [],
        'attack_left': []
    }
    for action in actions:
        for i in range(1, 5):
            path = os.path.join(player_dir, f'{action}_{i}.png')
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            actions[action].append(img)
    return actions

# --- Player class: manages attributes, input, damage, and drawing ---
class Player:
    def __init__(self):
        self.max_hp = 100
        self.hp = 100
        self.damage_popups = []
        self.frames = load_player_frames()
        self.x = SCREEN_WIDTH // 2
        self.y = -100  # Nasce no topo da tela, caindo
        self.vx = 0
        self.vy = 0
        self.speed = 16
        self.jump_power = 38
        self.gravity = 2
        self.on_ground = False  # Começa caindo
        self.direction = 'right'
        self.state = 'idle'  # idle, walk, jump, attack
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.13
        self.attack_anim_speed = 0.28
        self.attack_cooldown = 0
        self.mana = 0
        self.max_mana = 100

    def handle_input(self, keys):
        if self.attack_cooldown > 0:
            return
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.direction = 'left'
            if self.on_ground:
                self.state = 'walk'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.direction = 'right'
            if self.on_ground:
                self.state = 'walk'
        else:
            if self.on_ground:
                self.state = 'idle'
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -self.jump_power
            self.on_ground = False
            self.state = 'jump'
        if keys[pygame.K_SPACE] and self.attack_cooldown == 0:
            self.state = 'attack'
            self.anim_index = 0
            self.attack_cooldown = 20

    def update(self):
        from hud import update_damage_popups
        update_damage_popups(self.damage_popups)
        self.x += self.vx
        self.x = max(0, min(self.x, SCREEN_WIDTH - 180))
        if not self.on_ground:
            self.vy += self.gravity
            self.y += self.vy
            if self.y >= SCREEN_HEIGHT - 250:
                self.y = SCREEN_HEIGHT - 250
                self.vy = 0
                self.on_ground = True
                self.state = 'idle'
        if self.state == 'attack':
            self.anim_timer += self.attack_anim_speed
        else:
            self.anim_timer += self.anim_speed
        if self.state == 'walk':
            frames = self.frames['walk_right'] if self.direction == 'right' else self.frames['walk_left']
        elif self.state == 'jump':
            frames = self.frames['jump']
        elif self.state == 'attack':
            frames = self.frames['attack_right'] if self.direction == 'right' else self.frames['attack_left']
        else:
            frames = [self.frames['walk_right'][0]] if self.direction == 'right' else [self.frames['walk_left'][0]]
        if self.anim_timer >= 1:
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.anim_timer = 0
            if self.state == 'attack' and self.anim_index == 0:
                self.state = 'idle'
                if hasattr(self, 'attack_hit_set'):
                    self.attack_hit_set = set()

        if self.state == 'attack':
            self.attack_cooldown = max(0, self.attack_cooldown - 1)
        else:
            self.attack_cooldown = 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        # Add damage popup
        # Centralize above player
        popup_x = self.x + 90
        popup_y = self.y - 30
        self.damage_popups.append([str(dmg), popup_x, popup_y, 255, 0, "damage"])

    def heal(self, amount):
        # Ensure amount is a number
        amount = int(amount) if amount else 0
        
        # Limit healing to not exceed maximum HP
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        actual_heal = self.hp - old_hp
            
        if actual_heal > 0:
            # Add healing popup (similar to damage popup, but in green)
            popup_x = self.x + 90
            popup_y = self.y - 30
            self.damage_popups.append([str(actual_heal), popup_x, popup_y, 255, 0, "heal"])

    def draw(self, surface):
        from hud import draw_damage_popups
        if self.state == 'walk':
            frames = self.frames['walk_right'] if self.direction == 'right' else self.frames['walk_left']
        elif self.state == 'jump':
            frames = self.frames['jump']
        elif self.state == 'attack':
            frames = self.frames['attack_right'] if self.direction == 'right' else self.frames['attack_left']
        else:
            frames = [self.frames['walk_right'][0]] if self.direction == 'right' else [self.frames['walk_left'][0]]
        img = frames[self.anim_index % len(frames)]
        surface.blit(img, (self.x, self.y))
        # Draw player damage popups
        draw_damage_popups(surface, self.damage_popups)