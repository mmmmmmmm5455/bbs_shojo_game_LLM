import pygame
import os

class SoundEffectManager:
    """
    音效管理器类，负责加载和播放音效
    """
    def __init__(self):
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            except pygame.error:
                pygame.mixer.init()
        self.sounds = {}
        self.default_volume = 0.5
        
    def load_sound(self, name, sound_path):
        """加载音效文件"""
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(self.default_volume)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"加载音效失败 {sound_path}: {e}")
            return False
            
    def play_sound(self, name):
        """播放指定名称的音效"""
        if name in self.sounds:
            self.sounds[name].play()
            return True
        return False
        
    def set_volume(self, volume):
        """设置所有音效的音量（0-1）"""
        self.default_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.default_volume)
            
    def stop_all(self):
        """停止所有正在播放的音效"""
        pygame.mixer.stop()

# 预设的音效与表情映射
DEFAULT_EMOTION_SOUNDS = {
    "happy": "assets/sounds/happy.wav",
    "sad": "assets/sounds/sad.wav",
    "surprised": "assets/sounds/surprised.wav",
    "shy": "assets/sounds/shy.wav",
    "angry": "assets/sounds/angry.wav",
    "default": "assets/sounds/default.wav"
}

def create_default_sound_files():
    """创建默认的音效文件（如果不存在的话）"""
    # 注意：实际项目中应该有真实的音效文件，这里只是示例
    os.makedirs("assets/sounds", exist_ok=True)
    
    # 创建一些简单的音效（使用pygame生成简单的声音）
    if not os.path.exists("assets/sounds/happy.wav"):
        # 生成一个简单的欢快音效
        sample_rate = 44100
        duration = 0.5
        freq = 440
        
        # 生成正弦波
        import numpy as np
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        
        # 转换为16位整数
        wave = (wave * 32767).astype(np.int16)
        
        # 保存为wav文件
        import wave
        with wave.open("assets/sounds/happy.wav", 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wave.tobytes())
    
    # 其他音效可以类似创建，这里只创建一个示例

if __name__ == "__main__":
    # 测试音效管理器
    create_default_sound_files()
    
    manager = SoundEffectManager()
    manager.load_sound("happy", "assets/sounds/happy.wav")
    
    print("播放欢快音效...")
    manager.play_sound("happy")
    import time
    time.sleep(1)