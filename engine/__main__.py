"""CLI: batch-generate captioned hook+core videos for hook testing.

    python -m engine --hooks HOOKS --core CORE.mp4 --captions caps.txt --out OUT/
"""
import argparse
import shutil
from pathlib import Path

from .discovery import list_videos
from .hook_overlay import find_chrome
from .pipeline import make_video
from .proc import run


def _probe_tools():
    """Probe the system tools the engine needs. Yields (name, ok, detail)."""
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool):
            yield tool, True, run([tool, "-version"]).stdout.splitlines()[0]
        else:
            yield tool, False, "not found - install ffmpeg (https://ffmpeg.org/download.html)"
    try:
        yield "chrome", True, find_chrome()
    except RuntimeError as exc:
        yield "chrome", False, str(exc)


def check_environment() -> list:
    """Return human-readable problems; an empty list means ready to run."""
    return [f"{name}: {detail}" for name, ok, detail in _probe_tools() if not ok]


def selfcheck() -> int:
    """Print per-tool status; exit 0 if the engine can run here."""
    ready = True
    for name, ok, detail in _probe_tools():
        print(f"{'OK  ' if ok else 'FAIL'} {name}: {detail}")
        ready = ready and ok
    if ready:
        print("\nReady to render.")
    else:
        print("\nFix the FAIL item(s) above, then re-run --selfcheck.")
    return 0 if ready else 1


def load_captions(path) -> dict:
    """One 'hookname | caption' per line, keyed by hook filename without
    extension. Tab also accepted. Blank lines and #comments ignored."""
    mapping = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            key, val = line.split("|", 1)
        elif "\t" in line:
            key, val = line.split("\t", 1)
        else:
            raise SystemExit(f"Bad captions line (need 'hookname | caption'): {raw!r}")
        mapping[key.strip()] = val.strip()
    return mapping


def output_filename(hook, core, multi_core: bool) -> str:
    """Name outputs so pairings are traceable. With multiple cores the core
    stem is included (hook_x_core.mp4); with one core it's just hook.mp4."""
    stem = f"{hook.stem}_x_{core.stem}" if multi_core else hook.stem
    return f"{stem}.mp4"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m engine",
        description="Stitch hook + core and burn a Snapchat-style caption. "
                    "Every hook is combined with every core (N hooks x M cores = N*M videos). "
                    "Fully local (ffmpeg + Chrome), no AI.")
    p.add_argument("--selfcheck", action="store_true",
                   help="Verify this machine has ffmpeg + Chrome, then exit.")
    p.add_argument("--hooks", help="A hook video, or a folder of hooks (batch / hook-testing).")
    p.add_argument("--core",
                   help="A core video, or a folder of cores. Every hook pairs with every core.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--caption", help="One caption applied to every hook.")
    g.add_argument("--captions", help="Captions file: 'hookname | caption' per line.")
    p.add_argument("--out", help="Output folder.")
    p.add_argument("--hook-dur", type=float, default=3.5,
                   help="Seconds of the hook to keep (default 3.5).")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--caption-pos", type=float, default=14.0,
                   help="Caption band position, %% from bottom (default 14).")
    p.add_argument("--delogo",
                   help="Blur a watermark box on the hook: x:y:w:h (in the hook's resolution).")
    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)

    if args.selfcheck:
        raise SystemExit(selfcheck())

    if not args.hooks or not args.core or not args.out:
        raise SystemExit("--hooks, --core and --out are required (or run --selfcheck).")

    problems = check_environment()
    if problems:
        raise SystemExit("Environment not ready:\n  - " + "\n  - ".join(problems))

    hooks = list_videos(args.hooks)
    if not hooks:
        raise SystemExit(f"No hook videos found at {args.hooks}")
    cores = list_videos(args.core)
    if not cores:
        raise SystemExit(f"No core videos found at {args.core}")
    cap_map = load_captions(args.captions) if args.captions else None
    out_dir = Path(args.out)
    multi_core = len(cores) > 1

    total = len(hooks) * len(cores)
    print(f"{len(hooks)} hook(s) x {len(cores)} core(s) = {total} video(s)\n")
    done = 0
    for hook in hooks:
        caption = cap_map.get(hook.stem) if cap_map is not None else args.caption
        if cap_map is not None and caption is None:
            print(f"!  no caption for '{hook.stem}' - stitching without caption")
        for core in cores:
            name = output_filename(hook, core, multi_core)
            print(f"-> {hook.name} + {core.name}  ->  {name}")
            make_video(hook, core, caption, out_dir / name, hook_dur=args.hook_dur,
                       width=args.width, height=args.height, fps=args.fps,
                       caption_pos=args.caption_pos, delogo=args.delogo)
            done += 1
    print(f"\nDone: {done}/{total} video(s) written to {out_dir}")


if __name__ == "__main__":
    main()
