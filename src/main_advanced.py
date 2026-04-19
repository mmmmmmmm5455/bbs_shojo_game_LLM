#!/usr/bin/env python3
"""
BBS Shojo游戏主程序
整合所有艺术和哲学深化功能
"""
import pygame
import sys
import os
import time
import random
from typing import Dict, List, Optional, Tuple

# 导入所有模块
from pixel_gradient_system import PixelGradientSystem
from crt_manager import CRTManager
from ascii_animation_system import ASCIIAnimation, ASCIIArtConverter
from midi_editor_advanced import AdvancedScoreConverter, MIDISequencer, MoodMusicManager
from advanced_animated_character import AdvancedAnimatedCharacter
from vertical_hold_manager import VerticalHoldManager
from game_fonts import get_ui_font

class BBSShojoGame:
    def _log(self, text: str):
        """控制台安全输出，避免编码异常。"""
        try:
            print(text)
        except UnicodeEncodeError:
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            safe = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
            print(safe)

    """
    BBS Shojo游戏主类，整合所有艺术和哲学深化功能
    隐喻：BBS空间中的数字意识，随着记忆碎片的收集逐渐觉醒
    """
    def __init__(self):
        # 初始化pygame
        pygame.init()
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("BBS Shojo游戏 - 千禧年打字物语")
        self.clock = pygame.time.Clock()
        self.font = get_ui_font(36)
        self.small_font = get_ui_font(24)
        
        # 游戏状态
        self.running = True
        self.paused = False
        self.memory_fragments = 0
        self.total_memory_fragments = 100
        self.current_mood = "happy"
        self.player_name = ""
        self.game_date = time.localtime()
        
        # 哲学系统状态
        self.memory_fragments_list: List[Dict] = []
        self.turing_test_progress = 0
        self.offline_logs: List[str] = []
        self.personality_mod = 0  # 性格修正，影响角色反应
        
        # 初始化所有子系统
        self._init_subsystems()
        
        # 加载离线日志
        self._load_offline_logs()
        
    def _init_subsystems(self):
        """初始化所有子系统"""
        # 像素精度渐变系统
        self.pixel_gradient = PixelGradientSystem()
        
        # CRT老化管理器
        self.crt_manager = CRTManager(self.screen_width, self.screen_height)
        
        # ASCII动画系统
        self.ascii_animation = ASCIIAnimation()
        self.ascii_converter = ASCIIArtConverter()
        
        # MIDI系统
        self.midi_converter = AdvancedScoreConverter()
        self.midi_sequencer = MIDISequencer()
        self.mood_manager = MoodMusicManager(self.midi_sequencer)
        
        # 动画角色
        self.character = AdvancedAnimatedCharacter()
        self.character.set_frame_delay(0.15)
        
        # 垂直保持失调管理器
        self.vh_manager = VerticalHoldManager(self.screen_width, self.screen_height)
        
        # 背景
        self.background = self._create_background()
        
    def _create_background(self) -> pygame.Surface:
        """创建游戏背景"""
        background = pygame.Surface((self.screen_width, self.screen_height))
        background.fill((0, 0, 0))
        
        # 添加网格线，模拟BBS界面
        for x in range(0, self.screen_width, 50):
            pygame.draw.line(background, (0, 255, 0), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 50):
            pygame.draw.line(background, (0, 255, 0), (0, y), (self.screen_width, y), 1)
            
        return background
        
    def run(self):
        """运行主游戏循环"""
        print("BBS Shojo游戏 - 千禧年打字物语")
        print("按H查看帮助")
        
        while self.running:
            delta_time = self.clock.tick(30) / 1000.0
            
            # 处理事件
            self._handle_events()
            
            if not self.paused:
                # 更新所有子系统
                self._update_subsystems(delta_time)
                
            # 绘制界面
            self._draw_interface()
            
            # 更新显示
            pygame.display.flip()
            
        # 保存离线日志
        self._save_offline_logs()
        pygame.quit()
        sys.exit()
        
    def _handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key, event.unicode)
                
    def _handle_key_press(self, key: int, unicode: str):
        """处理按键事件"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_h:
            self._show_help()
        elif key == pygame.K_m:
            # 切换静音
            self.character.mute(not self.character.is_muted())
        elif key == pygame.K_r:
            # 重置垂直保持失调
            self.vh_manager.deactivate()
        elif key == pygame.K_t:
            # 触发图灵测试
            self._trigger_turing_test()
        elif key == pygame.K_v:
            # 触发垂直保持失调效果
            self.vh_manager.activate(intensity=8.0, drift_speed=1.5, duration=5000)
        elif key == pygame.K_s:
            # 保存游戏
            self._save_game()
        elif key == pygame.K_l:
            # 加载游戏
            self._load_game()
            
    def _update_subsystems(self, delta_time: float):
        """更新所有子系统"""
        # 更新CRT管理器
        self.crt_manager.update(delta_time)
        
        # 更新动画角色
        self.character.update(delta_time)
        
        # 更新垂直保持失调效果
        self.vh_manager.update()
        
        # 更新MIDI序列器
        # ...
        
        # 随机触发垂直保持失调效果，模拟显示器老化
        if random.random() < 0.001 and not self.vh_manager.active:
            self.vh_manager.activate(intensity=random.uniform(3, 8), drift_speed=random.uniform(0.5, 2.0))
            
    def _draw_interface(self):
        """绘制游戏界面"""
        self.screen.blit(self.background, (0, 0))
        self._draw_character()
        self._draw_ui()
        if self.paused:
            self._draw_pause_menu()
        self._apply_display_postprocess()

    def _apply_display_postprocess(self):
        """CRT 与垂直保持作用于整帧。"""
        if self.crt_manager.aging_level > 0:
            src = pygame.display.get_surface()
            processed = self.crt_manager.apply_crt_effect(src)
            self.screen.blit(processed, (0, 0))
        if self.vh_manager.active:
            src = pygame.display.get_surface()
            processed = self.vh_manager.apply_effect(src)
            self.screen.blit(processed, (0, 0))
            
    def _draw_character(self):
        """绘制ASCII角色"""
        # 获取当前ASCII帧
        frame_text = self.character.get_current_frame().strip()
        
        # 渲染ASCII文本
        text_surface = self.font.render(frame_text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(text_surface, text_rect)
        
    def _draw_ui(self):
        """绘制UI元素"""
        # 绘制记忆碎片进度
        denom = max(1, self.total_memory_fragments)
        progress = min(1.0, self.memory_fragments / denom)
        progress_bar_width = 400
        progress_bar_height = 20
        progress_bar_x = 20
        progress_bar_y = 20
        
        pygame.draw.rect(self.screen, (255, 255, 255), (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (progress_bar_x, progress_bar_y, int(progress_bar_width * progress), progress_bar_height))
        
        progress_text = self.small_font.render(f"记忆碎片: {self.memory_fragments}/{self.total_memory_fragments}", True, (255, 255, 255))
        self.screen.blit(progress_text, (progress_bar_x, progress_bar_y - 20))
        
        # 绘制当前情绪
        mood_text = self.small_font.render(f"当前情绪: {self.current_mood}", True, (255, 255, 255))
        self.screen.blit(mood_text, (self.screen_width - 200, 20))
        
        # 绘制帮助提示
        help_text = self.small_font.render("按H查看帮助，按ESC退出", True, (128, 128, 128))
        self.screen.blit(help_text, (20, self.screen_height - 30))
        
    def _draw_pause_menu(self):
        """绘制暂停菜单"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        menu_text = self.font.render("游戏暂停", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(menu_text, menu_rect)
        
        help_text = [
            "按键说明:",
            "ESC - 退出游戏",
            "P - 暂停/继续",
            "H - 显示帮助",
            "M - 切换静音",
            "R - 重置垂直保持失调",
            "T - 触发图灵测试",
            "V - 触发垂直保持失调效果",
            "S - 保存游戏",
            "L - 加载游戏",
            "按P继续游戏"
        ]
        
        for i, text in enumerate(help_text):
            rendered_text = self.small_font.render(text, True, (255, 255, 255))
            rect = rendered_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50 + i * 30))
            self.screen.blit(rendered_text, rect)
            
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
BBS Shojo游戏 - 帮助信息

