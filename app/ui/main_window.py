# app/ui/main_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect, 
                             QFrame, QListWidgetItem, QAbstractItemView, QComboBox)
from PyQt6.QtCore import Qt, QSize, QRect, QDate
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon
from app.config import *
from app.ui.components import CleanCalendar, TaskItemWidget

class ModernCalendarWindow(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        # 无边框窗口设置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 480) # 高度稍微增加以容纳自定义头部

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(root_layout)

        # 主容器（带阴影圆角）
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

        # --- 左侧区域：自定义导航栏 + 日历 ---
        calendar_container = QVBoxLayout()
        calendar_container.setSpacing(5)
        
        # 1. 初始化日历
        self.calendar = CleanCalendar(self.data_manager)
        self.calendar.selectionChanged.connect(self.update_task_list)
        # 翻页时同步更新下拉框
        self.calendar.currentPageChanged.connect(self.update_headers_from_calendar)

        # 2. 构建自定义头部 (年份/月份下拉框)
        self.setup_custom_header(calendar_container)

        # 3. 添加日历控件
        calendar_container.addWidget(self.calendar)
        
        content_layout.addLayout(calendar_container, 4)

        # --- 右侧区域：任务管理 ---
        right_panel = QVBoxLayout()
        
        # 顶部标题栏
        header_layout = QHBoxLayout()
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

        # 工作时长显示
        self.work_time_label = QLabel("🔥 今日投入: 0h 0m")
        self.work_time_label.setStyleSheet(f"color: #FF9966; font-size: 13px; font-weight: bold; margin-bottom: 5px;")
        right_panel.addWidget(self.work_time_label)

        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.task_list.setStyleSheet(f"""
            QListWidget {{ border: none; background: transparent; outline: none;}}
            QListWidget::item {{ 
                background-color: {CARD_BG}; 
                border-radius: 8px; 
                margin-bottom: 8px;
                border: 1px solid transparent;
            }}
            QListWidget::item:hover {{ 
                border: 1px solid {ACCENT_COLOR}; 
            }}
            QListWidget::item:selected {{
                outline: none;
                border: 1px solid {ACCENT_COLOR};
                background-color: {CARD_BG}; /* 保持背景不变，或者稍微变色 */
                color: {TEXT_PRIMARY};
            }}
        """)
        right_panel.addWidget(self.task_list)

        # 输入框区域
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
        
        # 清理按钮
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

    # --- 自定义导航栏构建逻辑 ---
    def setup_custom_header(self, parent_layout):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # --- 1. 样式表 (修复内容变成点的问题) ---
        combo_style = f"""
            /* 主体样式 */
            QComboBox {{
                border: none;
                background-color: transparent;
                color: {TEXT_PRIMARY};
                font-family: "Microsoft YaHei UI";
                font-size: 16px;     
                font-weight: bold;
                padding: 2px 10px;   
                border-radius: 6px;
                /* 稍微给个最小宽度，防止主体也被挤压 */
                min-width: 60px; 
            }}

            QComboBox:hover {{ background-color: #EDF2F7; }}
            QComboBox:on {{ background-color: #E2E8F0; }}

            /* 隐藏下拉按钮 */
            QComboBox::drop-down {{
                border: none;
                background: transparent;
                width: 0px; 
            }}
            QComboBox::down-arrow {{ image: none; border: none; }}

            /* 弹出的下拉列表 */
            QComboBox QAbstractItemView {{
                border: 1px solid #E2E8F0;
                background-color: white;
                border-radius: 6px;
                outline: none;
                padding: 4px;
                
                /* ⬇️ 【核心修复】强制给弹出菜单一个最小宽度，防止文字被压缩成点 */
                min-width: 100px; 
            }}

            /* 列表项 */
            QComboBox QAbstractItemView::item {{
                height: 30px;
                border-radius: 4px;
                padding-left: 10px; /* 给文字留足空间 */
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}

            QComboBox QAbstractItemView::item:hover, 
            QComboBox QAbstractItemView::item:selected {{
                background-color: {ACCENT_COLOR}; 
                color: white;
            }}
            
            QComboBox QAbstractItemView QScrollBar:vertical {{
                width: 4px;
                background: transparent;
            }}
            QComboBox QAbstractItemView QScrollBar::handle:vertical {{
                background: #CBD5E0;
                border-radius: 2px;
            }}
        """
        
        btn_style = f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_PRIMARY}; border: none; font-size: 16px; font-weight: bold;
            }}
            QPushButton:hover {{ color: {ACCENT_COLOR}; }}
        """

        # --- 2. 年份下拉框 (修复年份范围) ---
        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet(combo_style)
        self.year_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 获取当前年份
        current_year = QDate.currentDate().year()
        
        # ⬇️ 【修改这里】范围扩大：从 2000 年到 2050 年
        # 也可以改成 range(current_year - 10, current_year + 11) 前后10年
        for year in range(2000, 2051):
            self.year_combo.addItem(str(year), year)
            
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self.on_header_changed)

        # --- 3. 月份下拉框 ---
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet(combo_style)
        self.month_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        months = ["一月", "二月", "三月", "四月", "五月", "六月", 
                  "七月", "八月", "九月", "十月", "十一月", "十二月"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.currentIndexChanged.connect(self.on_header_changed)

        # --- 4. 翻页按钮 ---
        prev_btn = QPushButton("<")
        prev_btn.setFixedSize(30, 30)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.setStyleSheet(btn_style)
        prev_btn.clicked.connect(self.calendar.showPreviousMonth)

        next_btn = QPushButton(">")
        next_btn.setFixedSize(30, 30)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setStyleSheet(btn_style)
        next_btn.clicked.connect(self.calendar.showNextMonth)

        header_layout.addWidget(prev_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.year_combo)
        header_layout.addWidget(self.month_combo)
        header_layout.addStretch()
        header_layout.addWidget(next_btn)

        parent_layout.addLayout(header_layout)

    def on_header_changed(self):
        try:
            year = int(self.year_combo.currentText())
            month = self.month_combo.currentIndex() + 1
            self.calendar.setCurrentPage(year, month)
        except:
            pass

    def update_headers_from_calendar(self, year, month):
        # 暂时阻塞信号，防止循环触发
        self.year_combo.blockSignals(True)
        self.month_combo.blockSignals(True)
        
        # 确保年份在下拉框范围内，如果超出则动态添加（简单处理：如果在范围内才更新）
        idx = self.year_combo.findText(str(year))
        if idx != -1:
            self.year_combo.setCurrentIndex(idx)
        
        self.month_combo.setCurrentIndex(month - 1)
        
        self.year_combo.blockSignals(False)
        self.month_combo.blockSignals(False)

    def update_task_list(self):
        date = self.calendar.selectedDate()
        date_str = date.toString(Qt.DateFormat.ISODate)
        display_str = date.toString("M月d日 dddd")
        
        self.date_title.setText(display_str)
        self.task_list.clear()
        
        # 显示工作时长
        seconds = self.data_manager.get_work_time(date_str)
        if seconds > 0:
            h, rem = divmod(seconds, 3600)
            m = rem // 60
            self.work_time_label.setText(f"🔥 今日投入: {h}h {m}m")
            self.work_time_label.show()
        else:
            self.work_time_label.hide()
            
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
            
            # --- 回调函数修复：不接收 state 参数 ---
            on_toggle = lambda i=index: self.on_task_toggled(i)
            on_delete = lambda i=index: self.delete_task(i)
            
            widget = TaskItemWidget(t, on_toggle, on_delete)
            self.task_list.setItemWidget(item, widget)
            
        self.calendar.update() 

    def on_task_toggled(self, index):
        date_str = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
        self.data_manager.toggle_task_status(date_str, index)
        self.update_task_list()

    def delete_task(self, index):
        date_str = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
        success = self.data_manager.remove_task(date_str, index)
        if success:
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
        task_list = tasks if isinstance(tasks, list) else []
        for i in range(len(task_list) - 1, -1, -1):
            if task_list[i].get('completed'):
                self.data_manager.remove_task(date_str, i)
        self.update_task_list()

    def showEvent(self, event):
        # 每次显示窗口时，重置为今天
        self.calendar.setSelectedDate(QDate.currentDate())
        self.update_task_list()
        super().showEvent(event)

    def mousePressEvent(self, event):
        # 只响应左键
        if event.button() == Qt.MouseButton.LeftButton:
            # 【核心修复】
            # 计算鼠标位置与“窗口本身(frameGeometry)”左上角的差值
            # 之前写的 self.container.geometry().topLeft() 是错的
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 如果正在拖拽，且按住的是左键
        if self.drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            # 用当前鼠标位置减去之前的固定差值，得到窗口新位置
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None