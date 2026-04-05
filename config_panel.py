from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QAbstractItemView, QFrame, QMessageBox,
    QGraphicsDropShadowEffect, QColorDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QBrush

from wheel_widget import DEFAULT_COLORS

DEFAULT_OPTIONS = [
    {"text": "一等奖",  "weight": 5,   "text_color": "#FFFFFF", "quota": -1},
    {"text": "二等奖",  "weight": 15,  "text_color": "#FFFFFF", "quota": -1},
    {"text": "三等奖",  "weight": 30,  "text_color": "#FFFFFF", "quota": -1},
    {"text": "幸运奖",  "weight": 50,  "text_color": "#FFFFFF", "quota": -1},
    {"text": "谢谢参与","weight": 100, "text_color": "#FFFFFF", "quota": -1},
    {"text": "再来一次","weight": 80,  "text_color": "#FFFFFF", "quota": -1},
]

# 列索引
COL_TEXT   = 0
COL_COLOR  = 1   # 字色（色块，点击弹出颜色选择）
COL_WEIGHT = 2   # 权重（默认隐藏）
COL_QUOTA  = 3   # 份数（默认隐藏，-1=无限）

BTN_PRIMARY = """
    QPushButton {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #FF6B6B, stop:1 #EE5A24);
        color: white; border: none; border-radius: 10px;
        font-family: 微软雅黑; font-size: 16px; font-weight: bold;
        letter-spacing: 4px;
    }
    QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #FF8E8E, stop:1 #FF6B35); }
    QPushButton:disabled { background: #4A4A6A; color: #888; }
"""

BTN_SECONDARY = """
    QPushButton {
        background: rgba(255,255,255,0.08);
        color: #C8D6E5; border: 1px solid rgba(255,255,255,0.15);
        border-radius: 6px; padding: 4px 10px;
        font-family: 微软雅黑; font-size: 12px;
    }
    QPushButton:hover { background: rgba(255,255,255,0.16); }
    QPushButton:checked { background: rgba(255,107,107,0.25);
        border-color: #FF6B6B; color: #FF6B6B; }
"""

TABLE_STYLE = """
    QTableWidget {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px; color: #E0E0E0;
        gridline-color: rgba(255,255,255,0.08);
        font-family: 微软雅黑; font-size: 13px;
        selection-background-color: rgba(255,107,107,0.3);
    }
    QHeaderView::section {
        background: rgba(255,255,255,0.10); color: #A0AEC0;
        border: none; padding: 6px;
        font-family: 微软雅黑; font-size: 12px;
    }
    QTableWidget::item { padding: 4px 6px; }
    QTableWidget::item:selected { color: white; }
    QScrollBar:vertical { background: transparent; width: 6px; }
    QScrollBar::handle:vertical { background: rgba(255,255,255,0.2); border-radius: 3px; }
"""


