"""Main window for Milestone 1 MVP."""

from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import sessionmaker

from cratepilot.db.repositories.track_repo import TrackRepository
from cratepilot.gui.views.library_table import LibraryTable
from cratepilot.gui.views.track_detail import TrackDetailView
from cratepilot.sync.scanner import ScanResult, run_initial_scan


class MainWindow(QMainWindow):
    """CratePilot MVP window."""

    def __init__(self, root_folder: str, session_factory: sessionmaker):
        super().__init__()
        self.root_folder = root_folder
        self.session_factory = session_factory
        self.setWindowTitle("CratePilot MVP")
        self.resize(1280, 800)

        self.scan_button = QPushButton("Run Initial Scan")
        self.scan_button.clicked.connect(self.run_scan)
        self.status_label = QLabel(f"Root folder: {Path(root_folder)}")

        self.table = LibraryTable()
        self.detail = TrackDetailView()
        self.table.track_selected.connect(self.detail.set_track)

        top = QHBoxLayout()
        top.addWidget(self.scan_button)
        top.addWidget(self.status_label)
        top.addStretch()

        splitter = QSplitter()
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([900, 500])

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(splitter)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.refresh_tracks()

    def refresh_tracks(self) -> None:
        with self.session_factory() as session:
            tracks = TrackRepository(session).list_tracks()
        self.table.load_tracks(tracks)
        self.status_label.setText(f"Loaded {len(tracks)} tracks | Root: {self.root_folder}")

    def run_scan(self) -> None:
        try:
            result = run_initial_scan(self.root_folder, self.session_factory)
        except Exception as exc:
            QMessageBox.critical(self, "Scan failed", str(exc))
            return
        self.refresh_tracks()
        self._show_scan_summary(result)

    def _show_scan_summary(self, result: ScanResult) -> None:
        QMessageBox.information(
            self,
            "Scan complete",
            f"Scanned: {result.scanned_files}\nImported/updated: {result.imported_tracks}\nFailed: {result.failed_files}",
        )
