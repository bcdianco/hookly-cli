from engine.stitch import prep_hook, probe, stitch


def test_stitch_normalizes_and_concatenates(tmp_path, clip_factory):
    hook = clip_factory("hook.mp4", 1, "red")     # 1s, 720x1280@24
    core = clip_factory("core.mp4", 2, "blue")    # 2s
    out = tmp_path / "out.mp4"
    stitch(hook, core, out, width=1080, height=1920, fps=30)
    info = probe(out)
    assert info["width"] == 1080 and info["height"] == 1920
    assert info["has_audio"] is True
    assert 2.7 < info["duration"] < 3.6           # ~3s total, encoder slack


def test_stitch_handles_silent_hook(tmp_path, clip_factory):
    hook = clip_factory("hook.mp4", 1, "red", audio=False)   # no audio track
    core = clip_factory("core.mp4", 2, "blue")
    out = tmp_path / "out.mp4"
    stitch(hook, core, out, width=1080, height=1920, fps=30)
    info = probe(out)
    assert info["has_audio"] is True                          # silence synthesized


def test_prep_hook_trims_to_duration(tmp_path, clip_factory):
    hook = clip_factory("hook.mp4", 6, "red")                 # 6s source
    out = tmp_path / "trimmed.mp4"
    prep_hook(hook, out, dur=3.5)
    assert 3.2 < probe(out)["duration"] < 3.8                 # ~3.5s kept
