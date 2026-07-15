"""Video ops: probe, trim/clean the hook, and stitch hook -> core to a
normalized vertical frame. Pure ffmpeg — no AI."""
from __future__ import annotations

import json
from pathlib import Path

from .proc import run


def _norm(width, height, fps):
    return (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")


def _delogo_filter(spec: str) -> str:
    """'x:y:w:h' -> ffmpeg delogo filter string. Blurs an AI-gen watermark."""
    try:
        x, y, w, h = (part.strip() for part in spec.split(":"))
    except ValueError as err:
        raise ValueError(f"--delogo must be 'x:y:w:h', got {spec!r}") from err
    return f"delogo=x={x}:y={y}:w={w}:h={h}"


def prep_hook(hook, out_path, dur: float, delogo: str | None = None) -> Path:
    """Keep the first `dur` seconds of the hook (Bryan's locked 3.5s rule),
    optionally blurring a watermark box first. Single ffmpeg pass."""
    filters = []
    if delogo:
        filters.append(_delogo_filter(delogo))
    vf = ["-vf", ",".join(filters)] if filters else []
    cmd = ["ffmpeg", "-y", "-i", str(hook), "-t", f"{dur:.3f}", *vf,
           "-c:v", "libx264", "-c:a", "aac", "-ar", "48000", str(out_path)]
    run(cmd)
    return Path(out_path)


def stitch(hook, core, out_path, width, height, fps) -> Path:
    vf = _norm(width, height, fps)
    # Sources may lack an audio track (common for silent hook clips); synthesize
    # matching-length silence via anullsrc so concat always has 2 audio inputs.
    hp, cp = probe(hook), probe(core)
    inputs = ["-i", str(hook), "-i", str(core)]
    silence, idx = [], 2
    if hp["has_audio"]:
        a0 = "0:a"
    else:
        silence += ["-f", "lavfi", "-t", f"{hp['duration']:.3f}",
                    "-i", "anullsrc=r=48000:cl=stereo"]
        a0, idx = f"{idx}:a", idx + 1
    if cp["has_audio"]:
        a1 = "1:a"
    else:
        silence += ["-f", "lavfi", "-t", f"{cp['duration']:.3f}",
                    "-i", "anullsrc=r=48000:cl=stereo"]
        a1, idx = f"{idx}:a", idx + 1
    fc = (f"[0:v]{vf}[v0];[1:v]{vf}[v1];"
          f"[{a0}]aresample=48000[a0];[{a1}]aresample=48000[a1];"
          f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    cmd = ["ffmpeg", "-y", *inputs, *silence,
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-r", str(fps), "-c:v", "libx264", "-c:a", "aac", "-ar", "48000", str(out_path)]
    run(cmd)
    return Path(out_path)


def probe(path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration:stream=width,height,codec_type", "-of", "json", str(path)]).stdout
    data = json.loads(out)
    streams = data.get("streams", [])
    vid = next((s for s in streams if s.get("codec_type") == "video"), {})
    return {
        "duration": float(data["format"]["duration"]),
        "width": int(vid.get("width", 0)),
        "height": int(vid.get("height", 0)),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
    }
