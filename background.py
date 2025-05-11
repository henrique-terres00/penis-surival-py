import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class ParallaxBackground:
    def __init__(self, background_dir):
        self.layers = self.load_layers(background_dir)
        self.speeds = [0.2 + 0.3 * i for i in range(len(self.layers))]
        self.offsets = [0.0 for _ in self.layers]

    def load_layers(self, background_dir):
        layers = []
        for file in sorted(os.listdir(background_dir)):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = pygame.image.load(os.path.join(background_dir, file)).convert_alpha()
                img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                layers.append(img)
        return layers

    def update(self):
        for i in range(len(self.layers)):
            self.offsets[i] -= self.speeds[i]
            if self.offsets[i] <= -SCREEN_WIDTH:
                self.offsets[i] += SCREEN_WIDTH

    def draw(self, surface):
        for i, layer in enumerate(self.layers):
            x = int(self.offsets[i])
            surface.blit(layer, (x, 0))
            surface.blit(layer, (x + SCREEN_WIDTH, 0))