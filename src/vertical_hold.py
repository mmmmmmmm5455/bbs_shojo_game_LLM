import pygame
import random
import math

def vertical_hold_effect(surface, intensity=5, drift_speed=1):
    """
    模拟老式显示器的垂直保持失调效果（画面滚动）
    :param surface: 要处理的pygame.Surface对象
    :param intensity: 偏移强度，越大偏移越明显
    :param drift_speed: 漂移速度，越大变化越快
    :return: 处理后的pygame.Surface对象
    """
    width, height = surface.get_size()
    processed_surface = pygame.Surface((width, height))
    
    # 获取当前时间，用于生成动态偏移
    current_time = pygame.time.get_ticks()
    
    # 计算每个像素行的偏移量
    # 使用正弦函数生成平滑的漂移效果
    for y in range(height):
        # 计算当前行的偏移量，随时间和y值变化
        offset = int(intensity * random.uniform(-0.5, 0.5) + 
                   intensity * 0.5 * (1 + math.sin(current_time * 0.001 * drift_speed + y * 0.01)))
        
        # 限制偏移范围
        offset = max(-intensity, min(intensity, offset))
        
        # 复制当前行到目标位置
        if 0 <= y + offset < height:
            row = surface.subsurface((0, y, width, 1))
            processed_surface.blit(row, (max(0, offset), y) if offset < 0 else (0, y - offset))
        else:
            # 超出范围的行填充黑色
            pygame.draw.rect(processed_surface, (0, 0, 0), (0, y, width, 1))
    
    return processed_surface

def test_vertical_hold_effect():
    """测试垂直保持失调效果"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 创建一个测试图像
    test_image = pygame.Surface((800, 600))
    for y in range(600):
        color = (y % 256, (y + 100) % 256, (y + 200) % 256)
        pygame.draw.line(test_image, color, (0, y), (800, y))
    
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
        
        # 应用垂直保持失调效果
        processed_image = vertical_hold_effect(test_image, intensity, drift_speed)
        
        screen.fill((0, 0, 0))
        screen.blit(processed_image, (0, 0))
        
        # 绘制参数信息
        from game_fonts import get_ui_font

        font = get_ui_font(24)
        text1 = font.render(f"垂直保持失调效果测试", True, (255, 255, 255))
        text2 = font.render(f"偏移强度: {intensity} (按上下箭头调整)", True, (255, 255, 255))
        text3 = font.render(f"漂移速度: {drift_speed:.1f} (按左右箭头调整)", True, (255, 255, 255))
        text4 = font.render(f"按q退出", True, (255, 255, 255))
        
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 50))
        screen.blit(text3, (20, 80))
        screen.blit(text4, (20, 110))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    test_vertical_hold_effect()