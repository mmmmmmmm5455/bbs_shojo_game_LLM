import pygame
import random
import math
from typing import Tuple, Optional

class VerticalHoldManager:
    """
    垂直保持失调效果管理器，模拟老式显示器的画面滚动效果
    隐喻：技术故障下的数字存在不稳定，如同意识的模糊
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # 运行时默认值；不从磁盘读取。enabled / intensity_factor 由宿主
        #（如 main_advanced_v2.BBSShojoGame._apply_vh_settings）按 settings.json 同步。
        self.enabled = True
        self.intensity_factor = 1.0
        self.intensity = 0.0  # 偏移强度，0-100
        self.drift_speed = 1.0  # 漂移速度
        self.active = False
        self.start_time = 0
        self.effect_duration = 0  # 效果持续时间，0表示永久
        self.manual_offset = 0
        
    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)
        if not self.enabled:
            self.deactivate()

    def set_intensity_factor(self, factor: float) -> None:
        """激活时强度乘数，范围 0.0–1.0。"""
        self.intensity_factor = max(0.0, min(1.0, float(factor)))

    def activate(self, intensity: float = 5.0, drift_speed: float = 1.0, duration: int = 0):
        """激活垂直保持失调效果"""
        if not self.enabled:
            return
        self.active = True
        base = max(0.0, min(100.0, float(intensity)))
        self.intensity = base * self.intensity_factor
        self.drift_speed = max(0.1, drift_speed)
        self.effect_duration = duration
        self.start_time = pygame.time.get_ticks()
        self.manual_offset = 0
        
    def deactivate(self):
        """停用垂直保持失调效果"""
        self.active = False
        self.intensity = 0.0
        
    def set_manual_offset(self, offset: int):
        """设置手动偏移量，用于玩家调整"""
        self.manual_offset = max(-20, min(20, offset))
        
    def update(self):
        """更新效果状态，返回是否仍在活动"""
        if not self.active:
            return False
            
        # 检查是否达到持续时间
        if self.effect_duration > 0 and (pygame.time.get_ticks() - self.start_time) > self.effect_duration:
            self.deactivate()
            return False
            
        return True
        
    def apply_effect(self, surface: pygame.Surface) -> pygame.Surface:
        """应用垂直保持失调效果到表面"""
        if not self.active or self.intensity == 0:
            return surface
            
        width, height = surface.get_size()
        processed_surface = pygame.Surface((width, height))
        
        # 获取当前时间，用于生成动态偏移
        current_time = pygame.time.get_ticks()
        base_time = current_time * 0.001
        
        # 计算每个像素行的偏移量
        for y in range(height):
            # 计算当前行的偏移量：基础偏移 + 随机波动 + 时间变化 + 手动偏移
            base_offset = self.intensity * 0.5 * math.sin(base_time * self.drift_speed + y * 0.01)
            random_offset = self.intensity * random.uniform(-0.3, 0.3)
            total_offset = int(base_offset + random_offset + self.manual_offset)
            
            # 限制偏移范围
            total_offset = max(-int(self.intensity * 2), min(int(self.intensity * 2), total_offset))
            
            # 复制当前行到目标位置
            if 0 <= y + total_offset < height:
                row = surface.subsurface((0, y, width, 1))
                if total_offset < 0:
                    processed_surface.blit(row, (max(0, total_offset), y))
                else:
                    processed_surface.blit(row, (0, y - total_offset))
            else:
                # 超出范围的行填充黑色
                pygame.draw.rect(processed_surface, (0, 0, 0), (0, y, width, 1))
        
        return processed_surface
        
    def get_status(self) -> Tuple[bool, float, float]:
        """获取当前效果状态"""
        return (self.active, self.intensity, self.drift_speed)
        
    def is_active(self) -> bool:
        """检查效果是否激活"""
        return self.active

def test_vertical_hold_interactive():
    """测试交互式垂直保持失调效果"""
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    
    # 创建测试图像
    test_image = pygame.Surface((screen_width, screen_height))
    for y in range(screen_height):
        color = (y % 256, (y + 100) % 256, (y + 200) % 256)
        pygame.draw.line(test_image, color, (0, y), (screen_width, y))
    
    vh_manager = VerticalHoldManager(screen_width, screen_height)
    intensity = 5.0
    drift_speed = 1.0
    manual_offset = 0
    
    # 测试场景：触发效果，玩家需要输入v-hold恢复
    test_triggered = False
    trigger_time = 0
    
    running = True
    while running:
        delta_time = clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_t:
                    # 触发效果
                    test_triggered = True
                    trigger_time = pygame.time.get_ticks()
                    vh_manager.activate(intensity=8.0, drift_speed=1.5, duration=5000)
                elif event.key == pygame.K_r:
                    # 重置效果
                    vh_manager.deactivate()
                    test_triggered = False
                    manual_offset = 0
                elif event.key == pygame.K_UP:
                    intensity = min(20, intensity + 1)
                elif event.key == pygame.K_DOWN:
                    intensity = max(0, intensity - 1)
                elif event.key == pygame.K_LEFT:
                    drift_speed = max(0.1, drift_speed - 0.5)
                elif event.key == pygame.K_RIGHT:
                    drift_speed = drift_speed + 0.5
                elif event.key == pygame.K_a:
                    manual_offset -= 1
                elif event.key == pygame.K_d:
                    manual_offset += 1
                elif event.key == pygame.K_s:
                    # 保存当前偏移
                    vh_manager.set_manual_offset(manual_offset)
        
        # 更新效果
        vh_manager.update()
        
        # 应用效果
        if vh_manager.active:
            processed_image = vh_manager.apply_effect(test_image)
        else:
            processed_image = test_image.copy()
        
        screen.fill((0, 0, 0))
        screen.blit(processed_image, (0, 0))
        
        # 绘制参数信息
        from game_fonts import get_ui_font

        font = get_ui_font(24)
        text1 = font.render(f"垂直保持失调效果测试", True, (255, 255, 255))
        text2 = font.render(f"偏移强度: {intensity} (按上下箭头调整)", True, (255, 255, 255))
        text3 = font.render(f"漂移速度: {drift_speed:.1f} (按左右箭头调整)", True, (255, 255, 255))
        text4 = font.render(f"手动偏移: {manual_offset} (按A/D调整，按S保存)", True, (255, 255, 255))
        text5 = font.render(f"按T触发效果，按R重置", True, (255, 255, 255))
        text6 = font.render(f"效果状态: {'激活中' if vh_manager.active else '未激活'}", True, (255, 255, 255))
        
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 50))
        screen.blit(text3, (20, 80))
        screen.blit(text4, (20, 110))
        screen.blit(text5, (20, 140))
        screen.blit(text6, (20, 170))
        
        # 显示特殊场景提示
        if test_triggered:
            elapsed = (pygame.time.get_ticks() - trigger_time) / 1000
            if elapsed < 5:
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 30))
                screen.blit(overlay, (0, 0))
                
                warning_text = font.render(f"警告：显示器出现故障！请输入 'v-hold' 命令恢复", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(screen_width//2, screen_height//2))
                screen.blit(warning_text, warning_rect)
                
                help_text = font.render(f"当前手动偏移: {manual_offset}，按A/D调整，按S确认", True, (255, 255, 255))
                help_rect = help_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
                screen.blit(help_text, help_rect)
        
        pygame.display.flip()
    
    pygame.quit()

def create_vhold_command_system():
    """创建v-hold命令系统"""
    print("v-hold 命令系统")
    print("用法：v-hold [偏移量]")
    print("示例：v-hold 5 → 设置偏移量为5")
    print("      v-hold 0 → 重置偏移量")
    print("      v-hold help → 显示帮助")
    
    def parse_command(command: str) -> Optional[int]:
        parts = command.strip().split()
        if len(parts) < 2:
            return 0  # 默认重置
            
        if parts[1].lower() == 'help':
            print(help)
            return None
            
        try:
            return int(parts[1])
        except ValueError:
            print(f"错误：无效的偏移量 '{parts[1]}'")
            return None
            
    return parse_command

if __name__ == "__main__":
    # 测试交互式垂直保持失调效果
    test_vertical_hold_interactive()