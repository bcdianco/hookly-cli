"""Run a subprocess and, on failure, raise with the tool's actual stderr so
problems on any machine are debuggable instead of a bare traceback."""
from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tool = Path(str(cmd[0])).name
        tail = (proc.stderr or "").strip()[-1500:]
        raise RuntimeError(f"{tool} failed (exit {proc.returncode}):\n{tail}")
    return proc
