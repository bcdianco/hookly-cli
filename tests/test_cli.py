from pathlib import Path

import pytest

from engine.__main__ import check_environment, load_captions, output_filename


def test_output_filename_single_vs_multi_core():
    hook, core = Path("h1-pov.mp4"), Path("core.mp4")
    assert output_filename(hook, core, multi_core=False) == "h1-pov.mp4"
    assert output_filename(hook, core, multi_core=True) == "h1-pov_x_core.mp4"


def test_check_environment_passes_here():
    # ffmpeg + Chrome are present in this dev environment.
    assert check_environment() == []


def test_load_captions_parses_pipe_and_tab(tmp_path):
    f = tmp_path / "caps.txt"
    f.write_text("# comment\nh1 | first caption\nh2\tsecond caption\n\n", encoding="utf-8")
    assert load_captions(f) == {"h1": "first caption", "h2": "second caption"}


def test_load_captions_rejects_bad_line(tmp_path):
    f = tmp_path / "caps.txt"
    f.write_text("h1 no delimiter here\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        load_captions(f)
