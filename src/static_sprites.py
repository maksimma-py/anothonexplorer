from random import randint
from typing import TYPE_CHECKING

import pygame

from .abstract_classes import BaseSprite
from .groups import BLOCKS, UNIVERSUM
from .settings import DISPLAY_SETTINGS

if TYPE_CHECKING:
    from collections.abc import Sequence


class Block(BaseSprite):
    SIZE = pygame.Vector2(100, 100)

    def __init__(self, color: Sequence[int] | str | int) -> None:
        super().__init__(BLOCKS)

        self.image = pygame.Surface(self.SIZE)
        self.image.fill(color)

        self.rect = self.image.get_frect()
        ceil = (
            DISPLAY_SETTINGS.SIZE - self.rect.size
        ).elementwise() / self.SIZE

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
