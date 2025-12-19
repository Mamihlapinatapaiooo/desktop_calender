# app/ui/components.py
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QCalendarWidget, QPushButton, QGraphicsOpacityEffect,QSizePolicy)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen, QCursor, QFont
from app.config import *

# --- 1. 纯手绘极简复选框 (保持不变) ---
class CustomCheckButton(QWidget):
    def __init__(self, checked=False, size=22, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._hover = False

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        self._checked = checked
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self.update()
            if hasattr(self, 'clicked'): 
                self.clicked()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        margin = 3
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        active_color = QColor(ACCENT_COLOR)
        border_color = QColor("#CBD5E0")
        
        if self._checked:
            adjust = margin - 1 
            draw_rect = rect.adjusted(adjust, adjust, -adjust, -adjust)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(active_color)
            painter.drawEllipse(draw_rect)
            
            c = draw_rect.center()
            w = draw_rect.width()
            p1 = QPointF(c.x() - w * 0.25, c.y() + 2)
            p2 = QPointF(c.x() - w * 0.05, c.y() + w * 0.25)
            p3 = QPointF(c.x() + w * 0.3, c.y() - w * 0.25)
            
            pen = QPen(QColor("white"))
            pen.setWidthF(2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(p1, p2)
            painter.drawLine(p2, p3)
        else:
            pen = QPen(active_color if self._hover else border_color)
            pen.setWidthF(2.0)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(draw_rect)

# --- 2. 任务列表项组件 (修复版) ---
class TaskItemWidget(QWidget):
    def __init__(self, task_data, on_toggle_callback, on_delete_callback):
        super().__init__()
        self.task_data = task_data
        self.on_toggle_callback = on_toggle_callback
        self.on_delete_callback = on_delete_callback

        # 整体圆角
        self.setStyleSheet(f"""
            TaskItemWidget {{
                background-color: transparent;
                border-radius: 8px; 
            }}
            TaskItemWidget:hover {{
                 background-color: #F7FAFC;
            }}
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 左侧内容 ---
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent; border-radius: 8px;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 5, 10, 5) 
        content_layout.setSpacing(12)

        self.checkbox = CustomCheckButton(checked=task_data.get('completed', False))
        self.checkbox.clicked = self.on_checkbox_clicked
        
        self.lbl = QLabel(task_data.get('text', ''))
        self.lbl.setWordWrap(True)
        self.lbl.setStyleSheet("background: transparent; border: none;")
        
        content_layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(self.lbl, 1, Qt.AlignmentFlag.AlignVCenter)

        # --- 右侧删除按钮 ---
        self.del_btn = QPushButton("🗑 删除") # 加了文字，看起来更正式，如果不想要文字可以删掉
        self.del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # 【核心修复】：水平 Fixed (听指挥)，垂直 Expanding (填满高度)
        self.del_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        self.del_btn.setMaximumWidth(0) # 初始隐藏
        
        # 样式优化：文字居中，图标和文字有间隔
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E; 
                color: white; 
                border: none; 
                border-top-right-radius: 8px;     
                border-bottom-right-radius: 8px;  
                margin-left: 10px;
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
                padding-right: 5px;
            }
            QPushButton:hover {
                background-color: #C53030;
            }
        """)
        self.del_btn.clicked.connect(self.on_delete_callback)

        self.update_style()

        main_layout.addWidget(content_widget, 1)
        main_layout.addWidget(self.del_btn) # 这里不需要再设 AlignStretch 了，SizePolicy 会搞定

        # --- 动画设置 ---
        
        # 飞入
        self.anim_in = QPropertyAnimation(self.del_btn, b"maximumWidth")
        self.anim_in.setDuration(400)  # 400ms 比较丝滑
        self.anim_in.setStartValue(0)
        self.anim_in.setEndValue(90)   # 90px 宽度，足够放下图标和文字
        self.anim_in.setEasingCurve(QEasingCurve.Type.OutCubic) # 使用 OutCubic 曲线

        # 飞出
        self.anim_out = QPropertyAnimation(self.del_btn, b"maximumWidth")
        self.anim_out.setDuration(300)
        self.anim_out.setEndValue(0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

    def update_style(self):
        is_completed = self.checkbox.isChecked()
        base_style = "background: transparent; border: none; font-family: 'Microsoft YaHei UI', sans-serif;"
        if is_completed:
            self.lbl.setStyleSheet(base_style + f"color: {TEXT_SECONDARY}; font-size: 15px; text-decoration: line-through;")
        else:
            self.lbl.setStyleSheet(base_style + f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 500; line-height: 1.2;")

    def on_checkbox_clicked(self):
        self.update_style()
        self.on_toggle_callback()

    def enterEvent(self, event):
        self.anim_out.stop()
        self.anim_in.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim_in.stop()
        self.anim_out.setStartValue(self.del_btn.width())
        self.anim_out.start()
        super().leaveEvent(event)

# --- 3. 极简日历 (保持不变) ---
class CleanCalendar(QCalendarWidget):
    # ... (保持你原来的代码不变) ...
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(False)
        self.setNavigationBarVisible(False)
        
        self.setStyleSheet(f"""
            QCalendarWidget QWidget {{ alternate-background-color: {BG_COLOR}; background-color: {BG_COLOR}; }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QToolButton {{ 
                color: {TEXT_PRIMARY}; font-weight: bold; icon-size: 20px; border: none;
                background-color: transparent; padding: 5px;
            }}
            QCalendarWidget QToolButton:hover {{ background-color: {CARD_BG}; border-radius: 5px; }}
            QCalendarWidget QMenu {{ color: white; background-color: {TEXT_PRIMARY}; }}
            QCalendarWidget QSpinBox {{ 
                color: {TEXT_PRIMARY}; background: transparent; selection-background-color: {ACCENT_COLOR};
            }}
            QCalendarWidget QTableView QHeaderView::section {{
                background-color: white; color: {TEXT_SECONDARY}; border: none; font-weight: bold; padding-bottom: 5px;
            }}
            QCalendarWidget QAbstractItemView {{
                font-size: 14px; color: {TEXT_PRIMARY}; 
                selection-background-color: transparent; 
                selection-color: white; outline: none; border: none;
            }}
        """)

    def paintCell(self, painter, rect, date):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        is_selected = (date == self.selectedDate())
        
        if is_selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(ACCENT_COLOR))
            painter.drawRoundedRect(rect.adjusted(6, 6, -6, -6), 12, 12)
        
        painter.setPen(QColor("white") if is_selected else QColor(TEXT_PRIMARY))
        if date.month() != self.monthShown():
             painter.setPen(QColor("#CBD5E0"))
             
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        if self.task_manager.has_tasks(date):
            dot_color = QColor("white") if is_selected else QColor(DANGER_COLOR)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot_color)
            painter.drawEllipse(QPoint(int(rect.center().x()), int(rect.bottom() - 8)), 2, 2)