"""Preview: theme engine with system-aware light/dark mode and persisted manual toggle."""

from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QGuiApplication

from cratepilot.gui.design_tokens import DARK_TOKENS, LIGHT_TOKENS, ThemeTokens

THEME_AUTO = "auto"
THEME_LIGHT = "light"
THEME_DARK = "dark"


def detect_system_theme() -> str:
    hints = QGuiApplication.styleHints()
    return THEME_DARK if hints.colorScheme() == Qt.ColorScheme.Dark else THEME_LIGHT


def effective_theme(preference: str) -> str:
    if preference == THEME_AUTO:
        return detect_system_theme()
    return THEME_DARK if preference == THEME_DARK else THEME_LIGHT


def toggle_icon_for(theme_name: str) -> str:
    return "☀  Light" if theme_name == THEME_DARK else "🌙  Dark"


def tokens_for(theme_name: str) -> ThemeTokens:
    return DARK_TOKENS if theme_name == THEME_DARK else LIGHT_TOKENS


def app_stylesheet(theme_name: str) -> str:
    t = tokens_for(theme_name)
    return f"""
        QMainWindow, QWidget {{
            background: {t.bg_primary};
            color: {t.text_primary};
            font-family: "Helvetica Neue", "Arial";
            font-size: {t.font_body}px;
        }}
        QWidget#toolbar {{
            background: {t.bg_surface};
            border: 1px solid {t.border};
            border-radius: {t.radius_lg}px;
            min-height: 52px;
            max-height: 52px;
            padding: 0 {t.spacing_sm}px;
        }}
        QWidget#panel {{
            background: {t.bg_surface};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            padding: {t.spacing_md}px;
        }}
        QLineEdit {{
            min-height: 36px;
            max-height: 36px;
            border: 1px solid {t.border};
            border-radius: {t.radius_sm}px;
            background: {t.bg_surface if theme_name == THEME_LIGHT else t.bg_elevated};
            color: {t.text_primary};
            padding: 0 {t.spacing_sm}px;
        }}
        QLineEdit:focus {{ border: 2px solid {t.accent}; }}
        QLineEdit[role="search"] {{
            min-width: 280px;
            font-size: {t.font_subhead}px;
        }}
        QLineEdit::placeholder {{ color: {t.text_tertiary}; }}
        QPushButton {{
            min-height: 36px;
            max-height: 36px;
            padding: 0 {t.spacing_md}px;
            border-radius: {t.radius_md}px;
            border: 1px solid {t.border};
            color: {t.text_primary};
            background: transparent;
            font-size: {t.font_body}px;
            font-weight: 500;
        }}
        QPushButton:hover {{ background: {t.bg_elevated}; }}
        QPushButton:pressed {{ padding-top: 1px; padding-left: {t.spacing_md - 1}px; }}
        QPushButton[variant="primary"] {{
            background: {t.accent};
            color: #FFFFFF;
            border: none;
        }}
        QPushButton[variant="ghost"] {{
            border: none;
            color: {t.text_secondary};
            padding: 0 {t.spacing_sm}px;
        }}
        QPushButton[variant="ghost"]:hover {{ background: {t.bg_elevated}; }}
        QPushButton[variant="theme-toggle"] {{
            min-width: 112px;
            max-width: 112px;
            min-height: 40px;
            max-height: 40px;
            border: 2px solid {t.accent};
            border-radius: {t.radius_md}px;
            background: {t.accent};
            color: #FFFFFF;
            font-size: {t.font_subhead}px;
            font-weight: 600;
            padding: 0 10px;
        }}
        QPushButton[variant="theme-toggle"]:hover {{ background: #0077EE; }}
        QPushButton[variant="theme-toggle"]:pressed {{ background: #0066CC; }}
        QPushButton:disabled {{
            color: {t.text_tertiary};
            border-color: {t.border};
        }}
        QTableWidget {{
            border: none;
            background: {t.bg_surface};
            alternate-background-color: {t.bg_elevated};
            gridline-color: transparent;
            selection-background-color: {t.accent};
            selection-color: #FFFFFF;
        }}
        QHeaderView::section {{
            background: {t.bg_surface};
            color: {t.text_secondary};
            border: none;
            font-size: {t.font_label}px;
            font-weight: 600;
            padding: {t.spacing_sm}px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 4px;
            margin: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {t.text_tertiary};
            border-radius: 2px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 4px;
            margin: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t.text_tertiary};
            border-radius: 2px;
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        QLabel[role="title"] {{
            font-size: {t.font_title}px;
            font-weight: 600;
            color: {t.text_primary};
        }}
        QLabel[role="caption"] {{
            color: {t.text_secondary};
            font-size: {t.font_label}px;
            font-weight: 500;
        }}
        QLabel[role="toast"] {{
            background: {t.bg_surface};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            padding: {t.spacing_sm}px {t.spacing_md}px;
        }}
    """


def animate_theme_crossfade(window) -> None:
    animation = QPropertyAnimation(window, b"windowOpacity")
    animation.setDuration(200)
    animation.setStartValue(0.97)
    animation.setEndValue(1.0)
    animation.start()
    window._theme_animation = animation  # keep reference
