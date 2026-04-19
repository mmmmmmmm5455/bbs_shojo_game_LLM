# BBS Shojo — Bug Evaluation Report

**Scope:** `bbs-shojo-game/src` (primary entry `main_advanced_v2.py`), supporting modules.  
**Date:** 2026-04-08  

---

## Critical (crash or data loss)

| ID | Area | Description |
|----|------|-------------|
| C1 | `forum_npc.py` | `_generate_support_post` references `base_mood`, which is never defined. Triggering a supporter-style post raises **NameError** and can break NPC updates. |
| C2 | `main_advanced_v2.py` | `_save_game` passes `forum_posts` entries containing a live **`ForumNPC` object** (`"npc": npc`). **`json.dump` raises TypeError** when saving. |
| C3 | `typing_challenge.py` | `update_input` uses `return self._complete_challenge(), ""`, producing a **nested tuple** `((bool, str), str)` instead of `(bool, str)`. Any code that unpacks the return value would misbehave. |

---

## High (incorrect behavior / display)

| ID | Area | Description |
|----|------|-------------|
| H1 | `main_advanced_v2.py` | After load from JSON, posts lack `"npc"` objects; **`_draw_forum` assumes `post["npc"].personality`** and would **crash** if forum was ever saved/loaded with fixed serialization. |
| H2 | `crt_manager.py` | Geometric distortion block sets `offset` inside `for y`, but **blits once using only the last row’s offset**, so the effect does not match the intended per-row variation. |
| H3 | `typing_challenge.py` | **WPM** uses `split()` word count; **Chinese-dominant strings** yield ~1 “word”, so scores are misleading vs English-heavy text. |

---

## Medium (UX, consistency, polish)

| ID | Area | Description |
|----|------|-------------|
| M1 | `main_advanced_v2.py` | CRT pass runs on **background only**; HUD and character are drawn afterward **without** CRT. Intentional for readability but inconsistent with “full screen CRT” expectation. |
| M2 | `advanced_animated_character.py` | `add_emotion_sound` still uses **cwd-relative** `assets/sounds/...`, inconsistent with `ASSETS_DIR` used elsewhere. |
| M3 | `main_advanced_v2.py` | Long typing **feedback** string may exceed screen width; single-line `render` **clips** visually. |
| M4 | `time_system.py` | Multiple checks (e.g. late night + weekend) compete; **only the first matching handler** in dict order fires per cycle (acceptable but worth documenting). |

---

## Previously addressed (retained for audit trail)

- CRT `color_bias` tuple vs float interpolation (**TypeError**) — fixed in `crt_manager.get_current_params`.  
- Default font **CJK “tofu”** boxes — `game_fonts.get_ui_font` + replacements.  
- `TimeSystem` 60s cooldown using `last_check_time` overwritten each frame — fixed with `_event_triggered_at`.  
- **ESC** during typing/forum vs quit — fixed in `_handle_key_press`.  
- Resource paths / missing sound spam — `game_paths.ASSETS_DIR` + skip missing files.  
- `ascii_animation_system` import stdout **UnicodeEncodeError** on some Windows code pages — ASCII stderr message.  
- `pixel_gradient_system` missing **`import random`** for jitter path.  

---

## Recommendations (not all implemented)

- Add automated **smoke tests** (import + `json` round-trip save payload).  
- Optional: wrap long UI strings to multiple surfaces for forum/typing feedback.  
- Ship minimal **placeholder WAV** or document optional assets under `assets/sounds/`.  

---

## Resolution status

| ID | Status |
|----|--------|
| C1 | **Fixed** — `_generate_support_post` defines `base_mood` via mood table. |
| C2 | **Fixed** — Forum posts store only JSON-serializable fields; save builds explicit dicts. |
| C3 | **Fixed** — `update_input` returns `self._complete_challenge()` directly. |
| H1 | **Fixed** — `npc_color` on posts + `_post_display_color` / `_normalize_forum_posts` for load. |
| H2 | **Fixed** — CRT distortion uses a single `pan_offset` from mid-row. |
| H3 | **Fixed** — WPM uses `max(word_count, char_units/5)`. |
| M2 | **Fixed** — `add_emotion_sound` uses `ASSETS_DIR` and skips missing files. |
| M3 | **Fixed** — `ui_text.blit_wrapped` for typing result feedback. |
| M1 | **Fixed** — `_apply_display_postprocess()` runs **after** character, UI, typing, forum, pause; CRT then VH on full framebuffer (`main_advanced_v2.py`, `main_advanced.py`). |
| M4 | **Documented only** (time-event priority order unchanged). |

**Smoke checks:** `ForumNPC.generate_post` (support), `TypingChallenge.update_input` return shape, `json.dumps` on save-shaped forum payload, `_normalize_forum_posts` default color.

---

## 2026-04-08 Additional QA Pass

### New findings from play-style QA

| ID | Area | Description | Severity |
|----|------|-------------|----------|
| N1 | `main_advanced_v2.py` | Pressing `H` did not show in-game tutorial; help only printed to terminal, so players in fullscreen/window focus couldn't see it. | High |
| N2 | `main_advanced_v2.py` | Character frame rendering treated multiline text as one line; some text/ascii looked broken or clipped. | High |
| N3 | `main_advanced_v2.py` | Forum content lacked width wrapping and could overflow screen area. | Medium |
| N4 | `main_advanced_v2.py` | Console logs with emoji (`✅`, `📝`, `📋`) could raise `UnicodeEncodeError` under some Windows code pages during save/load flows. | Critical |
| N5 | `typing_challenge.py`, `time_system.py` | Strings with emoji/box-drawing symbols reduced readability on limited glyph fonts. | Medium |

### Fixes applied

- **N1 fixed:** Added `help_overlay_active` and `_draw_help_overlay()`; `H` now toggles in-game help, `ESC` closes it first.
- **N2 fixed:** `_draw_character()` now renders line-by-line for multiline frames.
- **N3 fixed:** `_draw_forum()` now wraps lines with `wrap_text_to_width()` and bounds rendering to visible area.
- **N4 fixed:** Added `_log()` safe console output in `main_advanced_v2.py` and `main_advanced.py`; replaced emoji log markers with plain text.
- **N5 fixed:** Replaced high-risk glyphs in challenge/time messages with plain text alternatives.

### Verification (this pass)

- Help overlay toggle: `H` open/close, `ESC` close behavior checked.
- Render safety: multiline character and long forum post draw paths executed without exception.
- Persistence path: save/load round-trip completed after fixes.
- Environment: Windows + Pygame dummy drivers smoke run succeeded (no unhandled exceptions).
