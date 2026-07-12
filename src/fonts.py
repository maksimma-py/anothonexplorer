from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pygame import Font
from pygame.font import init as init_font

from .settings import env_file_settings

init_font()


class SettingsFont(BaseSettings):
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


class DebugFont(SettingsFont):
    model_config = SettingsConfigDict(
        env_prefix="DEBUG_FONT_", **env_file_settings
    )


DEBUG_FONT = DebugFont().font
