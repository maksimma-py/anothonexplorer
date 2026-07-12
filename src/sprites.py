from random import randint
from typing import TYPE_CHECKING

import pygame
from pygame import locals as lc

from src.animation.decoration import (
    CANDLE_ANIMATION,
    CANDLES_ANIMATION,
    TORCH_ANIMATION,
)

from .abstract_classes import BaseSprite, SpriteWithDirection
from .animation.player import PlayerAnimation
from .events import CHANGE_DECORATION
from .groups import BLOCKS, DECORATION, UNIVERSUM
from .hitbox import Hitbox
from .settings import DISPLAY

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .animation.base_animation import BaseAnimation


class Player(SpriteWithDirection):
    def __init__(self, speed: int) -> None:
        super().__init__()

        self.speed = speed
        self.direction = pygame.Vector2()

        self.hitbox = Hitbox(self)
        self.player_animations = PlayerAnimation(self)

        self.image = next(self.player_animations.current_animation)
        self.rect = self.image.get_frect()

    def update(self, dt: float) -> None:
        self.direction.update(self.delta_move_vector)
        self.move(dt)

        self.player_animations.change_animation()
        self.image = next(self.player_animations.current_animation)

        self.hitbox.try_to_not_collide_with_blocks()

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
        super().__init__(BLOCKS)

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
            for sprite in UNIVERSUM.sprites():
                if sprite.rect and not (
                    self.rect.contains(sprite.rect)
                    or not self.rect.colliderect(sprite.rect)
                ):
                    break
            else:
                break

    def update(self, dt: float) -> None:
        super().update(dt)


class Decoration(BaseSprite):
    image: pygame.Surface
    rect: pygame.FRect

    def __init__(
        self, animation: BaseAnimation, *groups: pygame.sprite.AbstractGroup
    ) -> None:
        super().__init__(DECORATION, *groups)

        self.hitbox = Hitbox(self)
        self.animations = iter(animation)

        self.image = next(self.animations)
        self.rect = self.image.get_frect()

    def update(self, dt: float) -> None:  # noqa: ARG002
        keys = pygame.key.get_just_pressed()
        if keys[lc.K_l]:
            pygame.event.post(CHANGE_DECORATION)
        self.rect.center = pygame.mouse.get_pos()
        self.image = next(self.animations)


class Candle(Decoration):
    def __init__(self) -> None:
        super().__init__(CANDLE_ANIMATION)


class Candles(Decoration):
    def __init__(self) -> None:
        super().__init__(CANDLES_ANIMATION)


class Torch(Decoration):
    def __init__(self) -> None:
        super().__init__(TORCH_ANIMATION)
