from functools import partial
from typing import TYPE_CHECKING, ClassVar

import pygame
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from src.animation import Direction, DirectionalAnimation
from src.base_classes import SpriteWithDirection
from src.groups import DECORATION
from src.hitbox import Hitbox
from src.pydantic_adapters import Surface
from src.settings import TilemapSettings, env_file_settings

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class PlayerTilemap(TilemapSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLAYER_ANIMATION_TILEMAP_", **env_file_settings
    )

    TILEMAP: Surface = Field(alias="PLAYER_ANIMATION_TILEMAP")


PLAYER_TM = PlayerTilemap()


class PlayerDirectionalAnimations:
    _idle = partial(PLAYER_TM.animation, size=2, timeouts=(1000, 500))
    IDLE: ClassVar[DirectionalAnimation] = {
        Direction.DOWN: _idle(0),
        Direction.LEFT: _idle(2),
        Direction.RIGHT: _idle(4),
        Direction.UP: _idle(6),
    }

    _walk = partial(PLAYER_TM.animation, size=4, timeouts=200)
    WALK: ClassVar[DirectionalAnimation] = {
        Direction.DOWN: _walk(8),
        Direction.LEFT: _walk(12),
        Direction.RIGHT: _walk(16),
        Direction.UP: _walk(20),
    }

    _run = partial(PLAYER_TM.animation, size=6, timeouts=133)
    RUN: ClassVar[DirectionalAnimation] = {
        Direction.DOWN: _run(24),
        Direction.LEFT: _run(30),
        Direction.RIGHT: _run(36),
        Direction.UP: _run(42),
    }


PLAYER_DA = PlayerDirectionalAnimations()


class PlayerAnimation:
    def __init__(self, player: SpriteWithDirection) -> None:
        self.player = player
        self.current_da: DirectionalAnimation = PLAYER_DA.IDLE
        self.current_direction: Direction = Direction.DOWN

        self.do_change_animation = True
        self.__current_animation = self.current_animation

    def change_animation(self) -> None:
        self.do_change_animation = False

        da, direction = (
            self.next_directional_animation(),
            self.next_direction(),
        )

        if direction and direction != self.current_direction:
            self.current_direction = direction
            self.do_change_animation = True

        if da != self.current_da:
            self.current_da = da
            self.do_change_animation = True

    def next_direction(self) -> Direction | None:
        dir_x, dir_y = self.player.direction
        if dir_x > 0:
            return Direction.RIGHT
        if dir_x < 0:
            return Direction.LEFT
        if dir_y > 0:
            return Direction.DOWN
        if dir_y < 0:
            return Direction.UP
        return None

    def next_directional_animation(self) -> DirectionalAnimation:
        run_threshold = 1.2
        walk_threshold = 0.5
        direction_magnitude = self.player.direction.magnitude()

        return (
            PLAYER_DA.RUN
            if direction_magnitude > run_threshold
            else PLAYER_DA.WALK
            if direction_magnitude > walk_threshold
            else PLAYER_DA.IDLE
        )

    @property
    def current_animation(self) -> Iterator[pygame.Surface]:
        if self.do_change_animation:
            self.__current_animation = iter(
                self.current_da[self.current_direction]
            )
            self.do_change_animation = False
        return self.__current_animation


class Player(SpriteWithDirection):
    _debug_color = "red"

    def __init__(self, speed: int, **rect_kwargs) -> None:  # ruff:ignore[missing-type-kwargs]
        super().__init__()

        self.speed = speed
        self.direction = pygame.Vector2()

        self.hitbox = Hitbox(self)
        self.player_animations = PlayerAnimation(self)

        self.image = next(self.player_animations.current_animation)
        self.rect = self.image.get_frect(**rect_kwargs)

        self.universum.camera.center = self.rect.center

    def update(self, dt: float) -> None:
        self.direction.update(self.delta_move_vector)
        self.move(dt)

        self.player_animations.change_animation()
        self.image = next(self.player_animations.current_animation)

        self.hitbox.try_to_not_collide_with_blocks()
        self.lerp_camera_to_his_pos(dt)

    def debug_callback(self) -> Sequence[tuple[pygame.FRect, str | None]]:
        hitbox_color = (
            "purple" if self.hitbox.collides(DECORATION) else "green"
        )
        return (
            (self.rect, self.debug_color),
            (self.hitbox.rect, hitbox_color),
        )

    @property
    def delta_move_vector(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        delta = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s])
            - (keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        delta = delta and delta.normalize()

        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_SHIFT:
            delta *= 1.5

        return delta

    def move(self, dt: float) -> None:
        self.rect.x += self.direction.x * self.speed * dt
        if self.hitbox.block_collides():
            self.rect.x -= self.direction.x * self.speed * dt

        self.rect.y += self.direction.y * self.speed * dt
        if self.hitbox.block_collides():
            self.rect.y -= self.direction.y * self.speed * dt

    def lerp_camera_to_his_pos(self, dt: float) -> None:
        self.universum.camera.center = pygame.Vector2(
            self.universum.camera.center
        ).lerp(self.rect.center, pygame.math.clamp(dt * 10, 0, 1))
