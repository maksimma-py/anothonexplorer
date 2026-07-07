from loguru import logger

from src.config import init_logger


@logger.catch()
def main() -> None:
    from src.game import Game  # noqa: PLC0415

    init_logger()
    Game().start()


if __name__ == "__main__":
    main()
