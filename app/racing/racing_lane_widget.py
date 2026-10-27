"""
Racing Lane Widget for Algorithm Racing Arena.

Renders an individual algorithm's competitive track lane, including
its moving racer avatar, live array bar visualization, operations counters,
and dynamic finish line status.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QLinearGradient
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QProgressBar,
)

from app.theme import COLORS
from app.racing.race_models import RacerState


class _MiniVisualizerCanvas(QWidget):
    """Draws live array bars or graph path progress for this racer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(38)
        self._data: list[int] = []
        self._highlights: dict = {}
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    def update_state(self, data: Any, highlights: dict) -> None:
        if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
            self._data = list(data)
        elif isinstance(data, dict) and "path" in data:
            # Graph visualization fallback summary
            self._data = [len(data.get("path", []))]
        self._highlights = dict(highlights)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        w = self.width()
        h = self.height()

        # Track background
        painter.fillRect(0, 0, w, h, QColor(COLORS["bg_primary"]))

        if not self._data:
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "Waiting for race data...")
            return

        n = len(self._data)
        max_val = max(self._data) if self._data else 1
        max_val = max(max_val, 1)

        bar_width = max(1.0, (w - (n + 1)) / n)
        
        for i, val in enumerate(self._data):
            bar_h = max(3.0, (val / max_val) * (h - 4))
            x = 1 + i * (bar_width + 1)
            y = h - bar_h - 2

            # Determine highlight color
            hl_type = self._highlights.get(i, "")
            if hl_type == "comparing":
                col = QColor(COLORS["comparing"])
            elif hl_type == "swapping":
                col = QColor(COLORS["swapping"])
            elif hl_type == "sorted":
                col = QColor(COLORS["sorted"])
            elif hl_type == "pivot":
                col = QColor(COLORS["pivot"])
            elif hl_type == "found":
                col = QColor(COLORS["found"])
            else:
                col = QColor(COLORS["default_bar"])

            painter.fillRect(QRectF(x, y, bar_width, bar_h), col)


