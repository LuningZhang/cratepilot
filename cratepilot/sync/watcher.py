"""Filesystem watcher for track changes."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".aiff", ".aif", ".m4a", ".aac"}


@dataclass
class WatchHandle:
    observer: Observer

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(timeout=2)


class _TrackEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        self._emit(event.src_path)

    def on_modified(self, event):
        self._emit(event.src_path)

    def on_moved(self, event):
        self._emit(event.dest_path)

    def on_deleted(self, event):
        self._emit(event.src_path)

    def _emit(self, path: str) -> None:
        file_path = Path(path)
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            self.callback(str(file_path))


def start_watcher(root_folder: str, callback: Callable[[str], None]) -> WatchHandle:
    observer = Observer()
    observer.schedule(_TrackEventHandler(callback), root_folder, recursive=True)
    observer.start()
    return WatchHandle(observer=observer)
