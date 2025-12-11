# app/ui/floating_ball.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMenu, QApplication )
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices, QAction
from app.config import *
import time
import os

from app.ui.ball_body import BallBody
from app.ui.ball_dialogs import CustomTimeDialog

class LiveDateBall(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 保持和 BallBody 一致的尺寸
        self.setFixedSize(200, 200) 
        self.move(100, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.body = BallBody(data_manager=parent_window.data_manager)
        layout.addWidget(self.body)

        self.old_pos = None
        self.click_start_pos = None
        self.click_start_time = 0
        self.is_locked = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_date_update)
        self.timer.start(60000) 

    def check_date_update(self):
        if self.body.mode == "NORMAL":
            self.body.update()

    def mousePressEvent(self, event):
        if self.is_locked and event.button() == Qt.MouseButton.LeftButton:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.click_start_pos = event.globalPosition().toPoint()
            self.click_start_time = time.time()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        
        if event.button() == Qt.MouseButton.LeftButton:
            elapsed_time = time.time() - self.click_start_time
            move_distance = 0
            if self.click_start_pos:
                current_pos = event.globalPosition().toPoint()
                move_distance = (current_pos - self.click_start_pos).manhattanLength()

            if elapsed_time < 0.25 and move_distance < 5:
                self.toggle_calendar()
        
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.is_locked: return
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 6px 25px; margin: 2px; border-radius: 4px; color: #4A5568; font-family: "Microsoft YaHei UI"; font-size: 13px; }}
            QMenu::item:selected {{ background-color: {ACCENT_COLOR}; color: white; }}
            QMenu::separator {{ height: 1px; background: #E2E8F0; margin: 4px 10px; }}
        """)
        
        if self.body.mode == "FOCUS":
             menu.addAction("⏹ 停止专注").triggered.connect(self.body.stop_all)
        elif self.body.mode == "WORK":
             menu.addAction("⏹ 停止工作 (保存时间)").triggered.connect(self.body.stop_all)
        else:
            menu.addAction("🔥 开启工作模式").triggered.connect(self.body.start_work)
            menu.addSeparator()
            focus_menu = menu.addMenu("🍅 开始专注")
            focus_menu.addAction("25 分钟").triggered.connect(lambda: self.body.start_focus(25))
            focus_menu.addAction("45 分钟").triggered.connect(lambda: self.body.start_focus(45))
            focus_menu.addSeparator()
            focus_menu.addAction("⌨️ 自定义时长...").triggered.connect(self.set_custom_focus)
        
        menu.addSeparator()
        
        # 移除了动态调整球体尺寸的功能，因为现在使用了固定画布逻辑
        # 如果需要调整，需要重写更复杂的逻辑，暂时先精简掉以保证稳定性
        # appearance_menu = menu.addMenu("🎨 外观调节")
        
        opacity_menu = menu.addMenu("💧 日历透明度")
        opacity_menu.addAction("100%").triggered.connect(lambda: self.set_calendar_opacity(1.0))
        opacity_menu.addAction("90%").triggered.connect(lambda: self.set_calendar_opacity(0.9))
        opacity_menu.addAction("80%").triggered.connect(lambda: self.set_calendar_opacity(0.8))

        lock_action = QAction("🔒 锁定位置", menu)
        lock_action.setCheckable(True)
        lock_action.setChecked(self.is_locked)
        lock_action.triggered.connect(self.toggle_lock)
        menu.addAction(lock_action)

        settings_menu = menu.addMenu("⚙️ 更多设置")
        settings_menu.addAction("📂 打开数据文件夹").triggered.connect(self.open_data_folder)
        settings_menu.addAction("📍 重置悬浮球位置").triggered.connect(lambda: self.move(100, 100))
        
        menu.addSeparator()
        menu.addAction("🚪 退出程序").triggered.connect(QApplication.instance().quit)
        
        menu.exec(pos)

    def set_custom_focus(self):
        dialog = CustomTimeDialog(self)
        geo = self.geometry()
        screen_geo = self.screen().geometry()
        # 弹窗位置微调
        dialog_x = geo.x() + 150
        if dialog_x + dialog.width() > screen_geo.right():
            dialog_x = geo.x() - dialog.width() - 20
        dialog.move(dialog_x, geo.y())
        if dialog.exec():
            minutes = dialog.get_value()
            self.body.start_focus(minutes)

    def set_calendar_opacity(self, opacity):
        self.parent_window.setWindowOpacity(opacity)

    def toggle_lock(self, checked):
        self.is_locked = checked

    def open_data_folder(self):
        path = os.getcwd()
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def toggle_calendar(self):
        if self.parent_window.isVisible():
            self.parent_window.hide()
        else:
            geo = self.geometry()
            win_w = self.parent_window.width()
            screen_w = self.screen().geometry().width()
            
            # 因为外壳现在很大(200)，所以视觉上的球体在中心
            # 偏移量需要调整，让日历紧挨着视觉球体
            offset_x = 100 + 40 + 10 # 中心点(100) + 半径(40) + 间距(10)
            
            target_x = geo.x() + offset_x
            if target_x + win_w > screen_w:
                # 显示在左边
                target_x = geo.x() + (100 - 40 - 10) - win_w
            
            self.parent_window.move(target_x, geo.y() + 50)
            self.parent_window.show()
            self.parent_window.raise_()