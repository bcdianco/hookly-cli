---
name: hook-producer
description: >-
  Produce short-form hook videos from raw clips. Use this whenever the user has
  hook clips + a core/body clip and wants finished captioned videos, wants to
  test several hooks against one core, wants help writing or improving
  short-form video captions/hooks, or wants to batch-render hook x core
  combinations. Trigger it even when the user just drops a folder of clips and
  says something loose like "make hooks from these", "caption these", "stitch
  the hook to the core", or "which hook works best" — this skill covers the whole
  pipeline from analyzing the footage to rendering the final MP4s.
---

# Hook Producer

Turn raw **hook** clips and one **core** (body) clip into finished, captioned
short-form videos — the way a good short-form editor would: watch the footage,
understand the payoff, write hooks that actually set it up, then render.

The mechanical rendering (trim → stitch → burn a Snapchat-style caption) is done
by the bundled local engine (`ffmpeg` + headless Chrome, no AI/accounts). **Your
job is the judgment the engine can't do**: reading each clip, matching the hook
to the core's payoff, and writing captions that make people stop scrolling.

> The engine and the helper script ship *inside this plugin*, not in the user's
> project. Always call them through `${CLAUDE_PLUGIN_ROOT}` (the plugin's install
> path, which Claude Code sets for you) — the commands below already do this.
> The user's clips, `captions.txt`, and `outputs/` stay in *their* working dir.

## The pipeline

Work through these in order. Don't skip the analysis — captions written from
filenames alone are almost always off, because the whole game is matching the
hook to what the core actually delivers.

1. **Locate & confirm inputs** — the hook clips, the one core clip, the audience.
2. **Analyze every clip** — build a contact sheet per clip and describe what's on screen.
3. **Find the core's single payoff** — the one thing every video pays off.
4. **Write the captions** — one per hook, all funneling into that payoff.
5. **Render** — run the engine to burn captions and stitch each hook × core.

---

## 1. Locate & confirm inputs

The standard input is a **single project folder** the user points you at, laid
out by convention:

```
<campaign>/
  hooks/        one or more hook clips (each becomes a video's first ~3.5s)
  core.mp4      the core/body every hook stitches onto
                (or a cores/ folder → matrix: every hook × every core)
```

**Auto-detect first.** Given a folder, look for a `hooks/` subfolder plus a
`core.*` file (or a `cores/` subfolder). If that layout is there, just use it —
don't make the user re-type paths they already organized. **Ask only if unsure:**
if there's no `hooks/`, or two video folders and it's ambiguous which is which,
then ask them to point out the hooks vs. the core. (Loose inputs still work too —
a couple of files, or two arbitrary folders they name.)

Also confirm the **audience — local or international?** It decides the caption
language (step 4), so it genuinely changes the output. If it's not obvious from
the footage or the request, ask; don't guess.

## 2. Analyze every clip

You cannot write a good hook for footage you haven't seen. Build a contact sheet
(a grid of frames in one image) for each clip and actually look at it.

```bash
# a hook clip — first 4 seconds, which is all the viewer sees before the core
"${CLAUDE_PLUGIN_ROOT}/scripts/contact_sheet.sh" "path/to/hook.mp4" /tmp/hook.png
# the core — spread frames across the whole clip to read the full story
"${CLAUDE_PLUGIN_ROOT}/scripts/contact_sheet.sh" "path/to/core.mp4" /tmp/core.png full 4 5
```

Then **read each sheet** (open the PNG) and write a one-liner per clip: who's on
screen, the setting, the vibe, and the clip's *tell* — the one specific,
relatable detail a viewer latches onto (e.g. "always-hungry delivery rider",
"gym bro on a full cheat meal", "burnt-out office guy eating alone at night").
The tell is what makes a caption feel observed and real instead of generic.

If a clip has on-screen text (chat, captions, UI), the sheet will show it —
transcribe it, it's usually the key to the story.

