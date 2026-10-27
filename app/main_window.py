"""
Main Window — Flagship Algorithm Playground & Interactive Learning Laboratory.

Architecture:
┌────────────────────────────────────────────────────────────────────────┐
│  Top Application Bar: Logo • Algorithm Pill • Mode Switcher • Actions │
├───────────────┬────────────────────────────────────────┬───────────────┤
│  Algorithm    │  Central Workspace:                    │  Contextual   │
│  Explorer     │  ┌──────────────────────────────────┐  │  Inspector    │
│  (Collapsible │  │ Input Toolbar & Presets          │  │  (Tabs: Code, │
│   Drawer with │  ├──────────────────────────────────┤  │   Insights,   │
│   Live Search)│  │ Hero Visualization Canvas        │  │   Metrics,    │
│               │  │ (Bars, 2D Grid Graph, DS Views)  │  │   Complexity) │
│               │  ├──────────────────────────────────┤  │               │
│               │  │ Playback Bar & Timeline Scrubber │  │               │
│               │  └──────────────────────────────────┘  │               │
└───────────────┴────────────────────────────────────────┴───────────────┘
"""

from __future__ import annotations

import sys
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QFrame,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from app.theme import COLORS, get_category_config, apply_theme

# Redesigned Modern Widgets
from app.widgets.sidebar import Sidebar
from app.widgets.canvas import VisualizationCanvas
from app.widgets.playback_bar import PlaybackBar
from app.widgets.input_toolbar import InputToolbar
from app.widgets.inspector_panel import InspectorPanel
from app.widgets.ai_panel import AIPanel

# Engine
from app.engine.algorithm_engine import ALGORITHM_REGISTRY, Step
from app.engine.animation_engine import AnimationEngine

# Algorithm & Data Structure Registrations
from app.algorithms.sorting import register_sorting_algorithms
from app.algorithms.searching import register_searching_algorithms
from app.algorithms.graph import register_graph_algorithms, create_default_grid
from app.racing.racing_arena_window import RacingArenaWindow

from app.data_structures.stack_viz import (
    StackVisualizer,
    register_stack,
    STACK_PSEUDO,
)

from app.data_structures.queue_viz import (
    QueueVisualizer,
    register_queue,
    QUEUE_PSEUDO,
)

from app.data_structures.linked_list_viz import (
    LinkedListVisualizer,
    register_linked_list,
    LL_PSEUDO,
)

from app.data_structures.bst_viz import (
    BSTVisualizer,
    register_bst,
    BST_PSEUDO,
)


