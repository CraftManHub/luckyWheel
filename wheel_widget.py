import random
import math
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF,
    QPixmap, QMovie, QLinearGradient, QRadialGradient, QPainterPath
)

DEFAULT_COLORS = [
    "#E74C3C", "#3498DB", "#2ECC71", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#C0392B",
    "#16A085", "#8E44AD", "#D35400", "#27AE60",
]


def ease_out_quart(t):
    return 1 - (1 - t) ** 4


class WheelWidget(QWidget):
    spin_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.options = []
        self.current_angle = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._on_timer)

        self._elapsed = QElapsedTimer()
        self._duration = 5000
        self._start_angle = 0.0
        self._total_rotation = 0.0
        self._spinning = False
        self._winner_index = -1

        self._bg_pixmap = None
        self._bg_movie = None

        self.setMinimumSize(420, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_options(self, options):
        self.options = options
        self.current_angle = 0.0
        self.update()

    def set_background(self, path):
        if self._bg_movie:
            self._bg_movie.stop()
            self._bg_movie = None
        self._bg_pixmap = None

        if path.lower().endswith(".gif"):
            movie = QMovie(path)
            if movie.isValid():
                self._bg_movie = movie
                self._bg_movie.frameChanged.connect(self.update)
                self._bg_movie.start()
        else:
            px = QPixmap(path)
            if not px.isNull():
                self._bg_pixmap = px
        self.update()

    def clear_background(self):
        if self._bg_movie:
            self._bg_movie.stop()
            self._bg_movie = None
        self._bg_pixmap = None
        self.update()

    def _get_slice_angles(self):
        if not self.options:
            return []
        total_weight = sum(o["weight"] for o in self.options)
        if total_weight <= 0:
            return []
        result = []
        current = 0.0
        for o in self.options:
            span = (o["weight"] / total_weight) * 360.0
            result.append((current, span))
            current += span
        return result

    def _weighted_random_index(self):
        total = sum(o["weight"] for o in self.options)
        if total <= 0:
            return 0
        r = random.uniform(0, total)
        cumulative = 0
        for i, o in enumerate(self.options):
            cumulative += o["weight"]
            if r <= cumulative:
                return i
        return len(self.options) - 1

    def spin(self):
        if self._spinning or not self.options:
            return
        self._spinning = True
        self._winner_index = self._weighted_random_index()

        slices = self._get_slice_angles()
        start, span = slices[self._winner_index]
        mid_angle = start + span / 2.0

        # 推导：扇形中心 Qt 角度 = 90 - mid_angle - current_angle
        # 指针在顶部 = Qt 90°，令其相等：90 - mid_angle - target = 90 → target = -mid_angle
        target = -mid_angle
        min_target = self.current_angle + 360.0 * 5
        while target <= min_target:
            target += 360.0

        self._start_angle = self.current_angle
        self._total_rotation = target - self.current_angle
        self._elapsed.start()
        self._timer.start()

    def _on_timer(self):
        elapsed = self._elapsed.elapsed()
        t = min(elapsed / self._duration, 1.0)
        self.current_angle = self._start_angle + self._total_rotation * ease_out_quart(t)
        self.update()

        if t >= 1.0:
            self._timer.stop()
            self._spinning = False
            self.current_angle = self._start_angle + self._total_rotation
            self.spin_finished.emit(self.options[self._winner_index]["text"])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - 24
        cx, cy = w / 2, h / 2
        radius = size / 2
        rect_x = cx - radius
        rect_y = cy - radius

        # ── 转盘圆形背景图 ──
        has_bg = self._bg_movie or self._bg_pixmap
        if has_bg:
            painter.save()
            clip = QPainterPath()
            clip.addEllipse(QRectF(rect_x, rect_y, size, size))
            painter.setClipPath(clip)
            src = self._bg_movie.currentPixmap() if self._bg_movie else self._bg_pixmap
            if src and not src.isNull():
                scaled = src.scaled(int(size), int(size),
                                    Qt.KeepAspectRatioByExpanding,
                                    Qt.SmoothTransformation)
                painter.drawPixmap(int(cx - scaled.width() / 2),
                                   int(cy - scaled.height() / 2), scaled)
            painter.restore()

        if not self.options:
            if not has_bg:
                grad = QRadialGradient(cx, cy, radius)
                grad.setColorAt(0, QColor("#F8F9FA"))
                grad.setColorAt(1, QColor("#DEE2E6"))
                painter.setBrush(QBrush(grad))
                painter.setPen(QPen(QColor("#CED4DA"), 2))
                painter.drawEllipse(int(rect_x), int(rect_y), int(size), int(size))
            painter.setPen(QColor("#868E96"))
            painter.setFont(QFont("微软雅黑", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "请先添加选项")
            return

        slices = self._get_slice_angles()

        # ── 绘制扇形 ──
        for i, (start, span) in enumerate(slices):
            color = QColor(self.options[i].get("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)]))
            if has_bg:
                color.setAlpha(170)
            qt_start = int((90 - start - self.current_angle) * 16)
            qt_span = int(-span * 16)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(255, 255, 255, 160), 1.5))
            painter.drawPie(int(rect_x), int(rect_y), int(size), int(size),
                            qt_start, qt_span)

        # ── 绘制文字（随转盘旋转）──
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.current_angle)

        base_font_size = max(8, min(13, int(radius * 0.1)))

        for i, (start, span) in enumerate(slices):
            # 极小扇形（< 6°）跳过文字
            if span < 6:
                continue

            mid = start + span / 2.0
            painter.save()
            # 旋转到扇形中线方向
            painter.rotate(mid)

            # 文字绘制区域：沿径向从 20% 到 88% 半径，宽度由弧长决定
            inner_r = radius * 0.20
            outer_r = radius * 0.88
            text_len = outer_r - inner_r   # 文字框的"长"（沿径向）

            # 弧长决定文字框"宽"（垂直于径向）
            arc_width = span / 360.0 * 2 * math.pi * radius * 0.65
            arc_width = max(arc_width, 0)

            # 小扇形自动缩小字体
            if span < 15:
                font_size = max(6, int(base_font_size * span / 20))
            else:
                font_size = base_font_size

            font = QFont("微软雅黑", font_size, QFont.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()

            # 文字方向：沿径向从内到外（向上 = 朝圆心外）
            # 旋转后 Y 轴朝上为负，X 轴朝右
            # 用 QRectF 精确居中：x 居中于0，y 从 inner_r 到 outer_r（注意 painter 已 rotate(mid)，
            # 正 Y 方向已指向扇形中线外侧，但 QPainter 坐标 Y 向下，所以：
            # 朝外 = 负 Y 方向），用 rotate(-90) 让文字朝外排列
            painter.rotate(-90)  # 让文字朝向圆外（从圆心向外读）

            text = self.options[i]["text"]
            text_color = QColor(self.options[i].get("text_color", "#FFFFFF"))
            # 计算可用宽度，截断文字
            available_w = int(text_len)
            available_h = int(arc_width)
            if available_w < 10 or available_h < 8:
                painter.restore()
                continue

            elided = fm.elidedText(text, Qt.ElideRight, available_w)
            text_rect = QRectF(-available_w / 2, -available_h / 2,
                               available_w, available_h)

            # 文字中心在径向中点处（距圆心 (inner_r+outer_r)/2）
            mid_r = (inner_r + outer_r) / 2
            painter.translate(mid_r, 0)

            # 描边
            painter.setPen(QPen(QColor(0, 0, 0, 100), 2.5))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                t_rect = QRectF(text_rect.x() + dx, text_rect.y() + dy,
                                text_rect.width(), text_rect.height())
                painter.drawText(t_rect, Qt.AlignCenter, elided)
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignCenter, elided)

            painter.restore()

        painter.restore()

        # ── 中心圆 ──
        cr = radius * 0.13
        gc = QRadialGradient(cx, cy, cr)
        gc.setColorAt(0, QColor("#FFFFFF"))
        gc.setColorAt(1, QColor("#CCCCCC"))
        painter.setBrush(QBrush(gc))
        painter.setPen(QPen(QColor("#AAAAAA"), 2))
        painter.drawEllipse(QPointF(cx, cy), cr, cr)

        # ── 外圈高光 ──
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 80), 3))
        painter.drawEllipse(int(rect_x), int(rect_y), int(size), int(size))
        painter.setPen(QPen(QColor(0, 0, 0, 40), 6))
        painter.drawEllipse(int(rect_x - 1), int(rect_y - 1), int(size + 2), int(size + 2))

        # ── 顶部指针 ──
        ps = radius * 0.11
        pointer = QPolygonF([
            QPointF(cx, cy - radius + 4),
            QPointF(cx - ps * 0.6, cy - radius + ps * 1.6),
            QPointF(cx + ps * 0.6, cy - radius + ps * 1.6),
        ])
        gp = QLinearGradient(cx - ps, cy - radius, cx + ps, cy - radius + ps * 2)
        gp.setColorAt(0, QColor("#FF5252"))
        gp.setColorAt(1, QColor("#B71C1C"))
        painter.setBrush(QBrush(gp))
        painter.setPen(QPen(QColor("#B71C1C"), 1))
        painter.drawPolygon(pointer)
