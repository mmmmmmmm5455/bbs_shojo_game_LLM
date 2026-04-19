import pygame
import mido

from game_fonts import get_ui_font
import time
import re
from io import BytesIO

class MIDISequencer:
    """
    MIDI音序器类，负责播放MIDI音乐
    """
    def __init__(self):
        pygame.mixer.init()
        self.current_midi = None
        self.current_channel = 0
        self.volume = 100
        
    def load_midi(self, midi_data):
        """加载MIDI数据"""
        if self.current_midi:
            pygame.mixer.music.stop()
        
        # 将MIDI数据保存到临时文件
        with open("temp.mid", "wb") as f:
            f.write(midi_data)
        
        pygame.mixer.music.load("temp.mid")
        self.current_midi = "temp.mid"
        
    def play(self):
        """播放MIDI音乐"""
        if self.current_midi:
            pygame.mixer.music.play()
            
    def pause(self):
        """暂停播放"""
        if self.current_midi:
            pygame.mixer.music.pause()
            
    def resume(self):
        """恢复播放"""
        if self.current_midi:
            pygame.mixer.music.unpause()
            
    def stop(self):
        """停止播放"""
        if self.current_midi:
            pygame.mixer.music.stop()
            
    def set_volume(self, volume):
        """设置音量（0-100）"""
        self.volume = max(0, min(100, volume))
        pygame.mixer.music.set_volume(self.volume / 100)

