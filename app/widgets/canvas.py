"""
Visualization canvas — renders algorithm states with high-fidelity graphics.
Refined for DSA Lab's warm-light paper & editorial design language.

Supports 6 distinct visualization modes:
  bars         — vertical animated bar chart (sorting & searching)
  graph        — 2D grid pathfinding visualizer (BFS, DFS, Dijkstra, A*)
  stack        — vertical vessel with top pointer (Stack LIFO)
  queue        — horizontal conveyor with front/rear pointers (Queue FIFO)
  linked_list  — dual-cell node-pointer chain with null terminator
  bst          — balanced tree layout with branch edges and glowing nodes
"""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
)
from PySide6.QtWidgets import QWidget

from app.theme import COLORS, get_category_config


def _c(key: str) -> QColor:
    """Look up a color token and return QColor."""
    return QColor(COLORS.get(key, COLORS["default_bar"]))


class VisualizationCanvas(QWidget):
    """Adaptive, high-fidelity canvas that visually communicates algorithm logic."""

    wall_toggled = Signal(int, int)  # emitted when user clicks a grid cell in graph mode

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(500, 360)
        self._data: Any = None
        self._highlights: dict = {}
        self._mode: str = "bars"
        self._description: str = ""
        self._algorithm_name: str = "Bubble Sort"
        self._algorithm_complexity: str = "O(n²)"
        self._algorithm_key: str = "bubble_sort"
        self._is_empty: bool = True

        # Graph interactive state
        self._grid_cell_size: float = 40.0
        self._grid_offset_x: float = 0.0
        self._grid_offset_y: float = 0.0
        self._grid_rows: int = 7
        self._grid_cols: int = 12

    # ── Public API ───────────────────────────────────────────────

    def set_algorithm_info(self, name: str, complexity: str, mode: str = "bars", key: str = "") -> None:
        """Inform canvas about active algorithm for smart empty state."""
        self._algorithm_name = name
        self._algorithm_complexity = complexity
        self._mode = mode
        if key:
            self._algorithm_key = key
        self.update()

    def update_step(self, step) -> None:
        """Accept a Step snapshot and trigger a repaint."""
        self._data = step.data
        self._highlights = step.highlights
        self._mode = getattr(step, "visualization_type", "bars")
        self._description = step.description or ""
        self._is_empty = False
        self.update()

    def set_preview_data(self, data: Any, mode: str = "bars", key: str = "") -> None:
        """Display data in ready/preview state before animation runs."""
        self._data = data
        self._highlights = {}
        self._mode = mode
        if key:
            self._algorithm_key = key
        self._description = f"Ready to run {self._algorithm_name}. Click ▶ Play or ⏭ Step."
        self._is_empty = False
        self.update()

    def clear_canvas(self) -> None:
        self._data = None
        self._highlights = {}
        self._description = ""
        self._is_empty = True
        self.update()

    # ── Paint Dispatch ───────────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Warm-Light Canvas Background: Clean pure white with subtle border
        painter.fillRect(self.rect(), QColor(COLORS["bg_canvas"]))
        painter.setPen(QPen(QColor(COLORS["border"]), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # 2. Header Legend & Operation Banner
        self._paint_canvas_header(painter)

        # 3. Content Dispatch
        if self._is_empty or self._data is None:
            self._paint_empty_card(painter)
            painter.end()
            return

        dispatch = {
            "bars":        self._paint_bars,
            "graph":       self._paint_graph,
            "stack":       self._paint_stack,
            "queue":       self._paint_queue,
            "linked_list": self._paint_linked_list,
            "bst":         self._paint_bst,
        }
        fn = dispatch.get(self._mode, self._paint_bars)
        fn(painter)
        painter.end()

    # ── Canvas Header & Legend ────────────────────────────────────

    def _paint_canvas_header(self, p: QPainter) -> None:
        """Render two-tier HUD header: Category + Legend on top, full step description below."""
        p.save()
        header_h = 58

        # Divider line below header
        p.setPen(QPen(QColor(COLORS["border"]), 1))
        p.drawLine(14, header_h, self.width() - 14, header_h)

        cat_cfg = get_category_config(self._algorithm_key)
        cat_accent = QColor(cat_cfg["accent"])

        # Row 1: Algorithm mode on left, Legend pills on right
        y1 = 10
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.setPen(QColor(COLORS["text_primary"]))
        p.drawText(QRectF(18, y1, 280, 18),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   f"{cat_cfg['icon']}  {self._algorithm_name}  •  {self._algorithm_complexity}")

        # Legend items depending on mode
        legends = []
        if self._mode == "bars":
            if "search" in self._algorithm_key:
                legends = [
                    ("Active Range", COLORS["range"]),
                    ("Midpoint", COLORS["mid"]),
                    ("Target Match", COLORS["found"]),
                    ("Eliminated", COLORS["dimmed"]),
                ]
            else:
                legends = [
                    ("Comparing", COLORS["comparing"]),
                    ("Swapping", COLORS["swapping"]),
                    ("Pivot", COLORS["pivot"]),
                    ("Sorted", COLORS["sorted"]),
                    ("Unsorted", COLORS["default_bar"]),
                ]
        elif self._mode == "graph":
            legends = [
                ("Start", COLORS["graph_start"]),
                ("Goal", COLORS["graph_goal"]),
                ("Visited", COLORS["graph_visited"]),
                ("Frontier", COLORS["graph_frontier"]),
                ("Optimal Path", COLORS["graph_path"]),
                ("Obstacle", COLORS["graph_wall"]),
            ]
        else:
            legends = [
                ("Active", COLORS["node_active"]),
                ("Inspecting", COLORS["node_highlight"]),
                ("New", COLORS["node_new"]),
                ("Deleted", COLORS["node_delete"]),
            ]

        # Draw legend pills from right to left
        x = self.width() - 20
        p.setFont(QFont("Segoe UI", 9))

        for text, color_hex in reversed(legends):
            pill_w = len(text) * 6 + 22
            x -= pill_w
            # Dot with crisp border
            col = QColor(color_hex)
            p.setPen(QPen(col.darker(110), 1))
            p.setBrush(col)
            p.drawEllipse(QPointF(x + 7, y1 + 9), 4, 4)
            # Label
            p.setPen(QColor(COLORS["text_secondary"]))
            p.drawText(QRectF(x + 15, y1, pill_w - 15, 18), Qt.AlignmentFlag.AlignVCenter, text)
            x -= 6

        # Row 2: Full-width live step operation banner
        y2 = 33
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        # Use active category color for the operation indicator
        p.setPen(cat_accent)
        desc = self._description or f"Ready to run {self._algorithm_name}. Click ▶ Play or ⏭ Step to start."
        p.drawText(QRectF(18, y2, self.width() - 36, 20),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   f"▶  {desc}")

        p.restore()

    # ── Empty / Welcome State ────────────────────────────────────

    def _paint_empty_card(self, p: QPainter) -> None:
        """Display a refined editorial card in warm neutrals instead of a dark void."""
        p.save()
        cx = self.width() / 2
        cy = self.height() / 2 + 15

        card_w = min(460.0, self.width() - 80)
        card_h = 180.0
        rect = QRectF(cx - card_w / 2, cy - card_h / 2, card_w, card_h)

        cat_cfg = get_category_config(self._algorithm_key)

        # Card container with soft paper neutral background
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)

        p.fillPath(path, QColor(COLORS["bg_tertiary"]))
        p.setPen(QPen(QColor(COLORS["border"]), 1.5))
        p.drawPath(path)

        # Category Icon
        p.setFont(QFont("Segoe UI", 24))
        p.drawText(QRectF(cx - 30, cy - card_h / 2 + 14, 60, 36),
                   Qt.AlignmentFlag.AlignCenter, cat_cfg["icon"])

        # Title
        p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        p.setPen(QColor(COLORS["text_primary"]))
        p.drawText(QRectF(rect.left() + 20, cy - 28, card_w - 40, 24),
                   Qt.AlignmentFlag.AlignCenter, f"{self._algorithm_name}")

        # Subtitle
        p.setFont(QFont("Segoe UI", 10))
        p.setPen(QColor(COLORS["text_muted"]))
        p.drawText(QRectF(rect.left() + 20, cy, card_w - 40, 20),
                   Qt.AlignmentFlag.AlignCenter, f"Category: {cat_cfg['name']}  •  Time: {self._algorithm_complexity}")

        # Hint callout
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        p.setPen(QColor(COLORS["button_primary"]))
        p.drawText(QRectF(rect.left() + 20, cy + 30, card_w - 40, 22),
                   Qt.AlignmentFlag.AlignCenter, "Click ▶ Play to run animation or ⏭ Step forward")

        p.restore()

    # ═══════════════════════════════════════════════════════════════
    #  1. BAR CHART (Sorting & Searching)
    # ═══════════════════════════════════════════════════════════════

    def _paint_bars(self, p: QPainter) -> None:
        arr: list = self._data if isinstance(self._data, list) else []
        n = len(arr)
        if n == 0:
            self._paint_empty_card(p)
            return

        margin_x = 40.0
        top_offset = 78.0
        bottom_offset = 50.0

        w = self.width() - 2 * margin_x
        h = self.height() - top_offset - bottom_offset

        gap = max(3.0, min(10.0, (w / n) * 0.18))
        bar_w = max(6.0, (w - (n - 1) * gap) / n)

        max_val = max((abs(v) for v in arr), default=1) or 1

        for i, val in enumerate(arr):
            x = margin_x + i * (bar_w + gap)
            bar_h = (abs(val) / max_val) * (h - 25)
            bar_h = max(bar_h, 6.0)
            y = self.height() - bottom_offset - bar_h

            color_key = self._highlights.get(i, "default_bar")
            color = _c(color_key)

            # Elegant light bar styling: subtle gradient with crisp outlines
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color)

            path = QPainterPath()
            corner_radius = min(bar_w / 3.0, 5.0)
            rect = QRectF(x, y, bar_w, bar_h)
            path.addRoundedRect(rect, corner_radius, corner_radius)
            p.fillPath(path, grad)

            # Highlight border on active elements
            if color_key in ("comparing", "swapping", "active", "pivot", "found", "target"):
                p.setPen(QPen(color.darker(120), 1.5))
                p.drawPath(path)
            else:
                p.setPen(QPen(color.darker(110), 1))
                p.drawPath(path)

            # Value label above bar
            if bar_w >= 14:
                # Dimmed text if eliminated in search
                if color_key == "dimmed":
                    p.setPen(QColor(COLORS["text_muted"]))
                else:
                    p.setPen(QColor(COLORS["text_primary"]))
                val_font_size = max(8, min(11, int(bar_w / 2.6)))
                p.setFont(QFont("Segoe UI", val_font_size, QFont.Weight.DemiBold))
                label_rect = QRectF(x - 4, y - 22, bar_w + 8, 18)
                p.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, str(val))

            # Index label below bar
            if bar_w >= 18 or n <= 25:
                p.setPen(QColor(COLORS["text_muted"]))
                p.setFont(QFont("Segoe UI", 8))
                idx_rect = QRectF(x - 4, self.height() - bottom_offset + 6, bar_w + 8, 14)
                p.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, str(i))

    # ═══════════════════════════════════════════════════════════════
    #  2. GRAPH & PATHFINDING (BFS, DFS, Dijkstra, A*)
    # ═══════════════════════════════════════════════════════════════

    def _paint_graph(self, p: QPainter) -> None:
        """Render 2D pathfinding grid on warm paper surface with clear boundaries."""
        info = self._data if isinstance(self._data, dict) else {}
        rows = info.get("rows", 7)
        cols = info.get("cols", 12)
        start = info.get("start", (0, 0))
        goal = info.get("goal", (rows - 1, cols - 1))
        walls = set(info.get("walls", []))

        self._grid_rows = rows
        self._grid_cols = cols

        top_margin = 78.0
        bottom_margin = 30.0
        side_margin = 30.0

        avail_w = self.width() - 2 * side_margin
        avail_h = self.height() - top_margin - bottom_margin

        cell_size = min(avail_w / cols, avail_h / rows, 52.0)
        self._grid_cell_size = cell_size

        total_grid_w = cols * cell_size
        total_grid_h = rows * cell_size

        offset_x = (self.width() - total_grid_w) / 2.0
        offset_y = top_margin + (avail_h - total_grid_h) / 2.0

        self._grid_offset_x = offset_x
        self._grid_offset_y = offset_y

        cell_gap = max(2.0, min(4.0, cell_size * 0.08))

        # Render all cells
        for r in range(rows):
            for c in range(cols):
                cx = offset_x + c * cell_size
                cy = offset_y + r * cell_size
                cell_rect = QRectF(cx + cell_gap / 2, cy + cell_gap / 2,
                                   cell_size - cell_gap, cell_size - cell_gap)

                node = (r, c)
                state = self._highlights.get(node)

                # Determine cell appearance according to user's semantic spec
                text_col = QColor(COLORS["text_primary"])
                if node == start:
                    bg_col = QColor(COLORS["graph_start"])  # Forest green
                    label = "S"
                    border_col = bg_col.darker(115)
                    text_col = QColor("#FFFFFF")
                elif node == goal:
                    bg_col = QColor(COLORS["graph_goal"])   # Coral red
                    label = "G"
                    border_col = bg_col.darker(115)
                    text_col = QColor("#FFFFFF")
                elif node in walls:
                    bg_col = QColor(COLORS["graph_wall"])   # Soft terracotta / neutral stone
                    label = "🧱" if cell_size >= 28 else ""
                    border_col = bg_col.darker(120)
                    text_col = QColor("#FFFFFF")
                elif state == "found":
                    bg_col = QColor(COLORS["graph_path"])   # Strong forest green
                    label = "●"
                    border_col = bg_col.darker(120)
                    text_col = QColor("#FFFFFF")
                elif state == "active":
                    bg_col = QColor(COLORS["comparing"])    # Warm amber
                    label = "▶"
                    border_col = bg_col.darker(115)
                    text_col = QColor("#FFFFFF")
                elif state == "mid":  # frontier
                    bg_col = QColor(COLORS["graph_frontier"]) # Warm amber
                    label = "○"
                    border_col = QColor(COLORS["comparing"])
                    text_col = QColor("#7A5408")
                elif state == "visited":
                    bg_col = QColor(COLORS["graph_visited"])  # Muted lavender
                    label = ""
                    border_col = bg_col.darker(115)
                    text_col = QColor("#4C3A6E")
                else:
                    # Clean white empty grid cell
                    bg_col = QColor(COLORS["graph_cell"])
                    label = ""
                    border_col = QColor(COLORS["graph_cell_border"])

                # Draw cell with soft rounded corners
                path = QPainterPath()
                corner_radius = min(cell_size * 0.14, 5.0)
                path.addRoundedRect(cell_rect, corner_radius, corner_radius)

                p.fillPath(path, bg_col)
                p.setPen(QPen(border_col, 1.2))
                p.drawPath(path)

                # Draw label
                if label:
                    p.setFont(QFont("Segoe UI", int(cell_size * 0.35), QFont.Weight.Bold))
                    p.setPen(text_col)
                    p.drawText(cell_rect, Qt.AlignmentFlag.AlignCenter, label)

        # Interactive hint at bottom
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(COLORS["text_muted"]))
        p.drawText(QRectF(0, self.height() - 22, self.width(), 18),
                   Qt.AlignmentFlag.AlignCenter,
                   "💡 Click any cell to toggle obstacle walls • Green: Start • Coral: Goal")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """Allow clicking on grid cells in graph mode to toggle walls."""
        if self._mode != "graph" or self._grid_cell_size <= 0:
            super().mousePressEvent(event)
            return

        pos = event.position()
        gx = pos.x() - self._grid_offset_x
        gy = pos.y() - self._grid_offset_y

        c = int(gx // self._grid_cell_size)
        r = int(gy // self._grid_cell_size)

        if 0 <= r < self._grid_rows and 0 <= c < self._grid_cols:
            self.wall_toggled.emit(r, c)
        super().mousePressEvent(event)

    # ═══════════════════════════════════════════════════════════════
    #  3. STACK (Vertical LIFO)
    # ═══════════════════════════════════════════════════════════════

    def _paint_stack(self, p: QPainter) -> None:
        arr: list = self._data if isinstance(self._data, list) else []
        n = len(arr)

        box_w = min(150.0, self.width() * 0.35)
        box_h = min(42.0, (self.height() - 120.0) / max(n, 1))
        cx = self.width() / 2.0
        base_y = self.height() - 65.0

        # Draw stack chamber borders in warm stone
        chamber_w = box_w + 24
        p.setPen(QPen(QColor(COLORS["border"]), 2))
        p.drawLine(int(cx - chamber_w / 2), int(base_y), int(cx + chamber_w / 2), int(base_y))
        p.drawLine(int(cx - chamber_w / 2), int(base_y), int(cx - chamber_w / 2), int(base_y - 240))
        p.drawLine(int(cx + chamber_w / 2), int(base_y), int(cx + chamber_w / 2), int(base_y - 240))

        # Bottom label
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p.setPen(QColor(COLORS["text_muted"]))
        p.drawText(QRectF(cx - 50, base_y + 8, 100, 16), Qt.AlignmentFlag.AlignCenter, "STACK BASE")

        if n == 0:
            p.setFont(QFont("Segoe UI", 11))
            p.setPen(QColor(COLORS["text_muted"]))
            p.drawText(QRectF(cx - 100, base_y - 80, 200, 30), Qt.AlignmentFlag.AlignCenter, "Empty Stack")
            return

        for i in range(n):
            y = base_y - (i + 1) * (box_h + 6)
            x = cx - box_w / 2.0

            color_key = self._highlights.get(i, "node_active")
            color = _c(color_key)

            rect = QRectF(x, y, box_w, box_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)

            grad = QLinearGradient(x, y, x + box_w, y)
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color)
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(115), 1.5))
            p.drawPath(path)

            # Value & Index
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

            p.setPen(QColor(COLORS["text_muted"]))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(QRectF(x - 32, y + box_h / 2 - 8, 26, 16), Qt.AlignmentFlag.AlignRight, f"[{i}]")

        # Top Pointer in Muted Teal
        top_y = base_y - n * (box_h + 6) - 10
        p.setPen(QColor(COLORS["accent_teal"]))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(QRectF(cx - box_w / 2, top_y - 18, box_w, 18),
                   Qt.AlignmentFlag.AlignCenter, "▲ TOP")

    # ═══════════════════════════════════════════════════════════════
    #  4. QUEUE (Horizontal FIFO)
    # ═══════════════════════════════════════════════════════════════

    def _paint_queue(self, p: QPainter) -> None:
        arr: list = self._data if isinstance(self._data, list) else []
        n = len(arr)

        if n == 0:
            p.setFont(QFont("Segoe UI", 12))
            p.setPen(QColor(COLORS["text_muted"]))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Queue is empty. Enqueue values to begin.")
            return

        box_w = min(80.0, (self.width() - 140) / max(n, 1))
        box_h = 54.0
        cy = self.height() / 2.0 + 10
        start_x = max(60.0, (self.width() - n * (box_w + 12)) / 2.0)

        for i in range(n):
            x = start_x + i * (box_w + 12)
            y = cy - box_h / 2.0

            color_key = self._highlights.get(i, "node_active")
            color = _c(color_key)

            rect = QRectF(x, y, box_w, box_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)

            grad = QLinearGradient(x, y, x, y + box_h)
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color)
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(115), 1.5))
            p.drawPath(path)

            # Value & Index
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

            p.setPen(QColor(COLORS["text_muted"]))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(x, y + box_h + 4, box_w, 14), Qt.AlignmentFlag.AlignCenter, f"idx: {i}")

            # Flow arrow to next
            if i < n - 1:
                arrow_x = x + box_w + 2
                p.setPen(QPen(QColor(COLORS["arrow"]), 2))
                p.drawLine(int(arrow_x), int(cy), int(arrow_x + 8), int(cy))
                p.drawLine(int(arrow_x + 5), int(cy - 4), int(arrow_x + 8), int(cy))
                p.drawLine(int(arrow_x + 5), int(cy + 4), int(arrow_x + 8), int(cy))

        # FRONT & REAR pointers
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.setPen(QColor(COLORS["accent_teal"]))
        p.drawText(QRectF(start_x - 10, cy - box_h / 2 - 24, box_w + 20, 18),
                   Qt.AlignmentFlag.AlignCenter, "▼ FRONT")

        if n > 1:
            p.setPen(QColor(COLORS["accent_purple"]))
            last_x = start_x + (n - 1) * (box_w + 12)
            p.drawText(QRectF(last_x - 10, cy - box_h / 2 - 24, box_w + 20, 18),
                       Qt.AlignmentFlag.AlignCenter, "▼ REAR")

    # ═══════════════════════════════════════════════════════════════
    #  5. LINKED LIST (Node-Pointer Chain)
    # ═══════════════════════════════════════════════════════════════

    def _paint_linked_list(self, p: QPainter) -> None:
        arr: list = self._data if isinstance(self._data, list) else []
        n = len(arr)

        if n == 0:
            p.setFont(QFont("Segoe UI", 12))
            p.setPen(QColor(COLORS["text_muted"]))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Linked List is empty (HEAD ──► NULL)")
            return

        node_w = min(72.0, (self.width() - 140) / max(n, 1) * 0.7)
        node_h = 44.0
        gap = min(40.0, (self.width() - 140 - n * node_w) / max(n, 1))
        cy = self.height() / 2.0 + 10
        start_x = max(50.0, (self.width() - n * (node_w + gap)) / 2.0)

        for i in range(n):
            x = start_x + i * (node_w + gap)
            y = cy - node_h / 2.0

            color_key = self._highlights.get(i, "node_active")
            color = _c(color_key)

            rect = QRectF(x, y, node_w, node_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)

            grad = QLinearGradient(x, y, x + node_w, y)
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color)
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(115), 1.5))
            p.drawPath(path)

            # Divider line between value and next pointer
            div_x = x + node_w * 0.68
            p.setPen(QPen(QColor(COLORS["border"]), 1.5))
            p.drawLine(int(div_x), int(y + 4), int(div_x), int(y + node_h - 4))

            # Value
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            val_rect = QRectF(x, y, node_w * 0.68, node_h)
            p.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

            # Pointer dot
            dot_cx = x + node_w * 0.84
            dot_cy = cy
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(dot_cx, dot_cy), 3.5, 3.5)

            # Connecting arrow to next node
            if i < n - 1:
                next_x = start_x + (i + 1) * (node_w + gap)
                p.setPen(QPen(QColor(COLORS["arrow"]), 2))
                p.drawLine(int(dot_cx + 4), int(cy), int(next_x - 3), int(cy))
                p.drawLine(int(next_x - 8), int(cy - 4), int(next_x - 3), int(cy))
                p.drawLine(int(next_x - 8), int(cy + 4), int(next_x - 3), int(cy))

        # NULL pointer box
        null_x = start_x + n * (node_w + gap)
        p.setPen(QColor(COLORS["text_muted"]))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(QRectF(null_x - 8, cy - 10, 48, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "NULL")

        # HEAD label
        p.setPen(QColor(COLORS["accent_teal"]))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(QRectF(start_x, cy - node_h / 2 - 24, node_w, 18),
                   Qt.AlignmentFlag.AlignCenter, "▼ HEAD")

    # ═══════════════════════════════════════════════════════════════
    #  6. BINARY SEARCH TREE (BST)
    # ═══════════════════════════════════════════════════════════════

    def _paint_bst(self, p: QPainter) -> None:
        root = self._data
        if root is None or not isinstance(root, dict):
            p.setFont(QFont("Segoe UI", 12))
            p.setPen(QColor(COLORS["text_muted"]))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Binary Search Tree is empty. Insert values to begin.")
            return

        positions: dict[int, tuple[float, float]] = {}
        edges: list[tuple[float, float, float, float]] = []
        node_radius = 22.0

        top_y = 75.0
        self._compute_tree_layout(root, positions, edges,
                                  self.width() / 2.0, top_y,
                                  self.width() / 4.2, 65.0)

        # Draw connecting branch edges in warm stone
        p.setPen(QPen(QColor(COLORS["border"]), 2))
        for x1, y1, x2, y2 in edges:
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw nodes with Muted Violet palette
        for val, (nx, ny) in positions.items():
            color_key = self._highlights.get(val, "node_tree")
            color = _c(color_key)

            # Node circle gradient
            grad = QLinearGradient(nx - node_radius, ny - node_radius,
                                   nx + node_radius, ny + node_radius)
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color)
            p.setBrush(grad)
            p.setPen(QPen(color.darker(115), 1.5))
            p.drawEllipse(QPointF(nx, ny), node_radius, node_radius)

            # Value label
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            p.drawText(QRectF(nx - node_radius, ny - node_radius,
                              node_radius * 2, node_radius * 2),
                       Qt.AlignmentFlag.AlignCenter, str(val))

    def _compute_tree_layout(
        self,
        node: dict | None,
        positions: dict,
        edges: list,
        x: float,
        y: float,
        x_offset: float,
        y_offset: float,
    ) -> None:
        if node is None or not isinstance(node, dict):
            return
        positions[node["value"]] = (x, y)
        if node.get("left") is not None:
            edges.append((x, y, x - x_offset, y + y_offset))
            self._compute_tree_layout(node["left"], positions, edges,
                                      x - x_offset, y + y_offset,
                                      x_offset * 0.52, y_offset)
        if node.get("right") is not None:
            edges.append((x, y, x + x_offset, y + y_offset))
            self._compute_tree_layout(node["right"], positions, edges,
                                      x + x_offset, y + y_offset,
                                      x_offset * 0.52, y_offset)
