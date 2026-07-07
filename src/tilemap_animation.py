from collections.abc import Callable, Generator, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from itertools import cycle, repeat
from math import prod
from typing import Literal, Self

import pygame
from environs import env

from .abstract_classes import SpriteWithDirection
from .config import Singleton


class TilemapAnimation:
    def __init__(
        self,
        tile_map: pygame.Surface,
        tile_size: pygame.Vector2,
        frames_indexes: Sequence[pygame.Vector2],
        timeouts: int | Sequence[int],
        factor: float = 1.0,
    ) -> None:
        self.tile_map = tile_map
        self.tile_size = tile_size
        self._frames_indexes = frames_indexes
        self.timeouts = timeouts
        self.factor = factor

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
    def timeouts(self) -> Iterator[int]:
        if isinstance(self._timeouts, int):
            return repeat(self._timeouts)
        if isinstance(self._timeouts, Sequence):
            return cycle(self._timeouts)
        msg = "Timeout is not an integer or a sequence of integers"
        raise TypeError(msg)

    @timeouts.setter
    def timeouts(self, value: int | Sequence[int]) -> None:
        self._timeouts = value

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

    def __iter__(self) -> Iterator[pygame.Surface]:
        def inner() -> Iterator[pygame.Surface]:
            frames_timeouts = zip(
                cycle(self.frames), self.timeouts, strict=True
            )

            current_frame, current_timeout = next(frames_timeouts)
            last_ticks = pygame.time.get_ticks()
            while True:
                if pygame.time.get_ticks() - last_ticks >= current_timeout:
                    current_frame, current_timeout = next(frames_timeouts)
                    last_ticks = pygame.time.get_ticks()
                yield pygame.transform.scale_by(current_frame, self.factor)

        yield from inner()


type StrDirection = Literal["down", "left", "right", "up"]


@dataclass
class TMADirections:
    down: TilemapAnimation
    up: TilemapAnimation
    left: TilemapAnimation
    right: TilemapAnimation


@contextmanager
def temp_partial[**PS, R](
    f: Callable[..., R], *args: PS.args, **kwargs: PS.kwargs
) -> Generator[partial[R]]:
    yield partial(f, *args, **kwargs)


class PlayerTMADirections(Singleton):
    def __player_tma_helper(
        self, start: int, size: int, timeouts: Sequence[int] | int
    ) -> TilemapAnimation:
        return TilemapAnimation.indexes_as_range(
            self.TILEMAP,
            self.TILESIZE,
            range(start, start + size),
            timeouts=timeouts,
            factor=self.FACTOR,
        )

    def __init__(self) -> None:
        with env.prefixed("PLAYER_TMA_"):
            self.TILEMAP: pygame.Surface = env.surface("TILEMAP")
            self.TILESIZE: pygame.Vector2 = env.vector2("TILESIZE")
            self.FACTOR = env.vector2("FACTOR")

        with temp_partial(
            self.__player_tma_helper,
            size=2,
            timeouts=(1000, 500),
        ) as idle_tma:
            self.IDLE = TMADirections(
                down=idle_tma(start=0),
                left=idle_tma(start=2),
                right=idle_tma(start=4),
                up=idle_tma(start=6),
            )

        with temp_partial(
            self.__player_tma_helper,
            size=4,
            timeouts=200,
        ) as walk_tma:
            self.WALK = TMADirections(
                down=walk_tma(start=8),
                left=walk_tma(start=12),
                right=walk_tma(start=16),
                up=walk_tma(start=20),
            )

        with temp_partial(
            self.__player_tma_helper,
            size=6,
            timeouts=133,
        ) as run_tma:
            self.RUN = TMADirections(
                down=run_tma(start=24),
                left=run_tma(30),
                right=run_tma(36),
                up=run_tma(42),
            )


PLAYER_TMA_DIRECTIONS = PlayerTMADirections()


class PlayerTMAnimation:
    def __init__(self, player: SpriteWithDirection) -> None:
        self.player = player
        self.current_tma_directions: TMADirections = PLAYER_TMA_DIRECTIONS.IDLE
        self.current_str_direction: StrDirection = "down"

        self.do_change_animation = True
        self.__current_animation = self.current_animation

    def change_animation(self) -> None:
        self.do_change_animation = False

        tma, str_direction = (
            self.next_tma_directions(),
            self.next_str_direction(),
        )

        if str_direction and str_direction != self.current_str_direction:
            self.current_str_direction = str_direction
            self.do_change_animation = True

        if tma != self.current_tma_directions:
            self.current_tma_directions = tma
            self.do_change_animation = True

    def next_str_direction(self) -> StrDirection | None:
        if self.player.direction.x > 0:
            return "right"
        if self.player.direction.x < 0:
            return "left"
        if self.player.direction.y > 0:
            return "down"
        if self.player.direction.y < 0:
            return "up"
        return None

    def next_tma_directions(self) -> TMADirections:
        run_threshold = 1.2
        walk_threshold = 0.5

        if self.player.direction.magnitude() > run_threshold:
            return PLAYER_TMA_DIRECTIONS.RUN
        if self.player.direction.magnitude() > walk_threshold:
            return PLAYER_TMA_DIRECTIONS.WALK
        return PLAYER_TMA_DIRECTIONS.IDLE

    @property
    def current_animation(self) -> Iterator[pygame.Surface]:
        if self.do_change_animation:
            self.__current_animation = iter(
                getattr(
                    self.current_tma_directions, self.current_str_direction
                )
            )
        return self.__current_animation
