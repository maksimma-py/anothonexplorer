from collections.abc import Iterator, Sequence
from itertools import cycle, repeat

import pygame


class BaseAnimation:
    def __init__(
        self,
        frames: Sequence[pygame.Surface],
        frame_size: pygame.Vector2,
        timeouts: int | Sequence[int],
        scale_factor: float = 1.0,
    ) -> None:
        self.frames = frames
        self.frame_size = frame_size
        self.timeouts = timeouts
        self.scale_factor = scale_factor

    @property
    def timeouts(self) -> Iterator[int]:
        if isinstance(self._timeouts, int):
            return repeat(self._timeouts)
        if isinstance(self._timeouts, Sequence):
            return cycle(self._timeouts)
        msg = "Timeout is not an integer or a sequence of integers"
        raise TypeError(msg)

    @timeouts.setter
    def timeouts(self, value: int | Sequence[int]) -> None:
        self._timeouts = value

    @property
    def frames(self) -> Iterator[pygame.Surface]:
        return iter(self._frames)

    @frames.setter
    def frames(self, value: Sequence[pygame.Surface]) -> None:
        self._frames = value

    def __iter__(self) -> Iterator[pygame.Surface]:
        def inner() -> Iterator[pygame.Surface]:
            frames_timeouts = zip(
                cycle(self.frames), self.timeouts, strict=True
            )

            current_frame, current_timeout = next(frames_timeouts)
            last_ticks = pygame.time.get_ticks()
            while True:
                if pygame.time.get_ticks() - last_ticks >= current_timeout:
                    current_frame, current_timeout = next(frames_timeouts)
                    last_ticks = pygame.time.get_ticks()
                yield pygame.transform.scale_by(
                    current_frame, self.scale_factor
                )

        yield from inner()
