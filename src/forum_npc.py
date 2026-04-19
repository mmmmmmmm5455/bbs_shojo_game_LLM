import pygame
import time
import random
from typing import List, Dict, Tuple, Optional

class ForumNPC:
    """
    论坛NPC类，代表其他网友
    隐喻：网络社区中的个体，有不同的性格和行为模式
    """
    def __init__(self, npc_id: int):
        self.npc_id = npc_id
        self.personality = self._random_personality()
        self.name = self._generate_name()
        self.avatar = self._generate_avatar()
        self.opinion_on_character = 50.0  # 对少女的看法，0-100
        self.post_count = 0
        self.last_active = time.time()
        self.active_cooldown = random.randint(30, 120)  # 下次活动时间间隔
        
    def _random_personality(self) -> Dict:
        """随机生成性格"""
        personalities = [
            {
                "type": "normal",
                "name": "普通网友",
                "post_style": "normal",
                "opinion_change": 0.5,
                "color": (255, 255, 255)
            },
            {
                "type": "troll",
                "name": "杠精",
                "post_style": "troll",
                "opinion_change": -2.0,
                "color": (255, 100, 100)
            },
            {
                "type": "poet",
                "name": "诗人",
                "post_style": "poetry",
                "opinion_change": 1.0,
                "color": (100, 255, 100)
            },
            {
                "type": "silent",
                "name": "潜水员",
                "post_style": "silent",
                "opinion_change": 0.1,
                "color": (150, 150, 150)
            },
            {
                "type": "supporter",
                "name": "支持者",
                "post_style": "support",
                "opinion_change": 2.0,
                "color": (100, 100, 255)
            }
        ]
        return random.choice(personalities)
        
    def _generate_name(self) -> str:
        """生成随机用户名"""
        prefixes = ["小", "阿", "老", "大", "云", "风", "雨", "雪", "星", "月"]
        suffixes = ["猫", "狗", "鸟", "鱼", "兔", "虎", "龙", "凤", "花", "草"]
        numbers = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        
        return random.choice(prefixes) + random.choice(suffixes) + random.choice(numbers)
        
    def _generate_avatar(self) -> str:
        """生成随机头像ASCII艺术"""
        avatars = [
            "(◕‿◕)",
            "(≧ω≦)",
            "(⊙ω⊙)",
            "(╥ω╥)",
            "(✧ω✧)",
            "(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
            "(◕w◕)",
            "(≧▽≦)",
            "(｀ω´)",
            "(╬ω╬)"
        ]
        return random.choice(avatars)
        
    def generate_post(self, character_mood: str, memory_fragments: int) -> str:
        """根据性格和当前情况生成帖子"""
        style = self.personality["post_style"]
        
        if style == "normal":
            return self._generate_normal_post(character_mood, memory_fragments)
        elif style == "troll":
            return self._generate_troll_post(character_mood, memory_fragments)
        elif style == "poetry":
            return self._generate_poetry_post(character_mood, memory_fragments)
        elif style == "support":
            return self._generate_support_post(character_mood, memory_fragments)
        else:  # silent
            return ""
            
    def _generate_normal_post(self, character_mood: str, memory_fragments: int) -> str:
        """生成普通帖子"""
        moods = {
            "happy": "今天心情真好呀～",
            "sad": "好像有点难过呢…",
            "angry": "今天有点生气…",
            "surprised": "哇，发生了什么事？",
            "shy": "不好意思…",
            "neutral": "今天和平常一样呢。"
        }
        base_mood = moods.get(character_mood, "今天天气不错。")
        
        posts = [
            f"{base_mood} 大家有没有遇到过类似的事情？",
            f"今天在BBS上看到很多有趣的帖子呢～",
            f"我觉得这个话题很有意思，大家怎么看？",
            f"{memory_fragments}个记忆碎片，感觉离真相越来越近了呢…"
        ]
        return random.choice(posts)
        
    def _generate_troll_post(self, character_mood: str, memory_fragments: int) -> str:
        """生成杠精帖子"""
        troll_posts = [
            f"切，这有什么好讨论的？",
            f"{memory_fragments}？你是不是在骗人啊？",
            f"这帖子也太水了吧，不如去写代码吧～",
            f"你们这些人就是闲的没事干。"
        ]
        return random.choice(troll_posts)
        
    def _generate_poetry_post(self, character_mood: str, memory_fragments: int) -> str:
        """生成诗歌风格帖子"""
        poems = [
            f"月光洒在BBS上，/ 记忆碎片在闪烁，/ 我们在这里相遇，/ 等待着未来的曙光。",
            f"键盘敲击的声音，/ 是心灵的对话，/ 虽然隔着屏幕，/ 却能感受到彼此的温度。",
            f"{memory_fragments}个像素，/ 组成了我们的世界，/ 每一个都承载着，/ 我们的故事和回忆。"
        ]
        return random.choice(poems)
        
    def _generate_support_post(self, character_mood: str, memory_fragments: int) -> str:
        """生成支持帖子"""
        moods = {
            "happy": "今天心情真好呀～",
            "sad": "别灰心，会好起来的…",
            "angry": "消消气，喝点水吧。",
            "surprised": "哇，真有活力！",
            "shy": "慢慢來，不着急的～",
            "neutral": "今天也不错呢。",
        }
        base_mood = moods.get(character_mood, "一起加油吧！")
        supports = [
            "加油！我相信你一定可以的！",
            f"{base_mood} 大家都支持你！",
            f"{memory_fragments}个记忆碎片，每一个都很珍贵呢～",
            "看到你这么努力，我也很开心！",
        ]
        return random.choice(supports)
        
    def react_to_post(self, player_post: str, character_mood: str) -> Tuple[str, float]:
        """对玩家的帖子做出反应"""
        # 根据性格和内容调整看法
        opinion_change = 0.0
        
        if "help" in player_post.lower() or "救" in player_post:
            opinion_change += self.personality["opinion_change"] * 2
        elif "happy" in player_post.lower() or "开心" in player_post:
            opinion_change += self.personality["opinion_change"]
        elif "sad" in player_post.lower() or "难过" in player_post:
            opinion_change -= self.personality["opinion_change"]
            
        # 更新看法
        self.opinion_on_character = max(0, min(100, self.opinion_on_character + opinion_change))
        
        # 生成反应
        if self.personality["type"] == "troll":
            reaction = random.choice([
                f"{self.name}: 哼，这有什么用？",
                f"{self.name}: 说得比唱的好听。"
            ])
        elif self.personality["type"] == "poet":
            reaction = f"{self.name}: {player_post}… 真是一首美丽的诗呢。"
        elif self.personality["type"] == "supporter":
            reaction = f"{self.name}: 太棒了！我支持你！"
        else:
            reaction = f"{self.name}: 说得不错呢。"
            
        return reaction, opinion_change
        
    def update(self, current_time: float, character_mood: str, memory_fragments: int):
        """更新NPC状态"""
        if current_time - self.last_active >= self.active_cooldown:
            self.last_active = current_time
            self.active_cooldown = random.randint(30, 120)
            self.post_count += 1
            return self.generate_post(character_mood, memory_fragments)
        return None

def test_forum_npc():
    """测试论坛NPC"""
    npc = ForumNPC(1)
    print(f"NPC名称: {npc.name}")
    print(f"性格: {npc.personality['name']}")
    print(f"头像: {npc.avatar}")
    
    while True:
        post = npc.generate_post("happy", 50)
        print(f"\n帖子: {post}")
        time.sleep(2)

if __name__ == "__main__":
    test_forum_npc()