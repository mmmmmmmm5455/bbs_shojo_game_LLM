#!/usr/bin/env python3
"""BBS少女：千禧年打字物语（终端模式）"""

import sys
import time

from story_mode.bbs_engine import BBSEngine


def safe_print(text: str) -> None:
    s = str(text)
    try:
        print(s)
    except UnicodeEncodeError:
        buf = getattr(sys.stdout, "buffer", None)
        if buf is not None:
            try:
                buf.write((s + "\n").encode("utf-8", errors="replace"))
                buf.flush()
                return
            except Exception:
                pass
        try:
            enc = getattr(sys.stdout, "encoding", None) or "utf-8"
            print(s.encode(enc, errors="backslashreplace").decode(enc, errors="replace"))
        except Exception:
            print(s.encode("ascii", errors="replace").decode("ascii"))


def main():
    engine = BBSEngine()
    safe_print("Best viewed with Netscape Navigator 4.0 / 800x600")
    safe_print("<marquee>WELCOME TO WEBCORE BBS</marquee>")
    safe_print("欢迎来到『BBS少女：千禧年打字物语』")
    safe_print("你发现了一个被遗忘的论坛……")
    safe_print("输入 help 查看命令。")
    easter = engine.time_loophole_event()
    if easter:
        safe_print(easter)
    offline = engine.load_offline_log()
    if offline:
        safe_print(f"\n[离线日记]\n{offline}\n")

    blink = False
    while True:
        try:
            # 每回合刷新一次“状态栏”（blink/marquee 氛围）
            blink = not blink
            mood = engine.girl.current_mood_name
            os_mode = engine.girl.os_mode
            codex = engine.deadlinks_status()
            marquee = ">>> W E B C O R E   B B S   D A T A   D E C A Y <<<"
            bar = f"[{os_mode}] mood:{mood} | {codex} | {marquee}"
            if blink:
                safe_print(bar)
            hint = engine.tick_webcore()
            if hint:
                safe_print(hint)

            cmd = input("\n> ").strip()
            if not cmd:
                continue
            cmd_lower = cmd.lower()
            if cmd_lower == "exit":
                safe_print("你离开了论坛。少女的声音渐渐消失在数据流中……")
                break
            if cmd_lower == "list":
                safe_print(engine.list_topics())
                continue
            if cmd_lower.startswith("view "):
                try:
                    pid = int(cmd_lower.split()[1])
                except Exception:
                    safe_print("用法: view <帖子ID>")
                    continue
                safe_print(engine.view_post(pid))
                continue
            if cmd_lower.startswith("reply "):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    safe_print("用法: reply <帖子ID> <内容>")
                    continue
                try:
                    pid = int(parts[1])
                except Exception:
                    safe_print("帖子ID必须是数字。")
                    continue
                safe_print(engine.reply_to_post(pid, parts[2]))
                continue
            if cmd_lower == "status":
                safe_print(engine.get_status())
                continue
            if cmd_lower == "help":
                safe_print(
                    "可用命令: list, view <ID>, reply <ID> <内容>, status, memories, "
                    "edit_fragment <id> <文本>, delete_fragment <id>, ascii <文本>, "
                    "turing_test, answer <文本>, theseus <warm|cold>, "
                    "mode <win95|win98|winxp|win7>, "
                    "sig set <文本>|sig show, "
                    "geo edit <标题>|<简介>|<主题>, geo show, "
                    "webring <prev|next|random>, "
                    "guestbook add <名字>|<留言>, guestbook list, "
                    "deadlinks, "
                    "enter_404, exit"
                )
                continue
            if cmd_lower == "memories":
                safe_print(engine.list_memories())
                continue
            if cmd_lower.startswith("edit_fragment "):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    safe_print("用法: edit_fragment <id> <新文本>")
                    continue
                try:
                    idx = int(parts[1])
                except Exception:
                    safe_print("id 必须是数字。")
                    continue
                safe_print(engine.edit_fragment(idx, parts[2]))
                continue
            if cmd_lower.startswith("delete_fragment "):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    safe_print("用法: delete_fragment <id>")
                    continue
                try:
                    idx = int(parts[1])
                except Exception:
                    safe_print("id 必须是数字。")
                    continue
                safe_print(engine.delete_fragment(idx))
                continue
            if cmd_lower.startswith("ascii "):
                safe_print(engine.ascii_text(cmd[6:]))
                continue
            if cmd_lower == "turing_test":
                safe_print(engine.turing_test_round())
                continue
            if cmd_lower.startswith("answer "):
                safe_print(engine.turing_test_round(cmd[7:]))
                continue
            if cmd_lower.startswith("theseus "):
                parts = cmd_lower.split(maxsplit=1)
                safe_print(engine.theseus_rewrite(parts[1]))
                continue
            if cmd_lower.startswith("mode "):
                safe_print(engine.set_mode(cmd_lower.split(maxsplit=1)[1]))
                continue
            if cmd_lower == "sig show":
                safe_print(engine.get_signature())
                continue
            if cmd_lower.startswith("sig set "):
                safe_print(engine.set_signature(cmd[8:]))
                continue
            if cmd_lower.startswith("geo edit "):
                raw = cmd[9:]
                parts = [p.strip() for p in raw.split("|")]
                if len(parts) < 3:
                    safe_print("用法: geo edit <标题>|<简介>|<主题>")
                    continue
                safe_print(engine.geocities_update(parts[0], parts[1], parts[2]))
                continue
            if cmd_lower == "geo show":
                safe_print(engine.geocities_show())
                continue
            if cmd_lower.startswith("webring "):
                safe_print(engine.webring_nav(cmd_lower.split(maxsplit=1)[1]))
                continue
            if cmd_lower.startswith("guestbook add "):
                payload = cmd[14:]
                parts = [p.strip() for p in payload.split("|")]
                if len(parts) < 2:
                    safe_print("用法: guestbook add <名字>|<留言>")
                    continue
                safe_print(engine.guestbook_add(parts[0], parts[1]))
                continue
            if cmd_lower == "guestbook list":
                safe_print(engine.guestbook_list())
                continue
            if cmd_lower == "deadlinks":
                safe_print(engine.deadlinks_list())
                continue
            if cmd_lower == "enter_404":
                safe_print("你尝试在噪点里寻找 404 房间……")
                safe_print(engine.list_topics())
                continue
            if cmd_lower in {"desktop_pet", "frutiger", "midi_edit"}:
                safe_print("[UNDER CONSTRUCTION] 该功能正在搭建中。")
                continue
            safe_print(engine.render_404("未知命令。输入 help 查看帮助。"))
        except KeyboardInterrupt:
            safe_print("\n你关闭了终端连接。再见。")
            break
        except Exception as exc:
            safe_print(f"错误: {exc}")
    engine.write_offline_log()


if __name__ == "__main__":
    main()
