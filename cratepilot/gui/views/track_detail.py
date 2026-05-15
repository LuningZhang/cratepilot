"""Track detail widget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from cratepilot.db.models import Track


class TrackDetailView(QWidget):
    """Read-only details for selected track."""

    def __init__(self) -> None:
        super().__init__()
        self._fields: dict[str, QLabel] = {}
        container = QWidget()
        form = QFormLayout(container)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        for key in ("Artist", "Title", "Album", "Year", "Genre", "BPM", "Key", "Status", "Path"):
            label = QLabel("-")
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
            label.setMinimumWidth(320)
            label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            form.addRow(f"{key}:", label)
            self._fields[key] = label
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)

    def set_track(self, track: Track | None) -> None:
        if track is None:
            for label in self._fields.values():
                label.setText("-")
            return
        self._fields["Artist"].setText(track.artist or "")
        self._fields["Title"].setText(track.title or "")
        self._fields["Album"].setText(track.album or "")
        self._fields["Year"].setText(str(track.year or ""))
        self._fields["Genre"].setText(track.genre or "")
        self._fields["BPM"].setText(str(track.bpm or ""))
        self._fields["Key"].setText(track.musical_key or "")
        self._fields["Status"].setText(track.sync_status)
        self._fields["Path"].setText(track.absolute_path)
