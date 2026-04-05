from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPainterPath
import os, json

def _get_config_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "LuckyWheel")
    os.makedirs(path, exist_ok=True)
    return path

BG_CONFIG_FILE = os.path.join(_get_config_dir(), "bg_config.json")

DRAWER_W = 220

# 更新按钮样式
BTN_STYLE = """
    QPushButton {
        background: rgba(30, 41, 59, 0.9);
        color: #CBD5E0; 
        border: 1px solid rgba(71, 85, 105, 0.7);
        border-radius: 8px; 
        padding: 8px 12px;
        font-family: 微软雅黑; 
        font-size: 13px; 
        text-align: left;
    }
    QPushButton:hover { 
        background: rgba(45, 62, 82, 0.9); 
        color: #FFFFFF; 
    }
    QPushButton:pressed { 
        background: rgba(15, 23, 42, 0.9); 
    }
"""

TOGGLE_STYLE = """
    QPushButton {
        background-color: rgba(26, 26, 46, 0.9);
        color: #A0AEC0; 
        border: 1px solid rgba(71, 85, 105, 0.7);
        border-radius: 6px 0 0 6px;
        font-size: 16px;
        border-right: none;
    }
    QPushButton:hover { 
        background-color: rgba(45, 62, 82, 0.9); 
        color: white; 
    }
"""

# 更新标签样式
SECTION_LABEL = """
    color: #CBD5E0; 
    font-family: 微软雅黑; 
    font-size: 11px; 
    background: transparent;
    padding: 4px 0;
    font-weight: 600;
"""

VALUE_LABEL = """
    color: #E2E8F0; 
    font-family: 微软雅黑; 
    font-size: 11px; 
    padding: 2px 0; 
    background: transparent;
    margin: 4px 0;
"""


