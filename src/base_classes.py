from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Final

import pygame
from pygame.sprite import LayeredDirty

from .settings import DISPLAY_SETTINGS, GAME_SETTINGS, display

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence


class Universum[T: BaseSprite](LayeredDirty[T]):
    camera: pygame.FRect = pygame.FRect((0, 0), DISPLAY_SETTINGS.SIZE)

    bg_color = "gray30"
    bgd = pygame.Surface(DISPLAY_SETTINGS.SIZE)
    bgd.fill(bg_color)

    def clear(
        self,
        surface: pygame.Surface | None = None,
        bgd: pygame.Surface | None = None,
    ) -> None:
        surface = surface or display
        if not bgd:
            bgd = pygame.Surface(DISPLAY_SETTINGS.SIZE)
            bgd.fill(self.bg_color)
        super().clear(surface, bgd)

    def draw(
        self,
        surface: pygame.Surface | None = None,
        bgd: pygame.Surface | None = None,
        special_flags: int | None = None,
    ) -> list[pygame.FRect | pygame.Rect]:
        surface = surface or display
        with self.using_camera():
            res = super().draw(surface, bgd, special_flags)
            if GAME_SETTINGS.DEBUG:
                self.draw_debug(surface)

            return res

    @contextmanager
    def using_camera(self) -> Generator:
        delta = pygame.Vector2(self.camera.topleft)
        if not delta:
            yield
            return

        temp_positions: list[tuple[float, float]] = []
        for sprite in self:
            temp_positions.append(sprite.rect.topleft)
            if not sprite.is_ui:
                sprite.rect.topleft -= delta
        try:
            yield
        finally:
            for sprite, temp_pos in zip(
                self.sprites(), temp_positions, strict=True
            ):
                sprite.rect.topleft = temp_pos

    def draw_debug(self, surface: pygame.Surface) -> None:
        for sprite in self:
            for rect, debug_color in sprite.debug_callback():
                if debug_color is not None:
                    pygame.draw.rect(surface, debug_color, rect, 5, 5)


class BaseSprite(ABC, pygame.sprite.DirtySprite):
    image: pygame.Surface
    rect: pygame.FRect

    universum: Final[Universum[BaseSprite]] = Universum()
    is_ui: bool = False
    _debug_color: str | None = None

    _layer: float = 0

    @abstractmethod
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(self.universum, *groups)
        self.dirty = 2

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @property
    def debug_color(self) -> str | None:
        return self._debug_color or self.__class__._debug_color  # ruff:ignore[private-member-access]

    @debug_color.setter
    def debug_color(self, value: str | None) -> None:
        self._debug_color = value

    def debug_callback(self) -> Sequence[tuple[pygame.FRect, str | None]]:
        return ((self.rect, self.debug_color),)


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
