import pygame

# --- Manages all game states (menu, playing, paused, game over) ---
class GameState:
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    MENU = 'menu'

    def fade_out(self, screen, background):
        import pygame
        fade = pygame.Surface((screen.get_width(), screen.get_height()))
        fade.fill((0,0,0))
        alpha = 0
        speeds = list(background.speeds)
        for step in range(32):
            for i in range(len(background.speeds)):
                background.speeds[i] = speeds[i] * (1 - step/32)
            background.update()
            background.draw(screen)
            fade.set_alpha(alpha)
            screen.blit(fade, (0,0))
            pygame.display.flip()
            pygame.time.delay(16)
            alpha = min(255, alpha + 8)
        fade.set_alpha(255)
        screen.blit(fade, (0,0))
        pygame.display.flip()
        pygame.time.delay(300)

    def __init__(self):
        self.state = GameState.MENU
        self.restart_callback = None  # Function to restart the game
        self.music_on = True
        self.music_volume = 0.2  # Initial volume is 20%
        self.settings_index = 0
        self.menu_index = 0
        self.pause_index = 0
        self.gameover_index = 0
        try:
            from game_sounds import GameSounds
            GameSounds.set_volume(self.music_volume)
        except Exception:
            pass

    def set_restart_callback(self, callback):
        self.restart_callback = callback

    def set_state(self, new_state):
        self.state = new_state

    def is_playing(self):
        return self.state == GameState.PLAYING

    def handle_event(self, event):
        if self.state == GameState.MENU:
            if not hasattr(self, 'menu_index'):
                self.menu_index = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if self.menu_index == 0:
                        self.set_state(GameState.PLAYING)
                    elif self.menu_index == 1:
                        self.set_state('settings')
                    elif self.menu_index == 2:
                        self.set_state('leave_game')
        elif self.state == GameState.PAUSED:
            if not hasattr(self, 'pause_index'):
                self.pause_index = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pause_index = (self.pause_index - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.pause_index = (self.pause_index + 1) % 4
                elif event.key == pygame.K_RETURN:
                    if self.pause_index == 0:
                        self.set_state(GameState.PLAYING)
                    elif self.pause_index == 1:
                        self.set_state('settings')
                    elif self.pause_index == 2:
                        self.set_state(GameState.MENU)
                    elif self.pause_index == 3:
                        self.set_state('leave_game')
        elif self.state == GameState.GAME_OVER:
            if not hasattr(self, 'gameover_index'):
                self.gameover_index = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.gameover_index = (self.gameover_index - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.gameover_index = (self.gameover_index + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if self.gameover_index == 0 and self.restart_callback:
                        self.restart_callback()
                    elif self.gameover_index == 1:
                        self.set_state(GameState.MENU)
                    elif self.gameover_index == 2:
                        self.set_state('leave_game')
        elif self.state == 'settings':
            from game_sounds import GameSounds
            options = ['Music', 'Music Volume', 'Back']
            if not hasattr(self, 'settings_index'):
                self.settings_index = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.settings_index = (self.settings_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    self.settings_index = (self.settings_index + 1) % len(options)
                elif event.key == pygame.K_LEFT:
                    if self.settings_index == 0:
                        self.music_on = not self.music_on
                        if self.music_on:
                            GameSounds.resume()
                        else:
                            GameSounds.pause()
                    elif self.settings_index == 1:
                        self.music_volume = max(0.0, self.music_volume - 0.1)
                        GameSounds.set_volume(self.music_volume)
                elif event.key == pygame.K_RIGHT:
                    if self.settings_index == 0:
                        self.music_on = not self.music_on
                        if self.music_on:
                            GameSounds.resume()
                        else:
                            GameSounds.pause()
                    elif self.settings_index == 1:
                        self.music_volume = min(1.0, self.music_volume + 0.1)
                        GameSounds.set_volume(self.music_volume)
                elif event.key == pygame.K_RETURN:
                    if self.settings_index == 2:
                        # Back
                        self.set_state(GameState.MENU)
                    elif self.gameover_index == 2:
                        self.set_state('leave_game')
        elif event.type == pygame.KEYDOWN:
            if self.state == GameState.PLAYING and event.key == pygame.K_ESCAPE:
                self.set_state(GameState.PAUSED)
            elif self.state == GameState.PAUSED and event.key == pygame.K_ESCAPE:
                self.set_state(GameState.PLAYING)

    def update(self, player):
        if self.state == GameState.PLAYING and player.hp <= 0:
            self.set_state(GameState.GAME_OVER)

    def draw(self, screen, font, screen_width, screen_height, background=None):
        leave_game = False
        if self.state == GameState.MENU:
            # Animated background
            if background:
                background.update()
                background.draw(screen)
            else:
                screen.fill((30, 30, 30))
            # Logo
            import os
            logo_path = os.path.join('assets', 'logo', 'logo.png')
            if not hasattr(self, 'logo_img'):
                if os.path.exists(logo_path):
                    logo_img = pygame.image.load(logo_path).convert_alpha()
                    logo_img = pygame.transform.smoothscale(logo_img, (400, 200))
                    self.logo_img = logo_img
                else:
                    self.logo_img = None
            if self.logo_img:
                logo_rect = self.logo_img.get_rect()
                logo_rect.centerx = screen_width // 2
                logo_rect.top = 30
                screen.blit(self.logo_img, logo_rect)
            # Menu options
            options = ['Play Game', 'Settings', 'Leave Game']
            if not hasattr(self, 'menu_index'):
                self.menu_index = 0
            option_font = pygame.font.SysFont(None, 48)
            y_start = logo_rect.bottom + 30 if self.logo_img else 250
            for i, opt in enumerate(options):
                color = (255,255,200) if i == self.menu_index else (180,180,180)
                opt_txt = option_font.render(opt, True, color)
                screen.blit(opt_txt, (screen_width//2 - opt_txt.get_width()//2, y_start + i*70))
            # Instructions
            instr_font = pygame.font.SysFont(None, 28)
            instr = instr_font.render('Use arrows to navigate, ENTER to select', True, (220,220,220))
            screen.blit(instr, (screen_width//2 - instr.get_width()//2, screen_height-60))
        elif self.state == GameState.PAUSED:
            # Animated background
            if background:
                background.update()
                background.draw(screen)
            else:
                screen.fill((30, 30, 30))
            options = ['Resume Game', 'Settings', 'Go to Menu', 'Leave Game']
            if not hasattr(self, 'pause_index'):
                self.pause_index = 0
            title_font = pygame.font.SysFont(None, 64)
            option_font = pygame.font.SysFont(None, 44)
            title = title_font.render('PAUSED', True, (255,255,0))
            screen.blit(title, (screen_width//2 - title.get_width()//2, 120))
            for i, opt in enumerate(options):
                color = (255,255,200) if i == self.pause_index else (180,180,180)
                opt_txt = option_font.render(opt, True, color)
                screen.blit(opt_txt, (screen_width//2 - opt_txt.get_width()//2, 230 + i*60))
            instr_font = pygame.font.SysFont(None, 28)
            instr = instr_font.render('Use arrows to navigate, ENTER to select', True, (220,220,220))
            screen.blit(instr, (screen_width//2 - instr.get_width()//2, screen_height-60))
        elif self.state == GameState.GAME_OVER:
            # Animated background
            if background:
                background.update()
                background.draw(screen)
            else:
                screen.fill((20,0,0))
            # GAME OVER
            title_font = pygame.font.SysFont(None, 80)
            title = title_font.render('GAME OVER', True, (255,50,50))
            screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
            # Kills and time survived
            kills = getattr(self, 'last_kills', 0)
            elapsed_time = getattr(self, 'last_time', 0)
            info_font = pygame.font.SysFont(None, 44)
            min_ = elapsed_time // 60
            sec_ = elapsed_time % 60
            time_txt = info_font.render(f"Tempo: {min_:02}:{sec_:02}", True, (255,255,255))
            kills_txt = info_font.render(f"Kills: {kills}", True, (255,255,255))
            screen.blit(time_txt, (screen_width//2 - time_txt.get_width()//2, 210))
            screen.blit(kills_txt, (screen_width//2 - kills_txt.get_width()//2, 260))
            # Game over options
            options = ['Restart', 'Go to Menu', 'Leave Game']
            if not hasattr(self, 'gameover_index'):
                self.gameover_index = 0
            option_font = pygame.font.SysFont(None, 44)
            for i, opt in enumerate(options):
                color = (255,255,200) if i == self.gameover_index else (180,180,180)
                opt_txt = option_font.render(opt, True, color)
                screen.blit(opt_txt, (screen_width//2 - opt_txt.get_width()//2, 340 + i*60))
            instr_font = pygame.font.SysFont(None, 28)
            instr = instr_font.render('Use arrows to navigate, ENTER to select', True, (220,220,220))
            screen.blit(instr, (screen_width//2 - instr.get_width()//2, screen_height-60))
        elif self.state == 'settings':
            # Draw settings screen with animated background
            if background:
                background.update()
                background.draw(screen)
            else:
                screen.fill((30, 30, 30))
            title_font = pygame.font.SysFont(None, 72)
            option_font = pygame.font.SysFont(None, 48)
            title = title_font.render('SETTINGS', True, (255,255,255))
            screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
            options = ['Music', 'Music Volume', 'Back']
            values = ["On" if self.music_on else "Off", f"{int(self.music_volume*100)}%", ""]
            for i, opt in enumerate(options):
                color = (255,255,200) if i == self.settings_index else (180,180,180)
                if values[i]:
                    text = f"{opt}: {values[i]}"
                else:
                    text = opt
                opt_txt = option_font.render(text, True, color)
                screen.blit(opt_txt, (screen_width//2 - opt_txt.get_width()//2, 240 + i*60))
            instr_font = pygame.font.SysFont(None, 28)
            instr = instr_font.render('Use arrows to change option/volume, ENTER to go back', True, (220,220,220))
            screen.blit(instr, (screen_width//2 - instr.get_width()//2, screen_height-60))
        return leave_game