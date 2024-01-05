import pygame as pg


class UI:
    def __init__(self, surface):
        # SETUP
        self.display_surface = surface

        # HEALTH
        self.health_bar = pg.image.load("../graphics/ui/health_bar.png").convert_alpha()
        self.health_bar_topleft = (54, 39)
        self.bar_max_width = 152
        self.bar_height = 4

        # COINS
        self.coin = pg.image.load("../graphics/ui/coin.png").convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))
        self.font = pg.font.Font("../graphics/ui/ARCADEPI.ttf", 30)

    def show_health(self, current_health, full_health):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_ratio = current_health / full_health
        current_bar_width = self.bar_max_width * current_health_ratio
        health_bar_rect = pg.Rect(
            (self.health_bar_topleft), (current_bar_width, self.bar_height)
        )
        pg.draw.rect(self.display_surface, "#dc4949", health_bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surface = self.font.render(str(amount), False, "#33323d")
        coin_amount_rect = coin_amount_surface.get_rect(
            midleft=(self.coin_rect.right + 4, self.coin_rect.centery)
        )
        self.display_surface.blit(coin_amount_surface, coin_amount_rect)
