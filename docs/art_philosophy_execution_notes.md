# 艺术与哲学扩展：执行说明

本文记录已落地到代码的“艺术与哲学”扩展点，便于后续继续迭代。

## 艺术维度

- 像素/记忆量化：记忆碎片系统已接入终端模式，关键词对话会触发碎片收集。
- ASCII 语言-图像边界：新增 `ascii <文本>` 命令，将文本转成框式 ASCII 视觉。
- CRT/媒介痕迹：图形版保留 CRT + 垂直保持效果，支持波动与触发。
- MIDI 受限诗意：图形版已有 MIDI 子系统；终端模式先用文本叙事承接。

## 哲学维度

- 模拟与拟像：新增 `turing_test` / `answer <文本>`，对“像人”程度进行进度判定。
- 记忆与身份：新增 `memories` / `edit_fragment` / `delete_fragment`，可修改或删除记忆。
- 特修斯之船：新增 `theseus <warm|cold>`，重写人格片段并影响情绪/人格偏移。
- 千禧怀旧/时间陷阱：终端模式启动时读取系统年份，<2000 触发时间漏洞彩蛋提示。
- 孤独与连接：新增离线日记（退出写入，下次启动显示）。

## 对应代码

- `src/story_mode/bbs_engine.py`
- `src/story_mode/girl_state.py`
- `src/main_bbs_terminal.py`
- `src/main_advanced_v2.py`（按 `B` 启动终端模式）
