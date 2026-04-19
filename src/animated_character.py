from ascii_animation import ASCIIAnimation
from sound_effect import SoundEffectManager
import time

class AnimatedCharacter:
    """
    带音效的ASCII动画角色类，结合了ASCII表情动画和音效联动
    """
    def __init__(self):
        self.animation = ASCIIAnimation()
        self.sound_manager = SoundEffectManager()
        self.emotion_sounds = {
            "happy": "happy",
            "sad": "sad",
            "surprised": "surprised",
            "shy": "shy",
            "angry": "angry"
        }
        self.last_played_emotion = None
        
        # 加载默认音效
        self._load_default_sounds()
        
    def _load_default_sounds(self):
        """加载默认的音效文件"""
        for emotion, sound_name in self.emotion_sounds.items():
            sound_path = f"assets/sounds/{sound_name}.wav"
            self.sound_manager.load_sound(emotion, sound_path)
            
    def set_emotion(self, emotion):
        """设置角色表情，自动播放对应的音效"""
        if self.animation.set_animation(emotion):
            # 如果表情变化，播放对应的音效
            if emotion != self.last_played_emotion:
                self.sound_manager.play_sound(emotion)
                self.last_played_emotion = emotion
            return True
        return False
    
    def update(self):
        """更新动画帧"""
        self.animation.update()
        
    def get_current_frame(self):
        """获取当前帧的ASCII文本"""
        return self.animation.get_current_frame()
    
    def set_frame_delay(self, delay):
        """设置每帧延迟时间"""
        self.animation.set_frame_delay(delay)
        
    def set_emotion_sound(self, emotion, sound_name):
        """设置特定表情的音效"""
        if emotion in self.emotion_sounds:
            self.emotion_sounds[emotion] = sound_name
            return True
        return False

def test_animated_character():
    """测试带音效的ASCII动画角色"""
    character = AnimatedCharacter()
    character.set_frame_delay(0.2)
    
    emotions = ["happy", "sad", "surprised", "shy", "angry"]
    current_emotion_index = 0
    
    print("测试带音效的ASCII动画角色")
    print("按任意键切换表情，按q退出")
    
    import sys
    import select
    
    start_time = time.time()
    while True:
        # 检查键盘输入
        if sys.stdin.isatty():
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                key = sys.stdin.read(1).lower()
                if key == 'q':
                    break
                # 切换表情
                current_emotion_index = (current_emotion_index + 1) % len(emotions)
                character.set_emotion(emotions[current_emotion_index])
        
        # 更新动画
        character.update()
        
        # 清屏并显示
        print("\033[H")
        print("\033[J")
        print(f"当前表情: {emotions[current_emotion_index]}")
        print("-" * 20)
        print(character.get_current_frame())
        print("-" * 20)
        print("按任意键切换表情，按q退出")
        
        time.sleep(0.05)

if __name__ == "__main__":
    test_animated_character()