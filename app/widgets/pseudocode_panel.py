"""
Pseudocode panel — shows pseudocode lines with the current step highlighted.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QPushButton,
)

from app.theme import COLORS


class PseudocodePanel(QWidget):
    """Right-side panel displaying pseudocode with line highlighting."""

    maximize_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(200)
        self._lines: list[QLabel] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # ── Title bar ────────────────────────────────────────────
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📝  PSEUDOCODE")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {COLORS['accent_cyan']}; padding: 4px 0 8px 0;"
        )

        expand_btn = QPushButton("⛶")
        expand_btn.setFixedSize(28, 28)
        expand_btn.setToolTip("Maximize pseudocode")
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

        expand_btn.clicked.connect(self.maximize_requested.emit)

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(expand_btn)

        layout.addLayout(title_bar)

        # ── Scrollable container ─────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)

        self._content = QWidget()
        self._content.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
        )

        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 8, 4, 8)
        self._content_layout.setSpacing(0)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content)

        layout.addWidget(self._scroll, 1)

    # ── Public API ───────────────────────────────────────────────

    def set_pseudocode(self, lines: list[str]) -> None:
        """Replace displayed pseudocode."""

        # Clear existing
        for lbl in self._lines:
            self._content_layout.removeWidget(lbl)
            lbl.deleteLater()

        self._lines.clear()

        # Remove the stretch at the end temporarily
        stretch_item = self._content_layout.takeAt(
            self._content_layout.count() - 1
        )

        mono = QFont("JetBrains Mono", 11)
        mono.setStyleHint(QFont.StyleHint.Monospace)

        for i, line in enumerate(lines):
            lbl = QLabel(f" {i + 1:>2}  {line}")
            lbl.setFont(mono)
            lbl.setStyleSheet(self._line_style(False))
            lbl.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction
            )

            self._content_layout.addWidget(lbl)
            self._lines.append(lbl)

        self._content_layout.addStretch()

    def highlight_line(self, line_num: int) -> None:
        """Highlight the given 0-based pseudocode line."""

        for i, lbl in enumerate(self._lines):
            lbl.setStyleSheet(
                self._line_style(i == line_num)
            )

        # Scroll to the highlighted line
        if 0 <= line_num < len(self._lines):
            self._scroll.ensureWidgetVisible(
                self._lines[line_num]
            )

    def clear_highlight(self) -> None:
        for lbl in self._lines:
            lbl.setStyleSheet(
                self._line_style(False)
            )

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _line_style(active: bool) -> str:
        if active:
            return f"""
                QLabel {{
                    background: {COLORS['surface']};
                    color: {COLORS['accent_cyan']};
                    border-left: 3px solid {COLORS['accent_cyan']};
                    border-radius: 4px;
                    padding: 5px 8px;
                    margin: 1px 0;
                }}
            """

        return f"""
            QLabel {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border-left: 3px solid transparent;
                padding: 5px 8px;
                margin: 1px 0;
            }}
        """