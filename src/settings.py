from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import pygame
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pygame import Font

from .animation import TilemapAnimation
from .pydantic_adapters import Surface, Vector2

if TYPE_CHECKING:
    from collections.abc import Sequence

env_file_settings = {
    "extra": "ignore",
    "env_file": "game.env",
    "env_file_encoding": "utf-8",
}


class Game(BaseSettings):
    model_config = SettingsConfigDict(**env_file_settings)
    DEBUG: bool
    VSYNC: bool


GAME_SETTINGS = Game()


class DisplaySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DISPLAY_", **env_file_settings
    )

    SIZE: Vector2
    CAPTIONS: str
    ICON: Surface
    FPS: int


DISPLAY_SETTINGS = DisplaySettings()
try:
    display = pygame.display.set_mode(
        DISPLAY_SETTINGS.SIZE, vsync=GAME_SETTINGS.VSYNC
    )
except pygame.error:
    display = pygame.display.set_mode(DISPLAY_SETTINGS.SIZE)


class TilemapSettings(BaseSettings):
    TILEMAP: Surface
    TILESIZE: Vector2
    SCALE_FACTOR: float

    @model_validator(mode="before")
    @classmethod
    def check_model_config[T: dict](cls, data: T) -> T:
        if not vars(cls).get("model_config", None):
            msg = "model_config is missing"
            raise ValueError(msg)

        return data

    def animation(
        self, start: int, size: int, timeouts: Sequence[int] | int
    ) -> TilemapAnimation:
        return TilemapAnimation.indexes_as_range(
            self.TILEMAP,
            self.TILESIZE,
            range(start, start + size),
            timeouts=timeouts,
            factor=self.SCALE_FACTOR,
        )


class FontSettings(BaseSettings):
    filename: Path
    size: int
    font: Annotated[Font, Field(default_factory=Font, exclude=True)]

    @model_validator(mode="before")
    @classmethod
    def check_env_prefix[T: dict](cls, data: T) -> T:
        if not vars(cls).get("model_config", None):
            msg = "model_config is missing"
            raise ValueError(msg)

        return data

    @field_validator("filename", mode="after")
    @classmethod
    def extend_path(cls, value: Path) -> Path:
        return Path("static", "data", value)

    def model_post_init(self, context: object | None) -> None:  # ruff:ignore[unused-method-argument]
        self.font = Font(self.filename, self.size)
