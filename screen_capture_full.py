import os
import sys
import datetime
from pathlib import Path
import ctypes
from ctypes import wintypes

from PIL import ImageGrab


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SAVE_DIR = SCRIPT_DIR.parent / "snips"
SAVE_DIR = Path(os.getenv("SCREENSHOT_SAVE_DIR", str(DEFAULT_SAVE_DIR)))
SAVE_DIR.mkdir(parents=True, exist_ok=True)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_ulong),
    ]


MONITORINFOF_PRIMARY = 0x00000001


def get_monitor_infos() -> list[tuple[str, tuple[int, int, int, int]]]:
    infos: list[tuple[RECT, int]] = []

    if os.name != "nt":
        return []

    user32 = ctypes.windll.user32

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def _callback(hMonitor, _hdc, _lprcMonitor, _lparam):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if user32.GetMonitorInfoW(hMonitor, ctypes.byref(info)):
            infos.append((info.rcMonitor, info.dwFlags))
        return 1

    cb_func = MonitorEnumProc(_callback)
    user32.EnumDisplayMonitors(0, None, cb_func, 0)

    if not infos:
        return []

    sorted_infos = sorted(
        infos,
        key=lambda item: 0 if (item[1] & MONITORINFOF_PRIMARY) else 1,
    )

    result: list[tuple[str, tuple[int, int, int, int]]] = []
    for idx, (rect, flags) in enumerate(sorted_infos):
        label = "main" if idx == 0 else f"sub{idx}"
        result.append((label, (rect.left, rect.top, rect.right, rect.bottom)))

    return result


def capture_fullscreen() -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screen_{ts}.png"
    path = SAVE_DIR / filename

    try:
        img = ImageGrab.grab(all_screens=True)
    except TypeError:
        img = ImageGrab.grab()

    img.save(path, "PNG")

    return path


def capture_fullscreen_split() -> list[Path]:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        img = ImageGrab.grab(all_screens=True)
    except TypeError:
        img = ImageGrab.grab()

    monitor_infos = get_monitor_infos()
    if not monitor_infos:
        width, height = img.size
        monitor_infos = [("main", (0, 0, width, height))]

    paths: list[Path] = []
    for label, (left, top, right, bottom) in monitor_infos:
        cropped = img.crop((left, top, right, bottom))
        path = SAVE_DIR / f"screen_{ts}_{label}.png"
        cropped.save(path, "PNG")
        paths.append(path)

    return paths


def capture_fullscreen_quadrants() -> list[Path]:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    paths: list[Path] = []

    monitor_infos = get_monitor_infos()
    if not monitor_infos:
        width, height = img.size
        monitor_infos = [("main", (0, 0, width, height))]

    main_img = None

    try:
        all_img = ImageGrab.grab(all_screens=True)
    except TypeError:
        all_img = ImageGrab.grab()

    for label, (left, top, right, bottom) in monitor_infos:
        if label == "main":
            if main_img is None:
                main_img = ImageGrab.grab()
            width, height = main_img.size
            mid_x = width // 2
            mid_y = height // 2

            regions = {
                "tl": (0, 0, mid_x, mid_y),
                "tr": (mid_x, 0, width, mid_y),
                "bl": (0, mid_y, mid_x, height),
                "br": (mid_x, mid_y, width, height),
            }

            for suffix, box in regions.items():
                cropped = main_img.crop(box)
                path = SAVE_DIR / f"screen_{ts}_{label}_{suffix}.png"
                cropped.save(path, "PNG")
                paths.append(path)
        else:
            mid_x = (left + right) // 2
            mid_y = (top + bottom) // 2

            regions = {
                "tl": (left, top, mid_x, mid_y),
                "tr": (mid_x, top, right, mid_y),
                "bl": (left, mid_y, mid_x, bottom),
                "br": (mid_x, mid_y, right, bottom),
            }

            for suffix, box in regions.items():
                cropped = all_img.crop(box)
                path = SAVE_DIR / f"screen_{ts}_{label}_{suffix}.png"
                cropped.save(path, "PNG")
                paths.append(path)

    return paths


def capture_monitor_region(label: str, region: str) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    monitor_infos = get_monitor_infos()
    if not monitor_infos:
        width, height = img.size
        monitor_infos = [("main", (0, 0, width, height))]

    rect = None
    for mon_label, (left, top, right, bottom) in monitor_infos:
        if mon_label == label:
            rect = (left, top, right, bottom)
            break

    if rect is None:
        raise ValueError(f"monitor label not found: {label}")

    left, top, right, bottom = rect

    if label == "main":
        img = ImageGrab.grab()
        width, height = img.size
        mid_x = width // 2
        mid_y = height // 2

        regions = {
            "tl": (0, 0, mid_x, mid_y),
            "tr": (mid_x, 0, width, mid_y),
            "bl": (0, mid_y, mid_x, height),
            "br": (mid_x, mid_y, width, height),
        }
    else:
        try:
            img = ImageGrab.grab(all_screens=True)
        except TypeError:
            img = ImageGrab.grab()

        mid_x = (left + right) // 2
        mid_y = (top + bottom) // 2

        regions = {
            "tl": (left, top, mid_x, mid_y),
            "tr": (mid_x, top, right, mid_y),
            "bl": (left, mid_y, mid_x, bottom),
            "br": (mid_x, mid_y, right, bottom),
        }

    if region not in regions:
        raise ValueError(f"unknown region: {region}")

    box = regions[region]
    cropped = img.crop(box)
    path = SAVE_DIR / f"screen_{ts}_{label}_{region}.png"
    cropped.save(path, "PNG")

    return path


def main() -> None:
    try:
        if len(sys.argv) >= 3 and not sys.argv[1].startswith("-"):
            label = sys.argv[1]
            region = sys.argv[2]
            path = capture_monitor_region(label, region)
            print(str(path))
            return

        if "--single" in sys.argv:
            path = capture_fullscreen()
            print(str(path))
            return

        if "--split" in sys.argv:
            paths = capture_fullscreen_split()
        else:
            paths = capture_fullscreen_quadrants()

        for p in paths:
            print(str(p))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
