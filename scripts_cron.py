#!/usr/bin/env python3
"""Cron entry point for the awardhack watch job.

Runs `python3 -m awardhack watch` in the repo and prints its JSON digest to stdout,
which Hermes injects into the cron agent's prompt as context.
"""

import json
import os
import subprocess
import sys

REPO = os.path.expanduser("~/award-hack")


def main() -> int:
    if not os.path.isdir(REPO):
        print(json.dumps({"error": f"repo missing at {REPO}"}))
        return 1
    proc = subprocess.run(
        [sys.executable, "-m", "awardhack", "watch"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    out = (proc.stdout or "").strip()
    if proc.returncode != 0:
        print(json.dumps({
            "error": "awardhack watch failed",
            "returncode": proc.returncode,
            "stderr": (proc.stderr or "")[-1500:],
        }))
        return 1
    # Pass through the tool's own JSON verbatim; strip any stray human output.
    try:
        json.loads(out)
        print(out)
    except json.JSONDecodeError:
        start = out.find("{")
        print(out[start:] if start >= 0 else json.dumps({"raw": out[-3000:]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
