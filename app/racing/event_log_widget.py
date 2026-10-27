"""
Real-time Event Feed Widget for Algorithm Racing Arena.

Displays chronological execution events, comparisons, swaps, partitions,
and finish line notifications with leader highlighting.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextBrowser,
    QPushButton,
)

from app.theme import COLORS
from app.racing.race_models import RaceEvent


class RaceEventLogWidget(QFrame):
    """Chronological scrolling event feed with leader highlighting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(150)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            RaceEventLogWidget {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header
        head = QHBoxLayout()
        title = QLabel("📜  RACE EVENT FEED")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #D95F42;")
        head.addWidget(title)

        head.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 1px 8px;
                font-size: 10px;
                color: {COLORS['text_muted']};
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
                background: {COLORS['surface_hover']};
            }}
        """)
        clear_btn.clicked.connect(self.clear_log)
        head.addWidget(clear_btn)

        layout.addLayout(head)

        # Browser
        self._browser = QTextBrowser()
        self._browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px;
                color: {COLORS['text_secondary']};
                font-family: Consolas, monospace;
                font-size: 11px;
            }}
        """)
        layout.addWidget(self._browser, 1)

    def log_event(self, event: RaceEvent) -> None:
        """Append an event to the chronological feed."""
        bg = "#292518" if event.is_leader else "transparent"
        border = f"border-left: 3px solid {event.algo_color};" if event.algo_color != "#7f8790" else ""
        
        html = (
            f'<div style="margin: 2px 0; padding: 2px 6px; background-color: {bg}; {border} border-radius: 4px;">'
            f'<span style="color: {COLORS["text_muted"]};">{event.timestamp_str}</span> '
            f'<b style="color: {event.algo_color};">{event.algo_name}:</b> '
            f'<span style="color: {COLORS["text_primary"]};">{event.description}</span>'
            f'</div>'
        )
        self._browser.append(html)
        self._browser.moveCursor(QTextCursor.MoveOperation.End)

    def clear_log(self) -> None:
        self._browser.clear()
