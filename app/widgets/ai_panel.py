"""
AI Panel — Interactive AI Tutor Chatbot for DSA Visualizer.

Provides concise, student-friendly pedagogical tutoring with
real-time algorithm state awareness and accessible typography.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont, QTextCursor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QCheckBox,
    QFrame,
    QStackedWidget,
    QStyle,
    QStyleOption,
)

from app.theme import COLORS
from app.engine.algorithm_engine import AlgorithmInfo, Step
from app.engine.gemini_tutor import GeminiTutor, md_to_html
from app.widgets.api_key_dialog import ApiKeyDialog


class AIPanel(QWidget):
    """
    AI Tutor Chatbot Panel.

    Mounted beside the visualization canvas, offering clean, readable,
    and student-friendly assistance with accessible typography.
    """

    close_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(360)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        self._tutor = GeminiTutor(self)
        self._last_step_index: int = -1
        self._auto_step_enabled: bool = False
        self._is_thinking: bool = False
        self._has_messages: bool = False
        self._banner_dismissed: bool = False
        self._current_algo_name: str = "Bubble Sort"
        self._current_complexity: str = "O(n²)"

        self._build_ui()
        self._connect_signals()
        self._sync_setup_notice()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    # ── UI Construction ───────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_primary']};
                border-left: 1px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── 1. Header Bar: Title, Status, Action Buttons ─────────────
        header_bar = QHBoxLayout()
        header_bar.setContentsMargins(0, 0, 0, 0)
        header_bar.setSpacing(6)

        title = QLabel("AI Tutor")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #292B26; background: transparent;")
        header_bar.addWidget(title)

        # Compact algorithm status label: e.g. "Bubble Sort · O(n²)"
        self._algo_status_lbl = QLabel(f"{self._current_algo_name} · {self._current_complexity}")
        self._algo_status_lbl.setFont(QFont("Segoe UI", 10))
        self._algo_status_lbl.setStyleSheet(f"""
            QLabel {{
                color: #62665F;
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 11px;
            }}
        """)
        header_bar.addWidget(self._algo_status_lbl)

        header_bar.addStretch()

        # Settings Button (Gemini API Key dialog)
        self._key_btn = QPushButton("⚙")
        self._key_btn.setToolTip("Configure Gemini API Key")
        self._key_btn.setFixedSize(28, 28)
        self._key_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: #62665F;
                font-family: 'Segoe UI Symbol', 'Segoe UI Emoji', sans-serif;
                font-size: 14px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #F8F7F2;
                border-color: #34785B;
                color: #34785B;
            }}
        """)
        header_bar.addWidget(self._key_btn)

        # Clear Chat Button
        self._clear_btn = QPushButton("🗑")
        self._clear_btn.setToolTip("Clear conversation history")
        self._clear_btn.setFixedSize(28, 28)
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: #62665F;
                font-family: 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif;
                font-size: 13px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #F8F7F2;
                border-color: {COLORS['error']};
                color: {COLORS['error']};
            }}
        """)
        header_bar.addWidget(self._clear_btn)

        # Close Panel Button
        self._close_btn = QPushButton("×")
        self._close_btn.setToolTip("Close AI Tutor panel")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: #62665F;
                font-family: 'Segoe UI', sans-serif;
                font-size: 16px;
                font-weight: 400;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #F8F7F2;
                color: #252822;
                border-color: #252822;
            }}
        """)
        self._close_btn.clicked.connect(self._on_close_clicked)
        header_bar.addWidget(self._close_btn)

        layout.addLayout(header_bar)

        # ── 2. Contextual Setup Notice (Only if API key is missing) ──
        self._setup_banner = QFrame()
        self._setup_banner.setObjectName("setupBanner")
        self._setup_banner.setStyleSheet(f"""
            QFrame#setupBanner {{
                background-color: #F8F7F2;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QFrame#setupBanner QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        setup_lay = QHBoxLayout(self._setup_banner)
        setup_lay.setContentsMargins(8, 6, 8, 6)
        setup_lay.setSpacing(6)

        setup_text = QLabel("<b>Setup required:</b> Add your Gemini API key to enable AI answers.")
        setup_text.setStyleSheet("color: #62665F; font-size: 11px; background: transparent;")
        setup_text.setWordWrap(True)
        setup_lay.addWidget(setup_text, 1)

        setup_btn = QPushButton("Configure")
        setup_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #34785B;
                font-size: 11px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                color: #23523D;
                text-decoration: underline;
            }
        """)
        setup_btn.clicked.connect(self._open_key_dialog)
        setup_lay.addWidget(setup_btn)

        dismiss_btn = QPushButton("×")
        dismiss_btn.setFixedSize(16, 16)
        dismiss_btn.setToolTip("Dismiss notice")
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8F9489;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #252822;
            }
        """)
        dismiss_btn.clicked.connect(self._dismiss_setup_banner)
        setup_lay.addWidget(dismiss_btn)

        layout.addWidget(self._setup_banner)

        # ── 3. Central Stack: Empty State vs Chat History ────────────
        self._content_stack = QStackedWidget()

        # Page 0: Compact Empty State
        self._empty_state = QWidget()
        empty_layout = QVBoxLayout(self._empty_state)
        empty_layout.setContentsMargins(8, 16, 8, 8)
        empty_layout.setSpacing(8)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        intro_title = QLabel("AI Tutor")
        intro_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        intro_title.setStyleSheet("color: #292B26; background: transparent;")
        empty_layout.addWidget(intro_title)

        intro_desc = QLabel("Ask about the current algorithm or select a step to understand it.")
        intro_desc.setFont(QFont("Segoe UI", 11))
        intro_desc.setWordWrap(True)
        intro_desc.setStyleSheet("color: #62665F; background: transparent; font-style: italic;")
        empty_layout.addWidget(intro_desc)

        empty_layout.addSpacing(10)

        prompts_lbl = QLabel("Suggested prompts")
        prompts_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        prompts_lbl.setStyleSheet("color: #62665F; background: transparent; text-transform: uppercase;")
        empty_layout.addWidget(prompts_lbl)

        # 3 suggested prompt chips
        self._chip_step = QPushButton("Explain this step")
        self._chip_complexity = QPushButton(f"Why is this {self._current_complexity}?")
        self._chip_compare = QPushButton("Compare algorithms")

        chip_style = f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 7px 11px;
                color: #252822;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QPushButton:hover {{
                background-color: #F8F7F2;
                border-color: #34785B;
                color: #34785B;
            }}
            QPushButton:pressed {{
                background-color: #F0EEE7;
            }}
        """

        for chip in (self._chip_step, self._chip_complexity, self._chip_compare):
            chip.setStyleSheet(chip_style)
            empty_layout.addWidget(chip)

        self._chip_step.clicked.connect(lambda: self._on_quick_prompt("Explain what is happening in the current step right now."))
        self._chip_complexity.clicked.connect(self._on_complexity_chip_clicked)
        self._chip_compare.clicked.connect(lambda: self._on_quick_prompt("Compare this algorithm with common alternatives."))

        empty_layout.addStretch()
        self._content_stack.addWidget(self._empty_state)

        # Page 1: Chat History Browser
        self._chat = QTextBrowser()
        self._chat.setOpenExternalLinks(True)
        self._chat.setStyleSheet(f"""
            QTextBrowser {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                color: #252822;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Roboto', sans-serif;
                font-size: 12px;
            }}
        """)
        self._content_stack.addWidget(self._chat)

        self._content_stack.setCurrentIndex(0)
        layout.addWidget(self._content_stack, 1)

        # ── 4. Live Step Insights Checkbox ───────────────────────────
        step_opt_row = QHBoxLayout()
        step_opt_row.setContentsMargins(2, 0, 2, 0)
        self._auto_step_cb = QCheckBox("Live step insights")
        self._auto_step_cb.setToolTip("Automatically explain each step when stepping through the algorithm")
        self._auto_step_cb.setStyleSheet(f"""
            QCheckBox {{
                color: #62665F;
                font-size: 11px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                background: #FFFFFF;
            }}
            QCheckBox::indicator:hover {{
                border-color: #34785B;
            }}
            QCheckBox::indicator:checked {{
                background-color: #34785B;
                border-color: #34785B;
            }}
        """)
        self._auto_step_cb.toggled.connect(self._on_auto_step_toggled)
        step_opt_row.addWidget(self._auto_step_cb)
        step_opt_row.addStretch()
        layout.addLayout(step_opt_row)

        # ── 5. Thinking Status Indicator ─────────────────────────────
        self._thinking_lbl = QLabel("Formulating explanation...")
        self._thinking_lbl.setStyleSheet("color: #62665F; font-size: 11px; font-style: italic; padding: 2px 4px;")
        self._thinking_lbl.hide()
        layout.addWidget(self._thinking_lbl)

        # ── 6. Input Row ─────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask a question... (Press Enter)")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 7px 10px;
                color: #252822;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: #34785B;
            }}
        """)
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input, 1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #34785B;
                border: 1px solid #34785B;
                border-radius: 6px;
                padding: 7px 14px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QPushButton:hover {{
                background-color: #2B644B;
                border-color: #2B644B;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_tertiary']};
                border-color: {COLORS['border']};
                color: #8F9489;
            }}
        """)
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        layout.addLayout(input_row)

    # ── Signal Connections ────────────────────────────────────
    def _connect_signals(self) -> None:
        self._key_btn.clicked.connect(self._open_key_dialog)
        self._clear_btn.clicked.connect(self._clear_chat)

        self._tutor.response_ready.connect(self._on_tutor_response)
        self._tutor.error_occurred.connect(self._on_tutor_error)
        self._tutor.status_changed.connect(self._on_status_changed)
        self._tutor.step_insight_ready.connect(self._on_step_insight)

    def _sync_setup_notice(self) -> None:
        """Show setup instructions only when the API key is actually missing."""
        if self._banner_dismissed or self._tutor.is_online():
            self._setup_banner.hide()
        else:
            self._setup_banner.show()

    def _dismiss_setup_banner(self) -> None:
        self._banner_dismissed = True
        self._setup_banner.hide()

    def _on_close_clicked(self) -> None:
        self.hide()
        self.close_requested.emit()

    def _ensure_chat_visible(self) -> None:
        """Transition from empty state to chat display on first message."""
        if not self._has_messages:
            self._has_messages = True
            self._content_stack.setCurrentIndex(1)

    # ── Messages & Formatting ─────────────────────────────────────────
    def _append_message(self, sender: str, markdown_text: str) -> None:
        """Append a stylized chat message bubble to the chat browser with accessible typography."""
        self._ensure_chat_visible()
        formatted_html = md_to_html(markdown_text)

        if sender == "user":
            bubble_html = (
                f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin: 6px 0;">'
                f'<tr><td align="right">'
                f'<table border="0" cellpadding="0" cellspacing="0" style="background-color: {COLORS["bg_tertiary"]}; border: 1px solid {COLORS["border"]}; border-radius: 6px;">'
                f'<tr><td style="padding: 6px 10px; color: #252822; font-size: 12px; font-family: \'Segoe UI\', sans-serif; line-height: 1.4;">'
                f'<div style="font-size: 10px; font-weight: bold; color: #62665F; margin-bottom: 2px;">You</div>'
                f'<div>{formatted_html}</div>'
                f'</td></tr></table>'
                f'</td></tr></table>'
            )
        elif sender == "system":
            bubble_html = (
                f'<div style="margin: 5px 0; text-align: center; font-family: \'Segoe UI\', sans-serif;">'
                f'<span style="background-color: {COLORS["bg_tertiary"]}; color: #62665F; '
                f'padding: 3px 9px; border-radius: 4px; font-size: 11px; border: 1px solid {COLORS["border"]};">'
                f'{formatted_html}</span></div>'
            )
        else:  # assistant
            bubble_html = (
                f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin: 6px 0;">'
                f'<tr><td align="left">'
                f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #FFFFFF; border: 1px solid {COLORS["border"]}; border-left: 3px solid #34785B; border-radius: 6px;">'
                f'<tr><td style="padding: 8px 12px; color: #252822; font-size: 12px; font-family: \'Segoe UI\', sans-serif; line-height: 1.5;">'
                f'<div style="color: #34785B; font-weight: bold; font-size: 10px; margin-bottom: 4px;">AI Tutor</div>'
                f'<div>{formatted_html}</div>'
                f'</td></tr></table>'
                f'</td></tr></table>'
            )

        self._chat.append(bubble_html)
        self._chat.moveCursor(QTextCursor.MoveOperation.End)

    # ── User Interaction Handlers ─────────────────────────────────────
    @Slot()
    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text or self._is_thinking:
            return

        self._input.clear()
        self._append_message("user", text)
        self._set_thinking(True)
        self._tutor.ask(text)

    def _on_quick_prompt(self, prompt: str) -> None:
        if self._is_thinking:
            return
        self._append_message("user", prompt)
        self._set_thinking(True)
        self._tutor.ask(prompt)

    def _on_complexity_chip_clicked(self) -> None:
        self._on_quick_prompt(f"Why is the time complexity of this algorithm {self._current_complexity}?")

    @Slot(str)
    def _on_tutor_response(self, response: str) -> None:
        self._set_thinking(False)
        self._append_message("assistant", response)

    @Slot(str)
    def _on_tutor_error(self, err_msg: str) -> None:
        self._set_thinking(False)
        self._append_message("assistant", f"Notice: {err_msg}")

    def _set_thinking(self, thinking: bool) -> None:
        self._is_thinking = thinking
        if thinking:
            self._thinking_lbl.setText("Formulating explanation...")
            self._thinking_lbl.show()
            self._send_btn.setEnabled(False)
        else:
            self._thinking_lbl.hide()
            self._send_btn.setEnabled(True)

    @Slot(str, bool)
    def _on_status_changed(self, msg: str, is_online: bool) -> None:
        self._sync_setup_notice()

    def _on_auto_step_toggled(self, checked: bool) -> None:
        self._auto_step_enabled = checked

    def _open_key_dialog(self) -> None:
        dialog = ApiKeyDialog(self._tutor, self)
        dialog.exec()
        self._banner_dismissed = False
        self._sync_setup_notice()

    def _clear_chat(self) -> None:
        self._chat.clear()
        self._has_messages = False
        self._content_stack.setCurrentIndex(0)
        self._tutor.clear_history()

    # ── Visualizer State Synchronization ──────────────────────────────
    def set_algorithm(self, info: AlgorithmInfo) -> None:
        """Update context with selected algorithm information."""
        self._tutor.update_context(
            algo_key=info.key,
            algo_name=info.name,
            category=info.category,
            subcategory=info.subcategory,
            description=info.description,
            time_complexity=info.time_complexity,
            space_complexity=info.space_complexity,
            pseudocode=info.pseudocode,
            question=getattr(info, "question", ""),
        )
        self._last_step_index = -1
        self._current_algo_name = info.name
        self._current_complexity = info.time_complexity or "O(n²)"

        # Update compact status label (Requirement 5)
        self._algo_status_lbl.setText(f"{info.name} · {self._current_complexity}")
        self._chip_complexity.setText(f"Why is this {self._current_complexity}?")

    def set_input_context(self, input_data=None, target=None, question: str = "") -> None:
        """Update context with user input, search target, and problem question."""
        self._tutor.update_context(
            current_input=input_data,
            target=target,
            question=question,
        )

    def set_step(self, step: Step, current_index: int, total_steps: int) -> None:
        """Sync live animation step with the AI Tutor."""
        self._tutor.update_context(
            step_index=current_index,
            total_steps=total_steps,
            current_data=step.data,
            highlights=step.highlights,
            active_pseudo_line=step.pseudocode_line,
            step_description=step.description,
            stats=step.stats,
        )

        if self._auto_step_enabled and current_index != self._last_step_index and total_steps > 0:
            self._last_step_index = current_index
            self._tutor.generate_step_insight()

    @Slot(str)
    def _on_step_insight(self, insight: str) -> None:
        self._ensure_chat_visible()
        self._append_message("assistant", insight)
