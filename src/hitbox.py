from functools import partialmethod
from math import inf
from operator import attrgetter
from typing import TYPE_CHECKING

import pygame
from loguru import logger

from .abstract_classes import BaseSprite
from .groups import BLOCKS, DEBUG_POINTS
from .settings import GAME

if TYPE_CHECKING:
    from collections.abc import Callable


class DebugPoint(BaseSprite):
    image: pygame.Surface
    rect: pygame.FRect

    _layer: float = inf
    SIZE = 7

    def __init__(
        self, x: float, y: float, *groups: pygame.sprite.AbstractGroup
    ) -> None:
        super().__init__(DEBUG_POINTS, *groups)
        self.image = pygame.Surface(size=(self.SIZE, self.SIZE))
        self.image.fill("red")
        self.rect = self.image.get_frect(center=(x, y))
        self._layer = 1000

    def update(self, dt: float) -> None:
        super().update(dt)


class Hitbox:
    def __init__(self, sprite: BaseSprite, step: int = 10) -> None:
        self.sprite = sprite
        self.step = step

    def collides(
        self, group: pygame.sprite.AbstractGroup
    ) -> pygame.sprite.Sprite | None:
        return self.rect.collideobjects(
            group.sprites(), key=attrgetter("rect")
        )

    block_collides = partialmethod(collides, BLOCKS)

    def try_to_not_collide[**PS](
        self,
        collider: Callable[PS, pygame.sprite.Sprite | None],
        *args: PS.args,
        **kwargs: PS.kwargs,
    ) -> None:
        last_countervector: pygame.Vector2 | None = None

        while collided := collider(*args, **kwargs):
            x, y = self.sprite.rect.center
            if GAME.DEBUG:
                DebugPoint(x, y)
            last_countervector = self.get_collision_countervector(collided)
            self.sprite.rect.center += last_countervector

        if last_countervector is None:
            return

        last_countervector.normalize_ip()

        while not collider(*args, **kwargs):
            self.sprite.rect.center -= last_countervector
        self.sprite.rect.center += last_countervector

    def try_to_not_collide_with_blocks(self) -> None:
        self.try_to_not_collide(self.block_collides)

    def get_collision_countervector(
        self, collided: pygame.sprite.Sprite
    ) -> pygame.Vector2:
        if collided.rect is None:
            return pygame.Vector2()

        countervector = pygame.Vector2()

        points = [
            (point - pygame.Vector2(self.rect.center))
            for point in (
                self.rect.topleft,
                self.rect.midtop,
                self.rect.topright,
                self.rect.midright,
                self.rect.bottomright,
                self.rect.midbottom,
                self.rect.bottomleft,
                self.rect.midleft,
            )
            if collided.rect.collidepoint(point)
        ]

        if points:
            for point in points:
                point.x /= abs(point.x) or 1
                point.y /= abs(point.y) or 1
            logger.debug(f"COLLIDED ANGLES: {points}")

        countervector.x = (
            collided.rect.collidepoint(self.rect.topleft)
            + collided.rect.collidepoint(self.rect.bottomleft)
            + collided.rect.collidepoint(self.rect.midleft)
            - collided.rect.collidepoint(self.rect.topright)
            - collided.rect.collidepoint(self.rect.midright)
            - collided.rect.collidepoint(self.rect.bottomright)
        )

        countervector.y = (
            collided.rect.collidepoint(self.rect.topleft)
            + collided.rect.collidepoint(self.rect.midtop)
            + collided.rect.collidepoint(self.rect.topright)
            - collided.rect.collidepoint(self.rect.bottomright)
            - collided.rect.collidepoint(self.rect.midbottom)
            - collided.rect.collidepoint(self.rect.bottomleft)
        )

        comparing = pygame.Vector2(
            abs(countervector.x) > abs(countervector.y),
            abs(countervector.x) < abs(countervector.y),
        )

        if comparing:
            countervector = comparing.elementwise() * countervector
        logger.debug(f"{countervector = }")

        return countervector.normalize() * self.step

    @property
    def rel_rect(self) -> pygame.FRect:
        return pygame.FRect(self.sprite.image.get_bounding_rect())

    @property
    def rect(self) -> pygame.FRect:
        rel_rect = self.rel_rect
        rel_rect.center += pygame.Vector2(self.sprite.rect.topleft)
        return rel_rect
