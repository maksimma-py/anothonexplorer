from pydantic_settings import SettingsConfigDict
from pygame.font import init as init_font

from .settings import FontSettings, env_file_settings

init_font()


class DebugFont(FontSettings):
    model_config = SettingsConfigDict(
        env_prefix="DEBUG_FONT_", **env_file_settings
    )


DEBUG_FONT = DebugFont().font