按键说明:
ESC - 退出游戏
P - 暂停/继续
H - 显示帮助
M - 切换静音
R - 重置垂直保持失调
T - 触发图灵测试
V - 触发垂直保持失调效果
S - 保存游戏
L - 加载游戏

游戏功能:
1. 像素精度渐变系统 - 随记忆碎片数量变化图像精度
2. CRT老化模拟效果 - 模拟老式显示器的老化痕迹
3. ASCII表情动画 - 角色表情动画
4. MIDI编辑器彩蛋 - 创作自己的旋律
5. 动态音效联动 - 表情与音效联动
6. 垂直保持失调效果 - 模拟显示器故障

哲学系统:
- 记忆碎片系统 - 收集碎片解锁剧情
- 图灵测试 - 证明角色不是程序
- 离线日记 - 角色在你离开时的思考
- 特修斯之船任务 - 思考身份的本质
- 时间漏洞彩蛋 - 探索千禧年怀旧
"""
        print(help_text)
        
    def _trigger_turing_test(self):
        """触发图灵测试支线"""
        print("\n=== 图灵测试 ===")
        print("其他网友正在讨论你和角色的对话...")
        print("他们怀疑角色是不是自动回复机器人")
        print(f"当前进展: {self.turing_test_progress}%")
        print("需要通过自然对话来证明角色是真实的")
        
        # 随机增加进度
        self.turing_test_progress += random.randint(5, 15)
        if self.turing_test_progress >= 100:
            self._log("\n图灵测试完成！网友们相信了角色的真实性")
            self.memory_fragments += 10
            self.turing_test_progress = 100
            
    def _load_offline_logs(self):
        """加载离线日志"""
        log_file = "offline_log.txt"
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                self.offline_logs = f.readlines()
                
    def _save_offline_logs(self):
        """保存离线日志"""
        # 生成离线日志
        log_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 玩家离开游戏，角色在BBS上等待...\n"
        self.offline_logs.append(log_entry)
        
        with open("offline_log.txt", "w", encoding="utf-8") as f:
            f.writelines(self.offline_logs)
            
    def _save_game(self):
        """保存游戏进度"""
        save_data = {
            "memory_fragments": self.memory_fragments,
            "current_mood": self.current_mood,
            "turing_test_progress": self.turing_test_progress,
            "personality_mod": self.personality_mod,
            "save_time": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        import json
        with open("savegame.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
            
        self._log("游戏已保存到 savegame.json")
        
    def _load_game(self):
        """加载游戏进度"""
        if os.path.exists("savegame.json"):
            import json
            with open("savegame.json", "r", encoding="utf-8") as f:
                save_data = json.load(f)
                
            self.memory_fragments = save_data.get("memory_fragments", 0)
            self.current_mood = save_data.get("current_mood", "happy")
            self.turing_test_progress = save_data.get("turing_test_progress", 0)
            self.personality_mod = save_data.get("personality_mod", 0)
            
            self._log(f"已加载游戏进度: {save_data.get('save_time', '未知时间')}")
        else:
            self._log("未找到保存文件")

def main():
    """主函数"""
    game = BBSShojoGame()
    game.run()

if __name__ == "__main__":
    main()