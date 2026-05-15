"""Track repository scaffolding."""


class TrackRepository:
    def __init__(self, session):
        self.session = session

    def find_by_path(self, absolute_path: str):
        raise NotImplementedError
