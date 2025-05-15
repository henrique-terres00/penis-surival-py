import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def load_player_frames():
    # Base directory for player assets
    player_dir = os.path.join('assets', 'player')
    
    # Initialize dictionary for all player actions
    actions = {
        'walk_right': [],
        'walk_left': [],
        'jump': [],
        'attack_right': [],
        'attack_left': []
    }
    
    # Load walk animations from walk subfolder
    walk_dir = os.path.join(player_dir, 'walk')
    for i in range(1, 5):
        # Load walk right frames
        path = os.path.join(walk_dir, f'walk_right_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (180, 180))
        actions['walk_right'].append(img)
        
        # Load walk left frames
        path = os.path.join(walk_dir, f'walk_left_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (180, 180))
        actions['walk_left'].append(img)
    
    # Load jump animations from jump subfolder
    jump_dir = os.path.join(player_dir, 'jump')
    for i in range(1, 5):
        path = os.path.join(jump_dir, f'jump_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (180, 180))
        actions['jump'].append(img)
    
    # Load attack animations from base_attack subfolder
    attack_dir = os.path.join(player_dir, 'base_attack')
    for i in range(1, 5):
        # Load attack right frames
        path = os.path.join(attack_dir, f'attack_right_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (180, 180))
        actions['attack_right'].append(img)
        
        # Load attack left frames
        path = os.path.join(attack_dir, f'attack_left_{i}.png')
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (180, 180))
        actions['attack_left'].append(img)
    
    return actions

# --- Player class: manages attributes, input, damage, and drawing ---
class Player:
    def __init__(self):
        self.max_hp = 100
        self.hp = 100
        self.damage_popups = []
        self.frames = load_player_frames()
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 250
        self.vx = 0
        self.vy = 0
        self.speed = 16
        self.jump_power = 48
        self.gravity = 2
        self.on_ground = True
        self.direction = 'right'
        self.state = 'idle'  # idle, walk, jump, attack, ultimate
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.13
        self.attack_anim_speed = 0.28
        self.attack_cooldown = 0
        self.ultimate_cooldown = 0
        self.ultimate_active = False
        self.ultimate_duration = 0
        self.mana = 100
        self.max_mana = 100
        
        # Milky Grenade attributes
        self.grenade_cooldown = 0
        self.grenade_cooldown_max = 120  # 2 seconds at 60 FPS
        self.grenade_mana_cost = 30  # Mana cost for throwing a grenade

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
            
        # Ultimate ability activation with 'x' key when mana is full
        if keys[pygame.K_x] and self.mana >= self.max_mana and self.ultimate_cooldown == 0:
            self.use_ultimate()
            
        # Milky Grenade ability with 'q' key when enough mana is available and cooldown is ready
        if keys[pygame.K_q] and self.mana >= self.grenade_mana_cost and self.grenade_cooldown == 0:
            self.throw_grenade()

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
                
        # Update ultimate ability if active
        if self.ultimate_active:
            self.ultimate_duration -= 1
            if self.ultimate_duration <= 0:
                self.ultimate_active = False
                # Ultimate ability has ended
                
        # Update cooldowns
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
            
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1
                
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
            
    def use_ultimate(self):
        """Activate the player's ultimate ability when mana is full.
        The ultimate ability has the following effects:
        1. Deals damage to enemies in the direction the player is facing
        2. Heals the player
        3. Makes the player temporarily invulnerable
        4. Consumes all mana
        5. Creates a visual effect
        """
        if self.mana < self.max_mana:
            return  # Not enough mana
            
        # Ultimate ability has been activated
        
        # Consume all mana
        self.mana = 0
        
        # Set cooldown and duration
        self.ultimate_cooldown = 300  # 5 seconds at 60 FPS
        self.ultimate_active = True
        self.ultimate_duration = 180  # 3 seconds at 60 FPS
        
        # Store the direction at the time of activation
        self.ultimate_direction = self.direction
        
        # Heal the player for 30% of max health
        heal_amount = int(self.max_hp * 0.3)
        self.heal(heal_amount)
        
        # Set a flag to indicate that we need to create a visual effect
        # This will be checked in the main game loop
        self.ultimate_effect_created = True
        
        # Change player state to indicate ultimate is active
        self.state = 'ultimate'  # This can be used for special animations if needed
        
        # Set a flag to indicate that we need to apply damage to enemies
        # This will be checked in the main game loop
        self.ultimate_damage_pending = True
        
    def throw_grenade(self):
        # Throw a milky grenade in the direction the player is facing.
        # The grenade follows a projectile motion and explodes after a set time.
        # It costs mana and has a cooldown.
        if self.mana < self.grenade_mana_cost or self.grenade_cooldown > 0:
            return  # Not enough mana or on cooldown
            
        # Consume mana
        self.mana -= self.grenade_mana_cost
        
        # Set cooldown
        self.grenade_cooldown = self.grenade_cooldown_max
        
        # Set a flag to indicate that we need to create a grenade
        # This will be checked in the main game loop
        self.grenade_thrown = True
        
        # Store the player's position and direction for grenade creation
        self.grenade_position = (self.x + 90, self.y + 90)  # Center of player
        self.grenade_direction = self.direction

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
        
        # Draw the player normally (without glow effect)
        surface.blit(img, (self.x, self.y))
            
        # Draw player damage popups
        draw_damage_popups(surface, self.damage_popups)