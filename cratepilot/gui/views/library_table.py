"""Library table widget."""

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from cratepilot.db.models import Track


class LibraryTable(QTableWidget):
    """Track listing table."""

    track_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 6)
        self.setHorizontalHeaderLabels(["Artist", "Title", "Album", "Year", "Genre", "Path"])
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cellClicked.connect(self._emit_selection)
        self._tracks: list[Track] = []

    def load_tracks(self, tracks: Iterable[Track]) -> None:
        self._tracks = list(tracks)
        self.setRowCount(len(self._tracks))
        for row, track in enumerate(self._tracks):
            values = [
                track.artist or "",
                track.title or "",
                track.album or "",
                str(track.year or ""),
                track.genre or "",
                track.absolute_path,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, col, item)
        self.resizeColumnsToContents()

    def _emit_selection(self, row: int, _column: int) -> None:
        if 0 <= row < len(self._tracks):
            self.track_selected.emit(self._tracks[row])
