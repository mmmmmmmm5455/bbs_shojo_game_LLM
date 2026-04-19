# DeepSeek 项目交接说明（可复制）

## 1. 你怎么用

1. 打开 **第二节「粘贴给 DeepSeek」** 的全文，复制到你的 DeepSeek 对话（建议作为首条用户消息，或放在自定义说明里）。
2. 在复制内容**末尾**加上你自己的约束（语言、是否必须离线、基调等）——可用 **第三节模板** 填空。
3. 需要更深讨论时，把 **第四节附录** 里对应片段一并贴给 DeepSeek。

（本文件与 Cursor 内的 `deepseek_project_handoff` 计划内容一致；**请勿**编辑 `.cursor/plans` 下的 plan 文件。）

---

## 2. 粘贴给 DeepSeek（English block — copy below this line）

**Project:** BBS Shojo (千禧年打字物语) — a retro BBS / Y2K–nostalgia visual-novel style game in **Python + Pygame**, plus a separate **terminal Webcore mode**.

**Creative pillars:** memory fragments as progression metaphor; ASCII art + pixel portrait “clarity”; CRT scanlines / aging; philosophical tangents (Turing test, Ship of Theseus, simulacra / digital identity); early-internet “ghost” atmosphere (dead links, guestbook, webring).

**Two playable surfaces:**

1. **Graphical main game** — entry: `src/main_advanced_v2.py` (from repo root: `cd src` then `python main_advanced_v2.py`).
   - Chat-style UI at bottom: free text to talk to the girl (“小误”); slash commands for meta systems.
   - Core loops: `story_mode/bbs_engine.py` (posts, webcore commands, persistence under `bbs_data`), `story_mode/girl_conversation.py` (short-term dialogue memory + intent-ish replies), `story_mode/girl_state.py` (mood, keyword pools, OS flavor tags).
   - Systems already wired in main: pixel gradient preview + CRT tied to `memory_fragments`, ASCII character, typing challenge (`K`), forum (`F`), save/load (`S`/`L`), BGM (`G` / `/bgm`), `/midi` easter egg, vertical hold (`V`/`R`, rare random VH gated so it **does not** fire during typing challenge; time popups also suppressed during typing).
   - Paths / frozen exe: `src/game_paths.py` (`user_data_path`, `story_bbs_data_dir`, PyInstaller bundle vs writable dir).

2. **Terminal BBS mode** — `src/main_bbs_terminal.py`: command-line Web 1.0 fiction (404 pages, webring, guestbook, dead link codex, etc.). Can be spawned from the graphical game with `B` when **not** frozen-packaged.

**Docs in repo (paste excerpts as needed):**

- `README.md` — feature list and how to run.
- `game-design-document.md` — original GDD (some “待实现” items are now partially implemented in `main_advanced_v2`; checklist link inside).
- `docs/GDD_IMPLEMENTATION_CHECKLIST.md` — manual QA matrix.
- `docs/plans/2026-04-18-settings-and-features-outlook.md` — **planned gap**: almost no in-game **settings** UI yet; backlog for audio sliders, CRT/VH caps, autosave, chat persistence, localization, etc.

**Recent engineering reality (so ideas stay feasible):**

- Dialogue is **rules + templates**, not an LLM in-game. External LLMs (e.g. DeepSeek) are for **you** as designer/writer, not runtime NPC unless you later add an API client.
- Packaging: PyInstaller **onedir** spec `src/main_advanced_v2.spec`; `src/build_exe.bat`.
- Tech stack: Python 3.13 in dev logs; pygame; mido for MIDI; optional `ascii-art`.

**What to ask DeepSeek for:** branching narrative beats, new `/` commands, tone guides for 小误, setting screen UX copy, achievement themes, or prioritizing P1/P2 from the outlook doc—always mention whether output should stay **offline-first** (no network dependency in shipped game).

---

## 3. 建议你在末尾追加的约束（模板）

复制下面一段，填完后接在第二节英文块后面发给 DeepSeek：

```
Additional constraints for this project:
- UI / design copy language: [中文 only / bilingual zh+en / English only]
- Shipped game must remain: [offline-only / online features OK if optional]
- Tone for 小误: [e.g. gentle, slightly uncanny, no explicit gore]
- Age target: [e.g. teen+]
- Do NOT assume: [e.g. LLM in runtime, Unity engine]
```

---

## 4. 附录：可一并贴给 DeepSeek 的摘录

### 4.1 README 开头（项目定位）

（摘自 `README.md`）

- BBS Shojo：复古 BBS 风格视觉小说，像素、ASCII、千禧年氛围；核心机制「记忆碎片」。
- 终端版：`src` 下 `python main_bbs_terminal.py`；404、webring、guestbook、dead links、图灵/特修斯等 Webcore 叙事。

### 4.2 设置与功能展望摘要

（摘自 `docs/plans/2026-04-18-settings-and-features-outlook.md`）

- 现状：`main_advanced_v2.py` 已整合 CRT/VH/打字/论坛/存档/BGM·`/midi`/记忆条立绘；对话由 `girl_conversation` + `bbs_engine`；**游戏内设置 UI 几乎空白**。
- P1 建议：音量、CRT/VH 档位、`settings.json` + 可选 `O` 键设置层。
- P2：窗口/语言、自动保存、对话历史持久化。
- P3：文本速度、叙事章节节点、成就等。

### 4.3 对话层代码结构（节选）

（摘自 `src/story_mode/girl_conversation.py` — 说明非 LLM、有短期记忆与意图分支）

```python
class GirlConversationManager:
    def __init__(self) -> None:
        self.turns: List[Tuple[str, str]] = []

    def compose_reply(self, girl: GirlState, message: str, keywords: List[str]) -> str:
        # order: hard intents -> contextual_bridge -> keyword/mood templates (+ optional infection line)
```

硬意图与承接逻辑在同文件 `_match_hard_intents`、`_contextual_bridge`、`_from_keywords_and_mood` 中实现；向 DeepSeek 要**新台词池**或**新意图正则**时，可指明改此文件与 `girl_state.py` 的 `keyword_responses`。

---

**完成自检**：若你已将第二节复制到 DeepSeek并加上第三节约束，即可在任务列表里勾掉「粘贴」相关待办；附录用于可选的第二轮深聊。
