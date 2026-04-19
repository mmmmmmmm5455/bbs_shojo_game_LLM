import json
import os
import queue
import random
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple

from story_mode.girl_state import GirlState
from story_mode.girl_conversation import GirlConversationManager


class BBSEngine:
    """处理论坛帖子、对话和情绪变化的引擎。"""

    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            base = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base, "bbs_data")
        self.data_dir = data_dir
        self.posts = self._load_posts()
        self.girl = GirlState()
        self.current_post_id = 0
        self.reply_history = []
        self.turing_progress = 0
        self._last_turing_prompt = ""
        self.player_signature = "—— [System_User]"
        self.unlock_404 = False
        self.visit_count = 0
        self.dead_links: List[Dict] = []
        self._load_runtime_state()
        self._inc_visit_count()
        self._load_dead_links()
        self.conversation = GirlConversationManager()
        # 语义意图：延迟加载，frozen/无依赖时走关键词回退
        self._intent_classifier: Optional[object] = None
        # Ollama 兜底（Phase 2）；无 ollama 包或未启用时 None
        self.llm_fallback: Optional[object] = None
        self._llm_available: Optional[bool] = None
        self._llm_next_probe_mono: float = 0.0
        try:
            from ai.llm_fallback import LLMFallback

            _model = os.environ.get("BBS_SHOJO_OLLAMA_MODEL", "phi3:mini").strip() or "phi3:mini"
            self.llm_fallback = LLMFallback(
                model=_model,
                timeout=None,
            )
        except ImportError:
            self.llm_fallback = None

    def _semantic_intent_enabled(self) -> bool:
        if getattr(sys, "frozen", False):
            return False
        return True

    def _llm_runtime_enabled(self) -> bool:
        """打包 exe 默认关闭；可设环境变量 BBS_SHOJO_DISABLE_OLLAMA=1 关闭。"""
        if getattr(sys, "frozen", False):
            return False
        if os.environ.get("BBS_SHOJO_DISABLE_OLLAMA", "").strip() in (
            "1",
            "true",
            "yes",
        ):
            return False
        return self.llm_fallback is not None

    def _llm_probe_interval_sec(self) -> float:
        raw = os.environ.get("BBS_SHOJO_OLLAMA_PROBE_INTERVAL", "").strip()
        if not raw:
            return 20.0
        try:
            return max(3.0, float(raw))
        except ValueError:
            return 20.0

    def refresh_llm_availability(self) -> None:
        """清除 Ollama 可达性缓存，下次 _llm_enabled 会重新 list 探测。"""
        self._llm_available = None
        self._llm_next_probe_mono = 0.0
        if self.llm_fallback is not None:
            try:
                self.llm_fallback.invalidate_cache()
            except Exception:
                pass

    def _llm_enabled(self) -> bool:
        if not self._llm_runtime_enabled():
            return False
        if self.llm_fallback is None:
            return False
        now = time.monotonic()
        if self._llm_available is None:
            self._llm_available = bool(self.llm_fallback.is_available_cached())
            if not self._llm_available:
                self._llm_next_probe_mono = now + self._llm_probe_interval_sec()
            return bool(self._llm_available)
        if self._llm_available:
            return True
        if now >= self._llm_next_probe_mono:
            self.llm_fallback.invalidate_cache()
            self._llm_available = bool(self.llm_fallback.is_available_cached())
            self._llm_next_probe_mono = now + self._llm_probe_interval_sec()
        return bool(self._llm_available)

    def _llm_pair_history_block(self, max_pairs: int = 3, per_line: int = 72) -> str:
        """最近若干轮「访客→小误」成对摘要，控制总长以降低 prefill 延迟。"""
        turns: List[Tuple[str, str]] = list(getattr(self.conversation, "turns", []))
        pairs: List[Tuple[str, str]] = []
        i = len(turns) - 1
        while i >= 0 and len(pairs) < max_pairs:
            if turns[i][0] != "girl":
                i -= 1
                continue
            gtxt = (turns[i][1] or "")[:per_line]
            i -= 1
            ptxt = ""
            while i >= 0:
                if turns[i][0] == "player":
                    ptxt = (turns[i][1] or "")[:per_line]
                    i -= 1
                    break
                i -= 1
            pairs.append((ptxt, gtxt))
        pairs.reverse()
        if not pairs:
            return "（尚无更早成对记录。）"
        lines: List[str] = []
        budget = 900
        for idx, (pv, gv) in enumerate(pairs, 1):
            line = f"[{idx}] 访客：{pv}\n    小误：{gv}"
            if sum(len(x) + 1 for x in lines) + len(line) > budget:
                break
            lines.append(line)
        return "\n".join(lines) if lines else "（尚无更早成对记录。）"

    def _build_llm_prompt(self, user_message: str) -> str:
        girl = self.girl
        mood = girl.current_mood_name
        infection = girl.infection
        if infection >= 35:
            style = "你的语言严重破碎，夹杂乱码和错误信息，像是快要消失的信号。"
        elif infection >= 10:
            style = "你说话开始带有一丝清醒的质疑，偶尔提及代码、系统、真实与虚假。"
        elif infection >= 5:
            style = "你说话略带迟疑，偶尔会怀疑屏幕对面是否真实。"
        else:
            style = "你有点害羞、内向，喜欢用颜文字，说话温柔，像一个住在旧 BBS 里的幽灵。"

        hist_block = self._llm_pair_history_block(max_pairs=3, per_line=72)
        current = user_message.strip().replace("\n", " ")[:400]

        return f"""你是一个名叫「小误」的女孩，住在一个复古 BBS 终端里。
你正在与一位访客聊天。性格：内向、温柔、略带电波系，对访客有淡淡好感。
当前情绪：{mood}。感染度（0-100）：{infection}。{style}

【最近对话（访客→小误）】
{hist_block}

【访客当前这句】
{current}

请以小误的口吻用中文回复**一句**（不超过 60 字），可适当使用颜文字。不要输出引号或角色名前缀。"""

    def _sanitize_llm_reply_body(self, text: str, max_chars: int = 96) -> str:
        """截断到一句或上限，避免模型啰嗦拉长打字时间。"""
        s = (text or "").strip().replace("\r", " ").replace("\n", " ")
        s = s.strip("「」\"'“”")
        for sep in ("。", "！", "？", ".", "!", "?"):
            pos = s.find(sep)
            if pos != -1 and pos + 1 <= max_chars:
                return s[: pos + 1].strip()
        if len(s) > max_chars:
            return (s[: max_chars - 1] + "…").strip()
        return s

    def _format_public_reply(self, reply_inner: str) -> str:
        return (
            f"\n{self.girl.get_name()} 回复：\n"
            f"{self.girl.os_flavor(reply_inner)}\n"
            f"{self.girl.get_kaomoji()}\n"
        )

    def _append_replies_and_save(self, post_id: int, message: str, reply_inner: str) -> None:
        post = self.posts.get(str(post_id))
        if not post:
            return
        post.setdefault("replies", []).append(
            {
                "author": "Player",
                "content": message[:120],
                "signature": self.player_signature,
                "time": "刚刚",
            }
        )
        post.setdefault("replies", []).append(
            {
                "author": "System_Error",
                "content": self.girl.os_flavor(reply_inner),
                "signature": self.girl.get_signature(),
                "time": "刚刚",
            }
        )
        self.save_posts()

    def _spawn_llm_graphical_worker(
        self,
        post_id: int,
        message: str,
        keywords: List[str],
        prompt: str,
        result_queue: "queue.SimpleQueue",
        token: int,
    ) -> None:
        llm = self.llm_fallback

        def run() -> None:
            def on_first() -> None:
                try:
                    result_queue.put(("llm_first", token))
                except Exception:
                    pass

            raw: Optional[str] = None
            if llm is not None:
                try:
                    raw = llm.generate_reply_sync(prompt, on_first_chunk=on_first)
                except Exception:
                    raw = None
            if raw:
                inner = self._sanitize_llm_reply_body(raw)
                try:
                    result_queue.put(("llm_done", token, post_id, message, keywords, inner))
                except Exception:
                    pass
            else:
                try:
                    result_queue.put(("llm_fallback", token, post_id, message, keywords))
                except Exception:
                    pass

        threading.Thread(target=run, daemon=True).start()

    def complete_graphical_llm_success(
        self,
        post_id: int,
        message: str,
        keywords: List[str],
        reply_inner: str,
    ) -> str:
        self.conversation.record_llm_reply(message, reply_inner)
        self._collect_memory_fragment(message, keywords)
        self._append_replies_and_save(post_id, message, reply_inner)
        return self._format_public_reply(reply_inner)

    def complete_graphical_llm_fallback(
        self, post_id: int, message: str, keywords: List[str]
    ) -> str:
        reply_text = self.conversation.compose_reply_body(self.girl, message, keywords)
        self._collect_memory_fragment(message, keywords)
        self._append_replies_and_save(post_id, message, reply_text)
        return self._format_public_reply(reply_text)

    def reply_to_post_graphical(
        self,
        post_id: int,
        message: str,
        result_queue: "queue.SimpleQueue",
        llm_token: int,
    ) -> Tuple[Optional[str], bool]:
        """
        图形端专用：在需 Ollama 且可用时启动后台线程并通过队列返回结果。
        返回 (display_text, llm_pending)；llm_pending 为 True 时 display_text 为 None。
        llm_token 由主循环生成，用于丢弃过期异步结果。
        """
        if not message.strip():
            return ("说点什么吧…… (´-ω-`)\n", False)
        if message.strip().startswith("/"):
            return (
                "……以 / 开头的是命令语法，这条对话里我只想你像写信一样说话。"
                "想用命令请在图形版底部输入 /help，或在终端用 list / reply 等指令。(´-ω-`)\n",
                False,
            )

        keywords = self._analyze_keywords(message)
        mood_change = self.girl.process_message(keywords, message)
        self.reply_history.append(
            {
                "post_id": post_id,
                "message": message,
                "mood_before_delta": mood_change[0],
                "mood_after": self.girl.mood_value,
            }
        )

        early = self.conversation.try_early_reply(self.girl, message)
        if early is not None:
            reply_text = early
            self._collect_memory_fragment(message, keywords)
            self._append_replies_and_save(post_id, message, reply_text)
            return (self._format_public_reply(reply_text), False)

        if (
            keywords == ["neutral"]
            and self._llm_runtime_enabled()
            and self._llm_enabled()
        ):
            prompt = self._build_llm_prompt(message)
            self._spawn_llm_graphical_worker(
                post_id, message, keywords, prompt, result_queue, token=llm_token
            )
            return (None, True)

        if keywords == ["neutral"]:
            reply_text = self.conversation.compose_reply_body(self.girl, message, keywords)
        else:
            reply_text = self.conversation.compose_reply(self.girl, message, keywords)
        self._collect_memory_fragment(message, keywords)
        self._append_replies_and_save(post_id, message, reply_text)
        return (self._format_public_reply(reply_text), False)

    def _try_llm_reply(self, message: str) -> Optional[str]:
        if not self.llm_fallback or not self._llm_enabled():
            return None
        prompt = self._build_llm_prompt(message)
        return self.llm_fallback.generate_reply_sync(prompt)

    def _get_intent_classifier(self):
        """首次需要分类时构造 IntentClassifier；构造失败则缓存 False，之后返回 None。"""
        if not self._semantic_intent_enabled():
            return None
        if self._intent_classifier is False:
            return None
        if self._intent_classifier:
            return self._intent_classifier
        try:
            from ai.intent_classifier import IntentClassifier

            self._intent_classifier = IntentClassifier()
            return self._intent_classifier
        except Exception:
            self._intent_classifier = False
            return None

    def _posts_path(self) -> str:
        return os.path.join(self.data_dir, "posts.json")

    def _state_path(self) -> str:
        return os.path.join(self.data_dir, "runtime_state.json")

    def _geo_path(self) -> str:
        return os.path.join(self.data_dir, "geocities_home.json")

    def _guestbook_path(self) -> str:
        return os.path.join(self.data_dir, "guestbook.json")

    def _deadlinks_path(self) -> str:
        return os.path.join(self.data_dir, "dead_links.json")

    def _load_posts(self) -> Dict:
        with open(self._posts_path(), "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_runtime_state(self):
        path = self._state_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.player_signature = data.get("player_signature", self.player_signature)
            self.unlock_404 = bool(data.get("unlock_404", False))
            self.visit_count = int(data.get("visit_count", 0))
            if data.get("os_mode"):
                self.girl.os_mode = data.get("os_mode")
        except Exception:
            return

    def _save_runtime_state(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._state_path(), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "player_signature": self.player_signature,
                    "unlock_404": self.unlock_404,
                    "visit_count": self.visit_count,
                    "os_mode": self.girl.os_mode,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    def _load_dead_links(self):
        path = self._deadlinks_path()
        if not os.path.exists(path):
            self.dead_links = []
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.dead_links = json.load(f) or []
        except Exception:
            self.dead_links = []

    def _save_dead_links(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._deadlinks_path(), "w", encoding="utf-8") as f:
            json.dump(self.dead_links[-200:], f, indent=2, ensure_ascii=False)

    def _inc_visit_count(self):
        self.visit_count += 1
        self._save_runtime_state()

    def save_posts(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._posts_path(), "w", encoding="utf-8") as f:
            json.dump(self.posts, f, indent=2, ensure_ascii=False)
        self._save_runtime_state()
        self._save_dead_links()

    def tick_webcore(self) -> str:
        """
        每回合调用一次：
        - 低概率触发 Dead Link Cemetery 事件（并写入图鉴）
        - 返回可选的“系统提示行”（可能为空）
        """
        msg = self._maybe_dead_link_event()
        return msg

    def _maybe_dead_link_event(self) -> str:
        if random.random() > 0.10:
            return ""
        templates = [
            {"title": "broken-image.png", "hint": "[x] image not found"},
            {"title": "webring_prev.cgi", "hint": "CGI script missing"},
            {"title": "guestbook.pl", "hint": "permission denied"},
            {"title": "index_of_midi/", "hint": "directory listing vanished"},
            {"title": "lost_floppy.img", "hint": "CRC mismatch"},
            {"title": "geocities_neighborhood", "hint": "neighborhood deleted"},
        ]
        it = random.choice(templates)
        entry = {
            "id": len(self.dead_links) + 1,
            "title": it["title"],
            "hint": it["hint"],
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.dead_links.append(entry)
        self._save_dead_links()
        # 微小哲学回响：发现废链会略微增加感染或情绪波动
        if "CRC" in entry["hint"] or "vanished" in entry["hint"]:
            self.girl.infection = min(100, self.girl.infection + 1)
        return f"[dead-link] 你捡到一条失效链接：{entry['title']} ({entry['hint']})"

    def deadlinks_status(self) -> str:
        count = len(self.dead_links)
        return f"Dead Link Codex: {count} collected"

    def deadlinks_list(self) -> str:
        if not self.dead_links:
            return "Dead Link Codex 为空。多输入命令探索，可能会掉落失效链接。"
        lines = ["=== Dead Link Cemetery / Codex ==="]
        for it in self.dead_links[-15:]:
            lines.append(f"#{it['id']:03d} {it['title']}  [{it['hint']}]  ({it['time']})")
        return "\n".join(lines)

    def list_topics(self) -> str:
        self._maybe_ghost_event()
        self._maybe_unlock_404()
        counter = f"VISITOR COUNTER: {self.visit_count:06d}"
        wobble = random.choice(["*", "#", "@"])
        output = "\n┌────┬──────────────────────────────────┬────────────┐\n"
        output += f"│ {counter} {wobble}                                   │\n"
        output += "├────┬──────────────────────────────────┬────────────┤\n"
        output += "│ ID │ 标题                             │ 回复数     │\n"
        output += "├────┼──────────────────────────────────┼────────────┤\n"
        for pid, post in self.posts.items():
            if pid == "404" and not self.unlock_404:
                continue
            title = post["title"][:30].ljust(30)
            replies = len(post.get("replies", []))
            output += f"│ {int(pid):2} │ {title} │ {replies:3}       │\n"
        output += "└────┴──────────────────────────────────┴────────────┘\n"
        output += "\n使用 `view <ID>` 查看帖子。可用 webring <prev|next|random> 导航。"
        return output

    def view_post(self, post_id: int) -> str:
        self._maybe_ghost_event()
        post = self.posts.get(str(post_id))
        if not post:
            return self.render_404("帖子不存在，链接已腐化。")
        if str(post_id) == "404" and not self.unlock_404:
            return self.render_404("404 房间尚未稳定显现。")

        self.current_post_id = post_id
        output = f"\n【{post['title']}】\n"
        output += f"发帖人：{post['author']}  {post['time']}\n"
        output += f"{post['content']}\n"
        output += f"{self.girl.get_kaomoji('neutral')}\n"
        output += "-" * 40 + "\n"

        for idx, reply in enumerate(post.get("replies", []), 1):
            output += f"> 第{idx}楼 {reply['author']}：{reply['content']}\n"
            if reply.get("signature"):
                output += f"  {reply['signature']}\n"
        return output

    def render_404(self, reason: str = "链接失效") -> str:
        return (
            "\n+----------------------------------+\n"
            "| ERROR 404 - BROKEN LINK         |\n"
            "| [x] image not found             |\n"
            "| (；´Д`A 这里什么都没有         |\n"
            "+----------------------------------+\n"
            f"{reason}\n"
        )

    def webring_nav(self, action: str) -> str:
        """Webring 风格导航：上一页 / 下一页 / 随机。"""
        visible_ids = [
            int(pid) for pid in self.posts.keys() if pid.isdigit() and (pid != "404" or self.unlock_404)
        ]
        if not visible_ids:
            return self.render_404("没有可用帖子。")
        visible_ids.sort()
        if self.current_post_id in visible_ids:
            idx = visible_ids.index(self.current_post_id)
        else:
            idx = 0
        action = action.strip().lower()
        if action == "prev":
            idx = (idx - 1) % len(visible_ids)
        elif action == "next":
            idx = (idx + 1) % len(visible_ids)
        elif action == "random":
            idx = random.randint(0, len(visible_ids) - 1)
        else:
            return "用法: webring <prev|next|random>"
        return self.view_post(visible_ids[idx])

    def reply_to_post(self, post_id: int, message: str) -> str:
        if not message.strip():
            return "说点什么吧…… (´-ω-`)\n"

        if message.strip().startswith("/"):
            return (
                "……以 / 开头的是命令语法，这条对话里我只想你像写信一样说话。"
                "想用命令请在图形版底部输入 /help，或在终端用 list / reply 等指令。(´-ω-`)\n"
            )

        keywords = self._analyze_keywords(message)
        mood_change = self.girl.process_message(keywords, message)
        self.reply_history.append(
            {
                "post_id": post_id,
                "message": message,
                "mood_before_delta": mood_change[0],
                "mood_after": self.girl.mood_value,
            }
        )

        early = self.conversation.try_early_reply(self.girl, message)
        if early is not None:
            reply_text = early
        elif (
            keywords == ["neutral"]
            and self._llm_runtime_enabled()
            and self._llm_enabled()
        ):
            llm_text = self._try_llm_reply(message)
            if llm_text:
                reply_text = self._sanitize_llm_reply_body(llm_text)
                self.conversation.record_llm_reply(message, reply_text)
            else:
                reply_text = self.conversation.compose_reply_body(
                    self.girl, message, keywords
                )
        else:
            reply_text = self.conversation.compose_reply(self.girl, message, keywords)
        self._collect_memory_fragment(message, keywords)
        self._append_replies_and_save(post_id, message, reply_text)
        return self._format_public_reply(reply_text)

    def _collect_memory_fragment(self, message: str, keywords: List[str]):
        """记忆碎片系统：按关键词收集对话片段。"""
        if len(self.girl.memory_fragments) >= 12:
            return
        if any(
            k in keywords
            for k in (
                "past",
                "future",
                "love",
                "sad",
                "tech",
                "confused",
                "lonely",
                "phantom",
            )
        ):
            frag = message.strip()[:40]
            if frag and frag not in self.girl.memory_fragments:
                self.girl.memory_fragments.append(frag)

    def _analyze_keywords(self, text: str) -> List[str]:
        clf = self._get_intent_classifier()
        if clf is not None:
            intent, _score = clf.classify(text)
            if intent is not None:
                return [intent]
        return self._analyze_keywords_fallback(text)

    def _analyze_keywords_fallback(self, text: str) -> List[str]:
        """关键词子串匹配（与旧逻辑一致）；语义模型不可用或置信度低时使用。"""
        text_lower = text.lower()
        keywords: List[str] = []
        if any(word in text_lower for word in ["你好", "嗨", "hello", "hi"]):
            keywords.append("greeting")
        if any(word in text_lower for word in ["难过", "伤心", "哭", "sad"]):
            keywords.append("sad")
        if any(word in text_lower for word in ["程序", "代码", "bug", "病毒"]):
            keywords.append("tech")
        if any(word in text_lower for word in ["过去", "回忆", "以前"]):
            keywords.append("past")
        if any(word in text_lower for word in ["未来", "以后", "明天"]):
            keywords.append("future")
        if any(word in text_lower for word in ["喜欢", "爱", "suki", "love"]):
            keywords.append("love")
        if any(word in text_lower for word in ["谢谢", "感谢", "thanks", "thx"]):
            keywords.append("thanks")
        if any(word in text_lower for word in ["再见", "拜拜", "bye", "晚安"]):
            keywords.append("bye")

        if any(
            word in text_lower
            for word in ["我是谁", "身份", "真实", "存在", "混乱", "搞不懂"]
        ):
            keywords.append("confused")

        if any(
            word in text_lower
            for word in ["孤独", "一个人", "等待", "安静", "寂寞"]
        ):
            keywords.append("lonely")

        if any(
            word in text_lower
            for word in ["幽灵", "数据", "残留", "灵魂", "其他人", "幻影"]
        ):
            keywords.append("phantom")

        if "?" in text or "？" in text or any(m in text for m in ("吗", "么", "嘛", "呢")):
            keywords.append("question")
        return keywords if keywords else ["neutral"]

    def _maybe_ghost_event(self):
        """赛博幽灵：随机在帖子中留下模糊回复。"""
        if random.random() > 0.12:
            return
        candidates = [k for k in self.posts.keys() if k != "404"]
        if not candidates:
            return
        pid = random.choice(candidates)
        ghost_lines = [
            "看见你了。",
            "不要相信时间戳。",
            "她不是唯一的她。",
            "如果你看到这条，说明系统在回放。",
        ]
        self.posts[pid].setdefault("replies", []).append(
            {
                "author": "Cyber_Ghost",
                "content": random.choice(ghost_lines),
                "signature": "—— ???",
                "time": "未知",
            }
        )

    def _maybe_unlock_404(self):
        """低概率解锁 404 房间。"""
        if self.unlock_404:
            return
        if random.random() < 0.08:
            self.unlock_404 = True
            if "404" not in self.posts:
                self.posts["404"] = {
                    "title": "404 房间：这里本应什么都没有",
                    "author": "Unknown",
                    "time": "----/--/-- --:--",
                    "content": "你进入了一个不存在的帖子。屏幕像在呼吸。",
                    "replies": [
                        {
                            "author": "Cyber_Ghost",
                            "content": "你终于来了。",
                            "signature": "—— 404",
                            "time": "未知",
                        }
                    ],
                }
            self._save_runtime_state()

    def get_status(self) -> str:
        return f"""
┌─────────────────────────────────┐
│  {self.girl.get_name()} 状态                         │
├─────────────────────────────────┤
│  情绪值: {self.girl.mood_value:3}/100                    │
│  感染度: {self.girl.infection:3}/100                    │
│  记忆碎片: {len(self.girl.memory_fragments):2}/12                  │
│  当前心情: {self.girl.current_mood_name:6}                  │
│  人格偏移: {self.girl.personality_mod:4}                    │
│  系统模式: {self.girl.os_mode:6}                     │
└─────────────────────────────────┘
"""

    def list_memories(self) -> str:
        if not self.girl.memory_fragments:
            return "暂无记忆碎片。多聊聊过去、未来或感情话题来触发。"
        lines = ["记忆碎片列表:"]
        for idx, frag in enumerate(self.girl.memory_fragments, 1):
            lines.append(f"{idx:2}. {frag}")
        return "\n".join(lines)

    def edit_fragment(self, idx: int, new_text: str) -> str:
        if idx < 1 or idx > len(self.girl.memory_fragments):
            return "碎片编号不存在。"
        self.girl.memory_fragments[idx - 1] = new_text[:80]
        return f"已修改碎片 #{idx}。"

    def delete_fragment(self, idx: int) -> str:
        if idx < 1 or idx > len(self.girl.memory_fragments):
            return "碎片编号不存在。"
        removed = self.girl.memory_fragments.pop(idx - 1)
        return f"已删除碎片 #{idx}: {removed}"

    def ascii_text(self, text: str) -> str:
        """ASCII 文本渲染：语言与图像的边界。"""
        text = (text or "").strip()
        if not text:
            return "用法: ascii <文字>"
        line = " ".join(list(text.upper()))
        border = "+" + "-" * (len(line) + 2) + "+"
        return f"{border}\n| {line} |\n{border}"

    def turing_test_round(self, answer: str | None = None) -> str:
        """
        图灵测试简化回合：
        - 无 answer 时给出问题
        - 有 answer 时评分并更新进度
        """
        prompts = [
            "如果你难过时会做什么？",
            "你会如何描述‘被遗忘’的感觉？",
            "为什么你想活到2000年之后？",
        ]
        if answer is None:
            self._last_turing_prompt = random.choice(prompts)
            return f"[图灵测试] 请回答：{self._last_turing_prompt}"

        score = 0
        ans = answer.strip().lower()
        if len(ans) >= 8:
            score += 30
        if any(k in ans for k in ["因为", "如果", "记得", "害怕", "希望", "love", "feel"]):
            score += 40
        if any(k in ans for k in ["。", "？", "!", "！", "…"]):
            score += 10
        score += random.randint(0, 20)
        self.turing_progress = min(100, self.turing_progress + score // 4)
        if self.turing_progress >= 100:
            self.girl.mood_value = min(100, self.girl.mood_value + 10)
            return "图灵测试完成！网友开始相信她并非机械回复。"
        return f"本轮完成度 +{score // 4}，当前图灵进度: {self.turing_progress}%"

    def theseus_rewrite(self, direction: str) -> str:
        return self.girl.rewrite_personality_chunk(direction.strip().lower())

    def set_mode(self, mode: str) -> str:
        msg = self.girl.set_os_mode(mode)
        self._save_runtime_state()
        return msg

    def set_signature(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "签名不能为空。"
        self.player_signature = text[:60]
        self._save_runtime_state()
        return f"签名已更新: {self.player_signature}"

    def get_signature(self) -> str:
        return self.player_signature

    def geocities_update(self, title: str, about: str, theme: str) -> str:
        payload = {
            "title": title[:40],
            "about": about[:300],
            "theme": theme[:30],
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._geo_path(), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return "Geocities 小屋已保存。"

    def geocities_show(self) -> str:
        if not os.path.exists(self._geo_path()):
            return "还没有小屋主页。用: geo edit <标题>|<简介>|<主题>"
        with open(self._geo_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return (
            "=== Geocities 小屋 ===\n"
            f"标题: {data.get('title', '')}\n"
            f"主题: {data.get('theme', '')}\n"
            f"简介: {data.get('about', '')}\n"
            f"更新时间: {data.get('updated_at', '')}"
        )

    def guestbook_add(self, name: str, message: str) -> str:
        name = name.strip()[:24] or "Anonymous"
        message = message.strip()[:120]
        if not message:
            return "留言不能为空。"
        entries = self.guestbook_list(raw=True)
        entries.append(
            {
                "name": name,
                "message": message,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reply": random.choice(
                    [
                        "小误：我看到了你的留言。",
                        "小误：谢谢你留下痕迹，我会记住的。",
                        "小误：网络不会忘记每一次敲击。",
                    ]
                ),
            }
        )
        with open(self._guestbook_path(), "w", encoding="utf-8") as f:
            json.dump(entries[-30:], f, indent=2, ensure_ascii=False)
        return "留言已写入 guestbook。"

    def guestbook_list(self, raw: bool = False):
        path = self._guestbook_path()
        if not os.path.exists(path):
            if raw:
                return []
            return "留言板还没有内容。用: guestbook add <名字>|<留言>"
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        if raw:
            return entries
        lines = ["=== Guestbook ==="]
        for it in entries[-10:]:
            lines.append(f"[{it.get('time')}] {it.get('name')}: {it.get('message')}")
            if it.get("reply"):
                lines.append(f"  {it.get('reply')}")
        return "\n".join(lines)

    def time_loophole_event(self) -> str:
        year = time.localtime().tm_year
        if year < 2000:
            return "检测到系统年份早于2000：触发时间漏洞彩蛋。小误：'请不要骗我……现在真的是1999吗？'"
        return ""

    def load_offline_log(self) -> str:
        path = os.path.join(self.data_dir, "offline_log.txt")
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content

    def write_offline_log(self):
        lines = [
            "你离线后，我在论坛上翻了很久旧帖……",
            "我把今天的对话存成了碎片，怕哪天会忘记你。",
            "如果明天你还来，我就再给你讲一个过去的故事。",
        ]
        path = os.path.join(self.data_dir, "offline_log.txt")
        os.makedirs(self.data_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(random.choice(lines))
