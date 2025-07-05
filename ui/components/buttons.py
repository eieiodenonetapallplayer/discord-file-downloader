from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QIcon
from PyQt6.QtCore import pyqtProperty

class RippleButton(QPushButton):
    """
    ปุ่มแบบมีเอฟเฟกต์ ripple เมื่อคลิก
    """
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(42)
        
        self._ripple_radius = 0
        self._ripple_pos = QPoint(0, 0)
        self._ripple_alpha = 100
        self._animation = QPropertyAnimation(self, b"_ripple_radius")
        self._animation.setDuration(400)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._ripple_radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            
            theme = QApplication.instance().property("theme")
            ripple_color = QColor(theme["primary"])
            ripple_color.setAlpha(self._ripple_alpha)
            
            painter.setBrush(QBrush(ripple_color))
            painter.drawEllipse(self._ripple_pos, self._ripple_radius, self._ripple_radius)

    def mousePressEvent(self, event):
        self._ripple_pos = event.position().toPoint()
        self._ripple_radius = 1
        self._ripple_alpha = 100
        
        self._animation.stop()
        self._animation.setStartValue(1)
        self._animation.setEndValue(max(self.width(), self.height()) * 1.5)
        self._animation.finished.connect(self._reset_ripple)
        self._animation.start()
        
        super().mousePressEvent(event)

    def _reset_ripple(self):
        self._ripple_radius = 0
        self.update()

    def _get_ripple_radius(self):
        return self._ripple_radius

    def _set_ripple_radius(self, radius):
        self._ripple_radius = radius
        self.update()

    _ripple_radius = pyqtProperty(float, _get_ripple_radius, _set_ripple_radius)

class FloatingActionButton(QPushButton):
    """
    ปุ่มลอยแบบ Material Design
    """
    def __init__(self, icon_path: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border-radius: 28px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(88, 101, 242, 150))
        self.setGraphicsEffect(shadow)

class ToggleSwitch(QCheckBox):
    """
    สวิตช์เปิดปิดแบบสมัยใหม่
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._bg_color = QColor("#4E5058")
        self._active_color = QColor("#5865F2")
        self._circle_color = QColor("#FFFFFF")
        self._circle_pos = 3
        
        self._animation = QPropertyAnimation(self, b"circle_pos")
        self._animation.setDuration(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        theme = QApplication.instance().property("theme")
        bg_color = theme["primary"] if self.isChecked() else theme["secondary"]
        
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)
        
        painter.setBrush(QBrush(self._circle_color))
        painter.drawEllipse(self._circle_pos, 3, 24, 24)

    def mousePressEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._circle_pos)
        self._animation.setEndValue(33 if self.isChecked() else 3)
        self._animation.start()
        super().mousePressEvent(event)

    def _get_circle_pos(self):
        return self._circle_pos

    def _set_circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    circle_pos = pyqtProperty(int, _get_circle_pos, _set_circle_pos)