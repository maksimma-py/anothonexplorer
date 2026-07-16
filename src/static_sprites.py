from operator import attrgetter
from random import randint

import pygame

from .base_classes import BaseSprite
from .groups import BLOCKS
from .settings import DISPLAY_SETTINGS


class Block(BaseSprite):
    SIZE = pygame.Vector2(100, 100)

    def __init__(self) -> None:
        super().__init__(BLOCKS)

        self.image = pygame.Surface(self.SIZE)
        self.color = pygame.Color.from_hsva(randint(0, 360), 75, 100, 100)
        self.image.fill(self.color)

        self.rect = self.image.get_frect()

        self.random_noncolliding_place()
        self.propagate_color()

    def random_noncolliding_place(self) -> None:
        while True:
            self.rect.center = (
                pygame.Vector2(
                    randint(-20, 20),
                    randint(-20, 20),
                ).elementwise()
                * self.SIZE
                + DISPLAY_SETTINGS.SIZE / 2
            )
            for sprite in self.universum.sprites():
                if (
                    self.rect.colliderect(sprite.rect)
                    and sprite is not self
                    and not sprite.is_ui
                ):
                    break
            else:
                break

    def propagate_color(self) -> None:
        for block_object in self.rect.scale_by(1.1).collideobjectsall(
            BLOCKS.sprites(), key=attrgetter("rect")
        ):
            if (
                not isinstance(block_object, Block)
                or block_object.color == self.color
            ):
                continue

            block_object.color = self.color
            block_object.image.fill(self.color)
            block_object.propagate_color()

    def update(self, dt: float) -> None:
        super().update(dt)