class MainWindow(QMainWindow):
    """Flagship DSA Playground Application Window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DSA Lab — Interactive Algorithm Playground")
        self.setMinimumSize(1020, 680)
        self.resize(1440, 860)

        # Ensure warm-light theme is applied
        from PySide6.QtWidgets import QApplication
        q_app = QApplication.instance()
        if q_app and not q_app.styleSheet():
            apply_theme(q_app)

        # ---------------------------------------------------------
        # 1. Register Algorithms & Data Structures
        # ---------------------------------------------------------
        register_sorting_algorithms()
        register_searching_algorithms()
        register_graph_algorithms()
        register_stack()
        register_queue()
        register_linked_list()
        register_bst()

        # ---------------------------------------------------------
        # 2. Application State
        # ---------------------------------------------------------
        self._current_key: str = ""
        self._current_question: str = ""
        self._current_input: Any = None
        self._current_output: Any = None
        self._current_target: Any = None
        self._current_graph_grid: dict | None = None

        # Engines & Dialogs
        self._engine = AnimationEngine(self)
        self._racing_window: RacingArenaWindow | None = None

        self._ds_instances: dict = {
            "stack": StackVisualizer(),
            "queue": QueueVisualizer(),
            "linked_list": LinkedListVisualizer(),
            "bst": BSTVisualizer(),
        }

        # ---------------------------------------------------------
        # 3. Build UI & Connect Signals
        # ---------------------------------------------------------
        self._build_ui()
        self._connect_signals()
        self._setup_shortcuts()

        # Default Selection: Bubble Sort
        self._on_algorithm_selected("bubble_sort")

    # ═══════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─────────────────────────────────────────────────────────
        # 1. Top Application Bar
        # ─────────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(52)
        top_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        tb_lay = QHBoxLayout(top_bar)
        tb_lay.setContentsMargins(18, 0, 18, 0)
        tb_lay.setSpacing(14)

        # Brand / Logo
        brand_box = QHBoxLayout()
        brand_box.setSpacing(8)
        logo_lbl = QLabel("⚡")
        logo_lbl.setFont(QFont("Segoe UI Emoji", 15))
        brand_box.addWidget(logo_lbl)

        brand_lbl = QLabel("DSA LAB")
        brand_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        brand_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; letter-spacing: 1.5px;")
        brand_box.addWidget(brand_lbl)
        tb_lay.addLayout(brand_box)

        tb_lay.addSpacing(10)

        # Active Algorithm & Complexity Pill (Initialised for Bubble Sort)
        self._algo_badge = QFrame()
        self._algo_badge.setStyleSheet("""
            QFrame {
                background-color: #FDF1EE;
                border: 1px solid #EBB3A4;
                border-radius: 14px;
                padding: 2px 10px;
            }
        """)
        badge_lay = QHBoxLayout(self._algo_badge)
        badge_lay.setContentsMargins(8, 2, 8, 2)
        badge_lay.setSpacing(8)

        self._badge_name = QLabel("📊 Bubble Sort")
        self._badge_name.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self._badge_name.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent;")
        badge_lay.addWidget(self._badge_name)

        self._badge_cx = QLabel("O(n²)")
        self._badge_cx.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._badge_cx.setStyleSheet("""
            color: #D96C4F;
            background-color: #FFFFFF;
            border: 1px solid #EBB3A4;
            border-radius: 8px;
            padding: 2px 6px;
        """)
        badge_lay.addWidget(self._badge_cx)
        tb_lay.addWidget(self._algo_badge)

        tb_lay.addStretch()

        # Center Mode Selector: Playground | Racing Arena
        mode_box = QFrame()
        mode_box.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)
        m_lay = QHBoxLayout(mode_box)
        m_lay.setContentsMargins(3, 3, 3, 3)
        m_lay.setSpacing(2)

        self._btn_mode_vis = QPushButton("🔬 Playground")
        self._btn_mode_vis.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 13px;
                padding: 5px 14px;
                font-weight: 600;
                font-size: 11px;
            }}
        """)
        m_lay.addWidget(self._btn_mode_vis)

        self._btn_mode_arena = QPushButton("🏁 Racing Arena")
        self._btn_mode_arena.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: none;
                border-radius: 13px;
                padding: 5px 14px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #FDF0ED;
                color: #D95F42;
            }}
        """)
        self._btn_mode_arena.clicked.connect(self._open_racing_arena)
        m_lay.addWidget(self._btn_mode_arena)
        tb_lay.addWidget(mode_box)

        tb_lay.addStretch()

        # Action: Export PDF Report
        self._export_pdf_btn = QPushButton("🖨  Export Report")
        self._export_pdf_btn.setToolTip("Export current algorithm run as a PDF study sheet")
        self._export_pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                border-color: {COLORS['text_muted']};
                color: {COLORS['text_primary']};
            }}
        """)
        self._export_pdf_btn.clicked.connect(self._export_pdf)
        tb_lay.addWidget(self._export_pdf_btn)

        # Action: AI Tutor Drawer Toggle
        self._ai_toggle_btn = QPushButton("🤖  AI Tutor")
        self._ai_toggle_btn.setToolTip("Toggle AI Pedagogical Assistant")
        self._ai_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: #34785B;
                color: #34785B;
            }}
        """)
        self._ai_toggle_btn.clicked.connect(self._toggle_ai_panel)
        tb_lay.addWidget(self._ai_toggle_btn)

        root.addWidget(top_bar)

        # ─────────────────────────────────────────────────────────
        # 2. Main Workspace Splitter
        # ─────────────────────────────────────────────────────────
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setHandleWidth(1)

        # A. Left: Algorithm Explorer Sidebar
        self._sidebar = Sidebar()
        self._main_splitter.addWidget(self._sidebar)

        # B. Center: Main Visualization Workspace
        center_workspace = QWidget()
        center_workspace.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        c_lay = QVBoxLayout(center_workspace)
        c_lay.setContentsMargins(10, 10, 10, 10)
        c_lay.setSpacing(10)

        # Top docked input configuration toolbar
        self._input_toolbar = InputToolbar()
        c_lay.addWidget(self._input_toolbar)

        # Hero Visualization Canvas
        self._canvas = VisualizationCanvas()
        c_lay.addWidget(self._canvas, 1)

        # Bottom docked playback bar & scrubbable timeline
        self._controls = PlaybackBar()
        c_lay.addWidget(self._controls)

        self._main_splitter.addWidget(center_workspace)

        # C. Right: Contextual Tabbed Inspector
        self._inspector = InspectorPanel()
        self._main_splitter.addWidget(self._inspector)

        # D. Far Right: AI Tutor Panel (initially hidden)
        self._ai_panel = AIPanel()
        self._ai_panel.hide()
        self._main_splitter.addWidget(self._ai_panel)

        # Configure splitter ratio: [Sidebar: 270, Center: 810, Inspector: 360]
        self._main_splitter.setSizes([270, 810, 360, 0])
        self._main_splitter.setCollapsible(0, True)
        self._main_splitter.setCollapsible(1, False)
        self._main_splitter.setCollapsible(2, True)

        root.addWidget(self._main_splitter, 1)

    # ═══════════════════════════════════════════════════════════════
    #  SIGNAL WIRING
    # ═══════════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        # Sidebar
        self._sidebar.algorithm_selected.connect(self._on_algorithm_selected)
        self._sidebar.racing_arena_requested.connect(self._open_racing_arena)
        self._sidebar.collapse_toggled.connect(self._on_sidebar_collapse)

        # Input Toolbar
        self._input_toolbar.run_requested.connect(self._on_run_sort)
        self._input_toolbar.run_search_requested.connect(self._on_run_search)
        self._input_toolbar.ds_operation.connect(self._on_ds_operation)
        self._input_toolbar.graph_config_requested.connect(self._on_run_graph)

        # Canvas Interactions
        self._canvas.wall_toggled.connect(self._input_toolbar.toggle_wall)

        # Playback Controls
        self._controls.play_clicked.connect(self._on_play)
        self._controls.pause_clicked.connect(self._on_pause)
        self._controls.step_forward_clicked.connect(self._on_step_forward)
        self._controls.step_backward_clicked.connect(self._on_step_backward)
        self._controls.reset_clicked.connect(self._on_reset)
        self._controls.speed_changed.connect(self._engine.set_speed)
        self._controls.seek_requested.connect(self._engine.seek)

        # Animation Engine
        self._engine.step_updated.connect(self._on_step_updated)
        self._engine.animation_finished.connect(self._on_animation_finished)

        # AI Panel
        self._ai_panel.close_requested.connect(self._on_ai_closed)

        # Inspector maximize
        self._inspector.maximize_requested.connect(self._toggle_inspector_maximize)

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for developer tool feel."""
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._on_shortcut_space)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self._on_step_backward)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self._on_step_forward)
        QShortcut(QKeySequence("R"), self, self._on_reset)
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self._sidebar.search_input.setFocus())

    def _on_shortcut_space(self) -> None:
        if self._engine.is_playing:
            self._on_pause()
        else:
            self._on_play()

    # ═══════════════════════════════════════════════════════════════
    #  ALGORITHM SELECTION
    # ═══════════════════════════════════════════════════════════════

    @Slot(str)
    def _on_algorithm_selected(self, key: str) -> None:
        self._current_key = key
        self._current_input = None
        self._current_output = None
        self._current_target = None
        self._current_graph_grid = None

        info = ALGORITHM_REGISTRY.get(key)
        if info is None:
            return

        # 1. Update Top Bar Badge & Sidebar Highlight
        cat_cfg = get_category_config(key)
        self._algo_badge.setStyleSheet(f"""
            QFrame {{
                background-color: {cat_cfg['light']};
                border: 1px solid {cat_cfg['border']};
                border-radius: 14px;
                padding: 2px 10px;
            }}
        """)
        self._badge_name.setText(f"{cat_cfg['icon']}  {info.name}")
        self._badge_name.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent; font-weight: 600;")
        self._badge_cx.setText(info.time_complexity)
        self._badge_cx.setStyleSheet(f"""
            color: {cat_cfg['accent']};
            background-color: #FFFFFF;
            border: 1px solid {cat_cfg['border']};
            border-radius: 8px;
            padding: 2px 6px;
        """)
        self._inspector.set_algorithm_key(key)
        self._sidebar.select_algorithm(key)

        # 2. Update Question
        self._current_question = getattr(info, "question", "")
        if not self._current_question:
            self._current_question = f"Analyze and trace the {info.name} algorithm execution."

        # 3. Configure Contextual Inspector
        self._inspector.set_pseudocode(info.pseudocode)
        self._inspector.set_complexity(
            time_cx=info.time_complexity,
            space_cx=info.space_complexity,
            name=info.name,
            desc=info.description,
        )
        self._inspector.reset()

        # 4. Reset Engine & Prepare Initial Canvas Preview
        self._engine.clear()
        self._canvas.set_algorithm_info(info.name, info.time_complexity, key=key)

        # 5. Set Input Toolbar Mode & Initial Run
        if info.category == "data_structure":
            self._input_toolbar.set_mode("data_structure", info.operations)
            ds = self._ds_instances.get(key)
            if ds and hasattr(ds, "_items"):
                self._canvas.set_preview_data(list(ds._items), mode=key)
            elif key == "bst":
                self._canvas.set_preview_data(ds._root if hasattr(ds, "_root") else None, mode="bst")
        elif info.category == "searching":
            self._input_toolbar.set_mode("searching")
            self._input_toolbar._on_apply_clicked()
        elif info.category == "graph":
            self._input_toolbar.set_mode("graph")
            self._input_toolbar._on_run_graph_clicked()
        else:
            self._input_toolbar.set_mode("sorting")
            self._input_toolbar._on_apply_clicked()

        # 6. Inform AI Panel
        self._ai_panel.set_algorithm(info)

    # ═══════════════════════════════════════════════════════════════
    #  EXECUTION: SORTING, SEARCHING, GRAPH, DS
    # ═══════════════════════════════════════════════════════════════

    @Slot(list)
    def _on_run_sort(self, data: list[int]) -> None:
        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None or info.generator_func is None:
            return

        self._current_input = list(data)
        self._current_target = None

        # Pre-compute steps
        gen = info.generator_func(list(data))
        self._engine.load(gen)
        self._update_final_output()

        self._ai_panel.set_input_context(
            input_data=self._current_input,
            target=self._current_target,
            question=self._current_question,
        )

    @Slot(list, int)
    def _on_run_search(self, data: list[int], target: int) -> None:
        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None or info.generator_func is None:
            return

        # Binary search requires sorted array
        if self._current_key == "binary_search":
            data = sorted(data)
            self._input_toolbar.data_input.setText(", ".join(str(x) for x in data))

        self._current_input = list(data)
        self._current_target = target

        gen = info.generator_func(list(data), target)
        self._engine.load(gen)
        self._update_final_output()

        self._ai_panel.set_input_context(
            input_data=self._current_input,
            target=self._current_target,
            question=self._current_question,
        )

    @Slot(dict)
    def _on_run_graph(self, grid_info: dict) -> None:
        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None or info.generator_func is None:
            return

        self._current_graph_grid = grid_info
        self._current_input = f"Grid: {grid_info['rows']}x{grid_info['cols']} from {grid_info['start']} to {grid_info['goal']}"

        gen = info.generator_func(grid_info)
        self._engine.load(gen)
        self._update_final_output()

        self._ai_panel.set_input_context(
            input_data=self._current_input,
            target=f"Goal: {grid_info['goal']}",
            question=self._current_question,
        )

    @Slot(str, int)
    def _on_ds_operation(self, operation: str, value: int) -> None:
        key = self._current_key
        ds = self._ds_instances.get(key)
        if ds is None:
            return

        self._current_input = value
        self._current_output = None

        # Update pseudocode for this operation
        pseudo_map = {
            "stack": STACK_PSEUDO,
            "queue": QUEUE_PSEUDO,
            "linked_list": LL_PSEUDO,
            "bst": BST_PSEUDO,
        }
        pm = pseudo_map.get(key, {})
        if operation in pm:
            self._inspector.set_pseudocode(pm[operation])

        readable_op = operation.replace("_", " ").title()
        self._current_question = f"Perform {readable_op} operation on {info_name(key)}."

        # Dispatch operation
        gen = None
        if key == "stack":
            if operation == "push":
                gen = ds.push(value)
            elif operation == "pop":
                gen = ds.pop()
            elif operation == "peek":
                gen = ds.peek()
            elif operation == "clear":
                gen = ds.clear()
        elif key == "queue":
            if operation == "enqueue":
                gen = ds.enqueue(value)
            elif operation == "dequeue":
                gen = ds.dequeue()
            elif operation == "front":
                gen = ds.front()
            elif operation == "clear":
                gen = ds.clear()
        elif key == "linked_list":
            if operation == "insert_head":
                gen = ds.insert_head(value)
            elif operation == "insert_tail":
                gen = ds.insert_tail(value)
            elif operation == "delete":
                gen = ds.delete(value)
            elif operation == "search":
                gen = ds.search(value)
            elif operation == "clear":
                gen = ds.clear()
        elif key == "bst":
            if operation == "insert":
                gen = ds.insert(value)
            elif operation == "search":
                gen = ds.search(value)
            elif operation == "inorder":
                gen = ds.inorder()
            elif operation == "preorder":
                gen = ds.preorder()
            elif operation == "postorder":
                gen = ds.postorder()
            elif operation == "clear":
                gen = ds.clear()

        if gen is not None:
            self._engine.load(gen)
            self._update_final_output()
            self._ai_panel.set_input_context(
                input_data=f"{operation}({value})",
                target=None,
                question=self._current_question,
            )

    # ═══════════════════════════════════════════════════════════════
    #  STEP SYNCHRONIZATION
    # ═══════════════════════════════════════════════════════════════

    @Slot(object)
    def _on_step_updated(self, step: Step) -> None:
        # Canvas
        self._canvas.update_step(step)

        # Inspector Tabs
        self._inspector.highlight_line(step.pseudocode_line)
        self._inspector.update_stats(step.stats)
        self._inspector.set_description(step.description)
        self._inspector.update_progress(self._engine.current_index, self._engine.total_steps)

        # Playback Controls & Timeline Scrubber
        self._controls.update_step_counter(self._engine.current_index, self._engine.total_steps)

        # AI Tutor
        self._ai_panel.set_step(step, self._engine.current_index, self._engine.total_steps)

    @Slot()
    def _on_play(self) -> None:
        self._engine.play()
        self._controls.set_playing(True)

    @Slot()
    def _on_pause(self) -> None:
        self._engine.pause()
        self._controls.set_playing(False)

    @Slot()
    def _on_step_forward(self) -> None:
        self._engine.step_forward()
        self._controls.set_playing(False)

    @Slot()
    def _on_step_backward(self) -> None:
        self._engine.step_backward()
        self._controls.set_playing(False)

    @Slot()
    def _on_reset(self) -> None:
        self._engine.reset()
        self._controls.set_playing(False)

    @Slot()
    def _on_animation_finished(self) -> None:
        self._controls.set_playing(False)

    def _update_final_output(self) -> None:
        try:
            if self._engine.total_steps <= 0:
                return
            final_step = self._engine._steps[-1]
            self._current_output = final_step.data
        except Exception:
            self._current_output = None

    # ═══════════════════════════════════════════════════════════════
    #  PANEL TOGGLES & RACING ARENA
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _toggle_ai_panel(self) -> None:
        if self._ai_panel.isVisible():
            self._ai_panel.hide()
            sizes = self._main_splitter.sizes()
            sizes[3] = 0
            self._main_splitter.setSizes(sizes)
            self._ai_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 6px 14px;
                    color: {COLORS['text_primary']};
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_hover']};
                    border-color: #34785B;
                    color: #34785B;
                }}
            """)
        else:
            self._ai_panel.show()
            sizes = self._main_splitter.sizes()
            sizes[3] = 360
            if sizes[1] > 600:
                sizes[1] = max(400, sizes[1] - 360)
            self._main_splitter.setSizes(sizes)
            self._ai_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #34785B;
                    border: 1px solid #34785B;
                    border-radius: 8px;
                    padding: 6px 14px;
                    color: #ffffff;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2B644B;
                }
            """)

    @Slot()
    def _on_ai_closed(self) -> None:
        sizes = self._main_splitter.sizes()
        sizes[3] = 0
        self._main_splitter.setSizes(sizes)
        self._ai_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: #34785B;
                color: #34785B;
            }}
        """)

    @Slot()
    def _open_racing_arena(self) -> None:
        if self._racing_window is None:
            self._racing_window = RacingArenaWindow()
            self._racing_window.open_in_visualizer.connect(self._on_algorithm_selected)
        self._racing_window.show()
        self._racing_window.raise_()
        self._racing_window.activateWindow()

    def _on_sidebar_collapse(self, collapsed: bool) -> None:
        sizes = self._main_splitter.sizes()
        if collapsed:
            sizes[0] = 56
        else:
            sizes[0] = 270
        self._main_splitter.setSizes(sizes)

    def _toggle_inspector_maximize(self) -> None:
        sizes = self._main_splitter.sizes()
        if sizes[2] > 400:
            sizes[2] = 340
        else:
            sizes[2] = 520
        self._main_splitter.setSizes(sizes)

    # ═══════════════════════════════════════════════════════════════
    #  PDF EXPORT REPORT
    # ═══════════════════════════════════════════════════════════════

    def _export_pdf(self) -> None:
        """Export comprehensive study report with algorithm metadata, pseudocode, and metrics."""
        if not self._current_key:
            QMessageBox.warning(self, "Export Report", "Please select an algorithm first.")
            return

        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export DSA Study Sheet",
            f"{info.name.replace(' ', '_')}_Report.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
            )
            sub_style = ParagraphStyle(
                "SubTitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
            )
            h2_style = ParagraphStyle(
                "Heading2",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=16,
                textColor=colors.HexColor("#0284c7"),
            )
            body_style = ParagraphStyle(
                "Body",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#334155"),
            )
            code_style = ParagraphStyle(
                "CodeStyle",
                parent=styles["Normal"],
                fontName="Courier",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#0f172a"),
            )

            story = []

            # Header
            story.append(Paragraph("DSA LAB • ALGORITHM STUDY REPORT", title_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"Generated for: {info.name}  •  {info.category.replace('_', ' ').title()}", sub_style))
            story.append(Spacer(1, 16))

            # Metadata Table
            meta_data = [
                [Paragraph("<b>Algorithm:</b>", body_style), Paragraph(info.name, body_style)],
                [Paragraph("<b>Category:</b>", body_style), Paragraph(info.category.title(), body_style)],
                [Paragraph("<b>Time Complexity:</b>", body_style), Paragraph(info.time_complexity, body_style)],
                [Paragraph("<b>Space Complexity:</b>", body_style), Paragraph(info.space_complexity, body_style)],
                [Paragraph("<b>Input Data:</b>", body_style), Paragraph(str(self._current_input or "N/A"), body_style)],
                [Paragraph("<b>Final Result:</b>", body_style), Paragraph(self._format_output(self._current_output), body_style)],
            ]
            meta_table = Table(meta_data, colWidths=[130, 380])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 14))

            # Pseudocode
            story.append(Paragraph("Algorithm Implementation / Pseudocode", h2_style))
            story.append(Spacer(1, 6))

            pseudo_text = "<br/>".join(
                f"{i+1:2d}.  {line.replace(' ', '&nbsp;')}" for i, line in enumerate(info.pseudocode)
            )
            story.append(Paragraph(pseudo_text, code_style))
            story.append(Spacer(1, 16))

            # Insights & Invariants
            story.append(Paragraph("Core Invariants & Logic Analysis", h2_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(info.description or "No additional description.", body_style))

            doc.build(story)
            QMessageBox.information(self, "Export Report", f"Report saved successfully to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Report Failed", f"Could not generate PDF: {e}")

    def _format_output(self, output: Any) -> str:
        if output is None:
            return "Execution not started or pending."
        if isinstance(output, list):
            if self._current_target is not None:
                try:
                    idx = output.index(self._current_target)
                    return f"Target {self._current_target} found at index {idx}."
                except ValueError:
                    return f"Target {self._current_target} not found in array."
            return str(output)
        return str(output)


def info_name(key: str) -> str:
    names = {
        "stack": "Stack",
        "queue": "Queue",
        "linked_list": "Singly Linked List",
        "bst": "Binary Search Tree",
    }
    return names.get(key, key.replace("_", " ").title())