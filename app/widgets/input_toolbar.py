"""
Modern Dataset & Input Toolbar — Located directly above the visualization canvas.

Provides dedicated, structured controls for:
- Dataset generation with 5 distinct presets: Random, Nearly Sorted, Reversed, Duplicates, Sorted
- Array size adjustment with live data generation
- Search target selection with 'Present' and 'Absent' shortcuts
- Graph maze generation presets: Simple Maze, Spiral, Random Walls, Clear Grid
- Data structure value input and contextual action buttons (Push, Pop, Enqueue, Insert, etc.)
- Clear visual cue when data changes that resets current execution
"""

from __future__ import annotations

import random
from typing import Any

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
    QComboBox,
    QStackedWidget,
    QFrame,
)

from app.theme import COLORS
from app.algorithms.graph import (
    DEFAULT_GRID_ROWS,
    DEFAULT_GRID_COLS,
    DEFAULT_START,
    DEFAULT_GOAL,
    DEFAULT_WALLS,
    create_default_grid,
)


class InputToolbar(QWidget):
    """Contextual configuration toolbar positioned above the visualization."""

    # Signals
    run_requested = Signal(list)              # list[int] data for sorting
    run_search_requested = Signal(list, int)  # data, target
    ds_operation = Signal(str, int)           # operation name, value
    graph_config_requested = Signal(dict)     # grid dict with rows, cols, start, goal, walls

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(54)
        self._mode = "sorting"                # "sorting" | "searching" | "graph" | "data_structure"
        self._ds_operations: list[str] = []
        self._current_graph_walls: set = set(DEFAULT_WALLS)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1)

        # ── Page 0: Array / Sorting & Searching Input ────────────
        algo_page = QWidget()
        algo_lay = QHBoxLayout(algo_page)
        algo_lay.setContentsMargins(0, 0, 0, 0)
        algo_lay.setSpacing(8)

        # Preset Dropdown
        p_lbl = QLabel("Dataset:")
        p_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600; font-size: 11px;")
        algo_lay.addWidget(p_lbl)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "🎲 Random",
            "📈 Nearly Sorted",
            "📉 Reversed",
            "👥 Few Unique",
            "✨ Sorted",
        ])
        self.preset_combo.setFixedWidth(135)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        algo_lay.addWidget(self.preset_combo)

        # Size SpinBox
        s_lbl = QLabel("Size:")
        s_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600; font-size: 11px;")
        algo_lay.addWidget(s_lbl)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(5, 50)
        self.size_spin.setValue(16)
        self.size_spin.setFixedWidth(68)
        self.size_spin.valueChanged.connect(self._on_size_changed)
        algo_lay.addWidget(self.size_spin)

        # Data Line Edit
        d_lbl = QLabel("Data:")
        d_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600; font-size: 11px;")
        algo_lay.addWidget(d_lbl)

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Comma-separated values e.g. 24, 7, 51, 19, 88")
        self.data_input.setMinimumWidth(80)
        algo_lay.addWidget(self.data_input, 1)

        # Target (for searching)
        self.target_label = QLabel("Target:")
        self.target_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; font-weight: 600; font-size: 11px;")
        self.target_label.hide()
        algo_lay.addWidget(self.target_label)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("val")
        self.target_input.setFixedWidth(56)
        self.target_input.setValidator(QIntValidator())
        self.target_input.hide()
        algo_lay.addWidget(self.target_input)

        self.setStyleSheet(f"""
            InputToolbar {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)

        # Apply / New Data Button
        self.btn_apply = QPushButton("⚡ Apply")
        self.btn_apply.setToolTip("Generate/apply dataset and reset visualization")
        self.btn_apply.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['button_primary']};
                color: {COLORS['button_primary']};
            }}
        """)
        self.btn_apply.clicked.connect(self._on_apply_clicked)
        algo_lay.addWidget(self.btn_apply)

        self._stack.addWidget(algo_page)

        # ── Page 1: Graph Pathfinding Toolbar ────────────────────
        graph_page = QWidget()
        graph_lay = QHBoxLayout(graph_page)
        graph_lay.setContentsMargins(0, 0, 0, 0)
        graph_lay.setSpacing(8)

        g_lbl = QLabel("Maze Preset:")
        g_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600; font-size: 11px;")
        graph_lay.addWidget(g_lbl)

        self.maze_combo = QComboBox()
        self.maze_combo.addItems([
            "🧱 Default Obstacles",
            "🌀 Spiral Maze",
            "🎲 Random Walls (30%)",
            "⬜ Open Grid (No Walls)",
        ])
        self.maze_combo.setFixedWidth(175)
        self.maze_combo.currentIndexChanged.connect(self._on_maze_preset_changed)
        graph_lay.addWidget(self.maze_combo)

        btn_clear_walls = QPushButton("🗑️ Clear Walls")
        btn_clear_walls.setStyleSheet(f"""
            QPushButton {{
                background: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                border-color: {COLORS['error']};
                color: {COLORS['error']};
                background: #FDF1EE;
            }}
        """)
        btn_clear_walls.clicked.connect(self._on_clear_walls)
        graph_lay.addWidget(btn_clear_walls)

        graph_lay.addStretch()

        g_hint = QLabel("Grid: 7 × 12  •  Start: (0,0)  •  Goal: (6,11)")
        g_hint.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        graph_lay.addWidget(g_hint)

        self.btn_run_graph = QPushButton("⚡ Run Pathfinding")
        self.btn_run_graph.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['graph_start']};
                color: {COLORS['graph_start']};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #EEF6F3;
            }}
        """)
        self.btn_run_graph.clicked.connect(self._on_run_graph_clicked)
        graph_lay.addWidget(self.btn_run_graph)

        self._stack.addWidget(graph_page)

        # ── Page 2: Data Structure Operation Toolbar ─────────────
        ds_page = QWidget()
        self._ds_layout = QHBoxLayout(ds_page)
        self._ds_layout.setContentsMargins(0, 0, 0, 0)
        self._ds_layout.setSpacing(8)

        v_lbl = QLabel("Value:")
        v_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600; font-size: 11px;")
        self._ds_layout.addWidget(v_lbl)

        self.ds_value_input = QLineEdit()
        self.ds_value_input.setPlaceholderText("Integer")
        self.ds_value_input.setFixedWidth(70)
        self.ds_value_input.setValidator(QIntValidator())
        self._ds_layout.addWidget(self.ds_value_input)

        self._ds_btn_container = QWidget()
        self._ds_btn_layout = QHBoxLayout(self._ds_btn_container)
        self._ds_btn_layout.setContentsMargins(0, 0, 0, 0)
        self._ds_btn_layout.setSpacing(6)
        self._ds_layout.addWidget(self._ds_btn_container, 1)

        self._ds_layout.addStretch()
        self._stack.addWidget(ds_page)

        # Generate initial random data
        self._generate_preset_data("random")

    # ── Mode Selection ───────────────────────────────────────────

    def set_mode(self, mode: str, operations: list[str] | None = None) -> None:
        """Switch between 'sorting', 'searching', 'graph', 'data_structure'."""
        self._mode = mode
        if mode in ("sorting", "searching"):
            self._stack.setCurrentIndex(0)
            show_target = (mode == "searching")
            self.target_label.setVisible(show_target)
            self.target_input.setVisible(show_target)
            if show_target and not self.target_input.text():
                data = self.get_current_data()
                if data:
                    self.target_input.setText(str(random.choice(data)))
        elif mode == "graph":
            self._stack.setCurrentIndex(1)
        else:
            self._stack.setCurrentIndex(2)
            self._setup_ds_buttons(operations or [])

    # ── Dataset Generation ───────────────────────────────────────

    def get_current_data(self) -> list[int]:
        text = self.data_input.text().strip()
        if not text:
            self._generate_preset_data("random")
            text = self.data_input.text().strip()
        try:
            return [int(x.strip()) for x in text.split(",") if x.strip()]
        except ValueError:
            return [random.randint(5, 95) for _ in range(self.size_spin.value())]

    def _on_preset_changed(self, idx: int) -> None:
        presets = ["random", "nearly_sorted", "reversed", "duplicates", "sorted"]
        if 0 <= idx < len(presets):
            self._generate_preset_data(presets[idx])
            self._on_apply_clicked()

    def _on_size_changed(self, val: int) -> None:
        idx = self.preset_combo.currentIndex()
        presets = ["random", "nearly_sorted", "reversed", "duplicates", "sorted"]
        name = presets[idx] if 0 <= idx < len(presets) else "random"
        self._generate_preset_data(name)
        self._on_apply_clicked()

    def _generate_preset_data(self, preset: str) -> None:
        n = self.size_spin.value()
        if preset == "sorted":
            data = sorted(random.sample(range(5, 99), n))
        elif preset == "reversed":
            data = sorted(random.sample(range(5, 99), n), reverse=True)
        elif preset == "nearly_sorted":
            data = sorted(random.sample(range(5, 99), n))
            # Swap 2 or 3 adjacent items
            for _ in range(max(1, n // 6)):
                idx = random.randint(0, n - 2)
                data[idx], data[idx + 1] = data[idx + 1], data[idx]
        elif preset == "duplicates":
            choices = [random.randint(10, 80) for _ in range(max(3, n // 3))]
            data = [random.choice(choices) for _ in range(n)]
        else:  # random
            data = [random.randint(5, 95) for _ in range(n)]

        self.data_input.setText(", ".join(str(x) for x in data))

        # Update target if in search mode
        if self._mode == "searching" and data:
            self.target_input.setText(str(random.choice(data)))

    # ── Maze Presets ─────────────────────────────────────────────

    def _on_maze_preset_changed(self, idx: int) -> None:
        rows = DEFAULT_GRID_ROWS
        cols = DEFAULT_GRID_COLS
        if idx == 0:  # Default
            self._current_graph_walls = set(DEFAULT_WALLS)
        elif idx == 1:  # Spiral
            walls = set()
            for c in range(1, cols - 1):
                walls.add((1, c))
            for r in range(2, rows - 2):
                walls.add((r, cols - 2))
            for c in range(2, cols - 2):
                walls.add((rows - 2, c))
            self._current_graph_walls = walls
        elif idx == 2:  # Random (30%)
            walls = set()
            for r in range(rows):
                for c in range(cols):
                    if (r, c) not in (DEFAULT_START, DEFAULT_GOAL):
                        if random.random() < 0.28:
                            walls.add((r, c))
            self._current_graph_walls = walls
        else:  # Clear
            self._current_graph_walls = set()

        self._on_run_graph_clicked()

    def _on_clear_walls(self) -> None:
        self._current_graph_walls = set()
        self.maze_combo.setCurrentIndex(3)
        self._on_run_graph_clicked()

    def toggle_wall(self, r: int, c: int) -> None:
        """Called when user clicks a cell on the grid."""
        if (r, c) in (DEFAULT_START, DEFAULT_GOAL):
            return
        if (r, c) in self._current_graph_walls:
            self._current_graph_walls.remove((r, c))
        else:
            self._current_graph_walls.add((r, c))
        self._on_run_graph_clicked()

    def _on_run_graph_clicked(self) -> None:
        grid_info = {
            "rows": DEFAULT_GRID_ROWS,
            "cols": DEFAULT_GRID_COLS,
            "start": DEFAULT_START,
            "goal": DEFAULT_GOAL,
            "walls": set(self._current_graph_walls),
        }
        self.graph_config_requested.emit(grid_info)

    # ── Data Structure Operations ────────────────────────────────

    def _setup_ds_buttons(self, operations: list[str]) -> None:
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
            "insert_head": "⬆ Head",
            "insert_tail": "⬇ Tail",
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
            btn.setToolTip(f"Execute {op}")
            is_danger = op in ("clear", "delete")

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['surface']};
                    border: 1px solid {COLORS['border_light'] if not is_danger else COLORS['error']};
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-size: 11px;
                    color: {COLORS['error'] if is_danger else COLORS['text_primary']};
                }}
                QPushButton:hover {{
                    background: {COLORS['surface_hover']};
                    border-color: {COLORS['accent_cyan'] if not is_danger else COLORS['error']};
                }}
            """)
            btn.clicked.connect(lambda checked, o=op: self._on_ds_op(o))
            self._ds_btn_layout.addWidget(btn)

    def _on_ds_op(self, op: str) -> None:
        val_text = self.ds_value_input.text().strip()
        val = int(val_text) if val_text else random.randint(10, 99)
        self.ds_operation.emit(op, val)

    # ── Apply / Run Click ────────────────────────────────────────

    def _on_apply_clicked(self) -> None:
        data = self.get_current_data()
        if self._mode == "searching":
            target_str = self.target_input.text().strip()
            target = int(target_str) if target_str else (data[len(data) // 2] if data else 0)
            self.run_search_requested.emit(data, target)
        else:
            self.run_requested.emit(data)
