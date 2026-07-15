from math import inf

import pygame
from pydantic_settings import SettingsConfigDict
from pygame import font

from .abstract_classes import FontSprite
from .settings import DISPLAY_SETTINGS, FontSettings, env_file_settings

if not font.get_init():
    font.init()


class DebugFont(FontSprite):
    class DebugFontSettings(FontSettings):
        model_config = SettingsConfigDict(
            env_prefix="DEBUG_FONT_", **env_file_settings
        )

    font = DebugFontSettings().font
    font.align = pygame.FONT_RIGHT

    _layer = inf

    def render(self, text: str | dict[str, str], **_kwargs) -> None:  # ruff:ignore[missing-type-kwargs]
        if isinstance(text, dict):
            text = "\n".join(f"{k}: {v}" for k, v in text.items())
        super().render(
            text, bottomright=(DISPLAY_SETTINGS.SIZE.elementwise() - 20)
        )
