"""Preview: modernized split-view UI with toolbar card, theme toggle, and polished panel layout."""

from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QSplitter, QVBoxLayout, QWidget
from sqlalchemy.orm import sessionmaker

from cratepilot.gui.theme import THEME_AUTO, THEME_DARK, app_stylesheet, animate_theme_crossfade, effective_theme, toggle_icon_for
from cratepilot.gui.main_window_actions import MainWindowActionsMixin
from cratepilot.gui.toast import ToastLabel
from cratepilot.gui.views.library_table import LibraryTable
from cratepilot.gui.views.sync_panel import SyncPanel
from cratepilot.gui.views.track_detail import TrackDetailView
from cratepilot.gui.watcher_bridge import WatcherBridge
from cratepilot.services.library_service import LibraryService


class MainWindow(MainWindowActionsMixin, QMainWindow):
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
        self.settings = QSettings("CratePilot", "CratePilot")
        pref = self.settings.value("ui/theme", THEME_AUTO)
        self.theme_preference = pref if pref in {THEME_AUTO, "light", THEME_DARK} else THEME_AUTO
        self.current_theme = effective_theme(self.theme_preference)

        self.setWindowTitle("CratePilot")
        self.resize(1360, 860)
        self.setMinimumSize(1280, 800)
        self._build_ui()
        self._apply_theme(animated=False)
        self.refresh_tracks()

    def _build_ui(self) -> None:
        self.scan_button = self._button("Scan Library", self.run_scan, "primary")
        self.edit_button = self._button("Edit Selected", self.edit_selected)
        self.reveal_button = self._button("Reveal in Finder", self.reveal_selected_location)
        self.bulk_button = self._button("Bulk Edit", self.bulk_edit)
        self.dup_button = self._button("Find Duplicates", self.find_duplicates)
        self.watch_button = self._button("Start Watcher", self.toggle_watcher)
        self.theme_button = self._button("", self.toggle_theme, "theme-toggle")
        self.search = QLineEdit()
        self.search.setProperty("role", "search")
        self.search.setPlaceholderText("Search title, artist, album, genre, path...")
        self.search.textChanged.connect(self.refresh_tracks)
        self.status_label = QLabel(f"Root: {Path(self.root_folder)}")
        self.status_label.setProperty("role", "caption")
        self.edit_button.setEnabled(False)
        self.reveal_button.setEnabled(False)
        self.bulk_button.setEnabled(False)

        self.table = LibraryTable()
        self.detail = TrackDetailView()
        self.sync_panel = SyncPanel()
        self.toast = ToastLabel(self)
        self.table.track_selected.connect(self._on_track_selected)
        self.table.selection_changed.connect(self._on_selection_changed)
        self.sync_panel.reconcile_requested.connect(self.reconcile_selected)
        self.sync_panel.keep_db_requested.connect(lambda: self.resolve_conflict("keep_db"))
        self.sync_panel.accept_file_requested.connect(lambda: self.resolve_conflict("accept_file"))

        toolbar = QWidget(objectName="toolbar")
        top = QHBoxLayout(toolbar)
        top.setContentsMargins(12, 8, 12, 8)
        top.setSpacing(8)
        for btn in (self.scan_button, self.edit_button, self.reveal_button, self.bulk_button, self.dup_button, self.watch_button):
            top.addWidget(btn)
        top.addWidget(self.search, 1)
        top.addWidget(self.theme_button)

        left_panel = QWidget(objectName="panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.addWidget(self.table)

        right_panel = QWidget(objectName="panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.addWidget(self.detail, 3)
        right_layout.addWidget(self.sync_panel, 2)
        right_layout.addWidget(self.status_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([900, 500])

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.addWidget(toolbar)
        layout.addWidget(splitter)
        wrapper = QWidget()
        wrapper.setLayout(layout)
        self.setCentralWidget(wrapper)

    def _button(self, text: str, callback, variant: str = "secondary") -> QPushButton:
        button = QPushButton(text)
        button.setProperty("variant", variant)
        button.clicked.connect(callback)
        return button

    def _apply_theme(self, animated: bool) -> None:
        self.current_theme = effective_theme(self.theme_preference)
        self.theme_button.setText(toggle_icon_for(self.current_theme))
        self.theme_button.setToolTip("Toggle light/dark theme")
        self.setStyleSheet(app_stylesheet(self.current_theme))
        if animated:
            animate_theme_crossfade(self)

    def toggle_theme(self) -> None:
        self.theme_preference = "light" if self.current_theme == THEME_DARK else THEME_DARK
        self.settings.setValue("ui/theme", self.theme_preference)
        self._apply_theme(animated=True)

    def refresh_tracks(self) -> None:
        tracks = self.service.list_tracks(search=self.search.text())
        self.current_track = None
        self.detail.set_track(None)
        self.sync_panel.set_track_status(None)
        self.table.load_tracks(tracks)
        self.status_label.setText(f"Loaded {len(tracks)} tracks | Root: {self.root_folder}")

    def _on_track_selected(self, track) -> None:
        self.current_track = track
        self.detail.set_track(track)
        self.sync_panel.set_track_status(track.sync_status)

    def _on_selection_changed(self, tracks: list) -> None:
        self.selected_tracks = tracks
        one_selected = len(tracks) == 1
        self.edit_button.setEnabled(one_selected)
        self.reveal_button.setEnabled(one_selected)
        self.bulk_button.setEnabled(len(tracks) >= 1)
