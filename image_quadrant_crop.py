import sys
import os
from pathlib import Path

from PIL import Image


def crop_quadrants(src_path: Path) -> list[Path]:
    img = Image.open(src_path)
    width, height = img.size

    mid_x = width // 2
    mid_y = height // 2

    regions = {
        "tl": (0, 0, mid_x, mid_y),
        "tr": (mid_x, 0, width, mid_y),
        "bl": (0, mid_y, mid_x, height),
        "br": (mid_x, mid_y, width, height),
    }

    dst_paths: list[Path] = []
    stem = src_path.stem
    suffix = src_path.suffix or ".png"

    for key, box in regions.items():
        cropped = img.crop(box)
        dst = src_path.with_name(f"{stem}_{key}{suffix}")
        cropped.save(dst)
        dst_paths.append(dst)

    return dst_paths


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: image_quadrant_crop.py <image_path> [--cleanup]", file=sys.stderr)
        return 1

    src = Path(argv[1])
    cleanup = "--cleanup" in argv[2:]

    if not src.is_file():
        print(f"ERROR: file not found -> {src}", file=sys.stderr)
        return 1

    try:
        dst_paths = crop_quadrants(src)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    for p in dst_paths:
        print(str(p))

    if cleanup:
        try:
            os.remove(src)
        except OSError as e:
            print(f"WARNING: failed to remove source: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
