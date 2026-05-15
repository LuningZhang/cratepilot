"""Single-track edit dialog."""

from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from cratepilot.db.repositories.track_repo import EDITABLE_FIELDS

ORDERED_FIELDS = ["title", "artist", "album", "year", "genre", "bpm", "musical_key", "comment", "track_number"]


class TrackEditDialog(QDialog):
    """Modal editor for one track."""

    def __init__(self, track, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Track Metadata")
        self._inputs: dict[str, QLineEdit] = {}
        self.rename_checkbox = QCheckBox("Also rename file to match new title")
        self.rename_checkbox.setChecked(False)
        form = QFormLayout()
        for field in ORDERED_FIELDS:
            if field not in EDITABLE_FIELDS:
                continue
            edit = QLineEdit("" if getattr(track, field) is None else str(getattr(track, field)))
            form.addRow(field.replace("_", " ").title(), edit)
            self._inputs[field] = edit
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.rename_checkbox)
        layout.addWidget(buttons)

    def updates(self) -> dict[str, object]:
        result: dict[str, object] = {}
        for field, input_box in self._inputs.items():
            value = input_box.text().strip()
            if field == "year":
                result[field] = int(value) if value.isdigit() else None
            elif field == "bpm":
                result[field] = float(value) if value else None
            else:
                result[field] = value or None
        return result

    def rename_file_with_title(self) -> bool:
        return self.rename_checkbox.isChecked()
