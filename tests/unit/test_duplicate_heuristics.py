from cratepilot.sync.reconciler import run_reconciliation


def test_reconciler_counts_files(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"x")
    (tmp_path / "b.txt").write_bytes(b"y")
    count = run_reconciliation(str(tmp_path))
    assert count == 2
