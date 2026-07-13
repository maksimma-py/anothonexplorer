from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

import pygame

from src.abstract_classes import BaseSprite
from src.animation import DirectoryAnimation
from src.events import CHANGE_DECORATION
from src.groups import DECORATION
from src.hitbox import Hitbox

if TYPE_CHECKING:
    from os import PathLike

    from src.animation.base_animation import BaseAnimation


class Decoration(BaseSprite):
    image: pygame.Surface
    rect: pygame.FRect

    animation: ClassVar[BaseAnimation]
    decorations: ClassVar[dict[str, type[Self]]] = {}

    def __init_subclass__(cls, **kwargs) -> None:  # ruff:ignore[missing-type-kwargs]
        Decoration.decorations[cls.__name__] = cls

    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(DECORATION, *groups)

        self.hitbox = Hitbox(self)
        self.animations = iter(self.animation)

        self.image = next(self.animations)
        self.rect = self.image.get_frect()

    def update(self, dt: float) -> None:  # noqa: ARG002
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_l]:
            pygame.event.post(CHANGE_DECORATION)
        self.rect.center = pygame.mouse.get_pos()
        self.image = next(self.animations)


def _decoration_directiory_animation(
    directory: str | PathLike[str],
) -> DirectoryAnimation:
    return DirectoryAnimation(
        path_to_dir=Path("static/images/animations") / directory,
        timeouts=250,
        scale_factor=3,
    )


class Candle(Decoration):
    animation = _decoration_directiory_animation("candle")


class Candles(Decoration):
    animation = _decoration_directiory_animation("candles")


class Torch(Decoration):
    animation = _decoration_directiory_animation("torch")
