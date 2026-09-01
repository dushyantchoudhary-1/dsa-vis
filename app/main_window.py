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
    QPushButton,
    QFileDialog,
    QMessageBox,
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
    """Top-level application window."""

    # ═══════════════════════════════════════════════════════════════
    # INITIALIZATION
    # ═══════════════════════════════════════════════════════════════

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DSA Visualizer with AI")
        self.setMinimumSize(1200, 720)
        self.resize(1440, 840)

        # ---------------------------------------------------------
        # Register all algorithms / data structures
        # ---------------------------------------------------------

        register_sorting_algorithms()
        register_searching_algorithms()
        register_stack()
        register_queue()
        register_linked_list()
        register_bst()

        # ---------------------------------------------------------
        # Application state
        # ---------------------------------------------------------

        self._current_key: str = ""

        # Current question
        self._current_question: str = ""

        # Input given by the user
        self._current_input = None

        # Final output of the algorithm
        self._current_output = None

        # Search target
        self._current_target = None

        # Animation engine
        self._engine = AnimationEngine(self)

        # AI panel state
        self._ai_visible = False

        # ---------------------------------------------------------
        # Persistent data structure instances
        # ---------------------------------------------------------

        self._ds_instances: dict = {
            "stack": StackVisualizer(),
            "queue": QueueVisualizer(),
            "linked_list": LinkedListVisualizer(),
            "bst": BSTVisualizer(),
        }

        # ---------------------------------------------------------
        # Build UI
        # ---------------------------------------------------------

        self._build_ui()
        self._connect_signals()

    # ═══════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ═════════════════════════════════════════════════════════
        # TOP BAR
        # ═════════════════════════════════════════════════════════

        top_bar = QWidget()
        top_bar.setFixedHeight(48)

        top_bar.setStyleSheet(
            f"""
            QWidget {{
                background: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
            """
        )

        tb_layout = QHBoxLayout(top_bar)

        tb_layout.setContentsMargins(
            16,
            0,
            16,
            0
        )

        # Application title

        app_title = QLabel(
            "🔬  DSA Visualizer"
        )

        app_title.setFont(
            QFont(
                "Helvetica Neue",
                15,
                QFont.Weight.Bold
            )
        )

        app_title.setStyleSheet(
            f"""
            color: {COLORS['accent_cyan']};
            background: transparent;
            border: none;
            """
        )

        tb_layout.addWidget(
            app_title
        )

        tb_layout.addStretch()

        # Algorithm name

        self._algo_name_label = QLabel("")

        self._algo_name_label.setFont(
            QFont(
                "Helvetica Neue",
                13
            )
        )

        self._algo_name_label.setStyleSheet(
            f"""
            color: {COLORS['text_secondary']};
            background: transparent;
            border: none;
            """
        )

        tb_layout.addWidget(
            self._algo_name_label
        )

        tb_layout.addStretch()

        # ═════════════════════════════════════════════════════════
        # EXPORT PDF BUTTON
        # ═════════════════════════════════════════════════════════

        self._export_pdf_btn = QPushButton(
            "🖨  Export PDF"
        )

        self._export_pdf_btn.setStyleSheet(
            f"""
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
            """
        )

        tb_layout.addWidget(
            self._export_pdf_btn
        )

        # ═════════════════════════════════════════════════════════
        # AI TUTOR BUTTON
        # ═════════════════════════════════════════════════════════

        self._ai_toggle_btn = self._make_ai_toggle()

        tb_layout.addWidget(
            self._ai_toggle_btn
        )

        root.addWidget(
            top_bar
        )

        # ═════════════════════════════════════════════════════════
        # BODY
        # ═════════════════════════════════════════════════════════

        body = QHBoxLayout()

        body.setContentsMargins(
            0,
            0,
            0,
            0
        )

        body.setSpacing(0)

        # ═════════════════════════════════════════════════════════
        # SIDEBAR
        # ═════════════════════════════════════════════════════════

        self._sidebar = Sidebar()

        body.addWidget(
            self._sidebar
        )

        # Separator

        sep1 = QFrame()

        sep1.setFrameShape(
            QFrame.Shape.VLine
        )

        sep1.setStyleSheet(
            f"color: {COLORS['border']};"
        )

        body.addWidget(
            sep1
        )

        # ═════════════════════════════════════════════════════════
        # MAIN SPLITTER
        # ═════════════════════════════════════════════════════════

        self._splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self._splitter.setHandleWidth(8)

        # ═════════════════════════════════════════════════════════
        # CANVAS
        # ═════════════════════════════════════════════════════════

        self._canvas = VisualizationCanvas()

        self._splitter.addWidget(
            self._canvas
        )

        # ═════════════════════════════════════════════════════════
        # RIGHT SPLITTER
        # ═════════════════════════════════════════════════════════

        self._right_splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        self._right_splitter.setHandleWidth(6)

        # Pseudocode panel

        self._pseudocode_panel = PseudocodePanel()

        self._right_splitter.addWidget(
            self._pseudocode_panel
        )

        # Statistics panel

        self._stats_panel = StatsPanel()

        self._right_splitter.addWidget(
            self._stats_panel
        )

        self._right_splitter.setSizes(
            [300, 500]
        )

        # Maximize buttons

        self._pseudocode_panel.maximize_requested.connect(
            self._maximize_pseudocode
        )

        self._stats_panel.maximize_requested.connect(
            self._maximize_stats
        )

        # Add right panel

        self._splitter.addWidget(
            self._right_splitter
        )

        self._splitter.setSizes(
            [700, 420]
        )

        body.addWidget(
            self._splitter,
            1
        )

        # ═════════════════════════════════════════════════════════
        # AI PANEL
        # ═════════════════════════════════════════════════════════

        self._ai_panel = AIPanel()

        self._ai_panel.hide()

        body.addWidget(
            self._ai_panel
        )

        body_widget = QWidget()

        body_widget.setLayout(
            body
        )

        root.addWidget(
            body_widget,
            1
        )

        # ═════════════════════════════════════════════════════════
        # BOTTOM CONTROLS
        # ═════════════════════════════════════════════════════════

        bottom = QWidget()

        bottom.setStyleSheet(
            f"""
            QWidget {{
                background: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border']};
            }}
            """
        )

        bottom_lay = QVBoxLayout(bottom)

        bottom_lay.setContentsMargins(
            0,
            0,
            0,
            0
        )

        bottom_lay.setSpacing(0)

        # Controls

        self._controls = ControlsBar()

        bottom_lay.addWidget(
            self._controls
        )

        # Separator

        sep_b = QFrame()

        sep_b.setFrameShape(
            QFrame.Shape.HLine
        )

        sep_b.setStyleSheet(
            f"color: {COLORS['border']};"
        )

        bottom_lay.addWidget(
            sep_b
        )

        # Input panel

        self._input_panel = InputPanel()

        bottom_lay.addWidget(
            self._input_panel
        )

        root.addWidget(
            bottom
        )

    # ═══════════════════════════════════════════════════════════════
    # MAXIMIZE PSEUDOCODE
    # ═══════════════════════════════════════════════════════════════

    def _maximize_pseudocode(self) -> None:

        if self._stats_panel.isVisible():

            self._stats_panel.hide()

        else:

            self._stats_panel.show()

            self._right_splitter.setSizes(
                [300, 500]
            )

    # ═══════════════════════════════════════════════════════════════
    # MAXIMIZE STATS
    # ═══════════════════════════════════════════════════════════════

    def _maximize_stats(self) -> None:

        if self._pseudocode_panel.isVisible():

            self._pseudocode_panel.hide()

        else:

            self._pseudocode_panel.show()

            self._right_splitter.setSizes(
                [300, 500]
            )

    # ═══════════════════════════════════════════════════════════════
    # AI BUTTON
    # ═══════════════════════════════════════════════════════════════

    def _make_ai_toggle(self):

        btn = QPushButton(
            "🤖  AI Tutor"
        )

        btn.setStyleSheet(
            f"""
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
            """
        )

        btn.clicked.connect(
            self._toggle_ai_panel
        )

        return btn

    # ═══════════════════════════════════════════════════════════════
    # SIGNAL WIRING
    # ═══════════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:

        # Sidebar

        self._sidebar.algorithm_selected.connect(
            self._on_algorithm_selected
        )

        # Controls

        self._controls.play_clicked.connect(
            self._on_play
        )

        self._controls.pause_clicked.connect(
            self._on_pause
        )

        self._controls.step_forward_clicked.connect(
            self._on_step_forward
        )

        self._controls.step_backward_clicked.connect(
            self._on_step_backward
        )

        self._controls.reset_clicked.connect(
            self._on_reset
        )

        self._controls.speed_changed.connect(
            self._engine.set_speed
        )

        # Engine → UI

        self._engine.step_updated.connect(
            self._on_step_updated
        )

        self._engine.animation_finished.connect(
            self._on_animation_finished
        )

        # Input panel

        self._input_panel.run_requested.connect(
            self._on_run_sort
        )

        self._input_panel.run_search_requested.connect(
            self._on_run_search
        )

        self._input_panel.ds_operation.connect(
            self._on_ds_operation
        )

        # PDF

        self._export_pdf_btn.clicked.connect(
            self._export_pdf
        )

    # ═══════════════════════════════════════════════════════════════
    # ALGORITHM SELECTED
    # ═══════════════════════════════════════════════════════════════

    @Slot(str)
    def _on_algorithm_selected(
        self,
        key: str
    ) -> None:

        self._current_key = key

        # Reset input/output

        self._current_input = None
        self._current_output = None
        self._current_target = None

        info = ALGORITHM_REGISTRY.get(
            key
        )

        if info is None:
            return

        # ---------------------------------------------------------
        # Get question from AlgorithmInfo if available
        # ---------------------------------------------------------

        self._current_question = getattr(
            info,
            "question",
            ""
        )

        # If no question exists, automatically create one

        if not self._current_question:

            self._current_question = (
                f"Use the {info.name} algorithm "
                f"to solve the given problem."
            )

        # ---------------------------------------------------------
        # Algorithm name
        # ---------------------------------------------------------

        self._algo_name_label.setText(
            f"{info.name}  •  "
            f"{info.time_complexity}"
        )

        # ---------------------------------------------------------
        # Pseudocode
        # ---------------------------------------------------------

        self._pseudocode_panel.set_pseudocode(
            info.pseudocode
        )

        self._pseudocode_panel.clear_highlight()

        # ---------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------

        self._stats_panel.set_complexity(
            info.time_complexity,
            info.space_complexity
        )

        self._stats_panel.reset()

        # ---------------------------------------------------------
        # Reset engine/canvas
        # ---------------------------------------------------------

        self._engine.clear()

        self._canvas.clear_canvas()

        # ---------------------------------------------------------
        # Configure input panel
        # ---------------------------------------------------------

        if info.category == "data_structure":

            self._input_panel.set_mode(
                "data_structure",
                info.operations
            )

        elif info.category == "searching":

            self._input_panel.set_mode(
                "searching"
            )

        else:

            self._input_panel.set_mode(
                "sorting"
            )

    # ═══════════════════════════════════════════════════════════════
    # RUN SORTING
    # ═══════════════════════════════════════════════════════════════

    @Slot(list)
    def _on_run_sort(
        self,
        data: list[int]
    ) -> None:

        info = ALGORITHM_REGISTRY.get(
            self._current_key
        )

        if (
            info is None
            or info.generator_func is None
        ):
            return

        # ---------------------------------------------------------
        # SAVE INPUT
        # ---------------------------------------------------------

        self._current_input = list(data)

        self._current_target = None

        # ---------------------------------------------------------
        # SAVE QUESTION
        # ---------------------------------------------------------

        self._current_question = getattr(
            info,
            "question",
            ""
        )

        if not self._current_question:

            self._current_question = (
                f"Given an array of integers, "
                f"sort the array in ascending order "
                f"using the {info.name} algorithm."
            )

        # ---------------------------------------------------------
        # RUN GENERATOR
        # ---------------------------------------------------------

        gen = info.generator_func(
            data
        )

        self._engine.load(
            gen
        )

        # ---------------------------------------------------------
        # Get final output
        # ---------------------------------------------------------

        self._update_final_output()

    # ═══════════════════════════════════════════════════════════════
    # RUN SEARCH
    # ═══════════════════════════════════════════════════════════════

    @Slot(list, int)
    def _on_run_search(
        self,
        data: list[int],
        target: int
    ) -> None:

        info = ALGORITHM_REGISTRY.get(
            self._current_key
        )

        if (
            info is None
            or info.generator_func is None
        ):
            return

        # ---------------------------------------------------------
        # SAVE INPUT
        # ---------------------------------------------------------

        self._current_input = list(data)

        self._current_target = target

        # ---------------------------------------------------------
        # SAVE QUESTION
        # ---------------------------------------------------------

        self._current_question = getattr(
            info,
            "question",
            ""
        )

        if not self._current_question:

            self._current_question = (
                f"Given an array of integers and a target value, "
                f"find the target using the {info.name} algorithm."
            )

        # ---------------------------------------------------------
        # RUN GENERATOR
        # ---------------------------------------------------------

        gen = info.generator_func(
            data,
            target
        )

        self._engine.load(
            gen
        )

        # ---------------------------------------------------------
        # Get final output
        # ---------------------------------------------------------

        self._update_final_output()

    # ═══════════════════════════════════════════════════════════════
    # DATA STRUCTURE OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    @Slot(str, int)
    def _on_ds_operation(
        self,
        operation: str,
        value: int
    ) -> None:

        key = self._current_key

        ds = self._ds_instances.get(
            key
        )

        if ds is None:
            return

        # ---------------------------------------------------------
        # Save operation as input
        # ---------------------------------------------------------

        self._current_input = value

        self._current_output = None

        # ---------------------------------------------------------
        # Pseudocode
        # ---------------------------------------------------------

        pseudo_map = {
            "stack": STACK_PSEUDO,
            "queue": QUEUE_PSEUDO,
            "linked_list": LL_PSEUDO,
            "bst": BST_PSEUDO,
        }

        pm = pseudo_map.get(
            key,
            {}
        )

        if operation in pm:

            self._pseudocode_panel.set_pseudocode(
                pm[operation]
            )

        # ---------------------------------------------------------
        # Generate question automatically
        # ---------------------------------------------------------

        readable_operation = operation.replace(
            "_",
            " "
        ).title()

        self._current_question = (
            f"Perform the {readable_operation} operation "
            f"on the {info_name(key)}."
        )

        # ---------------------------------------------------------
        # Dispatch operation
        # ---------------------------------------------------------

        gen = None

        # Stack

        if key == "stack":

            if operation == "push":

                gen = ds.push(value)

            elif operation == "pop":

                gen = ds.pop()

            elif operation == "peek":

                gen = ds.peek()

            elif operation == "clear":

                gen = ds.clear()

        # Queue

        elif key == "queue":

            if operation == "enqueue":

                gen = ds.enqueue(value)

            elif operation == "dequeue":

                gen = ds.dequeue()

            elif operation == "front":

                gen = ds.front_peek()

            elif operation == "clear":

                gen = ds.clear()

        # Linked List

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

        # BST

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

        # ---------------------------------------------------------
        # Load animation
        # ---------------------------------------------------------

        if gen is not None:

            self._engine.load(
                gen
            )

            self._update_final_output()

    # ═══════════════════════════════════════════════════════════════
    # UPDATE FINAL OUTPUT
    # ═══════════════════════════════════════════════════════════════

    def _update_final_output(self) -> None:
        """
        Get the final state from the animation engine.

        The engine pre-computes all generator steps, so the final
        Step contains the final data state.
        """

        try:

            if self._engine.total_steps <= 0:
                return

            # Save current index

            old_index = self._engine.current_index

            # Get final step

            final_step = self._engine._steps[
                -1
            ]

            self._current_output = final_step.data

            # Restore current index

            self._engine._current_index = old_index

        except Exception:

            self._current_output = None

    # ═══════════════════════════════════════════════════════════════
    # STEP UPDATED
    # ═══════════════════════════════════════════════════════════════

    @Slot(object)
    def _on_step_updated(
        self,
        step: Step
    ) -> None:

        self._canvas.update_step(
            step
        )

        self._pseudocode_panel.highlight_line(
            step.pseudocode_line
        )

        self._stats_panel.update_stats(
            step.stats
        )

        self._stats_panel.set_description(
            step.description
        )

        self._controls.update_step_counter(
            self._engine.current_index,
            self._engine.total_steps
        )

    # ═══════════════════════════════════════════════════════════════
    # PLAY
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_play(self) -> None:

        self._engine.play()

        self._controls.set_playing(
            True
        )

    # ═══════════════════════════════════════════════════════════════
    # PAUSE
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_pause(self) -> None:

        self._engine.pause()

        self._controls.set_playing(
            False
        )

    # ═══════════════════════════════════════════════════════════════
    # STEP FORWARD
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_step_forward(self) -> None:

        self._engine.step_forward()

        self._controls.set_playing(
            False
        )

    # ═══════════════════════════════════════════════════════════════
    # STEP BACKWARD
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_step_backward(self) -> None:

        self._engine.step_backward()

        self._controls.set_playing(
            False
        )

    # ═══════════════════════════════════════════════════════════════
    # RESET
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_reset(self) -> None:

        self._engine.reset()

        self._controls.set_playing(
            False
        )

    # ═══════════════════════════════════════════════════════════════
    # ANIMATION FINISHED
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_animation_finished(self) -> None:

        self._controls.set_playing(
            False
        )

    # ═══════════════════════════════════════════════════════════════
    # AI PANEL
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _toggle_ai_panel(self) -> None:

        self._ai_visible = not self._ai_visible

        self._ai_panel.setVisible(
            self._ai_visible
        )

    # ═══════════════════════════════════════════════════════════════
    # PDF EXPORT
    # ═══════════════════════════════════════════════════════════════

    def _export_pdf(self) -> None:
        """
        Export the current visualization information as a PDF.

        The report contains:

        - Algorithm / Data Structure
        - Question
        - User Input
        - Target (for searching)
        - Output
        - Time Complexity
        - Space Complexity
        - Pseudocode
        - Statistics
        - Current Operation
        """

        # ---------------------------------------------------------
        # Check algorithm selection
        # ---------------------------------------------------------

        if not self._current_key:

            QMessageBox.warning(
                self,
                "Export PDF",
                "Please select an algorithm first."
            )

            return

        info = ALGORITHM_REGISTRY.get(
            self._current_key
        )

        if info is None:
            return

        # ---------------------------------------------------------
        # Ask save location
        # ---------------------------------------------------------

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export DSA Visualization",
            f"{info.name.replace(' ', '_')}_Report.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        # ---------------------------------------------------------
        # Generate PDF
        # ---------------------------------------------------------

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

            from reportlab.lib.styles import (
                getSampleStyleSheet,
                ParagraphStyle,
            )

            from reportlab.lib.enums import (
                TA_CENTER,
            )

            # =====================================================
            # DOCUMENT
            # =====================================================

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40,
            )

            styles = getSampleStyleSheet()

            title_style = styles["Title"]

            title_style.alignment = TA_CENTER

            heading_style = styles["Heading2"]

            normal_style = styles["BodyText"]

            # =====================================================
            # CONTENT
            # =====================================================

            content = []

            # =====================================================
            # TITLE
            # =====================================================

            content.append(
                Paragraph(
                    "DSA Visualizer Report",
                    title_style
                )
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # ALGORITHM
            # =====================================================

            content.append(
                Paragraph(
                    f"<b>Algorithm / Data Structure:</b> "
                    f"{info.name}",
                    normal_style
                )
            )

            content.append(
                Spacer(1, 12)
            )

            # =====================================================
            # QUESTION
            # =====================================================

            content.append(
                Paragraph(
                    "Question / Problem Statement",
                    heading_style
                )
            )

            question = self._current_question

            if not question:

                question = getattr(
                    info,
                    "question",
                    ""
                )

            if not question:

                question = (
                    f"Use the {info.name} algorithm "
                    f"to solve the given problem."
                )

            content.append(
                Paragraph(
                    question,
                    normal_style
                )
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # INPUT
            # =====================================================

            content.append(
                Paragraph(
                    "Input",
                    heading_style
                )
            )

            # Searching

            if (
                self._current_target is not None
                and isinstance(
                    self._current_input,
                    list
                )
            ):

                input_text = (
                    f"<b>Array:</b> "
                    f"{self._current_input}<br/>"
                    f"<b>Target:</b> "
                    f"{self._current_target}"
                )

            # Sorting

            elif isinstance(
                self._current_input,
                list
            ):

                input_text = str(
                    self._current_input
                )

            # Data structure

            elif self._current_input is not None:

                input_text = str(
                    self._current_input
                )

            else:

                input_text = (
                    "No input has been provided."
                )

            content.append(
                Paragraph(
                    input_text,
                    normal_style
                )
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # OUTPUT
            # =====================================================

            content.append(
                Paragraph(
                    "Output",
                    heading_style
                )

            )

            output_text = self._format_output(
                self._current_output
            )

            content.append(
                Paragraph(
                    output_text,
                    normal_style
                )
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # COMPLEXITY
            # =====================================================

            content.append(
                Paragraph(
                    f"<b>Time Complexity:</b> "
                    f"{info.time_complexity}",
                    normal_style
                )
            )

            content.append(
                Paragraph(
                    f"<b>Space Complexity:</b> "
                    f"{info.space_complexity}",
                    normal_style
                )
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # PSEUDOCODE
            # =====================================================

            content.append(
                Paragraph(
                    "Pseudocode",
                    heading_style
                )
            )

            for i, line in enumerate(
                info.pseudocode
            ):

                # Escape special ReportLab characters

                safe_line = (
                    str(line)
                    .replace(
                        "&",
                        "&amp;"
                    )
                    .replace(
                        "<",
                        "&lt;"
                    )
                    .replace(
                        ">",
                        "&gt;"
                    )
                )

                content.append(
                    Paragraph(
                        f"{i + 1}. {safe_line}",
                        normal_style
                    )
                )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # STATISTICS
            # =====================================================

            comparisons = (
                self
                ._stats_panel
                .card_comparisons
                ._value
                .text()
            )

            swaps = (
                self
                ._stats_panel
                .card_swaps
                ._value
                .text()
            )

            # Change "Swaps" to "Shifts" for Insertion Sort

            if info.name.lower() == "insertion sort":

                second_metric_name = "Shifts"

            else:

                second_metric_name = "Swaps"

            stats_data = [
                [
                    "Metric",
                    "Value",
                ],
                [
                    "Comparisons",
                    comparisons,
                ],
                [
                    second_metric_name,
                    swaps,
                ],
            ]

            table = Table(
                stats_data,
                colWidths=[
                    200,
                    100,
                ],
            )

            table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),

                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),

                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            content.append(
                Paragraph(
                    "Statistics",
                    heading_style
                )
            )

            content.append(
                table
            )

            content.append(
                Spacer(1, 15)
            )

            # =====================================================
            # CURRENT OPERATION
            # =====================================================

            content.append(
                Paragraph(
                    "Current Operation",
                    heading_style
                )
            )

            description = (
                self
                ._stats_panel
                .description_label
                .text()
            )

            if not description:

                description = (
                    "No operation has been executed yet."
                )

            content.append(
                Paragraph(
                    description,
                    normal_style
                )
            )

            # =====================================================
            # BUILD PDF
            # =====================================================

            doc.build(
                content
            )

            # =====================================================
            # SUCCESS
            # =====================================================

            QMessageBox.information(
                self,
                "Export Complete",
                f"PDF successfully saved to:\n\n"
                f"{file_path}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not create PDF:\n\n"
                f"{str(e)}"
            )

    # ═══════════════════════════════════════════════════════════════
    # FORMAT OUTPUT
    # ═══════════════════════════════════════════════════════════════

    def _format_output(
        self,
        output
    ) -> str:
        """
        Convert the final Step data into readable PDF text.
        """

        if output is None:

            return "No output available."

        # List output

        if isinstance(
            output,
            list
        ):

            # Search output

            if self._current_target is not None:

                target = self._current_target

                try:

                    index = output.index(
                        target
                    )

                    return (
                        f"Target {target} found at "
                        f"index {index}."
                    )

                except ValueError:

                    return (
                        f"Target {target} was not found."
                    )

            # Sorting output

            return str(
                output
            )

        # Dictionary output

        if isinstance(
            output,
            dict
        ):

            return str(
                output
            )

        return str(
            output
        )


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTION
# ═══════════════════════════════════════════════════════════════════

def info_name(
    key: str
) -> str:
    """
    Convert an internal data-structure key into a readable name.
    """

    names = {
        "stack": "Stack",
        "queue": "Queue",
        "linked_list": "Singly Linked List",
        "bst": "Binary Search Tree",
    }

    return names.get(
        key,
        key.replace("_", " ").title()
    )