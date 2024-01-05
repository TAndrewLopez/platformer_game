import pygame as pg, sys

from game import Game
from settings import *

pg.init()
screen = pg.display.set_mode((screen_width, screen_height))
clock = pg.time.Clock()
game = Game(screen)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.fill("grey")
    game.run()

    pg.display.update()
    clock.tick(60)
