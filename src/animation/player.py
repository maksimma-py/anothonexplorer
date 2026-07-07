from collections.abc import Callable, Generator, Iterator, Sequence
from contextlib import contextmanager
from functools import partial

import pygame
from environs import env

from src.abstract_classes import SpriteWithDirection
from src.config import Singleton

from .tilemap_animation import StrDirection, TilemapAnimation, TMADirections


@contextmanager
def temp_partial[**PS, R](
    f: Callable[..., R], *args: PS.args, **kwargs: PS.kwargs
) -> Generator[partial[R]]:
    yield partial(f, *args, **kwargs)


class PlayerAnimationDirections(Singleton):
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


PLAYER_ANIMATION_DIRECTIONS = PlayerAnimationDirections()


class PlayerAnimation:
    def __init__(self, player: SpriteWithDirection) -> None:
        self.player = player
        self.current_tma_directions: TMADirections = (
            PLAYER_ANIMATION_DIRECTIONS.IDLE
        )
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
            return PLAYER_ANIMATION_DIRECTIONS.RUN
        if self.player.direction.magnitude() > walk_threshold:
            return PLAYER_ANIMATION_DIRECTIONS.WALK
        return PLAYER_ANIMATION_DIRECTIONS.IDLE

    @property
    def current_animation(self) -> Iterator[pygame.Surface]:
        if self.do_change_animation:
            self.__current_animation = iter(
                getattr(
                    self.current_tma_directions, self.current_str_direction
                )
            )
        return self.__current_animation
