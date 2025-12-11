# app/ui/ball_dialogs.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QSpinBox, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from app.config import *

class CustomTimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(300, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)

        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        title = QLabel("⏱️ 专注时长")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY}; border: none;")
        content_layout.addWidget(title)

        input_row_layout = QHBoxLayout()
        input_row_layout.setContentsMargins(10, 0, 10, 0)
        input_row_layout.setSpacing(10)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 240) 
        self.spin_box.setValue(25)     
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spin_box.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CARD_BG};
                border-radius: 12px;
                height: 50px;
                font-size: 32px;
                font-family: Arial;
                font-weight: bold;
                color: {ACCENT_COLOR};
                selection-background-color: {ACCENT_COLOR};
            }}
            QSpinBox:focus {{
                background-color: white;
                border: 2px solid {ACCENT_COLOR};
            }}
        """)
        
        unit = QLabel("分钟")
        unit.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 16px; font-weight: bold; border: none;")
        
        input_row_layout.addWidget(self.spin_box, 1)
        input_row_layout.addWidget(unit)
        
        content_layout.addLayout(input_row_layout)

        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #F7FAFC; color: {TEXT_PRIMARY}; }}
        """)
        
        btn_ok = QPushButton("开始")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: #5A67D8; }}
        """)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        content_layout.addLayout(btn_layout)

    def get_value(self):
        return self.spin_box.value()