"""
鼠标点击花瓣粒子特效 overlay。
使用方式：
    overlay = PetalOverlay(parent_widget)
    overlay.resize(parent_widget.size())
    # 在父 widget 的 mousePressEvent 里调用：
    overlay.burst(event.pos())
"""
import math
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QTransform

# 花瓣颜色组
PETAL_COLORS = [
    "#FF85A1", "#FFB3C6", "#FF6B9D", "#C9184A",
    "#FFD6E0", "#FFADCF", "#FF4D88", "#FF8FAB",
    "#FFC2D4", "#FF006E", "#FB5607", "#FFBE0B",
    "#8338EC", "#3A86FF", "#06D6A0",
]


class Petal:
    def __init__(self, x, y):
        angle = random.uniform(0, 360)
        speed = random.uniform(3, 9)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(math.radians(angle)) * speed
        self.vy = math.sin(math.radians(angle)) * speed - random.uniform(2, 5)
        self.gravity = random.uniform(0.18, 0.35)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)
        self.size = random.uniform(7, 16)
        self.color = QColor(random.choice(PETAL_COLORS))
        self.alpha = 255
        self.fade = random.uniform(6, 12)
        # 花瓣形状：0=椭圆花瓣, 1=心形, 2=星形
        self.shape = random.randint(0, 2)

    def step(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.97
        self.rotation += self.rot_speed
        self.alpha = max(0, self.alpha - self.fade)

    def alive(self):
        return self.alpha > 0

    def draw(self, painter: QPainter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)

        c = QColor(self.color)
        c.setAlpha(int(self.alpha))
        painter.setPen(Qt.NoPen)
        painter.setBrush(c)

        s = self.size
        if self.shape == 0:
            # 椭圆花瓣
            painter.drawEllipse(QRectF(-s * 0.5, -s, s, s * 2))
        elif self.shape == 1:
            # 心形（近似两个圆 + 三角）
            path = QPainterPath()
            path.moveTo(0, s * 0.5)
            path.cubicTo(-s * 1.2, -s * 0.5, -s * 1.2, -s * 1.4, 0, -s * 0.6)
            path.cubicTo(s * 1.2, -s * 1.4, s * 1.2, -s * 0.5, 0, s * 0.5)
            painter.drawPath(path)
        else:
            # 五角星
            path = QPainterPath()
            outer = s
            inner = s * 0.45
            for i in range(5):
                a_out = math.radians(-90 + i * 72)
                a_in  = math.radians(-90 + i * 72 + 36)
                px_o, py_o = math.cos(a_out) * outer, math.sin(a_out) * outer
                px_i, py_i = math.cos(a_in)  * inner, math.sin(a_in)  * inner
                if i == 0:
                    path.moveTo(px_o, py_o)
                else:
                    path.lineTo(px_o, py_o)
                path.lineTo(px_i, py_i)
            path.closeSubpath()
            painter.drawPath(path)

        painter.restore()


class PetalOverlay(QWidget):
    """透明全覆盖层，负责渲染花瓣粒子"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._petals = []  # list of Petal
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)

    def burst(self, pos, count=18):
        """在指定位置爆发 count 个花瓣"""
        for _ in range(count):
            self._petals.append(Petal(pos.x(), pos.y()))
        if not self._timer.isActive():
            self._timer.start()
        self.raise_()

    def _tick(self):
        for p in self._petals:
            p.step()
        self._petals = [p for p in self._petals if p.alive()]
        if not self._petals:
            self._timer.stop()
        self.update()

    def paintEvent(self, event):
        if not self._petals:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for p in self._petals:
            p.draw(painter)
