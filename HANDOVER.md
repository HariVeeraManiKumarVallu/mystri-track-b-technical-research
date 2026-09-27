# Handover

## Submission

**Track:** B — Technical research and prototyping
**Workflow:** Missing-information follow-up triage
**Mode:** Dry run only; no messages were sent and no external service calls were made.

## Exact run commands

From the `track-b` directory:

python src/followup_experiment.py

python -m unittest discover -s tests -v

Python 3.10+ is sufficient. No third-party packages or credentials are required.

## Outputs

* `output/triage_results.csv` — baseline and proposed decisions for each evaluated pending request.
* `output/summary.json` — experiment counts and deduplicated effort metrics.
* `output/changed_input_triage_results.csv` — results after the deliberate C024 timestamp change.
* `output/changed_input_summary.json` — summary of the changed-input experiment.
* `output/no_action_triage_results.csv` — valid no-action scenario output.
* `output/no_action_summary.json` — confirms zero proposed actions in the no-action scenario.

## Verification performed

1. **Baseline and proposed results:**
   The supplied snapshot produced 7 simple-baseline actions, compared with 4 proposed actions, 3 reviews and 1 exclusion across 8 evaluated rows.

2. **Opt-out edge case:**
   C012 has `followup_allowed=0`. The proposed method correctly returns `EXCLUDE` rather than proposing customer contact.

3. **No-action scenario:**
   All pending in-scope requests were changed to have `received_at`. The program completed successfully and produced zero proposed actions.

4. **Changed-input experiment:**
   Before running the experiment, I predicted that changing C024's `last_requested_at` from `2026-09-04 12:00` to `2026-09-06 12:00` would move both C024 requests from `ACTION` to `REVIEW` because the 48-hour minimum follow-up interval would no longer be satisfied. The observed result matched the prediction: proposed actions decreased from 4 to 2, while reviews increased from 3 to 5.

5. **Duplicate event handling:**
   The supplied event data contains 128 rows but only 124 unique event IDs. Four duplicate deliveries were identified. The implementation deduplicates events by stable `event_id` before effort calculations, resulting in 400 known active minutes instead of 412 minutes if all rows were counted.

6. **Automated tests:**
   Four unit tests pass successfully with `OK`.

## Tool-use summary

* **ChatGPT, GPT-5.6 Luna:** Used to structure the experiment, inspect the assessment requirements, identify candidate hypotheses, draft implementation and documentation, and challenge the reasoning. Generated suggestions were treated as inputs rather than evidence. Data-derived results were independently checked by running the local program and tests. During verification, the initial test expectation was corrected because the opt-out row is intentionally retained as an inspectable `EXCLUDE` result.

* **Python 3.10+ standard library:** Used to implement the prototype, parse CSV/JSON data, perform timestamp calculations, apply deterministic eligibility rules, generate experiment outputs, and run unit tests. No external API calls are made by the prototype.

* **Web research:** Used official Microsoft, Dropbox and Jotform documentation to verify the capabilities of alternative tools considered in the decision analysis. Vendor documentation was treated as capability evidence rather than evidence of business value, and remaining licensing and adoption questions are documented in `SOURCES.md`.

**Concrete issue caught during verification:**
Counting all 128 event rows would have inflated known active effort from 400 to 412 minutes because four event IDs were duplicated. I therefore changed the implementation to deduplicate events using the stable `event_id` before calculating effort-related metrics.

## Remaining uncertainty

The supplied sample does not measure the coordinator's complete workload, every phone call, customer adoption, conversion or revenue impact, or the actual cost of coordinator time. Therefore, the 8-hour weekly owner estimate is treated as an input assumption rather than a measured benefit.

The recommended next step is a four-week operational measurement pilot to collect real workload, follow-up, response and outcome data before committing to further automation or a paid tool.