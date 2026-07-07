import sys
from json import loads
from pathlib import Path
from types import SimpleNamespace
from typing import Self

import pygame
from environs import env
from loguru import logger

env.read_env("game.env")


def __vector2_parser(value: str) -> pygame.Vector2:
    return pygame.Vector2(loads(value))


env.add_parser("vector2", __vector2_parser)


def __surface_parser(value: str) -> pygame.Surface:
    return pygame.image.load(Path(value)).convert_alpha()


env.add_parser("surface", __surface_parser)


def init_logger() -> None:
    logger.remove()
    if DEBUG:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<level>[{level.name} at {time:HH:mm}]</level> {message}",
        )


class Singleton(SimpleNamespace):
    __instance: Self | None = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance


DEBUG: bool = env.bool("DEBUG")
FPS: int = env.int("FPS")


class Display(Singleton):
    with env.prefixed("DISPLAY_"):
        SIZE: pygame.Vector2 = env.vector2("SIZE")
        CAPTIONS: str = env.str("CAPTIONS")
        ICON_PATH: Path = env.path("ICON_PATH")


DISPLAY = Display()
display = pygame.display.set_mode(DISPLAY.SIZE)


class Groups(Singleton):
    UNIVERSUM: pygame.sprite.LayeredUpdates[pygame.sprite.Sprite] = (
        pygame.sprite.LayeredUpdates()
    )
    BLOCKS: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
    DEBUG_POINTS: pygame.sprite.Group[pygame.sprite.Sprite] = (
        pygame.sprite.Group()
    )


GROUPS = Groups()
