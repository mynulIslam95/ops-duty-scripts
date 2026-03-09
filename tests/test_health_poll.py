from __future__ import annotations

import json
from pathlib import Path

from scripts.health_poll import append_history, check


class _Resp:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_check_healthy(monkeypatch):
    def fake_urlopen(req, timeout=0):
        return _Resp(200, b'{"status":"ok"}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    out = check("http://127.0.0.1:8000/health", 1.0)
    assert out["ok"] is True
    assert out["status_code"] == 200


def test_check_down(monkeypatch):
    def fake_urlopen(req, timeout=0):
        raise TimeoutError("timed out")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    out = check("http://127.0.0.1:8000/health", 1.0)
    assert out["ok"] is False
    assert "timed out" in out["body"]


def test_history_append(tmp_path: Path):
    p = tmp_path / "h.jsonl"
    append_history(p, {"ts": "t1", "ok": True})
    append_history(p, {"ts": "t2", "ok": False})
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["ok"] is False
