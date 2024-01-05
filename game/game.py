import pygame as pg

from level import Level
from overworld import Overworld
from ui import UI


class Game:
    def __init__(self, surface):
        self.display_surface = surface

        # GAME ATTRIBUTES
        self.max_level = 0
        self.max_health = 100
        self.current_health = 100
        self.coins = 0

        # AUDIO
        self.level_bg_music = pg.mixer.Sound("../audio/level_music.wav")
        self.overworld_bg_music = pg.mixer.Sound("../audio/overworld_music.wav")

        # OVERWORLD CREATION
        self.overworld = Overworld(
            0, self.max_level, self.display_surface, self.create_level
        )
        self.status = "overworld"
        self.overworld_bg_music.play(loops=-1)

        # USER INTERFACE
        self.ui = UI(self.display_surface)

    def create_level(self, current_level):
        self.level = Level(
            current_level,
            self.display_surface,
            self.create_overworld,
            self.change_coins,
            self.change_health,
        )
        self.status = "level"
        self.overworld_bg_music.stop()
        self.level_bg_music.play(loops=-1)

    def create_overworld(self, current_level, new_max_level):
        self.level_bg_music.stop()
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(
            current_level, self.max_level, self.display_surface, self.create_level
        )
        self.status = "overworld"
        self.overworld_bg_music.play(loops=-1)

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.current_health += amount

    def check_game_over(self):
        if self.current_health <= 0:
            self.current_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(
                0, self.max_level, self.display_surface, self.create_level
            )
            self.status = "overworld"
            self.level_bg_music.stop()
            self.overworld_bg_music.play(loops=-1)

    def run(self):
        if self.status == "overworld":
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