class ConfigPanel(QWidget):
    config_changed = pyqtSignal(list)
    spin_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget#panel {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1A1A2E, stop:1 #16213E);
                border-radius: 16px;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        # 标题行 + 权重/份数切换
        title_row = QHBoxLayout()
        title = QLabel("今天也有好运气")
        title.setFont(QFont("幼圆", 14, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        title_row.addWidget(title)
        title_row.addStretch()

        self.btn_toggle_weight = QPushButton("权重")
        self.btn_toggle_weight.setCheckable(True)
        self.btn_toggle_weight.setChecked(False)
        self.btn_toggle_weight.setFixedSize(52, 26)
        self.btn_toggle_weight.setStyleSheet(BTN_SECONDARY)
        self.btn_toggle_weight.toggled.connect(self._toggle_weight_column)
        title_row.addWidget(self.btn_toggle_weight)

        self.btn_toggle_quota = QPushButton("份数")
        self.btn_toggle_quota.setCheckable(True)
        self.btn_toggle_quota.setChecked(False)
        self.btn_toggle_quota.setFixedSize(52, 26)
        self.btn_toggle_quota.setStyleSheet(BTN_SECONDARY)
        self.btn_toggle_quota.toggled.connect(self._toggle_quota_column)
        title_row.addWidget(self.btn_toggle_quota)

        layout.addLayout(title_row)

        # 不管份数按钮行
        ignore_row = QHBoxLayout()
        ignore_row.addStretch()
        self.btn_ignore_quota = QPushButton("不管份数")
        self.btn_ignore_quota.setCheckable(True)
        self.btn_ignore_quota.setChecked(False)
        self.btn_ignore_quota.setFixedSize(80, 26)
        self.btn_ignore_quota.setStyleSheet(BTN_SECONDARY)
        ignore_row.addWidget(self.btn_ignore_quota)
        layout.addLayout(ignore_row)

        # 表格：选项名称 | 字色 | 权重 | 份数
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["选项名称", "字色", "权重", "份数"])
        hh = self.table.horizontalHeader()

        hh.setStyleSheet("""
            QHeaderView::section {
                color: #000000;
                font-family: 幼圆;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        hh.setSectionResizeMode(COL_TEXT,   QHeaderView.Stretch)
        hh.setSectionResizeMode(COL_COLOR,  QHeaderView.Fixed)
        hh.setSectionResizeMode(COL_WEIGHT, QHeaderView.Fixed)
        hh.setSectionResizeMode(COL_QUOTA,  QHeaderView.Fixed)
        self.table.setColumnWidth(COL_COLOR,  40)
        self.table.setColumnWidth(COL_WEIGHT, 50)
        self.table.setColumnWidth(COL_QUOTA,  50)
        self.table.setColumnHidden(COL_WEIGHT, True)
        self.table.setColumnHidden(COL_QUOTA,  True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setMinimumHeight(200)
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

        # 添加 / 删除
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_add = QPushButton("＋ 添加")
        self.btn_del = QPushButton("－ 删除")
        for btn in (self.btn_add, self.btn_del):
            btn.setFixedHeight(32)
            btn.setStyleSheet(BTN_SECONDARY)
        self.btn_add.clicked.connect(self._add_row)
        self.btn_del.clicked.connect(self._delete_row)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_del)
        layout.addLayout(btn_row)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.10);")
        layout.addWidget(line)

        # 抽奖按钮
        self.btn_spin = QPushButton("开 始 抽 奖")
        self.btn_spin.setFixedHeight(56)
        self.btn_spin.setStyleSheet(BTN_PRIMARY)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#EE5A24"))
        shadow.setOffset(0, 4)
        self.btn_spin.setGraphicsEffect(shadow)
        self.btn_spin.clicked.connect(self.spin_clicked.emit)
        layout.addWidget(self.btn_spin)

        # 结果显示
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(64)
        self.result_label.setStyleSheet("""
            color: #FFD700; font-family: 微软雅黑; font-size: 15px;
            font-weight: bold; background: rgba(255,215,0,0.08);
            border-radius: 8px; padding: 8px;
        """)
        layout.addWidget(self.result_label)
        layout.addStretch()

    # ── 权重列显隐 ──
    def _toggle_weight_column(self, checked):
        self.table.setColumnHidden(COL_WEIGHT, not checked)
        self.btn_toggle_weight.setText("隐藏" if checked else "权重")

    # ── 份数列显隐 ──
    def _toggle_quota_column(self, checked):
        self.table.setColumnHidden(COL_QUOTA, not checked)
        self.btn_toggle_quota.setText("隐藏" if checked else "份数")

    # ── 字色列点击 ──
    def _on_cell_clicked(self, row, col):
        if col != COL_COLOR:
            return
        item = self.table.item(row, COL_COLOR)
        current = item.data(Qt.UserRole) if item else "#FFFFFF"
        color = QColorDialog.getColor(QColor(current), self, "选择文字颜色")
        if color.isValid():
            self._set_color_cell(row, color.name())
            self._emit_change()

    def _set_color_cell(self, row, hex_color):
        """在字色列显示纯色色块"""
        item = self.table.item(row, COL_COLOR)
        if item is None:
            item = QTableWidgetItem()
            self.table.setItem(row, COL_COLOR, item)
        item.setData(Qt.UserRole, hex_color)
        item.setBackground(QBrush(QColor(hex_color)))
        item.setText("")
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    # ── 数据操作 ──
    def load_options(self, options):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for opt in options:
            self._append_row(
                opt["text"],
                opt.get("weight", 1),
                opt.get("text_color", "#FFFFFF"),
                opt.get("quota", -1)
            )
        self.table.blockSignals(False)

    def get_options(self):
        """返回所有选项（含份数为0的），供保存和列表显示用"""
        options = []
        for row in range(self.table.rowCount()):
            text_item   = self.table.item(row, COL_TEXT)
            color_item  = self.table.item(row, COL_COLOR)
            weight_item = self.table.item(row, COL_WEIGHT)
            quota_item  = self.table.item(row, COL_QUOTA)
            text = text_item.text().strip() if text_item else ""
            text_color = (color_item.data(Qt.UserRole)
                          if color_item and color_item.data(Qt.UserRole)
                          else "#FFFFFF")
            try:
                weight = max(1, int(weight_item.text())) if weight_item else 1
            except ValueError:
                weight = 1
            if quota_item:
                qt = quota_item.text().strip()
                quota = -1 if qt in ("∞", "") else (int(qt) if qt.lstrip("-").isdigit() else -1)
            else:
                quota = -1
            if text:
                options.append({
                    "text": text,
                    "weight": weight,
                    "color": DEFAULT_COLORS[row % len(DEFAULT_COLORS)],
                    "text_color": text_color,
                    "quota": quota,
                })
        return options

    def get_wheel_options(self):
        """返回供转盘使用的选项（过滤掉份数为0的）"""
        return [o for o in self.get_options() if o.get("quota", -1) != 0]

    def _append_row(self, text, weight, text_color="#FFFFFF", quota=-1):
        self.table.blockSignals(True)
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, COL_TEXT, QTableWidgetItem(text))
        self._set_color_cell(row, text_color)

        w_item = QTableWidgetItem(str(weight))
        w_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, COL_WEIGHT, w_item)

        # 份数：-1 表示无限，显示为"∞"
        q_item = QTableWidgetItem("∞" if quota < 0 else str(quota))
        q_item.setTextAlignment(Qt.AlignCenter)
        if quota == 0:
            q_item.setForeground(QBrush(QColor("#888888")))
        self.table.setItem(row, COL_QUOTA, q_item)

        self.table.blockSignals(False)

    def _add_row(self):
        self._append_row("新选项", 10, "#FFFFFF", -1)
        self._emit_change()
        new_row = self.table.rowCount() - 1
        self.table.setCurrentCell(new_row, COL_TEXT)
        self.table.editItem(self.table.item(new_row, COL_TEXT))

    def _delete_row(self):
        if not self.table.selectedItems():
            return
        if self.table.rowCount() <= 2:
            QMessageBox.warning(self, "提示", "至少保留 2 个选项")
            return
        self.table.removeRow(self.table.currentRow())
        self._emit_change()

    def _on_item_changed(self, item):
        col = item.column()
        if col == COL_WEIGHT:
            try:
                v = int(item.text())
                if v < 1:
                    raise ValueError
            except ValueError:
                self.table.blockSignals(True)
                item.setText("1")
                self.table.blockSignals(False)
        elif col == COL_QUOTA:
            text = item.text().strip()
            if text in ("∞", "-1", ""):
                self.table.blockSignals(True)
                item.setText("∞")
                item.setForeground(QBrush(QColor("#E0E0E0")))
                self.table.blockSignals(False)
            else:
                try:
                    v = int(text)
                    if v < 0:
                        self.table.blockSignals(True)
                        item.setText("∞")
                        item.setForeground(QBrush(QColor("#E0E0E0")))
                        self.table.blockSignals(False)
                    elif v == 0:
                        item.setForeground(QBrush(QColor("#888888")))
                    else:
                        item.setForeground(QBrush(QColor("#E0E0E0")))
                except ValueError:
                    self.table.blockSignals(True)
                    item.setText("∞")
                    item.setForeground(QBrush(QColor("#E0E0E0")))
                    self.table.blockSignals(False)
        self._emit_change()

    def _emit_change(self):
        opts = self.get_options()
        if opts:
            self.config_changed.emit(opts)

    def is_ignore_quota(self):
        return self.btn_ignore_quota.isChecked()

    def consume_quota(self, winner_text):
        """找到获奖选项，若不忽略份数则减一，返回更新后的全部选项"""
        if self.btn_ignore_quota.isChecked():
            return self.get_options()

        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            text_item = self.table.item(row, COL_TEXT)
            if text_item and text_item.text().strip() == winner_text:
                quota_item = self.table.item(row, COL_QUOTA)
                if quota_item:
                    try:
                        current_text = quota_item.text().strip()
                        if current_text == "∞":
                            break  # 无限份数，不扣减
                        q = int(current_text)
                        if q > 0:
                            q -= 1
                            quota_item.setText(str(q))
                            if q == 0:
                                quota_item.setForeground(QBrush(QColor("#888888")))
                    except ValueError:
                        pass
                break
        self.table.blockSignals(False)
        return self.get_options()

    def show_result(self, text):
        self.result_label.setText(f"🎉 恭喜获得\n{text}")
        self.btn_spin.setEnabled(True)

    def set_spinning(self, spinning):
        self.btn_spin.setEnabled(not spinning)
        self.result_label.setText("转动中..." if spinning else "")
