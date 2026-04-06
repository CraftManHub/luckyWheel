import json
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QMovie, QPainter, QColor, QBrush, QPainterPath, QLinearGradient

from wheel_widget import WheelWidget
from config_panel import ConfigPanel, DEFAULT_OPTIONS
from bg_drawer import BgDrawer
from petal_overlay import PetalOverlay
from sound_player import SoundPlayer

def _get_config_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "LuckyWheel")
    os.makedirs(path, exist_ok=True)
    return path

CONFIG_FILE = os.path.join(_get_config_dir(), "config.json")
SETTINGS_FILE = os.path.join(_get_config_dir(), "settings.json")


class RootWidget(QWidget):
    """支持全局背景图/gif 的根 widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = None
        self._bg_movie = None
        self._petal_overlay: "PetalOverlay | None" = None

    def set_petal_overlay(self, overlay: "PetalOverlay"):
        self._petal_overlay = overlay

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._petal_overlay and event.button() == Qt.LeftButton:
            self._petal_overlay.burst(event.pos())

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
            grad.setColorAt(0, QColor("#ff9d14"))     
            grad.setColorAt(0.5, QColor("#596c64"))   
            grad.setColorAt(1, QColor("#191919"))     

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

        # 花瓣特效 overlay（覆盖整个 root）
        self.petal_overlay = PetalOverlay(self.root)
        self.petal_overlay.resize(self.root.size())
        self.root.set_petal_overlay(self.petal_overlay)

        # 音效播放器（启动时扫描 sounds/ 文件夹）
        self._sound = SoundPlayer()

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
        self.wheel.set_options(self.panel.get_wheel_options())

        # 加载设置（静音等）
        settings = self._load_settings()
        self.drawer.set_muted(settings.get("muted", False))
        self.drawer.mute_changed.connect(self._on_mute_toggled)

        self._reposition_overlays()

    def _reposition_overlays(self):
        w, h = self.root.width(), self.root.height()
        self.btn_close.move(w - 48, 12)
        self.drawer.reposition(w, h)
        self.petal_overlay.resize(w, h)
        self.petal_overlay.raise_()

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

    def closeEvent(self, event):
        super().closeEvent(event)

    def _on_mute_toggled(self, checked):
        self._save_settings({"muted": checked})

    def _on_config_changed(self, options):
        # options 是全量（含份数0），转盘只显示有效份数的
        wheel_opts = [o for o in options if o.get("quota", -1) != 0]
        self.wheel.set_options(wheel_opts)
        self._save_config(options)

    def _on_spin_clicked(self):
        wheel_opts = self.panel.get_wheel_options()
        if not wheel_opts:
            self.panel.show_result("没有可用选项！")
            return
        if not self.drawer.btn_mute.isChecked():
            self._sound.play_random()
        self.panel.set_spinning(True)
        self.wheel.spin()

    def _on_spin_finished(self, winner_text):
        # 扣减份数，获取全量选项（含份数为0的）存盘
        all_options = self.panel.consume_quota(winner_text)
        self._save_config(all_options)
        # 刷新转盘（只显示份数>0或无限的），保留当前角度不跳回原位
        wheel_options = self.panel.get_wheel_options()
        self.wheel.set_options(wheel_options, reset_angle=False)
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

    def _load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_settings(self, patch):
        settings = self._load_settings()
        settings.update(patch)
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
