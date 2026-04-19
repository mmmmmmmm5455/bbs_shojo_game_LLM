import os
import time
import random
import pygame
from typing import Dict, Optional, List

from ascii_animation_system import ASCIIAnimation, ASCIIArtConverter
from game_paths import ASSETS_DIR

class AdvancedAnimatedCharacter:
    """
    高级带音效的ASCII动画角色类，结合了ASCII表情动画、音效联动和动态反应
    隐喻：声音与表情的联动，如同真实的情感表达
    """
    def __init__(self):
        self.animation = ASCIIAnimation()
        self.ascii_converter = ASCIIArtConverter()
        self.sound_manager = self._init_sound_manager()
        self.emotion_sounds: Dict[str, List[str]] = {
            "happy": ["happy1.wav", "happy2.wav", "laugh.wav"],
            "sad": ["sad1.wav", "sad2.wav", "cry.wav"],
            "surprised": ["surprise1.wav", "wow.wav", "shock.wav"],
            "shy": ["shy1.wav", "blush.wav"],
            "angry": ["angry1.wav", "angry2.wav", "growl.wav"],
            "blush": ["blush1.wav", "embarrassed.wav"],
            "wink": ["wink1.wav", "tease.wav"]
        }
        self.current_emotion = "happy"
        self.last_played_sound = None
        self.sound_cooldown = 0.0
        self.current_sound_index = 0
        self.muted = False
        
        # 情绪强度，0-100，影响音效和动画
        self.emotion_intensity: Dict[str, float] = {
            "happy": 50.0,
            "sad": 50.0,
            "surprised": 50.0,
            "shy": 50.0,
            "angry": 50.0,
            "blush": 50.0,
            "wink": 50.0
        }
        
        # 加载默认音效
        self._load_default_sounds()
        
    def _init_sound_manager(self):
        """初始化音效管理器"""
        try:
            from sound_effect import SoundEffectManager
            return SoundEffectManager()
        except ImportError:
            print("警告：sound_effect模块未找到，音效功能将不可用")
            return None
            
    def _load_default_sounds(self):
        """加载默认的音效文件"""
        if not self.sound_manager:
            return
            
        # 加载所有表情的音效
        for emotion, sound_files in self.emotion_sounds.items():
            for sound_file in sound_files:
                sound_path = os.path.join(ASSETS_DIR, "sounds", emotion, sound_file)
                if not os.path.isfile(sound_path):
                    continue
                self.sound_manager.load_sound(f"{emotion}_{sound_file}", sound_path)
                
    def set_emotion(self, emotion: str, intensity: Optional[float] = None) -> bool:
        """设置角色表情和强度，自动播放对应的音效"""
        if self.animation.set_animation(emotion):
            self.current_emotion = emotion
            if intensity is not None:
                self.emotion_intensity[emotion] = max(0.0, min(100.0, intensity))
                
            # 如果不在冷却期，播放音效
            if time.time() > self.sound_cooldown and not self.muted:
                self._play_emotion_sound()
                
            return True
        return False
    
    def _play_emotion_sound(self):
        """播放当前表情的音效"""
        if not self.sound_manager:
            return
            
        # 随机选择一个音效，避免重复
        available_sounds = self.emotion_sounds.get(self.current_emotion, [])
        if not available_sounds:
            return
            
        # 选择下一个音效，循环使用
        sound_name = f"{self.current_emotion}_{available_sounds[self.current_sound_index]}"
        self.current_sound_index = (self.current_sound_index + 1) % len(available_sounds)
        
        # 根据情绪强度调整音量
        intensity = self.emotion_intensity[self.current_emotion] / 100.0
        if self.sound_manager:
            self.sound_manager.set_volume(intensity)
            self.sound_manager.play_sound(sound_name)
            
        self.last_played_sound = sound_name
        self.sound_cooldown = time.time() + 1.0  # 1秒冷却时间
        
    def update(self, delta_time: float = 0.0):
        """更新动画帧和音效状态"""
        self.animation.update()
        if delta_time > 0:
            self.sound_cooldown -= delta_time
            
    def get_current_frame(self) -> str:
        """获取当前帧的ASCII文本"""
        return self.animation.get_current_frame()
    
    def set_frame_delay(self, delay: float):
        """设置每帧延迟时间"""
        self.animation.set_frame_delay(delay)
        
    def add_emotion_sound(self, emotion: str, sound_files: List[str]):
        """添加特定表情的音效"""
        self.emotion_sounds[emotion] = sound_files
        if self.sound_manager:
            for sound_file in sound_files:
                sound_path = os.path.join(ASSETS_DIR, "sounds", emotion, sound_file)
                if os.path.isfile(sound_path):
                    self.sound_manager.load_sound(f"{emotion}_{sound_file}", sound_path)
                
    def react_to_text(self, text: str):
        """根据输入的文本内容做出反应"""
        text_lower = text.lower()
        
        # 关键词触发表情变化
        triggers = {
            "happy": ["happy", "开心", "高兴", "笑", "funny", "good"],
            "sad": ["sad", "难过", "伤心", "cry", "bad", "sorry"],
            "surprised": ["surprise", "惊讶", "wow", "oh", "what", "really"],
            "angry": ["angry", "生气", "mad", "hate", "stop", "怒"],
            "shy": ["shy", "害羞", "embarrassed", "不好意思", "腼腆"],
        }
        
        for emotion, keywords in triggers.items():
            if any(keyword in text_lower for keyword in keywords):
                self.set_emotion(emotion)
                return
                
        # 默认反应
        self.set_emotion("happy")
        
    def mute(self, muted: bool = True):
        """静音/取消静音"""
        self.muted = muted
        if self.sound_manager:
            # 如果静音，播放电流底噪
            if muted:
                self.sound_manager.play_sound("background_noise")
            else:
                self.sound_manager.stop_all()
                
    def is_muted(self) -> bool:
        """检查是否静音"""
        return self.muted

def test_advanced_character():
    """测试高级带音效的ASCII动画角色"""
    character = AdvancedAnimatedCharacter()
    character.set_frame_delay(0.15)
    
    print("高级带音效的ASCII动画角色测试")
    print("输入任意文字，角色会根据内容做出反应")
    print("输入q退出")
    
    import sys
    import select
    
    start_time = time.time()
    while True:
        delta_time = time.time() - start_time
        start_time = time.time()
        
        character.update(delta_time)
        
        # 检查键盘输入
        if sys.stdin.isatty():
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                input_line = sys.stdin.readline().strip()
                if input_line.lower() == 'q':
                    break
                # 角色对输入做出反应
                character.react_to_text(input_line)
                print(f"角色反应: {input_line}")
        
        # 清屏并显示
        print("\033[H")
        print("\033[J")
        print(f"当前表情: {character.current_emotion}")
        print(f"情绪强度: {character.emotion_intensity[character.current_emotion]:.1f}%")
        print("-" * 40)
        print(character.get_current_frame())
        print("-" * 40)
        print("输入任意文字，角色会根据内容做出反应")
        print("输入q退出")
        
        time.sleep(0.05)

if __name__ == "__main__":
    test_advanced_character()