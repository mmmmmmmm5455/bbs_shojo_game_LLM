"""Resolve paths relative to bbs-shojo-game/ (parent of src/), not cwd."""
import os
import shutil
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) and hasattr(sys, "_MEIPASS")


def _bundle_root() -> str:
    if is_frozen():
        return getattr(sys, "_MEIPASS")
    return os.path.normpath(os.path.join(_SRC_DIR, ".."))


def user_writable_root() -> str:
    """Directory for saves, logs, and mutable BBS JSON (next to .exe when frozen)."""
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.normpath(os.path.join(_SRC_DIR, ".."))


GAME_ROOT = _bundle_root()
ASSETS_DIR = os.path.join(GAME_ROOT, "assets")


def asset_path(*parts: str) -> str:
    """Paths inside the bundle (dev tree or PyInstaller extract)."""
    return os.path.join(GAME_ROOT, *parts)


def user_data_path(*parts: str) -> str:
    """Writable paths (savegame.json, offline_log.txt, …)."""
    root = user_writable_root()
    return os.path.join(root, *parts) if parts else root


def story_bbs_data_dir() -> str:
    """BBS JSON directory; frozen builds use a copy beside the exe."""
    dev_dir = os.path.join(_SRC_DIR, "story_mode", "bbs_data")
    if not is_frozen():
        return dev_dir
    user_dir = os.path.join(user_writable_root(), "bbs_shojo_data")
    os.makedirs(user_dir, exist_ok=True)
    bundled = os.path.join(_bundle_root(), "story_mode", "bbs_data")
    if os.path.isdir(bundled):
        for name in os.listdir(bundled):
            src = os.path.join(bundled, name)
            dst = os.path.join(user_dir, name)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
    return user_dir
