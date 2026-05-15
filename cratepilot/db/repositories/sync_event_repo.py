"""Sync event repository scaffolding."""


class SyncEventRepository:
    def __init__(self, session):
        self.session = session

    def append_event(self, track_id, event_type: str, status: str, payload=None):
        raise NotImplementedError
