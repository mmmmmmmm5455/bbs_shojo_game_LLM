import pygame
import random

def crt_effect(surface, scanline_intensity=0.2, noise_intensity=0.05, color_bias=(1.05, 1.0, 0.95), burn_in=False):
    """
    为游戏画面添加CRT老化模拟效果
    :param surface: 要处理的pygame.Surface对象
    :param scanline_intensity: 扫描线强度（0-1），默认0.2
    :param noise_intensity: 噪点强度（0-1），默认0.05
    :param color_bias: RGB通道偏置，默认(1.05, 1.0, 0.95)，轻微偏红和偏黄
    :param burn_in: 是否添加烧屏效果，默认False
    :return: 处理后的pygame.Surface对象
    """
    width, height = surface.get_size()
    
    # 创建一个新的表面用于处理，避免修改原始表面
    processed_surface = surface.copy()
    pixels = pygame.PixelArray(processed_surface)
    
    # 应用颜色偏置
    for y in range(height):
        for x in range(width):
            # 获取原始像素颜色
            color = processed_surface.get_at((x, y))
            r, g, b, a = color
            
            # 应用颜色偏置
            r = min(255, int(r * color_bias[0]))
            g = min(255, int(g * color_bias[1]))
            b = min(255, int(b * color_bias[2]))
            
            # 设置新的像素颜色
            pixels[x, y] = (r, g, b, a)
    
    # 释放PixelArray
    del pixels
    
    # 添加扫描线
    if scanline_intensity > 0:
        scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 2):
            pygame.draw.rect(scanline_surface, (0, 0, 0, int(255 * scanline_intensity)), (0, y, width, 1))
        processed_surface.blit(scanline_surface, (0, 0))
    
    # 添加随机噪点
    if noise_intensity > 0:
        noise_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for _ in range(int(width * height * noise_intensity)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            alpha = random.randint(0, int(255 * 0.3))
            noise_surface.set_at((x, y), (255, 255, 255, alpha))
            noise_surface.set_at((x, y), (0, 0, 0, alpha))
        processed_surface.blit(noise_surface, (0, 0))
    
    # 添加烧屏效果（简单实现：叠加一个轻微的暗角）
    if burn_in:
        burn_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            for x in range(width):
                # 计算距离中心的距离，越靠近边缘透明度越高
                dx = abs(x - width//2) / (width//2)
                dy = abs(y - height//2) / (height//2)
                distance = (dx**2 + dy**2)**0.5
                alpha = int(50 * distance)
                burn_surface.set_at((x, y), (0, 0, 0, min(255, alpha)))
        processed_surface.blit(burn_surface, (0, 0))
    
    return processed_surface

def test_crt_effect():
    """测试CRT老化模拟效果"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 创建一个测试图像
    test_image = pygame.Surface((400, 400))
    test_image.fill((255, 255, 255))
    pygame.draw.circle(test_image, (255, 0, 0), (200, 200), 100)
    pygame.draw.circle(test_image, (0, 255, 0), (150, 150), 50)
    pygame.draw.circle(test_image, (0, 0, 255), (250, 250), 50)
    
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
        
        # 复制测试图像并应用CRT效果
        processed_image = test_image.copy()
        processed_image = crt_effect(processed_image, scanline_intensity, noise_intensity, burn_in=burn_in)
        
        screen.fill((0, 0, 0))
        screen.blit(processed_image, (200, 100))
        
        # 绘制参数信息
        from game_fonts import get_ui_font

        font = get_ui_font(24)
        text1 = font.render(f"扫描线强度: {scanline_intensity:.1f} (按1/2调整)", True, (255, 255, 255))
        text2 = font.render(f"噪点强度: {noise_intensity:.2f} (按3/4调整)", True, (255, 255, 255))
        text3 = font.render(f"烧屏效果: {'开启' if burn_in else '关闭'} (按5切换)", True, (255, 255, 255))
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 50))
        screen.blit(text3, (20, 80))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    test_crt_effect()