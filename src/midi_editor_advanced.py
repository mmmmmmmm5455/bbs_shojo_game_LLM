import os
import pygame
import mido
import time
import re
import random
import tempfile
from io import BytesIO
from typing import Dict, List, Tuple, Optional

from game_fonts import get_ui_font

class MIDISequencer:
    """
    MIDI音序器类，负责播放MIDI音乐
    隐喻受限的诗意：用最少的字节表达最丰富的情感
    """
    def __init__(self):
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            except pygame.error:
                pygame.mixer.init()
        self.current_midi = None
        self.current_channel = 0
        self.volume = 100
        self.instruments: Dict[int, str] = {
            0: "钢琴",
            1: "电钢琴",
            24: "尼龙吉他",
            33: "大提琴",
            40: "小提琴",
            73: "音色号",
            80: "单簧管",
            112: "钟声"
        }
        self.current_instrument = 0
        self.muted = False
        self.noise_sound = None
        self._midi_work_path = os.path.join(
            tempfile.gettempdir(), f"bbs_shojo_{os.getpid()}_temp.mid"
        )
        self._init_noise_sound()
        
    def _init_noise_sound(self):
        """初始化电流底噪声音"""
        try:
            # 创建简单的白噪音
            sample_rate = 44100
            duration = 0.5
            wave = []
            for _ in range(int(sample_rate * duration)):
                wave.append(random.randint(-100, 100))
            wave = bytes(wave)
            
            self.noise_sound = pygame.mixer.Sound(buffer=wave)
            self.noise_sound.set_volume(0.3)
        except:
            self.noise_sound = None
            
    def load_midi(self, midi_data):
        """加载MIDI数据"""
        if self.current_midi:
            pygame.mixer.music.stop()
        
        with open(self._midi_work_path, "wb") as f:
            f.write(midi_data)
        pygame.mixer.music.load(self._midi_work_path)
        self.current_midi = self._midi_work_path
        
    def play(self):
        """播放MIDI音乐"""
        if self.current_midi and not self.muted:
            pygame.mixer.music.set_volume(self.volume / 100.0)
            pygame.mixer.music.play()
            
    def pause(self):
        """暂停播放"""
        if self.current_midi:
            pygame.mixer.music.pause()
            
    def resume(self):
        """恢复播放"""
        if self.current_midi and not self.muted:
            pygame.mixer.music.unpause()
            
    def stop(self):
        """停止播放"""
        if self.current_midi:
            pygame.mixer.music.stop()
            if self.noise_sound:
                self.noise_sound.stop()
        
    def set_volume(self, volume):
        """设置音量（0-100）"""
        self.volume = max(0, min(100, volume))
        pygame.mixer.music.set_volume(self.volume / 100)
        if self.noise_sound:
            self.noise_sound.set_volume(0.3 * (self.volume / 100))
            
    def set_instrument(self, instrument_id: int):
        """设置当前乐器"""
        self.current_instrument = max(0, min(127, instrument_id))
        
    def get_instrument_name(self, instrument_id: Optional[int] = None) -> str:
        """获取乐器名称"""
        if instrument_id is None:
            instrument_id = self.current_instrument
        return self.instruments.get(instrument_id, f"未知乐器({instrument_id})")
        
    def mute(self, muted: bool = True):
        """静音/取消静音"""
        self.muted = muted
        if muted:
            pygame.mixer.music.pause()
            if self.noise_sound:
                self.noise_sound.play(-1)  # 循环播放底噪
        else:
            pygame.mixer.music.unpause()
            if self.noise_sound:
                self.noise_sound.stop()