## 3. Find the core's single payoff

Every finished video ends in the **same** core, so every hook has to pay off the
**same** thing. Read the core sheet and name that one payoff in a sentence — the
joke, the reveal, the transformation, the punchline. Be specific about *what* it
delivers, because that's the promise each hook has to make.

**This is the step people get wrong.** If the core's payoff is "his AI clone is
obsessed with burgers", then a hook promising "gym guy skips leg day" or "office
guy who ghosts the group chat" **breaks** — the hook sets an expectation the core
never pays off. The different hook clips are just different *faces* of the same
joke, shot for variety. The theme stays constant; only the framing varies.

## 4. Write the captions

One caption per hook. Every one has to funnel into the core's single payoff (step
3). Hold these in mind — they're what separate a scroll-stopper from filler:

- **Set up the payoff, don't wander off it.** The hook's promise = the core's
  delivery. Use each clip's *tell* (step 2) for flavor, but never invent a trait
  the core won't cash in.
- **Vary the POV across the set, not the theme.** Four clips → four *entry
  points* into the same payoff so the batch doesn't feel repetitive. Reliable
  angles: **you-did-it** ("I cloned my friend…"), **observer-disbelief** ("why
  does this sound EXACTLY like him??"), **warning/secret** ("never tell them
  you…"), **imagine/POV** ("POV: your friend isn't real").
- **Match the audience (from step 1).**
  - *Local* → local slang and brand names are an asset ("barkada", "Jollibee").
  - *International* → strip local-only slang and brands; use universal terms
    ("group chat" / "the gc", "burgers/fast food"). The visuals carry the
    locale; the words shouldn't gate-keep it.
- **Snapchat style = short and punchy.** One line that reads in under a second,
  ~40–90 characters (hard cap ~128). Casual, lowercase is fine, curiosity-gap or
  POV framing. At most one emoji, and only if it adds a beat.
- **Proofread.** Typos read as low-effort and kill trust on a hook. Check every
  line.

**Example** (core payoff = "an AI clone is indistinguishable from your friend"):

Input hook tells:
```
rider     — always-hungry delivery guy
gymbro    — jacked, mid cheat meal
office    — tired office guy, eating alone at night
student   — kid grinding on a laptop late
```
Output (international audience, one POV each, all funnel to the clone payoff):
```
rider   | cloned my friend into a bot. the group chat still hasn't noticed 💀
gymbro  | why does this bot sound EXACTLY like him?? 😳
office  | replaced him with an AI weeks ago. he's honestly more active now 🫠
student | nobody in the group chat knows he's been an AI for weeks 🤫
```

Show the captions to the user and get a nod before rendering — captions are cheap
to revise as text and expensive to re-render.

## 5. Render

Write the approved captions to a file, one line per hook keyed by filename
**without extension**, `name | caption`:

```
rider   | cloned my friend into a bot. the group chat still hasn't noticed 💀
gymbro  | why does this bot sound EXACTLY like him?? 😳
```

Then run the engine (see `references/engine.md` for all flags):

```bash
# many hooks, one core
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine --hooks inputs/hooks/ --core inputs/core.mp4 \
  --captions captions.txt --out outputs/

# many hooks × many cores (matrix) — point --core at a folder
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine --hooks inputs/hooks/ --core inputs/cores/ \
  --captions captions.txt --out outputs/
```

Outputs land in `outputs/` as `<hook>.mp4` (single core) or `<hook>_x_<core>.mp4`
(matrix). Report what was produced. If a clip carries an AI watermark (e.g. a
Veo/Gemini sparkle), pass `--delogo x:y:w:h` to blur it.

Deliver: the finished MP4s **and** the `captions.txt` used, so the user can tweak
lines and re-render fast.

## Setup check

If a render fails, verify the toolchain first — the engine needs `ffmpeg` and
Google Chrome/Chromium:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python3 -m engine --selfcheck
```
