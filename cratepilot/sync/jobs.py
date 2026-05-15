"""Minimal in-process job queue helpers."""

from queue import Queue


_job_queue: Queue[tuple[str, dict]] = Queue()


def enqueue_job(job_type: str, payload: dict) -> int:
    _job_queue.put((job_type, payload))
    return _job_queue.qsize()


def dequeue_job() -> tuple[str, dict] | None:
    if _job_queue.empty():
        return None
    return _job_queue.get_nowait()