class RacingLaneWidget(QFrame):
    """A horizontal racing track lane representing a competing algorithm."""

    def __init__(self, racer_state: RacerState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._racer = racer_state
        self.setFixedHeight(94)
        self._build_ui()
        self.update_state(racer_state)

    def _build_ui(self) -> None:
        self.setObjectName("racing_lane")
        self.setStyleSheet(f"""
            QFrame#racing_lane {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # ── Left: Racer Info ──────────────────────────────────────────
        left_box = QWidget()
        left_box.setFixedWidth(200)
        left_lay = QVBoxLayout(left_box)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(3)

        # Top row: Icon, Name, Rank badge
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        self._icon_lbl = QLabel(self._racer.icon)
        self._icon_lbl.setFont(QFont("Segoe UI Emoji", 15))
        name_row.addWidget(self._icon_lbl)

        self._name_lbl = QLabel(self._racer.name)
        self._name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._name_lbl.setStyleSheet(f"color: {self._racer.color};")
        name_row.addWidget(self._name_lbl)

        name_row.addStretch()

        self._rank_pill = QLabel("#-")
        self._rank_pill.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 1px 6px;
                font-size: 10px;
                font-weight: bold;
                color: {COLORS['text_secondary']};
            }}
        """)
        name_row.addWidget(self._rank_pill)
        left_lay.addLayout(name_row)

        # Middle row: Complexity tag & Space
        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)

        comp_badge = QLabel(self._racer.complexity)
        comp_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['accent_cyan']};
                padding: 1px 6px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
            }}
        """)
        meta_row.addWidget(comp_badge)

        space_badge = QLabel(self._racer.space_complexity)
        space_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_muted']};
                padding: 1px 6px;
                border-radius: 4px;
                font-size: 10px;
            }}
        """)
        meta_row.addWidget(space_badge)
        meta_row.addStretch()
        left_lay.addLayout(meta_row)

        # Bottom row: Operations count
        self._ops_lbl = QLabel("Ops: 0  •  Comps: 0  •  Swaps: 0")
        self._ops_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        left_lay.addWidget(self._ops_lbl)

        layout.addWidget(left_box)

        # ── Middle: Animated Racing Lane Track ────────────────────────
        track_box = QWidget()
        track_lay = QVBoxLayout(track_box)
        track_lay.setContentsMargins(0, 0, 0, 0)
        track_lay.setSpacing(4)

        # Track progress row with Start and Finish markers
        prog_row = QHBoxLayout()
        prog_row.setSpacing(8)

        start_flag = QLabel("🚩")
        start_flag.setToolTip("Start line")
        prog_row.addWidget(start_flag)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self._racer.color}, stop:1 #ffffff);
                border-radius: 3px;
            }}
        """)
        prog_row.addWidget(self._progress_bar, 1)

        self._pct_lbl = QLabel("0%")
        self._pct_lbl.setFixedWidth(38)
        self._pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._pct_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: bold;")
        prog_row.addWidget(self._pct_lbl)

        finish_flag = QLabel("🏁")
        finish_flag.setToolTip("Finish line")
        prog_row.addWidget(finish_flag)

        track_lay.addLayout(prog_row)

        # Mini Visualizer Canvas (bars)
        self._canvas = _MiniVisualizerCanvas()
        track_lay.addWidget(self._canvas)

        # Live operation description
        self._desc_lbl = QLabel("Ready to race.")
        self._desc_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        track_lay.addWidget(self._desc_lbl)

        layout.addWidget(track_box, 1)

        # ── Right: Live Status Badge ──────────────────────────────────
        right_box = QWidget()
        right_box.setFixedWidth(130)
        right_lay = QVBoxLayout(right_box)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(4)
        right_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_badge = QLabel("WAITING")
        self._status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        right_lay.addWidget(self._status_badge)

        self._time_lbl = QLabel(f"⚡ {self._racer.elapsed_time_ms:.2f} ms")
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_lbl.setToolTip("Measured computation benchmark time")
        self._time_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        right_lay.addWidget(self._time_lbl)

        layout.addWidget(right_box)

    # ── State Synchronization ─────────────────────────────────────────
    def update_state(self, racer: RacerState) -> None:
        self._racer = racer

        # Rank badge
        if racer.rank > 0:
            rank_text = {1: "🥇 1st", 2: "🥈 2nd", 3: "🥉 3rd"}.get(racer.rank, f"#{racer.rank}")
            self._rank_pill.setText(rank_text)
            if racer.rank == 1:
                self._rank_pill.setStyleSheet(f"""
                    QLabel {{
                        background-color: #713f12;
                        border: 1px solid #eab308;
                        border-radius: 8px;
                        padding: 1px 6px;
                        font-size: 10px;
                        font-weight: bold;
                        color: #fef08a;
                    }}
                """)
            else:
                self._rank_pill.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['bg_secondary']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 1px 6px;
                        font-size: 10px;
                        font-weight: bold;
                        color: {COLORS['text_secondary']};
                    }}
                """)

        # Operations counter
        self._ops_lbl.setText(f"Ops: {racer.operations}  •  Comps: {racer.comparisons}  •  Swaps: {racer.swaps}")

        # Progress bar
        pct = int(racer.progress_percent)
        self._progress_bar.setValue(pct)
        self._pct_lbl.setText(f"{pct}%")

        # Mini Canvas
        self._canvas.update_state(racer.current_data, racer.highlights)

        # Description
        desc = racer.current_description or ""
        if len(desc) > 65:
            desc = desc[:62] + "..."
        self._desc_lbl.setText(desc)

        # Status badge styling
        if racer.status == "FINISHED":
            if racer.rank == 1:
                self._status_badge.setText("🏆 WINNER")
                self._status_badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: #854d0e;
                        color: #fef08a;
                        border: 1px solid #facc15;
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
            else:
                rank_str = {2: "🥈 2nd Place", 3: "🥉 3rd Place"}.get(racer.rank, f"FINISHED (#{racer.rank})")
                self._status_badge.setText(rank_str)
                self._status_badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: #14532d;
                        color: #86efac;
                        border: 1px solid #22c55e;
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
        elif racer.status == "RACING":
            if racer.is_leader:
                self._status_badge.setText("👑 LEADING")
                self._status_badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: #1e3a5f;
                        color: #38bdf8;
                        border: 1px solid #38bdf8;
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
            else:
                self._status_badge.setText(f"🔥 Step {racer.current_step}")
                self._status_badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['bg_secondary']};
                        color: {COLORS['accent_cyan']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
        elif racer.status == "PAUSED":
            self._status_badge.setText("⏸️ PAUSED")
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['warning']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
        else:
            self._status_badge.setText("READY")
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_muted']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)

        # Leader outline highlight
        if racer.is_leader and racer.status == "RACING":
            self.setStyleSheet(f"""
                QFrame#racing_lane {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {racer.color};
                    border-left: 4px solid {racer.color};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#racing_lane {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 10px;
                }}
            """)
