"""
Live Leaderboard & Statistics Widget for Algorithm Racing Arena.

Displays real-time rankings, detailed operation counters, computation benchmarks,
and dynamic comparative charts of participating algorithms.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QProgressBar,
)

from app.theme import COLORS
from app.racing.race_models import RacerState


class _ComparativeBarChart(QWidget):
    """Draws horizontal comparison bars for all racers' operation counts or time."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(120)
        self._racers: list[RacerState] = []
        self._metric = "operations"  # or "time"

    def set_racers(self, racers: list[RacerState], metric: str = "operations") -> None:
        self._racers = list(racers)
        self._metric = metric
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(COLORS["bg_secondary"]))

        if not self._racers:
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "No active race data.")
            return

        n = len(self._racers)
        row_h = (h - 16) / max(n, 1)

        # Get max metric for scale
        if self._metric == "time":
            vals = [r.elapsed_time_ms for r in self._racers]
        else:
            vals = [max(r.operations, 1) for r in self._racers]
        max_val = max(vals) if vals else 1
        max_val = max(max_val, 1)

        label_w = 80
        bar_area_w = w - label_w - 60

        for idx, racer in enumerate(self._racers):
            y = 8 + idx * row_h
            val = racer.elapsed_time_ms if self._metric == "time" else racer.operations

            # Draw algorithm name
            painter.setPen(QColor(COLORS["text_secondary"]))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(QRectF(8, y, label_w - 10, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, racer.name[:12])

            # Draw bar
            bar_len = max(4.0, (val / max_val) * bar_area_w)
            bar_rect = QRectF(label_w, y + 3, bar_len, row_h - 6)
            painter.fillRect(bar_rect, QColor(racer.color))

            # Draw value text
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.setFont(QFont("Consolas", 8))
            val_str = f"{val:.2f}ms" if self._metric == "time" else str(val)
            painter.drawText(QRectF(label_w + bar_len + 6, y, 50, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, val_str)


class RaceLeaderboardWidget(QFrame):
    """Real-time ranking board with comparative metrics for all racers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(310)
        self._rows: dict[str, QWidget] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            RaceLeaderboardWidget {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header
        head_row = QHBoxLayout()
        title = QLabel("🏆  LIVE LEADERBOARD")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #D95F42;")
        head_row.addWidget(title)
        head_row.addStretch()

        self._badge = QLabel("READY")
        self._badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_muted']};
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        head_row.addWidget(self._badge)
        layout.addLayout(head_row)

        # Scrollable rows area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(6)
        self._scroll.setWidget(self._rows_container)
        layout.addWidget(self._scroll, 1)

        # Comparative Chart Header
        chart_head = QLabel("📊 Metric Comparison")
        chart_head.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        chart_head.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-top: 4px;")
        layout.addWidget(chart_head)

        self._chart = _ComparativeBarChart()
        layout.addWidget(self._chart)

    def update_leaderboard(self, racers_dict: dict[str, RacerState]) -> None:
        if not racers_dict:
            return

        # Sort racers by current rank or operations
        sorted_racers = sorted(
            racers_dict.values(),
            key=lambda r: (r.rank if r.rank > 0 else 999, r.operations)
        )

        # Clear existing rows
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, racer in enumerate(sorted_racers):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {'#eab308' if racer.is_leader else COLORS['border']};
                    border-radius: 8px;
                    padding: 4px;
                }}
            """)
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(8, 6, 8, 6)
            card_lay.setSpacing(8)

            # Rank Icon / Number
            rank_text = {1: "🥇", 2: "🥈", 3: "🥉"}.get(racer.rank, f"#{racer.rank}")
            rank_lbl = QLabel(rank_text)
            rank_lbl.setFont(QFont("Segoe UI Emoji", 12))
            rank_lbl.setFixedWidth(26)
            card_lay.addWidget(rank_lbl)

            # Name & details
            mid_lay = QVBoxLayout()
            mid_lay.setContentsMargins(0, 0, 0, 0)
            mid_lay.setSpacing(2)

            name_lbl = QLabel(f"{racer.icon} {racer.name}")
            name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            name_lbl.setStyleSheet(f"color: {racer.color};")
            mid_lay.addWidget(name_lbl)

            detail_lbl = QLabel(f"{racer.operations} ops  •  {racer.elapsed_time_ms:.2f}ms")
            detail_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 9px;")
            mid_lay.addWidget(detail_lbl)
            card_lay.addLayout(mid_lay, 1)

            # Progress %
            pct_lbl = QLabel(f"{int(racer.progress_percent)}%")
            pct_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            pct_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
            card_lay.addWidget(pct_lbl)

            self._rows_layout.addWidget(card)

        self._rows_layout.addStretch()

        # Update comparative chart
        self._chart.set_racers(sorted_racers)
