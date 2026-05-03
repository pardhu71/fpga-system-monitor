"""
FPGA System Monitor Dashboard
==============================
A PyQt5-based GUI dashboard that simulates real-time FPGA monitoring.
Built as a portfolio project to demonstrate GUI development skills.

Author: Masimukku Pardhasardhi
"""

import sys
import random
import math
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton,
    QProgressBar, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import pyqtgraph as pg


# ──────────────────────────────────────────────
#  THEME CONSTANTS
# ──────────────────────────────────────────────
BG_DARK      = "#0A0E1A"
BG_PANEL     = "#0F1626"
BG_CARD      = "#131D35"
ACCENT_CYAN  = "#00D4FF"
ACCENT_GREEN = "#00FF9C"
ACCENT_RED   = "#FF4560"
ACCENT_AMBER = "#FFB300"
TEXT_PRIMARY = "#E8F4FF"
TEXT_DIM     = "#4A6080"
BORDER       = "#1E3050"


# ──────────────────────────────────────────────
#  LIVE DATA SIMULATOR
# ──────────────────────────────────────────────
class FPGADataSimulator:
    def __init__(self, history_len=100):
        self.history_len = history_len
        self.clock_freq  = deque([0] * history_len, maxlen=history_len)
        self.temperature = deque([45] * history_len, maxlen=history_len)
        self.power       = deque([2.5] * history_len, maxlen=history_len)
        self.utilization = deque([30] * history_len, maxlen=history_len)
        self.t = 0

    def tick(self):
        self.t += 1
        freq = 225 + 20 * math.sin(self.t * 0.05) + random.gauss(0, 3)
        self.clock_freq.append(max(190, min(260, freq)))

        temp = list(self.temperature)[-1] + random.gauss(0, 0.8)
        self.temperature.append(max(35, min(90, temp)))

        pwr = list(self.power)[-1] + random.gauss(0, 0.1)
        self.power.append(max(1.5, min(4.5, pwr)))

        util = list(self.utilization)[-1] + random.gauss(0, 1.5)
        self.utilization.append(max(10, min(95, util)))

    def latest(self):
        return {
            "freq":  list(self.clock_freq)[-1],
            "temp":  list(self.temperature)[-1],
            "power": list(self.power)[-1],
            "util":  list(self.utilization)[-1],
        }


# ──────────────────────────────────────────────
#  STAT CARD WIDGET
# ──────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, title, unit, color=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.accent = color
        self.setFixedHeight(130)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; letter-spacing: 2px; background: transparent; border: none;")
        self.title_lbl.setFont(QFont("Courier New", 9))

        self.value_lbl = QLabel("—")
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold; background: transparent; border: none;")
        self.value_lbl.setFont(QFont("Courier New", 28, QFont.Bold))

        self.unit_lbl = QLabel(unit)
        self.unit_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; background: transparent; border: none;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.unit_lbl)

    def update_value(self, val):
        self.value_lbl.setText(f"{val:.1f}")

    def set_alert(self, alert: bool):
        color = ACCENT_RED if alert else self.accent
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold; background: transparent; border: none;")
        border = ACCENT_RED if alert else BORDER
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)


