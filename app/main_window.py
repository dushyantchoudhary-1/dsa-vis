"""
Main window — orchestrates all widgets, the algorithm registry,
and the animation engine.

Layout
──────
┌─────────┬───────────────────────┬────────────────┐
│ Sidebar │   Canvas              │  Pseudocode    │
│         │                       │  + Stats       │
│         │                       │                │
├─────────┴───────────────────────┴────────────────┤
│  Controls bar                                    │
│  Input panel                                     │
└──────────────────────────────────────────────────┘
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QFrame,
)

from app.theme import COLORS

# Widgets
from app.widgets.sidebar import Sidebar
from app.widgets.canvas import VisualizationCanvas
from app.widgets.controls import ControlsBar
from app.widgets.stats_panel import StatsPanel
from app.widgets.pseudocode_panel import PseudocodePanel
from app.widgets.input_panel import InputPanel
from app.widgets.ai_panel import AIPanel

# Engine
from app.engine.algorithm_engine import ALGORITHM_REGISTRY, Step
from app.engine.animation_engine import AnimationEngine

# Algorithm / DS registrations
from app.algorithms.sorting import register_sorting_algorithms
from app.algorithms.searching import register_searching_algorithms
from app.data_structures.stack_viz import StackVisualizer, register_stack, STACK_PSEUDO
from app.data_structures.queue_viz import QueueVisualizer, register_queue, QUEUE_PSEUDO
from app.data_structures.linked_list_viz import LinkedListVisualizer, register_linked_list, LL_PSEUDO
from app.data_structures.bst_viz import BSTVisualizer, register_bst, BST_PSEUDO


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DSA Visualizer with AI")
        self.setMinimumSize(1200, 720)
        self.resize(1440, 840)

        # Register all algorithms / data structures
        register_sorting_algorithms()
        register_searching_algorithms()
        register_stack()
        register_queue()
        register_linked_list()
        register_bst()

        # State
        self._current_key: str = ""
        self._engine = AnimationEngine(self)
        self._ai_visible = False

        # Data-structure instances (persistent across operations)
        self._ds_instances: dict = {
            "stack":       StackVisualizer(),
            "queue":       QueueVisualizer(),
            "linked_list": LinkedListVisualizer(),
            "bst":         BSTVisualizer(),
        }

        self._build_ui()
        self._connect_signals()

    # ═══════════════════════════════════════════════════════════════
    #  UI construction
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(48)
        top_bar.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(16, 0, 16, 0)

        app_title = QLabel("🔬  DSA Visualizer")
        app_title.setFont(QFont("Helvetica Neue", 15, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent; border: none;")
        tb_layout.addWidget(app_title)

        tb_layout.addStretch()

        self._algo_name_label = QLabel("")
        self._algo_name_label.setFont(QFont("Helvetica Neue", 13))
        self._algo_name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        tb_layout.addWidget(self._algo_name_label)

        tb_layout.addStretch()

        self._ai_toggle_btn = self._make_ai_toggle()
        tb_layout.addWidget(self._ai_toggle_btn)

        root.addWidget(top_bar)

        # ── Body (horizontal) ───────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        body.addWidget(self._sidebar)

        # Vertical separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color: {COLORS['border']};")
        body.addWidget(sep1)

        # Centre + right in a splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(3)

        # Canvas
        self._canvas = VisualizationCanvas()
        self._splitter.addWidget(self._canvas)

        # Right panel (pseudocode + stats)
        right_panel = QWidget()
        right_lay = QVBoxLayout(right_panel)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        self._pseudocode_panel = PseudocodePanel()
        right_lay.addWidget(self._pseudocode_panel, 1)

        sep_h = QFrame()
        sep_h.setFrameShape(QFrame.Shape.HLine)
        sep_h.setStyleSheet(f"color: {COLORS['border']};")
        right_lay.addWidget(sep_h)

        self._stats_panel = StatsPanel()
        right_lay.addWidget(self._stats_panel, 1)

        self._splitter.addWidget(right_panel)
        self._splitter.setSizes([800, 320])

        body.addWidget(self._splitter, 1)

        # AI panel (hidden by default)
        self._ai_panel = AIPanel()
        self._ai_panel.hide()
        body.addWidget(self._ai_panel)

        body_widget = QWidget()
        body_widget.setLayout(body)
        root.addWidget(body_widget, 1)

        # ── Bottom: controls + input ─────────────────────────────
        bottom = QWidget()
        bottom.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)
        bottom_lay = QVBoxLayout(bottom)
        bottom_lay.setContentsMargins(0, 0, 0, 0)
        bottom_lay.setSpacing(0)

        self._controls = ControlsBar()
        bottom_lay.addWidget(self._controls)

        sep_b = QFrame()
        sep_b.setFrameShape(QFrame.Shape.HLine)
        sep_b.setStyleSheet(f"color: {COLORS['border']};")
        bottom_lay.addWidget(sep_b)

        self._input_panel = InputPanel()
        bottom_lay.addWidget(self._input_panel)

        root.addWidget(bottom)

    def _make_ai_toggle(self):
        from PySide6.QtWidgets import QPushButton
        btn = QPushButton("🤖  AI Tutor")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 6px 16px;
                color: {COLORS['accent_cyan']};
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {COLORS['surface_hover']};
                border-color: {COLORS['accent_cyan']};
            }}
        """)
        btn.clicked.connect(self._toggle_ai_panel)
        return btn

    # ═══════════════════════════════════════════════════════════════
    #  Signal wiring
    # ═══════════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        # Sidebar
        self._sidebar.algorithm_selected.connect(self._on_algorithm_selected)

        # Controls
        self._controls.play_clicked.connect(self._on_play)
        self._controls.pause_clicked.connect(self._on_pause)
        self._controls.step_forward_clicked.connect(self._on_step_forward)
        self._controls.step_backward_clicked.connect(self._on_step_backward)
        self._controls.reset_clicked.connect(self._on_reset)
        self._controls.speed_changed.connect(self._engine.set_speed)

        # Engine → UI
        self._engine.step_updated.connect(self._on_step_updated)
        self._engine.animation_finished.connect(self._on_animation_finished)

        # Input panel
        self._input_panel.run_requested.connect(self._on_run_sort)
        self._input_panel.run_search_requested.connect(self._on_run_search)
        self._input_panel.ds_operation.connect(self._on_ds_operation)

    # ═══════════════════════════════════════════════════════════════
    #  Slots
    # ═══════════════════════════════════════════════════════════════

    @Slot(str)
    def _on_algorithm_selected(self, key: str) -> None:
        self._current_key = key
        info = ALGORITHM_REGISTRY.get(key)
        if info is None:
            return

        self._algo_name_label.setText(f"{info.name}  •  {info.time_complexity}")
        self._pseudocode_panel.set_pseudocode(info.pseudocode)
        self._pseudocode_panel.clear_highlight()
        self._stats_panel.set_complexity(info.time_complexity, info.space_complexity)
        self._stats_panel.reset()
        self._engine.clear()
        self._canvas.clear_canvas()

        if info.category == "data_structure":
            self._input_panel.set_mode("data_structure", info.operations)
        elif info.category == "searching":
            self._input_panel.set_mode("searching")
        else:
            self._input_panel.set_mode("sorting")

    @Slot(list)
    def _on_run_sort(self, data: list[int]) -> None:
        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None or info.generator_func is None:
            return
        gen = info.generator_func(data)
        self._engine.load(gen)

    @Slot(list, int)
    def _on_run_search(self, data: list[int], target: int) -> None:
        info = ALGORITHM_REGISTRY.get(self._current_key)
        if info is None or info.generator_func is None:
            return
        gen = info.generator_func(data, target)
        self._engine.load(gen)

    @Slot(str, int)
    def _on_ds_operation(self, operation: str, value: int) -> None:
        key = self._current_key
        ds = self._ds_instances.get(key)
        if ds is None:
            return

        # Update pseudocode for the specific operation
        pseudo_map = {
            "stack": STACK_PSEUDO,
            "queue": QUEUE_PSEUDO,
            "linked_list": LL_PSEUDO,
            "bst": BST_PSEUDO,
        }
        pm = pseudo_map.get(key, {})
        if operation in pm:
            self._pseudocode_panel.set_pseudocode(pm[operation])

        # Dispatch to the correct method
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
                gen = ds.front_peek()
            elif operation == "clear":
                gen = ds.clear()
        elif key == "linked_list":
            if operation == "insert_head":
                gen = ds.insert_head(value)
            elif operation == "insert_tail":
                gen = ds.insert_tail(value)
            elif operation == "delete":
                gen = ds.delete_value(value)
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

    @Slot(object)
    def _on_step_updated(self, step: Step) -> None:
        self._canvas.update_step(step)
        self._pseudocode_panel.highlight_line(step.pseudocode_line)
        self._stats_panel.update_stats(step.stats)
        self._stats_panel.set_description(step.description)
        self._controls.update_step_counter(
            self._engine.current_index, self._engine.total_steps
        )

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

    @Slot()
    def _toggle_ai_panel(self) -> None:
        self._ai_visible = not self._ai_visible
        self._ai_panel.setVisible(self._ai_visible)
