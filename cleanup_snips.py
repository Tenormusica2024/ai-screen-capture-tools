import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SNIPS_DIR = SCRIPT_DIR.parent / "snips"


def cleanup(all_files: bool = False, older_than_minutes: int = 60) -> int:
    if not SNIPS_DIR.is_dir():
        return 0

    now = time.time()
    threshold = older_than_minutes * 60
    deleted = 0

    for path in SNIPS_DIR.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue

        if not all_files:
            mtime = path.stat().st_mtime
            if now - mtime < threshold:
                continue

        try:
            path.unlink()
            deleted += 1
        except OSError:
            pass

    return deleted


def main(argv: list[str]) -> int:
    all_files = "--all" in argv[1:]
    if not SNIPS_DIR.is_dir():
        print(f"snips directory not found: {SNIPS_DIR}")
        return 0

    deleted = cleanup(all_files=all_files)
    print(f"deleted {deleted} file(s) under {SNIPS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
