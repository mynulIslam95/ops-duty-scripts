#!/usr/bin/env python3
"""Run the repetitive duty checklist.

Default is dry-run so nothing is changed by accident.
Pass --apply to actually write the handover note and history files.

TODO: later maybe attach this to the ticket tool the team uses.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent


def run_py(script: str, extra: list[str], dry_run: bool) -> int:
    cmd = [sys.executable, str(SCRIPTS / script), *extra]
    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return 0
    print("RUN:", " ".join(cmd))
    return subprocess.call(cmd)


def write_handover(path: Path, health_rc: int, log_rc: int, dry_run: bool) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = (
        f"Duty handover {ts}\n"
        f"health_poll exit: {health_rc}\n"
        f"log_scan exit:    {log_rc}\n"
        "If health is down, follow docs/incident_runbook.md before paging anyone.\n"
    )
    if dry_run:
        print("DRY-RUN handover would be:\n" + text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path}")


def audit(path: Path, message: str, dry_run: bool) -> None:
    line = json.dumps(
        {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "msg": message}
    )
    if dry_run:
        print("DRY-RUN audit:", line)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually run checks and write files")
    parser.add_argument("--url", default="http://127.0.0.1:8000/health")
    parser.add_argument("--logfile", default=str(ROOT / "fixtures" / "sample.log"))
    parser.add_argument("--handover", default=str(ROOT / "reports" / "handover.txt"))
    args = parser.parse_args()
    dry_run = not args.apply

    audit(ROOT / "reports" / "ops_actions.jsonl", "duty_tasks start", dry_run)

    health_rc = run_py(
        "health_poll.py",
        ["--url", args.url, "--history", str(ROOT / "reports" / "health_history.jsonl")],
        dry_run,
    )
    log_rc = run_py(
        "log_scan.py",
        [args.logfile, "--limit", "15"],
        dry_run,
    )
    write_handover(Path(args.handover), health_rc, log_rc, dry_run)
    audit(ROOT / "reports" / "ops_actions.jsonl", "duty_tasks done", dry_run)

    # dry-run always succeeds; apply returns 1 if health failed
    if dry_run:
        return 0
    return 0 if health_rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
