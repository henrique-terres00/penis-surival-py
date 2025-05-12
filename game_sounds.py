import pygame
import os

# Path to the soundtrack (assumes the file game_sounds/soundtrack.mp3 exists)
SOUNDTRACK_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'game_sounds', 'soundtrack.mp3')
MILKY_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'game_sounds', 'milky.mp3')

# Initialize the mixer with more channels
pygame.mixer.init()
pygame.mixer.set_num_channels(8)  # Increase the number of available channels

# Reserve a channel for the Milky effect
MILKY_CHANNEL = pygame.mixer.Channel(1)  # Channel 0 is used for background music

class GameSounds:
    @staticmethod
    def play_soundtrack():
        pygame.mixer.init()
        pygame.mixer.music.load(SOUNDTRACK_PATH)
        pygame.mixer.music.play(-1)  # -1 means loop forever

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

    @staticmethod
    def play_milky_effect():
        # Load the Milky sound effect
        milky_sound = pygame.mixer.Sound(MILKY_PATH)
        # Plays the sound effect on a separate channel to avoid interrupting the background music
        MILKY_CHANNEL.play(milky_sound)
