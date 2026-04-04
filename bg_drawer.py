from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor

DRAWER_W = 220

DRAWER_STYLE = """
    QWidget#drawer {
        background-color: #111827;
        border-left: 2px solid #2D3748;
    }
    QLabel { background: transparent; }
"""

BTN_STYLE = """
    QPushButton {
        background: #1E2A3A;
        color: #CBD5E0; border: 1px solid #2D3748;
        border-radius: 8px; padding: 8px 12px;
        font-family: 微软雅黑; font-size: 13px; text-align: left;
    }
    QPushButton:hover { background: #2D3E52; color: #FFFFFF; }
"""

TOGGLE_STYLE = """
    QPushButton {
        background-color: #1A1A2E;
        color: #A0AEC0; border: 1px solid #2D3748;
        border-radius: 6px 0 0 6px;
        font-size: 16px;
        border-right: none;
    }
    QPushButton:hover { background-color: #2D3E52; color: white; }
"""

SECTION_LABEL = "color: #718096; font-family: 微软雅黑; font-size: 11px; background: transparent;"
VALUE_LABEL = "color: #A0AEC0; font-family: 微软雅黑; font-size: 11px; padding: 2px 0; background: transparent;"


class BgDrawer(QWidget):
    """可从右侧滑入/滑出的背景设置抽屉"""
    wheel_bg_change = pyqtSignal(str)
    wheel_bg_clear = pyqtSignal()
    window_bg_change = pyqtSignal(str)
    window_bg_clear = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("drawer")
        self.setStyleSheet(DRAWER_STYLE)
        self._open = False
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

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(16)

        title = QLabel("背景设置")
        title.setFont(QFont("微软雅黑", 13, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
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

    def _clear_wheel_bg(self):
        self.lbl_wheel_bg.setText("未设置")
        self.wheel_bg_clear.emit()

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

    def _clear_window_bg(self):
        self.lbl_win_bg.setText("未设置")
        self.window_bg_clear.emit()

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
