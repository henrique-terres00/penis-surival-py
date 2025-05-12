import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Effects:
    def __init__(self):
        self.effects = []
        self.milky_image = None
        # We delay loading the image to ensure pygame is initialized
    
    def _load_milky_image(self):
        """Loads the Milky effect image."""
        try:
            image_path = os.path.join('assets', 'effects', 'milky.png')
            image = pygame.image.load(image_path).convert_alpha()
            # Resize the image to a smaller size (150x150 pixels)
            return pygame.transform.scale(image, (150, 150))
        except Exception as e:
            print(f"Erro ao carregar a imagem do efeito Milky: {e}")
            return None
    
    def add_milky_effect(self, duration=60, player_position=None):
        """Adds the Milky effect to the active effects list.
        
        Args:
            duration (int): Duration of the effect in frames (default: 60 frames = 1 second at 60 FPS)
            player_position (tuple): Player position (x, y)
        """
        # Parameter validation
        if player_position is None:
            return
            
        if not isinstance(player_position, tuple) or len(player_position) != 2:
            return
                
        # Load the image if it hasn't been loaded yet
        if self.milky_image is None:
            self.milky_image = self._load_milky_image()
            
        if self.milky_image is None:
            return
            
        # Calculate the position for the effect (horizontally centered and above the player)
        x = player_position[0] - self.milky_image.get_width() // 2
        y = player_position[1] - self.milky_image.get_height() - 20  # 20 pixels above the player
            
        # Ensure the effect doesn't go off-screen
        x = max(0, min(x, SCREEN_WIDTH - self.milky_image.get_width()))
        y = max(0, y)  # Prevent the effect from going off the top of the screen
            
        self.effects.append({
            'type': 'milky',
            'position': (x, y),
            'alpha': 0,  # Starts transparent
            'max_alpha': 255,  # Maximum alpha value (0-255)
            'duration': duration,
            'frame': 0,
            'fade_in': True
        })
    
    def update(self):
        """Updates all active effects."""
        effects_to_remove = []
        
        for i, effect in enumerate(self.effects):
            effect['frame'] += 1
            
            # Fade in effect
            if effect['fade_in'] and effect['alpha'] < effect['max_alpha']:
                effect['alpha'] = min(effect['alpha'] + 15, effect['max_alpha'])
                if effect['alpha'] >= effect['max_alpha']:
                    effect['fade_in'] = False
            # Fade out effect
            elif not effect['fade_in'] and effect['frame'] >= effect['duration']:
                effect['alpha'] = max(0, effect['alpha'] - 10)
            
            # Remove the effect if it has finished
            if effect['alpha'] <= 0 and effect['frame'] >= effect['duration']:
                effects_to_remove.append(i)
        
        # Remove finished effects (from back to front to avoid affecting indices)
        for i in sorted(effects_to_remove, reverse=True):
            if i < len(self.effects):
                self.effects.pop(i)
    
    def draw(self, screen):
        """Draws all active effects on the screen."""
        for effect in self.effects:
            if effect['type'] == 'milky' and self.milky_image:
                # Check if the position exists in the effect
                if 'position' not in effect:
                    continue
                # Create a copy of the image with the current alpha
                img_copy = self.milky_image.copy()
                img_copy.set_alpha(effect['alpha'])
                screen.blit(img_copy, effect['position'])