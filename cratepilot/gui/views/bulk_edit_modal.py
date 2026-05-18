"""Preview: minimalist bulk-edit modal using field toggles and clean form spacing."""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from cratepilot.db.repositories.track_repo import EDITABLE_FIELDS

ORDERED_FIELDS = ["title", "artist", "album", "year", "genre", "bpm", "musical_key", "comment", "track_number"]


class BulkEditDialog(QDialog):
    """Apply metadata updates to multiple tracks."""

    def __init__(self, selected_count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Edit Tracks")
        self.setObjectName("panel")
        self._checks: dict[str, QCheckBox] = {}
        self._inputs: dict[str, QLineEdit] = {}

        info = QLabel(f"Selected tracks: {selected_count}")
        form = QFormLayout()
        for field in ORDERED_FIELDS:
            if field not in EDITABLE_FIELDS:
                continue
            check = QCheckBox("Apply")
            input_box = QLineEdit("")
            row = QHBoxLayout()
            row.addWidget(check)
            row.addWidget(input_box)
            form.addRow(field.replace("_", " ").title(), row)
            self._checks[field] = check
            self._inputs[field] = input_box

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def updates(self) -> dict[str, object]:
        updates: dict[str, object] = {}
        for field, check in self._checks.items():
            if not check.isChecked():
                continue
            value = self._inputs[field].text().strip()
            if field == "year":
                updates[field] = int(value) if value.isdigit() else None
            elif field == "bpm":
                updates[field] = float(value) if value else None
            else:
                updates[field] = value or None
        return updates
