from pathlib import Path

from PIL import Image


# THX https://www.pythontutorials.net/blog/how-do-i-disable-the-libpng-warning-python-pygame/
def main() -> int:
    root = Path(__file__).parent

    for dirpath, _, filenames in Path("static").walk():
        for file in filter(
            lambda f: f.suffix.endswith("png"),
            (root / dirpath / f for f in filenames),
        ):
            with Image.open(file) as image:
                image.save(file, "PNG", icc_profile=None)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
