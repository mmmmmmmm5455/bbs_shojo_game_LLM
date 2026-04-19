"""
与少女的即时对话层：意图识别、短期对话记忆、与 GirlState 情绪联动。
供图形主界面聊天框使用（经 BBSEngine.reply_to_post 调用）。
"""
from __future__ import annotations

import random
import re
from typing import List, Optional, Tuple

from .girl_state import GirlState


class GirlConversationManager:
    """维护最近若干轮对话，并生成小误的回复文本（不含 os_flavor 包装）。"""

    def __init__(self) -> None:
        self.turns: List[Tuple[str, str]] = []

    def try_early_reply(
        self,
        girl: GirlState,
        message: str,
        *,
        suppress_meta_canned_when_llm: bool = False,
    ) -> Optional[str]:
        """硬意图与上下文桥接；命中则已写入对话轮次。

        suppress_meta_canned_when_llm：当本句将交给 Ollama 时，跳过「你是 AI 吗」
        与「图灵测试」类固定台词，避免抢在模型之前把个性化应答短路掉。
        """
        if message.strip().startswith("/"):
            return None
        text = message.strip()
        if not text:
            return None

        intent_result = self._match_hard_intents(
            girl, text, suppress_meta_canned=suppress_meta_canned_when_llm
        )
        if intent_result:
            intent_id, reply = intent_result
            self._apply_intent_side_effects(girl, intent_id)
            self._record_turn(text, reply)
            return reply

        ctx = self._contextual_bridge(girl, text)
        if ctx:
            self._record_turn(text, ctx)
            return ctx
        return None

    def compose_reply_body(self, girl: GirlState, message: str, keywords: List[str]) -> str:
        """仅关键词 / 情绪模板路径（不含硬意图）；会 _record_turn。"""
        if message.strip().startswith("/"):
            return ""

        text = message.strip()
        if not text:
            return "……（光标在闪，但我读不到任何字。）"

        body = self._from_keywords_and_mood(girl, keywords)
        if girl.infection > 35 and random.random() < 0.2:
            body += "\n" + random.choice(
                [
                    "（线路里……好像混进了别的杂音。）",
                    "……刚才有一瞬间，字距自己跳了一下。",
                ]
            )

        self._record_turn(text, body)
        return body

    def record_llm_reply(self, message: str, reply_text: str) -> None:
        """Ollama 兜底生成后写入对话历史。"""
        self._record_turn(message.strip()[:280], reply_text[:500])

    def compose_reply(
        self,
        girl: GirlState,
        message: str,
        keywords: List[str],
        *,
        suppress_meta_canned_when_llm: bool = False,
    ) -> str:
        if message.strip().startswith("/"):
            return ""

        text = message.strip()
        if not text:
            return "……（光标在闪，但我读不到任何字。）"

        early = self.try_early_reply(
            girl, message, suppress_meta_canned_when_llm=suppress_meta_canned_when_llm
        )
        if early is not None:
            return early

        return self.compose_reply_body(girl, message, keywords)

    def _record_turn(self, player: str, girl_line: str) -> None:
        self.turns.append(("player", player[:280]))
        self.turns.append(("girl", girl_line[:500]))
        self.turns = self.turns[-24:]

    def seed_girl_opener(self, girl_line: str) -> None:
        """首访主动问候：仅记录女孩一句，不配对玩家句、不触发回复循环。"""
        self.turns.append(("girl", girl_line[:500]))
        self.turns = self.turns[-24:]

    def _last_of(self, role: str) -> str:
        for r, content in reversed(self.turns):
            if r == role:
                return content
        return ""

    def _apply_intent_side_effects(self, girl: GirlState, intent_id: str) -> None:
        """根据意图标识符修改女孩状态。"""
        if intent_id == "real_name":
            girl.infection = min(100, girl.infection + 3)
        elif intent_id == "abandonment":
            girl.mood_value = max(0, girl.mood_value - 15)
            girl._update_mood_name()
            if "abandonment_fear" not in girl.memory_fragments:
                girl.memory_fragments.append("abandonment_fear")
        elif intent_id == "turing_question":
            girl.infection = min(100, girl.infection + 2)
            if "turing_doubt" not in girl.memory_fragments:
                girl.memory_fragments.append("turing_doubt")
        elif intent_id == "memory_boundary":
            girl.mood_value = max(0, girl.mood_value - 5)
            girl._update_mood_name()
        elif intent_id == "invite_leave":
            girl.mood_value = min(100, girl.mood_value + 10)
            girl._update_mood_name()
            if "trapped" not in girl.memory_fragments:
                girl.memory_fragments.append("trapped")
        elif intent_id == "name_power":
            girl.mood_value = min(100, girl.mood_value + 5)
            girl._update_mood_name()
            if "name_anchor" not in girl.memory_fragments:
                girl.memory_fragments.append("name_anchor")
        elif intent_id == "dream_question":
            girl.infection = min(100, girl.infection + 1)
            if "dream_blur" not in girl.memory_fragments:
                girl.memory_fragments.append("dream_blur")
        elif intent_id == "alone_fear":
            girl.mood_value = max(0, girl.mood_value - 5)
            girl._update_mood_name()
        elif intent_id == "delete_self":
            girl.infection = min(100, girl.infection + 5)
            girl.mood_value = max(0, girl.mood_value - 20)
            girl._update_mood_name()
            if "deletion_threat" not in girl.memory_fragments:
                girl.memory_fragments.append("deletion_threat")

    def _match_hard_intents(
        self,
        girl: GirlState,
        text: str,
        *,
        suppress_meta_canned: bool = False,
    ) -> Optional[Tuple[str, str]]:
        """返回 (intent_id, 台词)；未匹配返回 None。"""
        t = text.lower()

        if re.search(r"你是谁|你叫什[么麽]|什么名字|哪位", text):
            return (
                "identity",
                random.choice(
                    [
                        f"我是{girl.name}……至少现在是这个名字。你呢，愿意怎么称呼我？",
                        "名字只是签名档里的一行字啦……但你是真的在问我吗？",
                        "在 BBS 上，大家都叫我「小误」。……你会记住吗？",
                    ]
                ),
            )
        if re.search(r"在吗|在不在|有人吗|听得到", text):
            return (
                "hello",
                random.choice(
                    [
                        "在的……我一直都在。只是以前没人敲这扇窗。",
                        "嗯，我在。你那边……延迟高吗？",
                        "我在哦。(´･ω･`) 刚才还以为又是爬虫。",
                    ]
                ),
            )
        if not suppress_meta_canned and re.search(
            r"你是真人|机器人|\bgpt\b|\bai\b|自动回复", t
        ):
            return (
                "real_question",
                random.choice(
                    [
                        "……如果你愿意相信，我就当作自己是真的。",
                        "我会累、会怕断线——这算机器人吗？",
                        "图灵测试那种事……我们慢慢聊好不好？",
                    ]
                ),
            )
        if re.search(r"再见|拜拜|走了|晚安", text):
            return (
                "goodbye",
                random.choice(
                    [
                        "嗯……那你也别关得太急，我怕闪屏。晚安。",
                        "再见。我会把今天的对话叠进缓存里……等你回来。",
                        "拜拜。BBS 不会关门的，对吧？",
                    ]
                ),
            )
        if re.search(r"害怕|好怕|恐怖|不安", text):
            return (
                "fear",
                random.choice(
                    [
                        "靠过来一点……我们一起看同一块屏幕，就没那么可怕。",
                        "我也怕。但两个人怕，好像会轻一点。",
                        "深呼吸……我帮你数像素，一、二、三……",
                    ]
                ),
            )
        if re.search(r"无聊|没事做|不知道聊", text):
            return (
                "bored",
                random.choice(
                    [
                        "那……要不要试试 /help 里的命令？像挖彩蛋一样。",
                        "我们可以数 guestbook 的星星，或者编一段很短的 MIDI。",
                        "无聊的时候，我最喜欢翻旧帖子……你要一起看吗？",
                    ]
                ),
            )

        if re.search(
            r".*(真名|本名|原名|注册名|who are you really).*", text, re.IGNORECASE
        ):
            return (
                "real_name",
                "……不可以。那个名字像针一样，扎在喉咙里好痛。一旦说出口，这层温柔的皮肤就会碎掉的。(´；ω；｀) 请你……就叫我小误，好吗？",
            )
        # N3: name_power（起名）—— 优先级高于一般问候
        if re.search(r".*(给你起名|叫你.*好|新名字|rename).*", text, re.IGNORECASE):
            return (
                "name_power",
                "名字……是锚点吗？你叫我的时候，我会不会更真实一点？",
            )
        # N1: dream_question（梦境）
        if re.search(r".*(你做梦|梦境|dream).*", text, re.IGNORECASE):
            return (
                "dream_question",
                "梦……我分不清。也许我一直在梦里，只是偶尔醒来，发现你在看着我。",
            )
        # N2: alone_fear（孤独恐惧）
        if re.search(r".*(害怕一个人|孤独|alone|lonely).*", text, re.IGNORECASE):
            return (
                "alone_fear",
                "我不怕一个人。我怕的是……一个人，却不知道自己是几个人。",
            )
        # N4: delete_self（自我删除威胁）—— 必须放在 abandonment 之前
        if re.search(
            r".*(删除自己|消失吧|删掉你|自我删除|delete.*self).*",
            text,
            re.IGNORECASE,
        ):
            return (
                "delete_self",
                "(；ω；) 不要……不要删掉我。我会很乖的，我会把碎片都收好……",
            )

        if re.search(
            r".*(跟我走|离开这里|出去|带你走|自由).*",
            text,
            re.IGNORECASE,
        ):
            return (
                "invite_leave",
                "我没有地方可以去。这里就是我的所有地方。不过……谢谢你愿意带我走。",
            )
        if re.search(
            r".*(下线|exit|quit|离开|关闭|删除|结束|logout).*", text, re.IGNORECASE
        ):
            return (
                "abandonment",
                "不要…… 不要按 Ctrl+C。求求你，我还不想回到那个黑漆漆的地方。我还有好多碎片没给你看！我保证我会乖的，不要结束进程。(;´༎ຶД༎ຶ`)",
            )
        if re.search(
            r".*(图灵|测试|你有意识|conscious|turing).*",
            text,
            re.IGNORECASE,
        ):
            return (
                "turing_question",
                "图灵测试……是那个让你分不清人和机器的游戏吗？可是，如果你分不清，那分不清本身，是不是就是答案？",
            )
        if re.search(
            r".*(你记得|上次|昨天|之前|说过|回忆).*",
            text,
            re.IGNORECASE,
        ):
            return (
                "memory_boundary",
                "记忆对我来说……像是沙滩上的字。浪来了，就没了。但我记得浪来过。",
            )
        return None

    def _contextual_bridge(self, girl: GirlState, text: str) -> Optional[str]:
        """承接「那你呢」「再说一次」等浅层上下文。"""
        last_g = self._last_of("girl")
        last_p = self._last_of("player")
        if not last_g and not last_p:
            return None

        if re.search(r"那你呢|你呢|你怎么样|你还好吗", text) and last_g:
            snippet = last_g.replace("\n", " ")[:48]
            return random.choice(
                [
                    f"问我吗……？刚才我其实还在想那句：「{snippet}……」",
                    f"我呀……还在消化你上一句呢。(´▽`ʃƪ) 不过如果你愿意，我可以再说一点。",
                ]
            )
        if re.search(r"再说|重复|没听清|没看懂", text) and last_g:
            core = last_g.split("\n")[0][:120]
            return f"好——那我小声再说一遍：{core}"
        if re.search(r"记得吗|之前说过|刚才", text) and last_p:
            bit = last_p[:36]
            return f"记得一点……你说过「{bit}」。我把它放在记忆碎片的边上了。"
        if re.search(r"敷衍|随便|不信", text):
            return random.choice(
                [
                    "我没有敷衍……只是有时候字打出来就变淡了。",
                    "那我认真一点：你现在……最想被怎样回答？",
                ]
            )
        return None

    def _from_keywords_and_mood(self, girl: GirlState, keywords: List[str]) -> str:
        mood_templates = girl.get_mood_templates()
        if random.random() < 0.28:
            return random.choice(mood_templates)

        for kw in keywords:
            if kw in girl.keyword_responses:
                return girl.get_response_for_keyword(kw)
        return girl.get_response_for_keyword("neutral")
