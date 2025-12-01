import sys
import os
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent

# Priority: SCREENSHOT_SAVE_DIR > PROJECT_ROOT/Codex/snips > SCRIPT_DIR/../snips
env_save_dir = os.getenv("SCREENSHOT_SAVE_DIR")
if env_save_dir:
    SNIPS_DIR = Path(env_save_dir).resolve()
else:
    project_root = os.getenv("PROJECT_ROOT")
    if project_root:
        SNIPS_DIR = Path(project_root).resolve() / "Codex" / "snips"
    else:
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
    force = "--force" in argv[1:]
    
    if all_files and not force:
        print("ERROR: --all requires --force flag to prevent accidental deletion", file=sys.stderr)
        print("Usage: cleanup_snips.py --all --force", file=sys.stderr)
        return 1
    
    if not SNIPS_DIR.is_dir():
        print(f"snips directory not found: {SNIPS_DIR}")
        return 0

    deleted = cleanup(all_files=all_files)
    print(f"deleted {deleted} file(s) under {SNIPS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
