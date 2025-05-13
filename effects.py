import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Effects:
    def __init__(self):
        self.effects = []
        self.milky_image = None
        self.master_cum_image = None
        self.ult_popup_image = None
        self.ult_ready_hud_image = None
        self.ult_not_ready_hud_image = None
        self.ult_frames = {
            'right': [],
            'left': []
        }
        # We delay loading the image to ensure pygame is initialized
    
    def _load_milky_image(self):
        # Loads the Milky effect image.
        try:
            # Use the text_effects subfolder
            image_path = os.path.join('assets', 'effects', 'text_effects', 'milky.png')
            image = pygame.image.load(image_path).convert_alpha()
            # Resize the image to a smaller size (150x150 pixels)
            return pygame.transform.scale(image, (150, 150))
        except Exception as e:
            print(f"Error loading Milky effect image: {e}")
            return None
            
    def _load_ult_hud_images(self):
        # Loads the Ultimate Ready and Not Ready HUD images.
        # These images are displayed to show the status of the ultimate ability.
        try:
            # Use the ultimate_hud subfolder
            ult_hud_dir = os.path.join('assets', 'effects', 'ultimate_hud')
            
            # Load Ultimate Ready image
            ready_path = os.path.join(ult_hud_dir, 'ult_ready_hud.png')
            ready_image = pygame.image.load(ready_path).convert_alpha()
            self.ult_ready_hud_image = pygame.transform.scale(ready_image, (200, 200))
            
            # Load Ultimate Not Ready image
            not_ready_path = os.path.join(ult_hud_dir, 'ult_not_ready_hud.png')
            not_ready_image = pygame.image.load(not_ready_path).convert_alpha()
            self.ult_not_ready_hud_image = pygame.transform.scale(not_ready_image, (200, 200))
            
            return True
        except Exception as e:
            print(f"Error loading Ultimate HUD images: {e}")
            return False
            
    def _load_master_cum_image(self):
        # Loads the Master Cum effect image for the central ultimate effect.
        # Preserves the original aspect ratio of the image.
        try:
            # Use the text_effects subfolder
            image_path = os.path.join('assets', 'effects', 'text_effects', 'master_cum.png')
            original_image = pygame.image.load(image_path).convert_alpha()
            
            # Get the original dimensions
            original_width = original_image.get_width()
            original_height = original_image.get_height()
            
            # Calculate the original aspect ratio
            aspect_ratio = original_width / original_height
            
            # Define the desired width and calculate the proportional height
            # Increasing the width to ensure it doesn't look squeezed
            target_width = 900  # Increased to 900 pixels for a much more dramatic effect
            
            # Ensure the height is at least 180 pixels for better visualization
            target_height = max(180, int(target_width / aspect_ratio))
            
            # Redimensionar a imagem mantendo a proporção original
            scaled_image = pygame.transform.scale(original_image, (target_width, target_height))
            
            return scaled_image
        except Exception as e:
            print(f"Error loading Master Cum effect image: {e}")
            return None
            
    def _load_ultimate_frames(self):
        # Loads the Ultimate ability animation frames for both directions.
        # Preserves the natural size and proportions of the original PNGs.
        try:
            # Use the ultimate_animation subfolder
            ult_anim_dir = os.path.join('assets', 'effects', 'ultimate_animation')
            
            # Try to load the popup image if it exists
            # If not, we'll continue without it as it's not critical for the animation
            popup_path = os.path.join(ult_anim_dir, 'ult_popup.png')
            if os.path.exists(popup_path):
                self.ult_popup_image = pygame.image.load(popup_path).convert_alpha()
            else:
                self.ult_popup_image = None
            
            # Fator de escala base para ajustar o tamanho geral dos efeitos
            # Usando um valor moderado para o tamanho do efeito
            scale_factor = 2
            
            # Load right direction frames
            for i in range(1, 5):
                image_path = os.path.join(ult_anim_dir, f'ult_right_{i}.png')
                if not os.path.exists(image_path):
                    continue
                    
                original_image = pygame.image.load(image_path).convert_alpha()
                
                # Obter o tamanho original da imagem
                original_width = original_image.get_width()
                original_height = original_image.get_height()
                
                # Aplicar o fator de escala base, mas manter as proporções originais
                scaled_width = int(original_width * scale_factor)
                scaled_height = int(original_height * scale_factor)
                
                # Escalar a imagem mantendo suas proporções originais
                image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
                self.ult_frames['right'].append(image)
                
            # Load left direction frames
            for i in range(1, 5):
                image_path = os.path.join(ult_anim_dir, f'ult_left_{i}.png')
                if not os.path.exists(image_path):
                    continue
                    
                original_image = pygame.image.load(image_path).convert_alpha()
                
                # Obter o tamanho original da imagem
                original_width = original_image.get_width()
                original_height = original_image.get_height()
                
                # Aplicar o fator de escala base, mas manter as proporções originais
                scaled_width = int(original_width * scale_factor)
                scaled_height = int(original_height * scale_factor)
                
                # Escalar a imagem mantendo suas proporções originais
                image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
                self.ult_frames['left'].append(image)
                
            return True
        except Exception as e:
            print(f"Error loading Ultimate frames: {e}")
            return False
        
    def add_milky_effect(self, duration=60, player_position=None):
        # Adds the Milky effect to the active effects list.
        
        # Args:
        #    duration (int): Duration of the effect in frames (default: 60 frames = 1 second at 60 FPS)
        #    player_position (tuple): Player position (x, y)
        
        #Parameter validation
        if player_position is None:
            return
            
        if not isinstance(player_position, tuple) or len(player_position) != 2:
            return
                
        # Load the image if it hasn't been loaded yet
        if self.milky_image is None:
            self.milky_image = self._load_milky_image()
            
        if self.milky_image is None:
            return
            
        # Calculate the position for the effect (centered on the player)
        x = player_position[0] - self.milky_image.get_width() // 2
        y = player_position[1] - self.milky_image.get_height() // 2
        
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

    def add_ultimate_hud(self, is_ready=False):
        # Adds or updates the Ultimate HUD indicator.
        # This creates a visual indicator showing if the ultimate ability is ready or not.
        
        # Args:
        #    is_ready (bool): Whether the ultimate is ready to use
        
        # Load the images if they haven't been loaded yet
        if self.ult_ready_hud_image is None or self.ult_not_ready_hud_image is None:
            if not self._load_ult_hud_images():
                # Silently continue without HUD images
                return
        
        # Calculate the position for the effect (canto superior direito da tela)
        image = self.ult_ready_hud_image if is_ready else self.ult_not_ready_hud_image
        x = SCREEN_WIDTH - image.get_width() - 30  # 30 pixels da borda direita
        y = 30  # 30 pixels do topo da tela
        
        # Verificar se já existe um efeito de ultimate_hud
        for effect in self.effects:
            if effect.get('type') == 'ultimate_hud':
                # Atualizar o efeito existente
                effect['is_ready'] = is_ready
                effect['position'] = (x, y)
                return
        
        # Se não existe, adicionar um novo efeito
        self.effects.append({
            'type': 'ultimate_hud',
            'is_ready': is_ready,
            'position': (x, y),
            'alpha': 0,  # Starts transparent
            'max_alpha': 220,  # Maximum alpha value (0-255), slightly transparent
            'duration': 9999,  # Praticamente infinito, será atualizado conforme necessário
            'frame': 0,
            'fade_in': True,
            'scale': 1.0,
            'scale_direction': 0.005,  # Amount to increase/decrease scale each frame for pulsating effect
            'float_offset': 0,  # Used for floating animation
            'float_direction': 0.3,  # Pixels to move up/down per frame
            'show_text': True  # Flag to indicate that text should be shown
        })
    
    def add_master_cum_effect(self):
        # Adds a central Master Cum effect to the screen.
        # This creates a large, dramatic effect in the center of the screen.
        
        # Load the image if it hasn't been loaded yet
        if self.master_cum_image is None:
            self.master_cum_image = self._load_master_cum_image()
            
        if self.master_cum_image is None:
            # Silently continue without Master Cum image
            return
            
        # Calculate the position for the effect (centered horizontally, higher vertically)
        x = (SCREEN_WIDTH - self.master_cum_image.get_width()) // 2
        # Posicionar mais alto na tela (1/3 da altura da tela)
        y = SCREEN_HEIGHT // 3 - 100 - self.master_cum_image.get_height() // 2
        
        # Add the effect to the list
        self.effects.append({
            'type': 'master_cum',
            'position': (x, y),
            'alpha': 0,  # Starts transparent
            'max_alpha': 220,  # Maximum alpha value (0-255), slightly transparent
            'duration': 60,  # 1 second at 60 FPS
            'frame': 0,
            'fade_in': True,
            'scale': 1.0,
            'scale_direction': 0.01  # Amount to increase/decrease scale each frame for pulsating effect
        })
        
    def add_ultimate_effect(self, player_position, direction='right'):
        # Adds the Ultimate ability effect to the active effects list.
        # This creates a directional effect based on the player's facing direction.
        
        # Args:
        #    player_position (tuple): Player position (x, y)
        #    direction (str): Direction the player is facing ('right' or 'left')
        
        # Ensure the ultimate frames are loaded
        if not self.ult_frames['right'] and not self.ult_frames['left']:
            self._load_ultimate_frames()
            
        # Validate direction
        if direction not in ['right', 'left']:
            direction = 'right'  # Default to right if invalid
            
        # Get the frames for the specified direction
        frames = self.ult_frames[direction]
        if not frames:
            print(f"No frames available for direction: {direction}")
            return
            
        # Calculate positions for each frame
        frame_positions = []
        
        # Calculate the starting position based on player position and direction
        if direction == 'right':
            start_x = player_position[0] + 75
        else:
            start_x = player_position[0] - 75
        start_y = player_position[1] + 150  # Position the effect lower, saindo do corpo do jogador
        
        # Calculate different positions for each frame to create a directional effect
        for i, frame in enumerate(frames):
            frame_width = frame.get_width()
            frame_height = frame.get_height()
            
            # Adjust position based on direction
            if direction == 'right':
                # For right direction, each frame extends further to the right
                x = start_x + (i * 50)  # Each frame is positioned further to the right
            else:
                # For left direction, each frame extends further to the left
                x = start_x - frame_width - (i * 50)  # Each frame is positioned further to the left
                
            # Position vertically centered
            y = start_y - (frame_height // 2)
            
            frame_positions.append((x, y))
            
        # Calculate the effect area for damage application
        # The effect area is based on the last frame (frame 4) which has the largest reach
        last_frame = frames[-1]
        last_frame_width = last_frame.get_width()
        last_frame_height = last_frame.get_height()
        
        # Define the area of effect based on direction
        if direction == 'right':
            x_start = start_x
            x_end = start_x + last_frame_width
        else:
            x_start = start_x - last_frame_width
            x_end = start_x
            
        # Define the vertical area of effect
        y_top = start_y - (last_frame_height // 2)
        y_bottom = start_y + (last_frame_height // 2)
        
        # Create a pygame.Rect for collision detection
        if direction == 'right':
            hitbox_rect = pygame.Rect(x_start, y_top, last_frame_width, last_frame_height)
        else:
            # For the left direction, we need to use x_start as the initial X position of the rectangle
            # x_start is already calculated as start_x - last_frame_width, which is the correct position
            hitbox_rect = pygame.Rect(x_start, y_top, last_frame_width, last_frame_height)
            
        # Add the effect to the list
        self.effects.append({
            'type': 'ultimate_animated',
            'direction': direction,
            'frame_positions': frame_positions,
            'current_frame': 0,
            'frame_count': len(frames),
            'duration': 24,  # 24 frames = 0.4 seconds at 60 FPS (6 frames per animation frame)
            'effect_area': {
                'direction': direction,
                'x_start': x_start,
                'x_end': x_end,
                'y_center': start_y,
                'y_top': y_top,
                'y_bottom': y_bottom,
                'height': last_frame_height,
                'hitbox_rect': hitbox_rect  # Add the pygame.Rect for collision detection
            }
        })
            
    def update(self):
        # Updates all active effects.
        
        effects_to_remove = []
        
        for i, effect in enumerate(self.effects):
            # Increment the frame counter
            effect['frame'] = effect['frame'] + 1 if 'frame' in effect else 0
            
            # Handle different effect types
            if effect['type'] == 'ultimate_animated':
                # Update the current frame of the animation
                if 'current_frame' in effect:
                    effect['current_frame'] += 1
                    
                # Remove the effect if it has finished
                if 'duration' in effect and effect['current_frame'] >= effect['duration']:
                    effects_to_remove.append(i)
            else:
                # Handle fade in/out for other effects
                if 'alpha' in effect and 'max_alpha' in effect:
                    # Fade in effect
                    if 'fade_in' in effect and effect['fade_in'] and effect['frame'] < effect['duration'] // 2:
                        effect['alpha'] = min(effect['max_alpha'], effect['alpha'] + 10)
                        if effect['alpha'] >= effect['max_alpha']:
                            effect['fade_in'] = False
                    
                    # Fade out effect
                    elif 'fade_in' in effect and not effect['fade_in'] and effect['frame'] >= effect['duration']:
                        # Master cum effect fades out slower for dramatic effect
                        fade_speed = 5 if effect['type'] == 'master_cum' else 10
                        effect['alpha'] = max(0, effect['alpha'] - fade_speed)
                    
                    # Remove the effect if it has finished
                    if 'alpha' in effect and effect['alpha'] <= 0 and effect['frame'] >= effect['duration']:
                        effects_to_remove.append(i)
        
        # Remove finished effects (from back to front to avoid affecting indices)
        for i in sorted(effects_to_remove, reverse=True):
            if i < len(self.effects):
                self.effects.pop(i)
    
    def draw(self, screen):
        # Draws all active effects on the screen.
        
        for effect in self.effects:
            
            # Draw the actual effect
            if effect['type'] == 'milky' and self.milky_image:
                # Check if the position exists in the effect
                if 'position' not in effect:
                    continue
                # Create a copy of the image with the current alpha
                img_copy = self.milky_image.copy()
                img_copy.set_alpha(effect['alpha'])
                screen.blit(img_copy, effect['position'])
                    
            elif effect['type'] == 'ultimate_animated':
                # Handle the animated ultimate effect
                if 'frame_positions' not in effect or 'direction' not in effect:
                    continue
                
                # Get the current frame based on the animation progress
                # Cada frame é exibido por 6 ticks, garantindo que a animação passe por todos os frames
                frame_index = min(effect['current_frame'] // 6, effect['frame_count'] - 1)
                
                # Get the frame image
                frame_img = self.ult_frames[effect['direction']][frame_index]
                
                # Get the position for this specific frame
                frame_position = effect['frame_positions'][frame_index]
                
                # Draw the frame at its specific position
                screen.blit(frame_img, frame_position)
                
            elif effect['type'] == 'master_cum' and self.master_cum_image:
                # Handle the master cum effect (central screen effect)
                if 'position' not in effect:
                    continue
                    
                # Apply scaling for pulsating effect if needed
                if 'scale' in effect and 'scale_direction' in effect:
                    effect['scale'] += effect['scale_direction']
                    # Reverse direction if scale gets too large or too small
                    if effect['scale'] > 1.1 or effect['scale'] < 0.9:
                        effect['scale_direction'] *= -1
                        
                    # Get the original dimensions of the image
                    original_width = self.master_cum_image.get_width()
                    original_height = self.master_cum_image.get_height()
                    
                    # Calculate the new dimensions while maintaining the aspect ratio
                    new_width = int(original_width * effect['scale'])
                    new_height = int(original_height * effect['scale'])
                    
                    # Rescale the image while maintaining the original aspect ratio
                    scaled_surface = pygame.transform.scale(self.master_cum_image, (new_width, new_height))
                    
                    # Adjust the position to keep it centered
                    x, y = effect['position']
                    center_x = x + original_width // 2
                    center_y = y + original_height // 2
                    new_x = center_x - new_width // 2
                    new_y = center_y - new_height // 2
                    
                    # Set alpha and blit
                    scaled_surface.set_alpha(effect['alpha'])
                    screen.blit(scaled_surface, (new_x, new_y))
                else:
                    # Just apply alpha if no scaling info
                    img_copy = self.master_cum_image.copy()
                    img_copy.set_alpha(effect['alpha'])
                    screen.blit(img_copy, effect['position'])
                    
            elif effect['type'] == 'ult_ready_popup' and self.ult_popup_image:
                # Handle the ultimate ready popup effect
                if 'position' not in effect:
                    continue
                    
                # Apply scaling and floating animation
                if 'scale' in effect and 'scale_direction' in effect:
                    # Update scale for pulsating effect
                    effect['scale'] += effect['scale_direction']
                    if effect['scale'] > 1.1 or effect['scale'] < 0.9:
                        effect['scale_direction'] *= -1
                    
                    # Update floating animation
                    if 'float_offset' in effect and 'float_direction' in effect:
                        effect['float_offset'] += effect['float_direction']
                        if abs(effect['float_offset']) > 10:  # Maximum float distance
                            effect['float_direction'] *= -1
                    
                    # Get original dimensions
                    original_width = self.ult_popup_image.get_width()
                    original_height = self.ult_popup_image.get_height()
                    
                    # Calculate new dimensions
                    new_width = int(original_width * effect['scale'])
                    new_height = int(original_height * effect['scale'])
                    
                    # Scale the image
                    scaled_surface = pygame.transform.scale(self.ult_popup_image, (new_width, new_height))
                    
                    # Adjust position for scaling and floating
                    x, y = effect['position']
                    center_x = x + original_width // 2
                    center_y = y + original_height // 2
                    new_x = center_x - new_width // 2
                    new_y = center_y - new_height // 2 + effect['float_offset']  # Apply floating offset
                    
                    # Set alpha and blit
                    scaled_surface.set_alpha(effect['alpha'])
                    screen.blit(scaled_surface, (new_x, new_y))
                    
                    # Add the "Ultimate Ready" text below the icon
                    if effect.get('show_text', False):
                        font = pygame.font.SysFont(None, 36)  # Font and size
                        text_color = (255, 255, 0)  # Yellow
                        text_surface = font.render("Ultimate Ready", True, text_color)
                        
                        # Apply the same alpha to the text
                        text_surface.set_alpha(effect['alpha'])
                        
                        # Position the text centered below the icon
                        text_x = new_x + (new_width - text_surface.get_width()) // 2
                        text_y = new_y + new_height + 10  # 10 pixels below the icon
                        text_color = (255, 255, 255)  # White
                        text_surface = font.render("Ultimate Ready", True, text_color)
                        
                        # Apply the same alpha to the text
                        text_surface.set_alpha(effect['alpha'])
                        
                        # Position the text centered below the icon
                        text_x = effect['position'][0] + (self.ult_popup_image.get_width() - text_surface.get_width()) // 2
                        text_y = effect['position'][1] + self.ult_popup_image.get_height() + 10  # 10 pixels below the icon
                        
                        # Draw the text
                        screen.blit(text_surface, (text_x, text_y))

            elif effect['type'] == 'ultimate_hud':
                # Handle the ultimate HUD effect (ready or not ready)
                if 'position' not in effect or 'is_ready' not in effect:
                    continue
                    
                # Determine which image to use based on ready status
                hud_image = self.ult_ready_hud_image if effect['is_ready'] else self.ult_not_ready_hud_image
                if hud_image is None:
                    continue
                    
                # Apply scaling and floating animation
                if 'scale' in effect and 'scale_direction' in effect:
                    # Update scale for pulsating effect
                    effect['scale'] += effect['scale_direction']
                    if effect['scale'] > 1.05 or effect['scale'] < 0.95:
                        effect['scale_direction'] *= -1
                    
                    # Update floating animation
                    if 'float_offset' in effect and 'float_direction' in effect:
                        effect['float_offset'] += effect['float_direction']
                        if abs(effect['float_offset']) > 5:  # Maximum float distance
                            effect['float_direction'] *= -1
                    
                    # Get original dimensions
                    original_width = hud_image.get_width()
                    original_height = hud_image.get_height()
                    
                    # Calculate new dimensions
                    new_width = int(original_width * effect['scale'])
                    new_height = int(original_height * effect['scale'])
                    
                    # Scale the image
                    scaled_surface = pygame.transform.scale(hud_image, (new_width, new_height))
                    
                    # Adjust position for scaling and floating
                    x, y = effect['position']
                    center_x = x + original_width // 2
                    center_y = y + original_height // 2
                    new_x = center_x - new_width // 2
                    new_y = center_y - new_height // 2 + effect['float_offset']  # Apply floating offset
                    
                    # Set alpha and blit
                    scaled_surface.set_alpha(effect['alpha'])
                    screen.blit(scaled_surface, (new_x, new_y))
                    
                    # Add the appropriate text below the icon
                    if effect.get('show_text', False):
                        font = pygame.font.SysFont(None, 36)  # Font and size
                        
                        # Text and color depend on the ultimate state
                        if effect['is_ready']:
                            text_color = (255, 255, 0)  # Yellow for Ready
                            text_content = "Ultimate Ready"
                        else:
                            text_color = (200, 200, 200)  # Light gray for Not Ready
                            text_content = "Ultimate Not Ready"
                        
                        text_surface = font.render(text_content, True, text_color)
                        
                        # Apply the same alpha to the text
                        text_surface.set_alpha(effect['alpha'])
                        
                        # Position the text centered below the icon
                        text_x = new_x + (new_width - text_surface.get_width()) // 2
                        text_y = new_y + new_height + 10  # 10 pixels below the icon
                        
                        # Draw the text
                        screen.blit(text_surface, (text_x, text_y))
                else:
                    # Just apply alpha if no scaling info
                    img_copy = hud_image.copy()
                    img_copy.set_alpha(effect['alpha'])
                    screen.blit(img_copy, effect['position'])
                    
                    # Add the appropriate text below the icon
                    if effect.get('show_text', False):
                        font = pygame.font.SysFont(None, 36)  # Font and size
                        
                        # Text and color depend on the ultimate state
                        if effect['is_ready']:
                            text_color = (255, 255, 0)  # Yellow for Ready
                            text_content = "Ultimate Ready"
                        else:
                            text_color = (200, 200, 200)  # Light gray for Not Ready
                            text_content = "Ultimate Not Ready"
                            
                        text_surface = font.render(text_content, True, text_color)
                        
                        # Apply the same alpha to the text
                        text_surface.set_alpha(effect['alpha'])
                        
                        # Position the text aligned with the icon in the top right corner
                        text_x = effect['position'][0]  # Alinhado à esquerda com o ícone
                        text_y = effect['position'][1] + hud_image.get_height() + 5  # 5 pixels below the icon
                        
                        # Draw the text
                        screen.blit(text_surface, (text_x, text_y))
