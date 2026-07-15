#!/usr/bin/env bash
# Fetch a Google Sheet tab as CSV on stdout. The sheet must be link-shared
# ("anyone with the link can view"). No auth, no API key.
#
# Usage: gsheet_csv.sh <sheet-id-or-url> [gid=0] > out.csv
#   gid is the tab id (in the sheet URL as #gid=NNN); the first tab is 0.
set -euo pipefail

RAW="${1:?usage: gsheet_csv.sh <sheet-id-or-url> [gid]}"
GID="${2:-0}"

ID="$RAW"
case "$RAW" in
  *docs.google.com*) ID=$(printf '%s' "$RAW" | sed -nE 's#.*/spreadsheets/d/([^/]+).*#\1#p' | head -1) ;;
esac
[ -n "$ID" ] || { echo "gsheet_csv.sh: could not parse a sheet id from: $RAW" >&2; exit 1; }

OUT=$(curl -sL "https://docs.google.com/spreadsheets/d/${ID}/export?format=csv&gid=${GID}")

# A private sheet redirects to an HTML sign-in page instead of CSV.
if printf '%s' "$OUT" | head -c 15 | grep -qi "<!DOCTYPE html" 2>/dev/null; then
  echo "gsheet_csv.sh: got an HTML page, not CSV — the sheet isn't link-shared for viewing." >&2
  exit 1
fi

printf '%s' "$OUT"
