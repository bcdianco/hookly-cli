from engine.discovery import list_videos


def test_list_videos_from_folder_sorted(tmp_path):
    for name in ("b.mp4", "a.mov", "note.txt", "c.webm"):
        (tmp_path / name).write_bytes(b"x")
    got = [p.name for p in list_videos(tmp_path)]
    assert got == ["a.mov", "b.mp4", "c.webm"]      # sorted, non-video filtered


def test_list_videos_single_file(tmp_path):
    f = tmp_path / "hook.mp4"
    f.write_bytes(b"x")
    assert list_videos(f) == [f]


def test_list_videos_rejects_non_video_file(tmp_path):
    f = tmp_path / "hook.txt"
    f.write_bytes(b"x")
    assert list_videos(f) == []
