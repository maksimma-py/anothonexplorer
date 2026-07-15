from itertools import cycle
from typing import Self

import pygame

from .animated_sprites import Decoration, Player
from .events import CHANGE_DECORATION
from .fonts import DebugFont
from .groups import DECORATION, UNIVERSUM
from .settings import DISPLAY_SETTINGS, GAME_SETTINGS, display
from .static_sprites import Block


class Game:
    __instance: Self | None = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        pygame.init()
        self.window_setup_settings()
        self.sprites_setup()

        self.fps = DISPLAY_SETTINGS.FPS
        self.clock = pygame.Clock()
        self.ui = UI(self)

    @staticmethod
    def window_setup_settings() -> None:
        pygame.display.set_caption(DISPLAY_SETTINGS.CAPTIONS)
        pygame.display.set_icon(DISPLAY_SETTINGS.ICON)

    def sprites_setup(self) -> None:
        self.player = Player(250)

        for _ in range(20):
            Block("gray50")

        self.decorations = cycle(Decoration.decorations.values())
        self.current_decoration = next(self.decorations)()

    def start(self) -> None:
        self.running = True

        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False
                    case CHANGE_DECORATION.type:
                        self.current_decoration.kill()
                        self.current_decoration = next(self.decorations)()

            if self.running:
                self.update_and_draw_sprites()
                self.ui.draw()
                pygame.display.update(self.draw_rects)

        pygame.quit()

    def update_and_draw_sprites(self) -> None:
        UNIVERSUM.update(self.dt)
        UNIVERSUM.clear()
        self.draw_rects = UNIVERSUM.draw(display)


class UI:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.debug_font = DebugFont()

    def draw(self) -> None:
        if GAME_SETTINGS.DEBUG:
            self.draw_hitboxes()
            self.draw_debug_text()

    def draw_hitboxes(self) -> None:
        hitbox_color = (
            "purple"
            if self.game.player.hitbox.collides(DECORATION)
            else "green"
        )

        pygame.draw.rect(
            display, hitbox_color, self.game.player.hitbox.rect, width=7
        )

        pygame.draw.rect(display, "red", self.game.player.rect, width=7)

        pygame.draw.rect(
            display,
            "blue",
            self.game.current_decoration.hitbox.rect,
            width=7,
        )

    def draw_debug_text(self) -> None:
        self.debug_text = {
            "Time": f"{pygame.time.get_ticks() / 1000:.2f}",
            "FPS": f"{self.game.clock.get_fps():.2f}",
            "Player direction": f"{self.game.player.player_animations.current_direction.value}",
            "Player direction magnitude": f"{self.game.player.direction.magnitude():.2f}",
            "Current decoration": f"{self.game.current_decoration.__class__.__name__.lower()!r}",
        }

        self.debug_font.render(self.debug_text)
