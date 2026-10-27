"""
Statistics panel — displays live comparisons, swaps, and complexity info.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)

from app.theme import COLORS


class _StatCard(QFrame):
    """A single metric card with label + value."""

    def __init__(
        self,
        label: str,
        initial: str = "0",
        accent: str = "",
    ) -> None:
        super().__init__()

        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        self._label = QLabel(label)
        self._label.setStyleSheet(
            f"""
            color: {COLORS['text_muted']};
            font-size: 10px;
            border: none;
            background: transparent;
            """
        )
        self._label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        layout.addWidget(self._label)

        color = accent or COLORS["text_primary"]

        self._value = QLabel(initial)
        self._value.setFont(
            QFont("Segoe UI", 18, QFont.Weight.Bold)
        )

        self._value.setStyleSheet(
            f"""
            color: {color};
            border: none;
            background: transparent;
            """
        )

        self._value.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        layout.addWidget(self._value)

    def set_value(self, text: str) -> None:
        self._value.setText(text)


class StatsPanel(QWidget):
    """Right-side panel showing live statistics."""

    maximize_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.setMinimumWidth(200)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ── Section title ────────────────────────────────────────
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📈  STATISTICS")
        title.setFont(
            QFont("Segoe UI", 12, QFont.Weight.Bold)
        )

        title.setStyleSheet(
            f"color: {COLORS['accent_cyan']}; padding: 4px 0;"
        )

        expand_btn = QPushButton("⛶")
        expand_btn.setFixedSize(28, 28)
        expand_btn.setToolTip("Maximize statistics")

        expand_btn.setStyleSheet(f"""
            QPushButton {{
                color: {COLORS['text_secondary']};
                background: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 16px;
            }}

            QPushButton:hover {{
                background: {COLORS['surface']};
                color: {COLORS['accent_cyan']};
            }}
        """)

        expand_btn.clicked.connect(
            self.maximize_requested.emit
        )

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(expand_btn)

        layout.addLayout(title_bar)

        # ── Stat cards ───────────────────────────────────────────

        self.card_comparisons = _StatCard(
            "COMPARISONS",
            "0",
            COLORS["comparing"]
        )

        self.card_swaps = _StatCard(
            "SWAPS",
            "0",
            COLORS["swapping"]
        )

        layout.addWidget(self.card_comparisons)
        layout.addWidget(self.card_swaps)

        # ── Divider ──────────────────────────────────────────────

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(
            f"color: {COLORS['border']};"
        )

        layout.addWidget(div)

        # ── Complexity ───────────────────────────────────────────

        cx_title = QLabel("⏱  COMPLEXITY")
        cx_title.setFont(
            QFont("Segoe UI", 12, QFont.Weight.Bold)
        )

        cx_title.setStyleSheet(
            f"color: {COLORS['accent_purple']}; padding: 4px 0;"
        )

        layout.addWidget(cx_title)

        self.card_time_cx = _StatCard(
            "TIME",
            "—",
            COLORS["accent_purple"]
        )

        self.card_space_cx = _StatCard(
            "SPACE",
            "—",
            COLORS["accent_pink"]
        )

        layout.addWidget(self.card_time_cx)
        layout.addWidget(self.card_space_cx)

        # ── Divider ──────────────────────────────────────────────

        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet(
            f"color: {COLORS['border']};"
        )

        layout.addWidget(div2)

        # ── Step info ────────────────────────────────────────────

        desc_title = QLabel("💬  STEP INFO")
        desc_title.setFont(
            QFont("Segoe UI", 12, QFont.Weight.Bold)
        )

        desc_title.setStyleSheet(
            f"color: {COLORS['accent_cyan']}; padding: 4px 0;"
        )

        layout.addWidget(desc_title)

        self.description_label = QLabel(
            "Select an algorithm to begin."
        )

        self.description_label.setWordWrap(True)

        self.description_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 10px;
            font-size: 12px;
            line-height: 1.4;
        """)

        layout.addWidget(self.description_label)

        layout.addStretch()

    # ── Public API ───────────────────────────────────────────────

    def update_stats(self, stats: dict) -> None:
        self.card_comparisons.set_value(
            str(stats.get("comparisons", "—"))
        )

        self.card_swaps.set_value(
            str(stats.get("swaps", "—"))
        )

    def set_complexity(
        self,
        time_cx: str,
        space_cx: str
    ) -> None:
        self.card_time_cx.set_value(
            time_cx or "—"
        )

        self.card_space_cx.set_value(
            space_cx or "—"
        )

    def set_description(self, text: str) -> None:
        self.description_label.setText(text)

    def reset(self) -> None:
        self.card_comparisons.set_value("0")
        self.card_swaps.set_value("0")

        self.description_label.setText(
            "Select an algorithm to begin."
        )