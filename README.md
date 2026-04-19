# BBS Shojo游戏 - 千禧年打字物语

## 🎉 项目简介
BBS Shojo游戏是一个基于复古BBS风格的视觉小说游戏，结合像素艺术、ASCII动画和怀旧千禧年氛围，旨在为玩家提供沉浸式的复古网络体验。游戏核心机制围绕“记忆碎片”展开，玩家通过互动收集记忆碎片，解锁不同的视觉表现和剧情分支。

## 🌐 Webcore 叙事模式（终端版，新增）

除了图形版（Pygame）外，项目还包含一个 **终端版 BBS 少女模式**：更贴近 Web 1.0 的“限制性体验”，以命令行、废链、留言板、webring 导航等方式营造早期互联网的幽灵感。

- **启动**：在 `bbs-shojo-game/src` 目录运行 `python main_bbs_terminal.py`
- **特点**：
  - **404 错误页**：未知命令/失效帖子会显示 ASCII 404 页面
  - **Webring 导航**：`webring prev|next|random`
  - **Guestbook 留言板**：`guestbook add <名字>|<留言>` / `guestbook list`
  - **访客计数器**：`list` 顶部会显示 `VISITOR COUNTER`
  - **Dead Link Codex**：随机掉落“失效链接”，`deadlinks` 查看图鉴
  - **Blink/Marquee 状态栏**：每次输入前刷新一行氛围状态条
  - **哲学支线**：`turing_test`、`theseus warm|cold`、离线日记、时间漏洞彩蛋等

## ✨ 新增功能（最新）

### 🎨 艺术深化功能
1. **像素精度渐变系统**：根据记忆碎片数量动态切换立绘精度，隐喻记忆复苏的过程
2. **CRT老化模拟效果**：模拟老式显示器的扫描线、噪点、偏色和烧屏效果
3. **ASCII表情动画系统**：多帧表情动画，支持ASCII艺术转换，探索语言与图像的边界
4. **高级MIDI编辑器**：支持简谱和命令输入，情绪切换乐器，实现“受限的诗意”
5. **动态音效联动**：表情与音效自动关联，增强情感表达
6. **垂直保持失调效果**：交互式画面滚动，模拟显示器故障，增强沉浸感

### 🧠 哲学深化功能
1. **记忆碎片系统**：收集、修改和删除记忆碎片，探索身份的本质
2. **图灵测试支线**：证明角色不是自动回复机器人，引发对AI真实性的思考
3. **离线日记功能**：角色在玩家离开时的思考，增强情感连接
4. **特修斯之船任务**：重写角色代码，思考身份的连续性
5. **时间漏洞彩蛋**：探索千禧年怀旧和世纪末焦虑
6. **多结局系统**：根据玩家选择的不同，实现多种哲学结局

### 🚀 全新功能
1. **时间系统联动**：根据真实时间触发特殊事件（深夜提示、节日祝福、周末问候）
2. **打字挑战小游戏**：测试玩家的打字速度和准确性，提升好感度
3. **论坛NPC系统**：其他网友NPC，动态生成帖子和互动，模拟真实的BBS社区

## 📦 最终交付物

```
bbs-shojo-game/
├── assets/          # 资源文件目录
│   ├── images/      # 立绘资源
│   └── sounds/      # 音效资源
├── src/             # 源代码目录
│   ├── main_advanced.py # 主程序入口（整合所有功能）
│   ├── main_advanced_v2.py # 整合最新功能的主程序
│   ├── pixel_gradient_system.py # 像素精度渐变系统
│   ├── crt_manager.py # CRT老化模拟管理器
│   ├── ascii_animation_system.py # ASCII表情动画系统
│   ├── midi_editor_advanced.py # 高级MIDI编辑器
│   ├── advanced_animated_character.py # 带音效的ASCII角色
│   ├── vertical_hold_manager.py # 垂直保持失调管理器
│   ├── time_system.py # 时间系统联动
│   ├── typing_challenge.py # 打字挑战小游戏
│   ├── forum_npc.py # 论坛NPC系统
│   └── test_*.py # 各模块测试脚本
├── docs/            # 文档目录
│   ├── user_manual.md # 用户手册
│   └── art_philosophy_design.md # 艺术与哲学设计文档
├── game-design-document.md # 游戏设计文档
├── tech-stack.md    # 技术栈文档
├── implementation-plan.md # 实施计划文档
├── progress.md      # 项目进度记录
└── README.md        # 项目说明文档
```

## 🚀 快速使用

**说明路径：** 下面「仓库根目录」指含有 `src`、`README.md` 的那一层。若你当前路径已是该目录（例如 `...\bbs-shojo-game`），请使用 `cd src`，**不要**再写 `cd bbs-shojo-game\src`（否则会多一层不存在的路径）。

### 方式一：直接运行可执行文件（PyInstaller 打包产物）
```bash
cd src/dist/BBSShojoGame
BBSShojoGame.exe   # Windows：请保留整个 BBSShojoGame 文件夹一起拷贝
```

### 方式二：从源代码运行
```bash
cd src
python main_advanced_v2.py
```

### 方式三：运行终端版 BBS 少女模式（Webcore）
```bash
cd src
python main_bbs_terminal.py
```

## 🎯 游戏特色

1. **复古BBS风格**：网格界面、ASCII艺术、复古音效，带你回到90年代的网络时代
2. **深度哲学思考**：探讨数字意识、记忆、身份和存在等哲学议题
3. **丰富的互动系统**：打字挑战、论坛互动、时间联动，提供多样化的游戏体验
4. **高可定制性**：支持自定义背景、音效、角色表情，满足不同玩家的需求
5. **多结局系统**：玩家的选择将影响游戏的结局，实现不同的故事走向

## 💡 项目亮点

- ✅ 完全遵循Vibe Coding开发流程，规划先行，模块化开发
- ✅ 深入的艺术设计，每个视觉效果都有哲学隐喻
- ✅ 丰富的哲学议题，引发玩家对数字意识和身份的思考
- ✅ 模块化的代码结构，易于维护和扩展
- ✅ 详细的文档和测试，确保代码质量
- ✅ 支持多种平台运行（Windows/Linux/Mac）

## 📞 技术支持

如有任何问题或需要进一步的定制，请随时联系项目开发者。

---

**项目状态：✅ 全部完成**
**开发周期：从基础版本到艺术哲学深化**
**遵循流程：Vibe Coding 完整指南**
**最终交付：完整的游戏体验 + 深入的艺术哲学设计 + 全新的互动系统**