# ──────────────────────────────────────────────
#  UTILIZATION BAR WIDGET
# ──────────────────────────────────────────────
class UtilBar(QWidget):
    def __init__(self, label, color=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self.lbl = QLabel(label)
        self.lbl.setFixedWidth(80)
        self.lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px;")
        self.lbl.setFont(QFont("Courier New", 9))

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(10)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {BG_DARK};
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}80, stop:1 {color});
                border-radius: 5px;
            }}
        """)

        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setFixedWidth(38)
        self.pct_lbl.setAlignment(Qt.AlignRight)
        self.pct_lbl.setStyleSheet(f"color: {color}; font-size: 10px;")
        self.pct_lbl.setFont(QFont("Courier New", 9))

        layout.addWidget(self.lbl)
        layout.addWidget(self.bar)
        layout.addWidget(self.pct_lbl)

    def set_value(self, val):
        v = int(max(0, min(100, val)))
        self.bar.setValue(v)
        self.pct_lbl.setText(f"{v}%")


# ──────────────────────────────────────────────
#  STATUS DOT WIDGET
# ──────────────────────────────────────────────
class StatusDot(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self._on = True
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px;")

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px;")
        self.lbl.setFont(QFont("Courier New", 9))

        layout.addWidget(self.dot)
        layout.addWidget(self.lbl)
        layout.addStretch()

    def blink(self):
        self._on = not self._on
        self.dot.setStyleSheet(f"color: {'#00FF9C' if self._on else '#1E3050'}; font-size: 10px;")


# ──────────────────────────────────────────────
#  MAIN WINDOW
# ──────────────────────────────────────────────
class FPGADashboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.sim    = FPGADataSimulator(history_len=120)
        self.x_data = list(range(120))
        self._running = True

        self.setWindowTitle("FPGA System Monitor  |  Pardhasardhi")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(f"QMainWindow {{ background: {BG_DARK}; }}")
        self._build_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(300)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink)
        self.blink_timer.start(800)

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {BG_DARK};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        root.addLayout(self._header())
        root.addLayout(self._stat_cards())
        root.addLayout(self._charts_and_sidebar(), stretch=1)
        root.addLayout(self._status_bar())

    def _header(self):
        row = QHBoxLayout()

        title = QLabel("⬡  FPGA SYSTEM MONITOR")
        title.setFont(QFont("Courier New", 15, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT_CYAN}; letter-spacing: 3px;")

        subtitle = QLabel("Real-time Telemetry Dashboard  •  AI-Assisted Interface  •  Pardhasardhi")
        subtitle.setFont(QFont("Courier New", 9))
        subtitle.setStyleSheet(f"color: {TEXT_DIM};")

        self.toggle_btn = QPushButton("⏸  PAUSE")
        self.toggle_btn.setFixedSize(110, 34)
        self.toggle_btn.setFont(QFont("Courier New", 9, QFont.Bold))
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_CYAN};
                border: 1px solid {ACCENT_CYAN};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {ACCENT_CYAN}20;
            }}
        """)
        self.toggle_btn.clicked.connect(self._toggle)

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(title)
        col.addWidget(subtitle)

        row.addLayout(col)
        row.addStretch()
        row.addWidget(self.toggle_btn)
        return row

    def _stat_cards(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        self.card_freq  = StatCard("Clock Frequency", "MHz", ACCENT_CYAN)
        self.card_temp  = StatCard("Core Temperature", "°C",  ACCENT_AMBER)
        self.card_power = StatCard("Power Draw",       "W",   ACCENT_GREEN)
        self.card_util  = StatCard("LUT Utilization",  "%",   "#B388FF")

        for card in [self.card_freq, self.card_temp, self.card_power, self.card_util]:
            row.addWidget(card)
        return row

    def _charts_and_sidebar(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        charts_col = QVBoxLayout()
        charts_col.setSpacing(12)
        charts_col.addWidget(self._make_chart("CLOCK FREQUENCY", "MHz", ACCENT_CYAN,  "freq_plot"))
        charts_col.addWidget(self._make_chart("TEMPERATURE",     "°C",  ACCENT_AMBER, "temp_plot"))

        sidebar = self._sidebar()
        sidebar.setFixedWidth(280)

        row.addLayout(charts_col, stretch=2)
        row.addWidget(sidebar, stretch=0)
        return row

    def _make_chart(self, title, unit, color, attr_name):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        lbl = QLabel(title)
        lbl.setFont(QFont("Courier New", 9))
        lbl.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 2px; background: transparent; border: none;")
        layout.addWidget(lbl)

        pg.setConfigOption('background', BG_PANEL)
        pg.setConfigOption('foreground', TEXT_DIM)

        plot = pg.PlotWidget()
        plot.setStyleSheet("border: none; background: transparent;")
        plot.showGrid(x=False, y=True, alpha=0.15)
        plot.getAxis('left').setTextPen(pg.mkPen(color=TEXT_DIM))
        plot.getAxis('bottom').setTextPen(pg.mkPen(color=TEXT_DIM))
        plot.getAxis('left').setPen(pg.mkPen(color=BORDER))
        plot.getAxis('bottom').setPen(pg.mkPen(color=BORDER))
        plot.setMouseEnabled(x=False, y=False)
        plot.setMenuEnabled(False)
        plot.hideButtons()

        curve = plot.plot(
            self.x_data,
            [0] * 120,
            pen=pg.mkPen(color=color, width=2),
            fillLevel=0,
            brush=pg.mkBrush(color + "30")
        )

        layout.addWidget(plot)
        setattr(self, attr_name, curve)
        return frame

    def _sidebar(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        t = QLabel("RESOURCE UTILIZATION")
        t.setFont(QFont("Courier New", 9))
        t.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 2px; background: transparent; border: none;")
        layout.addWidget(t)

        self.bar_lut  = UtilBar("LUT",       "#B388FF")
        self.bar_ff   = UtilBar("Flip-Flop", ACCENT_CYAN)
        self.bar_bram = UtilBar("BRAM",      ACCENT_GREEN)
        self.bar_dsp  = UtilBar("DSP",       ACCENT_AMBER)
        self.bar_io   = UtilBar("I/O",       ACCENT_RED)

        for bar in [self.bar_lut, self.bar_ff, self.bar_bram, self.bar_dsp, self.bar_io]:
            layout.addWidget(bar)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(div)

        info_title = QLabel("DEVICE INFO")
        info_title.setFont(QFont("Courier New", 9))
        info_title.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 2px; background: transparent; border: none;")
        layout.addWidget(info_title)

        infos = [
            ("Device",  "Xilinx Virtex-7"),
            ("Family",  "7 Series"),
            ("Package", "FFG1157"),
            ("Speed",   "-2"),
        ]
        for k, v in infos:
            row = QHBoxLayout()
            kl = QLabel(k)
            kl.setFont(QFont("Courier New", 9))
            kl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent; border: none;")
            vl = QLabel(v)
            vl.setFont(QFont("Courier New", 9, QFont.Bold))
            vl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; border: none;")
            row.addWidget(kl)
            row.addStretch()
            row.addWidget(vl)
            layout.addLayout(row)

        layout.addStretch()
        return frame

    def _status_bar(self):
        row = QHBoxLayout()

        self.dot1 = StatusDot("PLL LOCKED")
        self.dot2 = StatusDot("JTAG CONNECTED")
        self.dot3 = StatusDot("AI ENGINE ACTIVE")

        self.time_lbl = QLabel("T+0s")
        self.time_lbl.setFont(QFont("Courier New", 9))
        self.time_lbl.setStyleSheet(f"color: {TEXT_DIM};")

        for d in [self.dot1, self.dot2, self.dot3]:
            row.addWidget(d)
        row.addStretch()
        row.addWidget(self.time_lbl)
        return row

    def _tick(self):
        if not self._running:
            return
        self.sim.tick()
        d = self.sim.latest()

        self.card_freq.update_value(d["freq"])
        self.card_temp.update_value(d["temp"])
        self.card_power.update_value(d["power"])
        self.card_util.update_value(d["util"])

        self.card_temp.set_alert(d["temp"] > 78)
        self.card_power.set_alert(d["power"] > 4.0)

        self.freq_plot.setData(self.x_data, list(self.sim.clock_freq))
        self.temp_plot.setData(self.x_data, list(self.sim.temperature))

        self.bar_lut.set_value(d["util"])
        self.bar_ff.set_value(d["util"] * 0.6 + random.gauss(0, 1))
        self.bar_bram.set_value(d["util"] * 0.3 + random.gauss(0, 0.5))
        self.bar_dsp.set_value(d["util"] * 0.45 + random.gauss(0, 1))
        self.bar_io.set_value(d["util"] * 0.2 + random.gauss(0, 0.5))

        elapsed = self.sim.t * 0.3
        self.time_lbl.setText(f"T+{elapsed:.0f}s")

    def _blink(self):
        self.dot1.blink()
        self.dot2.blink()
        self.dot3.blink()

    def _toggle(self):
        self._running = not self._running
        self.toggle_btn.setText("⏸  PAUSE" if self._running else "▶  RESUME")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("FPGA System Monitor")
    window = FPGADashboard()
    window.show()
    sys.exit(app.exec_())