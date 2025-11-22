#!/usr/bin/env python3
"""Poll an app health endpoint and keep a small status history.

I use this during a duty shift instead of hitting the URL by hand.
Default is read-only. Exit 0 = healthy, 1 = down / bad response.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "ok": 200 <= resp.status < 300,
                "status_code": resp.status,
                "body": body[:500],
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status_code": exc.code, "body": str(exc)}
    except Exception as exc:  # timeout, DNS, connection refused
        return {"ok": False, "status_code": None, "body": str(exc)}


def append_history(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("APP_HEALTH_URL", "http://127.0.0.1:8000/health"))
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--history", type=Path, default=Path("reports/health_history.jsonl"))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    result = check(args.url, args.timeout)
    row = {"ts": utc_now(), "url": args.url, **result}
    append_history(args.history, row)

    if not args.quiet:
        state = "UP" if result["ok"] else "DOWN"
        code = result["status_code"] if result["status_code"] is not None else "-"
        print(f"{row['ts']}  {state}  {code}  {args.url}")
        if not result["ok"]:
            print(result["body"])

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
