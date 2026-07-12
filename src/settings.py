import pygame
from pydantic_settings import BaseSettings, SettingsConfigDict

from .pydantic_adapters import Surface, Vector2

env_file_settings = {
    "extra": "ignore",
    "env_file": "game.env",
    "env_file_encoding": "utf-8",
}


class Game(BaseSettings):
    model_config = SettingsConfigDict(**env_file_settings)
    DEBUG: bool


GAME = Game()


class Display(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DISPLAY_", **env_file_settings
    )

    SIZE: Vector2
    CAPTIONS: str
    ICON: Surface
    FPS: int


DISPLAY = Display()
display = pygame.display.set_mode(DISPLAY.SIZE)
