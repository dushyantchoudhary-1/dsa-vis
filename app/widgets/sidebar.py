"""
Sidebar widget — algorithm / data-structure selector.

A styled QTreeWidget with three top-level categories:
  ▸ Sorting
  ▸ Searching
  ▸ Data Structures

Emits ``algorithm_selected(key: str)`` when the user clicks a leaf item.
"""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
)

from app.theme import COLORS


# ── Sidebar icons (Unicode) ─────────────────────────────────────
_ICONS = {
    "sorting":          "📊",
    "searching":        "🔍",
    "data_structure":   "🧩",
    "bubble_sort":      "🫧",
    "selection_sort":   "☝️",
    "insertion_sort":   "📥",
    "merge_sort":       "🔀",
    "quick_sort":       "⚡",
    "linear_search":    "➡️",
    "binary_search":    "✂️",
    "stack":            "📚",
    "queue":            "🚶",
    "linked_list":      "🔗",
    "bst":              "🌳",
}

_CATEGORIES = [
    ("sorting", "Sorting Algorithms", [
        "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort",
    ]),
    ("searching", "Searching Algorithms", [
        "linear_search", "binary_search",
    ]),
    ("data_structure", "Data Structures", [
        "stack", "queue", "linked_list", "bst",
    ]),
]

_DISPLAY_NAMES = {
    "bubble_sort":    "Bubble Sort",
    "selection_sort": "Selection Sort",
    "insertion_sort": "Insertion Sort",
    "merge_sort":     "Merge Sort",
    "quick_sort":     "Quick Sort",
    "linear_search":  "Linear Search",
    "binary_search":  "Binary Search",
    "stack":          "Stack",
    "queue":          "Queue",
    "linked_list":    "Linked List",
    "bst":            "Binary Search Tree",
}


class Sidebar(QWidget):
    """Left-hand algorithm / data-structure selector."""

    algorithm_selected = Signal(str)   # emits the algorithm key

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setObjectName("sidebar")
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("🔬  DSA Visualizer")
        title.setFont(QFont("Helvetica Neue", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            padding: 8px 4px 16px 4px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Select an algorithm or data structure")
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 0 4px 8px 4px; font-size: 11px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                font-size: 13px;
            }}
            QTreeWidget::item {{
                padding: 7px 8px;
                border-radius: 6px;
                margin: 1px 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {COLORS['surface']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['surface']};
                color: {COLORS['accent_cyan']};
            }}
        """)

        for cat_key, cat_label, items in _CATEGORIES:
            cat_item = QTreeWidgetItem([f"{_ICONS.get(cat_key, '')}  {cat_label}"])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = cat_item.font(0)
            font.setBold(True)
            font.setPointSize(12)
            cat_item.setFont(0, font)
            cat_item.setForeground(0, QColor(COLORS["text_secondary"]))

            for key in items:
                child = QTreeWidgetItem([f"  {_ICONS.get(key, '')}  {_DISPLAY_NAMES.get(key, key)}"])
                child.setData(0, Qt.ItemDataRole.UserRole, key)
                self.tree.setItemWidget(child, 0, None)
                cat_item.addChild(child)

            self.tree.addTopLevelItem(cat_item)

        self.tree.expandAll()
        self.tree.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.tree, 1)

        # Version label at bottom
        ver = QLabel("v1.0 — AI coming soon ✨")
        ver.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; padding: 8px 4px 0 4px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

    # ── Slots ────────────────────────────────────────────────────
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if key:
            self.algorithm_selected.emit(key)
