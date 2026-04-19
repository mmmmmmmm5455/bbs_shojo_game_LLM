import pygame
import time
import sys
import random
from typing import Dict, List, Optional

_MISSING_ASCII_ART_NOTICE_SHOWN = False
try:
    from ascii_art import AsciiArt
    HAS_ASCII_ART = True
except ImportError:
    HAS_ASCII_ART = False
    if not _MISSING_ASCII_ART_NOTICE_SHOWN:
        _MISSING_ASCII_ART_NOTICE_SHOWN = True
        print(
            "ascii-art not installed; ASCII art conversion disabled. pip install ascii-art",
            file=sys.stderr,
        )

class ASCIIAnimation:
    """
    ASCII表情动画系统类，负责管理和播放多帧ASCII表情动画
    隐喻语言与图像的边界：ASCII艺术处在文字与图像的交界上
    """
    def __init__(self):
        # 定义各种表情的多帧ASCII序列，更流畅的动画
        self.animations: Dict[str, List[str]] = {
            "happy": [
                "(◕‿◕✿)",
                "(✧ω✧)",
                "(≧ω≦)",
                "(◕ᴗ◕✿)",
                "(✧∀✧)",
                "(≧▽≦)",
                "(◕‿◕✿)"
            ],
            "sad": [
                "(╥﹏╥)",
                "(ಥ_ಥ)",
                "(╥ω╥)",
                "(ಥωಥ)",
                "(╥﹏╥)"
            ],
            "surprised": [
                "(⊙o⊙)",
                "(〇o〇)",
                "(⊙ω⊙)",
                "(〇ω〇)",
                "(⊙o⊙)"
            ],
            "shy": [
                "(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
                "(≧ω≦)",
                "(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
                "(≧ω≦)",
                "(⁄ ⁄•⁄ω⁄•⁄ ⁄)"
            ],
            "angry": [
                "(╬◣д◢)",
                "(╬ω╬)",
                "(｀ε´)",
                "(｀ω´)",
                "(╬◣д◢)"
            ],
            "blush": [
                "(≧ω≦)",
                "(✧ω✧)",
                "(◕‿◕✿)",
                "(≧ω≦)✧",
                "(✧ω✧)"
            ],
            "wink": [
                "(◕w◕)",
                "(✧w✧)",
                "(◕ᴗ◕)✧",
                "(✧ω✧)",
                "(◕w◕)"
            ]
        }
        
        self.current_animation = "happy"
        self.current_frame = 0
        self.frame_delay = 0.15  # 每帧延迟时间（秒），更流畅
        self.last_frame_time = time.time()
        self.loop = True  # 是否循环播放
        self.paused = False
        
    def set_animation(self, animation_name: str) -> bool:
        """设置当前播放的动画"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_frame = 0
            self.last_frame_time = time.time()
            return True
        return False
    
    def update(self) -> bool:
        """更新动画帧"""
        if self.paused:
            return False
            
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
    
    def get_current_frame(self) -> str:
        """获取当前帧的ASCII文本"""
        return self.animations[self.current_animation][self.current_frame]
    
    def set_frame_delay(self, delay: float):
        """设置每帧延迟时间"""
        self.frame_delay = max(0.01, delay)
    
    def set_loop(self, loop: bool):
        """设置是否循环播放"""
        self.loop = loop
    
    def pause(self):
        """暂停动画"""
        self.paused = True
    
    def resume(self):
        """恢复动画"""
        self.paused = False
        self.last_frame_time = time.time()
    
    def random_frame(self):
        """随机跳转到一帧"""
        self.current_frame = random.randint(0, len(self.animations[self.current_animation]) - 1)
        self.last_frame_time = time.time()

class ASCIIArtConverter:
    """
    ASCII艺术转换器，将任意文本转换为ASCII艺术
    隐喻语言与图像的交界：用打字来绘画
    """
    def __init__(self):
        self.ascii_art: Optional[AsciiArt] = None
        if HAS_ASCII_ART:
            self.ascii_art = AsciiArt()
            
    def text_to_ascii(self, text: str, width: int = 40, height: Optional[int] = None) -> str:
        """将文本转换为ASCII艺术"""
        if not HAS_ASCII_ART:
            return f"[ASCII艺术不可用：{text}]"
            
        try:
            # 简单的ASCII艺术转换，使用字符画
            if height is None:
                height = width // 2
                
            # 使用随机字符集
            chars = random.choice([" .:-=+*#%@", " ░▒▓█", " .'`^", "  oaAHX"])
            ascii_result = self.ascii_art.text_to_ascii(text, width=width, height=height, chars=chars)
            return ascii_result
        except Exception as e:
            return f"[生成ASCII艺术失败：{str(e)}]"
            
    def image_to_ascii(self, image_path: str, width: int = 40) -> str:
        """将图像转换为ASCII艺术"""
        if not HAS_ASCII_ART:
            return "[ASCII艺术不可用：请安装ascii-art库]"
            
        try:
            return self.ascii_art.image_to_ascii(image_path, width=width)
        except Exception as e:
            return f"[生成图像ASCII艺术失败：{str(e)}]"

def test_ascii_animation():
    """测试ASCII表情动画系统"""
    animation = ASCIIAnimation()
    converter = ASCIIArtConverter()
    current_emotion = "happy"
    input_text = ""
    
    print("ASCII表情动画测试")
    print("按键说明：")
    print("1-6: 切换表情 (1:开心, 2:难过, 3:惊讶, 4:害羞, 5:生气, 6:脸红)")
    print("ascii [文本]: 将文本转换为ASCII艺术")
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
                elif key == '6':
                    current_emotion = "blush"
                    animation.set_animation("blush")
                elif key == 'a':
                    # 进入ASCII转换模式
                    print("\n输入要转换为ASCII艺术的文本：")
                    input_text = sys.stdin.readline().strip()
                    if input_text:
                        ascii_art = converter.text_to_ascii(input_text)
                        print(f"\nASCII艺术结果：\n{ascii_art}")
                        print("\n按任意键继续...")
                        sys.stdin.read(1)
        
        # 更新动画
        animation.update()
        
        # 清屏并显示当前帧
        print("\033[H")  # 光标移到左上角
        print("\033[J")  # 清除屏幕
        print(f"当前表情: {current_emotion}")
        print("-" * 40)
        print(animation.get_current_frame())
        print("-" * 40)
        print("按q退出，1-6切换表情，a生成ASCII艺术")
        
        time.sleep(0.05)

def test_pygame_ascii():
    """在Pygame窗口中显示ASCII动画"""
    pygame.init()
    screen_width = 600
    screen_height = 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    from game_fonts import get_ui_font

    font = get_ui_font(36)
    
    animation = ASCIIAnimation()
    animation.set_frame_delay(0.15)
    converter = ASCIIArtConverter()
    
    current_emotion = "happy"
    ascii_art_text = ""
    input_active = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_emotion = "happy"
                    animation.set_animation("happy")
                elif event.key == pygame.K_2:
                    current_emotion = "sad"
                    animation.set_animation("sad")
                elif event.key == pygame.K_3:
                    current_emotion = "surprised"
                    animation.set_animation("surprised")
                elif event.key == pygame.K_4:
                    current_emotion = "shy"
                    animation.set_animation("shy")
                elif event.key == pygame.K_5:
                    current_emotion = "angry"
                    animation.set_animation("angry")
                elif event.key == pygame.K_6:
                    current_emotion = "blush"
                    animation.set_animation("blush")
                elif event.key == pygame.K_r:
                    animation.random_frame()
                elif event.key == pygame.K_SPACE:
                    if animation.paused:
                        animation.resume()
                    else:
                        animation.pause()
                elif event.key == pygame.K_RETURN and input_active:
                    # 处理ASCII艺术输入
                    if ascii_art_text:
                        ascii_result = converter.text_to_ascii(ascii_art_text)
                        print(f"生成ASCII艺术: {ascii_result}")
                        input_active = False
                elif event.key == pygame.K_BACKSPACE and input_active:
                    ascii_art_text = ascii_art_text[:-1]
                elif event.unicode.isprintable() and input_active:
                    ascii_art_text += event.unicode
        
        animation.update()
        
        screen.fill((0, 0, 0))
        
        # 渲染ASCII文本
        frame_text = animation.get_current_frame().strip()
        text_surface = font.render(frame_text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(screen_width//2, screen_height//2 - 50))
        screen.blit(text_surface, text_rect)
        
        # 绘制提示
        tip1 = font.render(f"当前表情: {current_emotion}", True, (255, 255, 255))
        tip2 = font.render("按1-6切换表情, R随机帧, 空格暂停/继续", True, (128, 128, 128))
        tip3 = font.render("按a生成ASCII艺术", True, (128, 128, 128))
        
        screen.blit(tip1, (20, 20))
        screen.blit(tip2, (20, screen_height - 60))
        screen.blit(tip3, (20, screen_height - 30))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    # 选择测试模式：终端或Pygame
    if len(sys.argv) > 1 and sys.argv[1] == "pygame":
        test_pygame_ascii()
    else:
        test_ascii_animation()