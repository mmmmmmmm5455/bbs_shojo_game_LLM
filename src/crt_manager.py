import pygame
import random
import math
from typing import Tuple, Optional

from game_fonts import get_ui_font

class CRTManager:
    """
    CRT老化模拟管理器，管理老化程度和随机变化
    隐喻时间的伤痕：老化程度越高，显示器越陈旧，时间痕迹越明显
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.aging_level = 0.0  # 0-100%，0为全新，100为严重老化
        self.scanline_offset = random.uniform(0, 1)  # 扫描线偏移，用于随机变化
        self.last_aging_change = 0
        self.quality = "low"  # low/medium/high
        self._scanline_cache: Optional[pygame.Surface] = None
        self._noise_cache: Optional[pygame.Surface] = None
        self._cache_size: Tuple[int, int] = (0, 0)
        self._cache_tick = 0
        
        # 预定义不同老化程度的参数
        self.aging_params = {
            0: {"scanline_intensity": 0.1, "noise_intensity": 0.01, "color_bias": (1.0, 1.0, 1.0), "burn_in": 0.0},
            25: {"scanline_intensity": 0.15, "noise_intensity": 0.03, "color_bias": (1.02, 1.01, 0.99), "burn_in": 0.1},
            50: {"scanline_intensity": 0.25, "noise_intensity": 0.05, "color_bias": (1.05, 1.02, 0.98), "burn_in": 0.3},
            75: {"scanline_intensity": 0.35, "noise_intensity": 0.08, "color_bias": (1.08, 1.03, 0.97), "burn_in": 0.6},
            100: {"scanline_intensity": 0.5, "noise_intensity": 0.12, "color_bias": (1.1, 1.05, 0.95), "burn_in": 1.0},
        }
        
    def set_aging_level(self, level: float):
        """设置老化程度（0-100）"""
        self.aging_level = max(0.0, min(100.0, level))
        
    def get_current_params(self) -> Tuple[float, float, Tuple[float, float, float], float]:
        """根据当前老化程度获取CRT参数"""
        # 线性插值获取参数
        if self.aging_level >= 100:
            params = self.aging_params[100]
        elif self.aging_level <= 0:
            params = self.aging_params[0]
        else:
            # 找到相邻的两个等级
            lower = int(self.aging_level // 25) * 25
            upper = lower + 25
            if upper > 100:
                upper = 100
                
            t = (self.aging_level - lower) / (upper - lower)
            
            params = {}
            for key in self.aging_params[lower]:
                a, b = self.aging_params[lower][key], self.aging_params[upper][key]
                if isinstance(a, tuple):
                    params[key] = tuple(
                        a[i] * (1 - t) + b[i] * t for i in range(len(a))
                    )
                else:
                    params[key] = a * (1 - t) + b * t
                
        return (
            params["scanline_intensity"],
            params["noise_intensity"],
            params["color_bias"],
            params["burn_in"] > 0.5  # 烧屏效果开关
        )
        
    def apply_crt_effect(self, surface: pygame.Surface, aging_override: Optional[float] = None) -> pygame.Surface:
        """应用CRT效果，支持老化程度覆盖"""
        if aging_override is not None:
            original_aging = self.aging_level
            self.set_aging_level(aging_override)
            
        scanline_intensity, noise_intensity, color_bias, burn_in = self.get_current_params()
        # 低成本实现：降采样 + 分层叠加（避免逐像素）
        src_w, src_h = surface.get_size()
        if self.quality == "high":
            scale = 1.0
        elif self.quality == "medium":
            scale = 0.5
        else:
            scale = 0.34

        w = max(1, int(src_w * scale))
        h = max(1, int(src_h * scale))

        base = pygame.transform.smoothscale(surface, (w, h)) if scale != 1.0 else surface.copy()
        processed = base.convert_alpha() if base.get_flags() & pygame.SRCALPHA else base.convert()

        # 颜色偏置：用乘色近似
        if color_bias != (1.0, 1.0, 1.0):
            tint = pygame.Surface((w, h), pygame.SRCALPHA)
            tr = min(255, int(255 * color_bias[0]))
            tg = min(255, int(255 * color_bias[1]))
            tb = min(255, int(255 * color_bias[2]))
            tint.fill((tr, tg, tb, 255))
            processed.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 缓存层更新（每隔 N 帧）
        self._cache_tick += 1
        if self._cache_size != (w, h):
            self._cache_size = (w, h)
            self._scanline_cache = None
            self._noise_cache = None

        if scanline_intensity > 0 and (self._scanline_cache is None or self._cache_tick % 20 == 0):
            scan = pygame.Surface((w, h), pygame.SRCALPHA)
            y0 = int(self.scanline_offset * 2) % 2
            alpha = int(255 * scanline_intensity)
            for yy in range(y0, h, 2):
                pygame.draw.rect(scan, (0, 0, 0, alpha), (0, yy, w, 1))
            self._scanline_cache = scan

        if noise_intensity > 0 and (self._noise_cache is None or self._cache_tick % 10 == 0):
            noise = pygame.Surface((w, h), pygame.SRCALPHA)
            # 噪点量与尺寸成正比，但在降采样后成本很低
            total = int(w * h * noise_intensity * 0.5)
            max_a = int(255 * 0.25 * (1 + self.aging_level / 120))
            for _ in range(total):
                x = random.randint(0, w - 1)
                y = random.randint(0, h - 1)
                a = random.randint(0, max_a)
                c = 255 if random.random() > 0.5 else 0
                noise.set_at((x, y), (c, c, c, a))
            self._noise_cache = noise

        if self._scanline_cache is not None:
            processed.blit(self._scanline_cache, (0, 0))
        if self._noise_cache is not None:
            processed.blit(self._noise_cache, (0, 0))

        # 烧屏：用边缘暗角近似（低分辨率计算一次）
        if burn_in and self.quality != "low":
            vignette = pygame.Surface((w, h), pygame.SRCALPHA)
            cx = w / 2.0
            cy = h / 2.0
            max_r = (cx * cx + cy * cy) ** 0.5
            step = 4 if self.quality == "medium" else 2
            for yy in range(0, h, step):
                for xx in range(0, w, step):
                    dx = xx - cx
                    dy = yy - cy
                    r = (dx * dx + dy * dy) ** 0.5 / max_r
                    a = int(60 * r * (1 + self.aging_level / 100))
                    pygame.draw.rect(vignette, (0, 0, 0, min(255, a)), (xx, yy, step, step))
            processed.blit(vignette, (0, 0))

        # 轻微几何失真：整体平移
        if self.aging_level > 50:
            pan = int(math.sin((h // 2) * 0.01 + self.scanline_offset) * 2 * (self.aging_level / 100))
            shifted = pygame.Surface((w, h), pygame.SRCALPHA)
            shifted.blit(processed, (pan, 0))
            processed = shifted

        # 还原到原尺寸
        processed_surface = (
            pygame.transform.smoothscale(processed, (src_w, src_h)) if scale != 1.0 else processed
        )
            
        if aging_override is not None:
            self.set_aging_level(original_aging)
            
        return processed_surface
        
    def randomize_scanline_offset(self):
        """随机化扫描线偏移，模拟不同显示器的差异"""
        self.scanline_offset = random.uniform(0, 1)
        
    def update(self, delta_time: float = 0.0):
        """更新CRT管理器状态"""
        # 每10秒随机轻微变化老化程度
        if delta_time > 0:
            self.last_aging_change += delta_time
            if self.last_aging_change > 10:
                self.set_aging_level(self.aging_level + random.uniform(-5, 5))
                self.last_aging_change = 0

def test_crt_manager():
    """测试CRT管理器"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 创建测试图像
    test_image = pygame.Surface((400, 400))
    test_image.fill((255, 255, 255))
    pygame.draw.circle(test_image, (255, 0, 0), (200, 200), 100)
    pygame.draw.circle(test_image, (0, 255, 0), (150, 150), 50)
    pygame.draw.circle(test_image, (0, 0, 255), (250, 250), 50)
    
    crt_manager = CRTManager(400, 400)
    aging_level = 50.0
    running = True
    
    while running:
        delta_time = clock.tick(30) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    aging_level = max(0, aging_level - 10)
                elif event.key == pygame.K_RIGHT:
                    aging_level = min(100, aging_level + 10)
                elif event.key == pygame.K_r:
                    crt_manager.randomize_scanline_offset()
                    print(f"随机扫描线偏移: {crt_manager.scanline_offset:.2f}")
                    
        crt_manager.set_aging_level(aging_level)
        crt_manager.update(delta_time)
        
        processed_image = crt_manager.apply_crt_effect(test_image)
        
        screen.fill((0, 0, 0))
        screen.blit(processed_image, (200, 100))
        
        # 绘制参数信息
        font = get_ui_font(24)
        text1 = font.render(f"老化程度: {int(aging_level)}% (按左右箭头调整)", True, (255, 255, 255))
        text2 = font.render(f"扫描线偏移: {crt_manager.scanline_offset:.2f} (按R随机化)", True, (255, 255, 255))
        text3 = font.render(f"扫描线强度: {crt_manager.get_current_params()[0]:.2f}", True, (255, 255, 255))
        text4 = font.render(f"噪点强度: {crt_manager.get_current_params()[1]:.2f}", True, (255, 255, 255))
        
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 50))
        screen.blit(text3, (20, 80))
        screen.blit(text4, (20, 110))
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    test_crt_manager()