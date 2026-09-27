# Track B — Missing-information follow-up triage

## Decision in one sentence

The evidence supports a **small process change first**, not a two-week AI build: use a deterministic, reviewable follow-up queue that reconciles request status, received timestamps, case status, opt-out, and the 48-hour rule before a reminder can be proposed.

## Run

Requires Python 3.10+ and no third-party packages.

```text
python src/followup_experiment.py
python -m unittest discover -s tests -v
```

Outputs are written to `output/triage_results.csv` and `output/summary.json`.

The program is **dry-run only**. It reads the supplied CSVs and creates proposed actions/reviews; it never sends a message or calls an external service.

## Experiment

The baseline represents a simple manual pending list: pending in-scope requests on `waiting_info` cases with follow-up allowed are surfaced as actions. It does not reconcile stale `pending` states, missing timestamps, or received information in another field.

The proposed method applies the assessment constraints explicitly and returns `ACTION`, `REVIEW`, or `EXCLUDE` with a reason. The experiment also deduplicates event deliveries by `event_id` for effort calculations.

The changed-input test modifies C024's request timestamps from 4 September 12:00 to 6 September 12:00. Before running, the expected result was that both C024 requests would move from `ACTION` to `REVIEW` because the elapsed time would fall below 48 hours. The test verifies that outcome.
