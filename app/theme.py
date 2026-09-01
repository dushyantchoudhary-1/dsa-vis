"""
Dark-mode theme configuration and QSS stylesheet for the DSA Visualizer.

Colour palette inspired by modern code-editor dark themes with
cyan / purple / indigo accents and amber/red/green state colours.
"""

from __future__ import annotations

# ── Colour Palette ──────────────────────────────────────────────────
COLORS: dict[str, str] = {
    # Backgrounds
    "bg_primary":      "#080c24",
    "bg_secondary":    "#0f1535",
    "bg_tertiary":     "#182048",
    "surface":         "#1a2150",
    "surface_hover":   "#222a5c",
    "border":          "#2a3266",
    "border_light":    "#3d4578",

    # Text
    "text_primary":    "#e8ecf4",
    "text_secondary":  "#a0aec0",
    "text_muted":      "#718096",

    # Accents
    "accent_cyan":     "#00d4ff",
    "accent_purple":   "#8b5cf6",
    "accent_pink":     "#ec4899",
    "accent_blue":     "#3b82f6",

    # Algorithm state colours
    "default_bar":     "#6366f1",
    "comparing":       "#f59e0b",
    "swapping":        "#ef4444",
    "sorted":          "#10b981",
    "active":          "#00d4ff",
    "pivot":           "#ec4899",
    "found":           "#10b981",
    "not_found":       "#ef4444",
    "range":           "#8b5cf6",
    "mid":             "#f59e0b",
    "low":             "#3b82f6",
    "high":            "#ec4899",
    "target":          "#fbbf24",

    # Data-structure node colours
    "node_fill":       "#6366f1",
    "node_active":     "#00d4ff",
    "node_highlight":  "#f59e0b",
    "node_new":        "#10b981",
    "node_delete":     "#ef4444",
    "arrow":           "#a0aec0",

    # UI elements
    "button_primary":  "#6366f1",
    "button_hover":    "#7c7ff7",
    "button_pressed":  "#4f46e5",
    "scrollbar":       "#2a3266",
    "scrollbar_hover": "#3d4578",
    "success":         "#10b981",
    "warning":         "#f59e0b",
    "error":           "#ef4444",
}


def _qss() -> str:
    """Build the full QSS stylesheet string."""
    c = COLORS
    return f"""
    /* ═══════ Global ═══════ */
    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Helvetica Neue', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{
        background-color: {c['bg_primary']};
    }}

    /* ═══════ Scroll-bars ═══════ */
    QScrollBar:vertical {{
        background: {c['bg_secondary']};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_hover']};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {c['bg_secondary']};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['scrollbar']};
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {c['scrollbar_hover']};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ═══════ Labels ═══════ */
    QLabel {{
        background: transparent;
        padding: 0;
    }}

    /* ═══════ Buttons ═══════ */
    QPushButton {{
        background-color: {c['button_primary']};
        color: {c['text_primary']};
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {c['button_hover']};
    }}
    QPushButton:pressed {{
        background-color: {c['button_pressed']};
    }}
    QPushButton:disabled {{
        background-color: {c['bg_tertiary']};
        color: {c['text_muted']};
    }}

    /* ═══════ Line-edit ═══════ */
    QLineEdit {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: {c['accent_purple']};
    }}
    QLineEdit:focus {{
        border-color: {c['accent_cyan']};
    }}

    /* ═══════ Spin-box ═══════ */
    QSpinBox {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    QSpinBox:focus {{
        border-color: {c['accent_cyan']};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background: {c['surface']};
        border: none;
        width: 20px;
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background: {c['surface_hover']};
    }}

    /* ═══════ Slider ═══════ */
    QSlider::groove:horizontal {{
        background: {c['bg_tertiary']};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {c['accent_cyan']};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background: #33ddff;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {c['accent_purple']}, stop:1 {c['accent_cyan']});
        border-radius: 3px;
    }}

    /* ═══════ Tree widget (sidebar) ═══════ */
    QTreeWidget {{
        background-color: {c['bg_secondary']};
        border: none;
        outline: none;
    }}
    QTreeWidget::item {{
        padding: 6px 8px;
        border-radius: 6px;
        margin: 1px 4px;
    }}
    QTreeWidget::item:hover {{
        background-color: {c['surface']};
    }}
    QTreeWidget::item:selected {{
        background-color: {c['surface']};
        color: {c['accent_cyan']};
    }}
    QTreeWidget::branch {{
        background: transparent;
    }}
    QHeaderView::section {{
        background: {c['bg_secondary']};
        color: {c['text_secondary']};
        border: none;
        padding: 8px;
        font-weight: 600;
    }}

    /* ═══════ Group-box ═══════ */
    QGroupBox {{
        background-color: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        margin-top: 12px;
        padding-top: 24px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        color: {c['accent_cyan']};
    }}

    /* ═══════ Splitter ═══════ */
    QSplitter::handle {{
        background-color: {c['border']};
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}

    /* ═══════ Text-edit / code view ═══════ */
    QTextEdit, QPlainTextEdit {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 12px;
    }}

    /* ═══════ Frame panels ═══════ */
    QFrame[frameShape="4"] {{
        color: {c['border']};
    }}

    /* ═══════ Stacked widget ═══════ */
    QStackedWidget {{
        background: transparent;
    }}

    /* ═══════ Tool-tip ═══════ */
    QToolTip {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    """


def apply_theme(app) -> None:
    """Apply the dark theme to a QApplication instance."""
    app.setStyleSheet(_qss())
