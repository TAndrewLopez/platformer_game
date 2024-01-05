import pygame as pg
from os import walk
from csv import reader

from settings import tile_size


def import_folder(path):
    surface_list = []

    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surface = pg.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list


def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=",")
        for row in level:
            terrain_map.append(list(row))

        return terrain_map


def import_cut_graphics(path):
    surface = pg.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_width() / tile_size)
    tile_num_y = int(surface.get_height() / tile_size)
    cut_tiles = []

    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surface = pg.Surface((tile_size, tile_size), flags=pg.SRCALPHA)
            new_surface.blit(surface, (0, 0), pg.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surface)

    return cut_tiles
