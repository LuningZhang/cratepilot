"""Application entrypoint."""

from pathlib import Path
import os
import subprocess
import sys

from PySide6.QtWidgets import QApplication, QWidget

from cratepilot.config import load_settings
from cratepilot.db.bootstrap import initialize_database
from cratepilot.db.connection import make_engine, make_session_factory
from cratepilot.gui.main_window import MainWindow
from cratepilot.gui.onboarding import ensure_runtime_settings
from cratepilot.utils.logging import configure_logging


_FOREGROUND_ENV = "CRATEPILOT_FOREGROUND"


def _migrations_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "db" / "migrations"


def _run_foreground_app() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    settings = ensure_runtime_settings(QWidget(), load_settings())
    initialize_database(settings, _migrations_dir())
    engine = make_engine(settings.db_dsn)
    session_factory = make_session_factory(engine)
    window = MainWindow(settings.root_folder, session_factory)
    window.show()
    return app.exec()


def main() -> int:
    if os.environ.get(_FOREGROUND_ENV) == "1":
        return _run_foreground_app()

    env = os.environ.copy()
    env[_FOREGROUND_ENV] = "1"
    subprocess.Popen(
        [sys.executable, "-m", "cratepilot"],
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("CratePilot is launching in the background.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
