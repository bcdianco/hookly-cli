---
name: hook-producer
description: >-
  Produce short-form hook videos from raw clips. Use this whenever the user has
  hook clips + a core/body clip and wants finished captioned videos, wants to
  test several hooks against one core, wants help writing or improving
  short-form video captions/hooks, or wants to batch-render hook x core
  combinations. It also handles a Google Sheet of Google Drive links (hooks +
  core, often with a caption column) as input. Trigger it even when the user just
  drops a folder of clips, pastes a sheet/Drive links, or says something loose
  like "make hooks from these", "caption these", "render these against the core",
  or "which hook works best" — this skill covers the whole pipeline from getting
  the footage to rendering the final MP4s.
---

# Hook Producer

Turn raw **hook** clips and one **core** (body) clip into finished, captioned
short-form videos — the way a good short-form editor would: get the footage,
understand the payoff, make sure the hooks set it up, QA, then render.

The mechanical rendering (trim → stitch → burn a Snapchat-style caption) is done
by the bundled local engine (`ffmpeg` + headless Chrome, no AI/accounts). **Your
job is the judgment the engine can't do**: reading each clip, matching the hook
to the core's payoff, and making sure the captions are right before they're baked
in.

> The engine, helper scripts, and the `hook-qa` reviewer ship *inside this
> plugin*, not in the user's project. Call the bundled tools through
> `${CLAUDE_PLUGIN_ROOT}` (the plugin's install path, which Claude Code sets for
> you) — the commands below already do this. The user's clips, `captions.txt`,
> and `outputs/` stay in *their* working dir.

## The pipeline

1. **Get the inputs** — a folder of clips, or a Google Sheet + Drive links.
2. **Analyze every clip** — contact sheets; describe the footage.
3. **Find the core's single payoff** — the one thing every video pays off.
4. **Get the captions** — use the ones provided, or write them.
5. **QA the captions** — run the `hook-qa` reviewer; fix what it flags.
6. **Render** — burn each caption onto its hook and stitch hook × core.

Don't skip analysis or QA. The whole game is matching each hook to what the core
actually delivers, and the writer (human or agent) is the one who can't see their
own misses — that's what step 5 is for.

---

## 1. Get the inputs

The caption is always tied to a **hook** (one caption per hook, not per output
video). Inputs come two ways:

### Folder mode

A single project folder, by convention:

```
<campaign>/
  hooks/        one or more hook clips
  core.mp4      the core/body (or a cores/ folder → matrix: every hook × every core)
```

Auto-detect: given a folder, look for a `hooks/` subfolder + a `core.*` file (or
`cores/`). If it's there, use it — don't make the user re-type paths. Ask only if
it's ambiguous (no `hooks/`, or two video folders). Loose inputs (a few files,
two named folders) work too.

### Google Sheet / Drive mode

The user points you at a Google Sheet (or pastes Drive links) where each row
carries the Drive links for its hook + the core, and often a **caption column**.
The sheet and files must be **link-shared** ("anyone with the link").

```bash
# 1) pull the sheet tab as CSV (gid is the tab id; first tab = 0)
"${CLAUDE_PLUGIN_ROOT}/scripts/gsheet_csv.sh" <sheet-url-or-id> 0 > /tmp/sheet.csv

# 2) read the header + a couple rows, then map the columns yourself:
#    which column is the hook link, the core link, the caption (if any), the name.
#    If the layout isn't obvious, show the header row and ask which is which.

# 3) download each video into a local ./inputs/ (one core, reused by all hooks)
mkdir -p inputs/hooks
"${CLAUDE_PLUGIN_ROOT}/scripts/gdrive.sh" <hook-link> inputs/hooks/<name>.mp4
"${CLAUDE_PLUGIN_ROOT}/scripts/gdrive.sh" <core-link> inputs/core.mp4
```

For big Drive files, `gdown` is far more reliable than curl — if `gdrive.sh`
warns it's missing, tell the user to `pip install gdown`. Once downloaded, the
files are local and the rest of the pipeline is identical to folder mode.

### Two things to settle now

- **Audience — local or international?** It decides the caption language (step 4).
  If it's not obvious from the footage/request, ask; don't guess.
- **Were captions provided?** (a sheet caption column, a `captions.txt`, or the
  user typed them.) This decides step 4 — note it now.

