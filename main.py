import sys

from loguru import logger

from src.settings import GAME


def init_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if GAME.DEBUG else "INFO",
        format="<level>[{level.name} at {time:HH:mm}]</level> {message}",
    )


@logger.catch()
def main() -> None:
    from src.game import Game  # ruff:ignore[import-outside-top-level]

    init_logger()
    Game().start()


if __name__ == "__main__":
    main()
