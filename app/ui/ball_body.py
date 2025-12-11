# app/ui/ball_body.py
from PyQt6.QtWidgets import (QWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QDate, QRect, QPointF
from PyQt6.QtGui import QColor, QPainter, QBrush, QFont, QLinearGradient, QPen, QPainterPath
from app.config import *
import time
import math
import random

class BallBody(QWidget):
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager 
        
        self.setFixedSize(200, 200) 
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        self.mode = "NORMAL"
        self.total_seconds = 25 * 60
        self.remaining_seconds = 0
        self.work_start_time = 0
        
        # --- 动画控制变量 ---
        self.anim_step = 0
        
        # [核心修改] 引入随机平滑呼吸变量
        self.current_intensity = 0.5 # 当前燃烧强度 (0.0 ~ 1.0)
        self.target_intensity = 0.8  # 下一个想要达到的强度
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logic)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)

    def start_focus(self, minutes):
        self.stop_all()
        self.mode = "FOCUS"
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.timer.start(1000)
        self.update()

    def start_work(self):
        self.stop_all()
        self.mode = "WORK"
        self.work_start_time = time.time()
        self.timer.start(1000)
        self.anim_timer.start(30)
        self.update()

    def stop_all(self):
        if self.mode == "WORK":
            duration = int(time.time() - self.work_start_time)
            if self.data_manager and duration > 0:
                date_str = QDate.currentDate().toString(Qt.DateFormat.ISODate)
                self.data_manager.add_work_time(date_str, duration)
        
        self.mode = "NORMAL"
        self.timer.stop()
        self.anim_timer.stop()
        self.update()

    def update_logic(self):
        if self.mode == "FOCUS":
            self.remaining_seconds -= 1
            if self.remaining_seconds <= 0:
                self.stop_all()
        self.update()

    def update_animation(self):
        if self.mode == "WORK":
            self.anim_step += 1
            
            # --- [核心算法] 随机平滑插值 ---
            # 1. 计算当前值与目标值的差
            diff = self.target_intensity - self.current_intensity
            
            # 2. 每一帧只移动差值的 5% (0.05)，这就是平滑的关键
            # 数值越小越平滑迟缓，数值越大越灵敏抖动
            speed_factor = 0.05 
            self.current_intensity += diff * speed_factor
            
            # 3. 如果已经很接近目标了，就随机生成一个新的目标
            if abs(diff) < 0.01:
                # 随机生成 0.3 到 1.0 之间的强度，保证火焰不会熄灭，也不会一直太弱
                self.target_intensity = random.uniform(0.3, 1.0)
            
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        full_rect = self.rect()
        center = full_rect.center()
        ball_size = 80
        
        ball_rect = QRect(
            center.x() - ball_size // 2, 
            center.y() - ball_size // 2, 
            ball_size, 
            ball_size
        )
        
        h = ball_rect.height()
        w = ball_rect.width()
        base_radius = w / 2
        
        start_point = ball_rect.topLeft().toPointF()
        end_point = ball_rect.bottomRight().toPointF()
        
        # ===========================
        # 1. 绘制背景与特效
        # ===========================
        if self.mode == "WORK":
            painter.setPen(Qt.PenStyle.NoPen)
            
            # 使用计算好的平滑随机变量替代 sin
            pulse_base = self.current_intensity 

            def draw_fire_halo(color_hex, max_stretch, alpha_base, noise_speed_factor):
                path = QPainterPath()
                # 保持 1度 的超精细粒度
                angle_step = 1
                
                for angle in range(0, 360, angle_step):
                    rad = math.radians(angle)
                    
                    # 基础波浪
                    noise = math.sin(angle * 0.1 + self.anim_step * noise_speed_factor) * \
                            math.cos(angle * 0.3 - self.anim_step * noise_speed_factor * 0.8)
                    
                    # 微抖动 (Micro-jitter)
                    micro_jitter = random.uniform(-1.5, 1.5)
                    
                    # 延伸长度
                    noise_stretch = (noise + 1) / 2 * 8
                    
                    # 计算最终半径
                    # pulse_base * max_stretch: 决定了整体的呼吸幅度 (随机平滑)
                    current_radius = base_radius + (pulse_base * max_stretch * 0.6) + noise_stretch + micro_jitter
                    
                    px = center.x() + current_radius * math.cos(rad)
                    py = center.y() + current_radius * math.sin(rad)
                    
                    if angle == 0: path.moveTo(px, py)
                    else: path.lineTo(px, py)
                path.closeSubpath()
                
                color = QColor(color_hex)
                # 透明度也跟随强度平滑变化
                current_alpha = int(alpha_base - (pulse_base * 20))
                color.setAlpha(max(20, current_alpha))
                painter.setBrush(QBrush(color))
                painter.drawPath(path)

            # 这里保留了上次你要求的“高度减半”参数 (12 和 7)
            draw_fire_halo("#FF4500", max_stretch=9, alpha_base=70, noise_speed_factor=0.2)
            draw_fire_halo("#FF8C00", max_stretch=4, alpha_base=100, noise_speed_factor=0.15)

            fire_gradient = QLinearGradient(start_point, end_point)
            fire_gradient.setColorAt(0, QColor("#FF512F"))
            fire_gradient.setColorAt(1, QColor("#F09819"))
            painter.setBrush(QBrush(fire_gradient))
            painter.drawEllipse(ball_rect.adjusted(2, 2, -2, -2))

        elif self.mode == "FOCUS":
            painter.setBrush(QColor("white")) 
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(ball_rect)

        else:
            gradient = QLinearGradient(start_point, end_point)
            gradient.setColorAt(0, QColor(THEME_GRADIENT_START))
            gradient.setColorAt(1, QColor(THEME_GRADIENT_END))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            rounded_r = int(h * 0.24)
            painter.drawRoundedRect(ball_rect, rounded_r, rounded_r)

        painter.setPen(QColor("white"))

        # ===========================
        # 2. 绘制文字内容
        # ===========================
        if self.mode == "FOCUS":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            ring_rect = ball_rect.adjusted(4, 4, -4, -4) 
            
            track_pen = QPen(QColor("#EEF2FF")) 
            track_pen.setWidthF(3.0)
            painter.setPen(track_pen)
            painter.drawEllipse(ring_rect) 

            progress = self.remaining_seconds / self.total_seconds
            span_angle = int(-360 * 16 * progress)
            prog_pen = QPen(QColor(ACCENT_COLOR)) 
            prog_pen.setWidthF(3.0)
            prog_pen.setCapStyle(Qt.PenCapStyle.RoundCap) 
            painter.setPen(prog_pen)
            painter.drawArc(ring_rect, 90 * 16, span_angle)
            
            painter.setPen(QColor(ACCENT_COLOR))
            mins, secs = divmod(self.remaining_seconds, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            font_time = QFont("Arial", int(h * 0.26), QFont.Weight.Bold)
            painter.setFont(font_time)
            painter.drawText(ball_rect, Qt.AlignmentFlag.AlignCenter, time_str)

        elif self.mode == "WORK":
            current_duration = int(time.time() - self.work_start_time)
            mins, secs = divmod(current_duration, 60)
            hrs, mins = divmod(mins, 60)
            if hrs > 0: time_str = f"{hrs}:{mins:02d}"
            else: time_str = f"{mins}:{secs:02d}"
            
            painter.setPen(QColor("white"))
            
            font_label = QFont("Arial", int(h * 0.13), QFont.Weight.DemiBold)
            font_label.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
            painter.setFont(font_label)
            
            label_rect = QRect(ball_rect.x(), ball_rect.y() + int(h * 0.22), w, int(h * 0.2))
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "WORK")

            font_time = QFont("Arial", int(h * 0.30), QFont.Weight.Bold)
            painter.setFont(font_time)
            time_rect = QRect(ball_rect.x(), ball_rect.y() + int(h * 0.42), w, int(h * 0.4))
            painter.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, time_str)

        else:
            today = QDate.currentDate()
            month_str = today.toString("MMM").upper()
            day_str = today.toString("d")
            
            font_month = QFont("Arial", int(h * 0.11), QFont.Weight.Bold)
            painter.setFont(font_month)
            month_rect = QRect(ball_rect.x(), ball_rect.y() + int(h * 0.1), w, int(h * 0.25))
            painter.drawText(month_rect, Qt.AlignmentFlag.AlignCenter, month_str)

            font_day = QFont("Arial", int(h * 0.32), QFont.Weight.Bold)
            painter.setFont(font_day)
            day_rect = QRect(ball_rect.x(), ball_rect.y() + int(h * 0.3), w, int(h * 0.5))
            painter.drawText(day_rect, Qt.AlignmentFlag.AlignCenter, day_str)