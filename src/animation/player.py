from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.pydantic_adapters import Surface, Vector2
from src.settings import env_file_settings

from .tilemap_animation import StrDirection, TilemapAnimation, TMADirections

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator, Sequence

    import pygame

    from src.abstract_classes import SpriteWithDirection


class PlayerTMA(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLAYER_TMA_", **env_file_settings
    )

    TILEMAP: Surface
    TILESIZE: Vector2
    FACTOR: float


PLAYER_TMA = PlayerTMA()


@contextmanager
def temp_partial[**PS, R](
    f: Callable[..., R], *args: PS.args, **kwargs: PS.kwargs
) -> Generator[partial[R]]:
    yield partial(f, *args, **kwargs)


class PlayerAnimationDirections:
    @staticmethod
    def __player_tma_helper(
        start: int, size: int, timeouts: Sequence[int] | int
    ) -> TilemapAnimation:
        return TilemapAnimation.indexes_as_range(
            PLAYER_TMA.TILEMAP,
            PLAYER_TMA.TILESIZE,
            range(start, start + size),
            timeouts=timeouts,
            factor=PLAYER_TMA.FACTOR,
        )

    def __init__(self) -> None:
        with temp_partial(
            self.__player_tma_helper, size=2, timeouts=(1000, 500)
        ) as start:
            self.IDLE = TMADirections(
                down=start(0), left=start(2), right=start(4), up=start(6)
            )

        with temp_partial(
            self.__player_tma_helper, size=4, timeouts=200
        ) as start:
            self.WALK = TMADirections(
                down=start(8), left=start(12), right=start(16), up=start(20)
            )

        with temp_partial(
            self.__player_tma_helper, size=6, timeouts=133
        ) as start:
            self.RUN = TMADirections(
                down=start(24), left=start(30), right=start(36), up=start(42)
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
