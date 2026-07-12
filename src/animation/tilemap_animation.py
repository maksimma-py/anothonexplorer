from dataclasses import dataclass
from math import prod
from typing import TYPE_CHECKING, Literal, Self

import pygame

from .base_animation import BaseAnimation

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class TilemapAnimation(BaseAnimation):
    def __init__(
        self,
        tile_map: pygame.Surface,
        tile_size: pygame.Vector2,
        frames_indexes: Sequence[pygame.Vector2],
        timeouts: int | Sequence[int],
        scale_factor: float = 1.0,
    ) -> None:
        self.tile_map = tile_map
        self.tile_size = tile_size
        self._frames_indexes = frames_indexes

        self.timeouts = timeouts
        self.scale_factor = scale_factor

    @classmethod
    def indexes_as_range(
        cls,
        tile_map: pygame.Surface,
        tile_size: pygame.Vector2,
        index_range: range | Sequence[int],
        timeouts: int | Sequence[int],
        factor: float = 1.0,
    ) -> Self:
        tile_map_size = (
            pygame.Vector2(tile_map.size) // tile_size.elementwise()
        )
        last_index = int(prod(tile_map_size)) - 1

        frames_indexes: list[pygame.Vector2] = []
        for frame_index in (
            pygame.math.clamp(i, 0, last_index) for i in index_range
        ):
            y, x = divmod(frame_index, tile_map_size.x)
            frames_indexes.append(pygame.Vector2(x, y))
        return cls(tile_map, tile_size, frames_indexes, timeouts, factor)

    @property
    def frames(self) -> Iterator[pygame.Surface]:
        for i in self._frames_indexes:
            yield self.tile_map.subsurface((
                self.tile_size.elementwise() * i,
                self.tile_size,
            ))

    @frames.setter
    def frames(self, value: Sequence[pygame.Vector2]) -> None:
        self._frames_indexes = value


type StrDirection = Literal["down", "left", "right", "up"]


@dataclass
class TMADirections:
    down: TilemapAnimation
    up: TilemapAnimation
    left: TilemapAnimation
    right: TilemapAnimation
