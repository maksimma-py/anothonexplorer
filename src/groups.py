import pygame
from pygame.sprite import DirtySprite, Group, LayeredDirty, Sprite

from .settings import DISPLAY_SETTINGS, display


class Universum[T: DirtySprite](LayeredDirty[T]):
    bg_color = "gray30"

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


UNIVERSUM: Universum[DirtySprite] = Universum()
BLOCKS: Group[Sprite] = Group()
DEBUG_POINTS: Group[Sprite] = Group()
DECORATION: Group[Sprite] = Group()