class ScoreConverter:
    """
    简谱到MIDI的转换器
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
    }
    
    # 时值映射（以四分音符为1拍，每分钟120拍）
    DURATION_MAP = {
        'whole': 4.0,   # 全音符
        'half': 2.0,    # 二分音符
        'quarter': 1.0, # 四分音符
        'eighth': 0.5,  # 八分音符
        'sixteenth': 0.25, # 十六分音符
    }
    
    def __init__(self, tempo=120):
        self.tempo = tempo  # 每分钟节拍数
        self.tick_per_beat = 480  # 每拍的tick数
        
    def parse_score(self, score_text):
        """
        解析简谱文本，返回MIDI消息列表
        简谱格式示例：1 2 3 | 4 5 6 | 7 - 1"""
        # 清理输入文本
        score_text = score_text.replace('\n', ' ').replace('\t', ' ')
        # 分割音符和节拍
        tokens = re.split(r'\s+', score_text.strip())
        
        midi_messages = []
        current_time = 0
        
        for token in tokens:
            if not token:
                continue
                
            # 处理休止符
            if token.startswith('0') or token == '0':
                # 休止符，计算时长
                duration = self._parse_duration(token)
                current_time += self._duration_to_ticks(duration)
                continue
                
            # 处理音符
            # 匹配高音点、低音点、音符、延时
            match = re.match(r'([1-7])([\',.]*)?([\.]*)?', token)
            if not match:
                continue
                
            note_num = match.group(1)
            modifiers = match.group(2) or ''
            dots = match.group(3) or ''
            
            # 计算音高
            base_note = self.BASE_NOTES[note_num]
            
            # 处理高音点（' 表示高八度，'' 表示高两个八度）
            octave_adjust = modifiers.count("'")
            # 处理低音点（. 表示低八度，.. 表示低两个八度）
            octave_adjust -= modifiers.count(".")
            
            final_note = base_note + octave_adjust * 12
            
            # 计算时长
            duration = self._parse_duration(token.replace(note_num, '').replace(modifiers, '').replace(dots, ''))
            # 处理附点
            for dot in dots:
                duration += duration / 2
                
            # 添加音符开始消息
            midi_messages.append(('note_on', current_time, self._note_to_midi(final_note), 64))
            # 添加音符结束消息
            note_duration = self._duration_to_ticks(duration)
            midi_messages.append(('note_off', current_time + note_duration, self._note_to_midi(final_note), 64))
            
            current_time += note_duration
            
        return midi_messages
    
    def _parse_duration(self, token):
        """解析简谱中的时值"""
        # 默认四分音符
        if not token:
            return self.DURATION_MAP['quarter']
            
        # 处理减时线（-）
        if '-' in token:
            parts = token.split('-')
            base_duration = self.DURATION_MAP['quarter']
            for _ in parts[1:]:
                base_duration *= 2
            return base_duration
            
        # 处理增时线（.）
        if '.' in token:
            parts = token.split('.')
            base_duration = self.DURATION_MAP['quarter'] / (len(parts[0]) if parts[0] else 1)
            for _ in parts[1:]:
                base_duration += base_duration / 2
            return base_duration
            
        # 处理数字后缀
        if token.isdigit():
            div = int(token)
            return self.DURATION_MAP['quarter'] / div
            
        return self.DURATION_MAP['quarter']
    
    def _note_to_midi(self, note):
        """将简谱音符转换为MIDI音符号"""
        return note
        
    def _duration_to_ticks(self, duration):
        """将时值转换为MIDI ticks"""
        return int(duration * self.tick_per_beat * (self.tempo / 60))
    
    def create_midi(self, score_text, instrument=0):
        """将简谱转换为MIDI文件数据"""
        midi_messages = self.parse_score(score_text)
        
        # 创建MIDI文件
        mid = mido.MidiFile(ticks_per_beat=self.tick_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # 设置乐器
        track.append(mido.Message('program_change', program=instrument, time=0))
        
        # 添加节拍设置
        tempo = mido.bpm2tempo(self.tempo)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        
        # 添加所有消息
        for msg_type, time, note, velocity in midi_messages:
            if msg_type == 'note_on':
                track.append(mido.Message('note_on', note=note, velocity=velocity, time=time))
            elif msg_type == 'note_off':
                track.append(mido.Message('note_off', note=note, velocity=velocity, time=time))
        
        # 保存到内存
        midi_data = BytesIO()
        mid.save(file=midi_data)
        midi_data.seek(0)
        
        return midi_data.getvalue()

def test_midi_editor():
    """测试MIDI编辑器"""
    print("MIDI编辑器测试")
    print("示例简谱：1 2 3 4 5 6 7 1' - 1' 7 6 5 4 3 2 1")
    
    converter = ScoreConverter()
    sequencer = MIDISequencer()
    
    while True:
        print("\n请输入简谱（输入q退出）：")
        score = input("> ")
        if score.lower() == 'q':
            break
            
        try:
            midi_data = converter.create_midi(score)
            sequencer.load_midi(midi_data)
            print("播放中...")
            sequencer.play()
            
            # 等待播放完成
            time.sleep(10)
            sequencer.stop()
        except Exception as e:
            print(f"错误：{e}")

def test_pygame_midi():
    """在Pygame窗口中测试MIDI编辑器"""
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    font = get_ui_font(24)
    
    converter = ScoreConverter()
    sequencer = MIDISequencer()
    
    input_text = ""
    current_score = "1 2 3 4 5 6 7 1'"
    playing = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # 播放当前输入的简谱
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
                elif event.unicode.isprintable():
                    input_text += event.unicode
                    # 按空格分隔简谱
                    current_score = input_text.strip()
        
        screen.fill((0, 0, 0))
        
        # 绘制提示
        text1 = font.render("BBS Shojo游戏 - MIDI编辑器彩蛋", True, (255, 255, 255))
        text2 = font.render("输入简谱（例如：1 2 3 4 5 6 7 1'）", True, (255, 255, 255))
        text3 = font.render(f"当前简谱：{current_score}", True, (0, 255, 0))
        text4 = font.render("按回车播放，按空格暂停/继续", True, (255, 255, 255))
        
        screen.blit(text1, (50, 50))
        screen.blit(text2, (50, 100))
        screen.blit(text3, (50, 150))
        screen.blit(text4, (50, 200))
        
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