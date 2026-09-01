
"""
Clean dark theme for the DSA Visualizer.

Theme:
- Charcoal / graphite backgrounds
- Warm orange as the main accent
- Muted blue as a secondary accent
- Softer green / red / yellow state colours
- Minimal neon / gradient styling
"""

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────
# Colour Palette
# ─────────────────────────────────────────────────────────────────

COLORS: dict[str, str] = {

    # Backgrounds
    "bg_primary":      "#17191c",
    "bg_secondary":    "#1f2226",
    "bg_tertiary":     "#292d32",

    # Panels / surfaces
    "surface":         "#25292e",
    "surface_hover":   "#30353b",

    # Borders
    "border":          "#383e45",
    "border_light":    "#4a5159",

    # Text
    "text_primary":    "#eeeeee",
    "text_secondary":  "#b4bac2",
    "text_muted":      "#7f8790",

    # Main accents
    "accent_cyan":     "#e09a45",
    "accent_purple":   "#6f8fb8",
    "accent_pink":     "#c97878",
    "accent_blue":     "#6f8fb8",

    # Algorithm states
    "default_bar":     "#68778a",
    "comparing":       "#d6a84f",
    "swapping":        "#c96b67",
    "sorted":          "#6fa477",

    "active":          "#e09a45",
    "pivot":           "#c97878",
    "found":           "#6fa477",
    "not_found":       "#c96b67",

    "range":           "#6f8fb8",
    "mid":             "#d6a84f",
    "low":             "#6f8fb8",
    "high":            "#c97878",
    "target":          "#d6a84f",

    # Data structure nodes
    "node_fill":       "#596879",
    "node_active":     "#e09a45",
    "node_highlight":  "#d6a84f",
    "node_new":        "#6fa477",
    "node_delete":     "#c96b67",

    "arrow":           "#8f969e",

    # UI elements
    "button_primary":  "#b87532",
    "button_hover":    "#cc8840",
    "button_pressed":  "#965f29",

    "scrollbar":       "#454b52",
    "scrollbar_hover": "#5a626b",

    # Status colours
    "success":         "#6fa477",
    "warning":         "#d6a84f",
    "error":           "#c96b67",
}


# ─────────────────────────────────────────────────────────────────
# QSS
# ─────────────────────────────────────────────────────────────────

def _qss() -> str:
    """Build the application stylesheet."""

    c = COLORS

    return f"""
    /* =============================================================
       GLOBAL
       ============================================================= */

    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {c['bg_primary']};
    }}


    /* =============================================================
       SCROLLBARS
       ============================================================= */

    QScrollBar:vertical {{
        background: {c['bg_secondary']};
        width: 9px;
        border: none;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        min-height: 35px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_hover']};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: {c['bg_secondary']};
        height: 9px;
        border: none;
    }}

    QScrollBar::handle:horizontal {{
        background: {c['scrollbar']};
        min-width: 35px;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {c['scrollbar_hover']};
    }}

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}


    /* =============================================================
       LABELS
       ============================================================= */

    QLabel {{
        background: transparent;
        padding: 0px;
    }}


    /* =============================================================
       BUTTONS
       ============================================================= */

    QPushButton {{
        background-color: {c['button_primary']};
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
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


    /* =============================================================
       LINE EDIT
       ============================================================= */

    QLineEdit {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px 11px;
        selection-background-color: {c['accent_cyan']};
        selection-color: #ffffff;
    }}

    QLineEdit:hover {{
        border-color: {c['border_light']};
    }}

    QLineEdit:focus {{
        border-color: {c['accent_cyan']};
    }}


    /* =============================================================
       SPIN BOX
       ============================================================= */

    QSpinBox {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 5px 8px;
    }}

    QSpinBox:focus {{
        border-color: {c['accent_cyan']};
    }}

    QSpinBox::up-button,
    QSpinBox::down-button {{
        background: {c['surface']};
        border: none;
        width: 20px;
    }}

    QSpinBox::up-button:hover,
    QSpinBox::down-button:hover {{
        background: {c['surface_hover']};
    }}


    /* =============================================================
       SLIDER
       ============================================================= */

    QSlider::groove:horizontal {{
        background: {c['bg_tertiary']};
        height: 5px;
        border-radius: 2px;
    }}

    QSlider::sub-page:horizontal {{
        background: {c['accent_cyan']};
        border-radius: 2px;
    }}

    QSlider::add-page:horizontal {{
        background: {c['bg_tertiary']};
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        background: {c['accent_cyan']};
        width: 15px;
        height: 15px;
        margin: -5px 0;
        border-radius: 7px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {c['button_hover']};
    }}


    /* =============================================================
       TREE / SIDEBAR
       ============================================================= */

    QTreeWidget {{
        background-color: {c['bg_secondary']};
        border: none;
        outline: none;
    }}

    QTreeWidget::item {{
        padding: 6px 8px;
        border-radius: 5px;
        margin: 1px 4px;
    }}

    QTreeWidget::item:hover {{
        background-color: {c['surface']};
    }}

    QTreeWidget::item:selected {{
        background-color: {c['surface_hover']};
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


    /* =============================================================
       GROUP BOX
       ============================================================= */

    QGroupBox {{
        background-color: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 7px;
        margin-top: 12px;
        padding-top: 22px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 3px 10px;
        color: {c['accent_cyan']};
    }}


    /* =============================================================
       SPLITTER
       ============================================================= */

    QSplitter::handle {{
        background-color: {c['border']};
    }}

    QSplitter::handle:horizontal {{
        width: 2px;
    }}

    QSplitter::handle:vertical {{
        height: 2px;
    }}


    /* =============================================================
       CODE / TEXT AREAS
       ============================================================= */

    QTextEdit,
    QPlainTextEdit {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px;

        font-family: 'Consolas',
                     'JetBrains Mono',
                     'Fira Code',
                     monospace;

        font-size: 12px;
    }}

    QTextEdit:focus,
    QPlainTextEdit:focus {{
        border-color: {c['accent_cyan']};
    }}


    /* =============================================================
       FRAME PANELS
       ============================================================= */

    QFrame[frameShape="4"] {{
        color: {c['border']};
    }}


    /* =============================================================
       STACKED WIDGET
       ============================================================= */

    QStackedWidget {{
        background: transparent;
    }}


    /* =============================================================
       TOOLTIP
       ============================================================= */

    QToolTip {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border_light']};
        padding: 6px 9px;
    }}
    """


# ─────────────────────────────────────────────────────────────────
# Apply theme
# ─────────────────────────────────────────────────────────────────

def apply_theme(app) -> None:
    """Apply the theme to the QApplication."""

    app.setStyleSheet(_qss())

