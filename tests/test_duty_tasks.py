from pathlib import Path

from scripts.duty_tasks import write_handover


def test_handover_apply(tmp_path: Path):
    out = tmp_path / "handover.txt"
    write_handover(out, health_rc=0, log_rc=1, dry_run=False)
    text = out.read_text(encoding="utf-8")
    assert "health_poll exit: 0" in text
    assert "log_scan exit:    1" in text
    assert "incident_runbook" in text


def test_handover_dry_run_does_not_write(tmp_path: Path):
    out = tmp_path / "handover.txt"
    write_handover(out, health_rc=1, log_rc=0, dry_run=True)
    assert not out.exists()
