"""
API Key Settings Dialog for Gemini AI Tutor.

Provides a secure, elegant modal interface to view, enter, test,
and persist the Google Gemini API key.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QWidget,
)

from app.theme import COLORS
from app.engine.gemini_tutor import GeminiTutor


class ApiKeyDialog(QDialog):
    """Modal dialog for configuring and testing the Gemini API key."""

    def __init__(self, tutor: GeminiTutor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tutor = tutor
        self.setWindowTitle("🔑 Gemini AI Tutor — API Settings")
        self.setFixedWidth(460)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Header ──────────────────────────────────────────────────
        title = QLabel("Gemini AI Tutor Configuration")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #292B26;")
        layout.addWidget(title)

        desc = QLabel(
            "Enter your Google Gemini API Key below to unlock dynamic, "
            "deep pedagogical AI explanations, live algorithm Q&A, and interactive quizzes."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc)

        # ── Key Input Row ───────────────────────────────────────────
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 4, 0, 0)
        input_layout.setSpacing(6)

        lbl = QLabel("Gemini API Key:")
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 12px;")
        input_layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(8)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("AIzaSy...")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setText(self._tutor.get_api_key())
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['code_text']};
                font-family: Consolas, monospace;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: #34785B;
            }}
        """)
        row.addWidget(self._key_input, 1)

        self._toggle_vis_btn = QPushButton("👁️")
        self._toggle_vis_btn.setFixedSize(36, 36)
        self._toggle_vis_btn.setToolTip("Show / Hide API Key")
        self._toggle_vis_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._toggle_vis_btn.clicked.connect(self._toggle_visibility)
        row.addWidget(self._toggle_vis_btn)

        input_layout.addLayout(row)
        layout.addWidget(input_container)

        # ── Status & Link ───────────────────────────────────────────
        self._status_lbl = QLabel("")
        self._status_lbl.setWordWrap(True)
        self._status_lbl.setStyleSheet("font-size: 12px; padding: 4px 0;")
        layout.addWidget(self._status_lbl)

        link_btn = QPushButton("Get a Free Gemini API Key (Google AI Studio) ↗")
        link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        link_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #34785B;
                text-align: left;
                font-size: 12px;
                text-decoration: underline;
                padding: 0;
            }
            QPushButton:hover {
                color: #23523D;
            }
        """)
        link_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aistudio.google.com/app/apikey")))
        layout.addWidget(link_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(sep)

        # ── Action Buttons ──────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        # Test Connection button
        self._test_btn = QPushButton("⚡ Test Key")
        self._test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 14px;
                color: {COLORS['text_primary']};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['accent_cyan']};
            }}
        """)
        self._test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(self._test_btn)

        # Clear button
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['error']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._clear_btn.clicked.connect(self._clear_key)
        btn_row.addWidget(self._clear_btn)

        btn_row.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                color: {COLORS['text_secondary']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        # Save & Connect button
        self._save_btn = QPushButton("Save & Connect")
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_primary']};
                border: 1px solid {COLORS['accent_cyan']};
                border-radius: 8px;
                padding: 8px 18px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        self._save_btn.clicked.connect(self._save_and_connect)
        btn_row.addWidget(self._save_btn)

        layout.addLayout(btn_row)

    # ── Slots ─────────────────────────────────────────────────────────
    def _toggle_visibility(self) -> None:
        if self._key_input.echoMode() == QLineEdit.EchoMode.Password:
            self._key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_vis_btn.setText("🔒")
        else:
            self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_vis_btn.setText("👁️")

    def _test_connection(self) -> None:
        key = self._key_input.text().strip()
        if not key:
            self._status_lbl.setText("⚠️ Please enter an API key to test.")
            self._status_lbl.setStyleSheet(f"color: {COLORS['warning']}; font-size: 12px;")
            return

        self._status_lbl.setText("⏳ Testing connection with Google Gemini...")
        self._status_lbl.setStyleSheet(f"color: {COLORS['accent_cyan']}; font-size: 12px;")
        self.repaint()

        success, msg = self._tutor.test_key_connection(key)
        if success:
            self._status_lbl.setText(f"✓ {msg}")
            self._status_lbl.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px; font-weight: bold;")
        else:
            self._status_lbl.setText(f"✕ {msg}")
            self._status_lbl.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")

    def _clear_key(self) -> None:
        self._key_input.clear()
        self._tutor.clear_api_key()
        self._status_lbl.setText("Key cleared. Operating in Offline Tutor Mode.")
        self._status_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")

    def _save_and_connect(self) -> None:
        key = self._key_input.text().strip()
        if key:
            self._tutor.set_api_key(key, persist=True)
        else:
            self._tutor.clear_api_key()
        self.accept()
