import json
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QMovie, QPainter, QColor, QBrush, QPainterPath, QLinearGradient

from wheel_widget import WheelWidget
from config_panel import ConfigPanel, DEFAULT_OPTIONS
from bg_drawer import BgDrawer

def _get_config_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "LuckyWheel")
    os.makedirs(path, exist_ok=True)
    return path

CONFIG_FILE = os.path.join(_get_config_dir(), "config.json")


class RootWidget(QWidget):
    """支持全局背景图/gif 的根 widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = None
        self._bg_movie = None

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        src = None
        if self._bg_movie:
            src = self._bg_movie.currentPixmap()
        elif self._bg_pixmap:
            src = self._bg_pixmap

        if src and not src.isNull():
            scaled = src.scaled(self.size(),
                                Qt.KeepAspectRatioByExpanding,
                                Qt.SmoothTransformation)
            ox = (self.width() - scaled.width()) // 2
            oy = (self.height() - scaled.height()) // 2
            painter.drawPixmap(ox, oy, scaled)
            # 半透明深色蒙版，让前景控件可读
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        else:
            # 默认渐变背景
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0, QColor("#FFD700"))     # 深紫
            grad.setColorAt(0.5, QColor("#4A148C"))   # 紫色
            grad.setColorAt(1, QColor("#7B1FA2"))     # 紫红

            painter.fillRect(self.rect(), QBrush(grad))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(820, 580)
        self._drag_pos = None

        self.root = RootWidget()
        self.setCentralWidget(self.root)

        layout = QHBoxLayout(self.root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.wheel = WheelWidget()
        self.panel = ConfigPanel()
        layout.addWidget(self.wheel, stretch=1)
        layout.addWidget(self.panel)

        # 关闭按钮
        self.btn_close = QPushButton("✕", self.root)
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.10); color: #aaa;
                border: none; border-radius: 16px; font-size: 14px;
            }
            QPushButton:hover { background: #E74C3C; color: white; }
        """)
        self.btn_close.clicked.connect(self.close)

        # 右侧背景抽屉
        self.drawer = BgDrawer(self.root)

        # 信号连接
        self.panel.config_changed.connect(self._on_config_changed)
        self.panel.spin_clicked.connect(self._on_spin_clicked)
        self.wheel.spin_finished.connect(self._on_spin_finished)

        self.drawer.wheel_bg_change.connect(self.wheel.set_background)
        self.drawer.wheel_bg_clear.connect(self.wheel.clear_background)
        self.drawer.window_bg_change.connect(self.root.set_background)
        self.drawer.window_bg_clear.connect(self.root.clear_background)

        # 加载配置
        self.drawer.load_bg()
        options = self._load_config()
        self.panel.load_options(options)
        self.wheel.set_options(self.panel.get_options())

        self._reposition_overlays()

    def _reposition_overlays(self):
        w, h = self.root.width(), self.root.height()
        self.btn_close.move(w - 48, 12)
        self.drawer.reposition(w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_overlays()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _on_config_changed(self, options):
        self.wheel.set_options(options)
        self._save_config(options)

    def _on_spin_clicked(self):
        self.panel.set_spinning(True)
        self.wheel.spin()

    def _on_spin_finished(self, winner_text):
        self.panel.show_result(winner_text)

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    return data
            except Exception:
                pass
        return DEFAULT_OPTIONS

    def _save_config(self, options):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(options, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
