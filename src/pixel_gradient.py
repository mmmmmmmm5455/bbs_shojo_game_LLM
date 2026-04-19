import pygame
import math

def pixel_gradient(image_path, memory_fragments, target_width=None, target_height=None):
    """
    根据记忆碎片数量动态调整图像的精度，实现从像素化到清晰的平滑过渡
    :param image_path: 图像文件路径
    :param memory_fragments: 记忆碎片数量（0-100），0表示完全像素化，100表示完全清晰
    :param target_width: 目标宽度，None则使用原始图像宽度
    :param target_height: 目标高度，None则使用原始图像高度
    :return: 处理后的pygame.Surface对象
    """
    # 加载原始图像
    original_image = pygame.image.load(image_path).convert_alpha()
    original_width, original_height = original_image.get_size()
    
    # 设置目标尺寸
    if target_width is None:
        target_width = original_width
    if target_height is None:
        target_height = original_height
    
    # 计算缩放比例：memory_fragments从0到100，缩放比例从0.1到1.0
    scale = 0.1 + (memory_fragments / 100) * 0.9
    
    # 计算小尺寸图像的尺寸
    small_width = max(1, int(original_width * scale))
    small_height = max(1, int(original_height * scale))
    
    # 缩小图像
    small_image = pygame.transform.scale(original_image, (small_width, small_height))
    
    # 如果需要的话，再放大到目标尺寸
    if scale < 1.0:
        # 使用最近邻缩放保持像素化效果
        processed_image = pygame.transform.scale(small_image, (target_width, target_height))
    else:
        # 原始尺寸，直接使用
        processed_image = original_image
    
    return processed_image

def test_pixel_gradient():
    """测试像素精度渐变系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 加载测试图像
    test_image_path = "assets/images/test_image.png"
    # 如果没有测试图像，使用一个简单的矩形
    try:
        test_image = pixel_gradient(test_image_path, 0, 400, 400)
    except:
        # 创建一个简单的测试图像
        test_image = pygame.Surface((100, 100))
        test_image.fill((255, 0, 0))
        pygame.draw.circle(test_image, (0, 255, 0), (50, 50), 30)
        test_image = pixel_gradient_from_surface(test_image, 0, 400, 400)
    
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
        
        # 更新图像
        processed_image = pixel_gradient_from_surface(test_image, memory_fragments, 400, 400)
        
        screen.fill((0, 0, 0))
        screen.blit(processed_image, (200, 100))
        
        # 绘制进度条
        progress_bar_width = 400
        progress_bar_height = 20
        progress = memory_fragments / 100
        pygame.draw.rect(screen, (255, 255, 255), (200, 550, progress_bar_width, progress_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (200, 550, int(progress_bar_width * progress), progress_bar_height))
        
        # 绘制文字
        from game_fonts import get_ui_font

        font = get_ui_font(36)
        text = font.render(f"记忆碎片数量: {memory_fragments}/100", True, (255, 255, 255))
        screen.blit(text, (200, 50))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

def pixel_gradient_from_surface(surface, memory_fragments, target_width=None, target_height=None):
    """
    从已有的pygame.Surface对象创建像素渐变效果
    """
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
    test_pixel_gradient()