"""Preview: extracted action handlers keep the main window layout file concise and maintainable."""

from cratepilot.gui.views.bulk_edit_modal import BulkEditDialog
from cratepilot.gui.views.confirm_dialog import ConfirmDialog
from cratepilot.gui.views.track_edit_dialog import TrackEditDialog
from cratepilot.sync.scanner import run_initial_scan
from cratepilot.sync.watcher import start_watcher
from cratepilot.utils.file_navigation import reveal_in_finder


class MainWindowActionsMixin:
    def run_scan(self) -> None:
        try:
            result = run_initial_scan(self.root_folder, self.session_factory)
            self.refresh_tracks()
            self.toast.show_message(f"Scan complete · Scanned {result.scanned_files} · Imported {result.imported_tracks} · Failed {result.failed_files}")
        except Exception as exc:
            self.toast.show_message(f"Scan failed: {exc}")

    def toggle_watcher(self) -> None:
        if self.watch_handle is not None:
            self.watch_handle.stop()
            self.watch_handle = None
            self.watch_button.setText("Start Watcher")
            self.toast.show_message("Watcher stopped")
            return
        self.watch_handle = start_watcher(self.root_folder, lambda path: self.watcher_bridge.changed.emit(path))
        self.watch_button.setText("Stop Watcher")
        self.toast.show_message("Watcher started")

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
            ok = self.service.update_track_metadata(self.current_track.id, dialog.updates(), rename_file_with_title=dialog.rename_file_with_title())
            self.toast.show_message("Track updated" if ok else "Edit failed: could not update metadata")
            self.refresh_tracks()

    def reveal_selected_location(self) -> None:
        if not self.current_track:
            return
        try:
            reveal_in_finder(self.current_track.absolute_path)
        except FileNotFoundError:
            self.toast.show_message("File not found on disk. Scan Library to refresh list.")
        except Exception as exc:
            self.toast.show_message(f"Reveal failed: {exc}")

    def bulk_edit(self) -> None:
        if not self.selected_tracks:
            return
        dialog = BulkEditDialog(len(self.selected_tracks), self)
        if not dialog.exec():
            return
        updates = dialog.updates()
        if not updates:
            return
        confirm = ConfirmDialog("Confirm bulk edit", f"Apply {len(updates)} fields to {len(self.selected_tracks)} tracks?", self)
        if not confirm.exec():
            return
        result = self.service.bulk_update_metadata([track.id for track in self.selected_tracks], updates)
        self.toast.show_message(f"Bulk edit complete · Success {result.success_count} · Failed {len(result.failed)}")
        self.refresh_tracks()

    def reconcile_selected(self) -> None:
        if self.current_track:
            ok = self.service.reconcile_track(self.current_track.id)
            self.toast.show_message("Reconciled selected track" if ok else "Reconcile failed")
            self.refresh_tracks()

    def resolve_conflict(self, mode: str) -> None:
        if self.current_track:
            ok = self.service.resolve_conflict(self.current_track.id, mode)
            self.toast.show_message("Conflict resolved" if ok else f"Resolve failed: {mode}")
            self.refresh_tracks()

    def find_duplicates(self) -> None:
        data = self.service.find_duplicates()
        self.toast.show_message(f"Duplicate scan · Exact groups {len(data['exact_groups'])} · Fuzzy {len(data['fuzzy_candidates'])}")

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        if self.toast.isVisible():
            self.toast.show_message(self.toast.text(), 1600)

    def closeEvent(self, event):  # noqa: N802
        if self.watch_handle is not None:
            self.watch_handle.stop()
            self.watch_handle = None
        super().closeEvent(event)
