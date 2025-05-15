import pygame
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class MilkyGrenade:
    """
    Represents a milky grenade that can be thrown by the player.
    The grenade follows a projectile motion and explodes after a set time.
    """
    
    def __init__(self, x, y, direction, initial_velocity=20):
        """
        Initialize a new milky grenade.
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
            direction (str): Direction to throw ('left' or 'right')
            initial_velocity (int): Initial velocity of the grenade
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.active = True
        self.exploding = False
        self.explosion_radius = 250  # Increased radius of explosion for damage
        
        # Physics parameters
        self.initial_velocity = initial_velocity
        self.angle = math.radians(45)  # 45 degrees in radians
        self.gravity = 0.5
        self.time = 0
        
        # Calculate initial velocity components
        self.vx = self.initial_velocity * math.cos(self.angle)
        if direction == 'left':
            self.vx = -self.vx
        self.vy = -self.initial_velocity * math.sin(self.angle)  # Negative because y increases downwards
        
        # Timer for explosion
        self.timer = 0
        self.explosion_time = 60  # Explode after 60 frames (1 second at 60 FPS)
        self.explosion_duration = 24  # Duration of explosion animation in frames
        
        # Animation frames
        self.grenade_frames = {
            'left': None,
            'right': None
        }
        self.explosion_frames = []
        self.explosion_index = 0
        self.load_frames()
        
        # Hitbox for collision detection - will be updated after loading frames
        self.rect = pygame.Rect(self.x, self.y, 48, 48)  # Initial size, will be updated
        
    def load_frames(self):
        """Load all animation frames for the grenade and explosion."""
        try:
            # Load grenade frames and scale them up (1.5x larger)
            grenade_scale = 1.5
            left_img = pygame.image.load('assets/effects/grenade/granada_left.png').convert_alpha()
            right_img = pygame.image.load('assets/effects/grenade/granada_right.png').convert_alpha()
            
            # Get original dimensions
            original_width = left_img.get_width()
            original_height = left_img.get_height()
            
            # Scale up the grenade images
            self.grenade_frames['left'] = pygame.transform.scale(
                left_img, 
                (int(original_width * grenade_scale), int(original_height * grenade_scale))
            )
            self.grenade_frames['right'] = pygame.transform.scale(
                right_img, 
                (int(original_width * grenade_scale), int(original_height * grenade_scale))
            )
            
            # Load explosion frames and scale them up (2x larger)
            explosion_scale = 2.0
            for i in range(1, 5):  # 4 explosion frames
                original_frame = pygame.image.load(f'assets/effects/grenade/explosao_{i}.png').convert_alpha()
                # Get original dimensions
                original_width = original_frame.get_width()
                original_height = original_frame.get_height()
                
                # Scale up the explosion images
                scaled_frame = pygame.transform.scale(
                    original_frame, 
                    (int(original_width * explosion_scale), int(original_height * explosion_scale))
                )
                self.explosion_frames.append(scaled_frame)
        except Exception as e:
            print(f"Error loading grenade frames: {e}")
    
    def update(self):
        """Update the grenade's position and state."""
        if not self.active:
            return
            
        if self.exploding:
            # Update explosion animation
            self.timer += 1
            if self.timer >= self.explosion_duration:
                self.active = False
            return
            
        # Update timer
        self.timer += 1
        if self.timer >= self.explosion_time:
            self.exploding = True
            self.timer = 0
            return
            
        # Update position using projectile motion equations
        self.time += 1
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Apply gravity
        
        # Update hitbox with the actual size of the grenade image
        if self.grenade_frames[self.direction]:
            self.rect.width = self.grenade_frames[self.direction].get_width()
            self.rect.height = self.grenade_frames[self.direction].get_height()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Check if grenade hits the ground
        if self.y > SCREEN_HEIGHT - 100:  # Assuming ground is at SCREEN_HEIGHT - 100
            self.y = SCREEN_HEIGHT - 100
            self.exploding = True
            self.timer = 0
            
        # Check if grenade goes off-screen horizontally
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.active = False
    
    def draw(self, screen):
        """Draw the grenade or explosion on the screen."""
        if not self.active:
            return
            
        if self.exploding:
            # Draw explosion
            explosion_index = min(self.timer // 6, len(self.explosion_frames) - 1)
            explosion_img = self.explosion_frames[explosion_index]
            
            # Center the explosion at the grenade's position
            explosion_x = self.x - explosion_img.get_width() // 2 + self.rect.width // 2
            explosion_y = self.y - explosion_img.get_height() // 2 + self.rect.height // 2
            
            screen.blit(explosion_img, (explosion_x, explosion_y))
        else:
            # Draw grenade
            grenade_img = self.grenade_frames[self.direction]
            if grenade_img:
                screen.blit(grenade_img, (self.x, self.y))
    
    def get_explosion_rect(self):
        """Get the rectangle representing the explosion area for damage calculation."""
        if not self.exploding:
            return None
            
        # Create a rect centered on the grenade with the explosion radius
        return pygame.Rect(
            self.x - self.explosion_radius,
            self.y - self.explosion_radius,
            self.explosion_radius * 2,
            self.explosion_radius * 2
        )
