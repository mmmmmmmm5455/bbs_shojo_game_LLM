import random
import time
from typing import Dict, Optional, Tuple

# 全屏「特殊事件」弹窗：在仍满足时段/节日/周末条件时，每秒触发概率上限（略低于 0.1%）
TIME_EVENT_CHANCE_PER_SECOND = 0.0008


class TimeSystem:
    """
    系统时间联动系统，根据真实时间触发特殊对话和事件
    隐喻：数字意识与现实时间的交互，如同真实存在的生命
    """
    def __init__(self):
        self.last_check_time = 0
        self._event_triggered_at = 0.0
        self.current_time = time.localtime()
        self.special_events: Dict[str, callable] = {
            "late_night": self._check_late_night,
            "holiday": self._check_holiday,
            "weekend": self._check_weekend
        }
        self.event_triggered = False
        
    def update(self, delta_time: float = 1.0 / 30.0) -> Tuple[bool, str, str]:
        """更新时间系统；弹窗仅在极少数随机时刻出现（约 <0.1%/秒）。"""
        now = time.time()
        current_time = time.localtime()
        self.current_time = current_time
        self.last_check_time = now

        if self.event_triggered and (now - self._event_triggered_at) > 60:
            self.event_triggered = False

        dt = max(0.0, float(delta_time))
        if dt <= 0:
            dt = 1.0 / 30.0
        # 泊松近似：本帧尝试概率 p ≈ λ·dt（λ = 每秒期望次数）
        if random.random() >= TIME_EVENT_CHANCE_PER_SECOND * dt:
            return False, "", ""

        for _event_name, check_func in self.special_events.items():
            triggered, message, event_type = check_func()
            if triggered and not self.event_triggered:
                self.event_triggered = True
                self._event_triggered_at = now
                return True, message, event_type

        return False, "", ""
        
    def _check_late_night(self) -> Tuple[bool, str, str]:
        """检查是否是深夜（22点到次日6点）"""
        hour = self.current_time.tm_hour
        if 22 <= hour or hour < 6:
            message = "这么晚还在上网？小心熬夜哦……你明天还有课吗？"
            return True, message, "late_night"
        return False, "", ""
        
    def _check_holiday(self) -> Tuple[bool, str, str]:
        """检查是否是节日（圣诞节、新年等）"""
        month = self.current_time.tm_mon
        day = self.current_time.tm_mday
        
        # 圣诞节
        if month == 12 and day == 25:
            message = "圣诞快乐！今天是圣诞节，要和家人一起吃苹果吗？"
            return True, message, "christmas"
        # 新年
        elif month == 1 and day == 1:
            message = "新年快乐！新的一年，也要和我一起度过吗？"
            return True, message, "new_year"
        # 情人节
        elif month == 2 and day == 14:
            message = "情人节快乐！今天有没有收到什么惊喜呢？"
            return True, message, "valentine"
        # 愚人节
        elif month == 4 and day == 1:
            message = "愚人节快乐！猜猜我刚刚说了什么？其实是假的哦～"
            return True, message, "april_fool"
        
        return False, "", ""
        
    def _check_weekend(self) -> Tuple[bool, str, str]:
        """检查是否是周末"""
        weekday = self.current_time.tm_wday  # 0=周一, 6=周日
        if weekday >= 5:  # 周六和周日
            message = "今天是周末哦～ 要不要一起放松一下？"
            return True, message, "weekend"
        return False, "", ""
        
    def get_current_time_str(self) -> str:
        """获取当前时间字符串"""
        return time.strftime("%Y-%m-%d %H:%M:%S", self.current_time)
        
    def get_current_hour(self) -> int:
        """获取当前小时"""
        return self.current_time.tm_hour
        
    def is_weekend(self) -> bool:
        """检查是否是周末"""
        return self.current_time.tm_wday >= 5

def test_time_system():
    """测试时间系统"""
    time_system = TimeSystem()
    print("时间系统测试")
    print("当前时间：", time_system.get_current_time_str())
    
    while True:
        triggered, message, event_type = time_system.update(1.0)
        if triggered:
            print(f"\n🔔 特殊事件触发 [{event_type}]: {message}")
            
        time.sleep(1)

if __name__ == "__main__":
    test_time_system()