# Settings & feature outlook（简报 + 规划骨架）

> 按 **writing-plans** 思路：先划边界与文件归属，再分阶段；**非**逐文件 TDD 清单（需要时可对单一子系统另开完整 plan）。

**游戏现状摘要**：`main_advanced_v2.py` 已整合 CRT/VH/打字/论坛/存档/BGM·`/midi`/记忆条立绘；对话由 `story_mode/girl_conversation.py` + `bbs_engine`；设置层几乎全缺。

---

## 一、设置（Settings）— 建议优先级

| 方向 | 玩家价值 | 建议落点（代码） | 阶段 |
|------|-----------|------------------|------|
| **音量** | Master / BGM / SFX 分轨 | `main_advanced_v2` 状态 + `MIDISequencer` / `AdvancedAnimatedCharacter` 读音量；持久化进 `user_data_path("settings.json")` | P1 |
| **CRT / VH 强度** | 可访问性 + 个人口味 | 已有 `crt_manager.set_aging_level`、VH `activate` 参数 → UI 滑条或档位（轻/中/重/关） | P1 |
| **窗口** | 全屏/分辨率/VSync | `pygame.display.set_mode`  flags、`SCRATCH` 配置 | P2 |
| **语言** | 中/英 UI 与帮助 | `ui_text` 或字符串表 `locales/zh.json` + 切换重载字体 | P2 |
| **文本速度** | 视觉小说感 | 聊天历史逐字显示或 `time_system` 提示停留时长 | P3 |
| **自动保存** | 防丢档 | 定时 `_save_game` 或关键事件后节流写入 | P2 |
| **对话历史持久化** | 重启后续聊 | `GirlConversationManager.turns` 写入 `savegame.json` 或独立 `chat_log.json` | P2 |

**设置 UI 形态（三选一）**：① 游戏内 `ESC`→设置子菜单；② 独立 `settings_overlay`（`O` 键）；③ 首次启动向导。推荐 **② + `settings.json`**，改动面小于重构主循环。

---

## 二、非设置类功能 — 可加分项

| 类别 | 想法 | 说明 |
|------|------|------|
| **叙事** | 章节/日标记节点 | 用 `girl_state` + 标记位驱动新命令与结局分支 |
| **系统** | 好感/信任独立条 | 与 `memory_fragments` 解耦，影响 `girl_conversation` 池解锁 |
| **社交** | NPC 私信或 @ 提及 | 论坛帖子引用玩家上一句聊天 |
| **可发现性** | 成就/图鉴 | Dead links、打字 WPM、图灵进度可视化 |
| **技术** | 单元测试 | `girl_conversation`、`bbs_engine` 纯函数测回复分支；存档 round-trip |
| **分发** | 单文件 exe / 自动更新 | PyInstaller onefile vs onedir 取舍 |

---

## 三、分阶段实施骨架（给未来「完整 plan」用）

**P1 — 最小可用设置**

- 新建 `src/settings_store.py`：读写 `settings.json`（与 `game_paths.user_data_path` 一致）。
- `main_advanced_v2`：加载设置 → 应用音量与 CRT 上限夹紧。
- 简单 overlay：`O` 打开/关闭，3～5 个控件。

**P2 — 持久化与窗口**

- 对话 tail、自动保存、分辨率写入同一 `settings.json` 或拆分文件。
- `display` 预设与全屏切换。

**P3 — 叙事与 polish**

- 本地化、文本动画、成就。

---

## 四、自检（对照 writing-plans）

- **Spec 覆盖**：设置音量/CRT/持久化均有上表对应行。  
- **占位**：无 TBD 任务号；具体实现时再拆 Task 1…N。  
- **缺口**：未指定美术资源需求；若要做设置 UI 皮肤需另列。

---

**下一步**：若你选定 **P1 设置 overlay**，可回复「做 P1」；我会再写一份带 **具体文件与步骤** 的 implementation plan（可放进 `docs/plans/` 或 `docs/superpowers/plans/` 以配合你们的 agent 流程）。
