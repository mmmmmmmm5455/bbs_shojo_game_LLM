import pygame
import sys
import os
from pixel_gradient import pixel_gradient
from crt_effect import crt_effect
from ascii_animation import ASCIIAnimation
from midi_editor import ScoreConverter, MIDISequencer
from animated_character import AnimatedCharacter
from vertical_hold import vertical_hold_effect
from game_fonts import get_ui_font

class MainMenu:
    """
    BBS Shojo游戏主菜单类
    """
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("BBS Shojo游戏 - 主菜单")
        self.clock = pygame.time.Clock()
        self.font = get_ui_font(36)
        self.small_font = get_ui_font(24)
        
        # 菜单选项
        self.menu_options = [
            "像素精度渐变系统",
            "CRT老化模拟效果",
            "ASCII表情动画",
            "MIDI编辑器彩蛋",
            "带音效的ASCII角色",
            "垂直保持失调效果",
            "退出"
        ]
        self.current_selection = 0
        
        # 加载测试图像
        self.test_image = self._create_test_image()
        
    def _create_test_image(self):
        """创建测试图像"""
        image = pygame.Surface((400, 400))
        image.fill((255, 255, 255))
        pygame.draw.circle(image, (255, 0, 0), (200, 200), 100)
        pygame.draw.circle(image, (0, 255, 0), (150, 150), 50)
        pygame.draw.circle(image, (0, 0, 255), (250, 250), 50)
        return image
        
    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill((0, 0, 0))
        
        # 绘制标题
        title_text = self.font.render("BBS Shojo游戏", True, (0, 255, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制菜单选项
        for i, option in enumerate(self.menu_options):
            if i == self.current_selection:
                text = self.font.render(option, True, (255, 0, 0))
            else:
                text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width//2, 200 + i * 70))
            self.screen.blit(text, text_rect)
        
        # 绘制提示
        tip_text = self.small_font.render("使用上下箭头选择，按回车进入，按ESC返回菜单", True, (128, 128, 128))
        tip_rect = tip_text.get_rect(center=(self.screen_width//2, 550))
        self.screen.blit(tip_text, tip_rect)
        
        pygame.display.flip()
        
    def run(self):
        """运行主菜单"""
        running = True
        while running:
            self.draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        # 进入选中的模块
                        self._enter_module(self.current_selection)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()
        
    def _enter_module(self, selection):
        """进入选中的模块"""
        if selection == 0:
            self._pixel_gradient_module()
        elif selection == 1:
            self._crt_effect_module()
        elif selection == 2:
            self._ascii_animation_module()
        elif selection == 3:
            self._midi_editor_module()
        elif selection == 4:
            self._animated_character_module()
        elif selection == 5:
            self._vertical_hold_module()
        elif selection == 6:
            pygame.quit()
            sys.exit()
            
    def _pixel_gradient_module(self):
        """像素精度渐变系统模块"""
        memory_fragments = 0
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        memory_fragments = max(0, memory_fragments - 10)
                    elif event.key == pygame.K_RIGHT:
                        memory_fragments = min(100, memory_fragments + 10)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # 应用像素渐变效果
            processed_image = pixel_gradient_from_surface(self.test_image, memory_fragments, 400, 400)
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(processed_image, (200, 100))
            
            # 绘制进度条
            progress_bar_width = 400
            progress_bar_height = 20
            progress = memory_fragments / 100
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 550, progress_bar_width, progress_bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (200, 550, int(progress_bar_width * progress), progress_bar_height))
            
            # 绘制文字
            text = self.font.render(f"记忆碎片数量: {memory_fragments}/100", True, (255, 255, 255))
            self.screen.blit(text, (200, 50))
            tip_text = self.small_font.render("按左右箭头调整记忆碎片数量，按ESC返回菜单", True, (128, 128, 128))
            self.screen.blit(tip_text, (200, 580))
            
            pygame.display.flip()
            self.clock.tick(30)
            
    def _crt_effect_module(self):
        """CRT老化模拟效果模块"""
        scanline_intensity = 0.2
        noise_intensity = 0.05
        burn_in = False
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        scanline_intensity = max(0, scanline_intensity - 0.1)
                    elif event.key == pygame.K_2:
                        scanline_intensity = min(1.0, scanline_intensity + 0.1)
                    elif event.key == pygame.K_3:
                        noise_intensity = max(0, noise_intensity - 0.05)
                    elif event.key == pygame.K_4:
                        noise_intensity = min(1.0, noise_intensity + 0.05)
                    elif event.key == pygame.K_5:
                        burn_in = not burn_in
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # 应用CRT效果
            processed_image = self.test_image.copy()
            processed_image = crt_effect(processed_image, scanline_intensity, noise_intensity, burn_in=burn_in)
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(processed_image, (200, 100))
            
            # 绘制参数信息
            text1 = self.font.render("CRT老化模拟效果", True, (255, 255, 255))
            text2 = self.small_font.render(f"扫描线强度: {scanline_intensity:.1f} (按1/2调整)", True, (255, 255, 255))
            text3 = self.small_font.render(f"噪点强度: {noise_intensity:.2f} (按3/4调整)", True, (255, 255, 255))
            text4 = self.small_font.render(f"烧屏效果: {'开启' if burn_in else '关闭'} (按5切换)", True, (255, 255, 255))
            tip_text = self.small_font.render("按ESC返回菜单", True, (128, 128, 128))
            
            self.screen.blit(text1, (200, 50))
            self.screen.blit(text2, (200, 500))
            self.screen.blit(text3, (200, 530))
            self.screen.blit(text4, (200, 560))
            self.screen.blit(tip_text, (200, 590))
            
            pygame.display.flip()
            self.clock.tick(30)
            
    def _ascii_animation_module(self):
        """ASCII表情动画模块"""
        animation = ASCIIAnimation()
        current_emotion = "happy"
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            animation.update()
            
            self.screen.fill((0, 0, 0))
            
            # 渲染ASCII文本
            frame_text = animation.get_current_frame().strip()
            text_surface = self.font.render(frame_text, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(text_surface, text_rect)
            
            # 绘制提示
            text1 = self.font.render("ASCII表情动画", True, (255, 255, 255))
            text2 = self.small_font.render(f"当前表情: {current_emotion}", True, (255, 255, 255))
            text3 = self.small_font.render("按1-5切换表情，按ESC返回菜单", True, (128, 128, 128))
            
            self.screen.blit(text1, (200, 50))
            self.screen.blit(text2, (200, 500))
            self.screen.blit(text3, (200, 530))
            
            pygame.display.flip()
            self.clock.tick(30)
            
    def _midi_editor_module(self):
        """MIDI编辑器彩蛋模块"""
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
                        try:
                            midi_data = converter.create_midi(current_score)
                            sequencer.load_midi(midi_data)
                            sequencer.play()
                            playing = True
                        except Exception as e:
                            print(f"错误：{e}")
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        current_score = input_text.strip()
                    elif event.key == pygame.K_SPACE:
                        if playing:
                            sequencer.pause()
                        else:
                            sequencer.resume()
                        playing = not playing
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        sequencer.stop()
                    elif event.unicode.isprintable():
                        input_text += event.unicode
                        current_score = input_text.strip()
            
            self.screen.fill((0, 0, 0))
            
            # 绘制界面
            text1 = self.font.render("MIDI编辑器彩蛋", True, (255, 255, 255))
            text2 = self.small_font.render("输入简谱（例如：1 2 3 4 5 6 7 1'）", True, (255, 255, 255))
            text3 = self.small_font.render(f"当前简谱：{current_score}", True, (0, 255, 0))
            text4 = self.small_font.render("按回车播放，按空格暂停/继续", True, (255, 255, 255))
            tip_text = self.small_font.render("按ESC返回菜单", True, (128, 128, 128))
            
            self.screen.blit(text1, (50, 50))
            self.screen.blit(text2, (50, 100))
            self.screen.blit(text3, (50, 150))
            self.screen.blit(text4, (50, 200))
            self.screen.blit(tip_text, (50, 550))
            
            pygame.display.flip()
            self.clock.tick(30)
            
    def _animated_character_module(self):
        """带音效的ASCII角色模块"""
        character = AnimatedCharacter()
        character.set_frame_delay(0.2)
        current_emotion = "happy"
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_emotion = "happy"
                        character.set_emotion("happy")
                    elif event.key == pygame.K_2:
                        current_emotion = "sad"
                        character.set_emotion("sad")
                    elif event.key == pygame.K_3:
                        current_emotion = "surprised"
                        character.set_emotion("surprised")
                    elif event.key == pygame.K_4:
                        current_emotion = "shy"
                        character.set_emotion("shy")
                    elif event.key == pygame.K_5:
                        current_emotion = "angry"
                        character.set_emotion("angry")
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            character.update()
            
            self.screen.fill((0, 0, 0))
            
            # 渲染ASCII文本
            frame_text = character.get_current_frame().strip()
            text_surface = self.font.render(frame_text, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(text_surface, text_rect)
            
            # 绘制提示
            text1 = self.font.render("带音效的ASCII角色", True, (255, 255, 255))
            text2 = self.small_font.render(f"当前表情: {current_emotion}", True, (255, 255, 255))
            text3 = self.small_font.render("按1-5切换表情，按ESC返回菜单", True, (128, 128, 128))
            
            self.screen.blit(text1, (200, 50))
            self.screen.blit(text2, (200, 500))
            self.screen.blit(text3, (200, 530))
            
            pygame.display.flip()
            self.clock.tick(30)
            
    def _vertical_hold_module(self):
        """垂直保持失调效果模块"""
        intensity = 5
        drift_speed = 1
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        intensity = min(20, intensity + 1)
                    elif event.key == pygame.K_DOWN:
                        intensity = max(0, intensity - 1)
                    elif event.key == pygame.K_LEFT:
                        drift_speed = max(0.1, drift_speed - 0.5)
                    elif event.key == pygame.K_RIGHT:
                        drift_speed = drift_speed + 0.5
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # 应用垂直保持失调效果
            processed_image = vertical_hold_effect(self.test_image, intensity, drift_speed)
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(processed_image, (0, 0))
            
            # 绘制参数信息
            text1 = self.font.render("垂直保持失调效果", True, (255, 255, 255))
            text2 = self.small_font.render(f"偏移强度: {intensity} (按上下箭头调整)", True, (255, 255, 255))
            text3 = self.small_font.render(f"漂移速度: {drift_speed:.1f} (按左右箭头调整)", True, (255, 255, 255))
            tip_text = self.small_font.render("按ESC返回菜单", True, (128, 128, 128))
            
            self.screen.blit(text1, (20, 20))
            self.screen.blit(text2, (20, 50))
            self.screen.blit(text3, (20, 80))
            self.screen.blit(tip_text, (20, 110))
            
            pygame.display.flip()
            self.clock.tick(30)
            
def pixel_gradient_from_surface(surface, memory_fragments, target_width=None, target_height=None):
    """从已有的pygame.Surface对象创建像素渐变效果"""
    original_width, original_height = surface.get_size()
    
    if target_width is None:
        target_width = original_width
    if target_height is None:
        target_height = original_height
    
    scale = 0.1 + (memory_fragments / 100) * 0.9
    small_width = max(1, int(original_width * scale))
    small_height = max(1, int(original_height * scale))
    
    small_image = pygame.transform.scale(surface, (small_width, small_height))
    
    if scale < 1.0:
        processed_image = pygame.transform.scale(small_image, (target_width, target_height))
    else:
        processed_image = surface
    
    return processed_image

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()