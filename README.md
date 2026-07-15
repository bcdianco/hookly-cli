# Hookly CLI

**Short-form hook-video production for Claude Code.**

A Claude Code plugin that turns raw footage into finished, captioned short-form
videos. Drop in a folder of **hook** clips + one **core** (body) clip, and Claude
watches the footage, writes Snapchat-style **hook captions** that set up the
core's payoff, and renders every **hook × core** with the caption burned in.

It bundles a fully-local renderer (`ffmpeg` + headless Chrome — no AI, no
accounts, no API keys) so the whole thing runs on your machine.

> Built to de-silo the hook-testing workflow: the process *and* the caption
> judgment travel with the repo, so anyone on the team can produce hooks without
> a bottleneck.

---

## Install

**1. Requirements** (one-time, machine-wide):

- **Python 3.10+**
- **ffmpeg** (includes `ffprobe`) — <https://ffmpeg.org/download.html>
- **Google Chrome** or Chromium (renders the caption)
- **Claude Code**

**2. Get the code:**

```bash
git clone https://github.com/bcdianco/hookly-cli.git
cd hookly-cli
python3 -m engine --selfcheck        # confirms ffmpeg + Chrome are present
```

**3. Install the plugin into Claude Code** (from the repo root):

```bash
claude
# then, inside Claude Code:
/plugin marketplace add .
/plugin install hookly-cli
```

Or point Claude Code at the GitHub repo directly:

```
/plugin marketplace add bcdianco/hookly-cli
/plugin install hookly-cli
```

---

## Use it

Lay out a campaign folder like this:

```
my-campaign/
├── hooks/        all your hook clips
└── core.mp4      the core   (or a cores/ folder for a matrix)
```

Then open Claude Code and just say what you want — the skill drives the rest:

```
"produce hooks from ./my-campaign, international audience"
```

(No strict layout? That's fine — point it at any folders/files and it'll ask
which are the hooks and which is the core.)

Claude will:

1. **Analyze** each clip (builds contact sheets, describes the footage + the core's payoff)
2. **Write** one caption per hook, all funneling into that payoff, matched to your audience
3. **Show you the captions** for a quick nod
4. **Render** every hook × core into `outputs/`, and hand back the `captions.txt`

You review the captions as text (cheap) before anything renders (expensive).

---

## Run the renderer directly (no Claude)

The engine is a normal CLI if you already have captions:

```bash
python3 -m engine --hooks inputs/hooks/ --core inputs/core.mp4 \
  --captions captions.txt --out outputs/
```

See `skills/hook-producer/references/engine.md` for every flag.

---

## License

Proprietary — see [`LICENSE`](./LICENSE). © Bryan Christian Dianco / Techie Labs.
Internal team use.
