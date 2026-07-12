from itertools import pairwise, starmap
from operator import eq
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

import pygame

from .base_animation import BaseAnimation

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from os import PathLike

    from pygame.surface import Surface


class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...


class SupportsDunderLT[T](Protocol):
    def __lt__(self, other: T, /) -> SupportsBool: ...


class SupportsDunderGT[T](Protocol):
    def __gt__(self, other: T, /) -> SupportsBool: ...


type SupportsRichComparison = SupportsDunderLT[Any] | SupportsDunderGT[Any]


class DirectoryAnimation(BaseAnimation):
    def __init__(
        self,
        path_to_dir: str | PathLike[str],
        timeouts: int | Sequence[int],
        key: Callable[[Path], SupportsRichComparison] | None = None,
        size_equilizer: Callable[
            [pygame.Vector2, pygame.Surface], pygame.Surface
        ]
        | None = None,
        scale_factor: float = 1.0,
    ) -> None:
        key = key or self.default_key
        size_equilizer = size_equilizer or self.default_size_equilizer
        path_frames = sorted(Path(path_to_dir).iterdir(), key=key)

        maxsize = pygame.Vector2(-1, -1)
        surface_frames: list[Surface] = []
        for path in path_frames:
            surface_frames.append(
                surface := pygame.image.load(path).convert_alpha()
            )
            vec2_size = pygame.Vector2(surface.size)

            if vec2_size.x > maxsize.x or vec2_size.y > maxsize.y:
                maxsize = vec2_size

        if not all(starmap(eq, pairwise(surface_frames))):
            for i, surface in enumerate(surface_frames):
                surface_frames[i] = size_equilizer(maxsize, surface)

        super().__init__(surface_frames, maxsize, timeouts, scale_factor)

    @staticmethod
    def default_key(path: Path) -> int:
        return int(path.with_suffix("").name)

    @staticmethod
    def default_size_equilizer(
        maxsize: pygame.Vector2, surface: pygame.Surface
    ) -> pygame.Surface:
        new_surface = pygame.Surface(maxsize, pygame.SRCALPHA)
        new_surface.blit(surface, surface.get_frect(bottomleft=(0, maxsize.y)))
        return new_surface
