import pygame
import time
import random
from typing import List, Tuple, Optional

class TypingChallenge:
    """
    打字挑战小游戏，测试玩家的打字速度和准确性
    隐喻：通过文字的互动，加深与少女的连接
    """
    def __init__(self):
        self.challenge_texts = [
            "(◕‿◕✿) 欢迎来到BBS世界！",
            "1 2 3 4 5 6 7 1' 7 6 5 4 3 2 1",
            "你好呀，今天天气真好呢～",
            "+-------------------------+\n| BBS Shojo Game           |\n+-------------------------+",
            "Hello, welcome to BBS Shojo!\nI'm glad to meet you here.",
            "小星星，亮晶晶，满天都是小星星"
        ]
        self.current_challenge = ""
        self.player_input = ""
        self.start_time = 0
        self.end_time = 0
        self.challenge_active = False
        self.wpm = 0
        self.accuracy = 100.0
        self.score = 0
        self.gain = 0
        
    def generate_challenge(self) -> str:
        """生成随机挑战文本"""
        self.current_challenge = random.choice(self.challenge_texts)
        return self.current_challenge
        
    def start_challenge(self) -> Tuple[str, str]:
        """开始打字挑战"""
        self.generate_challenge()
        self.player_input = ""
        self.start_time = time.time()
        self.challenge_active = True
        return self.current_challenge, "准备开始！输入以下文本："
        
    def update_input(self, char: str) -> Tuple[bool, str]:
        """更新玩家输入"""
        if not self.challenge_active:
            return False, "挑战未激活"
            
        if char == "\b":  # 退格键
            self.player_input = self.player_input[:-1]
        elif char == "\n":  # 回车键
            return self._complete_challenge()
        else:
            self.player_input += char
            
        # 计算当前准确率
        self.accuracy = self._calculate_accuracy()
        
        # 检查是否完成（提前完成）
        if self.player_input == self.current_challenge:
            return self._complete_challenge()
            
        return False, ""
        
    def _complete_challenge(self) -> Tuple[bool, str]:
        """完成挑战，计算结果"""
        self.end_time = time.time()
        self.challenge_active = False
        
        # 计算时间和速度
        time_taken = self.end_time - self.start_time
        if time_taken > 0:
            # WPM：英文按词计；无空格文本按「约 5 字符一词」折算，避免中文过低估分
            stripped = self.current_challenge.replace("\n", "").replace("\r", "")
            word_count = len(self.current_challenge.split())
            char_units = max(len(stripped.replace(" ", "")), 1)
            word_equiv = max(word_count, char_units / 5.0)
            self.wpm = int((word_equiv / time_taken) * 60)
            
        # 计算准确率
        self.accuracy = self._calculate_accuracy()
        
        # 计算得分和好感度
        self.score = int(self.wpm * (self.accuracy / 100))
        self.gain = int(self.score / 10)
        
        # 生成反馈
        if self.accuracy >= 90:
            feedback = f"太棒了！准确率{self.accuracy:.1f}%，速度{self.wpm}WPM，得分{self.score}！好感度+{self.gain}"
        elif self.accuracy >= 70:
            feedback = f"不错哦！准确率{self.accuracy:.1f}%，速度{self.wpm}WPM，得分{self.score}！好感度+{self.gain}"
        else:
            feedback = f"加油呀！准确率{self.accuracy:.1f}%，速度{self.wpm}WPM，得分{self.score}！好感度+{self.gain}"
            
        return True, feedback
        
    def _calculate_accuracy(self) -> float:
        """计算输入准确率"""
        if not self.current_challenge or not self.player_input:
            return 100.0
            
        min_len = min(len(self.current_challenge), len(self.player_input))
        correct = 0
        
        for i in range(min_len):
            if self.current_challenge[i] == self.player_input[i]:
                correct += 1
                
        # 考虑额外输入的字符
        total = max(len(self.current_challenge), len(self.player_input))
        if total == 0:
            return 100.0
            
        return (correct / total) * 100
        
    def get_current_progress(self) -> Tuple[str, str, float, float]:
        """获取当前进度"""
        return (
            self.current_challenge,
            self.player_input,
            self.accuracy,
            self.wpm
        )
        
    def is_active(self) -> bool:
        """检查挑战是否激活"""
        return self.challenge_active
        
    def reset(self):
        """重置挑战"""
        self.current_challenge = ""
        self.player_input = ""
        self.start_time = 0
        self.end_time = 0
        self.challenge_active = False
        self.wpm = 0
        self.accuracy = 100.0
        self.score = 0
        self.gain = 0

