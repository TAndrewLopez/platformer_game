import pygame as pg
from random import choice, randint

from settings import vertical_tile_number, screen_width, tile_size
from support import import_folder
from tiles import AnimatedTile, StaticTile


top = "../graphics/decoration/sky/sky_top.png"
bottom = "../graphics/decoration/sky/sky_bottom.png"
middle = "../graphics/decoration/sky/sky_middle.png"


class Sky:
    def __init__(self, horizon, style="level"):
        self.top = pg.image.load(top).convert()
        self.bottom = pg.image.load(bottom).convert()
        self.middle = pg.image.load(middle).convert()
        self.horizon = horizon

        # STRETCH
        self.top = pg.transform.scale(self.top, (screen_width, tile_size))
        self.bottom = pg.transform.scale(self.bottom, (screen_width, tile_size))
        self.middle = pg.transform.scale(self.middle, (screen_width, tile_size))

        self.style = style
        if self.style == "overworld":
            palm_surfaces = import_folder("../graphics/overworld/palms")
            self.palms = []

            for surface in [choice(palm_surfaces) for image in range(10)]:
                x = randint(0, screen_width)
                y = (self.horizon * tile_size) + randint(50, 100)
                rect = surface.get_rect(midbottom=(x, y))
                self.palms.append((surface, rect))

            cloud_surfaces = import_folder("../graphics/overworld/clouds")
            self.clouds = []

            for surface in [choice(cloud_surfaces) for image in range(10)]:
                x = randint(0, screen_width)
                y = randint(0, (self.horizon * tile_size) - 100)
                rect = surface.get_rect(midbottom=(x, y))
                self.clouds.append((surface, rect))

    def draw(self, surface):
        for row in range(vertical_tile_number):
            y = row * tile_size

            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))

        if self.style == "overworld":
            for palm in self.palms:
                surface.blit(palm[0], palm[1])
            for cloud in self.clouds:
                surface.blit(cloud[0], cloud[1])


class Water:
    def __init__(self, top, level_width):
        water_start = -screen_width
        water_tile_width = 192
        tile_x_amount = int((level_width + screen_width * 2) / water_tile_width)
        self.water_sprites = pg.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(192, x, y, "../graphics/decoration/water")
            self.water_sprites.add(sprite)

    def draw(self, surface, shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)


class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surface_list = import_folder("../graphics/decoration/clouds")
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pg.sprite.Group()

        for cloud in range(cloud_number):
            cloud = choice(cloud_surface_list)
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = StaticTile(0, x, y, cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift):
        self.cloud_sprites.update(shift)
        self.cloud_sprites.draw(surface)
