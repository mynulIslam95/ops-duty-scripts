#!/usr/bin/env python3
"""Scan application logs for ERROR / WARN lines.

Meant for the first minutes of a shift: dump a short triage list
instead of scrolling the whole file.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# keep this simple on purpose — real log formats differ per app
LINE_RE = re.compile(r"\b(ERROR|WARN|WARNING|CRITICAL|FATAL)\b", re.IGNORECASE)


def scan(path: Path, limit: int) -> tuple[list[str], Counter]:
    hits: list[str] = []
    counts: Counter = Counter()
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = LINE_RE.search(line)
            if not m:
                continue
            level = m.group(1).upper()
            if level == "WARNING":
                level = "WARN"
            counts[level] += 1
            if len(hits) < limit:
                hits.append(line.rstrip())
    return hits, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    try:
        hits, counts = scan(args.logfile, args.limit)
    except FileNotFoundError:
        print(f"log file not found: {args.logfile}", file=sys.stderr)
        return 2

    total = sum(counts.values())
    print(f"file: {args.logfile}")
    print(f"hits: {total}  (showing {len(hits)})")
    for level in ("CRITICAL", "FATAL", "ERROR", "WARN"):
        if counts[level]:
            print(f"  {level}: {counts[level]}")
    if hits:
        print("---")
        for line in hits:
            print(line)
    return 1 if counts["ERROR"] or counts["CRITICAL"] or counts["FATAL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
