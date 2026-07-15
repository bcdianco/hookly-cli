#!/usr/bin/env bash
# Build a contact sheet (grid of frames) from a clip for fast visual analysis.
# The grid lets you "read" a clip in one image instead of scrubbing a player.
#
# Usage:
#   contact_sheet.sh <video> <out.png> [window] [cols] [rows]
#     window : seconds from the start to sample (default 4, good for a 3.5s hook),
#              or the literal word "full" to spread frames across the whole clip
#     cols   : grid columns (default 4)
#     rows   : grid rows    (default 2)
#
# Examples:
#   contact_sheet.sh hook.mp4 sheet.png            # first 4s, 4x2 grid
#   contact_sheet.sh core.mp4 core.png full 4 5    # whole clip, 4x5 grid
set -euo pipefail

V="${1:?usage: contact_sheet.sh <video> <out.png> [window] [cols] [rows]}"
OUT="${2:?missing output path}"
WIN="${3:-4}"
COLS="${4:-4}"
ROWS="${5:-2}"
N=$(( COLS * ROWS ))

if [ "$WIN" = "full" ]; then
  # spread N frames across the whole clip
  DUR=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$V")
  FPS=$(awk "BEGIN{printf \"%.4f\", $N/$DUR}")
  ffmpeg -y -i "$V" \
    -vf "fps=${FPS},scale=300:-1,tile=${COLS}x${ROWS}" \
    -frames:v 1 -update 1 "$OUT" >/dev/null 2>&1
else
  # N frames spread evenly across the first $WIN seconds (output-side trim)
  FPS=$(awk "BEGIN{printf \"%.4f\", $N/$WIN}")
  ffmpeg -y -i "$V" -t "$WIN" \
    -vf "fps=${FPS},scale=300:-1,tile=${COLS}x${ROWS}" \
    -frames:v 1 -update 1 "$OUT" >/dev/null 2>&1
fi

echo "$OUT"
