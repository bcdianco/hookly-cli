"""The recipe: trim hook -> stitch hook+core -> burn Snapchat caption.
Deterministic end to end."""
import shutil
import tempfile
from pathlib import Path

from .hook_overlay import overlay_hook_caption
from .stitch import prep_hook, probe, stitch


def make_video(hook, core, caption, out_path, *, hook_dur=3.5,
               width=1080, height=1920, fps=30, caption_pos=14.0, delogo=None) -> Path:
    """Produce one captioned vertical video from a hook + core pair.

    caption: text to burn over the hook segment; falsy => stitch only.
    """
    hook, core, out_path = Path(hook), Path(core), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        prepped = prep_hook(hook, d / "hook.mp4", hook_dur, delogo)
        stitched = stitch(prepped, core, d / "stitched.mp4", width, height, fps)
        if caption and caption.strip():
            # Caption window = the hook's actual length (may be < hook_dur if the
            # source clip was shorter), so it never bleeds onto the core.
            hook_len = probe(prepped)["duration"]
            overlay_hook_caption(stitched, caption, out_path, hook_len,
                                 width, height, caption_pos)
        else:
            shutil.copy(stitched, out_path)
    return out_path
