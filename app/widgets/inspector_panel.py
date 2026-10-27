"""
Contextual Tabbed Inspector — Deep Pedagogical Layer for the Algorithm Playground.
Refined for DSA Lab's warm-light paper & editorial design language.

Organized into 4 clean, non-clipping tabs:
  1. 📝 Code       — Line-numbered pseudocode with category-tinted active line highlight
  2. 💡 Insights   — Contextual step explanation (What, Why, Next Action, Invariants)
  3. 📊 Metrics    — Real-time comparison, swap, write counters and progress bar
  4. ⏱ Complexity — Time/Space complexity breakdown, stability, and algorithmic paradigm
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QPushButton,
    QTabWidget,
    QProgressBar,
    QStyle,
    QStyleOption,
)

from app.theme import COLORS, get_category_config


class InspectorPanel(QWidget):
    """Contextual tabbed inspector providing deep pedagogical insights."""

    maximize_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(330)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self._lines: list[QLabel] = []
        self._current_step_desc: str = ""
        self._active_key: str = "bubble_sort"
        self._build_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── 1. Inspector Header ──────────────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)

        title = QLabel("INSPECTOR")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; letter-spacing: 1px;")
        header.addWidget(title)

        header.addStretch()

        self._expand_btn = QPushButton("⛶")
        self._expand_btn.setFixedSize(26, 26)
        self._expand_btn.setToolTip("Toggle expand inspector")
        self._expand_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: {COLORS['text_secondary']};
                font-size: 13px;
                padding: 0;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
        """)
        self._expand_btn.clicked.connect(self.maximize_requested.emit)
        header.addWidget(self._expand_btn)
        root.addLayout(header)

        # ── 2. Tab Widget ────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Tab 1: Code
        self._build_code_tab()
        self.tabs.addTab(self.code_tab, "📝 Code")

        # Tab 2: Insights
        self._build_insights_tab()
        self.tabs.addTab(self.insights_tab, "💡 Insights")

        # Tab 3: Metrics
        self._build_metrics_tab()
        self.tabs.addTab(self.metrics_tab, "📊 Metrics")

        # Tab 4: Complexity
        self._build_complexity_tab()
        self.tabs.addTab(self.complexity_tab, "⏱ Complexity")

        root.addWidget(self.tabs, 1)

    # ── Tab 1: Code (Pseudocode) ─────────────────────────────────

    def _build_code_tab(self) -> None:
        self.code_tab = QWidget()
        lay = QVBoxLayout(self.code_tab)
        lay.setContentsMargins(6, 8, 6, 8)
        lay.setSpacing(6)

        # Scroll area for code lines
        self._code_scroll = QScrollArea()
        self._code_scroll.setWidgetResizable(True)
        self._code_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._code_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._code_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        self._code_container = QWidget()
        self._code_container.setStyleSheet(f"background: {COLORS['bg_secondary']};")
        self._code_layout = QVBoxLayout(self._code_container)
        self._code_layout.setContentsMargins(4, 6, 4, 6)
        self._code_layout.setSpacing(1)
        self._code_layout.addStretch()

        self._code_scroll.setWidget(self._code_container)
        lay.addWidget(self._code_scroll, 1)

        # Invariant note footer
        self.code_invariant_lbl = QLabel("Invariant: Elements before index are processed.")
        self.code_invariant_lbl.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 11px;
        """)
        self.code_invariant_lbl.setWordWrap(True)
        lay.addWidget(self.code_invariant_lbl)

    # ── Tab 2: Insights (Pedagogical Learning Layer) ──────────────

    def _build_insights_tab(self) -> None:
        self.insights_tab = QWidget()
        lay = QVBoxLayout(self.insights_tab)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(10)

        # Card 1: What is happening
        card_action = QFrame()
        card_action.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        act_lay = QVBoxLayout(card_action)
        act_lay.setContentsMargins(10, 8, 10, 8)
        act_lay.setSpacing(4)

        act_title = QLabel("CURRENT OPERATION")
        act_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        act_title.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        act_lay.addWidget(act_title)

        self.insight_operation = QLabel("Select an algorithm and click ▶ Play to inspect execution.")
        self.insight_operation.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.insight_operation.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.insight_operation.setWordWrap(True)
        act_lay.addWidget(self.insight_operation)
        lay.addWidget(card_action)

        # Card 2: Why it's doing it & What is next
        card_why = QFrame()
        card_why.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        why_lay = QVBoxLayout(card_why)
        why_lay.setContentsMargins(10, 8, 10, 8)
        why_lay.setSpacing(4)

        why_title = QLabel("PEDAGOGICAL INSIGHT")
        why_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        why_title.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        why_lay.addWidget(why_title)

        self.insight_why = QLabel("Step-by-step logic and mathematical invariants will update as the algorithm progresses.")
        self.insight_why.setFont(QFont("Segoe UI", 10))
        self.insight_why.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.4;")
        self.insight_why.setWordWrap(True)
        why_lay.addWidget(self.insight_why)
        lay.addWidget(card_why)

        # Card 3: Live Pointers & Invariants
        card_state = QFrame()
        card_state.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        state_lay = QVBoxLayout(card_state)
        state_lay.setContentsMargins(10, 8, 10, 8)
        state_lay.setSpacing(4)

        state_title = QLabel("ALGORITHM STATE & INVARIANTS")
        state_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        state_title.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        state_lay.addWidget(state_title)

        self.insight_state = QLabel("Pointers: None active • Invariant: Pre-execution")
        self.insight_state.setFont(QFont("Cascadia Code", 10))
        self.insight_state.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.insight_state.setWordWrap(True)
        state_lay.addWidget(self.insight_state)
        lay.addWidget(card_state)

        lay.addStretch()

    # ── Tab 3: Metrics ───────────────────────────────────────────

    def _build_metrics_tab(self) -> None:
        self.metrics_tab = QWidget()
        lay = QVBoxLayout(self.metrics_tab)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(10)

        # Top progress bar
        prog_box = QVBoxLayout()
        prog_box.setSpacing(3)
        p_row = QHBoxLayout()
        p_lbl = QLabel("Progress")
        p_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        p_row.addWidget(p_lbl)
        p_row.addStretch()
        self.metric_pct_lbl = QLabel("0%")
        self.metric_pct_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.metric_pct_lbl.setStyleSheet(f"color: {COLORS['button_primary']};")
        p_row.addWidget(self.metric_pct_lbl)
        prog_box.addLayout(p_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_tertiary']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['button_primary']};
                border-radius: 3px;
            }}
        """)
        prog_box.addWidget(self.progress_bar)
        lay.addLayout(prog_box)

        # Metric Tiles (Horizontal Pairs)
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.tile_comparisons = self._make_stat_tile("COMPARISONS", "0", COLORS["comparing"])
        self.tile_swaps = self._make_stat_tile("SWAPS / WRITES", "0", COLORS["swapping"])
        row1.addWidget(self.tile_comparisons)
        row1.addWidget(self.tile_swaps)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.tile_accesses = self._make_stat_tile("OPERATIONS", "0", COLORS["accent_purple"])
        self.tile_efficiency = self._make_stat_tile("STATUS", "Ready", COLORS["success"])
        row2.addWidget(self.tile_accesses)
        row2.addWidget(self.tile_efficiency)
        lay.addLayout(row2)

        # Summary box
        self.metric_summary_lbl = QLabel("Execution stats update in real time as each comparison, swap, and visit occurs.")
        self.metric_summary_lbl.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 10px;
            font-size: 11px;
            line-height: 1.4;
        """)
        self.metric_summary_lbl.setWordWrap(True)
        lay.addWidget(self.metric_summary_lbl)

        lay.addStretch()

    def _make_stat_tile(self, label: str, val: str, color_hex: str) -> QFrame:
        tile = QFrame()
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        t_lay = QVBoxLayout(tile)
        t_lay.setContentsMargins(10, 8, 10, 8)
        t_lay.setSpacing(2)

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_muted']}; border: none; background: transparent;")
        t_lay.addWidget(lbl)

        val_lbl = QLabel(val)
        val_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color: {color_hex}; border: none; background: transparent;")
        val_lbl.setObjectName("val")
        t_lay.addWidget(val_lbl)

        return tile

    def _set_tile_val(self, tile: QFrame, text: str) -> None:
        val_lbl = tile.findChild(QLabel, "val")
        if val_lbl:
            val_lbl.setText(text)

    # ── Tab 4: Complexity ────────────────────────────────────────

    def _build_complexity_tab(self) -> None:
        self.complexity_tab = QWidget()
        lay = QVBoxLayout(self.complexity_tab)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(10)

        # Time Complexity Card
        c_time = QFrame()
        c_time.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        t_lay = QVBoxLayout(c_time)
        t_lay.setContentsMargins(10, 8, 10, 8)
        t_lay.setSpacing(6)

        t_head = QLabel("TIME COMPLEXITY")
        t_head.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_head.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        t_lay.addWidget(t_head)

        self.cx_worst = QLabel("Worst Case:  O(n²)")
        self.cx_worst.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.cx_worst.setStyleSheet(f"color: {COLORS['text_primary']};")
        t_lay.addWidget(self.cx_worst)

        self.cx_avg = QLabel("Average Case: O(n²)")
        self.cx_avg.setFont(QFont("Segoe UI", 10))
        self.cx_avg.setStyleSheet(f"color: {COLORS['text_secondary']};")
        t_lay.addWidget(self.cx_avg)

        self.cx_best = QLabel("Best Case:    O(n)")
        self.cx_best.setFont(QFont("Segoe UI", 10))
        self.cx_best.setStyleSheet(f"color: {COLORS['success']};")
        t_lay.addWidget(self.cx_best)
        lay.addWidget(c_time)

        # Space & Properties Card
        c_prop = QFrame()
        c_prop.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        p_lay = QVBoxLayout(c_prop)
        p_lay.setContentsMargins(10, 8, 10, 8)
        p_lay.setSpacing(6)

        p_head = QLabel("SPACE & PROPERTIES")
        p_head.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p_head.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        p_lay.addWidget(p_head)

        self.cx_space = QLabel("Space Complexity: O(1) Auxiliary")
        self.cx_space.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.cx_space.setStyleSheet(f"color: {COLORS['accent_purple']};")
        p_lay.addWidget(self.cx_space)

        self.cx_props = QLabel("In-Place: Yes  •  Stable: Yes")
        self.cx_props.setFont(QFont("Segoe UI", 10))
        self.cx_props.setStyleSheet(f"color: {COLORS['text_secondary']};")
        p_lay.addWidget(self.cx_props)
        lay.addWidget(c_prop)

        # Theoretical Description
        self.cx_desc = QLabel("Iteratively sweeps adjacent items and bubbles larger values to their final sorted positions.")
        self.cx_desc.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 10px;
            font-size: 11px;
            line-height: 1.4;
        """)
        self.cx_desc.setWordWrap(True)
        lay.addWidget(self.cx_desc)

        lay.addStretch()

    # ── Public API (Pseudocode & Stats) ──────────────────────────

    def set_algorithm_key(self, key: str) -> None:
        """Store the active algorithm key and update tab accent highlights."""
        self._active_key = key
        cat_cfg = get_category_config(key)
        # Update Tab styling with active category color
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: {COLORS['surface']};
                border-radius: 0px 0px 8px 8px;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_tertiary']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                padding: 6px 11px;
                font-weight: 600;
                font-size: 11px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:hover {{
                background: {COLORS['surface_hover']};
                color: {COLORS['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background: {COLORS['surface']};
                color: {cat_cfg['accent']};
                border-bottom: 2px solid {cat_cfg['accent']};
            }}
        """)
        # Update progress bar chunk
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_tertiary']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {cat_cfg['accent']};
                border-radius: 3px;
            }}
        """)

    def set_pseudocode(self, lines: list[str]) -> None:
        """Replace pseudocode lines with clean monospace layout."""
        # Synchronously remove and detach all old widgets
        while self._code_layout.count():
            item = self._code_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self._lines.clear()

        mono = QFont("Cascadia Code", 9)
        mono.setStyleHint(QFont.StyleHint.Monospace)

        for i, line in enumerate(lines):
            lbl = QLabel(f" {i + 1:>2}  {line}")
            lbl.setFont(mono)
            lbl.setStyleSheet(self._code_line_style(False))
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self._code_layout.addWidget(lbl)
            self._lines.append(lbl)

        self._code_layout.addStretch()

    def highlight_line(self, line_num: int) -> None:
        """Highlight active 0-based pseudocode line."""
        for i, lbl in enumerate(self._lines):
            is_active = (i == line_num)
            lbl.setStyleSheet(self._code_line_style(is_active))
            if is_active:
                text = lbl.text()
                if not text.startswith("▶"):
                    lbl.setText(f"▶{text[1:]}")
            else:
                text = lbl.text()
                if text.startswith("▶"):
                    lbl.setText(f" {text[1:]}")

        if 0 <= line_num < len(self._lines):
            self._code_scroll.ensureWidgetVisible(self._lines[line_num])

    def clear_highlight(self) -> None:
        for lbl in self._lines:
            lbl.setStyleSheet(self._code_line_style(False))
            text = lbl.text()
            if text.startswith("▶"):
                lbl.setText(f" {text[1:]}")

    def update_stats(self, stats: dict) -> None:
        """Update metrics cards."""
        comps = stats.get("comparisons", stats.get("visited", "0"))
        swaps = stats.get("swaps", stats.get("path_length", "0"))
        ops = stats.get("operations", (int(comps) if str(comps).isdigit() else 0) + (int(swaps) if str(swaps).isdigit() else 0))

        self._set_tile_val(self.tile_comparisons, str(comps))
        self._set_tile_val(self.tile_swaps, str(swaps))
        self._set_tile_val(self.tile_accesses, str(ops))

    def update_progress(self, current: int, total: int) -> None:
        if total > 0:
            pct = int((current + 1) / total * 100)
            self.progress_bar.setValue(pct)
            self.metric_pct_lbl.setText(f"{pct}%")
            self._set_tile_val(self.tile_efficiency, f"Step {current + 1}/{total}")
        else:
            self.progress_bar.setValue(0)
            self.metric_pct_lbl.setText("0%")
            self._set_tile_val(self.tile_efficiency, "Ready")

    def set_description(self, text: str) -> None:
        """Update pedagogical insight based on current step description."""
        self._current_step_desc = text
        self.insight_operation.setText(text or "Executing algorithm step...")

        # Contextual intelligence: explain WHY and WHAT NEXT
        lower = text.lower()
        if "compare" in lower or "comparing" in lower:
            self.insight_why.setText(
                "The algorithm is comparing two elements to verify their relative ordering. "
                "If they violate the sorted invariant, a swap or partition boundary shift will occur next."
            )
            self.insight_state.setText("Action: Comparison • State: Evaluating Condition A[i] > A[j]")
        elif "swap" in lower or "moved" in lower:
            self.insight_why.setText(
                "An inversion was detected. The two elements are being exchanged to bring the larger "
                "item closer to its target position."
            )
            self.insight_state.setText("Action: Mutation • State: Array elements swapped at active indices")
        elif "pivot" in lower:
            self.insight_why.setText(
                "Pivot chosen. Partitioning guarantees that all elements less than the pivot move left, "
                "and elements greater move right."
            )
            self.insight_state.setText("Action: Partition • Invariant: A[p] in sorted position after partition")
        elif "sorted" in lower or "complete" in lower or "found" in lower:
            self.insight_why.setText(
                "Goal state reached! All elements satisfy the monotonicity invariant (A[0] ≤ A[1] ≤ ... ≤ A[n-1]), "
                "or the search target has been verified."
            )
            self.insight_state.setText("Status: Execution Finished Successfully ✨")
        elif "visit" in lower or "frontier" in lower:
            self.insight_why.setText(
                "Graph traversal is expanding neighboring unvisited vertices from the frontier queue. "
                "Shortest path estimates are updated monotonically."
            )
            self.insight_state.setText("Action: Graph Exploration • State: Frontier Pop & Neighbor Inspection")
        else:
            self.insight_why.setText(text)
            self.insight_state.setText("State: Advancing through instruction pipeline")

    def set_complexity(self, time_cx: str, space_cx: str, name: str = "", desc: str = "") -> None:
        """Configure complexity tab with algorithm properties."""
        self.cx_worst.setText(f"Worst Case:   {time_cx or 'O(n²)'}")
        self.cx_avg.setText(f"Average Case: {time_cx or 'O(n log n)'}")

        # Best case heuristics
        if "log" in time_cx:
            best = "O(n log n)"
        elif "²" in time_cx:
            best = "O(n)" if "bubble" in name.lower() or "insertion" in name.lower() else "O(n²)"
        else:
            best = "O(1)" if "stack" in name.lower() or "queue" in name.lower() else "O(V)"

        self.cx_best.setText(f"Best Case:     {best}")
        self.cx_space.setText(f"Space Complexity: {space_cx or 'O(1) Auxiliary'}")

        # Properties
        stable = "Yes" if any(k in name.lower() for k in ["bubble", "insertion", "merge"]) else "No"
        in_place = "Yes" if "merge" not in name.lower() and "graph" not in name.lower() else "No"
        self.cx_props.setText(f"In-Place: {in_place}  •  Stable: {stable}")

        if desc:
            self.cx_desc.setText(desc)

    def reset(self) -> None:
        self.clear_highlight()
        self.progress_bar.setValue(0)
        self.metric_pct_lbl.setText("0%")
        self._set_tile_val(self.tile_comparisons, "0")
        self._set_tile_val(self.tile_swaps, "0")
        self._set_tile_val(self.tile_accesses, "0")
        self._set_tile_val(self.tile_efficiency, "Ready")
        self.insight_operation.setText("Ready to execute algorithm. Press ▶ Play to begin.")
        self.insight_why.setText("Insights will stream as each step executes.")

    def set_algorithm_key(self, key: str) -> None:
        """Update active algorithm key to customize category styling and progress bar."""
        self._active_key = key
        cat_cfg = get_category_config(key)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_tertiary']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {cat_cfg['accent']};
                border-radius: 3px;
            }}
        """)

    def _code_line_style(self, active: bool) -> str:
        cat_cfg = get_category_config(self._active_key)
        if active:
            return f"""
                QLabel {{
                    background-color: {cat_cfg['light']};
                    color: {cat_cfg['accent']};
                    border-left: 3px solid {cat_cfg['accent']};
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-weight: bold;
                }}
            """
        return f"""
            QLabel {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border-left: 3px solid transparent;
                padding: 4px 8px;
            }}
        """
