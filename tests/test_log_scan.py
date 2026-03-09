from pathlib import Path

from scripts.log_scan import scan


def test_scan_counts_and_limit(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text(
        "INFO start\n"
        "WARN disk 80%\n"
        "ERROR write failed\n"
        "WARNING retry\n"
        "INFO done\n",
        encoding="utf-8",
    )
    hits, counts = scan(log, limit=1)
    assert counts["ERROR"] == 1
    assert counts["WARN"] == 2  # WARN + WARNING
    assert len(hits) == 1


def test_scan_clean_file(tmp_path: Path):
    log = tmp_path / "ok.log"
    log.write_text("INFO all good\nINFO still good\n", encoding="utf-8")
    hits, counts = scan(log, limit=10)
    assert hits == []
    assert sum(counts.values()) == 0
