import pygame as pg

from decoration import Sky, Water, Clouds
from enemy import Enemy
from game_data import levels
from particle import ParticleEffect
from player import Player
from settings import tile_size, screen_height, screen_width
from support import import_csv_layout, import_cut_graphics
from tiles import Tile, StaticTile, Crate, Coin, Palm


class Level:
    def __init__(
        self, current_level, surface, create_overworld, change_coins, change_health
    ):
        # GENERAL SETUP
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # AUDIO SETUP
        self.coin_sound = pg.mixer.Sound("../audio/effects/coin.wav")
        self.stomp_sound = pg.mixer.Sound("../audio/effects/stomp.wav")

        # OVERWORLD SETUP
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data["unlock"]

        # PLAYER SETUP
        player_layout = import_csv_layout(level_data["player"])
        self.player = pg.sprite.GroupSingle()
        self.goal = pg.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # USER INTERFACE SETUP
        self.change_coins = change_coins

        # EXPLOSION PARTICLES SETUP
        self.explosion_sprites = pg.sprite.Group()

        # DUST SETUP
        self.dust_sprite = pg.sprite.GroupSingle()
        self.player_on_ground = False

        # TERRAIN SETUP
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        # GRASS SETUP
        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_sprites = self.create_tile_group(grass_layout, "grass")

        # CRATES SETUP
        crate_layout = import_csv_layout(level_data["crates"])
        self.crate_sprites = self.create_tile_group(crate_layout, "crates")

        # COINS SETUP
        coin_layout = import_csv_layout(level_data["coins"])
        self.coin_sprites = self.create_tile_group(coin_layout, "coins")

        # FG PALM SETUP
        fg_palm_layout = import_csv_layout(level_data["fg palms"])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, "fg palms")

        # BG PALM SETUP
        bg_palm_layout = import_csv_layout(level_data["bg palms"])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, "bg palms")

        # ENEMY SETUP
        enemy_layout = import_csv_layout(level_data["enemies"])
        self.enemy_sprites = self.create_tile_group(enemy_layout, "enemies")

        # CONSTRAINT SETUP
        constraint_layout = import_csv_layout(level_data["constraints"])
        self.constrains_sprites = self.create_tile_group(
            constraint_layout, "constraints"
        )

        # DECORATION
        self.sky = Sky(8)
        level_width = len(terrain_layout[0] * tile_size)
        self.water = Water(screen_height - 20, level_width)
        self.clouds = Clouds(400, level_width, 30)

    def create_tile_group(self, layout, type):
        sprite_group = pg.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == "terrain":
                        terrain_tile_list = import_cut_graphics(
                            "../graphics/terrain/terrain_tiles.png"
                        )
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "grass":
                        grass_tile_list = import_cut_graphics(
                            "../graphics/decoration/grass/grass.png"
                        )
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "crates":
                        sprite = Crate(tile_size, x, y)

                    if type == "coins":
                        if val == "0":
                            sprite = Coin(tile_size, x, y, "../graphics/coins/gold/", 5)
                        if val == "1":
                            sprite = Coin(
                                tile_size, x, y, "../graphics/coins/silver/", 1
                            )

                    if type == "fg palms":
                        if val == "0":
                            sprite = Palm(
                                tile_size, x, y, "../graphics/terrain/palm_small", 38
                            )
                        if val == "1":
                            sprite = Palm(
                                tile_size, x, y, "../graphics/terrain/palm_large", 64
                            )

                    if type == "bg palms":
                        sprite = Palm(
                            tile_size, x, y, "../graphics/terrain/palm_bg", 64
                        )

                    if type == "enemies":
                        sprite = Enemy(tile_size, x, y)

                    if type == "constraints":
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == "0":
                    sprite = Player(
                        (x, y),
                        self.display_surface,
                        self.create_jump_particles,
                        change_health,
                    )
                    self.player.add(sprite)
                if val == "1":
                    hat_surface = pg.image.load(
                        "../graphics/character/hat.png"
                    ).convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pg.sprite.spritecollide(enemy, self.constrains_sprites, False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pg.math.Vector2(10, 5)
        else:
            pos += pg.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, "jump")
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed
        collidable_sprites = (
            self.terrain_sprites.sprites()
            + self.crate_sprites.sprites()
            + self.fg_palm_sprites.sprites()
        )

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True

                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = (
            self.terrain_sprites.sprites()
            + self.crate_sprites.sprites()
            + self.fg_palm_sprites.sprites()
        )

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
                elif player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_particles(self):
        if (
            not self.player_on_ground
            and self.player.sprite.on_ground
            and not self.dust_sprite.sprites()
        ):
            if self.player.sprite.facing_right:
                offset = pg.math.Vector2(10, 15)
            else:
                offset = pg.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(
                self.player.sprite.rect.midbottom - offset, "land"
            )
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pg.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pg.sprite.spritecollide(
            self.player.sprite, self.coin_sprites, True
        )
        if collided_coins:
            self.coin_sound.play()
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_enemy_collision(self):
        enemy_collisions = pg.sprite.spritecollide(
            self.player.sprite, self.enemy_sprites, False
        )

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom

                if (
                    enemy_top < player_bottom < enemy_center
                    and self.player.sprite.direction.y >= 0
                ):
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, "explosion")
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def run(self):
        # RUN THE ENTIRE GAME / LEVEL

        # DECORATION
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # BACKGROUND PALMS
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        # DUST PARTICLES
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # TERRAIN
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # ENEMIES
        self.enemy_sprites.update(self.world_shift)
        self.constrains_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        # CRATES
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # GRASS
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # COINS
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # FOREGROUND PALMS
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        # PLAYER SPRITES
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_particles()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()
        self.check_coin_collisions()
        self.check_enemy_collision()

        # WATER
        self.water.draw(self.display_surface, self.world_shift)
