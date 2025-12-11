# app/ui/main_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect, 
                             QFrame, QListWidgetItem, QAbstractItemView)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QColor, QFont, QFontMetrics
from app.config import *
from app.ui.components import CleanCalendar, TaskItemWidget

class ModernCalendarWindow(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 450)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(root_layout)

        self.container = QFrame()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR};
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)
        root_layout.addWidget(self.container)

        content_layout = QHBoxLayout(self.container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        self.calendar = CleanCalendar(self.data_manager)
        self.calendar.selectionChanged.connect(self.update_task_list)
        self.calendar.currentPageChanged.connect(lambda: self.calendar.update())
        content_layout.addWidget(self.calendar, 4)

        right_panel = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        # 日期标题
        self.date_title = QLabel("今日待办")
        self.date_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        
        close_btn = QPushButton("×")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("""
            QPushButton { color: #A0AEC0; border: none; font-size: 20px; font-weight: bold;}
            QPushButton:hover { color: #E53E3E; }
        """)
        
        header_layout.addWidget(self.date_title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        right_panel.addLayout(header_layout)

        # --- 新增：今日投入时长显示 ---
        self.work_time_label = QLabel("🔥 今日投入: 0h 0m")
        self.work_time_label.setStyleSheet(f"color: #FF9966; font-size: 13px; font-weight: bold; margin-bottom: 5px;")
        right_panel.addWidget(self.work_time_label)
        # ---------------------------

        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.task_list.setStyleSheet(f"""
            QListWidget {{ border: none; background: transparent; }}
            QListWidget::item {{ 
                background-color: {CARD_BG}; 
                border-radius: 8px; 
                margin-bottom: 8px;
                border: 1px solid transparent;
            }}
            QListWidget::item:hover {{ 
                border: 1px solid {ACCENT_COLOR}; 
            }}
        """)
        right_panel.addWidget(self.task_list)

        input_box = QFrame()
        input_box.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 20px;")
        input_layout = QHBoxLayout(input_box)
        input_layout.setContentsMargins(5, 5, 5, 5)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText(" 添加新任务...")
        self.input_line.setStyleSheet("border: none; background: transparent; font-size: 14px;")
        self.input_line.returnPressed.connect(self.add_task)

        self.add_btn = QPushButton("＋")
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_task)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR}; color: white; border-radius: 16px; font-size: 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #5A67D8; }}
        """)
        
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.add_btn)
        right_panel.addWidget(input_box)
        
        self.del_link = QPushButton("清理已完成")
        self.del_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_link.setStyleSheet(f"""
            QPushButton {{ color: {TEXT_SECONDARY}; border: none; text-align: right; font-size: 12px; }}
            QPushButton:hover {{ color: {DANGER_COLOR}; text-decoration: underline; }}
        """)
        self.del_link.clicked.connect(self.clear_completed_tasks)
        right_panel.addWidget(self.del_link, alignment=Qt.AlignmentFlag.AlignRight)

        content_layout.addLayout(right_panel, 3)
        self.drag_pos = None

    def update_task_list(self):
        date = self.calendar.selectedDate()
        date_str = date.toString(Qt.DateFormat.ISODate)
        display_str = date.toString("M月d日 dddd")
        
        self.date_title.setText(display_str)
        self.task_list.clear()
        
        # --- 获取并显示工作时长 ---
        seconds = self.data_manager.get_work_time(date_str)
        if seconds > 0:
            h, rem = divmod(seconds, 3600)
            m = rem // 60
            self.work_time_label.setText(f"🔥 今日投入: {h}h {m}m")
            self.work_time_label.show()
        else:
            self.work_time_label.hide() # 如果没有记录，隐藏标签，保持界面干净
        # ------------------------
        
        tasks = self.data_manager.get_tasks(date_str)
        
        list_width = self.task_list.viewport().width()
        text_available_width = list_width - 80 
        if text_available_width < 100: text_available_width = 200

        font = QFont("Microsoft YaHei UI", 15)
        fm = QFontMetrics(font)

        for index, t in enumerate(tasks):
            item = QListWidgetItem(self.task_list)
            
            text = t.get('text', '')
            rect = fm.boundingRect(QRect(0, 0, text_available_width, 1000), 
                                   Qt.TextFlag.TextWordWrap, text)
            
            row_height = max(50, rect.height() + 25) 
            item.setSizeHint(QSize(list_width - 10, row_height)) 
            
            callback = lambda i=index: self.on_task_toggled(i)
            widget = TaskItemWidget(t, callback)
            self.task_list.setItemWidget(item, widget)
            
        self.calendar.update() 

    def on_task_toggled(self, index):
        date_str = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
        self.data_manager.toggle_task_status(date_str, index)
        self.update_task_list()

    def add_task(self):
        text = self.input_line.text().strip()
        if text:
            date_str = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
            self.data_manager.add_task(date_str, text)
            self.input_line.clear()
            self.update_task_list()

    def clear_completed_tasks(self):
        date_str = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
        tasks = self.data_manager.get_tasks(date_str)
        # 兼容性处理：如果tasks是字典(new struct)或者列表(old struct)
        # data_manager 里的 remove_task 已经处理了，这里只需要按索引删
        # 但因为remove_task需要索引，我们先获取列表长度
        
        # 为了安全，这里重新获取一次纯列表
        task_list = tasks if isinstance(tasks, list) else [] # 实际上 get_tasks 已经返回列表了
        
        for i in range(len(task_list) - 1, -1, -1):
            if task_list[i].get('completed'):
                self.data_manager.remove_task(date_str, i)
        self.update_task_list()

    def showEvent(self, event):
        self.update_task_list()
        super().showEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.container.geometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
    def mouseReleaseEvent(self, event):
        self.drag_pos = None