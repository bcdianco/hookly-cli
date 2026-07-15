# Engine reference — `python3 -m engine`

The bundled renderer. Fully local and deterministic (`ffmpeg` + headless Chrome).
Per hook it: trims the hook to `--hook-dur`, stitches hook → core into one
1080×1920@30 video, and burns the Snapchat-style caption over the hook segment.

## Invocation

```bash
# From inside the plugin skill (the engine is bundled in the plugin, not the cwd):
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine \
  --hooks <path> --core <path> --out <dir> [captions] [options]

# From a clone of the repo (cwd = repo root), or after `pip install -e .`:
python3 -m engine --hooks <path> --core <path> --out <dir> [captions] [options]
hook-caption   --hooks <path> --core <path> --out <dir> [captions] [options]
```

## Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--hooks` | — | A hook video, or a folder of hooks (**required**) |
| `--core` | — | A core video, or a folder of cores (**required**) |
| `--out` | — | Output folder (**required**) |
| `--caption` | — | One caption applied to every hook (pure visual test) |
| `--captions` | — | Captions file, one line per hook: `hookname \| caption` |
| `--hook-dur` | `3.5` | Seconds of the hook to keep |
| `--caption-pos` | `14.0` | Caption band position, % from the bottom |
| `--width` / `--height` | `1080` / `1920` | Output frame size |
| `--fps` | `30` | Output frame rate |
| `--delogo` | — | Blur a watermark box on the hook: `x:y:w:h` |
| `--selfcheck` | — | Verify `ffmpeg` + Chrome are installed, then exit |

## Captions file

One line per hook, keyed by filename **without extension**. The caption belongs
to the hook, so in a matrix it's the same across that hook's cores.

```
h1-pov    | POV: your bro got cloned
h2-whatif | what if this was actually you
```

## Output naming

- **One core** → `outputs/<hook>.mp4`
- **Many cores (matrix)** → `outputs/<hook>_x_<core>.mp4` (every pairing traceable)

## Notes

- Music is **not** added — add platform audio in-app on TikTok/IG to stay
  copyright-safe.
- `--delogo` coordinates are in output space (1080×1920). Cover the logo with a
  little margin; the blur feathers at the edges.
