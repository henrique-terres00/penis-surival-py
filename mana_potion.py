import os
import pygame
from settings import SCREEN_HEIGHT

class ManaPotion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.vel_y = 0  # Initial vertical velocity
        self.gravity = 0.5  # Gravity to simulate falling
        self.ground_y = SCREEN_HEIGHT - 150  # Ground position
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        self.active = True  # If False, the potion has been collected
        self.collectable = False  # If True, the potion can be collected (after hitting the ground)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.load_frames()
        
    def load_frames(self):
        #Loads the mana potion animation frames.
        try:
            potion_dir = os.path.join('assets', 'effects', 'mana_potion')
            for i in range(1, 5):  # 4 animation frames
                path = os.path.join(potion_dir, f'manapot_{i}.png')
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (self.width, self.height))
                self.frames.append(img)
        except Exception as e:
            print(f"Error loading mana potion frames: {e}")
            # Create empty frames to avoid errors
            self.frames = [pygame.Surface((self.width, self.height), pygame.SRCALPHA) for _ in range(4)]
    
    def update(self):
        #Updates the position and animation of the potion.
        if not self.active:
            return
            
        # Apply gravity
        self.vel_y += self.gravity
        self.y += self.vel_y
        
        # Check collision with the ground
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vel_y = 0
            self.collectable = True  # The potion can be collected after hitting the ground
        else:
            # Ensure the potion is not collectable while in the air
            self.collectable = False
        
        # Update collision rectangle
        self.rect.topleft = (self.x, self.y)
        
        # Update animation
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_counter = 0
    
    def draw(self, surface):
        #Draws the potion on the screen.
        if not self.active or not self.frames:
            return
        
        # Draw the potion
        surface.blit(self.frames[self.current_frame], (self.x, self.y))
    
    def collect(self):
        #Marks the potion as collected.
        if not self.collectable:
            return 0  # Cannot be collected yet
            
        self.active = False
        return 30  # Amount of mana the potion restores
        
    def can_collect(self):
        #Checks if the potion can be collected.
        return self.active and self.collectable
