from abc import ABC, abstractmethod
from typing import Final

import pygame

from .groups import UNIVERSUM


class BaseSprite(ABC, pygame.sprite.DirtySprite):
    image: pygame.Surface
    rect: pygame.FRect

    _layer: float = 0

    @abstractmethod
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(UNIVERSUM, *groups)
        self.dirty = 2

    @abstractmethod
    def update(self, dt: float) -> None:
        pass


class SpriteWithDirection(BaseSprite):
    direction: pygame.Vector2


class SurfacelessSprite(BaseSprite):
    image: None = None
    rect: None = None
    visible: Final = False


class FontSprite(BaseSprite):
    font: pygame.Font

    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_frect()

    def update(self, dt: float) -> None:
        super().update(dt)

    @abstractmethod
    def render(self, text: str, **kwargs) -> None:  # ruff:ignore[missing-type-kwargs]
        self.image = self.font.render(text, antialias=True, color="red")
        self.rect = self.image.get_frect(**kwargs)
