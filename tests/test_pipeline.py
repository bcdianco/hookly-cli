from engine.pipeline import make_video
from engine.stitch import probe


def test_make_video_captioned_end_to_end(tmp_path, clip_factory):
    hook = clip_factory("h1-pov.mp4", 6, "red", audio=False)   # 6s silent hook
    core = clip_factory("core.mp4", 4, "blue")                 # 4s core
    out = tmp_path / "out" / "h1-pov.mp4"
    make_video(hook, core, "wait what Mike??", out, hook_dur=3.5)
    info = probe(out)
    assert out.exists()
    assert info["width"] == 1080 and info["height"] == 1920
    assert 7.0 < info["duration"] < 8.2                        # 3.5s hook + 4s core


def test_make_video_without_caption(tmp_path, clip_factory):
    hook = clip_factory("h.mp4", 2, "red")
    core = clip_factory("core.mp4", 2, "blue")
    out = tmp_path / "out.mp4"
    make_video(hook, core, None, out, hook_dur=3.5)
    assert out.exists() and probe(out)["height"] == 1920
