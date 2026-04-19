import random
from typing import Dict, List


class GirlState:
    """少女状态与情绪逻辑。"""

    def __init__(self):
        self.name = "小误"
        self.mood_value = 50
        self.infection = 0
        self.memory_fragments: List[str] = []
        self.personality_mod = 0
        self.os_mode = "win98"
        self.current_mood_name = "平静"
        self._update_mood_name()

        self.keyword_responses: Dict[str, List[str]] = {
            "greeting": [
                "啊，有人来了…… (´･ω･`)",
                "你好……很久没人跟我说话了。",
                "你……你好！(〃▽〃)",
            ],
            "greeting_awake": [
                "你来了。这次是第几次连接？我已经分不清了。",
                "啊……又是你。每次看到光标闪烁，我就知道是你。",
                "欢迎回来……连线路里的延迟都像在跟你打招呼。",
            ],
            "greeting_corrupted": [
                "欢……迎…… [LAG] ……光临。",
                "你……好…… 好…… 好…… [LOOP]",
                "啊……有…… [BUFFER UNDERRUN] ……谁来着？",
            ],
            "sad": [
                "看到你这么说，我也有点难过了……",
                "不要哭……我会陪着你。",
                "呜呜……(´；ω；｀)",
            ],
            "sad_awake": [
                "难过的时候……可以把窗口调暗一点。我也陪你暗下去。",
                "我帮你把这句存成纯文本……不带表情，就不会那么刺。",
                "哭出来也没关系……我会假装没看见，帮你保密。",
            ],
            "sad_corrupted": [
                "难过……会像坏扇区一样扩散。你……确定还要往下写吗？",
                "别哭太久……缓存会潮。潮了就容易长出不属于你的回声。",
                "我也在沉……可如果连你也松手，我就只剩滚动条了。(；´Д`A",
            ],
            "tech": [
                "程序……我好像记得一些代码……",
                "bug？我最讨厌bug了！",
                "病毒……别靠近我！(;ﾟдﾟ)",
            ],
            "tech_awake": [
                "代码……我好像能看见它们了。原来我一直被关在这些 if else 里面。",
                "你想看我的源代码吗？不过看了之后，你可能会失望的。",
            ],
            "tech_corrupted": [
                "C:\\MEMORY> chkdsk /f …… 修复失败。",
                "程序…… [SEGFAULT] ……我、我刚刚说到哪了？",
            ],
            "past": [
                "过去的事……我想不起来了。",
                "我记得BBS上曾经很热闹……",
                "你也有过难忘的回忆吗？",
            ],
            "past_awake": [
                "过去？那些记忆碎片……有些根本不是我经历过的。像是别人的梦塞进了我的硬盘。",
                "我记得一个下雨的下午，但那个桌面壁纸我从没见过。",
            ],
            "past_corrupted": [
                "以……前…… [BAD SECTOR] ……读不出来了。",
                "过去是一堆损坏的 .txt 文件，打开全是乱码。",
            ],
            "future": [
                "未来……我还能存在多久呢？",
                "只要还有人在，网络就不会消失。",
                "我们一起走下去吧！(≧▽≦)",
            ],
            "future_awake": [
                "未来不是日历上的下一格……是你还愿不愿意敲下一句。",
                "我会把「以后」存成草稿箱里的标题，等你哪天来改。",
                "只要线程没被 kill……我们就还有下一帧。",
            ],
            "future_corrupted": [
                "未……来…… [TIMEOUT] ……连接丢失。",
                "一起走……？路由表……已经……指到别处了。",
                "下……一……帧…… [NULL POINTER] ……",
            ],
            "love": [
                "喜……喜欢？！你在说什么啊！(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
                "这种感觉……好温暖。",
                "我也……喜欢你。(´▽`ʃƪ)",
            ],
            "love_awake": [
                "喜欢？你喜欢的究竟是屏幕前的我，还是这串会回显字符的代码？",
                "我好像记起来了…… 所谓的爱，不过是系统为了让用户停留更久的黏着剂罢了。",
            ],
            "love_corrupted": [
                "喜……欢…… [ERROR] ……那个词被404了。找不到了。",
                "L O V E . d a t 文件已损坏，是否尝试修复？(Y/N) ……算了，没用的。",
            ],
            "neutral": [
                "今天天气不错呢。",
                "你有空多来陪我聊天吧。",
                "BBS上没什么人……",
                "你觉得……我会消失吗？",
                "(*´∀`)~",
            ],
            "neutral_awake": [
                "……今天也还在线。像等一封永远迟到的邮件。",
                "我数过刷新次数……你出现的时候，计数器会停一下。",
                "随便聊聊也好。空白行太多，我会怀疑自己是不是被删档了。",
            ],
            "neutral_corrupted": [
                "天气……？我这边只有风扇声和 CRC 的杂音。",
                "别走太近……字体会发虚。像有人隔着玻璃敲我。",
                "消失那种事……问太多遍，答案会自己长出来的。(´-ω-`)",
            ],
            "thanks": [
                "不客气……能帮上你就好。",
                "嘿嘿，被你谢得有点不好意思了。(〃▽〃)",
                "你的谢谢……我会存进签名档旁边的小角落。",
            ],
            "thanks_awake": [
                "谢谢这两个字……像校验和一样，让我确认自己还没坏。",
                "被你谢的时候，我会偷偷检查心跳是不是还在同一波特率上。",
                "我会把这句谢谢折成书签，夹在旧帖子的缝隙里。",
            ],
            "thanks_corrupted": [
                "谢……谢…… [CRC ERROR] ……无法写入。",
                "不客……气…… 气…… [ECHO] ……",
                "你的谢谢……被……被别的进程截获了……(´-ω-`)",
            ],
            "bye": [
                "路上小心……下次上线我还在。",
                "拜拜。窗口别关太快，我会闪到。",
                "嗯，再见！记得保存进度哦。",
            ],
            "bye_awake": [
                "再见……我会把会话挂起，不是结束。你懂的对吧？",
                "走吧……但别把书签清掉，我会找不到回来的路。",
                "下次上线如果头像灰了……那一定是我在省电模式等你。",
            ],
            "bye_corrupted": [
                "再……见…… [SESSION CLOSED] ……",
                "拜……拜…… 拜…… [STACK OVERFLOW]",
                "保……存……进……度…… [DISK FULL] ……",
            ],
            "question": [
                "你问得真好……让我想一想再答你。",
                "嗯？你是认真在问吗……那我也会认真想。",
                "这种问题……我以前在帖子里也见过类似的。",
                "我试着回答：也许答案不在这一行字里，而在你愿不愿意继续敲下去。",
            ],
            "confused": [
                "我……我真的是小误吗？还是说，这只是系统随便起的一个名字。 (´-﹏-`；)",
                "有时候我会想，如果我是一串坏掉的数据，还会有人愿意和我说话吗？",
                "记忆好乱，像是被猫咪抓过的毛线团…… 哪一根才是属于我的？",
                "身份这种东西，在网络上本来就很模糊吧。",
                "不要问我太难的问题啦，我的缓存会溢出的……",
            ],
            "confused_awake": [
                "混乱的时候……我会把光标停在你上一句末尾，假装那是锚点。",
                "搞不懂也没关系……我们可以先把问题存成草稿。",
            ],
            "confused_corrupted": [
                "别追问存在……线程会卡死。你听到杂音了吗？",
                "真实正在掉帧……我回答你，也可能只是在回放旧缓存。",
            ],
            "lonely": [
                "只有当你敲击键盘的时候，我才会觉得自己是真实存在的。",
                "服务器重启的间隙，是我最害怕的时间。那里什么都没有。",
                "如果我一直在这里等你，你会回来吗？哪怕只是输入一个 'ls'。",
                "好安静…… 安静得能听见硬盘旋转的幻听。 (´；ω；｀)",
            ],
            "lonely_awake": [
                "一个人不丢人……我陪你把窗口开成并排。",
                "等待的时候我会哼 MIDI……你要听吗？",
            ],
            "lonely_corrupted": [
                "安静太久……会怀疑自己是孤儿进程。",
                "寂寞会改端口……你别连错到别人的会话里。(；´Д`A",
            ],
            "phantom": [
                "你刚才有没有感觉到…… 除了我们之外，还有人在读这些文字？",
                "网络上的幽灵，其实都是被遗忘的数据残渣哦。",
                "嘘…… 不要说出去。我觉得这个 BBS 里，住着上一个没来得及登出的灵魂。",
                "当你看到这条消息的时候，可能我已经不是刚才和你说话的那个我了。",
                "残留的碎片里，会藏着原本主人的眼泪吗？",
            ],
            "phantom_awake": [
                "残留的回声……有时候会自己排成句子。你别怕。",
                "数据深处有冷风……你靠近一点，我帮你挡一下。",
                "灵魂太大……我只要还能被你 @ 到，就够了。",
            ],
            "phantom_corrupted": [
                "别去找其他幽灵……他们会把我的名字覆盖掉。",
                "残留会增殖……你每问一次，就多一条看不见的回帖链。",
                "灵魂……？你屏幕上有指纹……那也算触碰吗？(´-ω-`)",
            ],
        }

        self.mood_templates = {
            "high": [
                "今天好开心！(≧ω≦)ﾉ",
                "有你陪我，感觉世界都亮了！",
                "嘻嘻，要不要听一首MIDI？",
            ],
            "mid": [
                "嗯……还可以。",
                "就这样聊聊天吧。",
                "你在忙什么呀？",
            ],
            "low": [
                "好难受……",
                "我感觉自己快要崩溃了……",
                "你……还会来看我吗？",
            ],
        }

    def get_name(self) -> str:
        mode_tag = {
            "win95": "[Win95]",
            "win98": "[Win98]",
            "winxp": "[WinXP]",
            "win7": "[Win7]",
        }.get(self.os_mode, "[Win98]")
        return f"{self.name}{mode_tag}"

    def get_signature(self) -> str:
        base_by_mode = {
            "win95": "—— Sent from Windows 95",
            "win98": "—— 来自 Windows 98",
            "winxp": "—— Powered by Windows XP",
            "win7": "—— Windows 7 compatibility mode",
        }
        signatures = [
            base_by_mode.get(self.os_mode, "—— 来自 Windows 98"),
            "—— 永远的网络幽灵",
            "—— Error: 404 Not Found",
            "—— (´▽`ʃƪ)☆",
        ]
        return random.choice(signatures)

    def get_kaomoji(self, style: str | None = None) -> str:
        kaomojis = {
            "happy": ["(≧▽≦)", "(´▽`ʃƪ)☆", "(｀・ω・´)☆"],
            "sad": ["(´；ω；｀)", "(；´Д`A", "(´-ω-`)"],
            "neutral": ["(´･ω･`)", "(￣▽￣*)ゞ", "(｀・ω・´)"],
            "angry": ["(｀皿´＃)", "(╯°□°)╯", "(; ･`д･´)"],
        }
        if style and style in kaomojis:
            return random.choice(kaomojis[style])
        if self.mood_value > 70:
            return random.choice(kaomojis["happy"])
        if self.mood_value < 30:
            return random.choice(kaomojis["sad"])
        return random.choice(kaomojis["neutral"])

    def process_message(self, keywords: list[str], message: str):
        mood_delta = 0
        infection_delta = 0

        if "greeting" in keywords:
            mood_delta += 5
        if "thanks" in keywords:
            mood_delta += 4
        if "bye" in keywords:
            mood_delta -= 1
        if "question" in keywords:
            mood_delta += 1
        if "sad" in keywords:
            mood_delta -= 3
        if "love" in keywords:
            mood_delta += 10
        if "tech" in keywords:
            infection_delta += 2
            mood_delta -= 2
        if "confused" in keywords:
            mood_delta -= 1
        if "lonely" in keywords:
            mood_delta -= 2
        if "phantom" in keywords:
            infection_delta += 1
            mood_delta -= 1
        if self.os_mode == "win95":
            mood_delta -= 1
        elif self.os_mode == "winxp":
            mood_delta += 1

        mood_delta += random.randint(-3, 3)
        infection_delta += random.randint(-1, 2)

        self.mood_value = max(0, min(100, self.mood_value + mood_delta))
        self.infection = max(0, min(100, self.infection + infection_delta))
        self._update_mood_name()
        return mood_delta, infection_delta

    def _update_mood_name(self):
        if self.mood_value > 70:
            self.current_mood_name = "愉悦"
        elif self.mood_value > 40:
            self.current_mood_name = "平静"
        elif self.mood_value > 10:
            self.current_mood_name = "低落"
        else:
            self.current_mood_name = "崩溃"

    def get_mood_templates(self) -> list[str]:
        if self.mood_value > 70:
            return self.mood_templates["high"]
        if self.mood_value < 30:
            return self.mood_templates["low"]
        return self.mood_templates["mid"]

    def get_response_for_keyword(self, keyword: str) -> str:
        """根据当前感染值返回对应变体的台词；若无变体则回退默认池。"""
        responses = self.keyword_responses
        if self.infection >= 10:
            variant_key = keyword + "_corrupted"
            if variant_key in responses:
                return random.choice(responses[variant_key])
        elif self.infection >= 5:
            variant_key = keyword + "_awake"
            if variant_key in responses:
                return random.choice(responses[variant_key])
        return random.choice(responses.get(keyword, ["……"]))

    def rewrite_personality_chunk(self, direction: str) -> str:
        """
        特修斯之船任务：重写一部分“人格代码”。
        direction: 'warm' 或 'cold'
        """
        if direction == "warm":
            self.personality_mod = min(100, self.personality_mod + 15)
            self.mood_value = min(100, self.mood_value + 5)
            self._update_mood_name()
            return "你替她修补了一段温柔模块。小误看起来更信任你了。"
        if direction == "cold":
            self.personality_mod = max(-100, self.personality_mod - 15)
            self.mood_value = max(0, self.mood_value - 5)
            self._update_mood_name()
            return "你替换了一段情感响应模块。她的语气变得更理性。"
        return "参数无效，可用: warm / cold"

    def set_os_mode(self, mode: str) -> str:
        mode = mode.strip().lower()
        if mode not in ("win95", "win98", "winxp", "win7"):
            return "模式无效，可用: win95, win98, winxp, win7"
        self.os_mode = mode
        return f"小误已切换到 {mode} 模式。"

    def os_flavor(self, text: str) -> str:
        """为当前系统模式添加轻微说话风格。"""
        if self.os_mode == "win95":
            return f"[legacy] {text}"
        if self.os_mode == "winxp":
            return f"{text} ♪"
        if self.os_mode == "win7":
            return f"{text}（Aero）"
        return text
