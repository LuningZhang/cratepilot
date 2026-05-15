from cratepilot.services.file_name import title_to_stem, unique_path_for_title


def test_title_to_stem_sanitizes_invalid_characters():
    assert title_to_stem('A/B:C*D?"E<F>G|') == "A_B_C_D_E_F_G_"


def test_unique_path_for_title_preserves_extension(tmp_path):
    original = tmp_path / "old name.mp3"
    original.write_bytes(b"x")
    candidate = unique_path_for_title(str(original), "New Title")
    assert candidate.name == "New Title.mp3"
    assert candidate.suffix == ".mp3"


def test_unique_path_for_title_uses_suffix_when_name_exists(tmp_path):
    original = tmp_path / "old.mp3"
    original.write_bytes(b"x")
    existing = tmp_path / "Title.mp3"
    existing.write_bytes(b"y")
    candidate = unique_path_for_title(str(original), "Title")
    assert candidate.name == "Title (1).mp3"
