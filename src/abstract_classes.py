from abc import ABC, abstractmethod
from typing import ClassVar

import pygame

from .groups import UNIVERSUM


class BaseSprite(ABC, pygame.sprite.Sprite):
    image: pygame.Surface
    rect: pygame.FRect

    _layer: ClassVar[float] = 0

    @abstractmethod
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(UNIVERSUM, *groups)

    @abstractmethod
    def update(self, dt: float) -> None:
        pass


class SpriteWithDirection(BaseSprite):
    direction: pygame.Vector2
