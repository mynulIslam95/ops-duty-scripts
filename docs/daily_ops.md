# Daily ops (duty shift)

I wrote this so I do the same checks every time I sit down,
instead of improvising.

## Start of shift

1. `python scripts/duty_tasks.py` (dry-run) — see what would run
2. `python scripts/duty_tasks.py --apply` — poll health, scan logs, write handover
3. If health is DOWN: `docs/incident_runbook.md`
4. Leave `reports/handover.txt` for the next person

Health URL can be overridden:

```
APP_HEALTH_URL=http://127.0.0.1:8000/health python scripts/health_poll.py
```

## What I do not do from these scripts

- no secret files
- no remote restarts unless someone on the team asks
- dry-run stays the default in `duty_tasks.py`