## 2. Analyze every clip

You can't judge a hook for footage you haven't seen. Build a contact sheet (a
grid of frames in one image) per clip and look at it.

```bash
# a hook — first 4s, which is all the viewer sees before the core
"${CLAUDE_PLUGIN_ROOT}/scripts/contact_sheet.sh" "inputs/hooks/rider.mp4" /tmp/rider.png
# the core — spread frames across the whole clip to read the full story
"${CLAUDE_PLUGIN_ROOT}/scripts/contact_sheet.sh" "inputs/core.mp4" /tmp/core.png full 4 5
```

Read each sheet (open the PNG) and note, per hook, its **tell** — the one
specific, relatable detail a viewer latches onto ("always-hungry delivery rider",
"gym bro on a full cheat meal"). The tell is what makes a caption feel observed,
and it's what the QA agent checks captions against. Transcribe any on-screen text
(chat, UI) — it's usually the key to the story.

## 3. Find the core's single payoff

Every finished video ends in the **same** core, so every hook pays off the
**same** thing. Read the core sheet and name that one payoff in a sentence — the
joke, reveal, or punchline. Be specific about *what* it delivers; that's the
promise each hook has to make, and the yardstick QA measures against.

## 4. Get the captions

Branch on whether captions already exist (from step 1):

- **Provided** (sheet column / `captions.txt` / typed) → **use them as-is.** Do
  not rewrite the team's lines. Just map each caption to its hook by row or
  filename. They still go through QA (step 5) — but QA *proposes*, it doesn't
  silently overwrite a human's caption.
- **Not provided** → **write them.** One per hook, each funneling into the core's
  payoff (step 3):
  - **Set up the payoff, don't wander off it.** The hook's promise = the core's
    delivery. Use each hook's *tell* for flavor, never a trait the core won't cash in.
  - **Vary the POV across the set, not the theme.** Distinct entry points into the
    same payoff: you-did-it, observer-disbelief, warning/secret, imagine/POV.
  - **Match the audience.** International → drop local-only slang/brands; local →
    lean into them.
  - **Snapchat style:** one line, ~40–90 chars, casual, curiosity-gap or POV, at
    most one emoji.

Either way you end with one caption per hook, keyed by hook name.

## 5. QA the captions

Before rendering (captions are cheap to fix as text; renders are expensive), run
an **independent** review — the writer, human or agent, can't see their own drift.
Spawn the bundled reviewer with the Agent tool, `subagent_type: "hook-qa"`, and
pass it: the **core payoff** (step 3), the **audience**, and the **hook → caption
pairs with each hook's tell**.

It returns a per-caption verdict (`PASS`/`FIX`) with a concrete rewrite for each
`FIX`, plus a set-level note on POV variety. Act on it:

- **Captions you wrote** → apply the fixes directly.
- **Captions the team provided** → surface the flagged ones to the user with the
  suggested rewrite and let them decide; don't overwrite their line silently.

Then show the final **hook → caption table** for a nod. One QA pass + fixes, then
human sign-off — don't loop endlessly.

## 6. Render

Write the approved captions to a file, one line per hook keyed by filename
**without extension**, `name | caption`:

```
rider  | cloned my friend into a bot. the group chat still hasn't noticed 💀
gymbro | why does this bot sound EXACTLY like him?? 😳
```

Then run the engine (see `references/engine.md` for all flags):

```bash
# many hooks, one core
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine \
  --hooks inputs/hooks/ --core inputs/core.mp4 --captions captions.txt --out outputs/

# matrix — point --core at a folder (every hook × every core)
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine \
  --hooks inputs/hooks/ --core inputs/cores/ --captions captions.txt --out outputs/
```

The caption is burned onto the hook's first ~3.5s only (a Snapchat-style band);
the core plays clean. Outputs land in `outputs/` as `<hook>.mp4` (single core) or
`<hook>_x_<core>.mp4` (matrix). If a clip carries an AI watermark (Veo/Gemini
sparkle), add `--delogo x:y:w:h` to blur it.

Deliver: the finished MP4s **and** the `captions.txt` used, so the user can tweak
lines and re-render fast.

## Setup check

If a render fails, verify the toolchain — the engine needs `ffmpeg` and Chrome:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine --selfcheck
```
