"""
Winner Celebration Modal Dialog for Algorithm Racing Arena.

Displays final leaderboard standings, victory podium, comprehensive operation
breakdowns, and educational algorithm analysis.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
)

from app.theme import COLORS
from app.racing.race_models import RacerState


class WinnerCelebrationDialog(QDialog):
    """Celebratory finish dialog displaying winner, stats, and analysis."""

    inspect_requested = Signal(str)  # emits winning algo_key to load in main visualizer

    def __init__(self, rankings: list[RacerState], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rankings = rankings
        self.setWindowTitle("🏆 Race Results & Victory Podium")
        self.setFixedSize(680, 560)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        if not self._rankings:
            layout.addWidget(QLabel("No race results available."))
            return

        winner = self._rankings[0]

        # ── 1. Winner Banner Header ──────────────────────────────────
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FDF0ED, stop:1 #FBF5E8);
                border: 2px solid #D95F42;
                border-radius: 14px;
                padding: 12px;
            }}
        """)
        b_lay = QVBoxLayout(banner)
        b_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_lay.setSpacing(4)

        trophy = QLabel("🏆 ✨ 🏁 ✨ 🏆")
        trophy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trophy.setFont(QFont("Segoe UI Emoji", 18))
        b_lay.addWidget(trophy)

        w_title = QLabel(f"{winner.name} Takes 1st Place!")
        w_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        w_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        w_title.setStyleSheet("color: #D95F42;")
        b_lay.addWidget(w_title)

        w_sub = QLabel(f"Completed with {winner.operations} operations in {winner.elapsed_time_ms:.2f} ms ({winner.complexity})")
        w_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        w_sub.setFont(QFont("Segoe UI", 11))
        w_sub.setStyleSheet("color: #55584F;")
        b_lay.addWidget(w_sub)

        layout.addWidget(banner)

        # ── 2. Victory Podium ─────────────────────────────────────────
        podium = QHBoxLayout()
        podium.setSpacing(10)

        podium_ranks = [
            (1, "🥈 2nd Place", "#77796F", self._rankings[1] if len(self._rankings) > 1 else None),
            (0, "🥇 1st Place", "#D49A24", winner),
            (2, "🥉 3rd Place", "#D96C4F", self._rankings[2] if len(self._rankings) > 2 else None),
        ]

        for pos, title, col, racer in podium_ranks:
            p_card = QFrame()
            p_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {'#D95F42' if pos == 0 else COLORS['border']};
                    border-radius: 10px;
                    padding: 6px;
                }}
            """)
            c_lay = QVBoxLayout(p_card)
            c_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c_lay.setSpacing(3)

            lbl_t = QLabel(title)
            lbl_t.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl_t.setStyleSheet(f"color: {col};")
            lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c_lay.addWidget(lbl_t)

            if racer:
                lbl_n = QLabel(f"{racer.icon} {racer.name}")
                lbl_n.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                lbl_n.setStyleSheet(f"color: {racer.color};")
                lbl_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
                c_lay.addWidget(lbl_n)

                lbl_o = QLabel(f"{racer.operations} ops • {racer.elapsed_time_ms:.2f}ms")
                lbl_o.setFont(QFont("Segoe UI", 9))
                lbl_o.setStyleSheet(f"color: {COLORS['text_muted']};")
                lbl_o.setAlignment(Qt.AlignmentFlag.AlignCenter)
                c_lay.addWidget(lbl_o)
            else:
                lbl_empty = QLabel("—")
                lbl_empty.setStyleSheet(f"color: {COLORS['text_muted']};")
                c_lay.addWidget(lbl_empty)

            podium.addWidget(p_card)

        layout.addLayout(podium)

        # ── 3. Final Statistics Table ─────────────────────────────────
        table_lbl = QLabel("📋 Final Comparative Standings")
        table_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        table_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(table_lbl)

        table = QTableWidget()
        table.setRowCount(len(self._rankings))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Rank", "Algorithm", "Total Ops", "Comparisons", "Swaps", "Exec Time"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_primary']};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['surface']};
                color: {COLORS['accent_cyan']};
                font-weight: bold;
                border: none;
                padding: 4px;
            }}
        """)

        for row, r in enumerate(self._rankings):
            rank_str = {1: "🥇 1st", 2: "🥈 2nd", 3: "🥉 3rd"}.get(r.rank, f"#{r.rank}")
            table.setItem(row, 0, QTableWidgetItem(rank_str))
            table.setItem(row, 1, QTableWidgetItem(f"{r.icon} {r.name}"))
            table.setItem(row, 2, QTableWidgetItem(str(r.operations)))
            table.setItem(row, 3, QTableWidgetItem(str(r.comparisons)))
            table.setItem(row, 4, QTableWidgetItem(str(r.swaps)))
            table.setItem(row, 5, QTableWidgetItem(f"{r.elapsed_time_ms:.2f} ms"))

        table.setFixedHeight(120)
        layout.addWidget(table)

        # ── 4. Pedagogical Analysis ───────────────────────────────────
        analysis_box = QFrame()
        analysis_box.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        a_lay = QVBoxLayout(analysis_box)
        a_lay.setContentsMargins(0, 0, 0, 0)
        a_lay.setSpacing(4)

        a_title = QLabel("💡 Why Did This Algorithm Win?")
        a_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        a_title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        a_lay.addWidget(a_title)

        reason = self._generate_analysis(winner)
        a_desc = QLabel(reason)
        a_desc.setWordWrap(True)
        a_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; line-height: 1.4;")
        a_lay.addWidget(a_desc)

        layout.addWidget(analysis_box)

        # ── 5. Action Buttons ─────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        inspect_btn = QPushButton("🔬 Inspect Winner in Visualizer")
        inspect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                color: {COLORS['accent_cyan']};
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['accent_cyan']};
            }}
        """)
        inspect_btn.clicked.connect(self._on_inspect)
        btn_row.addWidget(inspect_btn)

        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                color: {COLORS['text_secondary']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)

        again_btn = QPushButton("🔄 Race Again")
        again_btn.setStyleSheet("""
            QPushButton {
                background-color: #D95F42;
                border: 1px solid #D95F42;
                border-radius: 8px;
                padding: 8px 20px;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #C24F34;
            }
        """)
        again_btn.clicked.connect(self.accept)
        btn_row.addWidget(again_btn)

        layout.addLayout(btn_row)

    def _generate_analysis(self, winner: RacerState) -> str:
        key = winner.algo_key
        if key in ("quick_sort", "merge_sort", "heap_sort"):
            return (
                f"{winner.name} achieved victory by leveraging divide-and-conquer logarithmic partitioning ({winner.complexity}). "
                "Unlike quadratic O(n²) algorithms which compare every pair repeatedly, it drastically minimizes redundant comparisons "
                "and efficiently sorts subarrays independently."
            )
        elif key == "insertion_sort":
            return (
                "Insertion Sort performed exceptionally well! On nearly sorted or smaller arrays, Insertion Sort's adaptive O(n) "
                "inner loop avoids overhead, shifting only inversions directly into position."
            )
        elif key == "binary_search":
            return (
                "Binary Search dominated by halving the search space at each comparison (O(log n)), finding the target in orders of "
                "magnitude fewer operations than Linear Search."
            )
        elif key == "astar_search":
            return (
                "A* Search claimed victory because its Manhattan heuristic guided the frontier directly toward the goal, "
                "avoiding expanding hundreds of irrelevant nodes unlike blind breadth or depth searches."
            )
        return (
            f"{winner.name} completed the challenge with superior operational efficiency on this input dataset. "
            "Note that algorithm performance varies depending on input size, distribution (random, sorted, or reversed), and hardware cache behavior."
        )

    def _on_inspect(self) -> None:
        if self._rankings:
            self.inspect_requested.emit(self._rankings[0].algo_key)
        self.accept()
