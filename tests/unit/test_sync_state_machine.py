from cratepilot.sync.jobs import dequeue_job, enqueue_job
from cratepilot.sync.watcher import start_watcher


def test_job_queue_round_trip():
    enqueue_job("scan", {"root": "/tmp"})
    job = dequeue_job()
    assert job == ("scan", {"root": "/tmp"})


def test_watcher_start_and_stop(tmp_path):
    events: list[str] = []
    handle = start_watcher(str(tmp_path), events.append)
    handle.stop()
    assert handle is not None