class BgDrawer(QWidget):
    """可从右侧滑入/滑出的背景设置抽屉"""
    wheel_bg_change = pyqtSignal(str)
    wheel_bg_clear = pyqtSignal()
    window_bg_change = pyqtSignal(str)
    window_bg_clear = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("drawer")
        self._open = False
        
        self.bg_config = self._load_default_bg()

        # 启用透明度
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(280)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self._build_ui()

        # 拨片按钮（固定在抽屉左侧外）
        self._toggle_btn = QPushButton("⚙", parent)
        self._toggle_btn.setFixedSize(28, 64)
        self._toggle_btn.setStyleSheet(TOGGLE_STYLE)
        self._toggle_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_btn.clicked.connect(self.toggle)
        self._toggle_btn.raise_()

        # 初始隐藏（收起状态）
        self.hide()
    
    def paintEvent(self, event):
        """绘制磨砂背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制磨砂背景
        painter.setBrush(QBrush(QColor(30, 41, 59, 217)))  # 85% 透明度
        painter.setPen(Qt.NoPen)
        
        # 创建圆角矩形路径 - 使用QRectF
        rect_f = QRectF(self.rect())
        painter.drawRoundedRect(rect_f, 12, 12)
        
        # 绘制左侧边框
        painter.setPen(QColor(71, 85, 105, 128))
        painter.drawLine(0, 12, 0, self.height() - 12)
        
        # 调用父类的绘制方法，确保子控件正确显示
        super().paintEvent(event)
    
    def _build_ui(self):
        # 设置一个布局，确保子控件能够正确显示
        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(16)

        title = QLabel("背景设置")
        title.setFont(QFont("微软雅黑", 13, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        layout.addWidget(line)

        # ── 转盘背景 ──
        layout.addWidget(self._section("转盘背景"))
        self.lbl_wheel_bg = QLabel("未设置")
        self.lbl_wheel_bg.setStyleSheet(VALUE_LABEL)
        self.lbl_wheel_bg.setWordWrap(True)
        layout.addWidget(self.lbl_wheel_bg)

        btn_wheel = QPushButton("🖼  选择图片 / GIF")
        btn_wheel.setStyleSheet(BTN_STYLE)
        btn_wheel.clicked.connect(self._pick_wheel_bg)
        layout.addWidget(btn_wheel)

        btn_wheel_clr = QPushButton("✕  清除转盘背景")
        btn_wheel_clr.setStyleSheet(BTN_STYLE)
        btn_wheel_clr.clicked.connect(self._clear_wheel_bg)
        layout.addWidget(btn_wheel_clr)

        layout.addSpacing(8)

        # ── 全局背景 ──
        layout.addWidget(self._section("全局背景"))
        self.lbl_win_bg = QLabel("未设置")
        self.lbl_win_bg.setStyleSheet(VALUE_LABEL)
        self.lbl_win_bg.setWordWrap(True)
        layout.addWidget(self.lbl_win_bg)

        btn_win = QPushButton("🖼  选择图片 / GIF")
        btn_win.setStyleSheet(BTN_STYLE)
        btn_win.clicked.connect(self._pick_window_bg)
        layout.addWidget(btn_win)

        btn_win_clr = QPushButton("✕  清除全局背景")
        btn_win_clr.setStyleSheet(BTN_STYLE)
        btn_win_clr.clicked.connect(self._clear_window_bg)
        layout.addWidget(btn_win_clr)

        layout.addStretch()


    def _section(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(SECTION_LABEL)
        return lbl

    def load_bg(self):
        """加载已保存的背景，并发送信号"""
        if self.bg_config:
            win_bg = self.bg_config.get("win_bg", "")
            wheel_bg = self.bg_config.get("wheel_bg", "")
            if win_bg and os.path.exists(win_bg):
                self.lbl_win_bg.setText(os.path.basename(win_bg))
                self.window_bg_change.emit(win_bg)
            if wheel_bg and os.path.exists(wheel_bg):
                self.lbl_wheel_bg.setText(os.path.basename(wheel_bg))
                self.wheel_bg_change.emit(wheel_bg)

    # ── 默认背景加载 ──
    def _load_default_bg(self):
        # 尝试加载默认路径
        if os.path.exists(BG_CONFIG_FILE):
            try:
                with open(BG_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
            except Exception:
                pass
        return dict()

    def _save_default_bg(self):
        try:
            with open(BG_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.bg_config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ── 转盘背景 ──
    def _pick_wheel_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择转盘背景", "",
            "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp)"
        )
        if path:
            import os
            self.lbl_wheel_bg.setText(os.path.basename(path))
            self.wheel_bg_change.emit(path)
            self.bg_config["wheel_bg"] = path
            self._save_default_bg()

    def _clear_wheel_bg(self):
        self.lbl_wheel_bg.setText("未设置")
        self.wheel_bg_clear.emit()
        self.bg_config["wheel_bg"] = ""
        self._save_default_bg()

    
    # ── 全局背景 ──
    def _pick_window_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择全局背景", "",
            "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp)"
        )
        if path:
            import os
            self.lbl_win_bg.setText(os.path.basename(path))
            self.window_bg_change.emit(path)
            self.bg_config["win_bg"] = path
            self._save_default_bg()

    def _clear_window_bg(self):
        self.lbl_win_bg.setText("未设置")
        self.window_bg_clear.emit()
        self.bg_config["win_bg"] = ""
        self._save_default_bg()

    # ── 展开/收起 ──
    def toggle(self):
        if self._open:
            self.close_drawer()
        else:
            self.open_drawer()

    def open_drawer(self):
        self._open = True
        parent = self.parent()
        ph, pw = parent.height(), parent.width()
        self.setGeometry(pw, 0, DRAWER_W, ph)
        self.show()
        self.raise_()
        self._anim.stop()
        self._anim.setStartValue(QRect(pw, 0, DRAWER_W, ph))
        self._anim.setEndValue(QRect(pw - DRAWER_W, 0, DRAWER_W, ph))
        self._anim.start()
        self._update_toggle_pos()

    def close_drawer(self):
        self._open = False
        parent = self.parent()
        ph, pw = parent.height(), parent.width()
        self._anim.stop()
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(QRect(pw, 0, DRAWER_W, ph))
        self._anim.finished.connect(self._on_close_done)
        self._anim.start()
        self._update_toggle_pos()

    def _on_close_done(self):
        self._anim.finished.disconnect(self._on_close_done)
        self.hide()

    def reposition(self, parent_w, parent_h):
        """父窗口 resize 时调用"""
        if self._open:
            self.setGeometry(parent_w - DRAWER_W, 0, DRAWER_W, parent_h)
        self._update_toggle_pos()

    def _update_toggle_pos(self):
        parent = self.parent()
        ph, pw = parent.height(), parent.width()
        btn_y = (ph - 64) // 2
        if self._open:
            self._toggle_btn.move(pw - DRAWER_W - 28, btn_y)
        else:
            self._toggle_btn.move(pw - 28, btn_y)