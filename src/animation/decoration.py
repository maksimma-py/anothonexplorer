from pathlib import Path

from .directory_animation import DirectoryAnimation

CANDLE_ANIMATION = DirectoryAnimation(
    path_to_dir=Path("static/images/animations/candle"),
    timeouts=250,
    scale_factor=3,
)

CANDLES_ANIMATION = DirectoryAnimation(
    path_to_dir="static/images/animations/candles",
    timeouts=250,
    scale_factor=3,
)

TORCH_ANIMATION = DirectoryAnimation(
    path_to_dir="static/images/animations/torch",
    timeouts=250,
    scale_factor=3,
)
