import random
from enemies import FatGirlEnemy, WolfEnemy, BlueBirdEnemy, RedBirdEnemy
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Spawner:
    def __init__(self):
        self.spawn_timer = 0
        self.difficulty_timer = 0
        self.difficulty = 1
        self.game_time = 0
        self.enemies = []

    def update(self, player_alive=True):
        self.game_time += 1
        self.spawn_timer += 1
        self.difficulty_timer += 1
        new_enemy = None
        if self.difficulty_timer > 600:  # Every 10 seconds
            self.difficulty += 1
            self.difficulty_timer = 0
        if player_alive and self.spawn_timer > max(30, 120 - self.difficulty*10):
            self.spawn_timer = 0
            side = random.choice(['left', 'right'])
            x = 0 if side == 'left' else SCREEN_WIDTH-180
            direction = 'right' if side == 'left' else 'left'
            enemy_type = random.choices(['blue_bird', 'red_bird', 'wolf', 'fatgirl'], weights=[1,1,1,1])[0]
            if enemy_type == 'blue_bird':
                y = random.randint(180, 250)
                speed = 7 + self.difficulty//2
                dmg_min = 2 + self.difficulty//2
                dmg_max = 6 + self.difficulty//2
                new_enemy = BlueBirdEnemy(x, y, direction, speed=speed, dmg_min=dmg_min, dmg_max=dmg_max)
            elif enemy_type == 'red_bird':
                y = random.randint(180, 250)
                speed = 7 + self.difficulty//2
                dmg_min = 2 + self.difficulty//2
                dmg_max = 6 + self.difficulty//2
                new_enemy = RedBirdEnemy(x, y, direction, speed=speed, dmg_min=dmg_min, dmg_max=dmg_max)
            elif enemy_type == 'wolf':
                speed = 6 + self.difficulty//2
                dmg_min = 1 + self.difficulty//2
                dmg_max = 7 + self.difficulty//2
                new_enemy = WolfEnemy(x, SCREEN_HEIGHT-250, direction, speed=speed, dmg_min=dmg_min, dmg_max=dmg_max)
            else:
                speed = 3 + self.difficulty//3
                dmg_min = 3 + self.difficulty//2
                dmg_max = 11 + self.difficulty//2
                new_enemy = FatGirlEnemy(x, SCREEN_HEIGHT-250, direction, speed=speed, dmg_min=dmg_min, dmg_max=dmg_max)
        return new_enemy

    def reset(self):
        self.spawn_timer = 0
        self.difficulty_timer = 0
        self.difficulty = 1
        self.game_time = 0
        self.enemies = []
