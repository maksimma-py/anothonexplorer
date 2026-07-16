from typing import TYPE_CHECKING

from pygame.sprite import Group

if TYPE_CHECKING:
    from .base_classes import BaseSprite

BLOCKS: Group[BaseSprite] = Group()
DEBUG_POINTS: Group[BaseSprite] = Group()
DECORATION: Group[BaseSprite] = Group()
