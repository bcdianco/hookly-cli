"""Discover hook inputs: a single video file, or every video in a folder
(the batch / hook-testing case)."""
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}


def list_videos(path) -> list:
    p = Path(path)
    if p.is_file():
        return [p] if p.suffix.lower() in VIDEO_EXTS else []
    if p.is_dir():
        return sorted(f for f in p.iterdir() if f.suffix.lower() in VIDEO_EXTS)
    return []
