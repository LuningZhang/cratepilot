"""Sync status and conflict panel."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class SyncPanel(QWidget):
    """Actions for reconcile and conflict resolution."""

    reconcile_requested = Signal()
    keep_db_requested = Signal()
    accept_file_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.status = QLabel("Status: -")
        self.hint = QLabel("No active conflict")
        self.reconcile_button = QPushButton("Reconcile Selected")
        self.keep_db_button = QPushButton("Resolve: Keep DB")
        self.accept_file_button = QPushButton("Resolve: Accept File")

        self.reconcile_button.clicked.connect(self.reconcile_requested.emit)
        self.keep_db_button.clicked.connect(self.keep_db_requested.emit)
        self.accept_file_button.clicked.connect(self.accept_file_requested.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status)
        layout.addWidget(self.hint)
        layout.addWidget(self.reconcile_button)
        layout.addWidget(self.keep_db_button)
        layout.addWidget(self.accept_file_button)
        layout.addStretch()

    def set_track_status(self, status: str | None) -> None:
        current = status or "-"
        self.status.setText(f"Status: {current}")
        conflict = current == "conflict"
        self.keep_db_button.setEnabled(conflict)
        self.accept_file_button.setEnabled(conflict)
        self.hint.setText("Conflict detected. Choose a resolution action." if conflict else "No active conflict")
