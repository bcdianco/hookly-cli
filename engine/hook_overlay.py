"""Snapchat-style caption: render a full-width semi-transparent band with
centered white text to a transparent PNG via headless Chrome, then burn it onto
the hook segment with ffmpeg. Cross-platform Chrome/Chromium detection.

Caption style is Bryan-locked: rgba(0,0,0,.42) band, Arial regular 50px white,
no stroke, bottom-anchored. No AI involved — the caption text is supplied."""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from .proc import run

_CHROME_CACHE: str | None = None


def find_chrome() -> str:
    """Locate a Chrome/Chromium/Edge binary across macOS, Windows, Linux.
    Override with the CHROME_PATH (or CHROME) environment variable."""
    global _CHROME_CACHE
    if _CHROME_CACHE:
        return _CHROME_CACHE

    env = os.environ.get("CHROME_PATH") or os.environ.get("CHROME")
    if env and Path(env).exists():
        _CHROME_CACHE = env
        return env

    candidates: list[str] = []
    if sys.platform == "darwin":
        candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    elif os.name == "nt":
        pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        la = os.environ.get("LOCALAPPDATA", "")
        candidates += [
            rf"{pf}\Google\Chrome\Application\chrome.exe",
            rf"{pf86}\Google\Chrome\Application\chrome.exe",
            rf"{la}\Google\Chrome\Application\chrome.exe",
            rf"{pf}\Microsoft\Edge\Application\msedge.exe",
            rf"{pf86}\Microsoft\Edge\Application\msedge.exe",
        ]
    # PATH-based lookup (Linux, and anything on PATH)
    for name in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "microsoft-edge", "chrome"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    for c in candidates:
        if c and Path(c).exists():
            _CHROME_CACHE = c
            return c

    raise RuntimeError(
        "Chrome/Chromium not found. Install Google Chrome (or Chromium), "
        "or set CHROME_PATH=/path/to/chrome.")


def clean_caption(text: str) -> str:
    """Strip wrapping quotes; normalize whitespace and curly quotes."""
    t = text.strip()
    t = t.replace("“", '"').replace("”", '"').replace("’", "'")
    t = re.sub(r'^"+|"+$', "", t).strip()
    return re.sub(r"\s+", " ", t)


def _html(caption: str, width: int, height: int, pos_pct: float) -> str:
    safe = (caption.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{{margin:0;width:{width}px;height:{height}px;background:transparent;}}
  .band{{position:absolute;bottom:{pos_pct}%;left:0;width:{width}px;box-sizing:border-box;
    text-align:center;background:rgba(0,0,0,0.42);padding:16px 60px;}}
  .cap{{font-family:Arial,"Liberation Sans","Helvetica Neue",Helvetica,"DejaVu Sans",sans-serif;
    font-weight:400;font-size:50px;line-height:1.3;color:#fff;}}
</style></head><body><div class="band"><span class="cap">{safe}</span></div></body></html>"""


def render_caption_png(caption, out_png, width=1080, height=1920, pos_pct=14.0) -> Path:
    out_png = Path(out_png)
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as d:
        html = Path(d) / "cap.html"
        html.write_text(_html(clean_caption(caption), width, height, pos_pct), encoding="utf-8")
        run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--no-sandbox", "--no-first-run", "--no-default-browser-check",
             "--default-background-color=00000000", "--force-device-scale-factor=1",
             f"--window-size={width},{height}", f"--screenshot={out_png}", html.as_uri()])
    return out_png


def overlay_hook_caption(video, caption, out_path, hook_dur,
                         width=1080, height=1920, pos_pct=14.0) -> Path:
    out_path = Path(out_path)
    with tempfile.TemporaryDirectory() as d:
        png = render_caption_png(caption, Path(d) / "cap.png", width, height, pos_pct)
        fc = f"[0:v][1:v]overlay=0:0:enable='between(t,0,{hook_dur:.3f})'[v]"
        run(["ffmpeg", "-y", "-i", str(video), "-i", str(png),
             "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-c:a", "aac", "-ar", "48000", str(out_path)])
    return out_path
