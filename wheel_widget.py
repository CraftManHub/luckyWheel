import random
import math
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF,
    QPixmap, QMovie, QLinearGradient, QRadialGradient, QPainterPath,
    QConicalGradient
)

# 魔法主题配色：深色调 + 神秘感
DEFAULT_COLORS = [
    "#3D1A78",  # 深紫
    "#1A3A6B",  # 深蓝
    "#6B1A3A",  # 深红玫瑰
    "#1A5C3A",  # 暗墨绿
    "#5C3A1A",  # 深琥珀
    "#1A5C5C",  # 深青
    "#4A1A6B",  # 紫罗兰
    "#6B3A1A",  # 赤褐
    "#1A4A6B",  # 钢蓝
    "#3A6B1A",  # 暗橄榄
    "#6B1A5C",  # 深品红
    "#1A6B4A",  # 暗翠绿
]


def ease_out_quart(t):
    return 1 - (1 - t) ** 4


def _star_path(cx, cy, outer_r, inner_r, points=6):
    """生成多角星路径"""
    path = QPainterPath()
    step = math.pi / points
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        a = i * step - math.pi / 2
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


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

        # 装饰动画：符文点和魔法阵持续慢速旋转
        self._deco_angle = 0.0
        self._deco_timer = QTimer(self)
        self._deco_timer.setInterval(32)
        self._deco_timer.timeout.connect(self._on_deco_tick)
        self._deco_timer.start()

        self._bg_pixmap = None
        self._bg_movie = None

        self.setMinimumSize(420, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _on_deco_tick(self):
        self._deco_angle = (self._deco_angle + 0.4) % 360
        if not self._spinning:
            self.update()

    def set_options(self, options, reset_angle=True):
        self.options = options
        if reset_angle:
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

    # ─────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - 32
        cx, cy = w / 2, h / 2
        radius = size / 2
        rect_x = cx - radius
        rect_y = cy - radius

        # ── 外发光晕 ──
        self._draw_outer_glow(painter, cx, cy, radius)

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
            self._draw_empty_state(painter, cx, cy, radius, rect_x, rect_y, size, has_bg)
            return

        slices = self._get_slice_angles()

        # ── 绘制扇形 ──
        self._draw_slices(painter, slices, cx, cy, radius, rect_x, rect_y, size, has_bg)

        # ── 扇形边缘金色线 ──
        self._draw_dividers(painter, slices, cx, cy, radius)

        # ── 旋转符文装饰点（外圈，随 deco 旋转）──
        self._draw_rune_dots(painter, cx, cy, radius)

        # ── 外圈魔法环 ──
        self._draw_magic_ring(painter, cx, cy, radius, rect_x, rect_y, size)

        # ── 绘制文字 ──
        self._draw_labels(painter, slices, cx, cy, radius)

        # ── 中心魔法阵 ──
        self._draw_magic_center(painter, cx, cy, radius)

        # ── 指针（水晶魔杖）──
        self._draw_pointer(painter, cx, cy, radius)

    # ─── 外发光 ────────────────────────────────────────────
    def _draw_outer_glow(self, painter, cx, cy, radius):
        for i in range(5):
            alpha = int(30 - i * 5)
            extra = (i + 1) * 6
            glow = QRadialGradient(cx, cy, radius + extra)
            glow.setColorAt(0.7, QColor(160, 80, 255, alpha))
            glow.setColorAt(1.0, QColor(160, 80, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            r2 = radius + extra
            painter.drawEllipse(QRectF(cx - r2, cy - r2, r2 * 2, r2 * 2))

    # ─── 空状态 ────────────────────────────────────────────
    def _draw_empty_state(self, painter, cx, cy, radius, rx, ry, size, has_bg):
        if not has_bg:
            grad = QRadialGradient(cx, cy, radius)
            grad.setColorAt(0, QColor("#2D1B55"))
            grad.setColorAt(1, QColor("#0D0820"))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(160, 80, 255, 80), 2))
            painter.drawEllipse(int(rx), int(ry), int(size), int(size))
        painter.setPen(QColor("#A855F7"))
        painter.setFont(QFont("微软雅黑", 14))
        painter.drawText(self.rect(), Qt.AlignCenter, "✦ 请先添加选项 ✦")

    # ─── 扇形 ──────────────────────────────────────────────
    def _draw_slices(self, painter, slices, cx, cy, radius, rx, ry, size, has_bg):
        for i, (start, span) in enumerate(slices):
            base = QColor(self.options[i].get("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)]))

            # 每个扇形用径向渐变：内侧亮一点，外侧暗一点
            mid_deg = start + span / 2.0
            mid_rad = math.radians(90 - mid_deg - self.current_angle)
            grad_cx = cx + math.cos(mid_rad) * radius * 0.4
            grad_cy = cy - math.sin(mid_rad) * radius * 0.4

            light = base.lighter(150)
            dark  = base.darker(120)
            if has_bg:
                light.setAlpha(185)
                dark.setAlpha(185)

            grad = QRadialGradient(grad_cx, grad_cy, radius * 0.9)
            grad.setColorAt(0.0, light)
            grad.setColorAt(1.0, dark)

            qt_start = int((90 - start - self.current_angle) * 16)
            qt_span  = int(-span * 16)
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawPie(int(rx), int(ry), int(size), int(size), qt_start, qt_span)

    # ─── 金色分割线 ────────────────────────────────────────
    def _draw_dividers(self, painter, slices, cx, cy, radius):
        pen = QPen(QColor(255, 215, 80, 140), 1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        for start, span in slices:
            angle_rad = math.radians(90 - start - self.current_angle)
            x = cx + math.cos(angle_rad) * radius
            y = cy - math.sin(angle_rad) * radius
            painter.drawLine(QPointF(cx, cy), QPointF(x, y))

    # ─── 符文装饰点 ────────────────────────────────────────
    def _draw_rune_dots(self, painter, cx, cy, radius):
        n = 12
        dot_r = radius * 1.06
        painter.setBrush(QBrush(QColor(220, 180, 255, 200)))
        painter.setPen(Qt.NoPen)
        for i in range(n):
            a = math.radians(self._deco_angle + i * 360 / n)
            x = cx + math.cos(a) * dot_r
            y = cy + math.sin(a) * dot_r
            sz = 3.5 if i % 3 == 0 else 2.0
            # 交替菱形和圆点
            if i % 3 == 0:
                diamond = QPainterPath()
                diamond.moveTo(x, y - sz * 1.8)
                diamond.lineTo(x + sz, y)
                diamond.lineTo(x, y + sz * 1.8)
                diamond.lineTo(x - sz, y)
                diamond.closeSubpath()
                painter.drawPath(diamond)
            else:
                painter.drawEllipse(QRectF(x - sz, y - sz, sz * 2, sz * 2))

    # ─── 外圈魔法环 ────────────────────────────────────────
    def _draw_magic_ring(self, painter, cx, cy, radius, rx, ry, size):
        painter.setBrush(Qt.NoBrush)

        # 最外暗圈
        painter.setPen(QPen(QColor(0, 0, 0, 60), 8))
        painter.drawEllipse(QRectF(rx - 2, ry - 2, size + 4, size + 4))

        # 金色主环
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(255, 210, 80, 200))
        painter.setPen(pen)
        painter.drawEllipse(QRectF(rx, ry, size, size))

        # 内侧紫色细环
        painter.setPen(QPen(QColor(180, 100, 255, 120), 1))
        inner_off = 6
        painter.drawEllipse(QRectF(rx + inner_off, ry + inner_off,
                                   size - inner_off * 2, size - inner_off * 2))

    # ─── 文字 ──────────────────────────────────────────────
    def _draw_labels(self, painter, slices, cx, cy, radius):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.current_angle)

        base_font_size = max(8, min(13, int(radius * 0.1)))

        for i, (start, span) in enumerate(slices):
            if span < 6:
                continue

            mid = start + span / 2.0
            painter.save()
            painter.rotate(mid)

            inner_r = radius * 0.20
            outer_r = radius * 0.88
            text_len = outer_r - inner_r
            arc_width = span / 360.0 * 2 * math.pi * radius * 0.65
            arc_width = max(arc_width, 0)

            font_size = max(6, int(base_font_size * span / 20)) if span < 15 else base_font_size
            font = QFont("幼圆", font_size, QFont.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()

            painter.rotate(-90)

            text = self.options[i]["text"]
            text_color = QColor(self.options[i].get("text_color", "#FFFFFF"))
            available_w = int(text_len)
            available_h = int(arc_width)
            if available_w < 10 or available_h < 8:
                painter.restore()
                continue

            elided = fm.elidedText(text, Qt.ElideRight, available_w)
            text_rect = QRectF(-available_w / 2, -available_h / 2, available_w, available_h)
            mid_r = (inner_r + outer_r) / 2
            painter.translate(mid_r, 0)

            # 金色光晕描边
            painter.setPen(QPen(QColor(255, 210, 80, 80), 3.5))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                t_rect = QRectF(text_rect.x() + dx, text_rect.y() + dy,
                                text_rect.width(), text_rect.height())
                painter.drawText(t_rect, Qt.AlignCenter, elided)

            # 黑色描边
            painter.setPen(QPen(QColor(0, 0, 0, 120), 2))
            for dx, dy in [(-1, -1), (1, 1), (-1, 1), (1, -1)]:
                t_rect = QRectF(text_rect.x() + dx, text_rect.y() + dy,
                                text_rect.width(), text_rect.height())
                painter.drawText(t_rect, Qt.AlignCenter, elided)

            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignCenter, elided)
            painter.restore()

        painter.restore()

    # ─── 中心魔法阵 ────────────────────────────────────────
    def _draw_magic_center(self, painter, cx, cy, radius):
        cr = radius * 0.14

        # 底层深色圆
        bg_grad = QRadialGradient(cx, cy, cr)
        bg_grad.setColorAt(0.0, QColor("#3D1278"))
        bg_grad.setColorAt(0.6, QColor("#1A0840"))
        bg_grad.setColorAt(1.0, QColor("#0A0420"))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), cr, cr)

        # 慢速反向旋转的六芒星（与 deco 反向）
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self._deco_angle * 0.6)
        star = _star_path(0, 0, cr * 0.82, cr * 0.42, 6)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(200, 150, 255, 160), 1.0))
        painter.drawPath(star)
        painter.restore()

        # 同向旋转的内三角
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._deco_angle * 0.4)
        tri = _star_path(0, 0, cr * 0.55, cr * 0.28, 3)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 200, 80, 140), 1.0))
        painter.drawPath(tri)
        painter.restore()

        # 外圈金环
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 210, 80, 200), 1.5))
        painter.drawEllipse(QPointF(cx, cy), cr, cr)

        # 内圈紫环
        painter.setPen(QPen(QColor(180, 100, 255, 180), 1.0))
        painter.drawEllipse(QPointF(cx, cy), cr * 0.65, cr * 0.65)

        # 中心亮点
        gc = QRadialGradient(cx - cr * 0.15, cy - cr * 0.15, cr * 0.4)
        gc.setColorAt(0.0, QColor(255, 255, 255, 220))
        gc.setColorAt(0.4, QColor(200, 150, 255, 120))
        gc.setColorAt(1.0, QColor(100, 50, 200, 0))
        painter.setBrush(QBrush(gc))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), cr * 0.38, cr * 0.38)

    # ─── 水晶魔杖指针 ──────────────────────────────────────
    def _draw_pointer(self, painter, cx, cy, radius):
        tip_y   = cy - radius + 2          # 顶尖
        base_y  = cy - radius * 0.72       # 底座
        gem_y   = cy - radius + radius * 0.07  # 宝石中心
        half_w  = radius * 0.045           # 杆宽的一半

        # ── 杆（细长菱形）──
        shaft = QPainterPath()
        shaft.moveTo(cx, tip_y)                     # 顶尖
        shaft.lineTo(cx - half_w, gem_y + radius * 0.04)
        shaft.lineTo(cx - half_w * 1.6, base_y)
        shaft.lineTo(cx, base_y + radius * 0.04)
        shaft.lineTo(cx + half_w * 1.6, base_y)
        shaft.lineTo(cx + half_w, gem_y + radius * 0.04)
        shaft.closeSubpath()

        shaft_grad = QLinearGradient(cx - half_w * 2, tip_y, cx + half_w * 2, base_y)
        shaft_grad.setColorAt(0.0, QColor(255, 230, 120))   # 金顶
        shaft_grad.setColorAt(0.3, QColor(220, 180, 80))
        shaft_grad.setColorAt(0.7, QColor(160, 100, 200))   # 紫杆
        shaft_grad.setColorAt(1.0, QColor(80, 40, 140))
        painter.setBrush(QBrush(shaft_grad))
        painter.setPen(QPen(QColor(60, 20, 100, 180), 0.8))
        painter.drawPath(shaft)

        # ── 宝石（顶部菱形水晶）──
        gem_size = radius * 0.07
        gem = QPainterPath()
        gem.moveTo(cx, gem_y - gem_size * 1.4)   # 顶
        gem.lineTo(cx + gem_size, gem_y)           # 右
        gem.lineTo(cx, gem_y + gem_size * 0.7)    # 底
        gem.lineTo(cx - gem_size, gem_y)           # 左
        gem.closeSubpath()

        gem_grad = QRadialGradient(cx - gem_size * 0.3, gem_y - gem_size * 0.5, gem_size * 1.6)
        gem_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        gem_grad.setColorAt(0.25, QColor(200, 240, 255, 220))
        gem_grad.setColorAt(0.6,  QColor(100, 180, 255, 180))
        gem_grad.setColorAt(1.0,  QColor(60,  80, 200, 160))
        painter.setBrush(QBrush(gem_grad))
        painter.setPen(QPen(QColor(180, 220, 255, 200), 1.0))
        painter.drawPath(gem)

        # ── 宝石发光晕 ──
        for i in range(3):
            alpha = 60 - i * 18
            extra = gem_size * (0.6 + i * 0.5)
            glow = QRadialGradient(cx, gem_y, extra)
            glow.setColorAt(0.0, QColor(150, 220, 255, alpha))
            glow.setColorAt(1.0, QColor(150, 220, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(cx - extra, gem_y - extra, extra * 2, extra * 2))

        # ── 宝石高光点 ──
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.setPen(Qt.NoPen)
        hl = gem_size * 0.22
        painter.drawEllipse(QRectF(cx - gem_size * 0.35 - hl,
                                   gem_y - gem_size * 0.7 - hl, hl * 2, hl * 2))
