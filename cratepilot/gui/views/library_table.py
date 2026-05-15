"""Library table widget."""

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from cratepilot.db.models import Track


class LibraryTable(QTableWidget):
    """Track listing table."""

    track_selected = Signal(object)
    selection_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(["Artist", "Title", "Album", "Year", "Genre"])
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        self.setColumnWidth(0, 240)
        self.setColumnWidth(1, 420)
        self.setColumnWidth(2, 220)
        self.setColumnWidth(3, 80)
        self.itemSelectionChanged.connect(self._emit_selection)
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
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, col, item)
        self.horizontalScrollBar().setValue(0)

    def selected_tracks(self) -> list[Track]:
        rows = sorted({item.row() for item in self.selectedItems()})
        return [self._tracks[row] for row in rows if 0 <= row < len(self._tracks)]

    def _emit_selection(self) -> None:
        selected = self.selected_tracks()
        if selected:
            self.track_selected.emit(selected[0])
        self.selection_changed.emit(selected)
