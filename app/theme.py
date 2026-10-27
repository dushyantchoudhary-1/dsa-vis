"""
Warm, distinctive, premium light theme for DSA Lab.

Design Direction:
- Warm ivory (#F8F7F2) and clean white (#FFFFFF) foundation with soft warm gray (#F0EEE7) layers
- Subtle warm stone (#E4E0D6) separators and deep charcoal (#252822) typography
- Category-specific semantic color system:
    • Sorting: Terracotta & Coral (#D96C4F)
    • Searching: Marigold & Amber (#D49A24)
    • Graph Algorithms: Botanical Green (#39836B)
    • Trees & Hierarchy: Muted Violet (#8970B5)
    • Linear Data Structures: Muted Teal (#398F91)
    • AI Tutor: Restrained Plum (#8B668E)
    • Racing Arena: Warm Vermilion (#D95F42)
- Primary action accent: Forest Green (#34785B)
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────
# Category Semantic Configurations
# ─────────────────────────────────────────────────────────────────

CATEGORY_CONFIGS: dict[str, dict[str, str]] = {
    "sorting": {
        "accent": "#D96C4F",       # Terracotta & Coral
        "light":  "#FDF1EE",       # Soft warm tint
        "border": "#EBB3A4",
        "icon":   "📊",
        "name":   "Sorting",
    },
    "searching": {
        "accent": "#D49A24",       # Marigold & Amber
        "light":  "#FBF5E8",
        "border": "#ECCF90",
        "icon":   "🔍",
        "name":   "Searching",
    },
    "graph": {
        "accent": "#39836B",       # Botanical Green
        "light":  "#EEF6F3",
        "border": "#A3CCBF",
        "icon":   "🌐",
        "name":   "Graphs & Trees",
    },
    "tree": {
        "accent": "#8970B5",       # Muted Violet
        "light":  "#F5F2F9",
        "border": "#C8BADF",
        "icon":   "🌳",
        "name":   "Trees",
    },
    "data_structure": {
        "accent": "#398F91",       # Muted Teal
        "light":  "#EDF6F7",
        "border": "#A1CFD0",
        "icon":   "🧩",
        "name":   "Data Structures",
    },
    "ai": {
        "accent": "#8B668E",       # Restrained Plum
        "light":  "#F6F0F6",
        "border": "#CDAECF",
        "icon":   "🤖",
        "name":   "AI Tutor",
    },
    "racing": {
        "accent": "#D95F42",       # Warm Vermilion
        "light":  "#FDF0ED",
        "border": "#EEAA9A",
        "icon":   "🏁",
        "name":   "Racing Arena",
    },
}

ALGO_TO_CATEGORY: dict[str, str] = {
    # Sorting
    "bubble_sort":    "sorting",
    "selection_sort": "sorting",
    "insertion_sort": "sorting",
    "merge_sort":     "sorting",
    "quick_sort":     "sorting",
    "heap_sort":      "sorting",

    # Searching
    "linear_search":  "searching",
    "binary_search":  "searching",

    # Graphs
    "bfs_search":      "graph",
    "dfs_search":      "graph",
    "dijkstra_search": "graph",
    "astar_search":    "graph",

    # Trees
    "bst":            "tree",

    # Linear DS
    "stack":          "data_structure",
    "queue":          "data_structure",
    "linked_list":    "data_structure",
}


def get_category_for_key(key: str) -> str:
    """Return category key ('sorting', 'searching', 'graph', 'tree', 'data_structure')."""
    return ALGO_TO_CATEGORY.get(key, "sorting")


def get_category_config(cat_or_key: str) -> dict[str, str]:
    """Retrieve color and styling dictionary for a category or algorithm key."""
    cat = ALGO_TO_CATEGORY.get(cat_or_key, cat_or_key)
    return CATEGORY_CONFIGS.get(cat, CATEGORY_CONFIGS["sorting"])


# ─────────────────────────────────────────────────────────────────
# Global Colour Palette (Warm Light Foundation)
# ─────────────────────────────────────────────────────────────────

COLORS: dict[str, str] = {
    # Base interface surfaces
    "bg_canvas":       "#FFFFFF",  # Pure clean white for primary visualization canvas
    "bg_primary":      "#F8F7F2",  # Warm ivory application background
    "bg_secondary":    "#FFFFFF",  # Clean white panels, headers, inspector
    "bg_tertiary":     "#F0EEE7",  # Soft warm gray for wells, inputs, secondary badges

    # Surfaces & Interactive
    "surface":         "#FFFFFF",  # White interactive card surface
    "surface_hover":   "#F0EEE7",  # Soft hover state
    "surface_active":  "#E4E0D6",  # Warm stone active/pressed state

    # Borders & Dividers
    "border":          "#E4E0D6",  # Subtle warm stone separator
    "border_light":    "#EAE7DD",  # Soft fine border
    "border_focus":    "#34785B",  # Active focus ring (forest green)

    # Typography
    "text_primary":    "#252822",  # Deep charcoal primary text
    "text_secondary":  "#62665F",  # Muted gray for subtitles & secondary text
    "text_heading":    "#292B26",  # Deep charcoal for headings
    "text_muted":      "#62665F",  # Muted gray for secondary notes & hints
    "interactive":     "#34785B",  # Forest Green for links and interactive elements
    "code_text":       "#343A40",  # Dark slate for code and technical values

    # Brand & Action Accents
    "accent_cyan":     "#34785B",  # Forest Green (Primary Brand & Play Action)
    "accent_green":    "#34785B",  # Forest Green
    "accent_amber":    "#D49A24",  # Marigold / Amber
    "accent_terracotta":"#D96C4F", # Terracotta & Coral
    "accent_purple":   "#8970B5",  # Muted Violet
    "accent_teal":     "#398F91",  # Muted Teal
    "accent_plum":     "#8B668E",  # Restrained Plum
    "accent_vermilion":"#D95F42",  # Warm Vermilion

    # Algorithm States
    "default_bar":     "#A8A29E",  # Muted warm stone for unsorted bars
    "comparing":       "#D49A24",  # Marigold / Amber — active comparison
    "swapping":        "#D96C4F",  # Terracotta / Coral — active swap or write
    "sorted":          "#34785B",  # Forest green — verified sorted
    "active":          "#D96C4F",  # Active element
    "pivot":           "#8970B5",  # Muted Violet — partition pivot
    "found":           "#34785B",  # Forest green — target found
    "not_found":       "#D9534F",  # Coral red — search failed
    "dimmed":          "#DDD8CE",  # Soft paper-dimmed for eliminated search spaces

    # Range & Partition Indicators
    "range":           "#D49A24",  # Active search range
    "mid":             "#D49A24",  # Midpoint in binary search
    "low":             "#8970B5",  # Low pointer
    "high":            "#D96C4F",  # High pointer
    "target":          "#D49A24",  # Target search key

    # Graph & Grid States (Semantic Distinct Palette)
    "graph_start":     "#34785B",  # Forest green — Start node
    "graph_goal":      "#D9534F",  # Coral-red — Goal node
    "graph_wall":      "#8C7A6B",  # Muted warm stone / terracotta obstacle
    "graph_visited":   "#C5B4E3",  # Muted lavender — Explored node
    "graph_frontier":  "#FDE68A",  # Warm amber — Frontier / candidate
    "graph_path":      "#236548",  # Deep forest green — Optimal path
    "graph_cell":      "#FFFFFF",  # Open grid cell
    "graph_cell_border":"#E4E0D6", # Grid cell border

    # Data Structure Nodes
    "node_fill":       "#FFFFFF",  # Node default background
    "node_border":     "#398F91",  # Teal node border
    "node_active":     "#398F91",  # Active node
    "node_highlight":  "#D49A24",  # Inspecting node
    "node_new":        "#34785B",  # Inserted node
    "node_delete":     "#D9534F",  # Deleted node
    "node_tree":       "#8970B5",  # Tree node fill/accent
    "arrow":           "#77796F",  # Connectors & pointers

    # Buttons
    "button_primary":  "#34785B",  # Forest green primary action
    "button_hover":    "#2B644B",  # Deeper forest green
    "button_pressed":  "#23523D",

    # Scrollbars
    "scrollbar":       "#D1CBC0",  # Soft stone scroll thumb
    "scrollbar_hover": "#B0ACA2",

    # Status / Alerts
    "success":         "#34785B",  # Forest Green
    "warning":         "#D49A24",  # Amber
    "error":           "#D9534F",  # Coral Red
}


# ─────────────────────────────────────────────────────────────────
# Global Stylesheet (QSS)
# ─────────────────────────────────────────────────────────────────

def _qss() -> str:
    """Build the clean warm-light application stylesheet."""
    c = COLORS

    return f"""
    /* =============================================================
       GLOBAL WIDGETS
       ============================================================= */

    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Roboto', sans-serif;
        font-size: 13px;
        selection-background-color: #E4E0D6;
        selection-color: {c['text_primary']};
    }}

    QMainWindow {{
        background-color: {c['bg_primary']};
    }}

    /* =============================================================
       SCROLLBARS
       ============================================================= */

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 2px 0 2px 0;
    }}

    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        min-height: 28px;
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
        background: transparent;
        height: 8px;
        margin: 0 2px 0 2px;
    }}

    QScrollBar::handle:horizontal {{
        background: {c['scrollbar']};
        min-width: 28px;
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
        color: {c['text_primary']};
        padding: 0px;
    }}

    /* =============================================================
       BUTTONS
       ============================================================= */

    QPushButton {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
        font-size: 12px;
    }}

    QPushButton:hover {{
        background-color: {c['surface_hover']};
        border-color: {c['border']};
        color: {c['text_primary']};
    }}

    QPushButton:pressed {{
        background-color: {c['surface_active']};
    }}

    QPushButton:disabled {{
        background-color: {c['bg_tertiary']};
        border-color: {c['border']};
        color: {c['text_muted']};
    }}

    /* =============================================================
       LINE EDIT
       ============================================================= */

    QLineEdit {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    QLineEdit:hover {{
        border-color: {c['text_muted']};
    }}

    QLineEdit:focus {{
        border-color: {c['border_focus']};
        background-color: #FFFFFF;
    }}

    /* =============================================================
       SPIN BOX
       ============================================================= */

    QSpinBox {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 5px 8px;
        font-size: 12px;
    }}

    QSpinBox:focus {{
        border-color: {c['border_focus']};
    }}

    QSpinBox::up-button,
    QSpinBox::down-button {{
        background: {c['bg_tertiary']};
        border: none;
        width: 18px;
    }}

    QSpinBox::up-button:hover,
    QSpinBox::down-button:hover {{
        background: {c['surface_active']};
    }}

    /* =============================================================
       COMBO BOX
       ============================================================= */

    QComboBox {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 12px;
        min-height: 20px;
    }}

    QComboBox:hover {{
        border-color: {c['text_muted']};
    }}

    QComboBox:focus {{
        border-color: {c['border_focus']};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        selection-background-color: {c['surface_hover']};
        selection-color: {c['text_primary']};
        padding: 4px;
        outline: none;
    }}

    /* =============================================================
       SLIDER
       ============================================================= */

    QSlider::groove:horizontal {{
        background: {c['border']};
        height: 4px;
        border-radius: 2px;
    }}

    QSlider::sub-page:horizontal {{
        background: {c['accent_green']};
        border-radius: 2px;
    }}

    QSlider::add-page:horizontal {{
        background: {c['border']};
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        background: #FFFFFF;
        border: 2px solid {c['accent_green']};
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {c['accent_green']};
        border-color: {c['accent_green']};
    }}

    /* =============================================================
       TAB WIDGET (INSPECTOR)
       ============================================================= */

    QTabWidget::pane {{
        border: 1px solid {c['border']};
        background-color: {c['surface']};
        border-radius: 0px 0px 8px 8px;
    }}

    QTabBar::tab {{
        background: {c['bg_tertiary']};
        color: {c['text_muted']};
        border: 1px solid {c['border']};
        border-bottom: none;
        padding: 6px 11px;
        font-weight: 600;
        font-size: 11px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}

    QTabBar::tab:hover {{
        background: {c['surface_hover']};
        color: {c['text_secondary']};
    }}

    QTabBar::tab:selected {{
        background: {c['surface']};
        color: {c['text_primary']};
        border-bottom: 2px solid {c['accent_green']};
    }}

    /* =============================================================
       TREE / EXPLORER
       ============================================================= */

    QTreeWidget {{
        background-color: transparent;
        border: none;
        outline: none;
    }}

    QTreeWidget::item {{
        padding: 5px 6px;
        border-radius: 6px;
        margin: 1px 0px;
        color: {c['text_primary']};
    }}

    QTreeWidget::item:hover {{
        background-color: {c['surface_hover']};
    }}

    QTreeWidget::item:selected {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        font-weight: 600;
    }}

    QTreeWidget::branch {{
        background: transparent;
    }}

    /* =============================================================
       SPLITTER
       ============================================================= */

    QSplitter::handle {{
        background-color: {c['border']};
    }}

    QSplitter::handle:horizontal {{
        width: 1px;
    }}

    QSplitter::handle:vertical {{
        height: 1px;
    }}

    /* =============================================================
       CODE / TEXT AREAS
       ============================================================= */

    QTextEdit,
    QPlainTextEdit {{
        background-color: {c['surface']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px;
        font-family: 'Cascadia Code', 'Consolas', 'JetBrains Mono', monospace;
        font-size: 12px;
    }}

    QTextBrowser {{
        background-color: #FFFFFF;
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Roboto', sans-serif;
        font-size: 12px;
    }}

    QTextEdit:focus,
    QPlainTextEdit:focus,
    QTextBrowser:focus {{
        border-color: {c['border_focus']};
    }}

    /* =============================================================
       TOOLTIP
       ============================================================= */

    QToolTip {{
        background-color: {c['text_primary']};
        color: #FFFFFF;
        border: 1px solid {c['text_secondary']};
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 11px;
    }}
    """


# ─────────────────────────────────────────────────────────────────
# Apply theme
# ─────────────────────────────────────────────────────────────────

def apply_theme(app) -> None:
    """Apply the warm-light theme to the QApplication."""
    app.setStyleSheet(_qss())
