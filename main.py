# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# 引入我们拆分好的模块
from app.data_manager import TaskManager
from app.ui.main_window import ModernCalendarWindow
from app.ui.floating_ball import LiveDateBall

if __name__ == "__main__":
    # 高分屏适配
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    # 1. 初始化数据管理器
    manager = TaskManager()
    
    # 2. 初始化主窗口 (默认隐藏)
    calendar_win = ModernCalendarWindow(manager)
    
    # 3. 初始化悬浮球
    ball = LiveDateBall(calendar_win)
    ball.show()
    
    sys.exit(app.exec())