def test_typing_challenge():
    """测试打字挑战小游戏"""
    challenge = TypingChallenge()
    print("打字挑战小游戏测试")
    print("按任意键开始挑战，按q退出")
    
    import sys
    import select
    
    while True:
        # 检查键盘输入
        if sys.stdin.isatty():
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                key = sys.stdin.read(1)
                if key.lower() == 'q':
                    break
                if not challenge.is_active():
                    text, msg = challenge.start_challenge()
                    print(f"\n{msg}")
                    print(text)
                else:
                    challenge.update_input(key)
                    current, input_text, acc, wpm = challenge.get_current_progress()
                    print(f"\033[H")
                    print(f"\033[J")
                    print(f"挑战文本:\n{current}")
                    print(f"你的输入:\n{input_text}")
                    print(f"准确率: {acc:.1f}%")
                    print(f"速度: {wpm} WPM")
                    print("按q退出，继续输入...")

def test_pygame_typing():
    """在Pygame窗口中测试打字挑战"""
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    from game_fonts import get_ui_font

    font = get_ui_font(24)
    
    challenge = TypingChallenge()
    challenge_active = False
    current_text = ""
    player_input = ""
    feedback = ""
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if not challenge.is_active():
                        current_text, msg = challenge.start_challenge()
                        feedback = msg
                    else:
                        success, fb = challenge.update_input("\n")
                        if success:
                            feedback = fb
                elif event.key == pygame.K_BACKSPACE:
                    if challenge.is_active():
                        challenge.update_input("\b")
                elif event.unicode.isprintable():
                    if challenge.is_active():
                        challenge.update_input(event.unicode)
        
        screen.fill((0, 0, 0))
        
        if not challenge.is_active():
            # 显示开始提示
            text1 = font.render("打字挑战小游戏", True, (255, 255, 255))
            text2 = font.render("按回车键开始挑战", True, (128, 128, 128))
            text3 = font.render("按ESC退出", True, (128, 128, 128))
            screen.blit(text1, (screen_width//2 - text1.get_width()//2, 200))
            screen.blit(text2, (screen_width//2 - text2.get_width()//2, 300))
            screen.blit(text3, (screen_width//2 - text3.get_width()//2, 350))
        else:
            # 显示挑战内容
            current, input_text, acc, wpm = challenge.get_current_progress()
            
            # 绘制挑战文本
            y = 100
            for line in current.split("\n"):
                text = font.render(line, True, (0, 255, 0))
                screen.blit(text, (screen_width//2 - text.get_width()//2, y))
                y += 30
                
            # 绘制输入文本
            y += 50
            input_text_surf = font.render(f"你的输入: {input_text}", True, (255, 255, 255))
            screen.blit(input_text_surf, (screen_width//2 - input_text_surf.get_width()//2, y))
            y += 30
            
            # 绘制进度
            acc_text = font.render(f"准确率: {acc:.1f}%", True, (255, 255, 255))
            screen.blit(acc_text, (screen_width//2 - acc_text.get_width()//2, y))
            y += 30
            
            wpm_text = font.render(f"速度: {wpm} WPM", True, (255, 255, 255))
            screen.blit(wpm_text, (screen_width//2 - wpm_text.get_width()//2, y))
            y += 30
            
            # 绘制反馈
            if feedback:
                feedback_text = font.render(feedback, True, (0, 255, 0))
                screen.blit(feedback_text, (screen_width//2 - feedback_text.get_width()//2, y))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    # 选择测试模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "pygame":
        test_pygame_typing()
    else:
        test_typing_challenge()