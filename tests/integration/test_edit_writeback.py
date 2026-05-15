from cratepilot.utils.hashing import sha256_file


def test_sha256_file(tmp_path):
    file_path = tmp_path / "sample.bin"
    file_path.write_bytes(b"cratepilot")
    digest = sha256_file(str(file_path))
    assert len(digest) == 64
