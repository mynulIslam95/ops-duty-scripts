# Incident runbook — app not healthy

Use this when `health_poll.py` exits 1 or the app returns 5xx.

1. Confirm it is not just my laptop
   - hit `/health` once more
   - check `reports/health_history.jsonl` for how long it has been down
2. Check logs
   - `python scripts/log_scan.py fixtures/sample.log` (or the real log path)
   - note the first ERROR time
3. Known leftovers I have already hit
   - disk quota on the data dir → free space, then retry the failed write
   - release job timeout → do not start a second job on top; cancel the leftover first
4. If it is still down after 10 minutes
   - write what I tried into `reports/handover.txt`
   - ping the person on duty (do not guess a restart on a shared host)

Do not paste tokens or customer ids into the handover file.
