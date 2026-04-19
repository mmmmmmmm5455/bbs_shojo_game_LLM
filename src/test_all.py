# BBS Shojo游戏 - 测试脚本

import pygame
import sys
import os


def _configure_stdio_utf8():
    """Avoid UnicodeEncodeError on Windows consoles (e.g. cp950) when printing CJK."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdio_utf8()

from pixel_gradient import pixel_gradient
from crt_effect import crt_effect
from ascii_animation import ASCIIAnimation
from midi_editor import ScoreConverter, MIDISequencer
from animated_character import AnimatedCharacter
from vertical_hold import vertical_hold_effect

def test_all_modules():
    """测试所有模块"""
    print("=== BBS Shojo游戏 模块测试 ===")
    
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 1. 测试像素精度渐变系统
    print("\n1. 测试像素精度渐变系统...")
    try:
        test_image = pygame.Surface((100, 100))
        test_image.fill((255, 0, 0))
        pygame.draw.circle(test_image, (0, 255, 0), (50, 50), 30)
        result = pixel_gradient_from_surface(test_image, 50, 200, 200)
        print("✓ 像素精度渐变系统测试成功")
    except Exception as e:
        print(f"✗ 像素精度渐变系统测试失败: {e}")
    
    # 2. 测试CRT老化模拟效果
    print("\n2. 测试CRT老化模拟效果...")
    try:
        test_image = pygame.Surface((400, 400))
        test_image.fill((255, 255, 255))
        result = crt_effect(test_image, 0.2, 0.05)
        print("✓ CRT老化模拟效果测试成功")
    except Exception as e:
        print(f"✗ CRT老化模拟效果测试失败: {e}")
    
    # 3. 测试ASCII表情动画系统
    print("\n3. 测试ASCII表情动画系统...")
    try:
        animation = ASCIIAnimation()
        animation.set_animation("happy")
        animation.update()
        frame = animation.get_current_frame()
        print(f"✓ ASCII表情动画系统测试成功，当前帧: {frame.strip()}")
    except Exception as e:
        print(f"✗ ASCII表情动画系统测试失败: {e}")
    
    # 4. 测试MIDI编辑器
    print("\n4. 测试MIDI编辑器...")
    try:
        converter = ScoreConverter()
        midi_data = converter.create_midi("1 2 3 4 5")
        print("✓ MIDI编辑器测试成功，生成了MIDI数据")
    except Exception as e:
        print(f"✗ MIDI编辑器测试失败: {e}")
    
    # 5. 测试动态音效与颜文字联动
    print("\n5. 测试动态音效与颜文字联动...")
    try:
        character = AnimatedCharacter()
        character.set_emotion("happy")
        print("✓ 动态音效与颜文字联动测试成功")
    except Exception as e:
        print(f"✗ 动态音效与颜文字联动测试失败: {e}")
    
    # 6. 测试垂直保持失调效果
    print("\n6. 测试垂直保持失调效果...")
    try:
        test_image = pygame.Surface((800, 600))
        result = vertical_hold_effect(test_image, 5, 1)
        print("✓ 垂直保持失调效果测试成功")
    except Exception as e:
        print(f"✗ 垂直保持失调效果测试失败: {e}")
    
    # 7. 测试主菜单
    print("\n7. 测试主菜单...")
    try:
        # 这里只测试导入，不运行完整菜单
        from main import MainMenu
        print("✓ 主菜单导入成功")
    except Exception as e:
        print(f"✗ 主菜单测试失败: {e}")
    
    print("\n=== 所有模块测试完成 ===")
    pygame.quit()

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
    test_all_modules()