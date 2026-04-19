import pygame
import time
import sys

class ASCIIAnimation:
    """
    ASCII表情动画系统类，负责管理和播放多帧ASCII表情动画
    """
    def __init__(self):
        # 定义各种表情的多帧ASCII序列
        self.animations = {
            "happy": [
                """
                (✧ω✧)
                """,
                """
                (✧ω✧)
                """,
                """
                (✧ω✧)
                """,
                """
                (≧ω≦)
                """,
                """
                (≧ω≦)
                """,
                """
                (≧ω≦)
                """,
                """
                (✧ω✧)
                """
            ],
            "sad": [
                """
                (╥ω╥)
                """,
                """
                (╥ω╥)
                """,
                """
                (ಥωಥ)
                """,
                """
                (ಥωಥ)
                """,
                """
                (╥ω╥)
                """
            ],
            "surprised": [
                """
                (⊙ω⊙)
                """,
                """
                (⊙ω⊙)
                """,
                """
                (〇ω〇)
                """,
                """
                (〇ω〇)
                """,
                """
                (⊙ω⊙)
                """
            ],
            "shy": [
                """
                (⁄ω⁄)
                """,
                """
                (⁄ω⁄)
                """,
                """
                (≧ω≦)
                """,
                """
                (≧ω≦)
                """,
                """
                (⁄ω⁄)
                """
            ],
            "angry": [
                """
                (╬ω╬)
                """,
                """
                (╬ω╬)
                """,
                """
                (｀ω´)
                """,
                """
                (｀ω´)
                """,
                """
                (╬ω╬)
                """
            ]
        }
        
        self.current_animation = "happy"
        self.current_frame = 0
        self.frame_delay = 0.1  # 每帧延迟时间（秒）
        self.last_frame_time = time.time()
        self.loop = True  # 是否循环播放
        
    def set_animation(self, animation_name):
        """设置当前播放的动画"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_frame = 0
            self.last_frame_time = time.time()
            return True
        return False
    
    def update(self):
        """更新动画帧"""
        current_time = time.time()
        if current_time - self.last_frame_time >= self.frame_delay:
            self.current_frame += 1
            self.last_frame_time = current_time
            
            # 检查是否到达动画末尾
            if self.current_frame >= len(self.animations[self.current_animation]):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.animations[self.current_animation]) - 1
            
            return True
        return False
    
    def get_current_frame(self):
        """获取当前帧的ASCII文本"""
        return self.animations[self.current_animation][self.current_frame]
    
    def set_frame_delay(self, delay):
        """设置每帧延迟时间"""
        self.frame_delay = delay
    
    def set_loop(self, loop):
        """设置是否循环播放"""
        self.loop = loop

def test_ascii_animation():
    """测试ASCII表情动画系统"""
    animation = ASCIIAnimation()
    current_emotion = "happy"
    
    print("ASCII表情动画测试")
    print("按键说明：")
    print("1-5: 切换表情 (1:开心, 2:难过, 3:惊讶, 4:害羞, 5:生气)")
    print("q: 退出")
    
    while True:
        # 检查键盘输入
        if sys.stdin.isatty():
            import select
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                key = sys.stdin.read(1).lower()
                if key == 'q':
                    break
                elif key == '1':
                    current_emotion = "happy"
                    animation.set_animation("happy")
                elif key == '2':
                    current_emotion = "sad"
                    animation.set_animation("sad")
                elif key == '3':
                    current_emotion = "surprised"
                    animation.set_animation("surprised")
                elif key == '4':
                    current_emotion = "shy"
                    animation.set_animation("shy")
                elif key == '5':
                    current_emotion = "angry"
                    animation.set_animation("angry")
        
        # 更新动画
        animation.update()
        
        # 清屏并显示当前帧
        print("\033[H")  # 光标移到左上角
        print("\033[J")  # 清除屏幕
        print(f"当前表情: {current_emotion}")
        print("-" * 20)
        print(animation.get_current_frame())
        print("-" * 20)
        print("按q退出，1-5切换表情")
        
        time.sleep(0.05)

def test_pygame_ascii():
    """在Pygame窗口中显示ASCII动画"""
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()
    from game_fonts import get_ui_font

    font = get_ui_font(48)
    
    animation = ASCIIAnimation()
    animation.set_frame_delay(0.2)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    animation.set_animation("happy")
                elif event.key == pygame.K_2:
                    animation.set_animation("sad")
                elif event.key == pygame.K_3:
                    animation.set_animation("surprised")
                elif event.key == pygame.K_4:
                    animation.set_animation("shy")
                elif event.key == pygame.K_5:
                    animation.set_animation("angry")
        
        animation.update()
        
        screen.fill((0, 0, 0))
        
        # 渲染ASCII文本
        frame_text = animation.get_current_frame().strip()
        text_surface = font.render(frame_text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(200, 150))
        screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    # 选择测试模式：终端或Pygame
    if len(sys.argv) > 1 and sys.argv[1] == "pygame":
        test_pygame_ascii()
    else:
        test_ascii_animation()