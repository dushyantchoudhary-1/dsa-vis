"""
DSA Visualizer — entry point.

Usage:
    python main.py
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.main_window import MainWindow
from app.theme import apply_theme


def main() -> None:
    app = QApplication(sys.argv)

    # Default font with Windows / cross-platform fallbacks
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Dark theme
    apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
