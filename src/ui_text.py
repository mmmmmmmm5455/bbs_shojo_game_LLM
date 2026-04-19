"""Helpers for rendering long strings in pygame."""
from __future__ import annotations

from typing import List, Tuple

import pygame


def wrap_text_to_width(
    font: pygame.font.Font,
    text: str,
    max_width: int,
) -> List[str]:
    """Split text into lines that fit max_width when rendered with font."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: List[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        if " " in para and len(para.split()) > 1:
            words = para.split(" ")
            line = ""
            for w in words:
                trial = w if not line else f"{line} {w}"
                if font.size(trial)[0] <= max_width:
                    line = trial
                else:
                    if line:
                        lines.append(line)
                    if font.size(w)[0] <= max_width:
                        line = w
                    else:
                        chunk = ""
                        for ch in w:
                            t2 = chunk + ch
                            if font.size(t2)[0] <= max_width:
                                chunk = t2
                            else:
                                if chunk:
                                    lines.append(chunk)
                                chunk = ch
                        line = chunk
            if line:
                lines.append(line)
        else:
            chunk = ""
            for ch in para:
                t2 = chunk + ch
                if font.size(t2)[0] <= max_width:
                    chunk = t2
                else:
                    if chunk:
                        lines.append(chunk)
                    chunk = ch
            if chunk:
                lines.append(chunk)
    return lines


def blit_wrapped(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    center_x: int,
    start_y: int,
    line_gap: int = 4,
    max_width: int = 900,
) -> int:
    """Draw wrapped text centered horizontally; returns bottom y."""
    y = start_y
    for line in wrap_text_to_width(font, text, max_width):
        surf = font.render(line, True, color)
        x = center_x - surf.get_width() // 2
        screen.blit(surf, (x, y))
        y += surf.get_height() + line_gap
    return y
