from cratepilot.sync.jobs import dequeue_job, enqueue_job
from cratepilot.sync.watcher import start_watcher


def test_job_queue_round_trip():
    enqueue_job("scan", {"root": "/tmp"})
    job = dequeue_job()
    assert job == ("scan", {"root": "/tmp"})


def test_watcher_disabled_marker():
    assert start_watcher("/tmp/music").startswith("watcher-disabled:")
