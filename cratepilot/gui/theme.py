"""UI theming helpers."""


def dark_minimal_stylesheet() -> str:
    return """
        QMainWindow, QWidget { background: #121316; color: #E8EAF0; font-size: 13px; }
        QLineEdit, QTableWidget, QDialog, QTextEdit { background: #1A1D23; border: 1px solid #2B313A; border-radius: 8px; color: #F5F7FC; }
        QPushButton { background: #2A2F38; border: 1px solid #343B46; border-radius: 8px; padding: 6px 12px; color: #F5F7FC; }
        QPushButton:hover { background: #343B46; }
        QPushButton:disabled { color: #818897; background: #1A1D23; }
        QHeaderView::section { background: #1A1D23; color: #AEB7C7; border: none; padding: 6px; }
        QTableWidget::item:selected { background: #3A7AFE; color: white; }
    """
