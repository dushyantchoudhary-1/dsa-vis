"""
Modern Algorithm Explorer — Searchable, Categorized Algorithm & Data Structure Explorer.
Refined for DSA Lab's warm-light paper & editorial design language.

Features:
- Instant live search filtering across all algorithms
- 4 Categorized Sections with distinct semantic color badges:
    • Sorting: Terracotta & Coral (#D96C4F)
    • Searching: Marigold & Amber (#D49A24)
    • Graphs: Botanical Green (#39836B)
    • Data Structures & Trees: Muted Teal (#398F91) & Violet (#8970B5)
- Selected state with category-tinted background and thin colored indicator
- Collapsible drawer mode (wide 270px vs icon/compact strip)
- Clean, non-truncated category labels and smooth scrolling
"""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QFrame,
    QStyle,
    QStyleOption,
)

from app.theme import COLORS, CATEGORY_CONFIGS, get_category_config, get_category_for_key


# ── Metadata ─────────────────────────────────────────────────────

_ICONS = {
    "sorting":          "📊",
    "searching":        "🔍",
    "graph":            "🌐",
    "data_structure":   "🧩",

    "bubble_sort":      "🫧",
    "selection_sort":   "☝️",
    "insertion_sort":   "📥",
    "merge_sort":       "🔀",
    "quick_sort":       "⚡",
    "heap_sort":        "🏔️",

    "linear_search":    "➡️",
    "binary_search":    "✂️",

    "bfs_search":       "🌊",
    "dfs_search":       "🧗",
    "dijkstra_search":  "🧭",
    "astar_search":     "⭐",

    "stack":            "📚",
    "queue":            "🚶",
    "linked_list":      "🔗",
    "bst":              "🌳",
}

_CATEGORIES = [
    ("sorting", "Sorting", [
        ("bubble_sort", "Bubble Sort", "O(n²)"),
        ("selection_sort", "Selection Sort", "O(n²)"),
        ("insertion_sort", "Insertion Sort", "O(n²)"),
        ("merge_sort", "Merge Sort", "O(n log n)"),
        ("quick_sort", "Quick Sort", "O(n log n)"),
        ("heap_sort", "Heap Sort", "O(n log n)"),
    ]),
    ("searching", "Searching", [
        ("linear_search", "Linear Search", "O(n)"),
        ("binary_search", "Binary Search", "O(log n)"),
    ]),
    ("graph", "Graphs & Trees", [
        ("bfs_search", "Breadth-First (BFS)", "O(V+E)"),
        ("dfs_search", "Depth-First (DFS)", "O(V+E)"),
        ("dijkstra_search", "Dijkstra's Path", "O(E log V)"),
        ("astar_search", "A* Heuristic Search", "O(E)"),
    ]),
    ("data_structure", "Data Structures", [
        ("stack", "Stack (LIFO)", "O(1)"),
        ("queue", "Queue (FIFO)", "O(1)"),
        ("linked_list", "Linked List", "O(n)"),
        ("bst", "Binary Search Tree", "O(log n)"),
    ]),
]


