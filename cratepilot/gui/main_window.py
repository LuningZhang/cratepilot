"""Main window for V1."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import sessionmaker

from cratepilot.gui.views.bulk_edit_modal import BulkEditDialog
from cratepilot.gui.views.library_table import LibraryTable
from cratepilot.gui.views.sync_panel import SyncPanel
from cratepilot.gui.views.track_detail import TrackDetailView
from cratepilot.gui.views.track_edit_dialog import TrackEditDialog
from cratepilot.gui.theme import dark_minimal_stylesheet
from cratepilot.gui.watcher_bridge import WatcherBridge
from cratepilot.services.library_service import LibraryService
from cratepilot.sync.scanner import run_initial_scan
from cratepilot.sync.watcher import start_watcher


class MainWindow(QMainWindow):
    """CratePilot V1 window."""

    def __init__(self, root_folder: str, session_factory: sessionmaker):
        super().__init__()
        self.root_folder = root_folder
        self.session_factory = session_factory
        self.service = LibraryService(session_factory)
        self.current_track = None
        self.selected_tracks = []
        self.watch_handle = None
        self.watcher_bridge = WatcherBridge()
        self.watcher_bridge.changed.connect(self._on_watcher_event)

        self.setWindowTitle("CratePilot")
        self.resize(1360, 860)
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(dark_minimal_stylesheet())

        self.scan_button = QPushButton("Scan Library")
        self.scan_button.clicked.connect(self.run_scan)
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_selected)
        self.bulk_button = QPushButton("Bulk Edit")
        self.bulk_button.clicked.connect(self.bulk_edit)
        self.dup_button = QPushButton("Find Duplicates")
        self.dup_button.clicked.connect(self.find_duplicates)
        self.watch_button = QPushButton("Start Watcher")
        self.watch_button.clicked.connect(self.toggle_watcher)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search title, artist, album, genre, path...")
        self.search.textChanged.connect(self.refresh_tracks)
        self.status_label = QLabel(f"Root: {Path(root_folder)}")
        self.edit_button.setEnabled(False)
        self.bulk_button.setEnabled(False)

        self.table = LibraryTable()
        self.detail = TrackDetailView()
        self.sync_panel = SyncPanel()
        self.table.track_selected.connect(self._on_track_selected)
        self.table.selection_changed.connect(self._on_selection_changed)
        self.sync_panel.reconcile_requested.connect(self.reconcile_selected)
        self.sync_panel.keep_db_requested.connect(lambda: self.resolve_conflict("keep_db"))
        self.sync_panel.accept_file_requested.connect(lambda: self.resolve_conflict("accept_file"))

        top = QHBoxLayout()
        top.addWidget(self.scan_button)
        top.addWidget(self.edit_button)
        top.addWidget(self.bulk_button)
        top.addWidget(self.dup_button)
        top.addWidget(self.watch_button)
        top.addWidget(self.search, 1)

        right = QVBoxLayout()
        right.addWidget(self.detail, 3)
        right.addWidget(self.sync_panel, 2)
        right.addWidget(self.status_label)
        right_box = QWidget()
        right_box.setLayout(right)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.table)
        splitter.addWidget(right_box)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([920, 440])

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(splitter)
        wrapper = QWidget()
        wrapper.setLayout(layout)
        self.setCentralWidget(wrapper)
        self.refresh_tracks()

    def refresh_tracks(self) -> None:
        tracks = self.service.list_tracks(search=self.search.text())
        self.table.load_tracks(tracks)
        self.status_label.setText(f"Loaded {len(tracks)} tracks | Root: {self.root_folder}")

    def _on_track_selected(self, track) -> None:
        self.current_track = track
        self.detail.set_track(track)
        self.sync_panel.set_track_status(track.sync_status)

    def _on_selection_changed(self, tracks: list) -> None:
        self.selected_tracks = tracks
        self.edit_button.setEnabled(len(tracks) == 1)
        self.bulk_button.setEnabled(len(tracks) >= 1)

    def run_scan(self) -> None:
        try:
            result = run_initial_scan(self.root_folder, self.session_factory)
        except Exception as exc:
            QMessageBox.critical(self, "Scan failed", str(exc))
            return
        self.refresh_tracks()
        QMessageBox.information(self, "Scan complete", f"Scanned: {result.scanned_files}\nImported: {result.imported_tracks}\nFailed: {result.failed_files}")

    def toggle_watcher(self) -> None:
        if self.watch_handle is not None:
            self.watch_handle.stop()
            self.watch_handle = None
            self.watch_button.setText("Start Watcher")
            return

        def on_change(path: str) -> None:
            self.watcher_bridge.changed.emit(path)

        self.watch_handle = start_watcher(self.root_folder, on_change)
        self.watch_button.setText("Stop Watcher")

    def _on_watcher_event(self, _path: str) -> None:
        try:
            run_initial_scan(self.root_folder, self.session_factory)
        except Exception:
            return
        self.refresh_tracks()

    def edit_selected(self) -> None:
        if not self.current_track:
            return
        dialog = TrackEditDialog(self.current_track, self)
        if dialog.exec():
            ok = self.service.update_track_metadata(self.current_track.id, dialog.updates())
            if not ok:
                QMessageBox.critical(self, "Edit failed", "Could not write metadata or update database.")
            self.refresh_tracks()

    def bulk_edit(self) -> None:
        if not self.selected_tracks:
            return
        dialog = BulkEditDialog(len(self.selected_tracks), self)
        if dialog.exec():
            updates = dialog.updates()
            if not updates:
                return
            if QMessageBox.question(self, "Confirm bulk edit", f"Apply {len(updates)} fields to {len(self.selected_tracks)} tracks?") != QMessageBox.StandardButton.Yes:
                return
            result = self.service.bulk_update_metadata([track.id for track in self.selected_tracks], updates)
            QMessageBox.information(self, "Bulk edit result", f"Success: {result.success_count}\nFailed: {len(result.failed)}")
            self.refresh_tracks()

    def reconcile_selected(self) -> None:
        if not self.current_track:
            return
        ok = self.service.reconcile_track(self.current_track.id)
        if not ok:
            QMessageBox.critical(self, "Reconcile failed", "Could not reconcile selected track.")
        self.refresh_tracks()

    def resolve_conflict(self, mode: str) -> None:
        if not self.current_track:
            return
        ok = self.service.resolve_conflict(self.current_track.id, mode)
        if not ok:
            QMessageBox.critical(self, "Resolve failed", f"{mode} action failed.")
        self.refresh_tracks()

    def find_duplicates(self) -> None:
        data = self.service.find_duplicates()
        QMessageBox.information(self, "Duplicate Scan", f"Exact duplicate groups: {len(data['exact_groups'])}\nFuzzy candidates: {len(data['fuzzy_candidates'])}")

    def closeEvent(self, event):  # noqa: N802
        if self.watch_handle is not None:
            self.watch_handle.stop()
            self.watch_handle = None
        super().closeEvent(event)
