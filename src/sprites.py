from collections.abc import Sequence
from random import randint

import pygame
from pygame import (
    locals as lc,
)

from .abstract_classes import BaseSprite, SpriteWithDirection
from .config import DEBUG, DISPLAY, GROUPS, display
from .hitbox import Hitbox
from .tilemap_animation import PlayerTMAnimation


class Player(SpriteWithDirection):
    def __init__(self, speed: int) -> None:
        super().__init__()

        self.speed = speed
        self.direction = pygame.Vector2()

        self.hitbox = Hitbox(self)
        self.tilemap_animations = PlayerTMAnimation(self)

        self.image = next(self.tilemap_animations.current_animation)
        self.rect = self.image.get_frect()

    def update(self, dt: float) -> None:
        self.direction.update(self.delta_move_vector)
        self.move(dt)

        self.tilemap_animations.change_animation()
        self.image = next(self.tilemap_animations.current_animation)

        self.hitbox.try_to_not_collide_with_blocks()

        if DEBUG:
            pygame.draw.rect(display, "red", self.rect, 7)
            pygame.draw.rect(display, "green", self.hitbox.rect, 7)

    @property
    def delta_move_vector(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        delta = pygame.Vector2(
            (keys[lc.K_RIGHT] or keys[lc.K_d])
            - (keys[lc.K_LEFT] or keys[lc.K_a]),
            (keys[lc.K_DOWN] or keys[lc.K_s])
            - (keys[lc.K_UP] or keys[lc.K_w]),
        )
        delta = delta and delta.normalize()

        mods = pygame.key.get_mods()
        if mods & lc.KMOD_SHIFT:
            delta *= 1.5

        return delta

    def move(self, dt: float) -> None:
        self.rect.x += self.direction.x * self.speed * dt
        if self.hitbox.block_collides():
            self.rect.x -= self.direction.x * self.speed * dt

        self.rect.y += self.direction.y * self.speed * dt
        if self.hitbox.block_collides():
            self.rect.y -= self.direction.y * self.speed * dt


class Block(BaseSprite):
    SIZE = pygame.Vector2(100, 100)

    def __init__(self, color: Sequence[int] | str | int) -> None:
        super().__init__(GROUPS.BLOCKS)

        self.image = pygame.Surface(self.SIZE)
        self.image.fill(color)

        self.rect = self.image.get_frect()
        ceil = (DISPLAY.SIZE - self.rect.size).elementwise() / self.SIZE

        while True:
            self.rect.topleft = (
                pygame.Vector2(
                    randint(0, int(ceil.x)),  # noqa: S311
                    randint(0, int(ceil.y)),  # noqa: S311
                ).elementwise()
                * self.SIZE
            )
            for sprite in GROUPS.UNIVERSUM.sprites():
                if sprite.rect and not (
                    self.rect.contains(sprite.rect)
                    or not self.rect.colliderect(sprite.rect)
                ):
                    break
            else:
                break

    def update(self, dt: float) -> None:
        super().update(dt)
