#!/usr/bin/env bash
# Download a Google Drive file (a hook or core video) to a local path.
#
# The file must be link-shared ("anyone with the link"). Big videos trip Drive's
# virus-scan confirmation page, so we prefer `gdown` (pip install gdown), which
# handles that reliably, and fall back to curl for small/public files.
#
# Usage: gdrive.sh <drive-file-id-or-url> <out-path>
set -euo pipefail

RAW="${1:?usage: gdrive.sh <drive-id-or-url> <out-path>}"
OUT="${2:?missing output path}"

# Accept a bare id, a /file/d/<ID>/ url, or a ...?id=<ID> url.
ID="$RAW"
case "$RAW" in
  *drive.google.com*|*docs.google.com*)
    ID=$(printf '%s' "$RAW" | sed -nE 's#.*/d/([^/]+).*#\1#p; s#.*[?&]id=([^&]+).*#\1#p' | head -1)
    ;;
esac
[ -n "$ID" ] || { echo "gdrive.sh: could not parse a Drive file id from: $RAW" >&2; exit 1; }

if command -v gdown >/dev/null 2>&1; then
  gdown --id "$ID" -O "$OUT" --quiet
else
  echo "gdrive.sh: 'gdown' not found — trying curl (works only for small/public files)." >&2
  echo "           For reliable large-file downloads: pip install gdown" >&2
  COOKIE=$(mktemp)
  CONFIRM=$(curl -sc "$COOKIE" "https://drive.google.com/uc?export=download&id=${ID}" \
              | sed -nE 's/.*confirm=([0-9A-Za-z_-]+).*/\1/p' | head -1)
  if [ -n "$CONFIRM" ]; then
    curl -sLb "$COOKIE" "https://drive.google.com/uc?export=download&confirm=${CONFIRM}&id=${ID}" -o "$OUT"
  else
    curl -sL "https://drive.google.com/uc?export=download&id=${ID}" -o "$OUT"
  fi
  rm -f "$COOKIE"
fi

# Sanity: a download that returned Drive's HTML page instead of a video is a failure.
if head -c 15 "$OUT" | grep -qi "<!DOCTYPE html" 2>/dev/null; then
  echo "gdrive.sh: got an HTML page, not a video — the file is likely not link-shared, or too big for curl. Install gdown and retry." >&2
  exit 1
fi

echo "$OUT"
