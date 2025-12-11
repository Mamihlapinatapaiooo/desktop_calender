# app/ui/components.py
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QCalendarWidget)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect
from PyQt6.QtGui import QColor, QPainter, QPen
from app.config import *

# --- 1. 纯手绘极简复选框 ---
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
        margin = 2
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        active_color = QColor(ACCENT_COLOR)
        border_color = QColor("#CBD5E0")
        
        if self._checked:
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

# --- 2. 任务列表项组件 ---
class TaskItemWidget(QWidget):
    def __init__(self, task_data, on_toggle_callback):
        super().__init__()
        self.task_data = task_data
        self.on_toggle_callback = on_toggle_callback
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(12)
        self.setLayout(layout)

        self.checkbox = CustomCheckButton(checked=task_data.get('completed', False))
        self.checkbox.clicked = self.on_checkbox_clicked
        
        self.lbl = QLabel(task_data.get('text', ''))
        self.lbl.setWordWrap(True)
        self.lbl.setContentsMargins(0, 0, 0, 0)
        
        self.update_style()

        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.lbl, 1, Qt.AlignmentFlag.AlignVCenter)

    def update_style(self):
        is_completed = self.checkbox.isChecked()
        if is_completed:
            self.lbl.setStyleSheet(f"""
                color: {TEXT_SECONDARY}; 
                background: transparent;
                font-family: "Microsoft YaHei UI", sans-serif;
                font-size: 14px; 
                text-decoration: line-through;
            """)
        else:
            self.lbl.setStyleSheet(f"""
                color: {TEXT_PRIMARY}; 
                background: transparent;
                font-family: "Microsoft YaHei UI", sans-serif;
                font-size: 15px;
                font-weight: 500;
                line-height: 1.2;
            """)

    def on_checkbox_clicked(self):
        self.update_style()
        self.on_toggle_callback()

# --- 3. 极简日历 (修复选中样式) ---
class CleanCalendar(QCalendarWidget):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(False)
        self.setNavigationBarVisible(True)
        
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
                
                /* --- 核心修复：把默认的蓝色背景设为透明 --- */
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
            
            # --- 核心优化：绘制圆角矩形 ---
            # adjusted(6,6,-6,-6) 是为了让背景比格子稍微小一圈，有留白
            # 12, 12 是圆角的半径，数值越大越圆
            painter.drawRoundedRect(rect.adjusted(6, 6, -6, -6), 12, 12)
        
        painter.setPen(QColor("white") if is_selected else QColor(TEXT_PRIMARY))
        if date.month() != self.monthShown():
             painter.setPen(QColor("#CBD5E0"))
             
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        if self.task_manager.has_tasks(date):
            dot_color = QColor("white") if is_selected else QColor(DANGER_COLOR)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot_color)
            # 计算小圆点位置
            painter.drawEllipse(QPoint(int(rect.center().x()), int(rect.bottom() - 8)), 2, 2)