"""Qt bridge for watcher callbacks."""

from PySide6.QtCore import QObject, Signal


class WatcherBridge(QObject):
    changed = Signal(str)
