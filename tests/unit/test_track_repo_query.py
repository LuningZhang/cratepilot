from cratepilot.db.repositories.track_repo import TrackRepository


class _FakeSession:
    def __init__(self):
        self.statement = None

    def scalars(self, statement):
        self.statement = statement
        return []


def test_list_tracks_excludes_missing_by_default():
    session = _FakeSession()
    repo = TrackRepository(session)
    repo.list_tracks()
    sql = str(session.statement)
    assert "tracks.sync_status !=" in sql


def test_list_tracks_can_include_missing():
    session = _FakeSession()
    repo = TrackRepository(session)
    repo.list_tracks(include_missing=True)
    sql = str(session.statement)
    assert "tracks.sync_status !=" not in sql
