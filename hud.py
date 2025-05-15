import pygame

# Draw health bar with text (for player or enemy)
def draw_health_bar(surface, x, y, w, h, hp, max_hp):
    fill = int(w * (hp / max_hp))
    # Red bar
    pygame.draw.rect(surface, (80,0,0), (x, y, w, h))
    pygame.draw.rect(surface, (220,20,40), (x, y, fill, h))
    pygame.draw.rect(surface, (60,0,0), (x, y, w, h), 3)
    # HP text
    font = pygame.font.SysFont(None, int(h*1.1))
    text = font.render(f"{int(hp)}/{int(max_hp)}", True, (255,255,255))
    surface.blit(text, (x + w//2 - text.get_width()//2, y + h//2 - text.get_height()//2))

# Draw mana bar with text
def draw_mana_bar(surface, x, y, w, h, mana, max_mana):
    fill = int(w * (mana / max_mana))
    # Blue bar
    pygame.draw.rect(surface, (30,30,80), (x, y, w, h))
    pygame.draw.rect(surface, (80,120,255), (x, y, fill, h))
    pygame.draw.rect(surface, (20,20,60), (x, y, w, h), 3)
    # Mana text
    font = pygame.font.SysFont(None, int(h*1.1))
    text = font.render(f"{int(mana)}/{int(max_mana)}", True, (220,220,255))
    surface.blit(text, (x + w//2 - text.get_width()//2, y + h//2 - text.get_height()//2))

# Utility to update and remove expired damage popups
def update_damage_popups(popups):
    for popup in popups[:]:
        try:
            popup[2] -= 1  # Move the popup upward
            popup[3] = max(0, popup[3]-8)  # Reduce alpha (transparency)
            popup[4] += 1  # Increment timer
            if popup[3] <= 0 or popup[4] > 40:
                popups.remove(popup)
        except Exception as e:
            # If there's any error, remove the problematic popup
            if popup in popups:
                popups.remove(popup)

# Draw damage popups
font = None
def draw_damage_popups(surface, popups):
    global font
    if font is None:
        font = pygame.font.SysFont('arial', 26, bold=True)
    for popup in popups:
        if len(popup) >= 6:
            # Popup format: [value, x, y, alpha, timer, type]
            dmg, x, y, alpha, timer, popup_type = popup
            
            # Define the color based on the popup type (damage, heal, or mana)
            if popup_type == "heal":
                # Green for heal
                color = (0, 255, 0)
                # Adds a '+' before the value to indicate healing
                text = font.render("+" + str(dmg), True, color)
            elif popup_type == "mana":
                # Blue for mana
                color = (0, 100, 255)
                # Adds a '+' before the value to indicate mana gain
                text = font.render("+" + str(dmg), True, color)
            else:
                # Red for damage
                color = (255, 0, 0)
                text = font.render(str(dmg), True, color)
        else:
            # Old popup format: [value, x, y, alpha, timer]
            dmg, x, y, alpha, timer = popup
            # Red for damage (default behavior)
            color = (255, 0, 0)
            text = font.render(str(dmg), True, color)
            
        text.set_alpha(alpha)
        surface.blit(text, (x - text.get_width()//2, y))

# Dictionary to store skill icons (loaded once)
skill_icons = {}

# Dictionary to store animation state for each skill icon
skill_animations = {
    'ultimate': {
        'scale': 1.0,
        'scale_direction': 0.005,  # Amount to increase/decrease scale each frame
        'float_offset': 0,
        'float_direction': 0.3,  # Pixels to move up/down per frame
    },
    'grenade': {
        'scale': 1.0,
        'scale_direction': 0.005,
        'float_offset': 0,
        'float_direction': 0.3,
    }
}

# Draw skill icons in the HUD
def draw_skill_icons(surface, player):
    # Draw skill icons in the center top of the screen
    # Each icon shows a different skill and its cooldown status
    
    # Define icon size and spacing (30% larger than before)
    icon_size = (100, 100)  # Increased size by 30% (from 60x60)
    icon_spacing = 20  # Space between icons
    
    # Load grenade icons if not already loaded
    if 'grenade_ready' not in skill_icons or 'grenade_not_ready' not in skill_icons:
        try:
            # Load the ready and not ready images for grenade
            ready_img = pygame.image.load('assets/effects/grenade/granada_ready.png').convert_alpha()
            not_ready_img = pygame.image.load('assets/effects/grenade/grenade_not_ready.png').convert_alpha()
            
            # Scale them to our icon size
            skill_icons['grenade_ready'] = pygame.transform.scale(ready_img, icon_size)
            skill_icons['grenade_not_ready'] = pygame.transform.scale(not_ready_img, icon_size)
        except Exception as e:
            print(f"Error loading grenade icons: {e}")
            # Create fallback icons
            fallback_ready = pygame.Surface(icon_size, pygame.SRCALPHA)
            fallback_not_ready = pygame.Surface(icon_size, pygame.SRCALPHA)
            pygame.draw.rect(fallback_ready, (0, 255, 0), (0, 0, icon_size[0], icon_size[1]))
            pygame.draw.rect(fallback_not_ready, (255, 0, 0), (0, 0, icon_size[0], icon_size[1]))
            skill_icons['grenade_ready'] = fallback_ready
            skill_icons['grenade_not_ready'] = fallback_not_ready
    
    # Load ultimate icons if not already loaded
    if 'ultimate_ready' not in skill_icons or 'ultimate_not_ready' not in skill_icons:
        try:
            # Load the ready and not ready images for ultimate
            ready_img = pygame.image.load('assets/effects/ultimate_hud/ult_ready_hud.png').convert_alpha()
            not_ready_img = pygame.image.load('assets/effects/ultimate_hud/ult_not_ready_hud.png').convert_alpha()
            
            # Scale them to our icon size
            skill_icons['ultimate_ready'] = pygame.transform.scale(ready_img, icon_size)
            skill_icons['ultimate_not_ready'] = pygame.transform.scale(not_ready_img, icon_size)
        except Exception as e:
            print(f"Error loading ultimate icons: {e}")
            # Create fallback icons
            fallback_ready = pygame.Surface(icon_size, pygame.SRCALPHA)
            fallback_not_ready = pygame.Surface(icon_size, pygame.SRCALPHA)
            pygame.draw.rect(fallback_ready, (255, 255, 255), (0, 0, icon_size[0], icon_size[1]))
            pygame.draw.rect(fallback_not_ready, (100, 100, 100), (0, 0, icon_size[0], icon_size[1]))
            skill_icons['ultimate_ready'] = fallback_ready
            skill_icons['ultimate_not_ready'] = fallback_not_ready
    
    # List of skills: (skill_name, current_cooldown, max_cooldown, has_enough_mana, key)
    skills = [
        ('ultimate', player.ultimate_cooldown, 300, player.mana >= player.max_mana, 'X'),  # Ultimate - X key
        ('grenade', player.grenade_cooldown, player.grenade_cooldown_max, player.mana >= player.grenade_mana_cost, 'Q')  # Grenade - Q key
    ]
    
    # Calculate total width of all icons plus spacing
    total_width = len(skills) * icon_size[0] + (len(skills) - 1) * icon_spacing
    
    # Center horizontally, position at top with some margin
    start_x = (surface.get_width() - total_width) // 2
    base_icon_y = 20  # 20px from top
    
    # Draw each skill icon
    for i, (skill_name, cooldown, max_cooldown, has_mana, key) in enumerate(skills):
        # Update animation state
        if skill_name not in skill_animations:
            skill_animations[skill_name] = {
                'scale': 1.0,
                'scale_direction': 0.005,
                'float_offset': 0,
                'float_direction': 0.3,
            }
        
        # Get animation state
        anim = skill_animations[skill_name]
        
        # Update scale (pulsating effect)
        anim['scale'] += anim['scale_direction']
        if anim['scale'] > 1.1 or anim['scale'] < 0.9:
            anim['scale_direction'] *= -1  # Reverse direction
        
        # Update float offset (floating effect)
        anim['float_offset'] += anim['float_direction']
        if abs(anim['float_offset']) > 3:  # Limit the float range
            anim['float_direction'] *= -1  # Reverse direction
        
        # Apply animation only if the skill is ready
        is_ready = cooldown <= 0 and has_mana
        
        # Calculate position with animation
        icon_x = start_x + i * (icon_size[0] + icon_spacing)
        icon_y = base_icon_y
        
        # Apply floating animation if ready
        if is_ready:
            icon_y += anim['float_offset']
        
        # Create a cooldown overlay if needed
        if cooldown > 0:
            # Draw cooldown overlay
            cooldown_overlay = pygame.Surface(icon_size, pygame.SRCALPHA)
            cooldown_height = int(icon_size[1] * (cooldown / max_cooldown))
            cooldown_y = 0  # Start from top
            pygame.draw.rect(cooldown_overlay, (100, 100, 100, 150), (0, cooldown_y, icon_size[0], cooldown_height))
        
        # Select the appropriate icon
        if skill_name == 'grenade':
            icon = skill_icons['grenade_ready'] if is_ready else skill_icons['grenade_not_ready']
        elif skill_name == 'ultimate':
            icon = skill_icons['ultimate_ready'] if is_ready else skill_icons['ultimate_not_ready']
        else:
            continue  # Skip unknown skills
        
        # Apply scale animation if ready
        if is_ready:
            # Calculate scaled dimensions
            scaled_size = (int(icon_size[0] * anim['scale']), int(icon_size[1] * anim['scale']))
            
            # Scale the icon
            scaled_icon = pygame.transform.scale(icon, scaled_size)
            
            # Adjust position to keep icon centered after scaling
            scaled_x = icon_x - (scaled_size[0] - icon_size[0]) // 2
            scaled_y = icon_y - (scaled_size[1] - icon_size[1]) // 2
            
            # Draw the scaled icon
            surface.blit(scaled_icon, (scaled_x, scaled_y))
        else:
            # Draw the regular icon without animation
            surface.blit(icon, (icon_x, icon_y))
            
            # Draw cooldown overlay on top if needed
            if cooldown > 0:
                surface.blit(cooldown_overlay, (icon_x, icon_y))
        
        # Draw key text below the icon
        font = pygame.font.SysFont(None, 28)  # Smaller font for key indicators
        key_text = font.render(key, True, (255, 255, 255))  # White text
        
        # Position the text centered below the icon
        text_x = icon_x + (icon_size[0] // 2) - (key_text.get_width() // 2)
        text_y = icon_y + icon_size[1] + 5  # 5px below the icon
        
        # Draw a small dark background for better visibility
        text_bg_rect = pygame.Rect(text_x - 5, text_y - 2, key_text.get_width() + 10, key_text.get_height() + 4)
        pygame.draw.rect(surface, (0, 0, 0, 150), text_bg_rect, border_radius=5)
        
        # Draw the text
        surface.blit(key_text, (text_x, text_y))

# --- Main function to draw the game HUD (health, mana, time, kills) ---
def draw_hud(surface, player, elapsed_time, kills):
    # Health
    draw_health_bar(surface, 30, 30, 200, 22, player.hp, player.max_hp)
    # Mana
    draw_mana_bar(surface, 30, 62, 200, 18, player.mana, player.max_mana)
    # Time
    font = pygame.font.SysFont(None, 32)
    min_ = elapsed_time // 60
    sec_ = elapsed_time % 60
    time_txt = font.render(f"Time alive: {min_:02}:{sec_:02}", True, (255,255,255))
    surface.blit(time_txt, (260, 30))
    # Kills
    kills_txt = font.render(f"Kills: {kills}", True, (255,255,255))
    surface.blit(kills_txt, (260, 62))
    
    # Draw skill icons
    draw_skill_icons(surface, player)