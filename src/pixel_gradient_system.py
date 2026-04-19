import os
import math
import random
import pygame
from typing import List, Tuple

class PixelGradientSystem:
    """
    像素精度渐变系统，根据记忆碎片数量切换不同精度的立绘
    隐喻记忆复苏：像素精度越高，记忆越清晰
    """
    def __init__(self, assets_dir: str | None = None):
        if assets_dir is None:
            from game_paths import ASSETS_DIR

            assets_dir = os.path.join(ASSETS_DIR, "images")
        self.assets_dir = assets_dir
        self.memory_fragments = 0
        # 预定义不同精度的立绘，从低到高
        self.art_assets: List[Tuple[int, pygame.Surface]] = []
        self._load_assets()
        
    def _load_assets(self):
        """加载不同精度的立绘资源"""
        # 假设资源文件命名为：character_16x16.png, character_32x32.png, character_64x64.png, character_128x128.png
        asset_names = ["16x16", "32x32", "64x64", "128x128"]
        for size in asset_names:
            asset_path = os.path.join(self.assets_dir, f"character_{size}.png")
            if os.path.exists(asset_path):
                try:
                    surface = pygame.image.load(asset_path).convert_alpha()
                    self.art_assets.append((int(size.split("x")[0]), surface))
                except Exception as e:
                    print(f"加载立绘资源失败 {asset_path}: {e}")
        
        # 如果没有实际资源，创建测试资源
        if not self.art_assets:
            self._create_test_assets()
            
    def _create_test_assets(self):
        """创建测试用的不同精度立绘"""
        sizes = [16, 32, 64, 128]
        for size in sizes:
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            # 绘制简单的少女形象
            pygame.draw.circle(surface, (255, 192, 203), (size//2, size//3), size//4)  # 头部
            pygame.draw.rect(surface, (255, 192, 203), (size//3, size//2, size//3, size//3))  # 身体
            pygame.draw.circle(surface, (0, 0, 0), (size//2 - size//6, size//3 - size//8), size//12)  # 眼睛
            pygame.draw.circle(surface, (0, 0, 0), (size//2 + size//6, size//3 - size//8), size//12)  # 眼睛
            self.art_assets.append((size, surface))
            
    def set_memory_fragments(self, fragments: int):
        """设置记忆碎片数量，0-100"""
        self.memory_fragments = max(0, min(100, fragments))
        
    def get_current_art(self, target_width: int = None, target_height: int = None) -> pygame.Surface:
        """根据记忆碎片数量获取立绘；在相邻精度档之间插值混合，碎片增加时连续变清晰。"""
        if not self.art_assets:
            return pygame.Surface((1, 1))

        n = len(self.art_assets)
        tw, th = target_width, target_height
        if not tw or not th:
            tw, th = self.art_assets[-1][1].get_size()

        if n == 1:
            return pygame.transform.scale(self.art_assets[0][1], (tw, th))

        # 0..100 映射到 [0, n-1]，在相邻两档间按 frac 混合
        t = (self.memory_fragments / 100.0) * (n - 1)
        i0 = int(math.floor(t))
        i1 = min(i0 + 1, n - 1)
        frac = max(0.0, min(1.0, t - i0))

        s0 = pygame.transform.scale(self.art_assets[i0][1], (tw, th))
        if frac < 0.02 or i0 == i1:
            return s0

        s1 = pygame.transform.scale(self.art_assets[i1][1], (tw, th))
        blend = s0.copy()
        s1.set_alpha(int(255 * frac))
        blend.blit(s1, (0, 0))
        return blend
        
    def get_pixel_jitter_art(self, intensity: float = 0.1) -> pygame.Surface:
        """获取带有像素抖动效果的立绘，用于情绪不稳定时"""
        base_art = self.get_current_art()
        width, height = base_art.get_size()
        jittered = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y in range(height):
            for x in range(width):
                color = base_art.get_at((x, y))
                # 添加随机抖动
                if random.random() < intensity:
                    offset_x = max(0, min(width-1, x + random.randint(-2, 2)))
                    offset_y = max(0, min(height-1, y + random.randint(-2, 2)))
                    jittered.set_at((x, y), base_art.get_at((offset_x, offset_y)))
                else:
                    jittered.set_at((x, y), color)
                    
        return jittered

# 示例使用
if __name__ == "__main__":
    import random
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    gradient_system = PixelGradientSystem()
    
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
                    
        gradient_system.set_memory_fragments(memory_fragments)
        art = gradient_system.get_current_art(400, 400)
        
        screen.fill((0, 0, 0))
        screen.blit(art, (0, 0))
        
        from game_fonts import get_ui_font

        font = get_ui_font(24)
        text = font.render(f"记忆碎片: {memory_fragments}/100", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()