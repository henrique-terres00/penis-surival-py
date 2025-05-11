import pygame
import os

# Path to the soundtrack (assumes the file game_sounds/soundtrack.mp3 exists)
SOUNDTRACK_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'game_sounds', 'soundtrack.mp3')

class GameSounds:
    @staticmethod
    def play_soundtrack():
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(SOUNDTRACK_PATH)
            pygame.mixer.music.play(-1)  # -1 means loop forever
        except Exception as e:
            print(f"Error loading soundtrack: {e}")

    @staticmethod
    def stop_soundtrack():
        pygame.mixer.music.stop()

    @staticmethod
    def set_volume(volume: float):
        # Clamp volume between 0.0 and 1.0
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)

    @staticmethod
    def get_volume():
        return pygame.mixer.music.get_volume()

    @staticmethod
    def pause():
        pygame.mixer.music.pause()

    @staticmethod
    def resume():
        pygame.mixer.music.unpause()