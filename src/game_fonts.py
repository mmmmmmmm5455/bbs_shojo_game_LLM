"""UI fonts with CJK coverage (fixes tofu boxes on Windows/Linux/macOS)."""
from __future__ import annotations

import os
import sys
from typing import Dict

import pygame

_CACHE: Dict[int, pygame.font.Font] = {}


def _font_file_candidates() -> list[str]:
    paths: list[str] = []
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        fonts = os.path.join(windir, "Fonts")
        paths.extend(
            [
                os.path.join(fonts, "msyh.ttc"),
                os.path.join(fonts, "msyhbd.ttc"),
                os.path.join(fonts, "simhei.ttf"),
                os.path.join(fonts, "simsun.ttc"),
                os.path.join(fonts, "msjhl.ttc"),
            ]
        )
    paths.extend(
        [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
    )
    return paths


def get_ui_font(size: int) -> pygame.font.Font:
    if size in _CACHE:
        return _CACHE[size]

    for path in _font_file_candidates():
        if path and os.path.isfile(path):
            try:
                font = pygame.font.Font(path, size)
                _CACHE[size] = font
                return font
            except OSError:
                continue

    for name in (
        "microsoftyahei",
        "microsoft yahei",
        "simhei",
        "simsun",
        "nsimsun",
        "notosanscjksc",
        "pingfang sc",
        "heiti sc",
        "stheitisc",
    ):
        try:
            font = pygame.font.SysFont(name, size)
            if font:
                _CACHE[size] = font
                return font
        except OSError:
            continue

    fallback = pygame.font.Font(None, size)
    _CACHE[size] = fallback
    return fallback
