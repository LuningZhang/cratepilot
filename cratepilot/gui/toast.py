"""Preview: inline toast notification layer replacing OS-style alert popups."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel, QWidget


class ToastLabel(QLabel):
    """Lightweight toast message inside main window."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setProperty("role", "toast")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setVisible(False)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.setVisible(False))

    def show_message(self, message: str, timeout_ms: int = 2800) -> None:
        self.setText(message)
        self.adjustSize()
        width = min(max(self.width() + 20, 260), 560)
        self.resize(width, self.height() + 12)
        x = self.parentWidget().width() - self.width() - 20
        y = 16
        self.move(max(20, x), y)
        self.setVisible(True)
        self.raise_()
        self._timer.start(timeout_ms)
