from pygame.sprite import Group, LayeredUpdates, Sprite

UNIVERSUM: LayeredUpdates[Sprite] = LayeredUpdates()
BLOCKS: Group[Sprite] = Group()
DEBUG_POINTS: Group[Sprite] = Group()
DECORATION: Group[Sprite] = Group()
