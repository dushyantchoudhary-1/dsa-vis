"""
AI panel — placeholder chat interface for future AI integration.

Defines the ``AIProvider`` abstract base class that future AI modules
will implement.  The panel itself shows a styled "Coming Soon" UI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFrame,
)

from app.theme import COLORS


# ═══════════════════════════════════════════════════════════════════
#  Abstract AI Provider (hook for future work)
# ═══════════════════════════════════════════════════════════════════

class AIProvider(ABC):
    """Interface that future AI modules must implement."""

    @abstractmethod
    def explain_step(self, step) -> str:
        """Given a ``Step`` object, return a natural-language explanation."""
        ...

    @abstractmethod
    def answer_question(self, question: str, context: dict) -> str:
        """Answer a free-form user question about the current algorithm."""
        ...


# ═══════════════════════════════════════════════════════════════════
#  Placeholder Panel Widget
# ═══════════════════════════════════════════════════════════════════

class AIPanel(QWidget):
    """Stub chat panel displayed when the user toggles the AI sidebar."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(300)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("🤖  AI Tutor")
        header.setFont(QFont("Helvetica Neue", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        layout.addWidget(header)

        # Coming-soon badge
        badge = QLabel("✨  Coming Soon")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Helvetica Neue", 13, QFont.Weight.Bold))
        badge.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['accent_purple']}, stop:1 {COLORS['accent_cyan']});
                color: #ffffff;
                border-radius: 20px;
                padding: 10px 20px;
            }}
        """)
        layout.addWidget(badge)

        # Description
        desc = QLabel(
            "The AI Tutor will:\n\n"
            "• Explain each algorithm step\n"
            "• Answer your questions\n"
            "• Walk through code line-by-line\n"
            "• Provide complexity analysis\n"
            "• Suggest learning paths\n\n"
            "Implement the AIProvider interface\n"
            "to plug in your own AI backend."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                background: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 16px;
                font-size: 12px;
                line-height: 1.5;
            }}
        """)
        layout.addWidget(desc)

        # Mock chat area
        self._chat = QTextEdit()
        self._chat.setReadOnly(True)
        self._chat.setPlaceholderText("AI responses will appear here…")
        self._chat.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 10px;
                color: {COLORS['text_muted']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(self._chat, 1)

        # Input row (disabled)
        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask the AI tutor…")
        self._input.setEnabled(False)
        input_row.addWidget(self._input, 1)

        self._send = QPushButton("Send")
        self._send.setEnabled(False)
        self._send.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_tertiary']};
                color: {COLORS['text_muted']};
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        input_row.addWidget(self._send)

        layout.addLayout(input_row)
