"""
Input panel — data entry for algorithms and operation buttons for data structures.

Two modes (swapped via QStackedWidget):
  1. **Algorithm mode** — text field for custom data, Generate Random button, size spin-box.
  2. **Data-structure mode** — value input + operation buttons (push, pop, etc.).
"""

from __future__ import annotations

from random import randint, sample

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QFrame,
)

from app.theme import COLORS


class InputPanel(QWidget):
    """Bottom input area — algorithm data or data-structure operations."""

    # Signals
    run_requested = Signal(list)          # list[int] data for sorting
    run_search_requested = Signal(list, int)  # data, target
    ds_operation = Signal(str, int)       # operation name, value

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(58)
        self._mode = "sorting"            # "sorting" | "searching" | "data_structure"
        self._ds_operations: list[str] = []
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 4, 16, 4)
        main_layout.setSpacing(8)

        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack, 1)

        # ── Page 0: algorithm input (sorting / searching) ────────
        algo_page = QWidget()
        algo_lay = QHBoxLayout(algo_page)
        algo_lay.setContentsMargins(0, 0, 0, 0)
        algo_lay.setSpacing(8)

        lbl = QLabel("Data:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        algo_lay.addWidget(lbl)

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("e.g. 5, 3, 8, 1, 9, 2, 7")
        self.data_input.setMinimumWidth(200)
        algo_lay.addWidget(self.data_input, 1)

        # Target (for searching)
        self.target_label = QLabel("Target:")
        self.target_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        self.target_label.hide()
        algo_lay.addWidget(self.target_label)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("value")
        self.target_input.setFixedWidth(70)
        self.target_input.setValidator(QIntValidator())
        self.target_input.hide()
        algo_lay.addWidget(self.target_input)

        # Size
        size_lbl = QLabel("Size:")
        size_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        algo_lay.addWidget(size_lbl)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 50)
        self.size_spin.setValue(15)
        self.size_spin.setFixedWidth(60)
        algo_lay.addWidget(self.size_spin)

        self.btn_random = QPushButton("🎲  Random")
        self.btn_random.setToolTip("Generate random data")
        self.btn_random.clicked.connect(self._generate_random)
        algo_lay.addWidget(self.btn_random)

        self.btn_run = QPushButton("▶  Run")
        self.btn_run.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']};
                color: #ffffff;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{ background: #34d399; }}
        """)
        self.btn_run.clicked.connect(self._on_run)
        algo_lay.addWidget(self.btn_run)

        self._stack.addWidget(algo_page)

        # ── Page 1: data-structure operations ────────────────────
        ds_page = QWidget()
        self._ds_layout = QHBoxLayout(ds_page)
        self._ds_layout.setContentsMargins(0, 0, 0, 0)
        self._ds_layout.setSpacing(8)

        val_lbl = QLabel("Value:")
        val_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        self._ds_layout.addWidget(val_lbl)

        self.ds_value_input = QLineEdit()
        self.ds_value_input.setPlaceholderText("integer")
        self.ds_value_input.setFixedWidth(80)
        self.ds_value_input.setValidator(QIntValidator())
        self._ds_layout.addWidget(self.ds_value_input)

        self._ds_btn_container = QWidget()
        self._ds_btn_layout = QHBoxLayout(self._ds_btn_container)
        self._ds_btn_layout.setContentsMargins(0, 0, 0, 0)
        self._ds_btn_layout.setSpacing(6)
        self._ds_layout.addWidget(self._ds_btn_container, 1)

        self._ds_layout.addStretch()

        self._stack.addWidget(ds_page)

    # ── Mode switching ───────────────────────────────────────────

    def set_mode(self, mode: str, operations: list[str] | None = None) -> None:
        """Switch between 'sorting', 'searching', 'data_structure'."""
        self._mode = mode
        if mode in ("sorting", "searching"):
            self._stack.setCurrentIndex(0)
            show_target = mode == "searching"
            self.target_label.setVisible(show_target)
            self.target_input.setVisible(show_target)
        else:
            self._stack.setCurrentIndex(1)
            self._setup_ds_buttons(operations or [])

    def _setup_ds_buttons(self, operations: list[str]) -> None:
        """Create operation buttons for the selected data structure."""
        # Clear old buttons
        while self._ds_btn_layout.count():
            item = self._ds_btn_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        _OP_LABELS = {
            "push": "📥 Push",
            "pop": "📤 Pop",
            "peek": "👁 Peek",
            "enqueue": "📥 Enqueue",
            "dequeue": "📤 Dequeue",
            "front": "👁 Front",
            "insert_head": "⬆ Insert Head",
            "insert_tail": "⬇ Insert Tail",
            "delete": "🗑 Delete",
            "search": "🔍 Search",
            "insert": "➕ Insert",
            "inorder": "↔ Inorder",
            "preorder": "⬅ Preorder",
            "postorder": "➡ Postorder",
            "clear": "🗑 Clear",
        }

        for op in operations:
            btn = QPushButton(_OP_LABELS.get(op, op))
            btn.setToolTip(op)

            if op == "clear":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['bg_tertiary']};
                        border: 1px solid {COLORS['border']};
                        color: {COLORS['error']};
                        border-radius: 8px;
                        padding: 6px 14px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{ background: {COLORS['surface']}; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['surface']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 6px 14px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background: {COLORS['surface_hover']};
                        border-color: {COLORS['accent_cyan']};
                    }}
                """)

            btn.clicked.connect(lambda checked, o=op: self._on_ds_op(o))
            self._ds_btn_layout.addWidget(btn)

    # ── Slots ────────────────────────────────────────────────────

    def _generate_random(self) -> None:
        n = self.size_spin.value()
        data = [randint(1, 99) for _ in range(n)]
        self.data_input.setText(", ".join(str(x) for x in data))

    def _on_run(self) -> None:
        text = self.data_input.text().strip()
        if not text:
            self._generate_random()
            text = self.data_input.text().strip()

        try:
            data = [int(x.strip()) for x in text.split(",") if x.strip()]
        except ValueError:
            return

        if self._mode == "searching":
            target_text = self.target_input.text().strip()
            target = int(target_text) if target_text else data[len(data) // 2]
            self.run_search_requested.emit(data, target)
        else:
            self.run_requested.emit(data)

    def _on_ds_op(self, operation: str) -> None:
        text = self.ds_value_input.text().strip()
        value = int(text) if text else 0
        self.ds_operation.emit(operation, value)
