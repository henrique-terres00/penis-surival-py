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
        popup[2] -= 1
        popup[3] = max(0, popup[3]-8)
        popup[4] += 1
        if popup[3] <= 0 or popup[4] > 40:
            popups.remove(popup)

# Draw damage popups
font = None
def draw_damage_popups(surface, popups):
    global font
    if font is None:
        font = pygame.font.SysFont('arial', 26, bold=True)
    for popup in popups:
        dmg, x, y, alpha, timer = popup
        text = font.render(str(dmg), True, (255,0,0))
        text.set_alpha(alpha)
        surface.blit(text, (x - text.get_width()//2, y))

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