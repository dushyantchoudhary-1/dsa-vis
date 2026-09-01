"""
Visualisation canvas — renders algorithm state using QPainter.

Supports five render modes controlled by ``Step.visualization_type``:
  bars         — vertical bar-chart (sorting / searching)
  stack        — vertical stack of boxes
  queue        — horizontal row of boxes
  linked_list  — node-arrow chain
  bst          — tree layout with circles and edges
"""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from app.theme import COLORS


def _c(key: str) -> QColor:
    """Shortcut: look up a COLORS key and return a QColor."""
    return QColor(COLORS.get(key, COLORS["default_bar"]))


class VisualizationCanvas(QWidget):
    """Custom-painted widget that renders the current algorithm step."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self._data: Any = None
        self._highlights: dict = {}
        self._mode: str = "bars"
        self._description: str = ""

    # ── Public API ───────────────────────────────────────────────

    def update_step(self, step) -> None:
        """Accept a ``Step`` and trigger a repaint."""
        self._data = step.data
        self._highlights = step.highlights
        self._mode = getattr(step, "visualization_type", "bars")
        self._description = step.description
        self.update()

    def clear_canvas(self) -> None:
        self._data = None
        self._highlights = {}
        self._description = ""
        self.update()

    # ── Paint dispatch ───────────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg = QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0, QColor(COLORS["bg_primary"]))
        bg.setColorAt(1, QColor(COLORS["bg_secondary"]))
        painter.fillRect(self.rect(), bg)

        if self._data is None or (isinstance(self._data, list) and len(self._data) == 0):
            self._paint_empty(painter)
            painter.end()
            return

        dispatch = {
            "bars":        self._paint_bars,
            "stack":       self._paint_stack,
            "queue":       self._paint_queue,
            "linked_list": self._paint_linked_list,
            "bst":         self._paint_bst,
        }
        fn = dispatch.get(self._mode, self._paint_bars)
        fn(painter)
        painter.end()

    # ── Empty state ──────────────────────────────────────────────

    def _paint_empty(self, p: QPainter) -> None:
        p.setPen(QColor(COLORS["text_muted"]))
        p.setFont(QFont("Helvetica Neue", 14))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Select an algorithm and press ▶ Play")

    # ═══════════════════════════════════════════════════════════════
    #  BAR CHART (sorting / searching)
    # ═══════════════════════════════════════════════════════════════

    def _paint_bars(self, p: QPainter) -> None:
        arr: list = self._data
        n = len(arr)
        if n == 0:
            self._paint_empty(p)
            return

        margin = 50
        w = self.width() - 2 * margin
        h = self.height() - 2 * margin - 20  # extra space for value labels
        gap = max(2, min(6, w / n * 0.15))
        bar_w = max(4, (w - (n - 1) * gap) / n)

        max_val = max(abs(v) for v in arr) or 1

        for i, val in enumerate(arr):
            x = margin + i * (bar_w + gap)
            bar_h = (abs(val) / max_val) * h
            y = self.height() - margin - bar_h

            color_key = self._highlights.get(i, "default_bar")
            color = _c(color_key)

            # Gradient fill
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0, color.lighter(140))
            grad.setColorAt(1, color)

            path = QPainterPath()
            radius = min(bar_w / 3, 8)
            rect = QRectF(x, y, bar_w, bar_h)
            path.addRoundedRect(rect, radius, radius)
            p.fillPath(path, grad)

            # Subtle border
            p.setPen(QPen(color.darker(130), 1))
            p.drawPath(path)

            # Value label
            if bar_w > 14:
                p.setPen(QColor(COLORS["text_primary"]))
                label_font = QFont("Helvetica Neue", max(8, min(11, int(bar_w / 2.5))))
                p.setFont(label_font)
                label_rect = QRectF(x, y - 20, bar_w, 18)
                p.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, str(val))

            # Index label
            if bar_w > 20:
                p.setPen(QColor(COLORS["text_muted"]))
                idx_font = QFont("Helvetica Neue", 8)
                p.setFont(idx_font)
                idx_rect = QRectF(x, self.height() - margin + 4, bar_w, 14)
                p.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, str(i))

    # ═══════════════════════════════════════════════════════════════
    #  STACK
    # ═══════════════════════════════════════════════════════════════

    def _paint_stack(self, p: QPainter) -> None:
        arr: list = self._data
        n = len(arr)
        if n == 0:
            self._paint_empty(p)
            return

        box_w = min(120, self.width() * 0.3)
        box_h = min(40, (self.height() - 80) / max(n, 1))
        cx = self.width() / 2

        # Draw from bottom (index 0) to top (index n-1)
        for i in range(n):
            y = self.height() - 60 - (i + 1) * (box_h + 4)
            x = cx - box_w / 2

            color_key = self._highlights.get(i, "node_fill")
            color = _c(color_key)

            rect = QRectF(x, y, box_w, box_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 8, 8)

            grad = QLinearGradient(x, y, x + box_w, y)
            grad.setColorAt(0, color)
            grad.setColorAt(1, color.lighter(125))
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(120), 1.5))
            p.drawPath(path)

            # Value
            p.setPen(QColor("#ffffff"))
            p.setFont(QFont("Helvetica Neue", 13, QFont.Weight.Bold))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

        # "TOP" label
        if n > 0:
            top_y = self.height() - 60 - n * (box_h + 4) - 4
            p.setPen(QColor(COLORS["accent_cyan"]))
            p.setFont(QFont("Helvetica Neue", 10, QFont.Weight.Bold))
            p.drawText(QRectF(cx - box_w / 2, top_y - 18, box_w, 16),
                       Qt.AlignmentFlag.AlignCenter, "▲ TOP")

        # Base line
        base_y = self.height() - 56
        p.setPen(QPen(QColor(COLORS["border_light"]), 2))
        p.drawLine(int(cx - box_w / 2 - 10), int(base_y),
                    int(cx + box_w / 2 + 10), int(base_y))

    # ═══════════════════════════════════════════════════════════════
    #  QUEUE
    # ═══════════════════════════════════════════════════════════════

    def _paint_queue(self, p: QPainter) -> None:
        arr: list = self._data
        n = len(arr)
        if n == 0:
            self._paint_empty(p)
            return

        box_w = min(70, (self.width() - 100) / max(n, 1))
        box_h = 50
        cy = self.height() / 2
        start_x = max(40, (self.width() - n * (box_w + 8)) / 2)

        for i in range(n):
            x = start_x + i * (box_w + 8)
            y = cy - box_h / 2

            color_key = self._highlights.get(i, "node_fill")
            color = _c(color_key)

            rect = QRectF(x, y, box_w, box_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 8, 8)

            grad = QLinearGradient(x, y, x, y + box_h)
            grad.setColorAt(0, color.lighter(130))
            grad.setColorAt(1, color)
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(120), 1.5))
            p.drawPath(path)

            # Value
            p.setPen(QColor("#ffffff"))
            p.setFont(QFont("Helvetica Neue", 13, QFont.Weight.Bold))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

            # Arrow to next
            if i < n - 1:
                arrow_x = x + box_w + 1
                p.setPen(QPen(QColor(COLORS["arrow"]), 2))
                p.drawLine(int(arrow_x), int(cy), int(arrow_x + 6), int(cy))
                # Arrowhead
                p.drawLine(int(arrow_x + 4), int(cy - 4), int(arrow_x + 6), int(cy))
                p.drawLine(int(arrow_x + 4), int(cy + 4), int(arrow_x + 6), int(cy))

        # Labels
        p.setFont(QFont("Helvetica Neue", 10, QFont.Weight.Bold))
        p.setPen(QColor(COLORS["accent_cyan"]))
        label_y = cy + box_h / 2 + 20
        p.drawText(QRectF(start_x, label_y, box_w, 16),
                   Qt.AlignmentFlag.AlignCenter, "FRONT")
        if n > 1:
            p.setPen(QColor(COLORS["accent_purple"]))
            p.drawText(QRectF(start_x + (n - 1) * (box_w + 8), label_y, box_w, 16),
                       Qt.AlignmentFlag.AlignCenter, "REAR")

    # ═══════════════════════════════════════════════════════════════
    #  LINKED LIST
    # ═══════════════════════════════════════════════════════════════

    def _paint_linked_list(self, p: QPainter) -> None:
        arr: list = self._data
        n = len(arr)
        if n == 0:
            self._paint_empty(p)
            return

        node_w = min(64, (self.width() - 100) / max(n, 1) * 0.65)
        node_h = 40
        gap = min(40, (self.width() - 100 - n * node_w) / max(n, 1))
        cy = self.height() / 2
        start_x = max(30, (self.width() - n * (node_w + gap)) / 2)

        for i in range(n):
            x = start_x + i * (node_w + gap)
            y = cy - node_h / 2

            color_key = self._highlights.get(i, "node_fill")
            color = _c(color_key)

            # Node box (split: value | pointer)
            rect = QRectF(x, y, node_w, node_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)

            grad = QLinearGradient(x, y, x + node_w, y)
            grad.setColorAt(0, color)
            grad.setColorAt(1, color.lighter(120))
            p.fillPath(path, grad)

            p.setPen(QPen(color.darker(120), 1.5))
            p.drawPath(path)

            # Divider line
            div_x = x + node_w * 0.7
            p.drawLine(int(div_x), int(y + 4), int(div_x), int(y + node_h - 4))

            # Value
            p.setPen(QColor("#ffffff"))
            p.setFont(QFont("Helvetica Neue", 12, QFont.Weight.Bold))
            val_rect = QRectF(x, y, node_w * 0.7, node_h)
            p.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, str(arr[i]))

            # Pointer dot
            dot_cx = x + node_w * 0.85
            dot_cy = cy
            p.setBrush(QColor(COLORS["accent_cyan"]))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(dot_cx, dot_cy), 3, 3)

            # Arrow to next node
            if i < n - 1:
                next_x = start_x + (i + 1) * (node_w + gap)
                p.setPen(QPen(QColor(COLORS["arrow"]), 2))
                p.drawLine(int(dot_cx + 3), int(cy), int(next_x - 2), int(cy))
                # Arrowhead
                p.drawLine(int(next_x - 8), int(cy - 5), int(next_x - 2), int(cy))
                p.drawLine(int(next_x - 8), int(cy + 5), int(next_x - 2), int(cy))

        # NULL terminator
        null_x = start_x + n * (node_w + gap)
        p.setPen(QColor(COLORS["text_muted"]))
        p.setFont(QFont("Helvetica Neue", 10))
        p.drawText(QRectF(null_x - 10, cy - 8, 40, 16),
                   Qt.AlignmentFlag.AlignLeft, "null")

        # HEAD label
        p.setPen(QColor(COLORS["accent_cyan"]))
        p.setFont(QFont("Helvetica Neue", 10, QFont.Weight.Bold))
        p.drawText(QRectF(start_x, cy - node_h / 2 - 22, node_w, 16),
                   Qt.AlignmentFlag.AlignCenter, "HEAD")

    # ═══════════════════════════════════════════════════════════════
    #  BST
    # ═══════════════════════════════════════════════════════════════

    def _paint_bst(self, p: QPainter) -> None:
        root = self._data
        if root is None:
            self._paint_empty(p)
            return

        # Compute positions
        positions: dict[int, tuple[float, float]] = {}
        edges: list[tuple[float, float, float, float]] = []
        node_radius = 22

        self._compute_tree_layout(root, positions, edges,
                                  self.width() / 2, 50,
                                  self.width() / 4.5, 65)

        # Draw edges first
        p.setPen(QPen(QColor(COLORS["border_light"]), 2))
        for x1, y1, x2, y2 in edges:
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw nodes
        for value, (nx, ny) in positions.items():
            color_key = self._highlights.get(value, "node_fill")
            color = _c(color_key)

            # Glow effect for highlighted nodes
            if color_key in ("node_active", "found", "node_new", "node_delete", "node_highlight"):
                glow = QColor(color)
                glow.setAlpha(60)
                p.setBrush(glow)
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(nx, ny), node_radius + 6, node_radius + 6)

            # Node circle
            grad = QLinearGradient(nx - node_radius, ny - node_radius,
                                   nx + node_radius, ny + node_radius)
            grad.setColorAt(0, color.lighter(130))
            grad.setColorAt(1, color)
            p.setBrush(grad)
            p.setPen(QPen(color.darker(120), 2))
            p.drawEllipse(QPointF(nx, ny), node_radius, node_radius)

            # Value text
            p.setPen(QColor("#ffffff"))
            p.setFont(QFont("Helvetica Neue", 12, QFont.Weight.Bold))
            p.drawText(QRectF(nx - node_radius, ny - node_radius,
                              node_radius * 2, node_radius * 2),
                       Qt.AlignmentFlag.AlignCenter, str(value))

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
        if node is None:
            return
        positions[node["value"]] = (x, y)
        if node["left"] is not None:
            edges.append((x, y, x - x_offset, y + y_offset))
            self._compute_tree_layout(node["left"], positions, edges,
                                      x - x_offset, y + y_offset,
                                      x_offset / 2, y_offset)
        if node["right"] is not None:
            edges.append((x, y, x + x_offset, y + y_offset))
            self._compute_tree_layout(node["right"], positions, edges,
                                      x + x_offset, y + y_offset,
                                      x_offset / 2, y_offset)
