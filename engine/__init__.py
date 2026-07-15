"""Hook Caption Engine — stitch a hook + core clip and burn a Snapchat-style
caption. Fully local and deterministic (ffmpeg + headless Chrome). No AI, no
network, no API keys."""

from .pipeline import make_video

__all__ = ["make_video"]
