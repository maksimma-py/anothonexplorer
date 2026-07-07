from collections.abc import Sequence

import pygame
from environs import env

from .config import DEBUG, DISPLAY, FPS, GROUPS, display
from .sprites import Block, Player


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.window_setup_settings()
        self.sprites_setup()

        self.fps = FPS
        self.clock = pygame.Clock()
        self.ui = UI(self)

    @staticmethod
    def window_setup_settings() -> None:
        pygame.display.set_caption(DISPLAY.CAPTIONS)
        pygame.display.set_icon(
            pygame.image.load(DISPLAY.ICON_PATH).convert_alpha()
        )

    def sprites_setup(self) -> None:
        self.player = Player(250)

        for _ in range(20):
            Block("gray50")

    def start(self) -> None:
        self.running = True

        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.running:
                self.update_and_draw_sprites("gray30")
                self.ui.draw()

                pygame.display.flip()

        pygame.quit()

    def update_and_draw_sprites(
        self, bg_color: Sequence[int] | str | int
    ) -> None:
        display.fill(bg_color)
        GROUPS.UNIVERSUM.update(self.dt)
        GROUPS.UNIVERSUM.draw(display)


class UI:
    def __init__(self, game: Game) -> None:
        self.game = game

        with env.prefixed("DEBUG_FONT_"):
            self.debug_font = pygame.font.SysFont(
                env.str("NAME"), env.int("SIZE")
            )
            self.debug_font.align = pygame.FONT_RIGHT

    def draw(self) -> None:
        if DEBUG:
            debug_text = ""

            debug_text += f"Time: {pygame.time.get_ticks() / 1000:.2f}\n"
            debug_text += f"FPS: {self.game.clock.get_fps():.2f}\n"

            debug_text += f"Player direction: {self.game.player.tilemap_animations.current_str_direction}\n"
            debug_text += f"Player direction magnitude: {self.game.player.direction.magnitude():.2f}\n"

            text_surface = self.render_outlined(
                self.debug_font, debug_text, "white", "black", 5
            )
            text_rect = text_surface.get_frect(
                topright=(DISPLAY.SIZE.x - 20, 20)
            )
            display.blit(text_surface, text_rect)

    @staticmethod
    def render_outlined(
        font: pygame.Font,
        text: str,
        text_color: pygame.typing.ColorLike,
        outline_color: pygame.typing.ColorLike,
        outline_width: int,
    ) -> pygame.Surface:
        old_outline = font.outline
        if old_outline != 0:
            font.outline = 0
        base_text_surf = font.render(text, antialias=True, color=text_color)
        font.outline = outline_width
        outlined_text_surf = font.render(
            text, antialias=True, color=outline_color
        )

        outlined_text_surf.blit(base_text_surf, (outline_width, outline_width))
        font.outline = old_outline
        return outlined_text_surf
