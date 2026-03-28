# ops-duty-scripts

Small scripts I use to practice day-to-day application support.

Not a product. The idea is: same checks every shift, write down what happened,
do not change systems unless I pass `--apply`.

## What it does

| Script | Point |
|--------|--------|
| `scripts/health_poll.py` | GET `/health`, keep a jsonl history |
| `scripts/log_scan.py` | pull ERROR/WARN lines out of a log |
| `scripts/duty_tasks.py` | run the two checks and write a handover note |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q

python scripts/duty_tasks.py
python scripts/duty_tasks.py --apply --url http://127.0.0.1:8000/health
python scripts/log_scan.py fixtures/sample.log
```

`duty_tasks.py` is dry-run unless `--apply` is set.

## Docs

- `docs/daily_ops.md` — start of shift
- `docs/incident_runbook.md` — health is down

I keep an action log in `reports/ops_actions.jsonl` when `--apply` is used.
No credentials in this repo.