class AdvancedScoreConverter:
    """
    高级简谱到MIDI的转换器，支持更多格式和命令
    隐喻受限的诗意：限制催生创造力
    """
    # 简谱音符到MIDI音符号的映射（C4为中央C，编号60）
    BASE_NOTES = {
        '1': 60,  # C4 - do
        '2': 62,  # D4 - re
        '3': 64,  # E4 - mi
        '4': 65,  # F4 - fa
        '5': 67,  # G4 - sol
        '6': 69,  # A4 - la
        '7': 71,  # B4 - si
        '0': 0,   # 休止符
    }
    
    # 时值映射（以四分音符为1拍，每分钟120拍）
    DURATION_MAP = {
        'w': 4.0,   # 全音符
        'h': 2.0,    # 二分音符
        'q': 1.0, # 四分音符
        'e': 0.5,  # 八分音符
        's': 0.25, # 十六分音符
        'whole': 4.0,
        'half': 2.0,
        'quarter': 1.0,
        'eighth': 0.5,
        'sixteenth': 0.25,
    }
    
    # 音符名称到MIDI音符号的映射
    NOTE_NAME_MAP = {
        'C': 60, 'C#': 61, 'Db': 61,
        'D': 62, 'D#': 63, 'Eb': 63,
        'E': 64, 'F': 65, 'F#': 66,
        'Gb': 66, 'G': 67, 'G#': 68,
        'Ab': 68, 'A': 69, 'A#': 70,
        'Bb': 70, 'B': 71,
    }
    
    def __init__(self, tempo=120):
        self.tempo = tempo  # 每分钟节拍数
        self.tick_per_beat = 480  # 每拍的tick数
        self.instrument_mappings = {
            "happy": [0, 24, 73],  # 钢琴、尼龙吉他、音色号
            "sad": [33, 40, 112],   # 大提琴、小提琴、钟声
            "angry": [1, 80],        # 电钢琴、单簧管
            "surprised": [73, 112],  # 音色号、钟声
            "shy": [0, 24],         # 钢琴、尼龙吉他
        }
        
    def parse_note_command(self, command: str) -> Tuple[int, float]:
        """解析note命令，如 note C4 1/4 或 note C#5 q"""
        parts = command.strip().split()
        if len(parts) < 3:
            raise ValueError("命令格式错误，应为：note <音符> <时值>")
            
        # 解析音符
        note_name = parts[1].upper()
        octave = 4
        # 分离音名和八度
        if len(note_name) >= 2 and note_name[1] in '#b':
            note = note_name[:2]
            octave = int(note_name[2:]) if len(note_name) > 2 else 4
        else:
            note = note_name[0]
            octave = int(note_name[1:]) if len(note_name) > 1 else 4
            
        if note not in self.NOTE_NAME_MAP:
            raise ValueError(f"未知音符: {parts[1]}")
            
        midi_note = self.NOTE_NAME_MAP[note] + (octave - 4) * 12
        
        # 解析时值
        duration_str = parts[2].lower()
        if '/' in duration_str:
            num, den = map(int, duration_str.split('/'))
            duration = 4.0 / den * num
        elif duration_str in self.DURATION_MAP:
            duration = self.DURATION_MAP[duration_str]
        else:
            try:
                duration = float(duration_str)
            except ValueError:
                raise ValueError(f"未知时值: {parts[2]}")
                
        return midi_note, duration
        
    def parse_score(self, score_text: str) -> List[Tuple[str, int, float]]:
        """
        解析简谱或命令文本，返回MIDI消息列表
        支持格式：
        - 简谱：1 2 3 4 5 6 7
        - 命令：note C4 1/4
        - 乐器切换：instrument 0
        - 速度设置：tempo 120
        """
        messages = []
        current_time = 0
        current_instrument = 0
        tempo = self.tempo
        
        # 分割命令
        commands = re.split(r'\s+|\n', score_text.strip())
        commands = [cmd for cmd in commands if cmd]
        
        i = 0
        while i < len(commands):
            cmd = commands[i].lower()
            
            if cmd == 'note':
                # note命令格式：note C4 1/4
                if i + 2 < len(commands):
                    try:
                        midi_note, duration = self.parse_note_command(f"note {commands[i+1]} {commands[i+2]}")
                        messages.append(('note_on', current_time, midi_note, 64))
                        current_time += self._duration_to_ticks(duration, tempo)
                        messages.append(('note_off', current_time, midi_note, 64))
                        i += 3
                    except Exception as e:
                        print(f"解析note命令失败: {e}")
                        i += 1
                else:
                    i += 1
                    
            elif cmd == 'instrument':
                # 切换乐器：instrument 0
                if i + 1 < len(commands):
                    try:
                        current_instrument = int(commands[i+1])
                        messages.append(('instrument', current_time, current_instrument))
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    i += 1
                    
            elif cmd == 'tempo':
                # 设置速度：tempo 120
                if i + 1 < len(commands):
                    try:
                        tempo = int(commands[i+1])
                        messages.append(('tempo', current_time, tempo))
                        self.tempo = tempo
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    i += 1
                    
            elif cmd.isdigit() or cmd in self.BASE_NOTES:
                # 简谱音符
                note_token = cmd
                if note_token in self.BASE_NOTES:
                    midi_note = self.BASE_NOTES[note_token]
                    duration = self.DURATION_MAP['quarter']
                    messages.append(('note_on', current_time, midi_note, 64))
                    current_time += self._duration_to_ticks(duration, tempo)
                    messages.append(('note_off', current_time, midi_note, 64))
                i += 1
                
            else:
                i += 1
                
        return messages
        
    def create_midi(self, score_text: str, instrument: int = 0) -> bytes:
        """将简谱或命令转换为MIDI文件数据"""
        midi_messages = []
        current_time = 0
        
        # 解析所有消息
        parsed_messages = self.parse_score(score_text)
        
        # 处理消息
        for msg_type, time, *params in parsed_messages:
            if msg_type == 'note_on':
                note, velocity = params
                delay = time - current_time
                current_time = time
                midi_messages.append(mido.Message('note_on', note=note, velocity=velocity, time=delay))
            elif msg_type == 'note_off':
                note, velocity = params
                delay = time - current_time
                current_time = time
                midi_messages.append(mido.Message('note_off', note=note, velocity=velocity, time=delay))
            elif msg_type == 'instrument':
                instrument_id = params[0]
                delay = time - current_time
                current_time = time
                midi_messages.append(mido.Message('program_change', program=instrument_id, time=delay))
            elif msg_type == 'tempo':
                tempo = params[0]
                delay = time - current_time
                current_time = time
                midi_messages.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo), time=delay))
                
        # 创建MIDI文件
        mid = mido.MidiFile(ticks_per_beat=self.tick_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # 添加所有消息
        for msg in midi_messages:
            track.append(msg)
        
        # 保存到内存
        midi_data = BytesIO()
        mid.save(file=midi_data)
        midi_data.seek(0)
        
        return midi_data.getvalue()
        
    def _duration_to_ticks(self, duration: float, tempo: Optional[int] = None) -> int:
        """将时值转换为MIDI ticks"""
        if tempo is None:
            tempo = self.tempo
        return int(duration * self.tick_per_beat * (tempo / 60))

class MoodMusicManager:
    """
    情绪音乐管理器，根据情绪切换乐器和音乐
    隐喻内部数据重组：不同情绪下乐器音色变化
    """
    def __init__(self, sequencer: MIDISequencer):
        self.sequencer = sequencer
        self.current_mood = "happy"
        self.mood_instruments = {
            "happy": [0, 24, 73],  # 钢琴、尼龙吉他、音色号
            "sad": [33, 40, 112],   # 大提琴、小提琴、钟声
            "angry": [1, 80],        # 电钢琴、单簧管
            "surprised": [73, 112],  # 音色号、钟声
            "shy": [0, 24],         # 钢琴、尼龙吉他
            "neutral": [0],         # 钢琴
        }
        self.background_music: Dict[str, bytes] = {}
        
    def set_mood(self, mood: str):
        """根据情绪设置乐器"""
        if mood in self.mood_instruments:
            self.current_mood = mood
            # 随机选择一个乐器
            instrument = random.choice(self.mood_instruments[mood])
            self.sequencer.set_instrument(instrument)
            return f"已切换到{ mood }情绪，乐器：{ self.sequencer.get_instrument_name(instrument) }"
        return f"未知情绪: {mood}"
        
    def get_mood_description(self, mood: Optional[str] = None) -> str:
        """获取情绪对应的音乐描述"""
        if mood is None:
            mood = self.current_mood
        
        descriptions = {
            "happy": "轻快的钢琴旋律，充满活力",
            "sad": "低沉的大提琴声，带着淡淡的忧伤",
            "angry": "强烈的电钢琴和单簧管，充满张力",
            "surprised": "清脆的钟声和音色号，意外和惊喜",
            "shy": "温柔的钢琴和尼龙吉他，安静腼腆",
            "neutral": "平静的钢琴声，平和安宁",
        }
        
        return descriptions.get(mood, "未知情绪的音乐")
        
    def add_background_music(self, name: str, midi_data: bytes):
        """添加背景音乐"""
        self.background_music[name] = midi_data
        
    def play_background_music(self, name: str):
        """播放背景音乐"""
        if name in self.background_music:
            self.sequencer.load_midi(self.background_music[name])
            self.sequencer.play()
            return True
        return False

def test_midi_editor():
    """测试高级MIDI编辑器"""
    print("高级MIDI编辑器测试")
    print("支持的命令：")
    print("- 简谱：1 2 3 4 5 6 7")
    print("- note命令：note C4 1/4")
    print("- 乐器切换：instrument 0")
    print("- 速度设置：tempo 120")
    print("示例：note C4 q note E4 q note G4 q")
    
    converter = AdvancedScoreConverter()
    sequencer = MIDISequencer()
    mood_manager = MoodMusicManager(sequencer)
    
    while True:
        print("\n请输入命令或简谱（输入q退出）：")
        score = input("> ")
        if score.lower() == 'q':
            break
            
        try:
            midi_data = converter.create_midi(score)
            sequencer.load_midi(midi_data)
            print("播放中...")
            sequencer.play()
            
            # 等待播放完成
            import time
            time.sleep(10)
            sequencer.stop()
        except Exception as e:
            print(f"错误：{e}")

def test_pygame_midi():
    """在Pygame窗口中测试高级MIDI编辑器"""
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    font = get_ui_font(24)
    
    converter = AdvancedScoreConverter()
    sequencer = MIDISequencer()
    mood_manager = MoodMusicManager(sequencer)
    
    input_text = ""
    current_score = "note C4 q note E4 q note G4 q"
    playing = False
    current_mood = "happy"
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # 播放当前输入的命令
                    try:
                        midi_data = converter.create_midi(current_score)
                        sequencer.load_midi(midi_data)
                        sequencer.play()
                        playing = True
                    except Exception as e:
                        print(f"错误：{e}")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_SPACE:
                    if playing:
                        sequencer.pause()
                    else:
                        sequencer.resume()
                    playing = not playing
                elif event.key == pygame.K_m:
                    # 切换静音
                    sequencer.mute(not sequencer.muted)
                elif event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    # 切换情绪
                    moods = ["happy", "sad", "angry", "surprised", "shy", "neutral"]
                    idx = event.key - pygame.K_1
                    if idx < len(moods):
                        current_mood = moods[idx]
                        result = mood_manager.set_mood(current_mood)
                        print(result)
                elif event.unicode.isprintable():
                    input_text += event.unicode
                    current_score = input_text.strip()
        
        screen.fill((0, 0, 0))
        
        # 绘制界面
        text1 = font.render("BBS Shojo游戏 - 高级MIDI编辑器", True, (255, 255, 255))
        text2 = font.render("当前命令/简谱：", True, (255, 255, 255))
        text3 = font.render(current_score, True, (0, 255, 0))
        text4 = font.render("按回车播放，按空格暂停/继续", True, (255, 255, 255))
        text5 = font.render(f"当前情绪：{current_mood} (按1-6切换)", True, (255, 255, 255))
        text6 = font.render(f"乐器：{sequencer.get_instrument_name()}", True, (255, 255, 255))
        text7 = font.render(f"静音：{'是' if sequencer.muted else '否'} (按M切换)", True, (255, 255, 255))
        text8 = font.render(mood_manager.get_mood_description(current_mood), True, (128, 128, 128))
        
        screen.blit(text1, (50, 50))
        screen.blit(text2, (50, 100))
        screen.blit(text3, (50, 150))
        screen.blit(text4, (50, 200))
        screen.blit(text5, (50, 250))
        screen.blit(text6, (50, 280))
        screen.blit(text7, (50, 310))
        screen.blit(text8, (50, 340))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    # 选择测试模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "pygame":
        test_pygame_midi()
    else:
        test_midi_editor()