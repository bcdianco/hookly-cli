from engine.hook_overlay import clean_caption, find_chrome, render_caption_png


def test_clean_caption_strips_wrapping_quotes():
    assert clean_caption('  "hey   there"  ') == "hey there"
    assert clean_caption("“curly”") == "curly"


def test_find_chrome_resolves():
    # Should find a real browser on this machine (or CHROME_PATH).
    assert find_chrome()


def test_render_caption_png_produces_image(tmp_path):
    out = render_caption_png("wait what Mike??", tmp_path / "cap.png",
                             width=1080, height=1920)
    assert out.exists() and out.stat().st_size > 0
