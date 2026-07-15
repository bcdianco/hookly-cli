import subprocess

import pytest


def _make_clip(path, seconds, color, fps=24, w=720, h=1280, audio=True):
    # distinct fps/size from target so tests prove normalization
    cmd = ["ffmpeg", "-y",
           "-f", "lavfi", "-i", f"color=c={color}:s={w}x{h}:r={fps}:d={seconds}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"]
    cmd += ["-c:v", "libx264"]
    if audio:
        cmd += ["-c:a", "aac", "-ar", "44100", "-shortest"]
    cmd += [str(path)]
    subprocess.run(cmd, check=True, capture_output=True)


@pytest.fixture
def clip_factory(tmp_path):
    def make(name, seconds, color="red", audio=True, w=720, h=1280):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        _make_clip(p, seconds, color, w=w, h=h, audio=audio)
        return p
    return make