class Sidebar(QWidget):
    """Warm-light collapsible Algorithm Explorer."""

    algorithm_selected = Signal(str)      # emits algorithm key
    racing_arena_requested = Signal()     # emits when user clicks Racing Arena
    collapse_toggled = Signal(bool)       # emits when sidebar collapsed state changes

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(270)
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self._is_collapsed = False
        self._items_by_key: dict[str, QTreeWidgetItem] = {}
        self._current_selected_key: str = ""
        self._build_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {COLORS['bg_primary']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(10)

        # ── 1. Header with Title & Collapse Toggle ──────────────
        header = QHBoxLayout()
        header.setSpacing(6)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)

        app_title = QLabel("⚡ DSA LAB")
        app_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {COLORS['text_primary']}; letter-spacing: 0.5px;")
        title_box.addWidget(app_title)

        sub = QLabel("Algorithm Explorer")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {COLORS['text_muted']};")
        title_box.addWidget(sub)
        header.addLayout(title_box)

        header.addStretch()

        self._collapse_btn = QPushButton("◀")
        self._collapse_btn.setFixedSize(26, 26)
        self._collapse_btn.setToolTip("Collapse / Expand Explorer")
        self._collapse_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: {COLORS['text_secondary']};
                font-size: 11px;
                padding: 0;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_tertiary']};
                border-color: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
        """)
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        header.addWidget(self._collapse_btn)
        layout.addLayout(header)

        # ── 2. Live Search Field ─────────────────────────────────
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search algorithms...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFFFF;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }}
            QLineEdit:hover {{
                border-color: {COLORS['text_muted']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_green']};
                background-color: #FFFFFF;
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # ── 3. Tree Widget ───────────────────────────────────────
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
                font-size: 12px;
                color: {COLORS['text_primary']};
            }}
            QTreeWidget::item {{
                padding: 5px 6px;
                border-radius: 6px;
                margin: 1px 0px;
            }}
            QTreeWidget::item:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                font-weight: 600;
            }}
        """)

        for cat_key, cat_label, items in _CATEGORIES:
            cat_cfg = CATEGORY_CONFIGS.get(cat_key, CATEGORY_CONFIGS["sorting"])
            cat_icon = cat_cfg["icon"]
            cat_item = QTreeWidgetItem([f"{cat_icon}  {cat_label}  ({len(items)})"])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            cat_item.setForeground(0, QColor(COLORS["text_secondary"]))
            cat_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            cat_item.setFont(0, cat_font)

            for key, name, complexity in items:
                child = QTreeWidgetItem([f"{_ICONS.get(key, '•')}  {name}"])
                child.setData(0, Qt.ItemDataRole.UserRole, key)
                child.setToolTip(0, f"{name} • Time: {complexity}")
                child.setForeground(0, QColor(COLORS["text_primary"]))
                child_font = QFont("Segoe UI", 10)
                child.setFont(0, child_font)
                cat_item.addChild(child)
                self._items_by_key[key] = child

            self.tree.addTopLevelItem(cat_item)

        self.tree.expandAll()
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree, 1)

        # ── 4. Bottom Arena Launch Banner ─────────────────────────
        arena_btn = QPushButton("🏁  Racing Arena")
        arena_btn.setToolTip("Launch multi-algorithm real-time showdown")
        arena_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FFFFFF;
                border: 1px solid {CATEGORY_CONFIGS['racing']['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {CATEGORY_CONFIGS['racing']['accent']};
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {CATEGORY_CONFIGS['racing']['light']};
                border-color: {CATEGORY_CONFIGS['racing']['accent']};
                color: {CATEGORY_CONFIGS['racing']['accent']};
            }}
        """)
        arena_btn.clicked.connect(self.racing_arena_requested.emit)
        layout.addWidget(arena_btn)

    # ── Search & Filter ──────────────────────────────────────────
    def _on_search_changed(self, text: str) -> None:
        query = text.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            cat_visible = False
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                key = child.data(0, Qt.ItemDataRole.UserRole)
                child_text = child.text(0).lower()
                matches = not query or (query in child_text or query in key)
                child.setHidden(not matches)
                if matches:
                    cat_visible = True
            cat_item.setHidden(not cat_visible)
            if query and cat_visible:
                cat_item.setExpanded(True)

    # ── Selection & Toggle ───────────────────────────────────────
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if key:
            self.algorithm_selected.emit(key)

    def select_algorithm(self, key: str) -> None:
        """Programmatically select an algorithm and apply category-tinted highlight."""
        self._current_selected_key = key
        item = self._items_by_key.get(key)
        if item:
            self.tree.setCurrentItem(item)
            cat_cfg = get_category_config(key)
            # Apply category-tinted selection style
            self.tree.setStyleSheet(f"""
                QTreeWidget {{
                    background-color: transparent;
                    border: none;
                    font-size: 12px;
                    color: {COLORS['text_primary']};
                }}
                QTreeWidget::item {{
                    padding: 5px 6px;
                    border-radius: 6px;
                    margin: 1px 0px;
                }}
                QTreeWidget::item:hover {{
                    background-color: {COLORS['bg_tertiary']};
                }}
                QTreeWidget::item:selected {{
                    background-color: {cat_cfg['light']};
                    color: {cat_cfg['accent']};
                    font-weight: 600;
                    border-left: 3px solid {cat_cfg['accent']};
                }}
            """)

    def _toggle_collapse(self) -> None:
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.setFixedWidth(56)
            self._collapse_btn.setText("▶")
            self.search_input.hide()
            self.tree.hide()
        else:
            self.setFixedWidth(270)
            self._collapse_btn.setText("◀")
            self.search_input.show()
            self.tree.show()
        self.collapse_toggled.emit(self._is_collapsed)
